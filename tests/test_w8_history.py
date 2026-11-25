"""SQLite and HTTP/SSE integration tests on a temporary database only."""
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request,urlopen
from unittest.mock import patch

from source.data.db.demo_history import HistoryStore,HistoryError
from w8_fixture import start,stop


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/'test.sqlite3';self.store=HistoryStore(self.path)
        self.session=self.store.create_session()
    def tearDown(self): self.temp.cleanup()
    def final(self):
        return {'type':'final','answer':'Đáp án giả lập có dấu tiếng Việt.','citation_indices':[0],
                'sources':[{'id':'fixture-0','text':'Nội dung nguồn synthetic.'}],'fixture_execution':True}
    def complete(self,question='Câu hỏi synthetic có dấu?'):
        turn=self.store.begin(self.session,question,'all','agentic');return self.store.complete(turn,self.final())
    def test_empty_session_visible(self):
        self.assertEqual(self.store.history(self.session)['chat_history'],[])
        self.assertEqual(self.store.sessions()[0]['id'],self.session)
    def test_unicode_and_source_payload_roundtrip(self):
        self.complete();data=self.store.history(self.session)
        self.assertEqual([m['sender'] for m in data['chat_history']],['user','bot'])
        self.assertEqual(data['chat_history'][1]['payload'],self.final())
    def test_last_five_messages_and_session_isolation(self):
        for i in range(4):self.complete('Synthetic '+str(i))
        other=self.store.create_session();memory=self.store.memory
        self.assertEqual(len(memory.get_recent_turns(self.session)),5)
        self.assertIn('Synthetic 3',memory.build_context(self.session))
        self.assertNotIn('Synthetic 0',memory.build_context(self.session))
        self.assertEqual(memory.build_context(other),'')
        with self.store.connection() as conn:conn.execute("INSERT INTO User_Facts(fact_text) VALUES ('must not enter context')")
        self.assertNotIn('must not enter',memory.build_context(self.session))
    def test_duplicate_request_and_busy_session_rejected(self):
        turn=self.store.begin(self.session,'q','all','agentic','same-request')
        with self.assertRaises(HistoryError):self.store.begin(self.session,'q2','all','agentic')
        self.store.complete(turn,self.final())
        with self.assertRaises(HistoryError):self.store.begin(self.session,'q','all','agentic','same-request')
    def test_failure_does_not_fabricate_answer(self):
        turn=self.store.begin(self.session,'q','all','agentic');self.store.fail(turn,'provider_error')
        data=self.store.history(self.session)
        self.assertEqual(data['chat_history'],[]);self.assertEqual(data['turns'][0]['status'],'failed')
    def test_restart_preserves_history_and_marks_interrupted(self):
        self.complete();self.store.begin(self.session,'interrupted','all','agentic')
        reopened=HistoryStore(self.path);data=reopened.history(self.session)
        self.assertEqual(len(data['chat_history']),2)
        self.assertEqual(data['turns'][-1]['error_code'],'server_restarted')
    def test_bad_reference_rolls_back_pair(self):
        turn=self.store.begin(self.session,'q','all','agentic');final=self.final();final['references']=[{'bad':'not text'}]
        with self.assertRaises(Exception):self.store.complete(turn,final)
        self.assertEqual(self.store.history(self.session)['chat_history'],[])
    def test_delete_cascades_references_and_turns(self):
        self.complete();self.store.delete_session(self.session)
        with self.store.connection() as conn:
            for name in ['Chat_Messages','Chat_References','Demo_Turns']:self.assertEqual(conn.execute('SELECT count(*) FROM '+name).fetchone()[0],0)
        with self.assertRaises(HistoryError):self.store.history(self.session)
    def test_processing_session_cannot_be_deleted(self):
        self.store.begin(self.session,'q','all','agentic')
        with self.assertRaises(HistoryError):self.store.delete_session(self.session)


class HTTPHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.store=HistoryStore(Path(cls.temp.name)/'http.sqlite3')
        cls.server,cls.engine,cls.old=start(cls.store)
        cls.base='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):stop(cls.server,cls.old);cls.temp.cleanup()
    def request(self,path,method='GET',payload=None,headers=None):
        data=json.dumps(payload,ensure_ascii=False).encode() if payload is not None else (b'' if method=='POST' else None)
        req=Request(self.base+path,data=data,method=method,headers={'Content-Type':'application/json',**(headers or {})})
        try:
            with urlopen(req,timeout=20) as res:return res.status,res.headers,res.read().decode('utf-8')
        except HTTPError as e:return e.code,e.headers,e.read().decode('utf-8')
    def session(self):return json.loads(self.request('/api/session/start-session','POST')[2])['session_id']
    def chat(self,session,question='Câu hỏi tổng hợp synthetic?',**kwargs):
        status,headers,body=self.request('/api/chat','POST',dict(question=question,session_id=session,domain='all',mode='agentic',**kwargs))
        self.assertEqual(status,200)
        events=[json.loads(s[6:]) for s in body.split('\n\n') if s.startswith('data: ')]
        return headers,events
    def test_sse_then_history_keeps_exact_citations(self):
        session=self.session();headers,events=self.chat(session)
        self.assertIn('text/event-stream',headers['Content-Type'])
        self.assertTrue(any(e['type']=='plan' for e in events));self.assertEqual(events[-1]['type'],'done')
        final=next(e for e in events if e['type']=='final')
        self.assertEqual(final['citation_base'],0);self.assertEqual(final['sources'][0]['id'],'fixture-A-0')
        data=json.loads(self.request('/api/session/get-chat-history/'+str(session))[2])
        self.assertEqual(data['chat_history'][-1]['payload']['sources'],final['sources'])
        refs=json.loads(self.request('/api/session/get-message-references/'+str(final['message_id']))[2])
        self.assertEqual(len(refs['references']),1)
    def test_followup_passes_prior_messages_to_real_graph(self):
        session=self.session();self.chat(session,'Câu đầu synthetic về mũ bảo hiểm?');self.chat(session,'Còn trường hợp đó thì sao?')
        prompt=self.engine.contexts[-1]['planner_prompt'];self.assertIn('Câu đầu synthetic về mũ bảo hiểm?',prompt)
        other=self.session();self.chat(other,'Phiên độc lập synthetic')
        self.assertNotIn('Câu đầu synthetic về mũ bảo hiểm?',self.engine.contexts[-1]['planner_prompt'])
    def test_provider_error_recorded_without_fake_final(self):
        session=self.session();_,events=self.chat(session,'W8_PROVIDER_ERROR')
        self.assertTrue(any(e['type']=='error' for e in events));self.assertFalse(any(e['type']=='final' for e in events))
        data=self.store.history(session);self.assertEqual(data['turns'][0]['status'],'failed');self.assertEqual(data['chat_history'],[])
    def test_history_write_error_still_delivers_real_final(self):
        session=self.session()
        with patch.object(self.store,'complete',side_effect=RuntimeError('fixture database write failure')):
            _,events=self.chat(session)
        final=next(e for e in events if e['type']=='final')
        self.assertEqual(final['history_status'],'failed')
        self.assertTrue(any(e['type']=='history_error' for e in events))
        self.assertFalse(any(e['type']=='error' for e in events))
        self.assertEqual(self.store.history(session)['turns'][0]['error_code'],'history_write_failed')
    def test_unknown_invalid_session_and_bad_request(self):
        for value,expected in [(999999,404),(True,400),('1',400)]:
            status,_,_=self.request('/api/chat','POST',dict(question='synthetic',session_id=value,domain='all',mode='agentic'))
            self.assertEqual(status,expected)
        self.assertEqual(self.request('/api/chat','POST',{'question':''})[0],400)
    def test_delete_and_reload(self):
        session=self.session();self.chat(session)
        self.assertEqual(self.request('/api/session/delete-session/'+str(session),'DELETE')[0],200)
        self.assertEqual(self.request('/api/session/get-chat-history/'+str(session))[0],404)
    def test_cross_origin_writes_rejected(self):
        self.assertEqual(self.request('/api/session/start-session','POST',headers={'Origin':'https://unrelated.example'})[0],403)
    def test_stateless_compatibility_without_session(self):
        _,events=self.chat(None)
        self.assertTrue(any(e['type']=='final' for e in events))
    def test_disconnect_keeps_worker_persistence(self):
        session=self.session();self.engine.pause=threading.Event()
        req=Request(self.base+'/api/chat',data=json.dumps(dict(question='Disconnect synthetic',session_id=session,mode='agentic')).encode(),headers={'Content-Type':'application/json'})
        response=urlopen(req,timeout=10);self.assertTrue(response.readline().startswith(b'data: '));response.close()
        self.engine.pause.set()
        deadline=time.monotonic()+8
        while self.store.history(session)['turns'][0]['status']=='processing' and time.monotonic()<deadline:time.sleep(.02)
        self.engine.pause=None
        self.assertEqual(self.store.history(session)['turns'][0]['status'],'complete')
    def test_inflight_duplicate_rejected(self):
        session=self.session();self.engine.pause=threading.Event()
        req=Request(self.base+'/api/chat',data=json.dumps(dict(question='First pending synthetic',session_id=session,mode='agentic',request_id='inflight-case')).encode(),headers={'Content-Type':'application/json'})
        response=urlopen(req,timeout=10);response.readline()
        self.assertEqual(self.request('/api/chat','POST',dict(question='Second synthetic',session_id=session,mode='agentic'))[0],409)
        self.assertEqual(self.request('/api/session/delete-session/'+str(session),'DELETE')[0],409)
        self.engine.pause.set();response.read();response.close();self.engine.pause=None
    def test_sources_and_static_assets(self):
        data=json.loads(self.request('/api/source/fixture-A-0')[2]);self.assertIn('synthetic',data['text'])
        for path in ['/','/app.js','/sse.js','/style.css']:self.assertEqual(self.request(path)[0],200)

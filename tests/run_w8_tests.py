"""W8 acceptance evidence with isolated synthetic data and deterministic model fixtures."""
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
os.environ['AWS_EC2_METADATA_DISABLED']='true'


def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


class Result(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.records=[]
    def startTest(self,test):super().startTest(test);self.records.append({'id':test.id(),'status':'running'})
    def addSuccess(self,test):super().addSuccess(test);self.records[-1]['status']='passed'
    def addFailure(self,test,err):super().addFailure(test,err);self.records[-1]['status']='failed'
    def addError(self,test,err):super().addError(test,err);self.records[-1]['status']='error'
    def addSkip(self,test,reason):super().addSkip(test,reason);self.records[-1].update(status='skipped',reason=reason)


def synthetic_conversations():
    qa=[json.loads(line) for line in (ROOT/'data/qa_w5_200.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    conversations=[]
    for domain in ['giaoThong_VanTai','laoDong_TienLuong']:
        selected=[q for q in qa if q['domain']==domain][:6]
        for q in selected:
            conversations.append({'id':f'W8-C{len(conversations)+1:02d}','domain':domain,'mode':'agentic',
                'source_qa_id':q['id'],'review_status':'synthetic_interaction_not_legal_gold',
                'turns':[q['question'],'Bạn đang dựa vào đoạn nguồn nào cho câu trả lời trước?',
                         'Nếu tôi chưa nêu đủ tình tiết, bạn cần tôi làm rõ điều gì?']})
    return conversations


def run_synthetic(folder):
    from source.data.db.demo_history import HistoryStore
    from w8_fixture import start,stop
    conversations=synthetic_conversations();logs=[];roundtrips=0
    with tempfile.TemporaryDirectory() as tmp:
        store=HistoryStore(Path(tmp)/'synthetic.sqlite3');server,engine,old=start(store)
        base='http://127.0.0.1:'+str(server.server_port)
        try:
            for conversation in conversations:
                session=store.create_session()
                for turn_index,question in enumerate(conversation['turns'],1):
                    payload=dict(question=question,domain=conversation['domain'],mode='agentic',session_id=session,
                                 request_id=conversation['id']+'-'+str(turn_index))
                    request=Request(base+'/api/chat',data=json.dumps(payload,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
                    with urlopen(request,timeout=20) as response:
                        events=[json.loads(frame[6:]) for frame in response.read().decode().split('\n\n') if frame.startswith('data: ')]
                    final=next(e for e in events if e['type']=='final')
                    history=store.history(session)
                    assert history['chat_history'][-1]['payload']['sources']==final['sources']
                    assert len(history['chat_history'])==2*turn_index
                    roundtrips+=1
                    common={'conversation_id':conversation['id'],'turn':turn_index,'domain':conversation['domain'],
                            'fixture_execution':True,'synthetic':True,'not_legal_gold':True}
                    logs.append({**common,'role':'user','content':question})
                    logs.append({**common,'role':'assistant','content':final['answer'],'source_ids':[s['id'] for s in final['sources']],
                                 'source_snapshot':final['sources'],'events':events,'history_roundtrip':'passed'})
        finally:stop(server,old)
    dump(folder/'synthetic_conversations.json',{'version':'1.0','status':'synthetic_integration_data_not_independent_qa_test',
          'conversations':conversations,'count':len(conversations),'turns':roundtrips,'aws_calls':0})
    (folder/'synthetic_chat_logs.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in logs),encoding='utf-8')
    return {'conversations':len(conversations),'user_turns':roundtrips,'chat_messages':len(logs),
            'history_roundtrips_passed':roundtrips,'fixture_execution':True,'aws_calls':0,'legal_answer_accuracy':'not_evaluated'}


def main():
    import test_w8_history,test_agent_w6,test_synthesis_response
    suite=unittest.TestSuite()
    for module in [test_w8_history,test_agent_w6,test_synthesis_response]:suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
    result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    folder=ROOT/'runs/w8';folder.mkdir(parents=True,exist_ok=True)
    js=subprocess.run(['node','tests/test_sse_w8.cjs'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if js.returncode:raise RuntimeError('SSE JavaScript tests failed: '+js.stderr)
    js_report=json.loads(js.stdout);dump(folder/'test-results-js.json',js_report)
    synthetic=run_synthetic(folder) if result.wasSuccessful() else {'status':'not_run_due_to_test_failure'}
    paths=['app.py','app.js','sse.js','index.html','style.css','runtime.py','source/agent/demo_agentic.py',
           'source/data/db/demo_history.py','source/data/db/db_connection.py','source/data/db/utils_db.py','source/data/db/memory.py',
           'source/agent/graph_orchestrator.py','source/agent/orchestrator.py','tests/run_w8_tests.py','tests/test_w8_history.py',
           'tests/w8_fixture.py','tests/test_sse_w8.cjs']
    report={'week':'W08','run_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
            'tests_run':result.testsRun,'passed':sum(r['status']=='passed' for r in result.records),'failures':len(result.failures),
            'errors':len(result.errors),'skipped':len(result.skipped),'cases':result.records,'javascript':js_report,'synthetic':synthetic,
            'aws_calls':0,'real_model_inference':False,'fixture_execution':True,'private_history_read':False,
            'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
            'limitations':['Fixture LLM/retrieval/BERT/CE, not a live model benchmark.','History DBs are temporary and never exported.',
                           'Browser visual acceptance is recorded separately.']}
    dump(folder/'test-results.json',report)
    print(json.dumps({key:report[key] for key in ['tests_run','passed','failures','errors','javascript','synthetic','aws_calls']},ensure_ascii=False))
    return int(not result.wasSuccessful())


if __name__=='__main__':raise SystemExit(main())

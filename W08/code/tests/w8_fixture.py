"""Real graph/API/history with deterministic W6 model fixtures, never AWS or weights."""
import copy
import json
import threading
from pathlib import Path

import app
import runtime
from source.agent.demo_agentic import DemoAgentic
from source.agent.graph_orchestrator import GraphOrchestrator
from test_agent_w6 import CASES, build


class FixtureEngine:
    def __init__(self):
        self.contexts=[]
        self.by_id={};self.nodes={}
        for i in range(2):
            key=f'fixture-A-{i}';node=f'fixture-node-{i}'
            self.by_id[key]={'id':key,'text':'Đoạn giả lập, không phải điều luật.', 'metadata':{
                'node_id':node,'SoHieu':'FIXTURE-W8','ChuDe':'Nguồn kiểm thử synthetic, không phải văn bản pháp luật',
                'Article':f'Điều giả lập {i+1}','NoiBanHanh':'Bộ kiểm thử','NgayBanHanh':'không áp dụng',
                'domain':'giaoThong_VanTai','source_file':'synthetic_fixture.docx'}}
            self.nodes[node]={'id':node,'parent_id':None,'text_original':'Nguồn synthetic để kiểm tra lưu và khôi phục trích dẫn.'}
        self.pause=None

    source=runtime.Engine.source

    def refresh_llm(self):
        return False

    def chat(self, question, domain, mode, session_id=None, memory=None):
        scenario='provider_error' if question=='W8_PROVIDER_ERROR' else 'outside' if 'ly hôn' in question else 'traffic'
        case=copy.deepcopy(next(c for c in CASES if c['scenario']==scenario))
        case['question']=question
        graph,generator,search,_,_=build(case,GraphOrchestrator)
        generator.usage=[]
        bridge=DemoAgentic.__new__(DemoAgentic)
        bridge.engine,bridge.generator,bridge.search,bridge.orchestrator=self,generator,search,graph
        # Pause after emitting one event, useful for disconnect and in-flight tests.
        yield {'type':'fixture_execution','message':'Test fixture, not legal advice'}
        if self.pause:
            self.pause.wait(timeout=10)
        for event in bridge.chat(question,domain,session_id=session_id,memory=memory):
            event['fixture_execution']=True
            yield event
        self.contexts.append({'session_id':session_id,'question':question,
                              'planner_prompt':next((p for tokens,p in generator.prompts if tokens==800),'')})


def start(store):
    old=(app.HISTORY,runtime.ENGINE,dict(runtime.STATE))
    engine=FixtureEngine()
    app.HISTORY=store;runtime.ENGINE=engine
    runtime.STATE.update(ready=True,phase='ready',fixture_execution=True,llm_ready=False,evaluation='not_run')
    server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    return server,engine,old


def stop(server,old):
    server.shutdown();server.server_close()
    app.HISTORY,runtime.ENGINE=old[:2]
    runtime.STATE.clear();runtime.STATE.update(old[2])

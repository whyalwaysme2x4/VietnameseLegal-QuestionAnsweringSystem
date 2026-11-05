"""Run exactly 15 agent cases and save explicitly fixture-based traces/results."""
import datetime
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
import test_agent_w6 as cases

suite=unittest.defaultTestLoader.loadTestsFromTestCase(cases.AgentPolicyTests)
result=unittest.TextTestRunner(verbosity=2).run(suite)
folder=ROOT/'runs/w6';(folder/'traces').mkdir(parents=True,exist_ok=True)
failed={test.id().split('.')[-1] for test,_ in result.failures+result.errors}
report={'suite':'original-policy parity through LangGraph','run_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
        'tests_run':result.testsRun,'passed':result.testsRun-len(result.failures)-len(result.errors),'failures':len(result.failures),'errors':len(result.errors),
        'aws_calls':0,'fixture_llm':True,'fixture_retrieval':True,'fixture_bert_tensors':True,
        'actual_code':['PlannerAgent','GraderAgent','HallucinationChecker','Extract_Information','RRF utility','Orchestrator reference','GraphOrchestrator'],
        'limitations':'Control-flow/contract parity tests. Not a live model benchmark, domain-classification accuracy, or legal correctness verification.',
        'cases':[{'id':case['id'],'name':case['name'],'status':'failed' if 'test_'+case['id'] in failed else 'passed'} for case in cases.CASES]}
for key,events in cases.TRACES.items():
    (folder/'traces'/f'{key}.jsonl').write_text(''.join(json.dumps({'case_id':key,'fixture_execution':True,**event},ensure_ascii=False)+'\n' for event in events),encoding='utf-8')
(folder/'test-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sys.exit(0 if result.wasSuccessful() and result.testsRun==15 else 1)

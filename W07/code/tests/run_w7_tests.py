"""W7 fixture/contract run. No Engine construction, model downloads or AWS calls."""
import datetime
import hashlib
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'tests')]
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['AWS_EC2_METADATA_DISABLED'] = 'true'

SELECTED = ['W6_01','W6_02','W6_03','W6_06','W6_07','W6_11','W6_12','W6_13','W6_14','W6_15']


class Result(unittest.TextTestResult):
    def startTest(self, test):
        super().startTest(test)
        self.records.append({'test_id':test.id(),'status':'running'})
    def addSuccess(self, test):
        super().addSuccess(test); self.records[-1]['status']='passed'
    def addFailure(self, test, err):
        super().addFailure(test, err); self.records[-1]['status']='failed'
    def addError(self, test, err):
        super().addError(test, err); self.records[-1]['status']='error'
    def addSkip(self, test, reason):
        super().addSkip(test, reason); self.records[-1].update(status='skipped', reason=reason)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs); self.records=[]


def main():
    # Deny external socket connections even if an unexpected code path attempts one.
    with patch('socket.socket.connect', side_effect=RuntimeError('W7 fixtures prohibit network connections')):
        import test_agent_w6 as agents
        import test_synthesis_response as baseline
        import test_w7_contract as contracts
        suite=unittest.TestSuite([agents.AgentPolicyTests('test_'+key) for key in SELECTED])
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(baseline))
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(contracts))
        result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
    folder=ROOT/'runs/w7'
    (folder/'traces').mkdir(parents=True,exist_ok=True)
    for key, events in agents.TRACES.items():
        (folder/'traces'/f'{key}.jsonl').write_text(''.join(json.dumps(
            {'case_id':key,'fixture_execution':True,**event},ensure_ascii=False)+'\n' for event in events),encoding='utf-8')
    inputs=['tests/run_w7_tests.py','tests/test_w7_contract.py','tests/test_agent_w6.py',
            'tests/test_synthesis_response.py','tests/agent_cases_w6.json','source/agent/orchestrator.py',
            'source/agent/graph_orchestrator.py','source/agent/hallucination_checker.py','source/agent/grader.py',
            'source/agent/planner.py','source/agent/demo_agentic.py','source/core/corpus_scope.json',
            'source/generate/synthesis_response.py','Evidence/W07/data/qa_candidates_30.jsonl',
            'data/documents.jsonl','data/qa_w5_200.jsonl','app.py','app.js','index.html']
    report={'week':'W07','suite':'W7 citation/refusal fixture and source/data contracts',
            'run_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(),
            'tests_run':result.testsRun,'passed':sum(r['status']=='passed' for r in result.records),
            'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
            'aws_calls':0,'model_inference':False,'fixture_execution':True,'network_connections_blocked':True,
            'selected_w6_cases_rerun':SELECTED,'cases':result.records,
            'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},
            'limitations':['Fixture control-flow and static contracts, not semantic grounding or refusal accuracy.',
                           'Source UI static check is not a browser visual test.',
                           'QA labels provisional and not human-reviewed.']}
    (folder/'test-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['tests_run','passed','failures','errors','skipped','aws_calls','model_inference']}))
    return int(not result.wasSuccessful() or result.testsRun!=28)


if __name__=='__main__':
    raise SystemExit(main())

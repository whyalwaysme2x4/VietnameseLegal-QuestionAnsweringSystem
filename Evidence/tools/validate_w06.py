"""Validate frozen W06 evidence using only the standard library; no inference."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
WEEK=ROOT/'Evidence/W06'

def load(path):return json.loads(path.read_text(encoding='utf-8'))

def validate(root=ROOT):
    folder=root/'Evidence/W06'
    failures=[]
    checks=[]
    def check(name, condition):
        checks.append(name)
        if not condition:failures.append(name)
    manifest=load(folder/'manifest.json')
    check('required_structure',all((folder/name).is_file() for name in ['README.md','metrics.csv','test-results.json','manifest.json']) and (folder/'figures').is_dir())
    check('main_branch_and_review_state',manifest['branch']=='main' and manifest['github']['pr'] is None and manifest['review_status']=='pending')
    case_definitions=load(folder/'agent-cases.json')['cases']
    report=load(folder/'test-results.json')
    check('fifteen_distinct_cases',len(case_definitions)==len({case['id'] for case in case_definitions})==15)
    check('saved_test_results',report['tests_run']==report['passed']==15 and report['failures']==report['errors']==0 and len(report['cases'])==15 and all(case['status']=='passed' for case in report['cases']))
    check('fixture_execution_explicit',report['fixture_llm'] and report['fixture_retrieval'] and report['fixture_bert_tensors'] and report['aws_calls']==0)
    check('case_ids_match', {case['id'] for case in case_definitions}=={case['id'] for case in report['cases']})
    check('case_file_matches_runtime_tests', (folder/'agent-cases.json').read_bytes()==(root/'tests/agent_cases_w6.json').read_bytes())
    expected_nodes={'planner','retrieve','extract','grader','select_best','generate','checker','regenerate','finish','alternate'}
    for case in case_definitions:
        path=folder/'traces'/f"{case['id']}.jsonl"
        trace=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
        check(case['id']+'_fixture_trace',bool(trace) and all(event['fixture_execution'] is True and event['case_id']==case['id'] for event in trace))
        check(case['id']+'_graph_nodes',any(event['type']=='graph_node' and event['node']=='planner' for event in trace) and all(event['node'] in expected_nodes for event in trace if event['type']=='graph_node'))
        check(case['id']+'_retrieval_round_limit',all(event['iteration']<=2 for event in trace if event['type']=='retrieve_start'))
    assets=load(folder/'asset-smoke.json')
    check('offline_assets_not_live_aws',assets['scope_documents']==53 and assets['scope_index_points']==6883 and assets['real_bert_loaded'] and assets['real_crossencoder_loaded'] and assets['aws_calls']==0 and not assets['full_agent_llm_run'] and assets['bert_answer_quality']=='not_evaluated')
    http=load(folder/'http-contract-smoke.json')
    check('http_fixture_contract',http['status']=='passed' and http['fixture_execution'] and http['aws_calls']==0 and not http['full_agent_llm_run'] and [item['citation_index'] for item in http['checks']]==[0,1] and all(item['source_card'] and item['final_trace_has_finish'] for item in http['checks']))
    with (folder/'metrics.csv').open(encoding='utf-8-sig',newline='') as stream: rows=list(csv.DictReader(stream))
    values={row['metric']:float(row['value']) for row in rows}
    check('metrics_match_observations',values=={'test_cases':15,'passed':15,'failures':0,'errors':0,'pass_rate':1,'aws_calls':0,'indexed_chunks':6883} and all(row['split'] in {'fixture_control_flow','offline_assets'} and row['week']=='W06' for row in rows))
    for entry in manifest['artifacts']:
        path=(root/entry['path']).resolve()
        safe=path.is_relative_to(root.resolve()) and path.is_file()
        check('sha256:'+entry['path'],safe and path.stat().st_size==entry['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'])
    for path in (root/'source').rglob('*.py'):
        ast.parse(path.read_text(encoding='utf-8-sig'))
    ET.parse(folder/'figures/agent-graph.svg')
    check('source_and_figure_parse',True)
    return {'status':'passed' if not failures else 'failed','checks':len(checks),'failures':failures,
            'aws_calls':0,'model_inference':False,'peer_review':'pending_not_assessed'}

if __name__=='__main__':
    result=validate()
    print(json.dumps(result,indent=2))
    raise SystemExit(result['status']!='passed')

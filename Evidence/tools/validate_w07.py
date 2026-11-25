"""Read-only W07 evidence/data/trace verification using only Python stdlib."""
import ast
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from snapshot_resolver import resolve_artifact

ROOT=Path(__file__).resolve().parents[2]


def load(path): return json.loads(path.read_text(encoding='utf-8'))
def jsonl(path): return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def main():
    folder=ROOT/'Evidence/W07'; checks=[]; failures=[]
    def check(name, condition):
        checks.append(name)
        if not condition: failures.append(name)
    for name in ['README.md','metrics.csv','test-results.json','manifest.json','CITATION_REFUSAL_POLICY.md',
                 'EVALUATION_PROTOCOL.md','SOURCE_UI.md','http-contract-smoke.json']:
        check('required:'+name,(folder/name).is_file())
    manifest=load(folder/'manifest.json')
    check('runtime_unchanged',not manifest['algorithm_changes'] and not manifest['new_inference'])
    check('honest_review_and_branch',manifest['branch']=='main' and manifest['review_status']=='pending' and manifest['github']['pr'] is None)
    for entry in manifest['artifacts']:
        path=resolve_artifact(ROOT,'W07',entry['path'],entry['sha256'])
        check('path:'+entry['path'],path.is_relative_to(ROOT.resolve()) and path.is_file())
        check('hash:'+entry['path'],hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'])
    report=load(folder/'test-results.json')
    check('fixture_result',report['tests_run']==report['passed']==28 and report['failures']==report['errors']==report['skipped']==0)
    check('fixture_limits',report['fixture_execution'] and report['network_connections_blocked'] and report['aws_calls']==0 and not report['model_inference'])
    check('case_results',len(report['cases'])==28 and all(c['status']=='passed' for c in report['cases']))
    for path,digest in report['input_sha256'].items():
        check('test_input:'+path,hashlib.sha256(resolve_artifact(ROOT,'W07',path,digest).read_bytes()).hexdigest()==digest)
    for key in report['selected_w6_cases_rerun']:
        trace=jsonl(folder/'traces'/f'{key}.jsonl')
        check('trace:'+key,bool(trace) and all(r['fixture_execution'] and r['case_id']==key for r in trace))
    qa=jsonl(folder/'data/qa_candidates_30.jsonl')
    check('candidate_count',len(qa)==len({q['id'] for q in qa})==30)
    check('provisional_labels',all(q['review_status']=='pending' and q['expected_action_status']=='provisional_not_human_gold' for q in qa))
    check('candidate_actions',Counter(q['expected_action'] for q in qa)=={'refuse':20,'clarify':5,'answer':5})
    original={q['id']:q for q in jsonl(ROOT/'data/qa_w5_200.jsonl')}
    controls=[q for q in qa if q['category']=='answerable_control']
    check('control_provenance',len(controls)==5 and all(q['question']==original[q['source_qa_id']]['question'] and q['supporting_source_ids']==original[q['source_qa_id']]['relevant_article_ids'] for q in controls))
    docs=jsonl(ROOT/'data/documents.jsonl')
    synthetic=[q for q in qa if q['absence_marker']]
    check('record_marker_absence',len(docs)==53 and len(synthetic)==10 and all(not any(q['absence_marker'].casefold() in d['text_original'].casefold() for d in docs) for q in synthetic))
    http=load(folder/'http-contract-smoke.json')
    check('http_fixture',http['status']=='passed' and http['fixture_execution'] and http['aws_calls']==0 and len(http['checks'])==2)
    with (folder/'metrics.csv').open(encoding='utf-8',newline='') as stream: metrics=list(csv.DictReader(stream))
    unmeasured={'citation_validity','grounding_support','refusal_recall','false_refusal_rate','clarification_accuracy','pipeline_error_rate'}
    check('unmeasured_not_fabricated',{r['metric'] for r in metrics if r['status']=='not_measured'}==unmeasured and all(r['value']=='' for r in metrics if r['metric'] in unmeasured))
    measured={r['metric']:r['value'] for r in metrics if r['status']=='measured'}
    check('measured_inventory_and_tests',measured.get('fixture_contract_pass_rate')=='1.0' and measured.get('qa_candidates')=='30' and measured.get('fixture_contract_tests')=='28')
    for path in [ROOT/'tests/run_w7_tests.py',ROOT/'tests/test_w7_contract.py',Path(__file__)]:
        ast.parse(path.read_text(encoding='utf-8'))
    print(json.dumps({'status':'failed' if failures else 'passed','checks':len(checks),'failures':failures,
                      'aws_calls':0,'model_inference':False,'semantic_grounding_evaluated':False},indent=2))
    return int(bool(failures))


if __name__=='__main__': raise SystemExit(main())

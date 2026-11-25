"""Read-only W08 publication validation; stdlib, no model/DB/API calls."""
import csv
import hashlib
import json
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]


def load(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    folder=ROOT/'Evidence/W08';failures=[];count=0
    def check(name,ok):
        nonlocal count
        count+=1
        if not ok:failures.append(name)
    for name in ['README.md','metrics.csv','test-results.json','manifest.json','github.json','packaging.json']:
        check('required:'+name,(folder/name).is_file())
    report=load(folder/'test-results.json')
    check('python_tests',report['tests_run']==report['passed']==46 and report['failures']==report['errors']==report['skipped']==0)
    check('fixture_not_real_model',report['fixture_execution'] and report['aws_calls']==0 and not report['real_model_inference'])
    check('sse_parser',report['javascript']['checks']==report['javascript']['passed']==8)
    check('history_roundtrips',report['synthetic']['history_roundtrips_passed']==36)
    rows=[json.loads(line) for line in (folder/'synthetic_chat_logs.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    check('synthetic_logs',len(rows)==72 and Counter(r['role'] for r in rows)=={'user':36,'assistant':36} and all(r['synthetic'] and r['fixture_execution'] and r['not_legal_gold'] for r in rows))
    conversations=load(folder/'synthetic_conversations.json')['conversations']
    check('conversation_distribution',len(conversations)==12 and all(len(c['turns'])==3 for c in conversations) and Counter(c['domain'] for c in conversations)=={'giaoThong_VanTai':6,'laoDong_TienLuong':6})
    browser=load(folder/'browser-results.json')
    check('chrome_checks',browser['status']=='passed' and browser['checks_passed']==8 and not browser['javascript_errors'] and browser['fixture_execution'] and browser['aws_calls']==0)
    for image in browser['screenshots']:check('screenshot:'+image,(folder/'figures'/image).is_file())
    for path,digest in report['input_sha256'].items():
        check('current_run_source:'+path,hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest)
    check('original_helpers_reused',all(r['identical_to_original'] for r in load(folder/'source_reuse.json')['reused_modules']))
    check('original_unchanged_at_implementation',load(folder/'original_preservation.json')['all_original_files_unchanged'])
    index=load(ROOT/'Evidence/_history/index.json')
    check('historical_snapshot_count',len(index['entries'])==26)
    for e in index['entries']:
        path=(ROOT/e['snapshot_path']).resolve()
        check('historical:'+e['week']+':'+e['path'],path.is_relative_to((ROOT/'Evidence/_history').resolve()) and path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==e['sha256'])
    with (folder/'metrics.csv').open(encoding='utf-8',newline='') as stream:metrics=list(csv.DictReader(stream))
    values={r['metric']:r['value'] for r in metrics if r['status']=='measured'}
    check('metrics_observed',values['python_tests']=='46' and values['sse_parser_checks']=='8' and values['browser_checks']=='8' and values['synthetic_chat_messages']=='72' and values['aws_calls']=='0')
    check('quality_not_fabricated',all(r['value']=='' for r in metrics if r['status']=='not_measured') and {r['metric'] for r in metrics if r['status']=='not_measured'}=={'legal_answer_accuracy','real_model_latency_ms'})
    manifest=load(folder/'manifest.json')
    check('main_and_review',manifest['branch']=='main' and manifest['review_status']=='pending' and manifest['github']['pr'] is None)
    check('publication_scope',not manifest['algorithm_changes'] and manifest['integration_behavior_changes'] and not manifest['new_inference'] and not manifest['private_database_exported'])
    for e in manifest['artifacts']:
        path=(ROOT/e['path']).resolve()
        check('safe_path:'+e['path'],path.is_relative_to(ROOT.resolve()) and path.is_file() and path.suffix not in {'.db','.sqlite','.sqlite3','.safetensors','.pt','.bin','.log'})
        check('sha256:'+e['path'],hashlib.sha256(path.read_bytes()).hexdigest()==e['sha256'] and path.stat().st_size==e['bytes'])
    print(json.dumps({'status':'failed' if failures else 'passed','checks':count,'failures':failures,
                      'aws_calls':0,'real_model_inference':False,'peer_review':'pending_not_assessed'},indent=2))
    return int(bool(failures))


if __name__=='__main__':raise SystemExit(main())

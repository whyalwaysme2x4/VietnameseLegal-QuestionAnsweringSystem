"""Read-only validation of the additional weekly browsing copies."""
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent

def main():
    failed=[]
    count=0
    totals={}
    for i in range(1,7):
        week=f'W{i:02d}'
        folder=ROOT/week
        for name in ['README.md','code','data','metrics.csv','test-results.json','figures','manifest.json']:
            if not (folder/name).exists():failed.append(week+':missing:'+name)
        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        if manifest['week']!=week or manifest['algorithm_changes'] or manifest['new_inference']:
            failed.append(week+':unexpected_claim')
        if manifest['organization']!='copies_of_current_code_by_week_not_historical_release':
            failed.append(week+':snapshot_semantics')
        totals[week]={}
        for entry in manifest['artifacts']+manifest['generated_files']:
            path=(ROOT/entry['path']).resolve()
            if not path.is_relative_to(folder.resolve()) or not path.is_file():
                failed.append(week+':invalid_path:'+entry['path']);continue
            digest=hashlib.sha256(path.read_bytes()).hexdigest()
            if digest!=entry['sha256']:failed.append(week+':hash:'+entry['path'])
            if 'bytes' in entry and path.stat().st_size!=entry['bytes']:failed.append(week+':size:'+entry['path'])
            if path.suffix=='.py':ast.parse(path.read_text(encoding='utf-8-sig'))
            if 'kind' in entry:totals[week][entry['kind']]=totals[week].get(entry['kind'],0)+1
            count+=1
        for link in re.findall(r'\]\(([^)]+)\)',(folder/'README.md').read_text(encoding='utf-8')):
            if link.startswith(('http:','https:','#')):continue
            target=(folder/link.split('#')[0]).resolve()
            if not target.is_relative_to(ROOT.resolve()) or not target.exists():failed.append(week+':broken_link:'+link)
        for name in ['metrics.csv','test-results.json']:
            if (folder/name).read_bytes()!=(ROOT/'Evidence'/week/name).read_bytes():failed.append(week+':evidence_changed:'+name)
    result={'status':'passed' if not failed else 'failed','copied_and_generated_file_hashes':count,'weeks':totals,
            'failures':failed,'model_inference':False,'aws_calls':0,'standalone_week_apps_tested':False}
    print(json.dumps(result,indent=2))
    return int(bool(failed))

if __name__=='__main__':raise SystemExit(main())

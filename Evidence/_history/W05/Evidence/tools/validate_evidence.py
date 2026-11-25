"""Validate saved evidence with the Python standard library; no model/API calls."""
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def first_rank(row, method, k):
    gold = set(row['gold_primary_article_ids'])
    return next((i + 1 for i, item in enumerate(row['rankings'][method][:k]) if item['article_id'] in gold), None)

def aggregate(rows, method, ks):
    result = {}
    for k in ks:
        result[f'recall@{k}'] = sum(first_rank(row, method, k) is not None for row in rows) / len(rows)
    k = max(ks)
    result[f'mrr@{k}'] = sum(1 / rank if (rank := first_rank(row, method, k)) else 0 for row in rows) / len(rows)
    return result

def stats(values):
    values = sorted(values)
    at = (len(values) - 1) * .95
    i = int(at)
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2
    return {'mean': sum(values) / len(values), 'median': median, 'p95': values[i] + (values[min(i + 1, len(values) - 1)] - values[i]) * (at - i)}

def tables(root=ROOT):
    shared = root / 'Evidence/_shared'
    data = shared / 'data'
    raw = shared / 'measurement_20261031'
    documents = load(data / 'manifest.json')
    validation = load(data / 'validation.json')
    predictions = jsonl(raw / 'rerank_predictions.jsonl')
    with (root / 'data/qa_pilot_50.csv').open(encoding='utf-8-sig', newline='') as stream:
        pilot = list(csv.DictReader(stream))
    output = {}
    headers = ['week', 'method', 'domain', 'n', 'metric', 'value', 'unit', 'k', 'split', 'measured_on']
    for week in ['W01', 'W02', 'W03', 'W04', 'W05']:
        rows = []
        def add(method, domain, n, metric, value, unit='fraction', k=None, split='dev', measured='2026-10-31'):
            rows.append([week, method, domain, n, metric, value, unit, k, split, measured])
        if week == 'W01':
            add('inventory', 'all', 53, 'documents', len(documents), 'count', split='scope', measured='2026-11-01')
            add('inventory', 'all', 50, 'pilot_questions', len(pilot), 'count', split='pilot', measured='2026-11-01')
            for domain, count in Counter(item['domain'] for item in documents).items():
                add('inventory', domain, count, 'documents', count, 'count', split='scope', measured='2026-11-01')
        elif week == 'W02':
            for name, count in validation['nodes'].items():
                add('structural_parser', 'all', 53, name + '_nodes', count, 'count', split='corpus_v1', measured='2026-11-01')
            for name, value in [('chunks', validation['chunks']), ('tables_read', validation['tables_read']), ('duplicate_marker_warnings', len(validation['warnings']))]:
                add('structural_parser', 'all', 53, name, value, 'count', split='corpus_v1', measured='2026-11-01')
        else:
            selected = [r for r in predictions if r['baseline']] if week == 'W03' else [r for r in predictions if r['w4']] if week == 'W04' else predictions
            methods = ['dense'] if week == 'W03' else ['dense', 'bm25', 'hybrid_rrf'] if week == 'W04' else ['w5_without_ce', 'w5_with_ce']
            ks = [1, 3, 5, 10, 20, 50] if week != 'W05' else [1, 3, 5]
            for domain in ['all', 'giaoThong_VanTai', 'laoDong_TienLuong']:
                group = selected if domain == 'all' else [r for r in selected if r['domain'] == domain]
                for method in methods:
                    for metric, value in aggregate(group, method, ks).items():
                        add(method, domain, len(group), metric, value, k=int(metric.split('@')[1]))
            if week == 'W04':
                for method in methods:
                    for statistic, value in stats([r['latency_excludes_query_embedding_ms'][method] for r in selected]).items():
                        add(method, 'all', len(selected), 'latency_' + statistic, value, 'ms_excluding_query_embedding')
            if week == 'W05':
                chunks = {c['id']: c for c in jsonl(data / 'chunks.jsonl')}
                coverage = sum(any(chunks[c]['metadata']['article_id'] in row['gold_primary_article_ids'] for c in row['candidate_chunk_ids']) for row in selected)
                add('candidate_pool', 'all', 200, 'gold_coverage@20', coverage / 200, k=20)
                pairs = Counter((first_rank(r, 'w5_without_ce', 5) is not None, first_rank(r, 'w5_with_ce', 5) is not None) for r in selected)
                for name, pair in [('both_hit', (True, True)), ('improved', (False, True)), ('regressed', (True, False)), ('both_miss', (False, False))]:
                    add('paired_ablation', 'all', 200, name, pairs[pair], 'count', k=5)
                for statistic, value in stats([r['latency_excludes_query_embedding_ms']['ce_added'] for r in selected]).items():
                    add('crossencoder', 'all', 200, 'added_latency_' + statistic, value, 'ms_rerank_only')
        output[week] = [headers] + rows
    return output

def validate(root=ROOT):
    shared = root / 'Evidence/_shared'
    data = shared / 'data'
    raw = shared / 'measurement_20261031'
    reports = {}
    def check(week, name, condition, detail):
        reports.setdefault(week, []).append({'name': name, 'status': 'passed' if condition else 'failed', 'detail': detail})
    documents = load(data / 'manifest.json')
    docs = {d['id']: d for d in jsonl(data / 'documents.jsonl')}
    nodes = jsonl(data / 'legal_nodes.jsonl')
    by_node = {n['id']: n for n in nodes}
    chunks = jsonl(data / 'chunks.jsonl')
    by_chunk = {c['id']: c for c in chunks}
    with (root / 'data/qa_pilot_50.csv').open(encoding='utf-8-sig', newline='') as stream:
        pilot = list(csv.DictReader(stream))
    check('W01', 'corpus_scope_and_count', len(documents) == 53 and Counter(d['domain'] for d in documents) == {'giaoThong_VanTai': 38, 'laoDong_TienLuong': 15}, '53 DOCX in two approved domains')
    check('W01', 'docx_source_hashes', all((root / d['source_file']).is_file() and sha(root / d['source_file']) == d['source_sha256'] for d in documents), 'Compare all 53 DOCX with source SHA-256')
    check('W01', 'pilot_count_and_ids', len(pilot) == 50 and len({r['qa_id'] for r in pilot}) == 50 and Counter(r['domain'] for r in pilot) == {'giaoThong_VanTai':25,'laoDong_TienLuong':25}, '50 existing pilot rows, 25 per domain; human/legal review not performed here')
    check('W02', 'node_identifiers_unique', len(nodes) == len(by_node) == 14935, '1776 articles + 6527 clauses + 6632 points')
    check('W02', 'parent_child_integrity', all(n['parent_id'] is None or n['parent_id'] in by_node and by_node[n['parent_id']]['document_id'] == n['document_id'] for n in nodes), 'Existing parent IDs belong to same document')
    check('W02', 'original_text_spans', all(n['text_original'] == docs[n['document_id']]['text_original'][n['start']:n['end']].rstrip('\n') for n in nodes), 'Compare each stored node with its original document text span')
    check('W02', 'chunk_metadata_links', len(chunks) == len(by_chunk) == 6883 and all(c['metadata']['node_id'] in by_node and c['metadata']['article_id'] in by_node and c['metadata']['document_id'] in docs for c in chunks), '6883 chunks; valid node/article/document IDs')
    check('W02', 'duplicate_warnings_retained', len(load(data / 'validation.json')['warnings']) == 9, 'Nine warnings retained for manual inspection, not silently removed')
    predictions = jsonl(raw / 'rerank_predictions.jsonl')
    summary = load(raw / 'evaluation_w1_w5.json')
    run = load(raw / 'measurement_run_manifest.json')
    source_files_valid = all((shared / 'source_snapshot' / name).exists() and sha(shared / 'source_snapshot' / name) == digest for name, digest in run['file_sha256'].items())
    source_files_valid = source_files_valid and all(sha(shared / name) == digest for name, digest in run['file_sha256'].items() if name.startswith('data/'))
    expected_tables = tables(root)
    for week, file, count, flag in [('W03', 'qa_baseline_100.jsonl', 100, 'baseline'), ('W04', 'qa_dev_150.jsonl', 150, 'w4'), ('W05', 'qa_w5_200.jsonl', 200, None)]:
        if not (root / 'Evidence' / week).exists():
            continue
        qa = jsonl(data / file)
        selected = predictions if flag is None else [r for r in predictions if r[flag]]
        check(week, 'qa_and_prediction_ids', len(qa) == len(selected) == count and len({q['id'] for q in qa}) == count and {q['id'] for q in qa} == {r['id'] for r in selected}, f'{count} unique QA IDs match saved predictions')
        by_qa = {q['id']: q for q in qa}
        check(week, 'primary_gold_mapping', all(len(q['relevant_article_ids']) == 1 and q['relevant_article_ids'][0] in by_node for q in qa) and all(r['gold_primary_article_ids'] == by_qa[r['id']]['relevant_article_ids'] for r in selected), 'One existing primary article label per QA; pending human review')
        check(week, 'prediction_chunk_metadata', all(item['chunk_id'] in by_chunk and by_chunk[item['chunk_id']]['metadata']['article_id'] == item['article_id'] for r in selected for ranking in r['rankings'].values() for item in ranking), 'Every saved ranking item maps to the corpus article')
        check(week, 'measurement_inputs_unchanged', source_files_valid, 'Snapshot bytes match all input/source hashes in original measurement manifest')
        methods = ['dense'] if week == 'W03' else ['dense', 'bm25', 'hybrid_rrf'] if week == 'W04' else ['w5_without_ce', 'w5_with_ce']
        ks = [1, 3, 5, 10, 20, 50] if week != 'W05' else [1, 3, 5]
        target = {'dense': summary['w3_dense_100']} if week == 'W03' else summary['w4_retrieval_150'] if week == 'W04' else summary['w5_rerank_200']
        computed = {m: aggregate(selected, m, ks) for m in methods}
        check(week, 'aggregate_metrics_recomputed', all(math.isclose(v, target[m][key], abs_tol=1e-12) for m, metrics in computed.items() for key, v in metrics.items()), 'Independent recomputation from per-query rankings; no model inference')
    if (root / 'Evidence/W05').exists():
        check('W05', 'same_twenty_candidates', len(predictions) == 200 and all(len(r['candidate_chunk_ids']) == len(set(r['candidate_chunk_ids'])) == 20 and [d['chunk_id'] for d in r['rankings']['w5_without_ce']] == r['candidate_chunk_ids'][:5] and len(r['rankings']['w5_with_ce']) == 5 and {d['chunk_id'] for d in r['rankings']['w5_with_ce']}.issubset(r['candidate_chunk_ids']) for r in predictions), 'Both arms use same 20 candidate IDs; reranker output stays inside pool')
    for week in reports:
        path = root / 'Evidence' / week / 'metrics.csv'
        with path.open(encoding='utf-8-sig', newline='') as stream:
            actual = list(csv.reader(stream))
        expected = expected_tables[week]
        valid = len(actual) == len(expected) and actual[0] == expected[0]
        if valid:
            for actual_row, expected_row in zip(actual[1:], expected[1:]):
                if len(actual_row) != len(expected_row): valid = False; break
                for actual_value, expected_value in zip(actual_row, expected_row):
                    if isinstance(expected_value, (int, float)):
                        valid = valid and math.isclose(float(actual_value), expected_value, rel_tol=1e-12, abs_tol=1e-9)
                    else:
                        valid = valid and actual_value == ('' if expected_value is None else expected_value)
        check(week, 'metrics_csv_matches_observations', valid, 'CSV values, units, population and cutoffs match saved observations')
    return reports

def main():
    reports = validate()
    failed = [(week, item['name']) for week, checks in reports.items() for item in checks if item['status'] != 'passed']
    hash_checks = 0
    for directory in sorted((ROOT / 'Evidence').glob('W[0-9][0-9]')):
        manifest_path = directory / 'manifest.json'
        if not manifest_path.exists():
            failed.append((directory.name, 'missing_manifest'))
            continue
        for entry in load(manifest_path)['artifacts']:
            path = ROOT / entry['path']
            hash_checks += 1
            if not path.is_file() or sha(path) != entry['sha256']:
                failed.append((directory.name, 'artifact_hash:' + entry['path']))
    for entry in load(ROOT / 'Evidence/_shared/inventory.json')['artifacts']:
        path = ROOT / entry['path']
        hash_checks += 1
        if not path.is_file() or sha(path) != entry['sha256']:
            failed.append(('shared', 'artifact_hash:' + entry['path']))
    print(json.dumps({'status': 'passed' if not failed else 'failed', 'data_checks': sum(map(len, reports.values())), 'artifact_hash_checks': hash_checks, 'failures': failed, 'llm_calls': 0, 'model_inference': False, 'peer_review': 'pending; not assessed by this validator'}, ensure_ascii=False, indent=2))
    return int(bool(failed))

if __name__ == '__main__':
    sys.exit(main())

"""W7 dataset/contract checks; these are not semantic grounding scores."""
import ast
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def jsonl(path):
    return [json.loads(line) for line in (ROOT/path).read_text(encoding='utf-8').splitlines() if line.strip()]


class W7ContractTests(unittest.TestCase):
    def test_qa_schema_and_unique_ids(self):
        rows = jsonl('Evidence/W07/data/qa_candidates_30.jsonl')
        required = {'id','question','category','expected_action','rationale','review_status','split',
                    'supporting_source_ids','checked_source_ids','expected_action_status'}
        self.assertEqual(len(rows), 30)
        self.assertEqual(len({q['id'] for q in rows}), 30)
        self.assertEqual(len({q['question'].strip().casefold() for q in rows}), 30)
        self.assertTrue(all(required <= q.keys() for q in rows))

    def test_provisional_labels_and_action_distribution(self):
        rows = jsonl('Evidence/W07/data/qa_candidates_30.jsonl')
        self.assertEqual(Counter(q['expected_action'] for q in rows), {'refuse':20,'clarify':5,'answer':5})
        self.assertTrue(all(q['review_status']=='pending' and q['expected_action_status']=='provisional_not_human_gold'
                            and q['split']=='w7_dev_candidate_not_independent_test' for q in rows))

    def test_controls_preserve_existing_dev_provenance(self):
        original = {q['id']:q for q in jsonl('data/qa_w5_200.jsonl')}
        controls = [q for q in jsonl('Evidence/W07/data/qa_candidates_30.jsonl') if q['category']=='answerable_control']
        self.assertEqual(len(controls), 5)
        for q in controls:
            source = original[q['source_qa_id']]
            self.assertEqual(q['question'], source['question'])
            self.assertEqual(q['reference_answer'], source['reference_answer'])
            self.assertEqual(q['supporting_source_ids'], source['relevant_article_ids'])

    def test_synthetic_record_markers_absent_from_all_documents(self):
        docs = jsonl('data/documents.jsonl')
        cases = [q for q in jsonl('Evidence/W07/data/qa_candidates_30.jsonl') if q['absence_marker']]
        self.assertEqual(len(docs), 53)
        self.assertEqual(len(cases), 10)
        for q in cases:
            self.assertEqual(set(q['checked_source_ids']), {d['id'] for d in docs})
            self.assertFalse(any(q['absence_marker'].casefold() in d['text_original'].casefold() for d in docs))

    def test_source_ui_static_contract(self):
        js = (ROOT/'app.js').read_text(encoding='utf-8')
        html = (ROOT/'index.html').read_text(encoding='utf-8')
        for token in ['async function openSource','/api/source/','function renderSources','retrieved_sources','showModal()']:
            self.assertIn(token, js)
        self.assertIn('source-dialog', html)
        # Static check, not a browser render, screenshot or accessibility test.

    def test_source_endpoint_and_agent_mapping_contract(self):
        api = (ROOT/'app.py').read_text(encoding='utf-8')
        mapping = (ROOT/'source/agent/demo_agentic.py').read_text(encoding='utf-8')
        self.assertIn("path.startswith('/api/source/')", api)
        self.assertIn('citation_indices', mapping)
        self.assertIn('retrieved_sources', mapping)
        ast.parse(api)
        ast.parse(mapping)

    def test_graph_regeneration_does_not_recheck(self):
        graph = ast.parse((ROOT/'source/agent/graph_orchestrator.py').read_text(encoding='utf-8'))
        node = next(n for n in ast.walk(graph) if isinstance(n, ast.FunctionDef) and n.name=='_regenerate_node')
        calls = [ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)]
        self.assertIn('self._generate_rag_answer', calls)
        self.assertNotIn('self.checker.check', calls)
        self.assertNotIn('self._check_node', calls)


if __name__ == '__main__':
    unittest.main()

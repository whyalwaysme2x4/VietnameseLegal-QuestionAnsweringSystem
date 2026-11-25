import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from source.generate.synthesis_response import SynthesisResponseError,parse_synthesis_response


class ResponseContractTests(unittest.TestCase):
    def response(self,citations,answer='Thông tin từ nguồn.'):
        return json.dumps({'answer':answer,'citations':citations},ensure_ascii=False)

    def test_source_mapping_keeps_one_based_order(self):
        parsed=parse_synthesis_response(self.response([2,1,2]),2)
        sources=['first','second']
        self.assertEqual([sources[k-1] for k in parsed['citations']],['second','first'])

    def test_unambiguous_model_label_formats(self):
        self.assertEqual(parse_synthesis_response(self.response(['2','S1','[S2]']),2)['citations'],[2,1])

    def test_empty_citations_for_clarification(self):
        self.assertEqual(parse_synthesis_response(self.response([],'Bạn cần làm rõ nội dung nào?'),5)['citations'],[])

    def test_json_fence(self):
        self.assertEqual(parse_synthesis_response('```json\n'+self.response([1])+'\n```',1)['citations'],[1])

    def test_invalid_sources_are_not_guessed_or_silently_dropped(self):
        for citations in [[0],[6],[-1],[True],[1.0],['0'],['Điều 7'],['1,2'],[1,99]]:
            with self.subTest(citations=citations),self.assertRaises(SynthesisResponseError):
                parse_synthesis_response(self.response(citations),5)

    def test_bad_schemas_are_rejected(self):
        for obj in [{},{'answer':None,'citations':[]},{'answer':'','citations':[]},
                    {'answer':'a','citations':None},{'answer':'a','citations':1},[]]:
            with self.subTest(obj=obj),self.assertRaises(SynthesisResponseError):
                parse_synthesis_response(json.dumps(obj),5)

    def test_malformed_json(self):
        with self.assertRaises(SynthesisResponseError) as error:parse_synthesis_response('{"answer":',5)
        self.assertEqual(error.exception.code,'invalid_response_json')

    def test_truncation_identified(self):
        with self.assertRaises(SynthesisResponseError) as error:parse_synthesis_response('{"answer":',5,'max_tokens')
        self.assertEqual(error.exception.code,'synthesis_truncated')

    def test_chat_handles_bad_output_without_attaching_uncertain_sources(self):
        # Exercise the actual chat generator, using a fake SDK response only.
        # No Engine initialization, models, credentials or network are involved.
        import runtime
        previous=dict(runtime.STATE)
        try:
            for output in ['{"answer":',self.response([99]),json.dumps({'answer':'a','citations':None})]:
                with self.subTest(output=output):
                    engine=object.__new__(runtime.Engine)
                    engine.retrieve=lambda *args:([('context',{'doc_metadata':{'chunk_id':'fixture'}})],{})
                    engine.source=lambda key:{'id':key,'number':'fixture','article':'fixture','clause':None,'excerpt':'fixture'}
                    engine.refresh_llm=lambda:True
                    engine.model_id='fixture-model'
                    engine.aws_client=SimpleNamespace(converse=lambda **kwargs:{'output':{'message':{'content':[{'text':output}]}},'stopReason':'end_turn'})
                    events=list(engine.chat('Quy định giao thông','giaoThong_VanTai','hybrid'))
                    final=events[-1]
                    self.assertEqual(final['type'],'final')
                    self.assertEqual(final['answer_status'],'invalid_model_response')
                    self.assertEqual(final['sources'],[])
                    self.assertEqual([s['id'] for s in final['retrieved_sources']],['fixture'])
                    self.assertEqual(final['trace'][0]['llm_calls'],1)
                    self.assertNotIn('fixture',final['answer'])
        finally:runtime.STATE.clear();runtime.STATE.update(previous)

    def test_ready_only_after_engine_is_published(self):
        import runtime
        previous=dict(runtime.STATE);previous_engine=runtime.ENGINE
        engine=object()
        def construct():
            self.assertFalse(runtime.STATE['ready'])
            self.assertIsNone(runtime.ENGINE)
            return engine
        try:
            with patch.object(runtime,'Engine',side_effect=construct):runtime.build_engine()
            self.assertIs(runtime.ENGINE,engine)
            self.assertTrue(runtime.STATE['ready'])
        finally:
            runtime.STATE.clear();runtime.STATE.update(previous);runtime.ENGINE=previous_engine

    def test_failed_startup_never_leaves_ready_true(self):
        import runtime
        previous=dict(runtime.STATE);previous_engine=runtime.ENGINE
        try:
            with patch.object(runtime,'Engine',side_effect=RuntimeError('fixture')),patch('traceback.print_exc'):
                runtime.build_engine()
            self.assertFalse(runtime.STATE['ready'])
            self.assertIsNone(runtime.ENGINE)
        finally:
            runtime.STATE.clear();runtime.STATE.update(previous);runtime.ENGINE=previous_engine

if __name__=='__main__':unittest.main()

"""Fifteen deterministic agent cases, including parity against the copied source."""
import contextlib
import io
import json
import unittest
from pathlib import Path
from types import SimpleNamespace

import torch
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from source.agent.planner import PlannerAgent
from source.agent.grader import GraderAgent
from source.agent.hallucination_checker import HallucinationChecker
from source.agent.orchestrator import Orchestrator
from source.agent.graph_orchestrator import GraphOrchestrator
from source.agent.corpus_scope import load_scope
from source.extract.utils_extract import Extract_Information
from source.generate.generate import Gemini_Generate
from source.rerank.utils_rerank import Rerank_Utils
from source.search.utils_search import Qdrant_Utils
from source.search.scoped_qdrant import ScopedQdrantUtils

ROOT=Path(__file__).resolve().parents[1]
CASES=json.loads((ROOT/'tests/agent_cases_w6.json').read_text(encoding='utf-8'))['cases']
TRACES={}

class FixtureGenerator(Gemini_Generate):
    def __init__(self, case):
        self.case=case;self.settings=SimpleNamespace(YAML_PATH='gemini_prompting.yaml');self.yaml_path=self.settings
        self.calls=[];self.prompts=[];self.generated_queries=[];self.response_count=0;self.grade_count=0;self.check_count=0

    def generate_query(self, original_query, memory_context=''):
        self.generated_queries.append(original_query)
        return [original_query]+[original_query+f' biến thể tìm kiếm số {i}' for i in range(1,4)]

    def _make_model(self, temperature=0.0, max_tokens=4096, top_p=1.0):
        def invoke(messages):
            self.calls.append(max_tokens);self.prompts.append((max_tokens,'\n'.join(str(m.content) for m in messages)))
            scenario=self.case['scenario']
            if max_tokens==800:
                if scenario=='provider_error':raise RuntimeError('fixture provider unavailable')
                if scenario=='planner_parse':return 'invalid planner JSON'
                plan={'intent':'out_of_scope' if scenario=='outside' else 'legal','tool':'rag','rewritten_query':self.case['question'],
                      'reason':'Fixture routing decision','entities':None}
                if scenario in ['entities','retry','best']:
                    plan['entities']={'LoaiVanBanFilter':'Luật','NoibanHanhFilter':None,'NgayBanHanhFilter':''}
                return json.dumps(plan,ensure_ascii=False)
            if max_tokens==500:
                self.grade_count+=1
                if scenario=='grader_parse':return 'invalid grader JSON'
                score=.8;decision='sufficient';suggested=None
                if scenario=='retry' and self.grade_count==1:score=.2;decision='insufficient';suggested='truy vấn thứ hai theo grader'
                if scenario=='best':score=.55 if self.grade_count==1 else .2;decision='partial';suggested='truy vấn thứ hai theo grader'
                if scenario=='partial_high':score=.7;decision='partial'
                return json.dumps({'relevance_score':score,'decision':decision,'reason':'Fixture grade','missing_aspects':[], 'suggested_query':suggested},ensure_ascii=False)
            if max_tokens==600:
                self.check_count+=1
                if scenario=='checker_parse':return 'invalid checker JSON'
                grounded=scenario not in ['regenerate','single_claim','low_confidence'];confidence=.7 if scenario=='low_confidence' else .8
                claims=[] if grounded else ['fixture claim A'] if scenario=='single_claim' else ['fixture claim A','fixture claim B']
                return json.dumps({'is_grounded':grounded,'confidence':confidence,'unsupported_claims':claims,'reason':'Fixture check'})
            if max_tokens==8192:
                self.response_count+=1
                keys=[] if scenario=='empty' else [-1,99,1] if scenario=='labour' else [1] if scenario=='regenerate' and self.response_count==2 else [0]
                return json.dumps({'answer':'Fixture answer '+str(self.response_count),'key':keys})
            return 'Bản demo hỗ trợ hai lĩnh vực trong corpus đã chốt.'
        return RunnableLambda(invoke)


class FixtureSearch(Qdrant_Utils):
    def __init__(self,case):self.case=case;self.calls=[];self.filters=[]
    def build_metadata_filter(self,entities):
        result=super().build_metadata_filter(entities);self.filters.append(result);return result
    def search_documents(self,query,top_k=25,filter=None):
        round=len(self.calls)//4;self.calls.append((query,filter))
        if self.case['scenario']=='empty':return []
        label='A' if round==0 else 'B'
        return [(Document(page_content=f'Nguồn_{label}_{i} chứa toàn bộ căn cứ và các nội dung bổ sung.',metadata={
            'chunk_id':f'fixture-{label}-{i}','article_id':f'fixture-{label}/article-{i}',
            'SoHieu':f'fixture-{label}','Article':f'Điều {i+1}','LoaiVanBan':'Luật','NoiBanHanh':'Quốc hội'}),1-i*.1) for i in range(2)]


class FixtureTokenizer:
    def __init__(self):self.calls=[]
    def __call__(self,question,context,**kwargs):
        self.calls.append(kwargs)
        return {'input_ids':torch.tensor([[0,1,2,3]]),'attention_mask':torch.ones((1,4),dtype=torch.long),
                'offset_mapping':torch.tensor([[[0,0],[0,4],[5,10],[0,0]]])}


class FixtureBert:
    def __init__(self):
        self.tokenizer=FixtureTokenizer();self.max_length=512;self.max_answer_length=2000;self.stride=150;self.nbert=380
        self.model_extract=lambda **kwargs:SimpleNamespace(start_logits=torch.tensor([[0.,5.,1.,0.]]),end_logits=torch.tensor([[0.,1.,5.,0.]]))


class FixtureCrossEncoder:
    def __init__(self):self.calls=[]
    def predict(self,pairs):self.calls.append(pairs);return [float(len(pairs)-i) for i in range(len(pairs))]


def build(case, cls):
    generator=FixtureGenerator(case);search=FixtureSearch(case);bert=FixtureBert();ce=FixtureCrossEncoder()
    reranker=Rerank_Utils(SimpleNamespace(model=ce))
    agent=cls(planner=PlannerAgent(generator),grader=GraderAgent(generator),checker=HallucinationChecker(generator),
              generator=generator,qdrant_utils=search,rerank_utils=reranker,extract_utils=Extract_Information(bert),
              search_tools=None,memory=None,settings=generator.settings,embedding=None,max_iterations=2)
    return agent,generator,search,bert,ce


def events(agent,question):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return [json.loads(frame.removeprefix('data: ').strip()) for frame in agent.run(question,None,False)]


def normalized(frames):
    keys={'type','agent','intent','tool','rewritten_query','entities','query','iteration','n_docs','n_snippets',
          'decision','relevance_score','missing_aspects','next_iteration','next_query','answer','references',
          'is_grounded','confidence','unsupported_claims','regenerated','n_citations','question'}
    return [{k:v for k,v in event.items() if k in keys} for event in frames if event['type']!='graph_node']


class AgentPolicyTests(unittest.TestCase):
    def exercise(self,case):
        original,*_=build(case,Orchestrator)
        expected=events(original,case['question'])
        graph,generator,search,bert,ce=build(case,GraphOrchestrator)
        actual=events(graph,case['question']);TRACES[case['id']]=actual
        self.assertEqual(normalized(actual),normalized(expected),'Graph behavior differs from original policy')
        self.assertTrue(any(e['type']=='graph_node' and e['node']=='planner' for e in actual))
        scope=load_scope();self.assertEqual(len(scope['documents']),53)
        planner_prompt=next(text for tokens,text in generator.prompts if tokens==800)
        self.assertTrue(all(d['id'] in planner_prompt for d in scope['documents']))
        self.assertNotIn('thụ tinh trong ống nghiệm',planner_prompt)
        self.assertNotIn('Input: "điều kiện kết hôn',planner_prompt)
        self.assertLessEqual(len(search.calls),8)
        if bert.tokenizer.calls:
            args=bert.tokenizer.calls[0]
            self.assertEqual(args['max_length'],512);self.assertEqual(args['stride'],150)
            self.assertEqual(args['truncation'],'only_second');self.assertNotIn('return_overflowing_tokens',args)
        scenario=case['scenario'];grades=[e for e in actual if e['type']=='grade'];checks=[e for e in actual if e['type']=='check']
        finals=[e for e in actual if e['type']=='final'];regens=[e for e in actual if e['type']=='regenerate']
        if scenario=='provider_error':
            self.assertFalse(finals);errors=[e for e in actual if e['type']=='error'];self.assertEqual(len(errors),1);self.assertEqual(errors[0]['agent'],'planner');return
        self.assertEqual(len(finals),1)
        if scenario=='outside':
            self.assertEqual(search.calls,[]);self.assertEqual(bert.tokenizer.calls,[]);self.assertEqual(checks,[]);return
        if scenario=='empty':
            self.assertEqual([g['relevance_score'] for g in grades],[0.,0.]);self.assertFalse(bert.tokenizer.calls);self.assertFalse(checks)
            self.assertEqual(finals[0]['references'],[]);return
        self.assertTrue(bert.tokenizer.calls)
        response_prompts=[text for tokens,text in generator.prompts if tokens==8192]
        self.assertTrue(all('BERT highlight' in text and 'nội dung bổ sung' in text for text in response_prompts))
        self.assertTrue(all(0<=i<2 for i in finals[0]['citation_indices'] if i not in [-1,99]))
        if scenario=='labour':
            self.assertEqual(finals[0]['citation_indices'],[-1,99,1]);self.assertEqual(len(finals[0]['references']),1)
            self.assertIn('Nguồn A 1',finals[0]['references'][0])
        if scenario=='entities':
            self.assertEqual(len(search.filters),1);self.assertEqual(len(search.filters[0].should),1)
            self.assertEqual(search.filters[0].should[0].key,'metadata.LoaiVanBanFilter')
            self.assertTrue(all(filter is search.filters[0] for _,filter in search.calls))
        if scenario in ['retry','best']:
            self.assertEqual(len(search.calls),8);self.assertEqual(len(grades),2)
            self.assertEqual(generator.generated_queries[1],'truy vấn thứ hai theo grader')
            self.assertEqual(search.filters[0].model_dump(),search.filters[1].model_dump())
        if scenario=='best':self.assertTrue(all('Nguồn A' in text and 'Nguồn B' not in text for text in response_prompts))
        if scenario=='retry':self.assertTrue(all('Nguồn B' in text for text in response_prompts))
        if scenario=='grader_parse':self.assertEqual(grades[0]['relevance_score'],.6);self.assertEqual(grades[0]['decision'],'sufficient')
        if scenario=='partial_high':self.assertEqual(len(search.calls),4);self.assertEqual(grades[0]['decision'],'partial')
        if scenario=='checker_parse':self.assertTrue(checks[0]['is_grounded']);self.assertEqual(checks[0]['confidence'],.3)
        if scenario=='regenerate':
            self.assertEqual(len(regens),1);self.assertEqual(generator.response_count,2);self.assertEqual(generator.check_count,1)
            self.assertEqual(finals[0]['citation_indices'],[1])
        else:self.assertFalse(regens)
        # Legacy checker sees only cited chunk(s), not the BERT hint or all distractors.
        checker_prompt=next(text for tokens,text in generator.prompts if tokens==600)
        self.assertNotIn('BERT highlight',checker_prompt)
        if scenario!='labour':self.assertNotIn('Nguồn A 1',checker_prompt)
        metadata=ScopedQdrantUtils.payload_metadata({'NoiBanHanh':'Quốc hội','LoaiVanBan':'Luật','NgayBanHanh':'20/11/2019'})
        self.assertEqual(metadata['NgayBanHanhFilter'],['20-11-2019','2019'])


def method(case):
    def run(self):self.exercise(case)
    run.__doc__=case['name'];return run

for case in CASES:
    setattr(AgentPolicyTests,'test_'+case['id'],method(case))

if __name__=='__main__':unittest.main()

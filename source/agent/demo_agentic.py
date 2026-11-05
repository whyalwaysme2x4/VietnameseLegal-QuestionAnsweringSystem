"""Composition root for original agents + BERT + scoped storage in the demo."""
import json
from pathlib import Path
from types import SimpleNamespace

from source.agent.graph_orchestrator import GraphOrchestrator
from source.agent.planner import PlannerAgent
from source.agent.grader import GraderAgent
from source.agent.hallucination_checker import HallucinationChecker
from source.extract.utils_extract import Extract_Information
from source.model.extract_model import Bert_Extract
from source.model.nova_converse import NovaConverseGenerate
from source.model.rerank_model_finetune import RerankModelFinetune
from source.rerank.utils_rerank import Rerank_Utils
from source.search.scoped_qdrant import ScopedQdrantUtils


class DemoAgentic:
    def __init__(self, engine, root):
        self.root=Path(root);self.engine=engine
        registry=json.loads((self.root/'models.json').read_text(encoding='utf-8'))
        bert=self.root/registry['bert']['path']
        if not (bert/'model.safetensors').exists():raise RuntimeError('Prepare the pinned BERT checkpoint with download_models.py')
        self.settings=SimpleNamespace(MODEL_EXTRACT=str(bert),TOKENIZER=str(bert),MAX_LENGTH=512,STRIDE=150,N_BEST=380,MAX_ANSWER_LENGTH=2000,
            RERANK=str(self.root/registry['reranker']['path']),YAML_PATH='gemini_prompting.yaml',PATH_INFOR='information.json',
            MAX_ITERATIONS=2,GRADER_THRESHOLD=0.6,HALLUCINATION_CHECK_ENABLED=True)
        self.generator=NovaConverseGenerate(engine,self.settings)
        self.bert=Bert_Extract(self.settings)
        self.extractor=Extract_Information(self.bert)
        # Separate original reranker instance. Do not inherit the W5 512-token/
        # batch-4 override or truncate the original RRF top-50 to 20 candidates.
        self.rerank=Rerank_Utils(RerankModelFinetune(self.settings))
        self.search=ScopedQdrantUtils(engine,self.root)
        self.orchestrator=GraphOrchestrator(planner=PlannerAgent(self.generator),grader=GraderAgent(self.generator,threshold=0.6),
            checker=HallucinationChecker(self.generator),generator=self.generator,qdrant_utils=self.search,
            rerank_utils=self.rerank,extract_utils=self.extractor,search_tools=None,memory=None,
            settings=self.settings,embedding=SimpleNamespace(embeddings_bkai=engine.embedding),max_iterations=2)

    def chat(self, question, domain):
        self.search.domain=domain;self.generator.usage=[];trace=[]
        for frame in self.orchestrator.run(question,session_id=None,web_search_enabled=False):
            event=json.loads(frame.removeprefix('data: ').strip())
            if event['type'] in {'graph_node','plan','grade','check','extract','iterate','regenerate','retrieve_done','generate_done'}:
                trace.append(dict(event))
            if event['type']=='final':
                ids=event.get('selected_chunk_ids',[]);indices=event.get('citation_indices',[])
                candidates=[self.engine.source(key) for key in ids if key in self.engine.by_id]
                cited=[self.engine.source(ids[i]) for i in indices if 0<=i<len(ids) and ids[i] in self.engine.by_id]
                event.update(sources=cited,retrieved_sources=candidates,llm=bool(self.generator.usage),mode='agentic',
                    trace=list(trace),usage=self.generator.usage,llm_calls=len(self.generator.usage),citation_base=0)
            yield event

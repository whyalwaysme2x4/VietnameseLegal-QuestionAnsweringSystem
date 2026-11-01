"""W1-W5 demo: retrieval, optional CrossEncoder, one grounded Nova call."""
import hashlib,json,os,re,sys,threading,time,uuid
from pathlib import Path
from types import SimpleNamespace
from source.generate.synthesis_response import SynthesisResponseError,parse_synthesis_response
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
os.environ['HF_HOME']=str(HERE/'.cache/huggingface')
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
STATE={'ready':False,'phase':'starting','progress':0,'llm_ready':False,'last_error':None}
LOCK=threading.Lock()
MODES={'dense','hybrid','rerank'}
BRANCH_K=25
CANDIDATE_K=20
TOP_K=5
def lines(path):return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
def norm(text):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFD',text.lower().replace('đ','d')) if unicodedata.category(c)!='Mn')

class Engine:
    def __init__(self):
        import numpy as np,torch
        from dotenv import load_dotenv
        load_dotenv(HERE/'.env',override=True)
        torch.set_num_threads(min(8,os.cpu_count() or 4))
        self.np=np
        self.chunks=lines(HERE/'data/chunks.jsonl');self.by_id={c['id']:c for c in self.chunks}
        self.nodes={n['id']:n for n in lines(HERE/'data/legal_nodes.jsonl')}
        self.models=json.loads((HERE/'models.json').read_text(encoding='utf-8'))
        settings=SimpleNamespace(MODEL_EMBEDDING=str(HERE/self.models['embedding']['path']),DEVICE={'device':'cpu'},
                                 RERANK=str(HERE/self.models['reranker']['path']))
        from source.model.embedding_model import Sentences_Transformer_Embedding
        from source.model.rerank_model_finetune import RerankModelFinetune
        from source.rerank.utils_rerank import Rerank_Utils
        from pyvi import ViTokenizer
        self.tokenize=ViTokenizer.tokenize
        STATE['phase']='loading_embedding'
        self.embedding=Sentences_Transformer_Embedding(settings).embeddings_bkai
        self.embedding.encode_kwargs.update(batch_size=16)
        STATE.update(phase='tokenizing_corpus',total=len(self.chunks))
        tokenfile=HERE/'index/tokenized.json'
        datahash=hashlib.sha256((HERE/'data/chunks.jsonl').read_bytes()).hexdigest()
        cached=json.loads(tokenfile.read_text(encoding='utf-8')) if tokenfile.exists() else {}
        self.tokenized=cached.get('texts') if cached.get('corpus_hash')==datahash else None
        if self.tokenized is None:
            self.tokenized=[self.tokenize(c['text']) for c in self.chunks]
            tokenfile.parent.mkdir(parents=True,exist_ok=True)
            tokenfile.write_text(json.dumps({'corpus_hash':datahash,'texts':self.tokenized},ensure_ascii=False),encoding='utf-8')
        fingerprint=hashlib.sha256((HERE/'data/chunks.jsonl').read_bytes()+self.models['embedding']['revision'].encode()).hexdigest()
        keyfile=HERE/'index/fingerprint.txt'
        if keyfile.exists() and keyfile.read_text()!=fingerprint:raise RuntimeError('Changed corpus/model: create a separate versioned index')
        keyfile.parent.mkdir(parents=True,exist_ok=True);keyfile.write_text(fingerprint)
        vectors=[];cache=HERE/'index/embedding_batches';cache.mkdir(exist_ok=True)
        STATE.update(phase='embedding_corpus',progress=0)
        for start in range(0,len(self.chunks),32):
            path=cache/f'{start:06d}.npy'
            if path.exists():batch=np.load(path,allow_pickle=False)
            else:
                batch=np.asarray(self.embedding.embed_documents(self.tokenized[start:start+32]),dtype=np.float32);np.save(path,batch)
            if len(batch)!=len(self.chunks[start:start+32]):raise RuntimeError('Invalid embedding cache batch')
            vectors.append(batch);STATE['progress']=min(start+32,len(self.chunks))
        vectors=np.concatenate(vectors)
        from qdrant_client import QdrantClient,models
        self.collection='legalqa_w1_w5_corpus_v1'
        self.client=QdrantClient(path=str(HERE/'index/qdrant'))
        exists=self.client.collection_exists(self.collection)
        if not exists:self.client.create_collection(self.collection,vectors_config=models.VectorParams(size=vectors.shape[1],distance=models.Distance.COSINE))
        STATE['phase']='indexing_qdrant'
        if self.client.count(self.collection,exact=True).count!=len(self.chunks):
            for start in range(0,len(self.chunks),128):
                self.client.upsert(self.collection,points=[models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL,c['id'])),
                    vector=vectors[start+i].tolist(),payload={'page_content':self.tokenized[start+i],'metadata':c['metadata']})
                    for i,c in enumerate(self.chunks[start:start+128])],wait=True)
        from rank_bm25 import BM25Okapi
        self.bm25=BM25Okapi([s.lower().split() for s in self.tokenized])
        STATE['phase']='loading_crossencoder'
        self.rerank=Rerank_Utils(RerankModelFinetune(settings));self.rerank.model_finetune.max_length=512
        self.ce_device='cuda' if torch.cuda.is_available() else 'cpu'
        self.rerank.model_finetune.model.to(self.ce_device)
        # Smaller batches reduce padding and fit the laptop GPU; weights and FP32 stay unchanged.
        from functools import partial
        self.rerank.model_finetune.predict=partial(self.rerank.model_finetune.predict,batch_size=4)
        STATE.update(phase='configuring_llm',ready=False,dimension=int(vectors.shape[1]),points=self.client.count(self.collection,exact=True).count,
                     components={'dense':True,'bm25':True,'rrf':True,'crossencoder':True},
                     pipeline='Dense/BM25 → RRF → optional CrossEncoder → Nova Micro',qa_w5=200,ce_device=self.ce_device,ce_batch_size=4)
        self.aws_client=None;self.refresh_llm()

    def dense(self,question,k=50,domain='all',vector=None):
        from qdrant_client.models import Filter,FieldCondition,MatchValue
        from langchain_core.documents import Document
        filtering=Filter(must=[FieldCondition(key='metadata.domain',match=MatchValue(value=domain))]) if domain!='all' else None
        if vector is None:vector=self.embedding.embed_query(self.tokenize(question))
        points=self.client.query_points(self.collection,query=list(map(float,vector)),limit=k,query_filter=filtering,with_payload=True).points
        return [(Document(page_content=p.payload['page_content'],metadata=p.payload['metadata']),p.score) for p in points]

    def lexical(self,question,k=50,domain='all'):
        from langchain_core.documents import Document
        scores=self.bm25.get_scores(self.tokenize(question).lower().split());out=[]
        for i in self.np.argsort(scores)[::-1]:
            c=self.chunks[int(i)]
            if domain!='all' and c['metadata']['domain']!=domain:continue
            if scores[i]<=0:break
            out.append((Document(page_content=self.tokenized[int(i)],metadata=c['metadata']),float(scores[i])))
            if len(out)>=k:break
        return out

    def retrieve(self,question,domain,mode):
        t=time.perf_counter();dense=self.dense(question,BRANCH_K,domain)
        dense_ms=(time.perf_counter()-t)*1000
        if mode=='dense':
            fused=[(d.page_content,{'doc_metadata':d.metadata,'score':score}) for d,score in dense]
            bm25=[]
        else:
            bm25=self.lexical(question,BRANCH_K,domain)
            fused=self.rerank.reciprocal_rank_fusion([dense,bm25])
        candidates=fused[:CANDIDATE_K]
        trace={'mode':mode,'query_variants':1,'dense_count':len(dense),'bm25_count':len(bm25),'fused_count':len(fused),
               'candidate_k':CANDIDATE_K,'top_k':TOP_K,'dense_ms':round(dense_ms,2)}
        return candidates,trace

    def rerank_candidates(self,question,candidates):
        ranked=self.rerank.rerank_documents_finetune(question,candidates) if candidates else []
        if candidates and len(ranked)!=min(TOP_K,len(candidates)):raise RuntimeError('CrossEncoder returned invalid candidates')
        return ranked

    def refresh_llm(self):
        from dotenv import load_dotenv
        load_dotenv(HERE/'.env',override=True)
        self.profile=os.getenv('AWS_PROFILE','legalqa-w4');self.region=os.getenv('AWS_REGION','us-east-1')
        self.model_id=os.getenv('BEDROCK_MODEL_ID','us.amazon.nova-micro-v1:0')
        if self.profile!='legalqa-w4' or self.model_id!='us.amazon.nova-micro-v1:0':
            STATE.update(llm_ready=False,llm_status='unexpected_profile_or_model');return False
        try:
            import boto3
            from botocore.config import Config
            session=boto3.Session(profile_name=self.profile,region_name=self.region)
            creds=session.get_credentials()
            if not creds:raise RuntimeError('NoCredentials')
            creds.get_frozen_credentials()
            if self.aws_client is None:self.aws_client=session.client('bedrock-runtime',config=Config(connect_timeout=8,read_timeout=60,retries={'max_attempts':0}))
            STATE.update(llm_ready=True,llm_status=STATE.get('llm_status') if STATE.get('llm_status')=='inference_verified' else 'credentials_available',llm_model=self.model_id)
            return True
        except Exception as error:
            STATE.update(llm_ready=False,llm_status=type(error).__name__);return False

    def source(self,key):
        c=self.by_id[key];md=c['metadata'];n=self.nodes[md['node_id']]
        return {'id':key,'number':md['SoHieu'],'title':md['ChuDe'],'article':md['Article'],'clause':md.get('clause_number'),
                'issuer':md['NoiBanHanh'],'issued':md['NgayBanHanh'],'domain':md['domain'],'text':n['text_original'],
                'excerpt':c['text'],'node_id':n['id'],'parent_id':n['parent_id'],'source_file':md['source_file'],'legal_status':'unverified'}

    def chat(self,question,domain,mode):
        STATE.update(request_stage='scope',last_request_error=None)
        # Scope keywords are a lightweight guard, not a certified classifier.
        if any(x in norm(question) for x in ['ly hon','ket hon','khai sinh','thoi tiet','bong da','chung khoan','dat dai']):
            yield {'type':'final','answer':'Bản demo hỗ trợ Giao thông vận tải và Lao động tiền lương trong corpus đã chọn.','sources':[],'llm':False};return
        yield {'type':'retrieve_start'}
        STATE['request_stage']='retrieval'
        candidates,trace=self.retrieve(question,domain,mode)
        yield {'type':'retrieve_done','n_docs':len(candidates)}
        if mode=='rerank':
            STATE['request_stage']='rerank'
            yield {'type':'rerank_start'};t=time.perf_counter();selected=self.rerank_candidates(question,candidates)
            trace['rerank_ms']=round((time.perf_counter()-t)*1000,2)
            yield {'type':'rerank_done','n_docs':len(selected)}
        else:selected=candidates[:TOP_K]
        sources=[self.source(info['doc_metadata']['chunk_id']) for _,info in selected]
        trace['selected_chunk_ids']=[s['id'] for s in sources]
        if not sources:
            yield {'type':'final','answer':'Chưa tìm được căn cứ phù hợp trong corpus.','sources':[],'llm':False,'trace':[trace]};return
        if not self.refresh_llm():
            yield {'type':'final','answer':'Retrieval đã chạy thật. Phiên AWS chưa sẵn sàng để tổng hợp câu trả lời; bạn có thể đọc các nguồn truy xuất bên cạnh.',
                   'sources':[],'retrieved_sources':sources,'llm':False,'trace':[trace]};return
        yield {'type':'generate_start'}
        STATE['request_stage']='generation'
        prompt=(HERE/'prompts/synthesis.txt').read_text(encoding='utf-8')
        context='\n\n'.join(f"[S{i+1}] {s['number']} | {s['article']} | Khoản {s['clause'] or 'không đánh số'}\n{s['excerpt']}" for i,s in enumerate(sources))
        result=self.aws_client.converse(modelId=self.model_id,system=[{'text':prompt}],
            messages=[{'role':'user','content':[{'text':json.dumps({'question':question,'sources':context},ensure_ascii=False)}]}],
            inferenceConfig={'maxTokens':1200,'temperature':0.1})
        STATE['llm_status']='inference_verified';trace['llm_calls']=1;trace['usage']=result.get('usage',{})
        STATE['request_stage']='synthesis_response'
        text=''.join(p.get('text','') for p in result['output']['message']['content']).strip()
        try:obj=parse_synthesis_response(text,len(sources),result.get('stopReason'))
        except SynthesisResponseError as error:
            STATE['last_request_error']={'stage':'synthesis_response','code':error.code,'error_type':type(error).__name__}
            trace['response_warning']=error.code
            yield {'type':'final','answer':'Chưa thể tạo câu trả lời có dẫn nguồn hợp lệ cho lượt này. Bạn có thể nêu rõ tình huống hoặc nội dung muốn tra cứu; các đoạn bên cạnh chỉ là ứng viên truy xuất, chưa phải căn cứ xác nhận câu trả lời.',
                   'sources':[],'retrieved_sources':sources,'llm':True,'answer_status':'invalid_model_response','code':error.code,'mode':mode,'trace':[trace]}
            return
        cited=[sources[k-1] for k in obj['citations']]
        yield {'type':'generate_done'}
        STATE['request_stage']='complete'
        yield {'type':'final','answer':obj['answer'],'sources':cited,'retrieved_sources':sources,'llm':True,'answer_status':'generated','mode':mode,'trace':[trace]}

ENGINE=None
def build_engine():
    global ENGINE
    ENGINE=None
    STATE.update(ready=False,phase='starting',last_error=None)
    try:
        engine=Engine()
        ENGINE=engine
        STATE.update(phase='ready',ready=True)
    except Exception as error:
        STATE.update(phase='failed',ready=False,last_error=type(error).__name__)
        import traceback;traceback.print_exc()

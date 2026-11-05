"""Offline asset smoke: real BERT + original CE loader + cached-vector scoped index.

No AWS, no new embedding computation and no retrieval-quality benchmark.
"""
import hashlib
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.environ['HF_HOME']=str(ROOT/'.cache/huggingface')
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
os.environ['TOKENIZERS_PARALLELISM']='false'

def rows(path):return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def main():
    import numpy as np
    import torch
    torch.set_num_threads(8)
    from pyvi import ViTokenizer
    from source.model.extract_model import Bert_Extract
    from source.extract.utils_extract import Extract_Information
    from source.model.rerank_model_finetune import RerankModelFinetune
    from source.search.scoped_qdrant import ScopedQdrantUtils
    registry=json.loads((ROOT/'models.json').read_text())
    chunks=rows(ROOT/'data/chunks.jsonl');qa=rows(ROOT/'data/qa_w5_200.jsonl')
    tokens=json.loads((ROOT/'index/tokenized.json').read_text(encoding='utf-8'))
    datahash=hashlib.sha256((ROOT/'data/chunks.jsonl').read_bytes()).hexdigest()
    assert tokens['corpus_hash']==datahash
    key=hashlib.sha256((ROOT/'data/qa_w5_200.jsonl').read_bytes()+(ROOT/'index/fingerprint.txt').read_bytes()).hexdigest()
    assert (ROOT/'evidence/query_vectors.sha256').read_text()==key
    vectors=np.load(ROOT/'evidence/query_vectors.npy',allow_pickle=False)
    expected=ViTokenizer.tokenize(qa[0]['question'])
    class CachedQuery:
        def embed_query(self,text):
            assert text==expected,'This smoke only uses the exact query matching the cached vector'
            return vectors[0].tolist()
    engine=SimpleNamespace(chunks=chunks,models=registry,np=np,tokenized=tokens['texts'],embedding=CachedQuery())
    search=ScopedQdrantUtils(engine,ROOT,domain=qa[0]['domain'])
    hits=search.search_documents(expected,top_k=5)
    assert hits and all(doc.metadata['document_id'] in search.allowed and doc.metadata['domain']==qa[0]['domain'] for doc,_ in hits)
    assert all('NoibanHanhFilter' in doc.metadata and 'NgayBanHanhFilter' in doc.metadata for doc,_ in hits)
    count=search.client.count(search.collection,exact=True).count;search.client.close()
    print('Scoped index ready; points='+str(count),flush=True)
    bert_dir=ROOT/registry['bert']['path']
    settings=SimpleNamespace(MODEL_EXTRACT=str(bert_dir),TOKENIZER=str(bert_dir),MAX_LENGTH=512,STRIDE=150,N_BEST=380,MAX_ANSWER_LENGTH=2000,RERANK=str(ROOT/registry['reranker']['path']))
    bert=Bert_Extract(settings)
    text=next(c['text'] for c in chunks if c['id'] in qa[0]['relevant_chunk_ids'])
    output=Extract_Information(bert).predict([text],qa[0]['question'])
    assert isinstance(output,dict) and set(output)=={0} and isinstance(output[0],str)
    print('Real BERT extraction returned one indexed result.',flush=True)
    rerank=RerankModelFinetune(settings)
    report={'scope_index_points':count,'scope_documents':53,'payload_schema':'legacy-filter-payload-v1',
            'real_bert_loaded':True,'bert_revision':registry['bert']['revision'],'bert_max_length':512,'bert_stride':150,'bert_n_best':380,
            'bert_extraction_result_type':'dict','bert_sample_count':1,'bert_answer_quality':'not_evaluated',
            'real_crossencoder_loaded':True,'crossencoder_effective_max_length':rerank.model.max_length,'crossencoder_explicit_max_length_override':False,'crossencoder_inference':'not_run',
            'query_embedding':'reused exact cached vector after QA/index hash checks','model_inference':'one real BERT extraction only',
            'aws_calls':0,'full_agent_llm_run':False}
    folder=ROOT/'runs/w6';folder.mkdir(parents=True,exist_ok=True)
    (folder/'asset-smoke.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report),flush=True)

if __name__=='__main__':main()

"""W3/W4 retrieval and W5 paired rerank ablation. Never calls an LLM."""
import hashlib,json,time
from pathlib import Path
import runtime
HERE=Path(__file__).resolve().parent
def evaluate(engine):
    runtime.STATE.update(evaluation='running',evaluation_progress=0,evaluation_total=200)
    try:
        with runtime.LOCK:
            qa=runtime.lines(HERE/'data/qa_w5_200.jsonl')
            baseline={q['id'] for q in runtime.lines(HERE/'data/qa_baseline_100.jsonl')}
            dev={q['id'] for q in runtime.lines(HERE/'data/qa_dev_150.jsonl')}
            root=HERE/'evidence';root.mkdir(exist_ok=True)
            key=hashlib.sha256((HERE/'data/qa_w5_200.jsonl').read_bytes()+(HERE/'index/fingerprint.txt').read_bytes()).hexdigest()
            vectorfile=root/'query_vectors.npy';keyfile=root/'query_vectors.sha256'
            if vectorfile.exists() and keyfile.exists() and keyfile.read_text()==key:vectors=engine.np.load(vectorfile,allow_pickle=False)
            else:
                vectors=engine.np.asarray(engine.embedding.embed_documents([engine.tokenize(q['question']) for q in qa]),dtype=engine.np.float32)
                engine.np.save(vectorfile,vectors);keyfile.write_text(key)
            predictions=[]
            partial=root/f'rerank_predictions_{time.time_ns()}.partial.jsonl'
            for i,(q,vec) in enumerate(zip(qa,vectors)):
                t=time.perf_counter();dense=engine.dense(q['question'],50,q['domain'],vector=vec);dense_ms=(time.perf_counter()-t)*1000
                t=time.perf_counter();lexical=engine.lexical(q['question'],50,q['domain']);bm25_ms=(time.perf_counter()-t)*1000
                t=time.perf_counter();fused=engine.rerank.reciprocal_rank_fusion([dense,lexical]);fusion_ms=(time.perf_counter()-t)*1000
                # Ablation uses exactly the candidates configured for the W5 chat.
                # Re-fuse the top-25 branches, then take the top-20 for both arms.
                candidates=engine.rerank.reciprocal_rank_fusion([dense[:runtime.BRANCH_K],lexical[:runtime.BRANCH_K]])[:runtime.CANDIDATE_K]
                t=time.perf_counter();reranked=engine.rerank_candidates(q['question'],candidates);rerank_ms=(time.perf_counter()-t)*1000
                def metadata(items):return [info['doc_metadata'] for _,info in items]
                rankings={'dense':[d.metadata for d,_ in dense],'bm25':[d.metadata for d,_ in lexical],
                          'hybrid_rrf':metadata(fused),'w5_without_ce':metadata(candidates[:runtime.TOP_K]),'w5_with_ce':metadata(reranked)}
                result={'id':q['id'],'domain':q['domain'],'baseline':q['id'] in baseline,'w4':q['id'] in dev,
                    'gold_primary_article_ids':q['relevant_article_ids'],
                    'candidate_chunk_ids':[m['chunk_id'] for m in metadata(candidates)],
                    'rankings':{m:[{'chunk_id':d['chunk_id'],'article_id':d['article_id']} for d in ds] for m,ds in rankings.items()},
                    'latency_excludes_query_embedding_ms':{'dense':dense_ms,'bm25':bm25_ms,'hybrid_rrf':dense_ms+bm25_ms+fusion_ms,
                                                          'ce_added':rerank_ms}}
                predictions.append(result)
                with partial.open('a',encoding='utf-8') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n')
                runtime.STATE.update(evaluation_progress=i+1)
                if i%10==0:print(json.dumps({'evaluation_progress':i+1,'total':200}),flush=True)
            def aggregate(rows,method,ks):
                out={'n':len(rows)}
                for k in ks:
                    out[f'recall@{k}']=sum(len(set(r['gold_primary_article_ids']) & {d['article_id'] for d in r['rankings'][method][:k]})/len(r['gold_primary_article_ids']) for r in rows)/len(rows)
                cutoff=max(ks)
                ranks=[next((j+1 for j,d in enumerate(r['rankings'][method][:cutoff]) if d['article_id'] in r['gold_primary_article_ids']),None) for r in rows]
                out[f'mrr@{cutoff}']=sum(1/r if r else 0 for r in ranks)/len(rows)
                return out
            w3=[r for r in predictions if r['baseline']];w4=[r for r in predictions if r['w4']]
            report={'status':'complete','label_status':'primary_citations_pending_human_review','llm_calls':0,
                'warning':'One primary article label per real source question; Recall equals Hit on these labels. Dev includes pilot and W4 items; not independent test or legal verification.',
                'fingerprint':key,'w3_dense_100':aggregate(w3,'dense',[1,3,5,10,20,50]),
                'w4_retrieval_150':{m:aggregate(w4,m,[1,3,5,10,20,50]) for m in ['dense','bm25','hybrid_rrf']},
                'w5_rerank_200':{m:aggregate(predictions,m,[1,3,5]) for m in ['w5_without_ce','w5_with_ce']},
                'w5_by_domain':{d:{m:aggregate([r for r in predictions if r['domain']==d],m,[1,3,5]) for m in ['w5_without_ce','w5_with_ce']} for d in ['giaoThong_VanTai','laoDong_TienLuong']},
                'protocol':{'query_variants':1,'filter_domain_from_qa_label':True,'branch_k':runtime.BRANCH_K,'rrf_k':60,
                    'ce_candidates':runtime.CANDIDATE_K,'output_top_k':runtime.TOP_K,'ce_max_tokens':512,
                    'ce_device':engine.ce_device,'ce_batch_size':4,'precision':'float32',
                    'same_candidates_both_arms':True,'matching_unit':'gold article within retrieved chunks','no_web':True,'no_llm':True},
                'ce_added_latency_mean_ms':sum(r['latency_excludes_query_embedding_ms']['ce_added'] for r in predictions)/len(predictions)}
            (root/'rerank_predictions.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in predictions),encoding='utf-8')
            (root/'evaluation_w1_w5.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            runtime.STATE['evaluation']='complete'
    except Exception as error:
        runtime.STATE.update(evaluation='failed',evaluation_error=type(error).__name__)
        import traceback;traceback.print_exc()

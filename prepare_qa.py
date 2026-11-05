"""Lock 200 real source questions; candidate citation labels require human review."""
import hashlib,json,random,re,unicodedata
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
DATA=HERE/'data'
def load(name):return [json.loads(s) for s in (DATA/name).read_text(encoding='utf-8').splitlines() if s.strip()]
def norm(s):return re.sub(r'\W+',' ',unicodedata.normalize('NFC',s).lower()).strip()
def main():
    base=load('qa_dev_150.jsonl');seen={norm(q['question']) for q in base}
    docs=json.loads((DATA/'manifest.json').read_text(encoding='utf-8'))
    nodes={n['id']:n for n in load('legal_nodes.jsonl')};chunks=load('chunks.jsonl');pool=[];skipped=Counter()
    for row in load('qa_source_rows.jsonl'):
        if norm(row['question']) in seen:continue
        text=row['answer'];numbers=re.findall(r'\d+/\d{4}/[\w-]+',text)
        matches=[d for d in docs if d['domain']==row['domain'] and any(d['number'].casefold()==n.casefold() for n in numbers)]
        aliases=[('laoDong_TienLuong-13',r'(bộ luật lao động|bllđ)[\s\S]{0,35}2019'),
                 ('laoDong_TienLuong-18',r'luật an toàn[\s,]*vệ sinh lao động[\s\S]{0,20}2015')]
        if row['domain']=='giaoThong_VanTai':aliases=[('giaoThong_VanTai-37',r'luật trật tự,?\s+an toàn giao thông\s+đường bộ')]
        for did,pattern in aliases:
            if re.search(pattern,re.sub(r'\s+',' ',text),re.I):
                d=next(d for d in docs if d['id']==did)
                if d not in matches:matches.append(d)
        if len(matches)!=1:skipped['ambiguous_or_missing_document']+=1;continue
        # Primary citation search window enlarged from 450 to 900 chars for long introductions.
        m=re.search(r'\bĐiều\s+(\d+)',text[:900],re.I)
        if not m:skipped['missing_primary_article']+=1;continue
        doc=matches[0];aid=doc['id']+'/article-'+m[1]
        if aid not in nodes:skipped['article_not_in_selected_corpus']+=1;continue
        provenance=row['source_dataset']+':'+str(row['source_row'])
        pool.append({'id':'W5-extra-'+hashlib.sha256(provenance.encode()).hexdigest()[:10],'domain':row['domain'],
            'question':row['question'],'reference_answer':text,'source_reference':f"{doc['source_file']}, Điều {m[1]}",
            'relevant_article_ids':[aid],'relevant_chunk_ids':[c['id'] for c in chunks if c['metadata']['article_id']==aid],
            'label_origin':'automatic_primary_citation_match_900char_window_pending_review','human_review':'pending',
            'legal_verification':'pending','source_dataset':row['source_dataset'],'source_row_1based_excluding_header':row['source_row'],
            'source_transform':row.get('source_transform'),'split':'dev','reference_answer_status':'repository_answer_not_verified_at_snapshot'})
        seen.add(norm(row['question']))
    if len(pool)<50:raise RuntimeError(f'Only {len(pool)} additional citation-matched source questions; do not invent the rest')
    random.Random(20261031).shuffle(pool)
    qa=base+pool[:50]
    assert len(qa)==200 and len({q['id'] for q in qa})==200 and len({norm(q['question']) for q in qa})==200
    assert all(q['relevant_chunk_ids'] for q in qa)
    (DATA/'qa_w5_200.jsonl').write_text(''.join(json.dumps(q,ensure_ascii=False)+'\n' for q in qa),encoding='utf-8')
    report={'w5_count':200,'w4_overlap':150,'pilot_overlap':50,'new_candidates':len(pool),'new_selected':50,
            'by_domain':dict(Counter(q['domain'] for q in qa)),'skipped':dict(skipped),'seed':20261031,
            'labels':'Primary article citations pending human and legal review; not complete relevance judgments.',
            'test_status':'Development; contains pilot and W4 dev. Not an independent holdout.',
            'sha256':hashlib.sha256((DATA/'qa_w5_200.jsonl').read_bytes()).hexdigest()}
    (DATA/'qa_selection_w5.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report))
if __name__=='__main__':main()

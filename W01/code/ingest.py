"""Versioned ingestion into this prototype only. Standard library, no model imports."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
PROJECT = HERE
OUT = HERE / 'data'
SCOPE = {'giaoThong_VanTai': sorted(set(range(1,40)) - {8}), 'laoDong_TienLuong': sorted(set(range(1,22)) - {3,6,10,12,14,20})}
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
ART = re.compile(r'^Điều\s+(\d+[a-zđ]?)\s*[.:]\s*(.*)$', re.I)
CLAUSE = re.compile(r'^(\d+)\.\s+(.*)$')
POINT = re.compile(r'^([a-zđ])\)\s*(.*)$', re.I)
SECTION = re.compile(r'^(Chương|Mục|Tiểu mục)\s+([IVXLCDM]+|\d+)\b', re.I)

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')

def sha(data): return hashlib.sha256(data).hexdigest()

def text_of(element):
    parts=[]
    for e in element.iter():
        if e.tag==W+'t': parts.append(e.text or '')
        elif e.tag in {W+'br',W+'cr'}: parts.append('\n')
        elif e.tag==W+'tab':parts.append('\t')
    return ''.join(parts)

def docx_lines(path):
    with zipfile.ZipFile(path) as z:
        body=ET.fromstring(z.read('word/document.xml')).find(W+'body')
    lines=[]; blocks=[]; offset=0; table_count=0
    for index,element in enumerate(body):
        kind=element.tag.removeprefix(W)
        if kind=='p': text=text_of(element)
        elif kind=='tbl':
            table_count+=1
            text='\n'.join(' | '.join('\n'.join(text_of(p) for p in cell.findall('.//'+W+'p')) for cell in row.findall(W+'tc')) for row in element.findall(W+'tr'))
        else:continue
        blocks.append({'block':index,'type':kind,'text':text})
        for line in text.split('\n'):
            lines.append({'text':line,'block':index,'block_type':kind,'start':offset,'end':offset+len(line)})
            offset+=len(line)+1
    full='\n'.join(x['text'] for x in lines)
    return full,lines,blocks,table_count

def parse_document(doc, lines):
    nodes=[];warnings=[];article=clause=point=None;counts=Counter()
    def create(kind,number,title,parent,line):
        path=(parent['id']+'/' if parent else doc['id']+'/')+kind+'-'+number
        counts[path]+=1
        if counts[path]>1:
            warnings.append({'kind':'duplicate_number','path':path,'occurrence':counts[path]})
            path+='~'+str(counts[path])
        node={'id':path,'document_id':doc['id'],'domain':doc['domain'],'type':kind,'number':number,
              'title':title,'parent_id':parent['id'] if parent else None,'start':line['start'],'end':line['end'],
              'start_block':line['block'],'text_original':line['text'],'own_lines':[line['text']]}
        nodes.append(node)
        return node
    for line in lines:
        s=line['text'].strip()
        m=ART.match(s) if line['block_type']=='p' else None
        if m:
            article=create('article',m[1],s,None,line);clause=point=None
            continue
        if SECTION.match(s) and line['block_type']=='p':
            article=clause=point=None
            continue
        if article is None:continue
        for ancestor in [article,clause,point]:
            if ancestor:
                ancestor['text_original']+='\n'+line['text'];ancestor['end']=line['end']
        m=CLAUSE.match(s) if line['block_type']=='p' else None
        if m:
            clause=create('clause',m[1],s,article,line);point=None
            continue
        m=POINT.match(s) if line['block_type']=='p' else None
        if m:
            point=create('point',m[1],s,clause or article,line)
            if clause is None:warnings.append({'kind':'point_without_numbered_clause','node':point['id']})
            continue
        (point or clause or article)['own_lines'].append(line['text'])
    # Reconstruct by offsets instead of accumulated state, which can cross sibling boundaries.
    full='\n'.join(x['text'] for x in lines)
    for i,n in enumerate(nodes):
        end=len(full)
        depth={'article':0,'clause':1,'point':2}[n['type']]
        for following in nodes[i+1:]:
            if {'article':0,'clause':1,'point':2}[following['type']]<=depth:
                end=following['start'];break
        # Respect previously recorded section boundaries / last line belonging to this article.
        article_node=n if n['type']=='article' else next(x for x in nodes if x['type']=='article' and n['id'].startswith(x['id']+'/'))
        end=min(end,article_node['end'])
        n['end']=max(n['start'],end)
        n['text_original']=full[n['start']:n['end']].rstrip('\n')
        n['own_text']='\n'.join(n.pop('own_lines'))
    return nodes,warnings

def main():
    OUT.mkdir(exist_ok=True)
    documents=[];nodes=[];chunks=[];warnings=[]
    for domain,ids in SCOPE.items():
        records=json.loads((PROJECT/'dataset'/domain/f'content_{domain}_Extracted.json').read_text(encoding='utf-8'))
        metadata={int(r['STT']):r for r in records}
        for stt in ids:
            path=PROJECT/'dataset'/domain/f'{stt}.docx';m=metadata[stt]
            doc={'id':f'{domain}-{stt}','domain':domain,'source_file':path.relative_to(PROJECT).as_posix(),
                 'source_sha256':sha(path.read_bytes()),'number':m['SoHieu'],'title':m['ChuDe'],'issuer':m['NoiBanHanh'],
                 'issued':m['NgayBanHanh'],'effective_date':None,'legal_status':'unverified','source_url':None,
                 'snapshot_date':'2026-07-01','corpus_version':'v1-prototype'}
            full,lines,blocks,tables=docx_lines(path);doc.update({'text_original':full,'blocks':blocks,'tables_read':tables})
            parsed,problems=parse_document(doc,lines)
            if not any(n['type']=='article' for n in parsed):raise ValueError('No article: '+doc['id'])
            documents.append(doc);nodes.extend(parsed);warnings.extend(problems)
            # Retrieval chunks follow structural clauses (or articles without clauses).
            for article in [n for n in parsed if n['type']=='article']:
                children=[n for n in parsed if n['parent_id']==article['id'] and n['type']=='clause']
                for unit in children or [article]:
                    content=unit['text_original']
                    if not content.strip():continue
                    # Bound the model context; retain pointer and complete original node separately.
                    for segment,start in enumerate(range(0,len(content),1800)):
                        piece=content[start:start+2000]
                        if len(piece.strip())<12:continue
                        chunk_id=unit['id']+f'/chunk-{segment}'
                        label=article['title']+(f" — Khoản {unit['number']}" if unit['type']=='clause' else '')
                        md={'document_id':doc['id'],'domain':domain,'corpus_version':'v1-prototype',
                            'SoHieu':doc['number'],'ChuDe':doc['title'],'NoiBanHanh':doc['issuer'],'NgayBanHanh':doc['issued'],
                            'LoaiVanBan':m['LoaiVanBan'],'Article':article['title'],'article_id':article['id'],
                            'node_id':unit['id'],'clause_number':unit['number'] if unit['type']=='clause' else None,
                            'chunk_id':chunk_id,'source_file':doc['source_file'],'snapshot_date':'2026-07-01',
                            'source_url':None,'legal_status':'unverified'}
                        chunks.append({'id':chunk_id,'text':doc['number']+'\n'+label+'\n'+piece,'metadata':md})
    ids={n['id'] for n in nodes}
    assert len(documents)==53 and all(n['parent_id'] is None or n['parent_id'] in ids for n in nodes)
    assert len(ids)==len(nodes) and len({c['id'] for c in chunks})==len(chunks)
    assert all(n['text_original']==next(d for d in documents if d['id']==n['document_id'])['text_original'][n['start']:n['end']].rstrip('\n') for n in nodes)
    jsonl(OUT/'documents.jsonl',documents);jsonl(OUT/'legal_nodes.jsonl',nodes);jsonl(OUT/'chunks.jsonl',chunks)
    manifest=[{k:v for k,v in d.items() if k not in {'text_original','blocks'}} for d in documents]
    dump(OUT/'manifest.json',manifest)
    counts=Counter(n['type'] for n in nodes)
    dump(OUT/'validation.json',{'documents':53,'nodes':dict(counts),'chunks':len(chunks),'warnings':warnings,
                              'legal_verification':'pending','tables_read':sum(d['tables_read'] for d in documents),
                              'parent_integrity':True,'original_text_spans':True})
    print(json.dumps({'documents':len(documents),'nodes':dict(counts),'chunks':len(chunks),'warnings':len(warnings)}))

if __name__=='__main__':main()

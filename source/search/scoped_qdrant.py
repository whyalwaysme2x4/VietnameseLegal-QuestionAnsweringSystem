"""Dedicated 53-document payload/index, retaining legacy entity-filter OR semantics."""
import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path

from qdrant_client import QdrantClient, models
from langchain_core.documents import Document
from source.agent.corpus_scope import load_scope
from source.search.utils_search import Qdrant_Utils


class ScopedQdrantUtils(Qdrant_Utils):
    def __init__(self, engine, root, domain='all'):
        self.root=Path(root);self.engine=engine;self.domain=domain
        self.scope=load_scope();self.allowed={d['id'] for d in self.scope['documents']}
        if len(self.allowed)!=53 or any(c['metadata']['document_id'] not in self.allowed for c in engine.chunks):
            raise ValueError('Corpus does not match the approved 53-document manifest')
        if {c['metadata']['document_id'] for c in engine.chunks}!=self.allowed:
            raise ValueError('Missing approved documents in structural corpus')
        self.collection='legalqa_w6_agentic_corpus_v1'
        data=(self.root/'data/chunks.jsonl').read_bytes()
        base=hashlib.sha256(data+engine.models['embedding']['revision'].encode()).hexdigest()
        if (self.root/'index/fingerprint.txt').read_text()!=base:
            raise ValueError('Embedding cache lineage differs from corpus/checkpoint')
        version=hashlib.sha256((base+'legacy-filter-payload-v1').encode()).hexdigest()
        folder=self.root/'index_w6';folder.mkdir(exist_ok=True)
        marker=folder/'fingerprint.txt'
        if marker.exists() and marker.read_text()!=version:
            raise ValueError('Changed W6 corpus/payload: create a separate index version')
        self.client=QdrantClient(path=str(folder/'qdrant'))
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(self.collection,vectors_config=models.VectorParams(size=768,distance=models.Distance.COSINE))
        if self.client.count(self.collection,exact=True).count!=len(engine.chunks):
            for start in range(0,len(engine.chunks),32):
                vectors=engine.np.load(self.root/'index/embedding_batches'/f'{start:06d}.npy',allow_pickle=False)
                chunks=engine.chunks[start:start+32]
                if vectors.shape!=(len(chunks),768):raise ValueError('Invalid cached vector shape')
                points=[]
                for i,chunk in enumerate(chunks):
                    metadata=self.payload_metadata(chunk['metadata'])
                    points.append(models.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL,chunk['id'])),vector=vectors[i].tolist(),payload={'page_content':engine.tokenized[start+i],'metadata':metadata}))
                self.client.upsert(self.collection,points=points,wait=True)
        marker.write_text(version)
        (folder/'lineage.json').write_text(json.dumps({'corpus_sha256':hashlib.sha256(data).hexdigest(),'embedding_revision':engine.models['embedding']['revision'],'fingerprint':version,'payload_schema':'legacy-filter-payload-v1','documents':53,'chunks':len(engine.chunks),'collection':self.collection},indent=2),encoding='utf-8')

    @staticmethod
    def payload_metadata(original):
        metadata=dict(original)
        metadata['LoaiVanBanFilter']=str(metadata.get('LoaiVanBan','')).lower()
        metadata['NoibanHanhFilter']=str(metadata.get('NoiBanHanh','')).lower()
        issued=str(metadata.get('NgayBanHanh',''));dates=[issued]
        for format in ['%d/%m/%Y','%d-%m-%Y','%Y-%m-%d']:
            try:
                value=datetime.strptime(issued,format);dates=[value.strftime('%d-%m-%Y'),str(value.year)];break
            except ValueError:pass
        metadata['NgayBanHanhFilter']=dates
        return metadata

    def search_documents(self, query, top_k=25, filter=None):
        conditions=[models.FieldCondition(key='metadata.document_id',match=models.MatchAny(any=sorted(self.allowed)))]
        if self.domain!='all':conditions.append(models.FieldCondition(key='metadata.domain',match=models.MatchValue(value=self.domain)))
        if filter is not None:conditions.append(filter)
        scoped=models.Filter(must=conditions)
        vector=self.engine.embedding.embed_query(query)
        points=self.client.query_points(self.collection,query=list(map(float,vector)),limit=top_k,query_filter=scoped,with_payload=True,timeout=300).points
        return [(Document(page_content=p.payload['page_content'],metadata=p.payload['metadata']),p.score) for p in points]

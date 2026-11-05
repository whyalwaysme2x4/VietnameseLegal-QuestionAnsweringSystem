"""LangGraph execution of the original agent policy, with original helpers intact."""
from __future__ import annotations

import json
import time
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.config import get_stream_writer
from source.agent.orchestrator import Orchestrator, _sse


class AgentState(TypedDict, total=False):
    user_input: str
    session_id: int | None
    memory_context: str
    web_enabled: bool
    plan: Any
    query: str
    entities: dict
    iteration: int
    rerank_docs: list
    snippets: dict
    best_result: Any
    best_score: float
    grade: Any
    answer: str
    references: list
    used_indices: list
    check: Any
    route: str
    events: list
    failed: bool
    trace: dict


class GraphOrchestrator(Orchestrator):
    """Same rules as Orchestrator; each actual stage is a graph node.

    The original manual orchestrator remains available for policy parity tests.
    In particular, fail-open grading/checking and the single, unchecked
    regeneration are intentional compatibility behavior, not new safety claims.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        graph = StateGraph(AgentState)
        methods = {
            'planner': self._plan_node, 'retrieve': self._retrieve_node,
            'extract': self._extract_node, 'grader': self._grade_node,
            'select_best': self._select_node, 'generate': self._generate_node,
            'checker': self._check_node, 'regenerate': self._regenerate_node,
            'finish': self._finish_node, 'alternate': self._alternate_node,
        }
        for name, method in methods.items():
            graph.add_node(name, self._guard(name, method))
        graph.add_edge(START, 'planner')
        graph.add_conditional_edges('planner', lambda s: s['route'], {'rag':'retrieve','alternate':'alternate','error':END})
        graph.add_conditional_edges('retrieve', lambda s: s['route'], {'extract':'extract','finish':'finish'})
        graph.add_conditional_edges('extract', lambda s: END if s.get('failed') else 'grader', {'grader':'grader',END:END})
        graph.add_conditional_edges('grader', lambda s: s['route'], {'retrieve':'retrieve','select_best':'select_best','error':END})
        graph.add_conditional_edges('select_best', lambda s: s['route'], {'generate':'generate','alternate':'alternate'})
        graph.add_conditional_edges('generate', lambda s: s['route'], {'checker':'checker','finish':'finish','alternate':'alternate','error':END})
        graph.add_conditional_edges('checker', lambda s: s['route'], {'regenerate':'regenerate','finish':'finish','error':END})
        graph.add_conditional_edges('regenerate', lambda s: END if s.get('failed') else 'finish', {'finish':'finish',END:END})
        graph.add_edge('alternate', END)
        graph.add_edge('finish', END)
        self.graph = graph.compile()

    def _guard(self, name, function):
        def node(state):
            start = time.perf_counter()
            get_stream_writer()({'type':'graph_node','node':name,'phase':'start'})
            try:
                update = function(state)
            except Exception as error:
                agent = 'planner' if name == 'planner' else 'retriever' if name == 'retrieve' else 'orchestrator'
                update = {'failed':True,'route':'finish' if name == 'retrieve' else 'error',
                          'events':[{'type':'error','agent':agent,'message':f'{type(error).__name__}: {error}'}]}
            update['trace'] = {'node':name,'phase':'end','elapsed_ms':round((time.perf_counter()-start)*1000,2),
                               'iteration':update.get('iteration',state.get('iteration',0)),
                               'route':update.get('route'), 'failed':update.get('failed',False)}
            return update
        return node

    def run(self, user_input, session_id=None, web_search_enabled=False):
        start = time.time()
        memory_context = self.memory.build_context(session_id) if session_id else ''
        state = {'user_input':user_input,'session_id':session_id,'memory_context':memory_context,
                 'web_enabled':web_search_enabled,'iteration':0,'best_score':-1.0,'best_result':None,'failed':False}
        failed = False
        planner_failed = False
        for mode, output in self.graph.stream(state, stream_mode=['updates','custom'], config={'recursion_limit':64}):
            if mode == 'custom':
                yield _sse(output)
                continue
            for name, update in output.items():
                trace = update.get('trace')
                if trace:
                    yield _sse({'type':'graph_node',**trace})
                for event in update.get('events', []):
                    yield _sse(event)
                if update.get('failed'):
                    failed = name != 'retrieve'
                    planner_failed = name == 'planner'
        # A retriever exception is handled inside the legacy RAG branch; other
        # uncaught failures return before the outer done frame, as in the source.
        if not failed and not planner_failed:
            yield _sse({'type':'done','total_ms':int((time.time()-start)*1000)})

    def _plan_node(self, state):
        start = time.time()
        plan = self.planner.plan(state['user_input'],state['memory_context'],state['web_enabled'])
        event = {'type':'plan','agent':'planner','elapsed_ms':int((time.time()-start)*1000),
                 'intent':plan.intent,'tool':plan.tool,'rewritten_query':plan.rewritten_query,
                 'search_query':plan.search_query,'entities':plan.entities,'reason':plan.reason}
        return {'plan':plan,'query':plan.rewritten_query,'entities':plan.entities or {},
                'route':'rag' if plan.tool == 'rag' else 'alternate','events':[event]}

    def _retrieve_node(self, state):
        iteration = state['iteration']+1
        get_stream_writer()({'type':'retrieve_start','agent':'retriever','iteration':iteration,
                             'query':state['query'],'entities':state['entities'] or None})
        start = time.time()
        docs = self._retrieve_and_rerank(state['query'],state['entities'])
        return {'iteration':iteration,'rerank_docs':docs,'route':'extract',
                'events':[{'type':'retrieve_done','agent':'retriever','iteration':iteration,
                           'elapsed_ms':int((time.time()-start)*1000),'n_docs':len(docs),
                           'docs':[self._format_doc_label(info) for _,info in docs]}]}

    def _extract_node(self, state):
        if not state['rerank_docs']:
            return {'snippets':{},'events':[]}
        start = time.time()
        snippets = self.extract_utils.predict([doc.replace('_',' ') for doc,_ in state['rerank_docs']],state['query'])
        if isinstance(snippets,str): snippets = {}
        return {'snippets':snippets,'events':[{'type':'extract','agent':'extractor',
                'elapsed_ms':int((time.time()-start)*1000),'n_snippets':len(snippets)}]}

    def _grade_node(self, state):
        start = time.time()
        grade = self.grader.grade(state['query'],state['snippets'])
        events = [{'type':'grade','agent':'grader','iteration':state['iteration'],
                   'elapsed_ms':int((time.time()-start)*1000),'relevance_score':grade.relevance_score,
                   'decision':grade.decision,'missing_aspects':grade.missing_aspects,'reason':grade.reason}]
        update = {'grade':grade,'events':events}
        if grade.relevance_score > state['best_score']:
            update.update(best_score=grade.relevance_score,best_result=(state['rerank_docs'],state['snippets'],grade))
        threshold = getattr(self.grader,'threshold',0.6)
        stop = grade.decision == 'sufficient' or grade.relevance_score >= threshold or state['iteration'] == self.max_iterations
        update['route'] = 'select_best' if stop else 'retrieve'
        if not stop:
            update['query'] = grade.suggested_query or state['query']
            events.append({'type':'iterate','agent':'orchestrator','next_iteration':state['iteration']+1,
                           'next_query':update['query'],'reason':f'Điểm liên quan {int(grade.relevance_score*100)}% dưới ngưỡng {int(threshold*100)}%, viết lại truy vấn và thử lại.'})
        return update

    def _select_node(self, state):
        docs,snippets,grade = state['best_result']
        update = {'rerank_docs':docs,'snippets':snippets,'grade':grade,'route':'generate','events':[]}
        if state['best_score'] < 0.4 and state['web_enabled']:
            plan = state['plan']
            update.update(plan=plan.model_copy(update={'tool':'web','search_query':plan.search_query or plan.rewritten_query}),route='alternate')
            update['events'] = [{'type':'iterate','agent':'orchestrator','reason':f'Điểm liên quan tốt nhất chỉ {int(state["best_score"]*100)}%, CSDL thiếu nhiều thông tin quan trọng — chuyển sang Web Search.'}]
        return update

    def _generate_node(self, state):
        get_stream_writer()({'type':'generate_start','agent':'generator','mode':'rag',
                             'reason':'Tổng hợp câu trả lời từ các đoạn trích được chọn.'})
        start = time.time()
        inputs = self._build_generator_input(state['rerank_docs'],state['snippets'])
        answer,refs,indices = self._generate_rag_answer(state['plan'].rewritten_query,inputs,state['rerank_docs'],state['memory_context'])
        update = {'answer':answer,'references':refs,'used_indices':indices,'route':'checker',
                  'events':[{'type':'generate_done','agent':'generator','elapsed_ms':int((time.time()-start)*1000),'n_citations':len(refs)}]}
        if not refs:
            if state['web_enabled']:
                plan=state['plan'];update.update(plan=plan.model_copy(update={'tool':'web','search_query':plan.search_query or plan.rewritten_query}),route='alternate')
                update['events'].append({'type':'iterate','agent':'orchestrator','reason':'LLM không chọn được văn bản trích dẫn, chuyển sang Web.'})
            else:
                update.update(route='finish',answer='Xin lỗi bạn, thông tin này không có trong cơ sở tri thức pháp luật của tôi. Nếu bạn muốn tôi tra cứu trên Internet, vui lòng bật chế độ **Web Search** ở thanh công cụ phía dưới rồi gửi lại câu hỏi.')
        return update

    def _check_node(self, state):
        docs=state['rerank_docs'];indices=state['used_indices'];start=time.time()
        sources=[docs[i][0].replace('_',' ') for i in indices if 0<=i<len(docs)] if indices else [doc.replace('_',' ') for doc,_ in docs if doc]
        result=self.checker.check(state['answer'],sources)
        regenerate=not result.is_grounded and result.confidence>=0.75 and len(result.unsupported_claims)>=2
        return {'check':result,'route':'regenerate' if regenerate else 'finish',
                'events':[{'type':'check','agent':'fact_checker','elapsed_ms':int((time.time()-start)*1000),
                           'is_grounded':result.is_grounded,'confidence':result.confidence,
                           'unsupported_claims':result.unsupported_claims,'reason':result.reason}]}

    def _regenerate_node(self, state):
        claims=state['check'].unsupported_claims
        get_stream_writer()({'type':'regenerate','agent':'generator',
                             'reason':f'Phát hiện {len(claims)} claim không có trong văn bản, tổng hợp lại với hướng dẫn cụ thể.'})
        start=time.time();inputs=self._build_generator_input(state['rerank_docs'],state['snippets'])
        answer,refs,indices=self._generate_rag_answer(state['plan'].rewritten_query,inputs,state['rerank_docs'],state['memory_context'],feedback_claims=claims)
        # Deliberately no second checker call: preserve the original policy.
        return {'answer':answer,'references':refs,'used_indices':indices,
                'events':[{'type':'generate_done','agent':'generator','elapsed_ms':int((time.time()-start)*1000),'regenerated':True,'n_citations':len(refs)}]}

    def _finish_node(self, state):
        if state.get('failed'):
            return {'events':[]}
        docs=state.get('rerank_docs',[])
        return {'events':[{'type':'final','answer':state['answer'],'references':state['references'],
                          'citation_indices':state.get('used_indices',[]),
                          'selected_chunk_ids':[info['doc_metadata'].get('chunk_id') for _,info in docs]}]}

    def _alternate_node(self, state):
        plan=state['plan'];memory=state['memory_context']
        if plan.tool=='template':frames=self._run_template(plan,memory)
        elif plan.tool=='ask_user':frames=self._run_clarify(plan)
        elif plan.tool=='reject':frames=self._run_reject(plan,memory)
        elif plan.tool=='web':frames=self._run_web(plan,memory)
        else:raise ValueError('Unknown tool: '+str(plan.tool))
        events=[]
        for frame in frames:
            event=json.loads(frame.removeprefix('data: ').strip())
            get_stream_writer()(event)
        return {'events':events}

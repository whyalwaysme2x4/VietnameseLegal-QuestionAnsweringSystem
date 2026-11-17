"""Local HTTP/SSE and source-card contract with fixtures, never AWS inference."""
import json
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]

import app
import runtime
from source.agent.demo_agentic import DemoAgentic
from source.agent.graph_orchestrator import GraphOrchestrator
from test_agent_w6 import CASES, build


def main():
    old_engine, old_state = runtime.ENGINE, dict(runtime.STATE)
    server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    checks = []
    try:
        for case, expected_index in [(CASES[0], 0), (CASES[1], 1)]:
            engine = runtime.Engine.__new__(runtime.Engine)
            engine.by_id, engine.nodes = {}, {}
            for i in range(2):
                key = f'fixture-A-{i}'
                node = f'fixture-node-{i}'
                metadata = dict(node_id=node, SoHieu='fixture', ChuDe='Fixture document',
                                Article=f'Article {i+1}', NoiBanHanh='Fixture issuer',
                                NgayBanHanh='01/01/2020', domain='giaoThong_VanTai',
                                source_file='fixture.docx')
                engine.by_id[key] = dict(id=key, metadata=metadata, text=f'Fixture chunk {i}')
                engine.nodes[node] = dict(id=node, parent_id='fixture-document', text_original=f'Fixture source {i}')
            graph, generator, search, _, _ = build(case, GraphOrchestrator)
            generator.usage = []
            bridge = DemoAgentic.__new__(DemoAgentic)
            bridge.engine, bridge.generator = engine, generator
            bridge.orchestrator, bridge.search = graph, search
            engine.agentic = bridge
            runtime.ENGINE = engine
            runtime.STATE.update(ready=True)
            base = f'http://127.0.0.1:{server.server_port}'
            payload = json.dumps(dict(question=case['question'], domain='all', mode='agentic')).encode()
            request = Request(base+'/api/chat', data=payload, headers={'Content-Type':'application/json'})
            with urlopen(request, timeout=15) as response:
                assert response.headers.get_content_type() == 'text/event-stream'
                frames = response.read().decode('utf-8').split('\n\n')
            events = [json.loads(frame[6:]) for frame in frames if frame.startswith('data: ')]
            assert not any(event['type'] == 'error' for event in events)
            final = next(event for event in events if event['type'] == 'final')
            assert final['citation_base'] == 0
            assert [source['id'] for source in final['sources']] == [f'fixture-A-{expected_index}']
            assert len(final['retrieved_sources']) == 2
            assert events[-1]['type'] == 'done'
            trace = final['trace']
            assert all(any(event['type'] == 'graph_node' and event['node'] == node and event['phase'] == 'end'
                           for event in trace) for node in ['planner','grader','checker','finish'])
            with urlopen(base+'/api/source/'+final['sources'][0]['id'], timeout=5) as response:
                source = json.load(response)
            assert source['text'] == f'Fixture source {expected_index}'
            checks.append(dict(case=case['id'], citation_index=expected_index, status='passed',
                               source_card=True, final_trace_has_finish=True))
        result = dict(status='passed', fixture_execution=True, aws_calls=0,
                      full_agent_llm_run=False, model_inference=False,
                      checks=checks, timestamp=datetime.now(timezone.utc).isoformat())
        target = ROOT/'runs/w6/http-contract-smoke.json'
        target.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        print(json.dumps(result, indent=2))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
        runtime.ENGINE = old_engine
        runtime.STATE.clear()
        runtime.STATE.update(old_state)


if __name__ == '__main__':
    main()

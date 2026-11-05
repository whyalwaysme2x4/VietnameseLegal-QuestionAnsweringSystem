"""Local chat/evaluation server with W1-W5 baselines and the W6 agent graph."""
import contextlib,io,json,os,queue,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote,urlparse
from dotenv import load_dotenv
import runtime
HERE=Path(__file__).resolve().parent
load_dotenv(HERE/'.env',override=True)
PORT=int(os.getenv('PORT','8086'))
DOMAINS={'all','giaoThong_VanTai','laoDong_TienLuong'}

def worker(question,domain,mode,output):
    try:
        with runtime.LOCK,contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            for event in runtime.ENGINE.chat(question,domain,mode):output.put(event)
    except Exception as error:
        stage=runtime.STATE.get('request_stage','unknown')
        runtime.STATE['last_request_error']={'stage':stage,'error_type':type(error).__name__}
        messages={'retrieval':'Chưa truy xuất được corpus ở lượt này.',
                  'rerank':'Chưa xếp hạng lại được các nguồn ở lượt này.',
                  'generation':'Chưa nhận được câu trả lời từ AWS Nova. Kiểm tra phiên đăng nhập hoặc quyền dùng model.',
                  'synthesis_response':'Câu trả lời nhận được chưa đúng định dạng để hiển thị kèm nguồn.'}
        output.put({'type':'error','code':'pipeline_'+stage,'stage':stage,
                    'message':messages.get(stage,'Lượt xử lý chưa hoàn tất. Hãy kiểm tra trạng thái ứng dụng hoặc thử lại.')})
    finally:output.put(None)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def respond(self,code,data,mime='application/json; charset=utf-8'):
        payload=json.dumps(data,ensure_ascii=False).encode() if isinstance(data,(dict,list)) else data
        self.send_response(code);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'")
        self.end_headers();self.wfile.write(payload)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/api/status':
            if runtime.ENGINE and runtime.STATE['ready']:runtime.ENGINE.refresh_llm()
            return self.respond(200,{**runtime.STATE,'documents':53,'qa_pilot':50,'qa_baseline':100,'qa_dev':150,'qa_w5':200,
                'snapshot_date':'2026-07-01','legal_verification':'pending','web':False,'port':PORT})
        if path.startswith('/api/source/'):
            key=unquote(path[len('/api/source/'):])
            if not runtime.ENGINE or key not in runtime.ENGINE.by_id:return self.respond(404,{'error':'Không có nguồn này.'})
            return self.respond(200,runtime.ENGINE.source(key))
        if path=='/api/evaluation':
            p=HERE/'runs/evaluation/evaluation_w1_w5.json'
            if not p.exists():p=HERE/'Evidence/_shared/measurement_20261031/evaluation_w1_w5.json'
            return self.respond(200,json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'status':'not_run'})
        if path in {'/','/style.css','/app.js'}:
            name='index.html' if path=='/' else path[1:]
            mime={'index.html':'text/html; charset=utf-8','style.css':'text/css; charset=utf-8','app.js':'text/javascript; charset=utf-8'}[name]
            return self.respond(200,(HERE/name).read_bytes(),mime)
        return self.respond(404,{'error':'Not found'})
    def do_POST(self):
        if self.headers.get('Origin') not in {None,f'http://127.0.0.1:{PORT}',f'http://localhost:{PORT}'}:return self.respond(403,{'error':'Origin rejected'})
        if self.path not in {'/api/chat','/api/evaluate'}:return self.respond(404,{'error':'Not found'})
        if not runtime.STATE['ready'] or runtime.ENGINE is None:return self.respond(503,{'error':'Model/index đang được khởi động.'})
        if self.path=='/api/evaluate':
            if runtime.STATE.get('evaluation') in {'queued','running'}:return self.respond(409,{'error':'Evaluation already running'})
            runtime.STATE['evaluation']='queued'
            from evaluate import evaluate
            threading.Thread(target=evaluate,args=(runtime.ENGINE,),daemon=True).start()
            return self.respond(202,{'status':'started'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<16000:raise ValueError()
            data=json.loads(self.rfile.read(size));question=data.get('question');domain=data.get('domain','all');mode=data.get('mode','rerank')
            if not isinstance(question,str) or not question.strip() or len(question)>1600 or domain not in DOMAINS or mode not in runtime.MODES:raise ValueError()
        except (ValueError,TypeError,AttributeError):return self.respond(400,{'error':'Câu hỏi/lĩnh vực/chế độ không hợp lệ.'})
        self.send_response(200);self.send_header('Content-Type','text/event-stream; charset=utf-8');self.send_header('Cache-Control','no-store');self.end_headers()
        output=queue.Queue();threading.Thread(target=worker,args=(question,domain,mode,output),daemon=True).start()
        try:
            while True:
                try:event=output.get(timeout=10)
                except queue.Empty:self.wfile.write(b': keepalive\n\n');self.wfile.flush();continue
                if event is None:break
                self.wfile.write(('data: '+json.dumps(event,ensure_ascii=False)+'\n\n').encode());self.wfile.flush()
        except (BrokenPipeError,ConnectionResetError):pass

if __name__=='__main__':
    threading.Thread(target=runtime.build_engine,daemon=True).start()
    print(f'W1-W6 demo: http://127.0.0.1:{PORT}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()

"""Integrated W8 demo: original agent SSE, SQLite sessions/history and source UI."""
import contextlib
import io
import json
import os
import queue
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
from dotenv import load_dotenv
import runtime
from source.data.db.demo_history import HistoryStore, HistoryError

HERE = Path(__file__).resolve().parent
load_dotenv(HERE/'.env', override=True)
PORT = int(os.getenv('PORT','8086'))
DOMAINS = {'all','giaoThong_VanTai','laoDong_TienLuong'}
HISTORY = None
HISTORY_LOCK = threading.Lock()


def history_store():
    global HISTORY
    with HISTORY_LOCK:
        if HISTORY is None:
            HISTORY = HistoryStore(os.getenv('LEGALQA_HISTORY_PATH', str(HERE/'local_data/chat_history.sqlite3')))
    return HISTORY


def worker(question, domain, mode, output, session_id=None, turn_id=None, store=None):
    final_seen = error_seen = done_seen = False
    error_code = 'no_final_answer'
    try:
        with runtime.LOCK, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            memory = store.memory if store else None
            for event in runtime.ENGINE.chat(question,domain,mode,session_id=session_id,memory=memory):
                event = dict(event)
                if event['type']=='error':
                    error_seen = True
                    error_code = 'pipeline_error'
                if event['type']=='done':
                    done_seen = True
                if event['type']=='final':
                    if final_seen:
                        continue
                    final_seen = True
                    if store:
                        event.update(session_id=session_id,turn_id=turn_id,history_status='saved')
                        try:
                            event['message_id'] = store.complete(turn_id,event)
                        except Exception:
                            event['history_status'] = 'failed'
                            output.put({'type':'history_error','message':'Đã có đáp án nhưng chưa lưu được lịch sử. Hãy giữ nội dung lượt này.'})
                            try:
                                store.fail(turn_id,'history_write_failed')
                            except Exception:
                                pass
                output.put(event)
    except Exception as error:
        error_seen = True
        error_code = type(error).__name__
        stage = runtime.STATE.get('request_stage','unknown')
        runtime.STATE['last_request_error'] = {'stage':stage,'error_type':error_code}
        messages = {'retrieval':'Chưa truy xuất được corpus ở lượt này.',
                    'rerank':'Chưa xếp hạng lại được các nguồn ở lượt này.',
                    'generation':'Chưa nhận được câu trả lời từ AWS Nova. Kiểm tra phiên đăng nhập hoặc quyền dùng model.',
                    'synthesis_response':'Câu trả lời nhận được chưa đúng định dạng để hiển thị kèm nguồn.'}
        output.put({'type':'error','code':'pipeline_'+stage,'stage':stage,
                    'message':messages.get(stage,'Lượt xử lý chưa hoàn tất. Hãy kiểm tra trạng thái ứng dụng hoặc thử lại.')})
    finally:
        if not final_seen:
            if store:
                try:
                    store.fail(turn_id,error_code)
                except Exception:
                    output.put({'type':'history_error','message':'Chưa cập nhật được trạng thái lịch sử.'})
            if not error_seen:
                output.put({'type':'error','code':'no_final_answer','message':'Luồng kết thúc trước khi có đáp án.'})
        if not done_seen:
            output.put({'type':'done','session_id':session_id,'turn_id':turn_id})
        output.put(None)


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass

    def respond(self,code,data,mime='application/json; charset=utf-8'):
        payload = json.dumps(data,ensure_ascii=False).encode() if isinstance(data,(dict,list)) else data
        self.send_response(code)
        self.send_header('Content-Type',mime)
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(payload)

    def valid_origin(self):
        port = self.server.server_address[1]
        return self.headers.get('Origin') in {None,f'http://127.0.0.1:{port}',f'http://localhost:{port}'}

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path=='/api/session/get-sessions':
                return self.respond(200,{'sessions':history_store().sessions()})
            if path.startswith('/api/session/get-chat-history/'):
                return self.respond(200,history_store().history(int(path.rsplit('/',1)[1])))
            if path.startswith('/api/session/get-message-references/'):
                return self.respond(200,{'references':history_store().references(int(path.rsplit('/',1)[1]))})
        except ValueError:
            return self.respond(400,{'error':'Mã phiên/tin nhắn không hợp lệ.'})
        except HistoryError as error:
            return self.respond(error.status,{'error':str(error)})
        except Exception:
            return self.respond(500,{'error':'Chưa đọc được lịch sử.'})
        if path=='/api/status':
            if runtime.ENGINE and runtime.STATE['ready']:
                runtime.ENGINE.refresh_llm()
            return self.respond(200,{**runtime.STATE,'documents':53,'qa_pilot':50,'qa_baseline':100,'qa_dev':150,'qa_w5':200,
                'snapshot_date':'2026-07-01','legal_verification':'pending','web':False,'port':self.server.server_address[1],
                'history_enabled':True,'history_scope':'local_single_user','sse_mode':'stage_events_not_llm_tokens'})
        if path.startswith('/api/source/'):
            key = unquote(path[len('/api/source/'):])
            if not runtime.ENGINE or key not in runtime.ENGINE.by_id:
                return self.respond(404,{'error':'Không có nguồn này.'})
            return self.respond(200,runtime.ENGINE.source(key))
        if path=='/api/evaluation':
            p = HERE/'runs/evaluation/evaluation_w1_w5.json'
            if not p.exists():
                p = HERE/'Evidence/_shared/measurement_20261031/evaluation_w1_w5.json'
            return self.respond(200,json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'status':'not_run'})
        if path in {'/','/style.css','/app.js','/sse.js'}:
            name = 'index.html' if path=='/' else path[1:]
            mime = {'index.html':'text/html; charset=utf-8','style.css':'text/css; charset=utf-8',
                    'app.js':'text/javascript; charset=utf-8','sse.js':'text/javascript; charset=utf-8'}[name]
            return self.respond(200,(HERE/name).read_bytes(),mime)
        return self.respond(404,{'error':'Not found'})

    def do_DELETE(self):
        if not self.valid_origin():
            return self.respond(403,{'error':'Origin rejected'})
        path = urlparse(self.path).path
        if not path.startswith('/api/session/delete-session/'):
            return self.respond(404,{'error':'Not found'})
        try:
            history_store().delete_session(int(path.rsplit('/',1)[1]))
            return self.respond(200,{'status':'success'})
        except ValueError:
            return self.respond(400,{'error':'Mã phiên không hợp lệ.'})
        except HistoryError as error:
            return self.respond(error.status,{'error':str(error)})
        except Exception:
            return self.respond(500,{'error':'Chưa xóa được phiên.'})

    def do_POST(self):
        if not self.valid_origin():
            return self.respond(403,{'error':'Origin rejected'})
        if self.path=='/api/session/start-session':
            try:
                return self.respond(200,{'session_id':history_store().create_session()})
            except Exception:
                return self.respond(500,{'error':'Chưa tạo được phiên.'})
        if self.path not in {'/api/chat','/api/evaluate'}:
            return self.respond(404,{'error':'Not found'})
        if not runtime.STATE['ready'] or runtime.ENGINE is None:
            return self.respond(503,{'error':'Model/index đang được khởi động.'})
        if self.path=='/api/evaluate':
            if runtime.STATE.get('evaluation') in {'queued','running'}:
                return self.respond(409,{'error':'Evaluation already running'})
            runtime.STATE['evaluation'] = 'queued'
            from evaluate import evaluate
            threading.Thread(target=evaluate,args=(runtime.ENGINE,),daemon=True).start()
            return self.respond(202,{'status':'started'})
        try:
            size = int(self.headers.get('Content-Length','0'))
            if not 0<size<16000:
                raise ValueError()
            data = json.loads(self.rfile.read(size))
            question,domain,mode = data.get('question'),data.get('domain','all'),data.get('mode','rerank')
            session_id = data.get('session_id')
            if not isinstance(question,str) or not question.strip() or len(question)>1600 or domain not in DOMAINS or mode not in runtime.MODES:
                raise ValueError()
        except (ValueError,TypeError,AttributeError):
            return self.respond(400,{'error':'Câu hỏi/lĩnh vực/chế độ không hợp lệ.'})
        store = None; turn_id = None
        if session_id is not None:
            try:
                store = history_store()
                turn_id = store.begin(session_id,question,domain,mode,data.get('request_id'))
            except HistoryError as error:
                return self.respond(error.status,{'error':str(error)})
            except Exception:
                return self.respond(500,{'error':'Chưa bắt đầu được lượt hỏi trong lịch sử.'})
        self.send_response(200)
        self.send_header('Content-Type','text/event-stream; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Accel-Buffering','no')
        self.end_headers()
        output = queue.Queue()
        threading.Thread(target=worker,args=(question,domain,mode,output,session_id,turn_id,store),daemon=True).start()
        try:
            while True:
                try:
                    event = output.get(timeout=10)
                except queue.Empty:
                    self.wfile.write(b': keepalive\n\n');self.wfile.flush();continue
                if event is None:
                    break
                self.wfile.write(('data: '+json.dumps(event,ensure_ascii=False)+'\n\n').encode())
                self.wfile.flush()
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):
            pass


if __name__=='__main__':
    history_store()
    threading.Thread(target=runtime.build_engine,daemon=True).start()
    print(f'W1-W8 demo: http://127.0.0.1:{PORT}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()

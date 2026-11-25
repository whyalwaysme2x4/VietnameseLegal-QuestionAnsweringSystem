"""W8 adapter around the original SQLite schema/read helpers; no private DB copying."""
import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

from source.data.db.db_connection import DBConnection
from source.data.db.utils_db import DB_Utils
from source.data.db.memory import Memory


class HistoryError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


class SessionHistoryMemory(Memory):
    """Reuse original per-session last-five-message context, without global facts.

    W8 does not enable LLM summarization or cross-session personal fact extraction.
    All completed messages remain in history even though context keeps five rows.
    """
    def __init__(self, db):
        super().__init__(db, generator=None)

    def get_facts(self, limit=20):
        return []


class HistoryStore:
    def __init__(self, path):
        self.path = Path(path).resolve()
        self.db = DBConnection(SimpleNamespace(DB_PATH=str(self.path)))
        self.utils = DB_Utils(self.db)
        self.memory = SessionHistoryMemory(self.db)
        self._lock = threading.RLock()
        with self.connection() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS Demo_Turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL UNIQUE,
                    session_id INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('processing','complete','failed')),
                    user_message_id INTEGER,
                    bot_message_id INTEGER,
                    final_json TEXT,
                    error_code TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    finished_at TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES Chat_Sessions(id) ON DELETE CASCADE,
                    FOREIGN KEY(user_message_id) REFERENCES Chat_Messages(id),
                    FOREIGN KEY(bot_message_id) REFERENCES Chat_Messages(id)
                );
                CREATE UNIQUE INDEX IF NOT EXISTS demo_session_one_processing
                    ON Demo_Turns(session_id) WHERE status='processing';
            ''')
            # On a new server process, no old in-flight worker can still finish.
            conn.execute("UPDATE Demo_Turns SET status='failed', error_code='server_restarted', finished_at=CURRENT_TIMESTAMP WHERE status='processing'")

    @contextmanager
    def connection(self):
        conn = self.db.Get_DB_Connection()
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _session(self, conn, session_id):
        if type(session_id) is not int or session_id < 1:
            raise HistoryError(400, 'Mã phiên không hợp lệ.')
        if not conn.execute('SELECT id FROM Chat_Sessions WHERE id=?', (session_id,)).fetchone():
            raise HistoryError(404, 'Phiên không còn tồn tại.')

    def create_session(self):
        return self.utils.Create_Session()

    def sessions(self):
        # Original Get_Session handles completed sessions; include new/failed ones too.
        completed = {row[0]: row[2] for row in self.utils.Get_Session()}
        with self.connection() as conn:
            rows = conn.execute('''SELECT s.id, s.create_at,
                (SELECT question FROM Demo_Turns WHERE session_id=s.id ORDER BY id LIMIT 1),
                (SELECT status FROM Demo_Turns WHERE session_id=s.id ORDER BY id DESC LIMIT 1)
                FROM Chat_Sessions s ORDER BY s.id DESC''').fetchall()
        return [dict(id=r[0], create_at=str(r[1]), first_message=completed.get(r[0]) or r[2] or 'Cuộc trò chuyện mới',
                     status=r[3] or 'empty') for r in rows]

    def begin(self, session_id, question, domain, mode, request_id=None):
        if request_id is None:
            request_id = str(uuid.uuid4())
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 80:
            raise HistoryError(400, 'Mã lượt hỏi không hợp lệ.')
        with self._lock, self.connection() as conn:
            self._session(conn, session_id)
            try:
                cur = conn.execute('''INSERT INTO Demo_Turns(request_id,session_id,question,domain,mode,status)
                    VALUES (?,?,?,?,?,'processing')''', (request_id,session_id,question,domain,mode))
            except sqlite3.IntegrityError:
                raise HistoryError(409, 'Lượt hỏi đã tồn tại hoặc phiên này đang xử lý. Hãy mở lại lịch sử để kiểm tra.') from None
            return cur.lastrowid

    def complete(self, turn_id, final):
        answer = final.get('answer')
        if not isinstance(answer, str):
            raise ValueError('Final answer must be text')
        payload = json.dumps(final, ensure_ascii=False)
        with self._lock, self.connection() as conn:
            row = conn.execute('SELECT session_id,question,status FROM Demo_Turns WHERE id=?', (turn_id,)).fetchone()
            if not row or row[2] != 'processing':
                raise HistoryError(409, 'Lượt hỏi không còn ở trạng thái xử lý.')
            session_id, question, _ = row
            # Atomically save the pair and its exact citation/source payload.
            user = conn.execute("INSERT INTO Chat_Messages(session_id,sender,message) VALUES (?,'user',?)", (session_id,question)).lastrowid
            bot = conn.execute("INSERT INTO Chat_Messages(session_id,sender,message) VALUES (?,'bot',?)", (session_id,answer)).lastrowid
            refs = final.get('references') or [json.dumps(s,ensure_ascii=False) for s in final.get('sources',[])]
            for ref in refs:
                conn.execute('INSERT INTO Chat_References(message_id,reference_content) VALUES (?,?)', (bot,ref))
            conn.execute("UPDATE Demo_Turns SET status='complete', user_message_id=?,bot_message_id=?,final_json=?,finished_at=CURRENT_TIMESTAMP WHERE id=?",
                         (user,bot,payload,turn_id))
            return bot

    def fail(self, turn_id, error_code):
        with self._lock, self.connection() as conn:
            conn.execute("UPDATE Demo_Turns SET status='failed',error_code=?,finished_at=CURRENT_TIMESTAMP WHERE id=? AND status='processing'",
                         (str(error_code)[:80],turn_id))

    def history(self, session_id):
        with self.connection() as conn:
            self._session(conn, session_id)
            rows = conn.execute('''SELECT id,question,domain,mode,status,bot_message_id,final_json,error_code,created_at
                FROM Demo_Turns WHERE session_id=? ORDER BY id''', (session_id,)).fetchall()
        payloads = {r[5]:json.loads(r[6]) for r in rows if r[6]}
        messages = [dict(id=r[0], sender=r[1], message=r[2], send_at=str(r[3]), payload=payloads.get(r[0]))
                    for r in sorted(self.utils.Get_History(session_id), key=lambda r:r[0])]
        turns = [dict(id=r[0],question=r[1],domain=r[2],mode=r[3],status=r[4],bot_message_id=r[5],
                      error_code=r[7],created_at=str(r[8])) for r in rows]
        return dict(session_id=session_id,chat_history=messages,turns=turns)

    def references(self, message_id):
        return self.utils.Get_References(message_id)

    def delete_session(self, session_id):
        with self._lock, self.connection() as conn:
            self._session(conn, session_id)
            if conn.execute("SELECT 1 FROM Demo_Turns WHERE session_id=? AND status='processing'", (session_id,)).fetchone():
                raise HistoryError(409, 'Phiên đang xử lý. Hãy đợi hoàn tất trước khi xóa.')
            # Same cascade schema as the original; keep both deletes atomic.
            conn.execute('DELETE FROM Demo_Turns WHERE session_id=?', (session_id,))
            conn.execute('DELETE FROM Chat_Sessions WHERE id=?', (session_id,))

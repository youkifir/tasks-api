"""A tiny REST API for tasks. Standard library only."""
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .db import connect, row_to_dict

TASK_PATH = re.compile(r"^/tasks/(\d+)$")


def make_handler(conn, lock):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # keep output quiet
            pass

        def _send(self, status, payload=None):
            body = b"" if payload is None else json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self):
            try:
                length = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(length) or b"{}")
                return data if isinstance(data, dict) else None
            except (ValueError, json.JSONDecodeError):
                return None

        def _get_task(self, task_id):
            return conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

        def do_GET(self):
            with lock:
                if self.path == "/tasks":
                    rows = conn.execute(
                        "SELECT * FROM tasks ORDER BY id").fetchall()
                    return self._send(200, [row_to_dict(r) for r in rows])
                m = TASK_PATH.match(self.path)
                if m:
                    row = self._get_task(int(m.group(1)))
                    if row:
                        return self._send(200, row_to_dict(row))
            self._send(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/tasks":
                return self._send(404, {"error": "not found"})
            data = self._read_json()
            title = (data or {}).get("title")
            if not isinstance(title, str) or not title.strip():
                return self._send(400, {"error": "title is required"})
            with lock:
                cur = conn.execute(
                    "INSERT INTO tasks (title) VALUES (?)", (title.strip(),))
                conn.commit()
                row = self._get_task(cur.lastrowid)
            self._send(201, row_to_dict(row))

        def do_PATCH(self):
            m = TASK_PATH.match(self.path)
            if not m:
                return self._send(404, {"error": "not found"})
            data = self._read_json()
            if data is None:
                return self._send(400, {"error": "invalid JSON"})
            with lock:
                row = self._get_task(int(m.group(1)))
                if not row:
                    return self._send(404, {"error": "not found"})
                title = data.get("title", row["title"])
                done = data.get("done", bool(row["done"]))
                if not isinstance(title, str) or not title.strip() \
                        or not isinstance(done, bool):
                    return self._send(400, {"error": "invalid fields"})
                conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                             (title.strip(), int(done), row["id"]))
                conn.commit()
                row = self._get_task(row["id"])
            self._send(200, row_to_dict(row))

        def do_DELETE(self):
            m = TASK_PATH.match(self.path)
            if not m:
                return self._send(404, {"error": "not found"})
            with lock:
                cur = conn.execute(
                    "DELETE FROM tasks WHERE id = ?", (int(m.group(1)),))
                conn.commit()
            if cur.rowcount:
                return self._send(204)
            self._send(404, {"error": "not found"})

    return Handler


def create_server(host="127.0.0.1", port=8000, db_path=":memory:"):
    conn = connect(db_path)
    return ThreadingHTTPServer((host, port), make_handler(conn, threading.Lock()))

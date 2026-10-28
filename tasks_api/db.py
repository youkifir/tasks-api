import sqlite3


def connect(path=":memory:"):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS tasks (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL,
               done INTEGER NOT NULL DEFAULT 0
           )"""
    )
    conn.commit()
    return conn


def row_to_dict(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

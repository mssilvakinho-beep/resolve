import sqlite3
from pathlib import Path
from app.core.config import db_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
 id TEXT PRIMARY KEY,
 name TEXT NOT NULL,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contacts (
 id TEXT PRIMARY KEY,
 user_id TEXT NOT NULL,
 name TEXT NOT NULL,
 kind TEXT DEFAULT 'contact',
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cases (
 id TEXT PRIMARY KEY,
 user_id TEXT NOT NULL,
 contact_id TEXT,
 title TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'ABERTO',
 description TEXT DEFAULT '',
 created_at TEXT NOT NULL,
 updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
 id TEXT PRIMARY KEY,
 user_id TEXT NOT NULL,
 case_id TEXT,
 contact_id TEXT,
 type TEXT NOT NULL,
 description TEXT NOT NULL,
 amount REAL,
 occurred_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS transactions (
 id TEXT PRIMARY KEY,
 user_id TEXT NOT NULL,
 case_id TEXT,
 contact_id TEXT,
 kind TEXT NOT NULL CHECK(kind IN ('RECEITA','DESPESA')),
 category TEXT NOT NULL,
 description TEXT NOT NULL,
 amount REAL NOT NULL,
 due_date TEXT,
 paid INTEGER NOT NULL DEFAULT 1,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS documents (
 id TEXT PRIMARY KEY,
 user_id TEXT NOT NULL,
 case_id TEXT,
 contact_id TEXT,
 filename TEXT NOT NULL,
 document_type TEXT DEFAULT 'outro',
 storage_ref TEXT,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS interpretations (
 id TEXT PRIMARY KEY,
 user_id TEXT NOT NULL,
 text TEXT NOT NULL,
 proposal_json TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'PENDENTE',
 created_at TEXT NOT NULL,
 confirmed_at TEXT
);
CREATE TABLE IF NOT EXISTS audit_log (
 id TEXT PRIMARY KEY,
 user_id TEXT NOT NULL,
 action TEXT NOT NULL,
 entity_type TEXT NOT NULL,
 entity_id TEXT,
 detail TEXT DEFAULT '',
 created_at TEXT NOT NULL
);
"""

def connect():
    path = Path(db_path())
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.executescript(SCHEMA)
        for table, column, ddl in [
            ('cases','contact_id','TEXT'),
            ('events','contact_id','TEXT'),
            ('transactions','contact_id','TEXT'),
            ('documents','contact_id','TEXT'),
            ('documents','storage_ref','TEXT'),
        ]:
            cols={r['name'] for r in conn.execute(f'PRAGMA table_info({table})').fetchall()}
            if column not in cols:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} {ddl}')
        conn.commit()

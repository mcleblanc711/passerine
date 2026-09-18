import os, sqlite3, json
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime, timezone

def now(): return datetime.now(timezone.utc).isoformat()
def path(): return Path(os.environ.get('PASSERINE_DB', 'runtime/passerine.sqlite3'))

@contextmanager
def db():
    target = path()
    target.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(target, timeout=10)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally: c.close()

def init():
    with db() as c:
        c.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY, payload TEXT, collected_at TEXT, attempt_at TEXT, error TEXT, failures INTEGER NOT NULL DEFAULT 0, next_at REAL NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, source TEXT, at TEXT, title TEXT, detail TEXT, url TEXT, origin TEXT);
        CREATE TABLE IF NOT EXISTS incidents(id TEXT PRIMARY KEY, source TEXT, title TEXT, opened_at TEXT, acknowledged_at TEXT, recovered_at TEXT);
        CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY, created_at TEXT, status TEXT, attempts INTEGER DEFAULT 0, error TEXT);
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, csrf TEXT, expires REAL);
        ''')
        for source in ('wethr','whiskeyjack','quire'):
            c.execute('INSERT OR IGNORE INTO sources(id) VALUES (?)', (source,))

def success(observation):
    with db() as c:
        existing = c.execute('SELECT payload FROM sources WHERE id=?', (observation.source_id,)).fetchone()
        if existing and existing[0]:
            previous = json.loads(existing[0])
            if (previous['origin'], previous.get('instance_id', 'synthetic-v1')) != (observation.origin, observation.instance_id):
                raise ValueError('Source identity changed; use a separate app database')
        c.execute('UPDATE sources SET payload=?,collected_at=?,error=NULL,failures=0 WHERE id=?', (observation.model_dump_json(), now(), observation.source_id))
        for event in observation.events:
            c.execute('INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?,?)', (f'{observation.source_id}:{observation.instance_id}:{event.id}', observation.source_id, event.at, event.title, event.detail, event.url, observation.origin))
        c.execute('UPDATE incidents SET recovered_at=? WHERE source=? AND recovered_at IS NULL', (now(), observation.source_id))

def failure(source, message):
    with db() as c:
        c.execute('UPDATE sources SET error=?, failures=failures+1 WHERE id=?', (message, source))
        active = c.execute('SELECT id FROM incidents WHERE source=? AND recovered_at IS NULL', (source,)).fetchone()
        if not active:
            identity = f'{source}:{now()}'
            c.execute('INSERT INTO incidents VALUES (?,?,?,?,NULL,NULL)', (identity,source,message,now()))
            # Delivery deliberately disabled until a transport/ownership policy is configured.
            c.execute('INSERT INTO outbox(id,created_at,status) VALUES (?,?,?)', (identity,now(),'disabled'))

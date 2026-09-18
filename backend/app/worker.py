"""One independent polling process; failures retain cached observations."""
import os, time, signal, fcntl
from pathlib import Path
from app import store, demo
from app.adapters import wethr, whiskeyjack, quire

SOURCES = ('wethr','whiskeyjack','quire')

def collect(source):
    if os.environ.get('PASSERINE_DEMO') == '1': return demo.collect(source)
    if source == 'wethr':
        if not os.environ.get('PASSERINE_WETHR_DB'): raise ValueError('Not configured')
        return wethr.collect(os.environ['PASSERINE_WETHR_DB'])
    if source == 'whiskeyjack': return whiskeyjack.collect()
    return quire.collect()

def tick(clock=None):
    stamp = time.time() if clock is None else clock
    with store.db() as c:
        c.execute('INSERT OR REPLACE INTO meta VALUES (?,?)', ('worker_heartbeat',store.now()))
    for source in SOURCES:
        with store.db() as c:
            state = c.execute('SELECT * FROM sources WHERE id=?', (source,)).fetchone()
            if state['next_at'] > stamp: continue
            c.execute('UPDATE sources SET attempt_at=? WHERE id=?', (store.now(),source))
        try:
            store.success(collect(source))
            failures = 0
        except Exception:
            # Never return underlying database paths, tokens or upstream payloads.
            message = 'Quire disconnected · OAuth client, selected projects and verified read adapter required' if source == 'quire' else 'Read failed · verify source path, permissions and schema compatibility'
            store.failure(source, message)
            failures = state['failures'] + 1
        delay = min(3600, (300 if source == 'quire' else 60) * 2 ** min(failures,6))
        with store.db() as c: c.execute('UPDATE sources SET next_at=? WHERE id=?', (stamp + delay,source))

def main():
    store.init()
    lock = open(str(store.path()) + '.worker.lock', 'w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    running = True
    def stop(*_):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM,stop)
    signal.signal(signal.SIGINT,stop)
    while running:
        tick()
        for _ in range(5):
            if not running: break
            time.sleep(1)

if __name__ == '__main__': main()

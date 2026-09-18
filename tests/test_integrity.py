import json, sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app import store, worker, demo
from app.adapters.wethr import collect, readonly, project
from app.main import app

@pytest.fixture
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv('PASSERINE_DB',str(tmp_path/'app.db'))
    monkeypatch.setenv('PASSERINE_PASSWORD','test-password-long')
    monkeypatch.setenv('PASSERINE_DEMO','1')
    monkeypatch.setenv('PASSERINE_ORIGIN','http://testserver')
    store.init()
    return tmp_path

def ledger(path):
    c=sqlite3.connect(path)
    c.executescript('''PRAGMA journal_mode=WAL;
    CREATE TABLE trades(id INTEGER,created_at TEXT,city TEXT,target_date TEXT,bracket_label TEXT,side TEXT,size_usd REAL,settled INTEGER,settled_at TEXT,outcome INTEGER,pnl REAL,strategy_version TEXT);
    CREATE TABLE settings(key TEXT,value TEXT);
    CREATE TABLE strategy_epochs(label TEXT,starting_bankroll REAL);
    INSERT INTO settings VALUES ('current_strategy_epoch','B');
    INSERT INTO strategy_epochs VALUES ('A',100),('B',100);
    INSERT INTO trades VALUES (1,'2026-09-01 10:00:00','City','2026-09-01','20C','YES',20,1,'2026-09-02 10:00:00',1,10,'A');
    INSERT INTO trades VALUES (2,'2026-09-02 10:00:00','City','2026-09-02','20C','YES',10,0,NULL,NULL,NULL,'B');
    ''')
    c.commit()
    return c

def test_wal_settlement_replay_and_bankroll(isolated):
    p=isolated/'source.db'; c=ledger(p)
    before=list(c.iterdump())
    first=collect(p); assert first.data['scopes']['all']['pnl']=='10.00'
    assert list(c.iterdump())==before
    with pytest.raises(sqlite3.OperationalError): readonly(p).execute('DELETE FROM trades')
    c.execute("UPDATE trades SET settled=1,pnl=5,settled_at='2026-09-03 10:00:00' WHERE id=2"); c.commit()
    observation=collect(p)
    assert observation.data['scopes']['all']['pnl']=='15.00'
    assert observation.data['bankroll']=='105.00'
    assert observation.data['mode']=='paper' and observation.data['fees'] is None
    for _ in range(3): store.success(observation)
    with store.db() as db:
        assert db.execute('SELECT count(*) FROM events').fetchone()[0]==2
        assert json.loads(db.execute("SELECT payload FROM sources WHERE id='wethr'").fetchone()[0])['data']['scopes']['all']['pnl']=='15.00'
    assert observation.source_observed_at=='2026-09-03T10:00:00+00:00'
    c.close()

def test_missing_database_not_created(isolated):
    p=isolated/'absent.db'
    with pytest.raises(sqlite3.OperationalError): collect(p)
    assert not p.exists()

def test_unknown_money_not_zero():
    rows=[dict(strategy_version='B',settled=1,pnl=None,size_usd=1)]
    p=project(rows,{'B':100},'B')
    assert p['scopes']['all']['pnl'] is None and p['bankroll'] is None

def test_source_failure_isolation_backoff_retention(isolated,monkeypatch):
    worker.tick(clock=1000)
    with store.db() as c: old=c.execute("SELECT payload FROM sources WHERE id='wethr'").fetchone()[0]
    def broken(source):
        if source=='wethr': raise TimeoutError('secret token must not leak')
        return demo.collect(source)
    monkeypatch.setattr(worker,'collect',broken)
    worker.tick(clock=1400)
    with store.db() as c:
        w=c.execute("SELECT * FROM sources WHERE id='wethr'").fetchone()
        assert w['payload']==old and 'secret' not in w['error'] and w['next_at']==1520
        assert c.execute("SELECT error FROM sources WHERE id='whiskeyjack'").fetchone()[0] is None
        assert c.execute('SELECT count(*) FROM incidents').fetchone()[0]==1
        assert c.execute('SELECT status FROM outbox').fetchone()[0]=='disabled'
    worker.tick(clock=1500)
    with store.db() as c: assert c.execute('SELECT count(*) FROM incidents').fetchone()[0]==1
    monkeypatch.setattr(worker,'collect',demo.collect)
    worker.tick(clock=1600)
    with store.db() as c: assert c.execute('SELECT recovered_at FROM incidents').fetchone()[0]

def test_auth_csrf_spoofing_and_worker_failure(isolated):
    with TestClient(app) as client:
        assert client.get('/api/overview',headers={'Tailscale-User-Login':'chris'}).status_code==401
        assert client.post('/api/login',json={'password':'test-password-long'}).status_code==403
        r=client.post('/api/login',json={'password':'test-password-long'},headers={'Origin':'http://testserver'})
        assert r.status_code==200
        csrf=r.json()['csrf']
        assert 'HttpOnly' in r.headers['set-cookie'] and 'SameSite=strict' in r.headers['set-cookie']
        assert client.post('/api/refresh',headers={'Origin':'http://testserver'}).status_code==403
        assert client.post('/api/refresh',headers={'Origin':'https://evil.example','X-CSRF-Token':csrf}).status_code==403
        headers={'Origin':'http://testserver','X-CSRF-Token':csrf}
        assert client.post('/api/refresh',headers=headers).status_code==200
        worker.tick(clock=1000)
        with store.db() as c: c.execute("UPDATE meta SET value=? WHERE key='worker_heartbeat'",((datetime.now(timezone.utc)-timedelta(minutes=5)).isoformat(),))
        result=client.get('/api/overview')
        assert result.headers['cache-control']=='no-store'
        assert result.json()['worker']['alive'] is False
        store.failure('wethr','Unavailable')
        incident=client.get('/api/overview').json()['incidents'][0]
        assert client.post('/api/ack/'+incident['id'],headers=headers).status_code==200
        item=client.get('/api/overview').json()['incidents'][0]
        assert item['acknowledged_at'] and not item['recovered_at']
        assert client.post('/api/logout',headers=headers).status_code==200
        assert client.get('/api/overview').status_code==401

def test_corrected_resolution_unscored_and_withheld():
    from types import SimpleNamespace as Row
    from app.forecasting import current_resolution
    first=Row(event_id=1,observed_at_utc='2026-01-01T00:00:00+00:00',kind='resolved',scorable=True)
    score=Row(resolution_event_id=1)
    later=Row(event_id=2,observed_at_utc='2026-01-02T00:00:00+00:00',kind='withheld',scorable=False)
    assert current_resolution([first],[score])==(first,[score])
    assert current_resolution([later,first],[score])==(later,[])
    corrected=Row(event_id=3,observed_at_utc='2026-01-03T00:00:00+00:00',kind='resolved',scorable=True)
    assert current_resolution([corrected,later,first],[score])==(corrected,[])
    assert current_resolution([],[])==(None,[])

def test_demo_and_ledger_identity_cannot_mix(isolated):
    from app.models import Observation
    store.success(demo.collect('wethr'))
    real=demo.collect('wethr').model_copy(update={'origin':'real','instance_id':'other-ledger'})
    with pytest.raises(ValueError): store.success(real)
    with store.db() as c:
        assert json.loads(c.execute("SELECT payload FROM sources WHERE id='wethr'").fetchone()[0])['origin']=='demo'

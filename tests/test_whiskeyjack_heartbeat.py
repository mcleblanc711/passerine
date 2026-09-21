"""Synthetic rows matching WJ migration 012 and tournament.run_once at 9e9fcfe.

No bot imports, entrypoints, network, production ledgers or source migrations.
"""
import importlib.util
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from app import store
from app.adapters import whiskeyjack
from app.adapters.whiskeyjack_heartbeat import read_heartbeat

NOW = datetime(2026, 9, 19, 12, tzinfo=timezone.utc)


@pytest.fixture
def ledger(tmp_path):
    path = tmp_path / 'synthetic-minibench.db'
    with sqlite3.connect(path) as conn:
        conn.executescript('''
            CREATE TABLE tournament_events(
                seq INTEGER PRIMARY KEY, kind TEXT, scope TEXT,
                created_at_utc TEXT, data TEXT
            );
            CREATE TABLE forecast_records(record_id TEXT, post_id INTEGER);
        ''')
    return path


def append(path, stamp, *, kind='heartbeat', scope='worker', data=None):
    with sqlite3.connect(path) as conn:
        conn.execute(
            'INSERT INTO tournament_events(kind,scope,created_at_utc,data) VALUES (?,?,?,?)',
            (kind, scope, stamp, json.dumps(data or {})),
        )


def read(path):
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as conn:
        return read_heartbeat(conn, now=NOW)


def test_missing_wrong_scope_and_non_heartbeat_do_not_become_evidence(ledger):
    assert read(ledger)[0] is None
    append(ledger, '2026-09-19T11:00:00Z', kind='cost_settled')
    append(ledger, '2026-09-19T11:00:00Z', scope='other-profile')
    assert read(ledger)[0] is None


def test_latest_sequence_controls_evidence_not_greatest_timestamp(ledger):
    append(ledger, '2026-09-19T11:00:00Z')
    append(ledger, '2026-09-18T04:00:00-06:00')
    assert read(ledger)[0] == '2026-09-18T10:00:00+00:00'


@pytest.mark.parametrize('stamp', [None, '', 'not-a-date', '2026-09-18',
                                 '2026-09-18T10:00:00', '2026-09-20T10:00:00Z'])
def test_invalid_latest_evidence_stays_unknown_without_fallback(ledger, stamp):
    append(ledger, '2026-09-18T10:00:00Z')
    append(ledger, stamp)
    at, note = read(ledger)
    assert at is None
    assert 'invalid or in the future' in note


@pytest.mark.parametrize('complete,failures', [(False, 0), (True, 0), (True, 3)])
def test_reader_adapter_and_persistence_keep_heartbeat_separate_from_success(
    ledger, tmp_path, monkeypatch, complete, failures
):
    append(ledger, '2026-09-18T10:00:00Z', data={'complete': complete, 'failures': failures})
    # Substitute only the external source interfaces; execute Passerine's actual reader.
    def connect_readonly(path):
        conn = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    package = ModuleType('whiskeyjack_bot')
    package.__path__ = []
    monkeypatch.setitem(sys.modules, 'whiskeyjack_bot', package)
    monkeypatch.setitem(sys.modules, 'whiskeyjack_bot.ledger', SimpleNamespace(connect_readonly=connect_readonly))
    monkeypatch.setitem(sys.modules, 'whiskeyjack_bot.show', SimpleNamespace(assemble_show=lambda *_: pytest.fail('No forecasts in fixture')))
    monkeypatch.setitem(sys.modules, 'whiskeyjack_bot.forecast', ModuleType('whiskeyjack_bot.forecast'))
    monkeypatch.setitem(sys.modules, 'whiskeyjack_bot.forecast.store', SimpleNamespace(read_forecast_record=lambda *_: pytest.fail('No forecasts in fixture')))
    reader_path = Path(__file__).resolve().parents[1] / 'scripts/read_whiskeyjack.py'
    spec = importlib.util.spec_from_file_location('heartbeat_test_reader', reader_path)
    reader = importlib.util.module_from_spec(spec)
    monkeypatch.setattr(sys, 'path', sys.path.copy())
    spec.loader.exec_module(reader)
    before = ledger.read_bytes()
    payload = reader.read(str(ledger))
    monkeypatch.setenv('PASSERINE_WJ_ROOT', str(tmp_path))
    monkeypatch.setenv('PASSERINE_WJ_DB', str(ledger))
    monkeypatch.setattr(whiskeyjack.subprocess, 'run', lambda *a, **kw: SimpleNamespace(returncode=0, stdout=json.dumps(payload)))
    monkeypatch.setenv('PASSERINE_DB', str(tmp_path / 'app.db'))
    store.init()
    for _ in range(2):
        observation = whiskeyjack.collect()
        store.success(observation)
        assert observation.heartbeat_at == '2026-09-18T10:00:00+00:00'
        assert observation.job_success_at is None
        assert observation.source_observed_at is None
        assert 'Resolution ingestion and scoring success remain unknown' in observation.heartbeat_note
    store.failure('whiskeyjack', 'Source unavailable')
    with store.db() as conn:
        state = conn.execute("SELECT * FROM sources WHERE id='whiskeyjack'").fetchone()
        saved = json.loads(state['payload'])
        assert saved['heartbeat_at'] == observation.heartbeat_at
        assert saved['job_success_at'] is None
        assert state['collected_at'] != saved['heartbeat_at']
        assert state['error'] == 'Source unavailable'
        assert conn.execute('SELECT count(*) FROM events').fetchone()[0] == 0
    assert ledger.read_bytes() == before

"""Passerine-owned projection. No imports from WETHR's writable helpers."""
import sqlite3
from pathlib import Path
from decimal import Decimal
from contextlib import closing
from datetime import datetime, timezone
from app.models import Observation, Event
import hashlib, json

def utc(value):
    if not value:
        return None
    parsed = datetime.fromisoformat(value)
    return parsed.replace(tzinfo=parsed.tzinfo or timezone.utc).astimezone(timezone.utc).isoformat()

def readonly(path):
    conn = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA query_only=ON')
    return conn

def amount(rows, field):
    values = [r[field] for r in rows]
    if any(v is None for v in values):
        return None
    return str(sum((Decimal(str(v)) for v in values), Decimal(0)).quantize(Decimal('.01')))

def project(rows, epochs, current):
    scopes = {}
    for label in ['all'] + sorted(set(r['strategy_version'] for r in rows) | set(epochs)):
        selected = rows if label == 'all' else [r for r in rows if r['strategy_version'] == label]
        settled = [r for r in selected if r['settled'] == 1]
        opened = [r for r in selected if r['settled'] == 0]
        scopes[label] = dict(pnl=amount(settled, 'pnl'), settled_stake=amount(settled, 'size_usd'), open_stake=amount(opened, 'size_usd'), open_count=len(opened), settled_count=len(settled))
    current_pnl = scopes.get(current, {}).get('pnl')
    bankroll = str((Decimal(str(epochs[current])) + Decimal(current_pnl)).quantize(Decimal('.01'))) if current in epochs and current_pnl is not None else None
    return dict(scopes=scopes, current_epoch=current, bankroll=bankroll, currency='USD', mode='paper', fees=None, net=None, live=None, unrealized=None)

def collect(path):
    with closing(readonly(path)) as conn:
        conn.execute('BEGIN')
        rows = [dict(r) for r in conn.execute('SELECT id,created_at,city,target_date,bracket_label,side,size_usd,settled,settled_at,outcome,pnl,strategy_version FROM trades')]
        epochs = {r['label']: r['starting_bankroll'] for r in conn.execute('SELECT label,starting_bankroll FROM strategy_epochs')}
        setting = conn.execute("SELECT value FROM settings WHERE key='current_strategy_epoch'").fetchone()
        current = setting[0] if setting else None
    data = project(rows, epochs, current)
    events = []
    for row in rows:
        if row['settled']:
            fingerprint = hashlib.sha256(json.dumps(row, sort_keys=True).encode()).hexdigest()[:20]
            events.append(Event(id=f"trade:{row['id']}:{fingerprint}", at=utc(row['settled_at'] or row['created_at']), title=f"{row['city']} · {row['bracket_label']}", detail=f"Paper settlement · USD {row['pnl']} gross · {row['strategy_version']}"))
    times = [utc(r['settled_at'] or r['created_at']) for r in rows]
    return Observation(source_id='wethr', instance_id=hashlib.sha256(str(Path(path).resolve()).encode()).hexdigest()[:16], origin='real', source_observed_at=max(times, default=None), provenance='WETHR SQLite mode=ro; full transaction; paper_trader.get_stats definitions', coverage='Recorded ledger history; lifetime completeness unverified. Decimal sums of stored floating-point values.', data=data, events=events)

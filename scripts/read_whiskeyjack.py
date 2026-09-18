"""Run with the matching deployed interpreter. Selected fields only; never call a CLI."""
import sys, json
from pathlib import Path
from decimal import Decimal
from contextlib import closing
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.forecasting import current_resolution
from whiskeyjack_bot.ledger import connect_readonly
from whiskeyjack_bot.show import assemble_show

def read(path):
    with closing(connect_readonly(Path(path))) as conn:
        conn.execute('PRAGMA query_only=ON')
        conn.execute('BEGIN')
        records, events, times = [], [], []
        for row in conn.execute('SELECT record_id,post_id FROM forecast_records'):
            view = assemble_show(conn, row['record_id'])
            latest, current_scores = current_resolution(view.resolution_history, view.score_history)
            scores = [dict(metric=s.metric, value=s.value, version=s.implementation_version, resolution_id=s.resolution_event_id) for s in current_scores]
            records.append(dict(id=row['record_id'], question_id=view.summary.question_id, type=view.summary.question_type, status=view.summary.status, resolution=latest.kind if latest else 'unresolved', resolution_id=latest.event_id if latest else None, outcome=latest.observation.outcome if latest else None, scores=scores, uncertainties=len(view.unresolved_uncertainties), at=latest.observed_at_utc if latest else view.summary.generated_at_utc, url=f"https://www.metaculus.com/questions/{row['post_id']}/" if row['post_id'] else None))
            for e in view.canonical_history:
                payload = getattr(e, {'lifecycle': 'lifecycle_event'}.get(e.kind, e.kind))
                identifier = getattr(payload, 'event_id', None) or getattr(payload, 'event_seq', None) or getattr(payload, 'attempt_id', None) or e.occurred_at_utc
                events.append(dict(id=f"{row['record_id']}:{e.kind}:{identifier}", at=e.occurred_at_utc, title=f"Question {view.summary.question_id} · {e.kind.replace('_', ' ')}", detail='Recorded MiniBench ledger event', url=records[-1]['url']))
                times.append(e.occurred_at_utc)
        # Same reservation semantics as tournament_state.spending; avoid importing notification code.
        activation = conn.execute("SELECT data FROM tournament_events WHERE kind='activation' AND scope='account' ORDER BY seq DESC LIMIT 1").fetchone()
        actual = held = None
        if activation:
            scope = json.loads(activation[0])['activation_id']
            reserved, settled = [], {}
            for e in conn.execute("SELECT kind,data FROM tournament_events WHERE scope=? AND kind IN ('cost_reserved','cost_settled') ORDER BY seq", (scope,)):
                d = json.loads(e['data'])
                if e['kind'] == 'cost_reserved': reserved.append(d)
                else: settled[d['reservation_id']] = d['actual_microusd']
            actual = str(Decimal(sum(settled.values())) / 1000000)
            held = str(Decimal(sum(r['estimate_microusd'] for r in reserved if r['reservation_id'] not in settled)) / 1000000)
        return dict(records=records, events=events, source_observed_at=max(times, default=None), actual=actual, reserved=held)

if __name__ == '__main__':
    try:
        print(json.dumps(read(sys.argv[1])))
    except Exception:
        print('Source-compatible reader refused ledger; verify schema, permissions and reader dependencies.', file=sys.stderr)
        sys.exit(1)

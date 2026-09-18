"""Fixed synthetic evidence; intentionally does not become fresh when polled."""
from app.models import Observation, Event
from app.adapters.wethr import project

AT = '2026-09-18T10:00:00+00:00'
def collect(source):
    common = dict(source_id=source, origin='demo', source_observed_at=AT, provenance='Synthetic scenario • fixed at 18 September 2026', coverage='Demo only; no production observations')
    if source == 'wethr':
        rows = [dict(strategy_version='epoch-A', settled=1, pnl=10, size_usd=20), dict(strategy_version='epoch-B', settled=1, pnl=5, size_usd=10), dict(strategy_version='epoch-B', settled=0, pnl=None, size_usd=25)]
        return Observation(**common, health_notes=['Missed successful job · heartbeat is newer than input data. Neither establishes a completed collection.'], heartbeat_at='2026-09-18T15:00:00+00:00', job_success_at='2026-09-17T10:00:00+00:00', data=project(rows, {'epoch-A': 100, 'epoch-B': 100}, 'epoch-B'), events=[Event(id='settlement-1', at=AT, title='Calgary · paper settlement', detail='Gross paper result +USD 5.00 · epoch-B')])
    if source == 'whiskeyjack':
        records = [dict(id='demo-1', question_id=101, type='binary', status='resolved', resolution='resolved', scores=[], at=AT, uncertainties=0, url=None), dict(id='demo-2', question_id=102, type='binary', status='scored', resolution='withheld', scores=[], at=AT, uncertainties=1, url=None)]
        return Observation(**common, health_notes=['Resolved question awaiting local score; a later withheld observation supersedes the old score.', 'Cup is dormant by intent; no downtime alert.'], data=dict(records=records, actual='4.25', reserved='1.00', cup='Dormant · withdrawn'), events=[Event(id='correction-2', at=AT, title='Question 102 · outcome withheld', detail='Previous score superseded; current outcome follows latest observation.'), Event(id='resolution-1', at=AT, title='Question 101 · awaiting local score', detail='Resolved evidence exists; official platform score unavailable.')])
    return Observation(**common, data=dict(tasks=[dict(id='q1', title='Review missed successful collection', project='Operations', due='2026-09-18', parent=None, url=None), dict(id='q2', title='Check input freshness', project='Operations', due='2026-09-19', parent='Review missed successful collection', url=None)]))

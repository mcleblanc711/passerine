"""Selected tournament evidence from the already-open, source-validated ledger.

Source: tournament.run_once writes worker heartbeats; wj-watchdog uses their
created_at_utc. These records do not establish resolution-job success or liveness.
"""
from datetime import datetime, timezone
import sqlite3


HEARTBEAT_NOTE = (
    'Recorded MiniBench tournament heartbeat; emitted at poll start, progress and '
    'completion. It does not prove the process is still running or that work '
    'succeeded. Resolution ingestion and scoring success remain unknown.'
)


def read_heartbeat(conn: sqlite3.Connection, *, now: datetime | None = None) -> tuple[str | None, str]:
    row = conn.execute(
        "SELECT created_at_utc FROM tournament_events "
        "WHERE kind='heartbeat' AND scope='worker' ORDER BY seq DESC LIMIT 1"
    ).fetchone()
    if row is None:
        return None, 'No recorded tournament heartbeat. ' + HEARTBEAT_NOTE
    # Never fall back to an older valid record when the newest evidence is invalid.
    try:
        stamp = datetime.fromisoformat(row[0])
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError('Timezone required')
        stamp = stamp.astimezone(timezone.utc)
        if stamp > (now or datetime.now(timezone.utc)):
            raise ValueError('Future evidence')
    except (TypeError, ValueError, OverflowError):
        return None, 'Latest tournament heartbeat timestamp is invalid or in the future. ' + HEARTBEAT_NOTE
    return stamp.isoformat(), HEARTBEAT_NOTE

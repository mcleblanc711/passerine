# MiniBench question display rollout

Prepared and deployed September 21, 2026 after user authorization. Release
`1bb2779` (feature code `0fcd86d`) is deployed from `master` in
`/home/cleblanc/projects/passerine`. The previous release was `7b91955`.
The procedure below records that rollout; do not rerun its backup destination
or reuse its old preflight assumptions. See [verification](VERIFICATION.md).

This release displays saved question text and recorded bot forecasts. Community
forecasts remain explicitly unavailable. It adds no database migration,
dependencies, configuration keys or platform requests. Cached observations from
the previous reader display an unavailable forecast until a successful new poll.

## Preflight

Before rollout, recheck both worktrees for unrelated edits and record the exact
release SHA. Confirm deployed HEAD is still `7b91955` and is an ancestor of the
release. Stop if it diverged; reconcile changes before proceeding. Preserve the
previous frontend build in a private recovery directory. Confirm the configured
`PASSERINE_DB` path without printing the rest of `.env`.

The September 21 inspection found both Passerine units active/running from the
main checkout. Whiskey Jack is now clean at
`9834e3676fe593f0b18c14574ad2484725b8e41d`; its diff from the previously inspected
`9e9fcfe` affects watchdog deployment code, docs and tests, with no `src/` changes.
This establishes source-interface continuity, not a fresh production-ledger read
or the revision loaded by any bot process.

## Rollout after authorization

Run from the deployed checkout. Substitute the verified app database path and a
new backup filename where shown. Do not source bot environment files.

1. Record current Passerine and bot service PIDs/start times read-only so unrelated
   scheduled bot activity can be distinguished from deployment changes.
2. Stop **only** Passerine before changing any tracked code. Its worker launches
   `scripts/read_whiskeyjack.py` afresh on each poll.

   ```bash
   systemctl --user stop passerine-api.service passerine-worker.service
   ```

3. Create a consistent private app backup using the SQLite backup API, then verify
   it with a strict read-only integrity check. Never copy just a live DB file.

   ```bash
   umask 077
   .venv/bin/python scripts/backup.py runtime/passerine.sqlite3 runtime/pre-questions-deploy-20260921.sqlite3
   sqlite3 -readonly runtime/pre-questions-deploy-20260921.sqlite3 'PRAGMA integrity_check;'
   ```

   Require `ok`; if backup fails, restart the unchanged Passerine services and stop
   rollout. Keep the backup and previous frontend assets until verification passes.

4. Fast-forward to the exact reviewed release SHA and build from that checkout.
   Pin the SHA recorded during preflight rather than a moving branch name.

   ```bash
   git merge --ff-only RELEASE_SHA
   npm --prefix frontend run build
   ```

5. If both operations succeed, start only the two Passerine services.

   ```bash
   systemctl --user start passerine-api.service passerine-worker.service
   systemctl --user is-active passerine-api.service passerine-worker.service
   ```

## Acceptance after rollout

Wait for a successful worker poll. Through the existing private HTTPS origin,
verify an advancing worker heartbeat and new successful real WETHR/Whiskey Jack
collections, with no source errors. Confirm MiniBench question titles, question
details, recorded probabilities/percentiles, forecast version and both timestamps.
Community must remain unavailable; generated forecasts must not imply accepted
submission. Successful-job evidence must remain unknown where absent upstream.
Check phone width and existing resolution/score labels.

Run the existing `scripts/verify-private.mjs` with the server environment loaded
as documented in [private access](PRIVATE-ACCESS.md#verification-and-recovery).
It checks authentication, CSRF, real source availability, layouts and offline cache,
and makes one normal app refresh request. It does not specifically assert the new
forecast fields or prove that collection advanced after rollout; check those
separately. Do not run a second polling worker or any source job.

Record final release SHA, build/check outcomes and post-rollout timestamps in
[verification](VERIFICATION.md) and update [handoff](HANDOFF.md). Confirm no bot
unit, configuration, prompt or dependency was changed.

## Rollback

On build failure or failed rollout acceptance, stop only Passerine. With a clean
deployed worktree, switch it temporarily to detached `7b91955` and restore the
saved frontend assets (or rebuild the previous revision). Keep the feature branch
intact; do not force-reset shared history. Start Passerine and repeat health and
private-access verification. Reconcile the branch before any later rollout.

There is no schema change, so retain the app database by default; a rollback poll
replaces its read models. Restore the backup only if app data recovery is actually
needed, following [the DB and WAL recovery procedure](PRIVATE-ACCESS.md#verification-and-recovery).
Restoring loses app observations and local acknowledgements after the backup.
Never restore or modify a bot database.

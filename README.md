# Passerine

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Node](https://img.shields.io/badge/node-22-339933?logo=node.js&logoColor=white)

A private, Android-friendly observatory for WETHR, Whiskey Jack, Quire and operational evidence. Previously called **Perch** in the original handoff.

React/TypeScript + Vite PWA, FastAPI, a separate SQLite database and **one independent polling process**. The app never starts bots, runs ingestion/scoring, submits forecasts, trades, or changes their configuration. Source failures retain the last successful observation.

## Run locally

Prerequisites: Python 3.11+, `uv`, Node 22 and npm. From this directory:

```bash
uv sync --locked --cache-dir /tmp/passerine-uv-cache
npm --prefix frontend ci
npm --prefix frontend run build
cp .env.example .env
chmod 600 .env
```

Edit `.env`: replace `PASSERINE_PASSWORD` with a private password of at least 12 characters. The supplied source paths match the inspected local checkouts. Then:

```bash
./scripts/run-local.sh
```

Open **http://127.0.0.1:8000**, sign in with that password. Ctrl-C stops the API and worker. Do not start a second polling process for the same database; an exclusive file lock enforces this.

For **demo mode**, set `PASSERINE_DEMO=1` and `PASSERINE_DB='runtime/demo.sqlite3'` in `.env` before starting. Fixtures use fixed September 18, 2026 timestamps, so demo evidence never becomes artificially fresh when polled. Use separate databases for real/demo and for different source ledgers; identity changes are refused.

For frontend development, run the API/worker as above, set `PASSERINE_ORIGIN='http://127.0.0.1:5173'`, and run `npm --prefix frontend run dev`. Vite proxies `/api` to port 8000. The production build has no external fonts or asset dependencies.

## What is connected

| Source | Implemented and verified | Limits |
| --- | --- | --- |
| WETHR | Real `mode=ro` full-ledger transaction; all/history/epoch gross paper USD totals; current-epoch bankroll; open stake; settlement updates | No live/net/fees/unrealized metrics. Lifetime completeness unverified. Process heartbeat and last successful job unknown. |
| Whiskey Jack | Real deployed `connect_readonly` and `assemble_show`, run with the existing matching interpreter; all canonical event categories; current resolution and matching local scores; latest activation actual/held costs | MiniBench only. Cup intentionally omitted/dormant. Official scores, host telemetry, activation-binding health, unrecorded-post status and export bootstrap are not implemented. |
| Quire | Clearly disconnected in real mode; nested/date-only synthetic tasks in demo | OAuth and real pagination/hierarchy traversal are **not implemented**. Needs a private read-access OAuth registration, selected project IDs, verified payloads and quota policy. No tokens collected by this slice. |
| Operations | Persisted sync failures, backoff, incident acknowledgement/recovery, deduplicated events, worker heartbeat | Bot heartbeat/job-success instrumentation is unavailable. No external dead-man check. Notification intents persist as `disabled`; no delivery attempt or push claim. |

The September 18 real-read verification covered WETHR accounting and 24 Whiskey Jack forecasts / 116 canonical events. On September 19, WETHR still matches that revision; Whiskey Jack has advanced with no changes under `src/` in the intervening diff. Real reads were not repeated during the documentation review. See [discovery](docs/DISCOVERY.md) for exact revisions and deployment evidence. Synthetic fixtures are never presented as connected production data.

Source readers require access to the database's directory and ordinary SQLite WAL/shared-memory locking. `mode=ro` forbids database writes, but derived locking files may be touched by SQLite. Never use `immutable=1`, copy only a live `.db`, run source reporting CLIs, or migrate a source database to satisfy Passerine. Whiskey Jack reader timeout is 45 seconds; WETHR SQLite busy timeout is five seconds. Failed sources back off independently to one hour; refresh does not bypass cooldowns.

## Checks

```bash
.venv/bin/pytest -q
npm --prefix frontend run build
```

Browser tests expect a **demo** server on port 8000 with password `local-verification-only`, strictly for local testing. Stop the ordinary server first; use two terminals:

```bash
PYTHONPATH=backend PASSERINE_DEMO=1 PASSERINE_DB=runtime/browser-demo.sqlite3 .venv/bin/python -m app.worker
PYTHONPATH=backend PASSERINE_DEMO=1 PASSERINE_DB=runtime/browser-demo.sqlite3 PASSERINE_PASSWORD=local-verification-only .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then:

```bash
cd frontend
npx playwright install chromium
npm run test:ui
```

Or set `PASSERINE_CHROMIUM=/absolute/path/to/chrome` to use an existing Chromium. Tests cover 360/390/430/1440px navigation, horizontal overflow, epoch amounts, withheld resolutions, offline fallback and cache contents. Screenshots are written under `runtime/screenshots/` (ignored). The backend suite covers financial reconciliation, WAL visibility/read-only behavior, mutable settlements, replay, missing stores, missing money, failure isolation/backoff, correction score binding, origin/CSRF/session controls, worker staleness and acknowledgements.

The environment's sandbox blocked listening sockets, Chromium sockets and the ASGI test client's wakeup. Those checks passed with permission outside the sandbox. The normal user launch does not use that agent sandbox.

## Private deployment and recovery

`docker compose up --build -d` prepares a **demo-only** two-process deployment, bound to loopback. Set `PASSERINE_PASSWORD` first. Compose/image execution has not been verified in this session. Real Whiskey Jack integration currently uses the existing source-host interpreter; the container deliberately does not install the bot dependency environment or mount its secrets. Prefer local host launch until a narrow source projection/export bridge is ready.

The host now runs `passerine-api.service` and `passerine-worker.service` as enabled user services, with lingering already enabled. Use `systemctl --user restart passerine-api passerine-worker` after configuration changes; the foreground launcher refuses to duplicate them. Private access uses Tailscale Serve and the exact HTTPS origin configured in `.env`, with Secure cookies and the existing password. See [private Android access and recovery](docs/PRIVATE-ACCESS.md) for the URL, setup status, phone checklist and service commands.

Private HTTPS access and PWA installation worked on the actual Samsung S24+, as confirmed by Chris. Background notification delivery remains disabled and unverified. The phone checklist is available for repeat checks.

Only static `offline.html` is cached by the service worker. Private responses use `Cache-Control: no-store`. Sessions are HttpOnly/SameSite Strict, expire after 12 hours, and browser mutations require an exact Origin plus CSRF token. The app escapes source text and permits only HTTPS source links. Rate limiting is local to the single API process.

Back up the **app** database with SQLite's backup API (below), not by copying a live main database. Keep `.env` separately in secure storage. Stop API/worker before restore, restore to `PASSERINE_DB`, clear old sessions if desired, then restart. Do not restore over either bot database. Events and notification intents persist across restarts; no notifications are delivered by this slice.

```bash
.venv/bin/python scripts/backup.py runtime/passerine.sqlite3 /secure/path/passerine-backup.sqlite3
```

## Next three priorities

1. Establish one narrow, authoritative job-success telemetry interface, preserving independent heartbeat and unknown states; prepare any source addition as a separate reviewable patch.
2. Connect one selected Quire project through server-side read-only OAuth, quota-aware traversal and partial-sync retention once authorized inputs exist.
3. Define ownership for Passerine alerts, then implement durable delivery retries through the existing transport and verify background delivery on the S24+.

See the [post-phone-validation roadmap](docs/ROADMAP.md) for prerequisites and completion criteria, [decisions](docs/DECISIONS.md), [verification](docs/VERIFICATION.md), and [source notices](docs/PROVENANCE.md). The current checkout is a functional Git repository.

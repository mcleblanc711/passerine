Build **Perch** (working name), my private, Android-friendly monitoring app for WETHR, Whiskey Jack, and Quire. Implement a working first slice in this repository; carry on beyond planning.

Read `AGENTS.md`, then `docs/DISCOVERY.md`, `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, `docs/INTEGRATIONS.md`, and `docs/ACCEPTANCE.md`. Consult `docs/RESEARCH.md` for scaffolding candidates. The handoff already includes a source investigation; verify differences against the available/deployed revisions and continue into implementation.

## My context and goal

I run WETHR, a Polymarket weather trading/research bot, and Whiskey Jack, a Metaculus MiniBench forecasting bot. Both are going well. I currently move between Telegram for two-way communication and ntfy for notifications. I use Quire for tasks. I want one place to see results, resolutions, tasks, recent activity, and whether everything is actually working.

I am comfortable with Python, Docker, Ubuntu, n8n, and agentic development. This is a personal application. Optimize for reliable daily use, straightforward maintenance, and a small number of moving parts.

## First inspect what exists

Check this repository's instructions and working tree. Locate the supplied source checkouts. The handoff inspected WETHR `main` at `05813605497b4ec5f1091c78a8af23055f64ef81` and Whiskey Jack `master` at `04f294e53ac8903ae9f55ed7a556ecb65115476f`. Check the deployed revisions, configured database paths, and scheduler evidence without starting bots, submitting forecasts, or placing orders. Update `docs/DISCOVERY.md` with differences and unresolved access; do not print secrets.

Keep source repositories, databases, configurations, and running services unchanged. Some apparently read-only commands initialize/migrate databases: do not poll WETHR's CLI or Whiskey Jack's `tournament status` CLI. Use the strict read-only paths in `docs/INTEGRATIONS.md`. Prepare any necessary telemetry addition separately. In particular, changing Whiskey Jack's effective config/prompt can invalidate its tournament activation binding; Perch settings belong in Perch.

If the source checkouts or credentials are unavailable, continue with clearly labeled synthetic fixtures and working adapter boundaries. Ask only for the smallest missing set of paths or configuration after completing everything possible. Never describe a fixture-backed integration as connected.

## Implementation defaults

- React, TypeScript, Vite, and a compact component set; installable PWA with Android-sized layouts.
- Python/FastAPI backend; its own SQLite database and a single polling worker. Use existing PostgreSQL if it materially simplifies deployment.
- Docker Compose for Perch; preserve the bots' existing systemd deployment. Same-origin UI/API; local development bound to loopback. Prepare private HTTPS access, preferably through Tailscale Serve if suitable.
- Consider the MIT-licensed `fastapi/full-stack-fastapi-template` as a source of reusable scaffolding. Record which pieces are reused and their upstream revision/license. Choose a small scaffold if retaining the full template adds unnecessary services.
- No LLM is needed in the monitoring app's critical path. Keep its operation independent of model/API spend.

## Build the first working slice

Implement Overview, bot details, Tasks, and Activity. Include WETHR and Whiskey Jack cards, an attention queue, recent resolutions, Quire tasks, and explicit freshness states. Add mobile navigation, readable charts only where data supports them, and deep links to original records.

Use labeled synthetic scenarios first: missed job, fresh heartbeat with stale data, resolution awaiting a local score, corrected/withheld resolution, dormant Cup profile, paper P&L by epoch, and disconnected Quire. A manifest and service worker should provide installation support and a clear offline screen. Keep private API data out of persistent browser caches.

Build separate adapters for WETHR, Whiskey Jack/Metaculus, and Quire. Implement whichever real read integrations can be grounded in available code and credentials. The server should schedule collection whether the phone app is open or closed. Persist successful observations and events; make imports idempotent and source failures independent. Persist notification intents before delivery and expose failures.

Implement these source-specific slices:

- **WETHR:** readonly access to `data/wethr.db` or a consistent projection. Show gross realized **paper** P&L in USD, open paper stake/count, current-epoch bankroll, and epoch/all-history filters. Port the inspected accounting definitions with read-only queries; do not call its read/write `get_db`. Its `trades` table also records paper entries during optional live execution. Fees, net/live/unrealized P&L remain unavailable until separately verified. Settlements update rows, so a cursor based only on new trade IDs is insufficient. The hourly JSON export defaults to recent settlements and cannot establish lifetime totals.
- **Whiskey Jack:** use `ledger.connect_readonly` with matching code/schema and `show.assemble_show` for joined record history; use the manifest-backed export for bootstrap/backfill. Serialize selected fields in a Perch-owned adapter; the existing `show` CLI is human text, not a JSON API. Keep MiniBench and historical Cup namespaces separate. Read latest resolution observations and matching local scores, including corrections; do not infer current outcomes from terminal lifecycle status alone. Polling local data frequently does not accelerate the existing six-hour resolution job. Never invoke ingestion, scoring, reconciliation, or submission as a dashboard refresh.
- **Quire:** server-side OAuth and budgeted read sync, including nested tasks and source links. Quire remains authoritative; defer write-back.

Keep explicit freshness, source coverage, and available/missing values. Never add cumulative snapshots. Distinguish local Brier/log diagnostics from official Metaculus scores; official ingestion is unimplemented in the inspected code. Track budget actual/reserved costs using existing reservation semantics. Whiskey Jack has no trading P&L.

Reuse ntfy and the existing Whiskey Jack watchdog where suitable. Persist an activity/alert record and deep link before sending push; avoid duplicate notifications for conditions the bots already send. Direct web push can follow. Keep Telegram workflows working while useful actions migrate deliberately.

## Finish with evidence

Run the meaningful checks in `docs/ACCEPTANCE.md`, inspect the UI at phone and desktop widths, and exercise a disconnected-source scenario. Document exact launch and test commands, real versus demo integrations, required configuration, and the next three tasks. Do not claim Android installation, production health, or notification delivery was verified unless it actually was.

Deliver a runnable local application and a concise implementation summary. If live integrations are blocked, deliver the working demo plus concrete adapter/configuration gaps. Prepare deployment instructions; production rollout is a separate step.

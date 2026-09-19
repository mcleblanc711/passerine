# Architecture defaults

Passerine implements React/Vite, FastAPI, a separate SQLite app database and one
polling process. Native user services and private Tailscale HTTPS are deployed;
actual S24+ access and installation are confirmed. WETHR and Whiskey Jack have
real read-only adapters. Recorded MiniBench tournament heartbeat reading is now
implemented and fixture-verified in an undeployed feature branch. Quire, WETHR
heartbeat and authoritative job-success telemetry, notification
delivery and an external watchdog remain follow-up work. The sections below include
design guidance for those additions; see [discovery](DISCOVERY.md) and the
[roadmap](ROADMAP.md) for the boundary between implemented and proposed behavior.

## Components

| Component | Responsibility |
| --- | --- |
| PWA | Phone/desktop presentation, authenticated API requests, deep links, offline shell |
| FastAPI service | Session/auth boundary, read APIs, alert acknowledgement, rate-limited refresh requests |
| One polling worker | Source collection, transformations, staleness evaluation, event creation, notification delivery |
| Monitoring database | Current observations, selected history, event identities, incidents, sync cursors, notification outbox |
| Source adapters | WETHR readonly projections, Whiskey Jack readonly ledger/history or exports, Quire API; independently fail and recover |
| External watchdog | Detect app/worker/host disappearance from another failure domain |

Keep the UI/API together under one origin. The worker can use the same image with a separate process command. Do not start a scheduler inside every HTTP worker. Use one writer for source collection, short transactions, database constraints, and a local persistent volume.

SQLite is suitable as an initial app store at this scale. Keep it separate from bot databases. Prefer an already-operated PostgreSQL instance if available and easier to support. Do not provision a distributed queue, broker, or time-series database for two bots unless observed requirements justify one.

Keep the existing bot systemd services/timers and n8n deployment. Perch's Compose deployment should consume narrow projections or exports from those hosts. It does not need to run the bots, mount their secrets, install their entire dependency environments, or control their services.

## Source boundary

WETHR uses a Passerine-owned strict read-only SQL projection using its existing accounting definitions. Whiskey Jack uses `connect_readonly` and canonical history assembly through `scripts/read_whiskeyjack.py`, launched with the source-owned interpreter. Its manifest-backed exporter is available upstream but is not consumed by Passerine. Neither integration exposes a source HTTP endpoint; a separate projection/export bridge remains an option for container deployment.

For a shared host, a verified read-only SQLite arrangement can be simpler than a new service. Validate WAL/shared-memory permissions and short consistent transactions before choosing it. Otherwise use consistent snapshots or atomically published projections. Do not copy only a live SQLite main file, use `immutable=1` on a changing file, or migrate the source schema. Match Whiskey Jack reader code to the deployed schema; a newer checkout may correctly refuse an older database.

Bootstrap Whiskey Jack history from a completed JSONL export where practical. Validate its manifest, hashes, counts, and supported schema; do not regenerate or serve full research exports every minute. For recurring collection, publish a small history/status projection. WETHR's existing 24-hour settlement export is only an incremental source and cannot bootstrap all-history P&L.

## Suggested boundaries

- `backend/app/adapters/`: source clients and source-to-domain mapping.
- `backend/app/domain/`: bot health, trading observations, forecasting observations, tasks, and incidents.
- `backend/app/api/`: authenticated endpoints and generated API schema.
- `backend/app/worker/`: scheduling, collection, and notification outbox processing.
- `frontend/`: mobile UI and generated client/types.
- `tests/fixtures/`: synthetic/sanitized source payloads with schema provenance.

This layout is a starting point. Keep the codebase simple; introduce modules only as the first slice needs them.

## Observation model

Use a versioned typed envelope with `source_id`, source instance/profile/ledger identity, stable entity identity, `source_observed_at`, `collected_at`, payload version, origin (`real` or `demo`), and provenance. Track source-check completion separately from an event timestamp. A successful collection time must not overwrite the original data time. Include a source revision/version when available; preserve a content fingerprint otherwise. Namespacing prevents MiniBench and Cup record IDs from colliding.

Domain payloads remain distinct. Common objects should cover health, events, links, and sync metadata, not force money, forecast scores, and tasks into one generic metric.

Keep current snapshots separate from historical events. A source's cumulative P&L is a replaceable observation, not an increment. Event identities should include source, entity, event kind, and source revision or equivalent fingerprint. Accept replay without duplicate incidents; handle later corrections without deleting the audit trail.

WETHR settlements mutate existing records, so ingestion must revisit them. Whiskey Jack corrections may append resolution/score events without changing lifecycle state, so ingest canonical history or all relevant event streams. Bind a current score to the latest eligible resolution, and retain superseded results as history.

## Collection

Starting Perch intervals are configurable suggestions: UI reads cached observations every 15–30 seconds while visible; cheap local projections/health about once a minute; Quire about every five minutes subject to quotas and traversal size. Backfills have a separate schedule and must not block fresh observations.

Read Whiskey Jack's existing resolution evidence in v1. Its checked-in source job runs every six hours; label this upstream cadence and last-success evidence. Do not add duplicate Metaculus polling, or invoke source ingestion/scoring/reconciliation to satisfy an app refresh. Faster upstream resolution checks would be a separate source scheduling change with a quota assessment.

Schedule external calls server-side. Returning to the foreground can refresh the app API without bypassing source cooldowns. All manual refreshes share the same rate limits and work queue/deduplication as scheduled refreshes.

Use bounded HTTP timeouts and retry budgets. Preserve last successful observations on errors; record current source errors alongside them. A Quire outage must not suppress WETHR updates. Commit sync checkpoints only after the corresponding batch is durably processed. Incomplete pagination must never be interpreted as deletion.

## Access

Private HTTPS is deployed through Tailscale Serve to the loopback API. App password,
exact-Origin and CSRF checks remain independent of tailnet membership; proxy identity
headers are not trusted. Actual S24+ access and installation are confirmed. See
[private access](PRIVATE-ACCESS.md) for the verified arrangement and recovery commands.

The phone needs network access to the private origin. Provide an authenticated single-user session or a correctly configured trusted authentication proxy. If using proxy identity, accept it only from that proxy, keep the raw backend unreachable to clients, and allowlist the intended identity. Keep source tokens server-side. Protect mutation endpoints and OAuth callbacks with appropriate session/state checks.

Do not expose the Docker daemon to the app. If host/container metrics are needed, consume an existing exporter or a narrowly scoped host-side collector. Lack of instrumentation should produce “Unknown,” not invented health.

## PWA and notifications

Provide a manifest, icons, standalone layout, and an offline shell. In v1, service workers cache static assets only; private API responses and tokens should not enter persistent browser caches. On connectivity loss, display an offline state and stop describing retained in-memory values as current.

Phone background execution is not the scheduler: browsers control service-worker activation and termination. [Google's service-worker documentation](https://web.dev/learn/pwa/service-workers) explains the lifecycle.

Create an incident/event and notification intent in the database transaction before external delivery. Track attempts, backoff, success, and failure separately. Delivery is generally at least once; use provider idempotency where available and avoid promising exactly-once push. Acknowledgement, recovery, and suppression/cooldown are distinct states.

Both repositories already use ntfy. Reuse it for early push with links into Perch; [ntfy supports notification click targets](https://docs.ntfy.sh/publish/#click-action). Initially send only Perch-owned conditions or explicitly migrated alerts, since existing bot/n8n/watchdog notifications continue independently. Record the owner of each alert condition to avoid duplicate delivery. Keep topic URLs/tokens server-side. Direct Web Push can later consolidate delivery into the app; test permissions, background delivery, expired subscriptions, and private links on the actual phone.

## Watchdog and recovery

Whiskey Jack already has a separate stdlib watchdog with an optional external healthcheck ping. Reuse verified existing coverage and add an independent Perch-worker heartbeat; do not require a second monitoring service by default. A dead-man check needs another host or external service to detect total host loss. Uptime Kuma remains an optional companion. HTTP availability is not proof the polling worker is advancing.

Verify the existing watchdog's limits: resolution timer enabled/active is not evidence of recent successful ingestion. Perch should show unavailable last-success evidence until it has a trustworthy source. Keep intentional dormancy, long-running work, missed successful work, and collector failure distinct.

Back up the monitoring database and the required secret material through the user's established secure process. Treat source history as separately authoritative; the app should rebuild read models where possible without re-sending historical notifications. Define retention for raw payloads and high-frequency samples; preserve necessary accounting coverage and meaningful events.

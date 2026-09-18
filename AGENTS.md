# Project instructions

## Purpose

Perch is Chris's private monitoring app for WETHR, Whiskey Jack, Quire tasks, and operational health. Build small, useful vertical slices. Current inspected source code outranks historical descriptions in the handoff.

## Working method

- Read `docs/DISCOVERY.md`, `docs/PRODUCT.md`, and `docs/ARCHITECTURE.md` before architectural changes. Use `docs/INTEGRATIONS.md` for adapters and `docs/ACCEPTANCE.md` for completion criteria. Reconcile inspected and deployed revisions.
- Inspect existing instructions and uncommitted work. Preserve unrelated changes. Do not run bot entrypoints merely to inspect their behavior.
- Keep evolving discovery in `docs/DISCOVERY.md` and consequential decisions in `docs/DECISIONS.md`. Do not grow this file into a changelog.
- Prefer working software with labeled fixtures when credentials or source access are missing. State the precise missing interface; never invent a production schema.
- Document the actual development, build, and test commands as soon as they exist. Finish with what works, what was verified, and what is blocked.

## Architecture

- Default to a mobile-first React/TypeScript PWA, Python/FastAPI, one polling worker, and a separate SQLite database. Adapt to inspected infrastructure where it simplifies the system.
- Use thin source adapters and typed, versioned contracts. Keep WETHR accounting, Metaculus lifecycle, and Quire semantics in their adapters/domain modules.
- Start with polling. Use timeouts, bounded retries, backoff, persisted sync state, and per-source isolation. Do not introduce a broker, plugin framework, or LLM dependency without a concrete need.
- Bots and Quire retain their authoritative state. The monitoring database contains observations, read models, alert state, and sync metadata.
- Keep bot systemd services in place. Docker Compose is a Perch deployment default, not a bot migration requirement.
- Serve cached server observations when sources fail, with visible age and error state. Keep sensitive API responses out of service-worker caches in v1.

## Data integrity

- Store timestamps in UTC and display with an IANA timezone, default `America/Edmonton`. Preserve date-only due dates without converting them into instants.
- Track collector contact, source observation time, bot heartbeat, and successful job time independently. A recent fetch of an old record does not make the bot healthy.
- Unknown is distinct from zero; stale is distinct from fresh; source failure is distinct from a bot failure.
- Use decimal-safe financial values. Separate paper/live/unknown modes and currencies. Keep realized and unrealized P&L separate; expose fee treatment and coverage. Never sum cumulative snapshots or subtract fees twice.
- Do not label a question resolved because its closing/expected resolution date passed. Official scores and locally computed diagnostics need distinct labels and methodology.
- Deduplicate events with stable source identity. Handle replay, out-of-order observations, changed resolutions, and incomplete pagination without silently losing records.

## Source-specific invariants

- WETHR `trades` is a paper ledger, including during optional live execution. Default to gross realized paper P&L in USD; fees/net/live/unrealized results require additional verified sources. Separate strategy epochs and historical coverage. The unfiltered report's bankroll still belongs to the current epoch; signal Brier statistics are not epoch-scoped.
- WETHR settlements mutate existing rows. New-ID-only ingestion loses updates; its default recent-settlement export cannot establish lifetime totals.
- Whiskey Jack identities include profile/ledger as well as record ID. Use the latest resolution observation and scores bound to that resolution. Local binary/multiclass scores are not official platform scores. Terminal lifecycle status alone is insufficient after corrections.
- Preserve intentional dormancy: the checked-in Cup deployment is withdrawn. Derive alerts from actual enabled profiles and job schedules; a frequent Perch refresh does not accelerate upstream resolution ingestion.

## Access and operational boundaries

- V1 reads existing bot/task state. Local alert acknowledgement and sync requests are allowed app features. Trading, forecast submissions, remote shell, and bot restarts are outside v1.
- Read-only intent is insufficient: WETHR CLI/report helpers and Whiskey Jack's `tournament status` CLI can initialize/migrate databases. Use strict read-only connections or validated exports. Never invoke source ingestion/scoring/reconciliation as a refresh, migrate a source database, or use `immutable=1` on a changing SQLite WAL database.
- Whiskey Jack's config/prompt participates in its activation binding. Keep monitoring configuration in Perch; do not modify source config, prompt, or deployed dependencies to install the dashboard.
- Keep credentials server-side, redact logs, and exclude runtime data from git. Use the narrowest available source credentials and adapter methods.
- Private networking and application authentication are separate controls. Do not expose the backend or accept spoofable proxy identity headers directly.
- Do not mount the Docker socket into this app. Prepare source telemetry additions as separate reviewable patches; do not alter running bot deployments during development.
- Use normal session/CSRF protections for browser mutations. Sanitize source text and allow only expected URL schemes for links.

## Verification and reuse

- Test material risks: financial reconciliation, false resolution, staleness, event deduplication, partial sync, authentication, and unavailable sources. Do not add tests that just repeat implementation details.
- Use synthetic or sanitized fixtures. Keep ordinary tests offline and free of trading/submission side effects.
- Check phone-sized layouts and accessibility; communicate health with text as well as color.
- Preserve upstream license/notice requirements and record copied code provenance. Do not assume every GitHub project has the same reuse terms.

# Integration mappings and contracts

## Start from current evidence

Both repositories were inspected through GitHub on 2026-09-18. [DISCOVERY.md](DISCOVERY.md) pins the revisions and links the implementation evidence. The mappings below are grounded in those commits; compare them with the deployed source/schema before enabling a connection.

Use existing strict read-only helpers and versioned exports where possible. A command named `status` or `report` is not proof that it avoids writes. No unified monitoring HTTP API was established by this inspection; small Perch-owned projections remain implementation work. Preserve existing source services, configuration, and notification paths. Both bots already use ntfy.

## WETHR

The source is a Polymarket weather bot with a **paper trading ledger** at repository-root `data/wethr.db` by default (`WETHR_DB_PATH` override). Confirm the configured path and historical coverage; do not mistake a legacy `collector/data/wethr.db` for the current database.

| Perch concept | Existing source / transformation |
| --- | --- |
| Trade identity | Source-instance/ledger namespace plus `trades.id`; retain city, target date, bracket, side, token/condition IDs where present |
| Mode/currency | `paper`, USD; optional live execution also records here, so runtime live mode cannot relabel this ledger |
| Gross realized P&L | Sum `pnl` where `settled = 1`, optionally filter `strategy_version`; match `paper_trader.get_stats` semantics |
| Open paper stake | Sum `size_usd` where `settled = 0`, with count; not an audited live exposure value |
| Strategy scope | `trades.strategy_version`, `strategy_epochs`, `settings.current_strategy_epoch`; preserve legacy epoch |
| Bankroll | Epoch starting bankroll plus that epoch's realized result; unfiltered source report still returns current epoch bankroll |
| Settlement change | Existing row's `settled`, `settled_at`, `outcome`, `pnl`; detect updates, not just inserts |
| Signal diagnostic | `signals.brier_score`; current aggregate is across epochs |
| Audit evidence | Separate `wethr_audit.db`, `audit_runs`/`divergences_trades`, and `ops.audit_db_status` semantics |

Implement parameterized queries on a strict `mode=ro` connection/consistent snapshot. Do not call the general `paper_trader.get_db`, source CLI, or `export_settled_trades` as a monitor: these open for writing or initialize the database. Use the inspected formulas as the reference and reconcile a known source period without invoking a mutating command. Keep a compatibility check for the required columns; incompatible schema yields an explicit connection problem, never an automatic migration.

For a small ledger, reread the relevant columns in one short transaction and compare fingerprints. For larger history, use separate backfill plus settlement-aware overlap/reconciliation; new trade IDs alone miss updates. Record source event time, collection time, and coverage independently. Interpret known SQLite UTC timestamps explicitly; do not infer the host's timezone from naive strings.

`n8n-wethr/wethr-output/settled_trades.json` defaults to recent 24-hour settlements and excludes open positions. It is useful incremental evidence, not an all-history bootstrap. Keep canonical ledger and n8n audit evidence separate.

V1 leaves fee/net/live/unrealized P&L unavailable. Later verified sources must establish fills, fees, marks, account identity, cash-flow treatment, and coverage before those labels appear. Use decimal-safe output and document conversion from the source's floating-point values; do not imply original precision was greater than stored. Never add cumulative snapshots or subtract fees twice.

Ledger timestamps and successful Perch reads do not prove the collector process is alive. Read existing host telemetry or prepare a narrow systemd/heartbeat projection separately. Do not execute trades or the collector loop to obtain status.

## Whiskey Jack / Metaculus

Use the source's append-only ledger and recorded platform evidence. Default to MiniBench project `33122`; Cup project `33108` is a separate ledger, documented as withdrawn/dormant. Keep source-instance/profile identity in every entity and event key.

| Need | Existing interface / boundary |
| --- | --- |
| Strict ledger read | `ledger.connect_readonly(path)`; validates exact migration checksums/schema, never creates or migrates |
| Per-record detail/history | `show.assemble_show(conn, record_id)`; dataclass with canonical history, uncertainties, and reservations |
| Bootstrap/backfill | `export.py` JSONL/Parquet plus `manifest.json`; one consistent transaction; manifest written last |
| Operational summary | Reuse/adapt underlying `tournament.status` semantics with readonly connection and correct config/artifact context; do not run its read/write CLI |
| Resolutions | Latest append-only `resolution_events` observation per record, including source revision and resolution kind |
| Local scores | `score_events` linked to `resolution_event_id` and implementation version |
| Cost/holds | Existing `tournament_state` reservation/settlement semantics and actual active policy; integer micro-USD conversion |
| Host/worker health | Existing independent `deploy/wj-watchdog`, plus actual systemd/last-success evidence where available |

Serialize selected `assemble_show` fields in a Perch-owned adapter rather than parse human-readable `show` output. Canonical history merges approval, submission attempt, submission verification, lifecycle, pre-forecast failure, resolution, and score streams. Consume every relevant stream or the joined history; lifecycle-only polling misses later resolution/score changes. Keep post, question, child/group, record, attempt, and project IDs distinct.

The exporter currently publishes schema version 1 and 15 tables against ledger migrations through version 16. Validate the actual manifest version, ledger schema, required files, hashes, and row counts; unknown versions fail explicitly. It refuses file overwrites, so generate each snapshot into a unique directory. A valid final manifest is the completion signal. Do not treat a partially written directory as a completed sync or expose full research/model payloads in the mobile API.

The existing readonly reader requires code matching the deployed schema. Use a source-compatible reader beside the ledger, or consume its versioned export. Do not install current head and migrate an older source database to satisfy Perch. Both SQLite adapters must handle WAL consistently; never copy just a live main file or use `immutable=1` on it.

Current outcome is established by the latest resolution observation, not a past lifecycle transition. Preserve `resolved`, `annulled`, `ambiguous`, `withheld`, and `unresolved`; null/withheld is not “No.” Current score display requires the latest eligible resolution ID. A newer withheld/retracted/annulled observation removes an older score from the current panel, while history remains available. Closing/expected-resolution dates never establish an actual resolution.

Supported metrics are **local** binary and multiclass Brier/log diagnostics. Numeric/discrete local scoring and official platform-score ingestion are unavailable in the inspected implementation. Do not present these local results as the official tournament score. Show resolved-but-unscored and out-of-scope states distinctly.

The source already fetches Metaculus question details by post ID and ingests resolutions on a six-hour timer. Perch polls recorded evidence; it does not run `ingest-resolutions`, `score`, `reconcile`, or any submission command. A faster Perch refresh only rereads current local evidence. Further direct platform reads would need a separately designed, verified adapter and quota policy.

Expose submission uncertainties and `unrecorded_posts` separately from process health. Activation `enabled` does not prove a running timer. Treat evidence gaps as the source defines them, not automatic execution failures. Spending is actual settled cost plus still-unsettled reserved estimates; avoid counting a settled reservation twice. Keep all Perch configuration outside source `AppConfig`/prompt inputs, which participate in tournament activation binding.

## Quire

The [official Quire API](https://quire.io/dev/api/) documents OAuth, task reads/updates, webhooks, and quotas. A server-side confidential client suits unattended syncing; follow actual expiry/refresh responses. Its project list endpoint returns root tasks by default, so explicitly retrieve children or use a suitable search endpoint. Preserve OIDs and source task links.

At the research date, documented Free-plan limits were 50 requests/minute and 200/hour per organization; personal-project limits were lower. These are shared budgets and may change. Honor `Retry-After` and verify the user's plan/current quotas. Some search/export features have plan restrictions. Webhooks require a reachable receiver and relevant subscriptions; polling is the initial design.

Implementation choices:

- Register a private app with read access initially. Protect OAuth state, keep secrets/refresh material in server-only storage, and handle revocation with a reconnect state.
- Select explicit project IDs and optional personal tasks. Include unmapped tasks in the Tasks view; project-to-bot labels are a convenience, not a requirement for inclusion.
- Preserve nesting, due-date precision, assignment, and status. Render source text safely; prefer source-provided links.
- Budget all pages and hierarchy traversal. Start around five-minute syncing and increase the interval if complete traversal consumes too much quota. Distinguish full and partial syncs.
- Mark task removals/completions only from adequate source evidence. A failed page must not erase tasks.
- Quire remains authoritative. In a later write phase, serialize changes, verify remote results, surface conflicts, and reconcile ambiguous retry outcomes before repeating non-idempotent creates.

## Minimal common contract

Define typed models after discovery rather than freezing guessed source schemas. Every adapter should expose capabilities, connection/sync state, versioned observations, and normalized events with stable identity.

Required distinctions: `real` versus `demo`; available versus missing values; source time versus collection time; partial versus complete sync; reachable source versus healthy bot; official versus derived metrics. Use decimal strings or minor units for money, and explicit nulls/reasons where data is unavailable.

Adapters should have isolated fixtures and schema-change tests. A new bot should need an adapter and view configuration, without creating a general-purpose plugin platform.

# Repository discovery

## Current checkout review · 2026-09-19

The earlier sections below record September 18 research and deployment evidence;
this review supersedes their pending phone-validation and Git-placeholder claims.
Passerine is a clean, functional Git worktree at
`56bff27ecece602ab3b839e406999d4ac4f14253` before this documentation slice.

WETHR remains at `05813605497b4ec5f1091c78a8af23055f64ef81`. Whiskey Jack is now at
`9e9fcfe51064620fa3d17b98d2321ec1f51095ff`; the diff from the previously inspected
`04f294e53ac8903ae9f55ed7a556ecb65115476f` changes docs, scripts, tests and fixtures,
with no `src/` changes. Its worktree is clean. No source database was opened, and
runtime schema compatibility or process-loaded bot revisions were not reverified.

Read-only systemd inspection shows both Passerine units active/running with this
repository as their working directory. Process state does not prove advancing
collection or identify the exact code loaded by a running process. No service was
restarted and nothing was rebuilt or redeployed.

Chris's handoff confirms private HTTPS access and PWA installation worked on the
actual Samsung S24+. Background notification delivery remains disabled and
unverified. Quire authorized configuration/payloads and authoritative bot heartbeat
and last-successful-job interfaces are still missing. See the
[post-phone-validation roadmap](ROADMAP.md) for bounded next slices.

## Heartbeat interface follow-up · 2026-09-19

The documentation slice was committed/pushed as `75480b2`. Subsequent read-only
source inspection at Whiskey Jack `9e9fcfe51064620fa3d17b98d2321ec1f51095ff` found
an existing tournament heartbeat interface: `tournament.run_once` appends
`tournament_events` with kind `heartbeat`, scope `worker`, at poll start, progress
and completion. Completion may include failures. `tournament.status` selects that
scope; the watchdog reads the newest heartbeat row's `created_at_utc`. The timestamp
is persisted evidence, not a continuous process heartbeat or a resolution-job
success receipt. The heartbeat has no project/activation ID of its own; retain the
reader's configured ledger namespace and do not claim activation-binding health.

The checked-in resolution service runs ingestion followed by scoring, but emits no
such heartbeat or durable successful-job record. The Passerine follow-up therefore
exposes only existing tournament evidence and leaves job success unknown. No source
entrypoint was run and no source files, configs, dependencies or databases changed.

Implementation and synthetic tests use the isolated branch
`feat/whiskeyjack-heartbeat`. This matters because the deployed Passerine worker
launches `scripts/read_whiskeyjack.py` afresh each poll: editing that path in the
running checkout can affect live reads without a restart. No feature changes were
applied there. Live source reads and rollout of the heartbeat feature remain unverified.

## Approved heartbeat deployment · 2026-09-19

With explicit user approval, the running checkout was fast-forwarded to `516ce8a`,
the production frontend was built, and only the two Passerine services were stopped
and started. The app database was backed up first to ignored
`runtime/pre-heartbeat-deploy-20260919.sqlite3`; SQLite integrity_check returned `ok`.
Both bot sources subsequently collected without errors. The real MiniBench
heartbeat read at 14:01:07 UTC carried source time 14:00:20 UTC; successful-job
evidence stayed null. WETHR heartbeat remains unknown.

Private HTTPS browser checks passed. WETHR collector and Telegram process IDs and
start times were unchanged; the resolution service's start time was unchanged and
Cup remained inactive. No bot entrypoint, ingestion, scoring, migration or source
configuration change was invoked for this deployment. Scheduled bot work remains
independent. This supersedes the undeployed status recorded in the follow-up above.

## Original source investigation · 2026-09-18

Inspected through the GitHub connection on **2026-09-18**. This records source evidence, not a production health check. No bot commands were executed, services started, forecasts submitted, trades placed, or source repositories changed.

## Revisions and confidence

| Repository | Default branch | Inspected commit | Commit timestamp (UTC) |
| --- | --- | --- | --- |
| `mcleblanc711/wethr` | `main` | `05813605497b4ec5f1091c78a8af23055f64ef81` | 2026-09-15 11:32:17 |
| `mcleblanc711/whiskeyjack-bot` | `master` | `04f294e53ac8903ae9f55ed7a556ecb65115476f` | 2026-09-17 00:58:03 |

Both repositories were accessible. Their current source trees, selected implementation files, deployment templates, and operational documentation were inspected. Their deployed revisions, databases, environment values, installed unit overrides, and current service state were not accessible in this investigation. Paths and schedules below are checked-in evidence to verify at deployment.

## WETHR

### Existing data and accounting

WETHR trades/researches Polymarket weather markets. Its canonical configured default is repository-root `data/wethr.db`, overridden by `WETHR_DB_PATH`. Treat older `collector/data/wethr.db` references as a possible separate historical store; do not combine histories automatically. The collector is a native systemd service; n8n runs separately in Docker. See [README][w-readme] and [operations][w-ops].

The [paper ledger][w-paper] already defines useful dashboard metrics:

| Metric | Source definition / limitation |
| --- | --- |
| Gross realized paper P&L | Sum `trades.pnl` where `settled = 1`; optional `strategy_version` filter |
| Settled stake | Sum `size_usd` for settled trades in the selected scope |
| Open paper stake/count | Sum `size_usd` / count where `settled = 0`; label as recorded stake, not a verified live risk measure |
| Current epoch | `settings.current_strategy_epoch`, with `strategy_epochs` metadata and starting bankroll |
| Epoch bankroll | That epoch's starting bankroll plus its realized P&L |
| All-history report bankroll | Still the **current epoch's** bankroll, even though its P&L covers the whole ledger |
| Signal Brier statistics | Read from `signals` across epochs; not scoped by the trade epoch filter |

Amounts are USD paper accounting. There is no explicit fee deduction in `get_stats`; v1 must not relabel gross P&L as net. The code does not provide a verified live-account or unrealized-P&L report for Perch to reuse. If showing `gross_pnl / settled_stake`, call it return on settled stake, not portfolio return.

The [execution loop][w-main] records a paper trade before optional live execution. Therefore `WETHR_LIVE=1` would not turn this table into an authoritative live fill ledger. The checked-in service uses `WETHR_LIVE=0`; the actual installed environment remains unverified.

Settlements update existing trade rows. Polling only IDs greater than the last seen trade loses these changes. Initial implementation should read a consistent bounded/full projection or use settlement timestamps with overlap and fingerprints. A trade's creation time is not its latest settlement observation time.

### Existing reports and safe access

[Telegram reports][w-telegram] already distinguish current epoch, legacy history, and all-time P&L. Reuse their definitions rather than scrape message text. `/status` explicitly reports ledger evidence, which is not a process heartbeat.

WETHR's general `get_db` opens SQLite for writing, enables WAL, and commits. Its main CLI invokes `init_db()` before dispatching reporting commands. `ops.export_settled_trades` also initializes the database. These are not strict read-only monitoring interfaces.

The [settlement exporter and audit reader][w-ops-code] are useful references, with different boundaries:

- `n8n-wethr/wethr-output/settled_trades.json` defaults to the last 24 hours of settlements. It omits open positions and earlier history, so it cannot establish lifetime P&L.
- `n8n-wethr/wethr-output/wethr_audit.db` contains `audit_runs` and `divergences_trades`; `audit_db_status` opens this store with `mode=ro`. Its daily freshness logic expects 09:00 America/Edmonton plus a 15-minute grace period.

Build a small Perch-owned, strict read-only projection over the ledger or a consistent source-host snapshot. Do not import general initialization paths merely to calculate a report. WAL readers must see committed WAL data; copying only the main `.db` file or using `immutable=1` on the live file is unsuitable.

### Checked-in schedules and notifications

| Job | Source schedule / interpretation |
| --- | --- |
| Collector loop | Default 600 seconds via `WETHR_SCAN_INTERVAL`; actual configuration can differ |
| Settlement | First scan after midnight UTC; unresolved target dates are retried daily |
| Settlement export | Five minutes after boot, then hourly |
| Daily calibration | 04:15 UTC |
| Monthly calibration | `OnCalendar=monthly`; check host timezone |
| n8n audit | Hourly trigger gates production auditing to once daily after 09:00 America/Edmonton |

Sources: [operations][w-ops], [main loop][w-main], and [systemd units][w-units]. Existing ntfy code sends position, settlement, and calibration messages; n8n audit notifications have a separate path. Bot notification mutes do not necessarily mute n8n. Preserve the existing Telegram long-poll consumer rather than starting another one. Source credentials/topic URLs should stay on the server.

## Whiskey Jack

### Profiles, source ownership, and reusable reads

The [MiniBench config][j-config] identifies project `33122` and a SQLite ledger at `/home/cleblanc/projects/whiskeyjack-bot/data/whiskeyjack_bot.sqlite3`, with artifacts, exports, and logs under the same project's `data/` directory. These are checked-in deployment leads, not verified paths on a connected host.

The separate [Cup config][j-cup] uses project `33108` and `data/cup/ledger.sqlite3`. [Tournament operations][j-ops] documents Cup withdrawal on September 10 and retired/disabled operation. Treat Cup as optional historical data until current deployment evidence says otherwise. Namespace records by source instance/profile/ledger; IDs can collide across databases. The [backlog][j-backlog] has Cup resolution ingestion scheduling (`M4-806`) marked Not Started.

Three useful existing interfaces reduce Perch's implementation work:

1. [`ledger.connect_readonly`][j-ledger] opens with `mode=ro`, validates schema/migration checksums, and refuses incompatible stores without migrating them. Use source code matching the deployed schema. WAL shared-memory/locking requirements still apply; read-only database content does not mean every filesystem arrangement supports the reader.
2. [`show.assemble_show(conn, record_id)`][j-show] returns joined record details, uncertainties, reservations, and canonical history. It merges seven event categories: approval, submission attempt, submission verification, lifecycle, pre-forecast failure, resolution, and score. Resolution corrections and rescoring may not create lifecycle transitions, so lifecycle-only ingestion is incomplete. The existing `show` CLI prints human-readable text; a JSON wrapper is proposed Perch work.
3. The [JSONL/Parquet exporter][j-export] reads all tables in one transaction and writes a versioned manifest last. At this commit `EXPORT_SCHEMA_VERSION = 1`, the migrations reach version 16, and `EXPORTED_TABLES` contains **15** entries (the introductory docstring still says fourteen). Each manifest records file names, columns, identifiers, row counts, and SHA-256 hashes. Use a new directory per export; ignore partial directories without a valid manifest. Full exports include research content and are best for bootstrap/backfill, not frequent phone responses.

The [`tournament status` CLI][j-cli] prints JSON, but its command path opens a read/write verified ledger and can run migrations. Do not poll it from Perch. Its underlying status calculation can inform a strictly read-only projection, preserving its actual config/artifact context. It distinguishes heartbeat, activation/refusal, spending holds, confirmed forecasts, comments, unresolved submissions, unrecorded posts, and evidence gaps. `enabled` does not prove that timers are running or credentials work.

[Tournament state][j-state] binds activation to effective configuration and prompt content. Keep Perch settings outside source config. Budget costs use micro-USD: settled actual spend and estimates for still-unsettled reservations are separate. Use current activation policy and source calculation; do not hardcode a budget from an example.

### Resolution and score semantics

The [existing ingester][j-resolutions] uses the existing Metaculus client to fetch questions by post ID, handles groups, and revisits previously submitted/resolved/scored records so corrections can be recorded. It appends local ledger events. Although the platform call is a GET, running this command is a **local write**, outside a Perch refresh.

Latest resolution observations can be `resolved`, `annulled`, `ambiguous`, `withheld`, or `unresolved`. Preserve these distinctions and the source revision. A withheld/null outcome is not a negative binary result. Terminal lifecycle state can survive a later resolution change; the latest resolution event establishes current outcome evidence.

[Local scoring][j-scoring] implements `local_brier_binary`, `local_log_binary`, `local_brier_multiclass`, and `local_log_multiclass`. Numeric/discrete local scoring is out of scope. A current score must reference the current eligible `resolution_event_id` and its implementation version. Retain old scores as history after corrections, without presenting them as current. Official platform/numeric score ingestion (`M4-803`) is Not Started in the [backlog][j-backlog].

### Checked-in schedules and health

| Job | Source schedule / interpretation |
| --- | --- |
| Tournament poll | Every five minutes; oneshot service can legitimately run up to 40 minutes |
| Resolution ingestion, then scoring | 00:23, 06:23, 12:23, 18:23 in the host timezone; persistent timer |
| Watchdog | Every five minutes, offset by two minutes |

See [systemd units][j-units]. Scheduled scoring runs only after the ingestion command exits successfully; a partially successful ingestion can leave new resolutions awaiting scores. A one-minute Perch poll does not make upstream resolution evidence arrive sooner.

The independent [watchdog][j-watchdog] already reads SQLite with `mode=ro`, checks tournament staleness and resolution timer/service state, and supports an optional `WJ_HEALTHCHECK_URL` external dead-man ping. Reuse it. Its tournament staleness default is 20 minutes with in-progress handling; inspect actual settings before defining alerts. Resolution checks do not yet establish last-trigger freshness (`M1-343` remains Not Started), so an enabled timer alone is insufficient evidence of a recent successful ingestion. ntfy is already integrated.

## Remaining implementation inputs

- Deployed source revisions, host(s), database paths, SQLite/WAL permissions, and available export locations. Match deployed schema before enabling an adapter.
- Installed service/timer definitions, overrides, host timezone, current activation/profile state, and last successful job evidence. Treat checked-in defaults as expectations until verified.
- WETHR historical coverage and any separate authoritative live-fill/fee/mark data if live or net P&L is requested. The initial paper view needs no exchange credentials.
- Whether the optional Whiskey Jack external healthcheck is configured, and which existing notification conditions should be linked or suppressed in Perch to avoid duplicates.
- Quire OAuth registration, selected projects, plan/quota, and safe sample task payloads; private access arrangement and actual Android browser/device.

Missing deployment access should result in a labeled runnable demo and precise configuration requests, not a fabricated connected state. No general dashboard fork removes these adapter requirements. The most valuable reuse found here is already in the two source projects.

[w-readme]: https://github.com/mcleblanc711/wethr/blob/05813605497b4ec5f1091c78a8af23055f64ef81/README.md
[w-ops]: https://github.com/mcleblanc711/wethr/blob/05813605497b4ec5f1091c78a8af23055f64ef81/OPERATIONS.md
[w-paper]: https://github.com/mcleblanc711/wethr/blob/05813605497b4ec5f1091c78a8af23055f64ef81/collector/src/paper_trader.py
[w-main]: https://github.com/mcleblanc711/wethr/blob/05813605497b4ec5f1091c78a8af23055f64ef81/collector/src/main.py
[w-telegram]: https://github.com/mcleblanc711/wethr/blob/05813605497b4ec5f1091c78a8af23055f64ef81/collector/src/telegram_bot.py
[w-ops-code]: https://github.com/mcleblanc711/wethr/blob/05813605497b4ec5f1091c78a8af23055f64ef81/collector/src/ops.py
[w-units]: https://github.com/mcleblanc711/wethr/tree/05813605497b4ec5f1091c78a8af23055f64ef81/deploy/systemd
[j-config]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/config/tournament.yaml
[j-cup]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/config/tournament-cup.yaml
[j-ops]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/docs/TOURNAMENT-OPERATIONS.md
[j-ledger]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/src/whiskeyjack_bot/ledger.py
[j-show]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/src/whiskeyjack_bot/show.py
[j-export]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/src/whiskeyjack_bot/export.py
[j-cli]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/src/whiskeyjack_bot/cli.py
[j-state]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/src/whiskeyjack_bot/tournament_state.py
[j-resolutions]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/src/whiskeyjack_bot/resolution_ingest.py
[j-scoring]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/src/whiskeyjack_bot/scoring.py
[j-backlog]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/docs/backlog/backlog.csv
[j-units]: https://github.com/mcleblanc711/whiskeyjack-bot/tree/04f294e53ac8903ae9f55ed7a556ecb65115476f/deploy/systemd
[j-watchdog]: https://github.com/mcleblanc711/whiskeyjack-bot/blob/04f294e53ac8903ae9f55ed7a556ecb65115476f/deploy/wj-watchdog

## Local implementation verification · 2026-09-18

The local `/home/cleblanc/projects/wethr` and `/home/cleblanc/projects/whiskeyjack-bot` checkouts match the pinned commits above exactly. Both contain available databases at the documented default paths. Installed user service working directories point to these checkouts. WETHR has existing unrelated documentation edits (`README.md`, `docs/README.md`, `docs/SQL_GUIDE.md`); they were preserved. Passerine's supplied `.git` is a read-only placeholder, not a usable Git worktree.

Read-only installed service evidence: `wethr-collector.service` active/enabled; `whiskeyjack-resolutions.timer` active/enabled with `OnCalendar=*-*-* 00/6:23:00`; `whiskeyjack-tournament-cup.timer` inactive/disabled. Unit state is inspection-time evidence, not an ongoing health integration or proof of last successful ingestion. Effective environment overrides/activation binding and process-loaded code revision were not established; no secrets were printed.

The implemented WETHR adapter successfully read the current ledger using a mode=ro transaction, including WAL rows. Whiskey Jack's matching `connect_readonly` validation and `assemble_show` successfully read 24 records and 116 canonical events. Initial sandbox refusal was SQLite directory/shared-memory access, not an incompatible schema; the approved reader succeeded outside that sandbox. No source initialization, CLI, ingestion, scoring or migration was run.

Passerine keeps the databases/configs/dependencies owned by the bots unchanged. Its own DB is under ignored `runtime/`. Quire OAuth registration, project selection and validated read payloads remain missing; the task UI is disconnected in real mode and synthetic in demo. Export-manifest bootstrap, live bot heartbeat/job telemetry, external worker watchdog and notification delivery remain unimplemented.

## Private access deployment · 2026-09-18

At this session's inspection, Tailscale 1.102.4 was already installed and authenticated,
with this Linux host and Chris’s S24+ online in the same tailnet. MagicDNS was enabled;
Serve required account activation (completed by the user) and a sudo-authorized host
configuration write. The host’s user linger setting was already yes and tailscaled
was enabled. The phone answered a Tailscale ping through the SEA relay; this does not
prove reverse-direction HTTPS access or Android installation.

Two enabled Passerine-only user units replace the foreground launcher. API binds
127.0.0.1:8000 and ignores proxy headers; worker uses its existing exclusive lock.
The exact tailnet HTTPS origin and Secure cookies are configured in the private .env.
Source checkout revisions still match the discovery pins. WETHR collector/Telegram
PIDs and activation timestamps were unchanged after deployment; Cup remains disabled.
No bot deployment/config/prompt/dependency was modified. See PRIVATE-ACCESS.md for
commands, URL and repeat-check instructions.

Serve was subsequently configured by the user with sudo. The saved configuration
contains HTTPS on 443 with the root handler proxying only http://127.0.0.1:8000, and
no Funnel entry. The real HTTPS origin passed automated Chrome login, CSRF, secure
cookie, source freshness, four-width navigation, offline cache and logout checks.
Actual Android HTTPS access and installation were subsequently confirmed by Chris;
see the September 19 review above. Separate network-transition results were not recorded.

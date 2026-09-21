# Verification · 2026-09-18

## Deployment preparation · 2026-09-21

In isolated `/tmp/passerine-questions.6iLfRS`, feature code `0fcd86d`:

- `/home/cleblanc/projects/passerine/.venv/bin/pytest -q`: 25 passed,
  two existing dependency deprecation warnings. A first sandbox run was interrupted;
  the full rerun outside the sandbox completed in 73.88 seconds.
- `npm --prefix frontend run build`: TypeScript and Vite production build passed.
  Artifacts are in this worktree's ignored `frontend/dist`, not the deployed tree.
  The original checkout's Python environment and Node modules were reused without
  installing or changing dependencies; the Node modules link was recreated locally.
- `PASSERINE_CHROMIUM=/opt/google/chrome/chrome node scripts/verify-questions.mjs`:
  passed with synthetic API responses at 360/390/430/1440px, including all forecast
  types, zero probability, unavailable community and escaped source text. The first
  browser run timed out loading the preview; the rerun outside the sandbox passed.
  The isolated Vite server on port 5175 was stopped afterward.
- Read-only service inspection: both Passerine services active/running from the
  main checkout. No services stopped/restarted, production assets replaced,
  production databases backed up/restored, or live source reads requested.

The prepared [deployment procedure](DEPLOYMENT.md) includes post-rollout checks.
Private HTTPS and real-reader evidence above/below remain historical until rollout.

## Question display milestone · checkpoint 2026-09-21

Checks completed September 19 in isolated `feat/minibench-questions`:

- 25 backend tests passed (the same two dependency deprecation warnings), including
  probabilities of zero/one, option ordering, numeric/discrete values, timestamps,
  version retention and exclusion of private model/research fields. The existing
  heartbeat reader fixture was extended for the new source read interface.
- `frontend/node_modules/.bin/tsc --noEmit -p frontend/tsconfig.json` passed.
- Real read-only projection succeeded for 24 records, all with question titles and
  recorded forecasts. No community values were claimed; see discovery for coverage.
- `PASSERINE_CHROMIUM=/opt/google/chrome/chrome node scripts/verify-questions.mjs`
  passed against an isolated Vite server on port 5175 with intercepted synthetic API
  responses: all four forecast types, zero probability, explicit unavailable
  community, safely escaped source text, no browser errors and no horizontal
  overflow at 360/390/430/1440px. The saved 390px screenshot was visually reviewed
  at the September 21 checkpoint. The check handles details already expanded when
  changing viewport; an initial test assertion was corrected for that state.

Repeat with `.venv/bin/pytest -q`, the TypeScript command above, and
`npm --prefix frontend run dev -- --port 5175` plus the browser command in another
terminal. This worktree reused the main checkout's Python and Node dependencies;
ordinary backend fixtures remain offline. No production build or deployment was
performed for this feature. Main remains on deployed heartbeat revision `7b91955`.

## Current status · 2026-09-19

Chris confirmed that private HTTPS access and Android PWA installation worked on
the actual Samsung S24+. Those checks are complete; the September 18 results below
remain historical evidence. The confirmation does not separately enumerate network
transitions or device offline behavior. Background notification delivery is still
disabled and unverified. Compose and whole-host reboot recovery remain unverified.

The documentation review started from a clean, functional Git checkout at
`56bff27ecece602ab3b839e406999d4ac4f14253`. Read-only service inspection found both
Passerine units active/running from this project directory, with main-process start
times of September 18, 07:08:37 MDT. This establishes process state, not advancing
worker heartbeat or fresh source observations. No build, redeployment, service
restart, source read cycle or bot command was run during this review.

Source checkout revisions were compared with the prior pins; see
[discovery](DISCOVERY.md#current-checkout-review--2026-09-19). `git diff --check`
passed, and a Node filesystem check validated all 19 relative Markdown file links
across README and the 11 docs files. Status claims and the final diff were reviewed.
Prior backend/browser passes below were not rerun for this documentation-only change.

## Recorded tournament heartbeat · 2026-09-19

Implemented on isolated branch `feat/whiskeyjack-heartbeat`; not rebuilt or deployed.
The running checkout stays on documentation commit `75480b2`. Source compatibility
is grounded in inspected Whiskey Jack code, not a fresh production-ledger read.

- Focused heartbeat suite: 11 passes covering missing/wrong-scope evidence,
  sequence ordering, timezone normalization, invalid/future timestamps without
  fallback, reader-to-observation persistence, replay, source failure retention,
  unchanged source fixture bytes, and job-success separation for incomplete,
  completed and failed polls.
- Full offline backend suite: 18 passes, with the same two dependency deprecation
  warnings. Ran outside the sandbox for ASGI test-client support; fixtures use
  temporary synthetic databases and no bot execution or network.
- TypeScript check passed with `tsc --noEmit`; no production assets were rebuilt.
- Chrome using the isolated Vite development server and intercepted synthetic API
  responses passed heartbeat labels, unknown job success and no horizontal overflow
  at 360/390/430/1440px. The 390px screenshot was visually inspected. Chrome required
  execution outside the sandbox because its sockets were blocked. This is a fixture
  browser check, not deployment or device verification; prior S24+ installation and
  private access remain confirmed.

Repeat checks from a checkout with development dependencies installed:

```bash
.venv/bin/pytest -q tests/test_whiskeyjack_heartbeat.py
.venv/bin/pytest -q
frontend/node_modules/.bin/tsc --noEmit -p frontend/tsconfig.json
```

For the synthetic UI check, run `npm --prefix frontend run dev -- --port 5174`
in an isolated checkout, then in another terminal:

```bash
PASSERINE_CHROMIUM=/opt/google/chrome/chrome node scripts/verify-heartbeat.mjs
```

Screenshots go to ignored `runtime/screenshots/`. Stop only that development server
afterward. During this run the isolated worktree reused the original checkout's
Python environment and node_modules; no dependencies were installed or changed.

Authoritative successful-job evidence, WETHR heartbeat, activation-binding health,
notification delivery, real-read verification of the new heartbeat projection and
feature rollout remain outstanding.

## Approved rollout · 2026-09-19

- Deployed feature commit `516ce8a` after explicit user approval. Production
  `npm --prefix frontend run build` passed. Only Passerine API and worker were
  stopped/started; both are active with new main processes.
- App backup `runtime/pre-heartbeat-deploy-20260919.sqlite3` was created with umask
  0077 using the SQLite backup API before the feature update; read-only
  `PRAGMA integrity_check` returned `ok`.
- Real WETHR and Whiskey Jack collections succeeded after restart. At 14:01:07 UTC,
  MiniBench's recorded heartbeat was 14:00:20 UTC; job success remained null. No
  production source database was migrated or written by Passerine.
- `PASSERINE_CHROMIUM=/opt/google/chrome/chrome node scripts/verify-private.mjs`
  with the existing server environment passed trusted HTTPS, login, cookie flags,
  unauthenticated/spoofed identity rejection, Origin/CSRF controls, fresh worker,
  real source reads, all routes at four widths, offline-only cache and logout.
- WETHR collector and Telegram process IDs/start times were unchanged; resolution
  service start time was unchanged and Cup remained inactive. Bot services and
  source configuration were not modified.

The 18-test backend suite passed before rollout; no backend behavior changed during
deployment. Actual S24+ installation/access remain confirmed from prior validation.
Successful-job telemetry, WETHR heartbeat, notifications and Compose remain gaps.
Earlier undeployed statements in this document describe the pre-rollout stage.

## Initial passes · 2026-09-18

- Production TypeScript check and Vite build (`npm --prefix frontend run build`). npm dependency audit reported no vulnerabilities at installation.
- Seven offline backend tests: WAL-visible readonly reads/refused writes, missing-source refusal without creation, epoch/all-history totals and current bankroll, mutable settlements, replay deduplication, unknown money, independent failures/cooldown/recovery, session/origin/CSRF/spoofed-header rejection, stale-worker detection, acknowledgement without false recovery, latest-resolution score binding and demo/ledger identity separation.
- Five Playwright tests against the built app: all routes at 360/390/430/1440 CSS pixels, no horizontal overflow, login, epoch filter reconciliation ($15 all-history / $105 current bankroll), withheld/unscored display, offline navigation and static-only service-worker cache.
- Phone and desktop screenshots visually inspected. Screenshots live in ignored `runtime/screenshots/`. Keyboard focus styles, semantic headings/buttons/labels, mobile navigation and text health labels are present; this is not a complete assistive-technology audit.
- Real worker cycle: WETHR and Whiskey Jack both successfully connected, Quire remained explicitly disconnected, and 890 source events persisted in `runtime/real-verification.sqlite3`. WJ matching readonly/schema reader assembled 24 forecasts and 116 canonical events. No bot entrypoint, ingestion, scoring or migration invoked.
- Installed service states checked read-only: WETHR active/enabled, resolution timer active/enabled, Cup timer inactive/disabled.

The ASGI test/client event-loop wakeup, Chromium local sockets and server listening socket needed permission outside this environment's agent sandbox. Whiskey Jack's SQLite shared-memory locks also required that permission. There were two upstream deprecation warnings from Starlette's test-client/httpx/AnyIO integration; tests passed.

## Not verified / not implemented

- Real-device background notifications, whole-host reboot and Docker image/Compose execution. Actual S24+ HTTPS access and installation are now confirmed above; individual network-transition results are not separately recorded.
- Quire OAuth, real task reads, quota behavior and incomplete-page reconciliation. Current adapter is explicitly unavailable; tasks are synthetic only in demo.
- Source-host heartbeat/last-success projection, ongoing installed-unit/activation verification, external worker dead-man monitor. A recent successful read does not label a bot healthy.
- Notification transport/retries/delivery. Outbox intents are durably `disabled`, and existing bot notifications remain in place.
- Whiskey Jack manifest-export bootstrap, historical Cup data, official scores, unrecorded-post reconciliation summary. Real MiniBench canonical history and current local scores are implemented.
- Full historical coverage certification, live/net/fee/unrealized P&L. Only recorded gross paper USD accounting is supported.

No production-ready or notification-delivered claim is made. All verification-only processes were stopped after testing; use the README launch commands for daily operation.

## Persistent services deployment · 2026-09-18

- Both unit files passed `systemd-analyze --user verify`; production frontend build
  passed; the seven offline backend tests passed again (same two dependency warnings).
- `passerine-api.service` and `passerine-worker.service` installed/enabled/running.
  Explicit restart succeeded; an unexpected SIGTERM to each main process produced
  one automatic restart each. Exactly one API and one worker remained, parented by
  the user service manager. The API listener is exclusively 127.0.0.1:8000.
- Fresh real WETHR/Whiskey Jack observations and advancing worker heartbeat verified
  after migration; Quire remains unavailable. Existing WETHR collector/Telegram PIDs
  unchanged and Cup disabled. Source commits still match discovery.
- User lingering and system tailscaled boot enablement confirmed without changing
  host policy. Whole-host reboot/suspend behavior remains untested to preserve bots.
- App SQLite backup restored to a separate app database, passed integrity_check and
  matched counts in sources/events/incidents/outbox/meta/sessions. Local backup and
  restore artifact are mode 0600; off-host backups and retention remain unconfigured.
- S24+ responds to Tailscale relay ping. Serve activation and persistent proxy configuration
  completed. Configuration confirms HTTPS 443 → loopback 8000 and no Funnel.
- `PASSERINE_CHROMIUM=/opt/google/chrome/chrome node scripts/verify-private.mjs`
  passed against the actual HTTPS origin using the existing private environment:
  trusted certificate, unauthenticated/spoofed-identity rejection, login, Secure/HttpOnly/
  SameSite Strict cookie, no-store private API, fresh worker and real bot reads, missing
  CSRF/wrong-Origin rejection, valid refresh, all routes at 360/390/430/1440 widths,
  offline-only cache/fallback and logout. No TLS validation bypass was used.
  The default Playwright browser binary was missing; installed Chrome passed.
- Actual S24+ HTTPS access and Android PWA installation were subsequently confirmed
  by Chris; see the September 19 status above. Host browser checks alone did not
  establish actual-device behavior.

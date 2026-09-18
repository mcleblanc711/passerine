# Verification · 2026-09-18

## Passed

- Production TypeScript check and Vite build (`npm --prefix frontend run build`). npm dependency audit reported no vulnerabilities at installation.
- Seven offline backend tests: WAL-visible readonly reads/refused writes, missing-source refusal without creation, epoch/all-history totals and current bankroll, mutable settlements, replay deduplication, unknown money, independent failures/cooldown/recovery, session/origin/CSRF/spoofed-header rejection, stale-worker detection, acknowledgement without false recovery, latest-resolution score binding and demo/ledger identity separation.
- Five Playwright tests against the built app: all routes at 360/390/430/1440 CSS pixels, no horizontal overflow, login, epoch filter reconciliation ($15 all-history / $105 current bankroll), withheld/unscored display, offline navigation and static-only service-worker cache.
- Phone and desktop screenshots visually inspected. Screenshots live in ignored `runtime/screenshots/`. Keyboard focus styles, semantic headings/buttons/labels, mobile navigation and text health labels are present; this is not a complete assistive-technology audit.
- Real worker cycle: WETHR and Whiskey Jack both successfully connected, Quire remained explicitly disconnected, and 890 source events persisted in `runtime/real-verification.sqlite3`. WJ matching readonly/schema reader assembled 24 forecasts and 116 canonical events. No bot entrypoint, ingestion, scoring or migration invoked.
- Installed service states checked read-only: WETHR active/enabled, resolution timer active/enabled, Cup timer inactive/disabled.

The ASGI test/client event-loop wakeup, Chromium local sockets and server listening socket needed permission outside this environment's agent sandbox. Whiskey Jack's SQLite shared-memory locks also required that permission. There were two upstream deprecation warnings from Starlette's test-client/httpx/AnyIO integration; tests passed.

## Not verified / not implemented

- Actual Android install, phone-to-host HTTPS over Wi-Fi/cellular, real-device background notifications, whole-host reboot and Docker image/Compose execution. See deployment verification below for host rollout status.
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
- Actual S24+ Wi-Fi/cellular HTTPS access and Android PWA installation remain pending
  user confirmation. Host browser checks do not establish actual-device behavior.

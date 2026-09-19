# Implementation decisions · 2026-09-18

## Post-phone-validation review · 2026-09-19

- Complete the documentation reconciliation before the next integration: actual
  S24+ access and installation are confirmed, while delivery remains disabled.
  Preserve prior verification dates rather than imply tests were rerun.
- Prioritize one authoritative job-success telemetry interface next because current
  successful source reads cannot answer whether scheduled bot work succeeded.
  Start with interface discovery; do not infer success from an enabled timer or a
  ledger event. Any required source producer is a separate reviewable patch and
  must not be applied to running bot deployments as part of Passerine development.
- Keep Quire disconnected until authorized scope and verified payloads exist.
  Keep notification delivery disabled until ownership and transport configuration
  are established. The [roadmap](ROADMAP.md) defines small completion boundaries
  without treating these inputs as already available.

## Recorded heartbeat slice · 2026-09-19

- Use the existing MiniBench tournament heartbeat as the first telemetry slice.
  Source inspection found this interface, while resolution-job success still needs
  a producer. Expose the scope and limitations alongside the timestamp; do not
  infer successful work from a heartbeat, completion flag or zero failures.
- Add an optional explanatory field to the version-1 observation. Keep source
  event time, collection time and job success independent. Invalid newest evidence
  stays unknown; do not silently substitute an older valid heartbeat.
- Implement in an isolated worktree because the live worker reloads the reader
  script every poll. A commit or push is not permission to deploy this reader.

## Initial implementation · 2026-09-18

- Name is **Passerine**. Historical handoff references to Perch describe the same project.
- Small original scaffold; no full-stack template copied. React/Vite + FastAPI + app SQLite + single file-locked worker. No broker, LLM, trading or submission dependency.
- Both local source revisions match the handoff. WETHR uses a Passerine-owned full read-only transaction. Whiskey Jack runs our selected-field reader with its existing matching interpreter and readonly ledger/show modules, with bytecode writes disabled. No source environment installation or configuration edits.
- An app database is bound to one origin/ledger per source. Changing ledger path or switching demo/real requires a new app database; do not silently merge source identities. Event keys include source instance and canonical identity/fingerprint.
- Missing heartbeat/job evidence remains unknown. A source event timestamp is not a process heartbeat. Browser API requests and worker contact are independently visible.
- Fixed demo scenarios illustrate missed successful work despite newer heartbeat, stale inputs, resolved/unscored, corrected/withheld outcomes, intentional Cup dormancy, and nested date-only tasks. They are isolated from real observations.
- Quire is an explicit unavailable adapter, not an invented schema. Real OAuth/pagination is deferred until authorized configuration and payloads exist.
- Notifications are disabled but durable intents are recorded atomically with source-failure incidents. Transport retry/delivery and alert ownership are pending. Existing ntfy/watchdog/Telegram services remain untouched.
- Local single-user password session boundary, explicit origin/CSRF, no trusted identity headers. API has no shell, bot action, source write or OAuth token input endpoint.
- Poll sources at 60 seconds (Quire placeholder 300), exponentially back off independently to one hour. Manual refresh records a request and fetches cached data; never bypasses source cooldown or invokes upstream jobs.
- Compose is a demo preparation path. Native host execution is the verified real-read path because it can reuse Whiskey Jack's deployed reader dependencies without changing them.

## Persistent private host operation · 2026-09-18

- Use native user systemd services for the API and single worker, matching the verified
  host reader/interpreter arrangement. Keep Compose demo-only and existing bots independent.
- Load the mode-0600 environment file through systemd; remove the app password from the
  worker environment. Use restrictive creation permissions and no-new-privileges.
- Terminate HTTPS at persistent Tailscale Serve, keep raw API on IPv4 loopback, disable
  Uvicorn proxy-header trust, and retain app password, exact-Origin and CSRF checks.
- Preserve existing host suspend/reboot policy; real reboot testing would interrupt bots.
  Lingering/boot enablement and Passerine-only service restarts establish configuration
  evidence, not a claim of tested whole-host recovery.

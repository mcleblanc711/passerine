# Implementation decisions · 2026-09-18

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

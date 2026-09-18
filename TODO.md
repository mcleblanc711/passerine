# Passerine — next-session handoff

Updated 2026-09-18. Passerine is the final name; Perch was the working name.

## Start here after /clear

Read `AGENTS.md`, this file, `README.md`, `docs/DISCOVERY.md`, `docs/DECISIONS.md`, and `docs/VERIFICATION.md`. Inspect current files and running processes before changing anything. The user has successfully launched the app and logged in at `http://127.0.0.1:8000/` on this computer.

Do not restart broad repository research. Both local bot checkouts matched the handoff commits during implementation. Preserve their running services, source databases, configuration, prompts and dependencies. Keep all credentials out of chat, logs and version control.

## Working now

- [x] React/TypeScript mobile UI: Overview, Bots/details, Tasks and Activity.
- [x] FastAPI, separate app SQLite store and one file-locked polling worker.
- [x] Password sessions, exact-Origin and CSRF protection; private API responses are not cached.
- [x] Real WETHR strict readonly ledger projection: gross paper USD P&L by epoch/history, current-epoch bankroll, open paper stake and mutable settlements.
- [x] Real Whiskey Jack matching `connect_readonly` + `assemble_show`: MiniBench canonical history, current resolutions, resolution-bound local scores and actual/held costs.
- [x] Independent source failures/backoff, retained observations, persistent events/incidents/acknowledgements and disabled notification intents.
- [x] Separate labeled demo scenarios; real/demo and different ledger identities cannot silently share the same app database.
- [x] PWA manifest/icons and offline screen. Browser cache contains only the offline page.
- [x] Seven backend tests and five browser tests passed; phone widths 360/390/430 and desktop 1440 checked. Production build passes.
- [x] Real worker verification imported 890 events; WJ reader assembled 24 forecasts/116 events at inspection time.
- [x] Improved login error messages distinguish unreachable server, rejected origin and incorrect password; rebuilt successfully.

Quire is **disconnected** in real mode and synthetic in demo. Notification delivery, bot heartbeat/job-success telemetry, external dead-man monitoring, export bootstrap and actual Android installation are not implemented/verified. Successful source reads are not proof of healthy bots.

## 1. Private phone access and persistent operation

- [x] Host and S24+ already joined the same tailnet at this session’s inspection; Tailscale 1.102.4, MagicDNS enabled, phone reachable via relay.
- [ ] Join the same private tailnet; verify access rules permit the phone to reach this host.
- [x] Persistent **Tailscale Serve** private HTTPS proxy: `https://desktop-m32cd-a-f-k20cd-k31cd.tail17d2ec.ts.net` → `http://127.0.0.1:8000`. No Funnel; raw API remains loopback-only. Trusted HTTPS, login, cookie flags, Origin/CSRF, real reads, all routes at four widths and offline-only cache passed the host browser check.
- [x] Set `.env` `PASSERINE_ORIGIN` to that exact HTTPS origin (no trailing slash) and `PASSERINE_SECURE_COOKIE=1`; restart Passerine. Keep app password authentication. The current configuration accepts one browser origin: use the HTTPS URL from both desktop and phone after this change.
- [x] Add **Passerine-only** user systemd service(s) for the API and single worker, with restart behavior and protected environment loading. Replace the foreground launcher without accidentally running a duplicate worker. Existing bot units stay untouched.
- [ ] Confirm login, CSRF mutations, all screens, offline behavior and PWA installation on the real Android device; verify Wi-Fi and cellular access with Tailscale connected.
- [ ] Verify restart/reboot behavior, host availability, backup/restore and retention. The host must remain awake and reachable for the phone app to work.

Reference: https://tailscale.com/docs/features/tailscale-serve and https://tailscale.com/docs/reference/tailscale-cli/serve . Persistent API/worker services are now installed, enabled and restart-verified; lingering and tailscaled boot enablement were already configured. Account-side Serve activation and host proxy configuration are complete; end-to-end HTTPS browser verification passed. See `docs/PRIVATE-ACCESS.md`.

## 2. Quire integration

- [ ] Obtain private read-access OAuth registration, redirect URI and selected project IDs without exposing secrets.
- [ ] Implement server-side OAuth/state/refresh-token storage and budgeted task reads using verified official payloads.
- [ ] Traverse all selected pages/children; preserve OIDs, parent context, task status, date-only due dates and HTTPS source links.
- [ ] Retain prior tasks on partial failures; test pagination, nesting, quotas/Retry-After, revocation and DST/date-only behavior.
- [ ] Group tasks as overdue/today/upcoming/unscheduled. No task write-back in v1.

## 3. Operational evidence and notifications

- [ ] Add narrow read-only heartbeat/last-success observations from actual installed schedules/watchdog evidence. Do not infer health from ledger activity or enabled timers.
- [ ] Verify ongoing MiniBench activation/policy evidence and submission uncertainty/unrecorded-post coverage; preserve intentional Cup dormancy.
- [ ] Enrich the Metaculus question view beyond `Question <id>`: retain and display the source question title, short description/question text, question type, post URL, project/tournament, group/child context, close and expected-resolution dates, latest resolution kind/outcome with observed time, forecast/submission status, unresolved uncertainty details, and the current local score with metric/version and bound resolution ID. Preserve explicit unavailable values for missing text, numeric/discrete local scoring, official scores, or incomplete history; never infer resolution from a passed date or replace a withheld/ambiguous outcome with “No.” Keep question metadata separate from append-only lifecycle/resolution/score evidence so corrections remain visible.
- [ ] Add external worker/host dead-man coverage; an API can be alive while collection is dead.
- [ ] Decide notification ownership relative to existing bot/n8n/watchdog ntfy alerts, then implement outbox delivery, bounded retries, failure visibility and deep links.
- [ ] Test actual phone/background delivery before replacing existing alerts.

## Follow-up hardening

- [ ] Manifest-validated Whiskey Jack export bootstrap/backfill and optional separately namespaced historical Cup view.
- [ ] Improve API domain typing and generated/shared frontend types; keep financial and forecasting semantics separate.
- [ ] Expand accessible text sizing/contrast and assistive-technology checks; current checks are not a complete accessibility audit.
- [ ] Validate Docker/Compose if desired. Current Compose is explicitly demo-only; verified real reads use the existing host interpreter for WJ.
- [ ] Establish proper Git version control. The supplied `.git` was a read-only placeholder; no commits were possible. Preserve unrelated WETHR documentation edits.
- [ ] Add a password-change workflow/session revocation policy; currently edit `.env` and restart. Do not paste passwords into chat.

## Launch and verification reminders

From `/home/cleblanc/projects/passerine`:

```bash
./scripts/run-local.sh
.venv/bin/pytest -q
npm --prefix frontend run build
```

The host now uses persistent services: `systemctl --user status passerine-api passerine-worker`. The foreground launcher is for development only and refuses to run while either service is active. The earlier `TypeError: NetworkError` was traced to **no server listening on port 8000**, not a bad browser URL. Password edits take effect only after restart.

See README for dependency installation, isolated demo/browser-test commands, backup commands and deployment limitations. Browser tests require a separate demo database and their documented test password; never point those tests at the normal real-data session. Agent sandbox restrictions required explicit escalated execution for local sockets, ASGI tests and source SQLite shared-memory locks.

Suggested next prompt: “Read TODO.md and the project instructions. Set up private Android access with Tailscale Serve and persistent Passerine-only services, preserving the existing bot deployments.”

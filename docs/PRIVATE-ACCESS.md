# Private Android access

Host setup on 2026-09-18 uses Tailscale and two Passerine-only user services.

The origin is **https://desktop-m32cd-a-f-k20cd-k31cd.tail17d2ec.ts.net**.
Use this address on desktop and Android. The app accepts this exact browser
origin and uses Secure, HttpOnly, SameSite Strict cookies; the existing app
password is still required. Port 8000 listens only on 127.0.0.1, and Uvicorn
ignores forwarded headers. No Tailscale identity header grants app access.

## Android

1. Connect Tailscale on the S24+ using the same tailnet as the host.
2. Open the HTTPS address above in Chrome and sign in with the app password.
3. Check Overview, Bots, both bot detail screens, Tasks and Activity; Quire is
   intentionally disconnected. Try Refresh to exercise the authenticated action.
4. Use Chrome's menu → Add to Home screen → Install (wording varies by browser).
5. With Tailscale connected, test once on Wi-Fi and again with Wi-Fi off over cellular.
6. Disconnect networking and reload: the offline screen should appear. Reconnect
   and reload to fetch current observations.

Chris confirmed private HTTPS access and PWA installation worked on the actual
Samsung S24+ (recorded in the September 19 handoff). The steps above remain useful
for repeat checks. The handoff does not separately enumerate Wi-Fi/cellular or
device offline results. Background notification delivery remains disabled and
unverified; successful installation does not establish delivery behavior.

## Services and configuration

```bash
systemctl --user status passerine-api.service passerine-worker.service
systemctl --user restart passerine-api.service passerine-worker.service
journalctl --user -u passerine-api -u passerine-worker -n 50 --no-pager
tailscale serve status
```

The units in `deploy/systemd/` are installed under
`~/.config/systemd/user/` and enabled under `default.target`. User lingering is
already enabled; `tailscaled` is already enabled at system boot. Each Passerine
process restarts after five seconds on unexpected exit, with a five-starts-per-minute
limit. To recover after repeated failures, fix the error, run
`systemctl --user reset-failed passerine-api passerine-worker`, then start them.
The worker retains its exclusive database lock; do not run a second launcher.
`scripts/run-local.sh` refuses to run while either service is active.

Units use the existing project `.venv` and native `EnvironmentFile` loading from
the mode-0600 `.env`. Keep entries as literal `KEY=value` assignments (quoted values
are allowed), without shell expansion or `export`. Restart the services after
edits. The worker removes `PASSERINE_PASSWORD` from its environment. Newly created
service files use umask 0077. Source readers retain their existing read-only access
and the source-owned interpreter; no bot unit, config, prompt or dependency is changed.

To reinstall these host-specific units from the project root:

```bash
systemd-analyze --user verify deploy/systemd/passerine-api.service deploy/systemd/passerine-worker.service
install -D -m 644 deploy/systemd/passerine-api.service ~/.config/systemd/user/passerine-api.service
install -D -m 644 deploy/systemd/passerine-worker.service ~/.config/systemd/user/passerine-worker.service
systemctl --user daemon-reload
systemctl --user enable --now passerine-api.service passerine-worker.service
```

Stop any foreground Passerine launcher first. Do not stop bot units or use broad
process-name kills. A previously running service needs an explicit restart to load changes.

## Tailscale Serve

Account-side activation and the host Serve configuration are complete. The actual
HTTPS origin passed the browser checks below; configuration contains no Funnel.
The host requires local sudo when saving Serve configuration:

```bash
sudo tailscale serve --bg http://127.0.0.1:8000
tailscale serve status
```

`--bg` persists the proxy across daemon/host restarts. Use Serve, never Funnel.
See [Tailscale's Serve reference](https://tailscale.com/docs/reference/tailscale-cli/serve).
Inspect existing routes before changing Serve settings; do not reset all routes.
The host must remain powered, awake and online. No suspend policy was changed and
no reboot was performed because existing bots are running. Host node-key expiry
at inspection was 2027-03-17; arrange reauthentication before expiry.

## Verification and recovery

The optional live browser check reads the configured password without printing it,
checks HTTPS/authentication/CSRF and real read availability, visits all screens at
four widths, and verifies the offline cache. It records one normal app refresh
request and logs out its own test session. It never invokes source jobs.

```bash
set -a
source .env
set +a
PASSERINE_CHROMIUM=/opt/google/chrome/chrome node scripts/verify-private.mjs
```

If needed, set `PASSERINE_CHROMIUM=/opt/google/chrome/chrome`. Never enable shell
tracing while loading secrets.

A pre-migration app backup is in ignored `runtime/pre-systemd-backup-20260918.sqlite3`.
It was restored to a separate verification database and passed SQLite integrity
and table-count checks. These files are local, mode 0600, and are not off-host recovery.
Keep `.env` separately in secure storage. For a new backup use a new destination:

```bash
umask 077
.venv/bin/python scripts/backup.py runtime/passerine.sqlite3 /secure/path/passerine-backup.sqlite3
```

For restore, stop only the two Passerine services, move the current app database
and its `-wal`/`-shm` sidecars together to a private recovery directory, then restore
the backup at the configured app database path with mode 0600. Never overwrite a
bot database. Restart both Passerine services and verify source/worker freshness.
Use `PASSERINE_DB` from `.env` if it differs from this default.

No automatic backup schedule or deletion policy is configured. App events/incidents
and disabled notification intents remain retained; expired sessions are pruned
on login. Off-host backups, retention policy and actual reboot recovery remain follow-ups.

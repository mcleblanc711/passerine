# Reuse assessment and sources

Research date: 2026-09-18; updated after GitHub source inspection of WETHR and Whiskey Jack. Third-party assessment is based on linked upstream READMEs, documentation, and displayed license information. No third-party candidate was built, security-audited, or tested against these integrations. These are architectural fit judgments; verify the exact revision and license before copying code.

## Recommendation

Build a small application with thin adapters, using permissively licensed scaffolding/components. Deploy a monitoring tool alongside it where useful. Among the projects inspected, none supplied WETHR, Whiskey Jack/Metaculus, and Quire as a turnkey combination.

The new repository evidence strengthens that recommendation: the most valuable domain code already exists in the user's bots. Reuse Whiskey Jack's strict readonly connector, canonical history assembly, export contract, and watchdog. Port WETHR's accounting definitions into a strict readonly projection; its convenient report commands can initialize the source database. [DISCOVERY.md](DISCOVERY.md) records exact commits and evidence. Neither bot needs to be replaced by a trading-dashboard framework.

| Project | Upstream license shown | Useful contribution | Fit judgment |
| --- | --- | --- | --- |
| [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template) | MIT | Python API, React/TypeScript UI, persistence/auth patterns, Docker and test scaffolding | Best starting code reference. Full template uses PostgreSQL and includes more account/deployment machinery than this personal app may need. Selectively reuse or trim after inspection. |
| [Homepage](https://github.com/gethomepage/homepage) | GPL-3.0 | Configurable service dashboard | Fastest low-code proof of concept. Custom API widgets can display an adapter's JSON, but richer question/task interactions still need application work. |
| [Homarr](https://github.com/homarr-labs/homarr) | Apache-2.0 | Configurable dashboard with built-in authentication and integrations | Another quick dashboard candidate. Extending a general portal may cost more than a focused app once detailed domain views are required. |
| [Uptime Kuma](https://github.com/louislam/uptime-kuma) | MIT | Uptime, HTTP/JSON/push checks and notification integrations | Optional companion outside the monitored host. First reuse Whiskey Jack's existing watchdog/external-ping capability where configured. It does not establish P&L or forecast correctness. |
| [FreqUI](https://github.com/freqtrade/frequi) | GPL-3.0 | Trading-bot interface implemented with Vue | Useful UX/reference material. It requires Freqtrade APIs; adapting both existing bots to that contract is an unattractive starting cost. |
| [Hummingbot Dashboard](https://github.com/hummingbot/dashboard) | Apache-2.0 | Bot performance views, orchestration, backtesting | Reference for domain views. Its Hummingbot deployment/control assumptions exceed the monitoring scope. |
| [Metaculus forecasting-tools](https://github.com/Metaculus/forecasting-tools) | MIT | First-party forecasting/client ecosystem and bot-template reference | Whiskey Jack already uses a pinned client. Reuse its recorded resolution evidence initially; a second forecasting framework/client is unnecessary for Perch. |

“Reference” means study behavior/design. If code is copied, record upstream identity and satisfy that code's actual license and notices. Deploying an independent tool as a companion and incorporating its source are different reuse decisions; avoid accidental wholesale copying from mixed-license repositories.

## Other useful components

- [Healthchecks](https://github.com/healthchecks/healthchecks): an option for missed jobs/dead-man monitoring. Whiskey Jack already supports an optional external healthcheck URL; verify existing configuration before adding infrastructure.
- [ntfy](https://github.com/binwiederhier/ntfy): confirmed in both source repositories. Its [publish documentation](https://docs.ntfy.sh/publish/#click-action) covers click targets; those can point into the app's event detail. Coordinate alert ownership with existing bot/n8n/watchdog messages.
- [Capacitor](https://github.com/ionic-team/capacitor): possible Android packaging path if a PWA later needs native integrations.

## Integration evidence

| Source | What was established | What remains to verify |
| --- | --- | --- |
| [Source discovery](DISCOVERY.md) | Actual bot branches/commits, schemas, accounting, resolution/scoring code, exports, schedules, ntfy/watchdog | Deployed revisions, source data/coverage, paths, installed units/overrides, live runtime state |
| [Quire API documentation](https://quire.io/dev/api/) | OAuth, tasks, webhooks, pagination/hierarchy details, plan-based quotas | Chris's app registration, plan, selected projects, actual payloads |
| [Homepage custom API widget](https://gethomepage.dev/widgets/services/customapi/) | JSON fields can be mapped into dashboard widgets | Whether this UI is enough for Chris's daily workflow |
| [Android PWA installation](https://web.dev/learn/pwa/installation) | Android installation options exist and vary by browser/device | Installation behavior for the chosen private origin on the actual phone |
| [Service-worker lifecycle](https://web.dev/learn/pwa/service-workers) | Browser controls worker activation/termination | Background push reliability in the deployed configuration |
| [Tailscale Serve](https://tailscale.com/kb/1242/tailscale-serve) | Tailnet-serving and HTTPS option | Actual network setup and identity enforcement |
| [Official AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md/) | Project instructions are discovered by Codex at run startup | Applicable instructions already present in the target workspace |

## Evidence limits

GitHub access now works for both bot repositories, superseding the original public-browsing limitation. The updated handoff is grounded in their pinned source revisions. It does not verify production state or actual data. In particular, WETHR's paper ledger is not evidence of live/fee-adjusted account P&L, and Whiskey Jack's local scoring is not official Metaculus scoring.

The earlier Metaculus API documentation page yielded no readable content. Inspection now establishes Whiskey Jack's existing resolution-client mapping and local score behavior; it does not establish a new official-score endpoint or platform scoring formula. Use the current ledger reader first, and verify any future direct API expansion against official evidence and safe read responses.

Third-party maintenance/commit history was not consistently retrievable. Do not interpret the shortlist as a dependency-health audit or claim a candidate is the best-maintained option. Inspect the selected revision, open issues, compatibility, and licensing before reuse.

## Decision rule

If the main goal is a quick display of a handful of numbers, Homepage plus a small Python adapter is the shortest experiment. For the described combination of resolutions, history, tasks, health, and eventual actions, the custom PWA is the better fit in my assessment. Both approaches require trustworthy source adapters, so keep those independent of the UI.

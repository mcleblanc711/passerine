# Product scope

## Why build it

The app serves a recurring need across two working systems: “What changed, what needs attention, and can I trust the latest results?” It also provides a natural place to connect operational incidents to existing Quire tasks.

The main cost is maintaining accurate adapters as source schemas evolve. Keep the first version small enough that the app reduces daily checking effort. Do not require a shared bot framework, a new forecast engine, or a migration of existing tasks.

## Product decisions

| Decision | Default | Reason |
| --- | --- | --- |
| Client | Installable PWA | One interface for Android and desktop; short route to a useful result |
| Audience | Chris, single user | Avoid account/team/product complexity |
| Main screen | Attention first | Incidents, changes, and next actions deserve priority |
| Source access | Read integrations in v1 | Existing automation remains operationally independent |
| Quire ownership | Quire is authoritative | Avoid maintaining two competing task lists |
| Notifications | Shared inbox, existing transport initially | Consolidate context and deep links before migrating delivery |
| Native Android | Later, if justified | APK packaging/widgets/native APIs should answer an observed need |

PWA installation behavior varies by Android browser/device; private origins should be tested on Chris's actual phone. [Google's installation guide](https://web.dev/learn/pwa/installation) documents Android installation. [Capacitor](https://github.com/ionic-team/capacitor) is a later packaging option for web-based code.

## Screens

| Screen | Content and behavior |
| --- | --- |
| Overview | Attention queue; two bot cards; most recent meaningful events; upcoming/overdue tasks; each source's freshness |
| WETHR | Gross paper P&L by epoch/history; current epoch bankroll; open paper stake; recent settlements; pipeline/job health; source freshness |
| Whiskey Jack | MiniBench run/submission status; latest resolutions/corrections; local score availability; spending/holds; optional historical Cup view |
| Tasks | Quire project filter; due today, overdue, upcoming, and unscheduled tasks; parent context and subtasks; open in Quire |
| Activity | Persistent incidents and source events; bot/project filter; read/acknowledged state; links to source evidence |

Use four bottom navigation items: Overview, Bots, Tasks, Activity. Bot details are reached through Bots or the overview cards. Health details are reachable from the affected card or incident.

## WETHR metrics

The inspected source supports **gross realized paper P&L in USD**, not a verified live or fee-adjusted account result. Start with those trustworthy metrics. Source mappings and evidence are in [INTEGRATIONS.md](INTEGRATIONS.md) and [DISCOVERY.md](DISCOVERY.md).

- **Gross realized paper P&L:** sum settled `trades.pnl`. Separate current strategy epoch, selected historical epoch, and all recorded history, including `legacy-v0` where present.
- **Bankroll:** show current epoch starting bankroll plus current epoch realized P&L. The existing unfiltered report mixes all-history P&L with current-epoch bankroll; label the scopes explicitly.
- **Open paper stake/count:** recorded unsettled `size_usd` and position count, labeled as paper stake. Do not relabel this as an audited live exposure measure.
- **History coverage:** use “Recorded history” until completeness is verified. Use “Lifetime” only after establishing complete relevant history; a recent-settlement export is insufficient.
- **Unavailable in the initial verified source:** live account P&L, fees/net P&L, and reliable unrealized P&L. Show an unavailable explanation or omit these tiles. Optional live execution does not change the paper ledger's meaning.
- **Diagnostics:** signal Brier statistics span epochs in the current implementation. Do not imply that the trade epoch filter scopes them. If showing P&L divided by settled stake, label it “Return on settled stake.”

Later financial adapters may add verified live fills, fees, and marks with currency, account, mode, timestamp, and coverage. Keep operating costs separate from trading fees. Never combine paper/live results, silently convert currencies, add cumulative snapshots, or turn missing amounts into zero.

## Whiskey Jack metrics

- Last successful run, next expected run when known, and failures requiring attention.
- Forecast generation and accepted submission are separate events. A generated forecast is not proof Metaculus received it.
- Question closing time, expected resolution time, actual resolution, and score availability are separate fields.
- Track actual outcomes and subsequent corrections using source evidence. Support ambiguous/annulled/other native states without forcing them into yes/no.
- Display the existing **local** binary/multiclass Brier/log scores with metric name, implementation version, record, and linked resolution. Numeric/discrete local scores are out of scope. Official platform-score ingestion is not implemented in the inspected source; label that capability unavailable.
- Preserve `resolved`, `annulled`, `ambiguous`, `withheld`, and `unresolved` observations. Use the latest resolution event for current outcome state and only a matching eligible score. Old scores remain history after a correction or withdrawal of outcome evidence.
- Separate confirmed forecast, comment completion, unresolved submission uncertainty, and unrecorded posts. A healthy process can still need reconciliation. Surface spending holds; keep settled actual spend and unsettled reserved estimates separate.
- MiniBench is the primary profile. Cup is documented as withdrawn/dormant and should be optional historical context, without down alerts for intentionally disabled operation. Check runtime state before changing that classification.

Document local scoring eligibility and methodology from the implementation; do not average unlike score types into an apparent tournament score. If official scores are added later, preserve their platform name, tournament/cohort, question type, and retrieval time separately.

## Health that means something

Show separate evidence for process heartbeat, successful scheduled work, input data freshness, submission/settlement reconciliation, and monitor sync. Ledger activity alone is not process health; no new trades need not mean a stopped bot.

Configure cadence per job from actual installed settings. Checked-in defaults include WETHR's ten-minute collector, daily settlements/audit, and Whiskey Jack's five-minute tournament poll plus six-hour resolution ingestion. A tournament run can remain active for much longer than five minutes. Display when the source last checked resolutions; refreshing Perch does not trigger upstream ingestion or scoring.

Use explicit healthy/degraded/failed/unknown states and visible reasons. Source reachability can be good while the last successful job is stale. Missing instrumentation stays unknown. Acknowledging an incident does not mark the underlying condition healthy.

## Next phase

Add direct web push, Quire task creation/completion, and selected existing bot commands only after the read model is trustworthy. Quire writes should show confirmed remote state and handle conflicts. Bot commands should call established allowlisted interfaces, retain existing approval boundaries, and return durable receipts. Do not add an arbitrary shell/chat-to-command endpoint.

Candidate actions: “Open failed run,” “Create Quire task from incident,” “Refresh status,” and eventually an already-supported safe diagnostic request. Preserve Telegram while any important two-way workflow has not been migrated.

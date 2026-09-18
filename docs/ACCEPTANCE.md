# Build order and acceptance

Use these as meaningful behavior checks. Implement checks appropriate to the code that actually exists; do not create a large test framework before the first slice.

## Milestone 0 — discovery

Start from the pinned source investigation in `docs/DISCOVERY.md`. Verify available/deployed revisions, schema compatibility, configured paths, installed job schedules/timezone, and missing access. Update differences rather than repeat the entire investigation. Select the stack and record significant departures. Do not execute either bot or migrate its data while inspecting it.

Completion: an adapter plan grounded in current code, or clearly identified missing inputs plus a fixture plan. Discovery should lead directly into implementation.

## Milestone 1 — runnable mobile demo

Build the API, one worker, app database, UI routes, demo fixtures, manifest, and offline shell. Provide exact local commands and a Compose configuration. Synthetic data is visibly labeled throughout; its timestamps should be controlled so scenarios remain reproducible.

Verify phone widths around 360–430 CSS pixels and a desktop layout. Cards, navigation, task links, freshness labels, and attention items are usable without horizontal page scrolling. Health uses text and icons, not color alone. Verify what can be tested locally and list actual-device installation as pending if the phone is unavailable.

Completion: Chris can open a running app and see the intended daily workflow, including stale/disconnected states.

## Milestone 2 — real source reads

Connect both bots and Quire where access permits. Test each adapter independently. Match WETHR gross paper totals and epoch bankroll to the inspected accounting definitions over known source data. Match Whiskey Jack canonical history, latest resolutions, and local scores to their supporting rows. Match Quire task counts/nesting to a complete selected scope.

Verify source isolation using synthetic/sanitized ledgers: reads cannot create a missing store, migrate schemas, or change source database/WAL content. A compatible WAL reader must see committed rows still in the WAL. Allow ordinary SQLite reader locking/shared-memory behavior; do not use raw file-metadata checks as a substitute for verifying unchanged source content. Do not run mutating source commands to create test evidence.

If access blocks one adapter, the others still operate. Clearly distinguish connected, not configured, unauthorized, failed, and demo. A missing integration does not block useful implementation, but the full real-data milestone is not complete until all selected sources are verified.

## Milestone 3 — daily use and alerts

Add persistent incidents, acknowledgements, an outbox, deep-linked push, Perch-worker watchdog coverage, backup/restore instructions, and private deployment instructions. Reuse existing Whiskey Jack watchdog/external-ping coverage where configured. Test a stopped Perch worker and an unavailable source using local fixtures/services. Test push/background behavior on the actual Android device before relying on it. Prepare deployment without altering running bot services.

Completion: the app detects meaningful failures, survives restarts, and does not produce repeated alerts for an unchanged condition. Existing notifications remain until replacement delivery is proven.

## Risk-focused checks

| Scenario | Required result |
| --- | --- |
| Same cumulative P&L snapshot read three times | Total stays unchanged |
| WETHR gross paper P&L 42.50, no fee evidence | Show gross paper 42.50; net/live/unrealized unavailable |
| Future fee-aware adapter: gross 42.50 minus fees 2.50, or already-net 40.00 | Net 40.00 under either explicitly supported convention; no double deduction |
| Paper and live accounts, or different currencies | Separate totals and labels |
| WETHR optional live execution enabled | Existing `trades` records remain labeled paper |
| WETHR epoch A P&L 10; current B starts 100 and earns 5 | All-history P&L 15; current B bankroll 105, not 115 |
| WETHR trade settles after its creation ID was imported | Settlement/P&L update is captured once |
| WETHR recent-settlement export used | No all-history/lifetime claim; no invented open positions |
| WETHR epoch filter changes | Global signal Brier statistic is not relabeled epoch-specific |
| Missing history or finance data | Partial coverage/unavailable, never an invented lifetime or zero |
| Recent collector poll, old source payload | Old freshness remains visible |
| Fresh heartbeat, missed successful run | Job health degrades independently |
| Question close/expected-resolution time passes | It does not automatically become resolved |
| Resolved binary question, local score absent | Outcome shown; local score pending; official score unavailable |
| Numeric/discrete question has no local score | Out-of-scope local capability, not a failed score job |
| Local Brier/log result present | Labeled local with metric/version, never official tournament score |
| Resolution correction/replay | Correction retained; replay does not duplicate the event |
| New withheld/annulled/unresolved event after a scored resolution | Current outcome follows newest event; old score retained only as history |
| Resolution or score added without lifecycle transition | Canonical history/import still captures it |
| Whiskey Jack export lacks manifest or has hash/count mismatch | Reject incomplete/corrupt snapshot; retain prior observations |
| Source schema differs from supported/deployed reader | Explicit compatibility error; no source migration |
| MiniBench and Cup share a record ID | Separate entities/history by source profile and ledger |
| Cup is intentionally dormant | Historical view available; no false downtime alert |
| Whiskey Jack resolution job last succeeded two hours ago under six-hour cadence | Expected source age shown; one-minute Perch poll does not imply a new platform check |
| Tournament job remains in progress beyond five minutes | Apply verified runtime/in-progress rules, not poll interval alone |
| Resolution timer enabled but last success unavailable | Job freshness unknown; do not infer successful ingestion |
| Settled reservation was previously counted as estimated cost | Actual and still-held costs do not double count it |
| Restart midway through collection | Durable work survives; cursor does not skip unfinished records |
| One adapter times out | Other sources continue; old data is labeled stale |
| Quire task is nested or on another page | Included in the selected scope |
| Quire page fails | Last known tasks retained; sync marked partial |
| Date-only task near midnight/DST change | Calendar due date preserved in America/Edmonton |
| API quota exhausted | Backoff/cooldown respected by automatic and manual refresh |
| Unauthorized request, spoofed proxy header | No private data or mutation access |
| Malicious task text or link | Safely rendered; unsupported URL schemes rejected |
| Notification provider times out | Intent retained and retry visible; delivery not claimed successful |
| Worker dies while HTTP server stays up | Independent worker health detects the problem |
| PWA goes offline | Clear offline state; no private API data in persistent service-worker cache |

## Deferred deliberately

Task creation/completion, direct web push, selected existing bot commands, native Android packaging/widgets, richer performance attribution, and additional bots. Move an item forward when it solves a demonstrated daily-use gap.

## Handoff from the implementing agent

Report exact run/test commands, what is real versus demo, evidence for completed checks, configuration still needed, and the next three priorities. Include screenshots if UI inspection is available. Do not call the app production-ready based solely on passing unit tests or a successful container startup.

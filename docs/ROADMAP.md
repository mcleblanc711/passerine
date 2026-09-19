# Post-phone-validation roadmap

As of September 19, 2026, private HTTPS access and PWA installation worked on Chris's
actual Samsung S24+. The app has real read-only WETHR and Whiskey Jack adapters,
cached observations, isolated polling/backoff, authenticated refresh and incident
acknowledgement. This establishes a useful private monitoring app, not complete
operational coverage. See [verification](VERIFICATION.md) for dated evidence.

The next slices are ordered below. Each should remain independently reviewable;
available authorized inputs can change the order.

## 1. One authoritative successful-job observation

Start by inspecting the existing Whiskey Jack resolution-job completion interface
and installed schedule read-only. Its recorded six-hour cadence gives a concrete
question: when did resolution ingestion last succeed? An enabled timer, recent
ledger event or fresh Passerine read cannot answer it. No verified completion
interface is currently available to the adapter.

Establish the producer's actual success/failure semantics, profile identity, UTC
timestamp and publication behavior before implementing a consumer. If the source
does not persist this evidence, prepare a separate reviewable source patch; do not
modify its deployment, config, prompt or dependencies. Fixtures must be labeled as
proposed contract examples until the producer is verified.

Complete the Passerine slice when one verified job observation reaches the existing
API and bot evidence view, independently of source contact and process heartbeat.
Test absent evidence, stale success despite fresh contact, malformed or out-of-order
observations, failure after success, and the configured cadence. Keep uninstrumented
jobs unknown and Cup dormancy intact. Broad host metrics, all-job instrumentation
and an external worker dead-man service are separate follow-ups.

## 2. One selected Quire project, read-only

Required inputs are a private read-access OAuth registration, approved callback,
selected project identifier, current plan/shared quota policy, and authorized
sanitized payloads showing pagination, children, status and due-date precision.
Verify current official API documentation when implementing; the historical quota
figures in integration notes are not a current budget guarantee. Keep credentials
and refresh tokens server-side.

Complete this slice when authenticated connection and token refresh allow one
selected project's full hierarchy to appear in Tasks. Persist quota/cooldown state
across restarts and share it with manual refresh. Tests must cover OAuth state and
revocation, nested pages, date-only due dates, quota exhaustion, and a failed page
that retains last-known tasks and visibly marks the sync partial. Do not infer
removal from an incomplete traversal. Quire remains authoritative; task writes and
additional project scopes are separate work.

## 3. Passerine-owned notification delivery

First define which conditions Passerine owns and verify the existing transport's
endpoint/authentication arrangement without exposing secrets. Existing bot, n8n
and watchdog notifications keep their ownership. Start with one Passerine source
collection failure condition; intentional Quire disconnection should not generate
repeated delivery. Worker/host disappearance requires detection outside the failed
worker and is a separate slice.

Complete the delivery slice when an incident creates a durable owned intent and
the worker records bounded attempts, next retry, provider acceptance or failure.
Test timeout ambiguity, restart recovery, unchanged-condition deduplication,
acknowledgement versus recovery and suppression. Explicitly decide whether historical
disabled intents expire or stay disabled before enabling delivery; do not bulk-send
the existing backlog. Provider acceptance is distinct from receipt on a device.

Use fixtures/fake transport for ordinary tests. A separately authorized live delivery
check must confirm background receipt and the private deep link on the S24+ before
relying on notifications. PWA installation has already been validated.

## Remaining limits

Compose execution, whole-host reboot recovery, off-host backup/retention and external
dead-man coverage remain unverified or unconfigured. They do not block the small
slices above. WETHR live/net/fee/unrealized accounting stays out of scope; recorded
gross paper USD totals do not certify lifetime coverage. Official platform scores,
historical Cup integration and export bootstrap remain separate capabilities.

Use [acceptance](ACCEPTANCE.md) for risk-focused checks and update README, discovery
and verification when implementation status changes. No rebuild or redeployment
is part of this documentation slice.

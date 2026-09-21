# Resume after the question-display milestone

Checkpoint: September 21, 2026. The user requested a solid stopping point before
clearing context. The implementation is complete for stored question text and bot
forecasts; the requested community comparison is still blocked on a verified data
interface. Do not describe that comparison as complete.

## Where the work lives

- Main/deployed checkout: `/home/cleblanc/projects/passerine`, `master` at `7b91955`.
  It includes the deployed MiniBench recorded tournament heartbeat.
- New work: branch `feat/minibench-questions`, worktree
  `/tmp/passerine-questions.6iLfRS`, pushed to the same GitHub origin at handoff.
  Check out the remote branch in a fresh isolated worktree if `/tmp` was cleared.
- Read `AGENTS.md` and the project docs before continuing. The live worker launches
  `scripts/read_whiskeyjack.py` on every poll; editing it in the deployed checkout
  changes live reads without a restart. Keep new work isolated until rollout.

## Completed here

The reader uses Whiskey Jack's source-owned `read_forecast_record` validator and
projects selected fields via `backend/app/adapters/whiskeyjack_questions.py`.
`frontend/src/ForecastComparison.tsx` displays bot percentages for binary and
multiple-choice questions, and stored percentile values/units for numeric and
discrete questions. Cards include titles/group context, expandable source text,
forecast version, generation and as-of timestamps. Existing resolution/score logic
is preserved. Community evidence is explicitly unavailable. Demo data is labelled.

Verification: 25 backend tests, TypeScript no-emit check, real read-only projection
of 24 records and synthetic browser checks at four widths passed. See
`docs/VERIFICATION.md` for commands and dates. No source configuration, bot services,
forecast submissions or production assets were changed by this feature.

## Next decision and boundaries

Deployment preparation continued September 21 without changing live services.
See [DEPLOYMENT.md](DEPLOYMENT.md) for the concrete preflight, backup, rollout,
acceptance and rollback procedure. The production build now passes in the isolated
worktree; all 25 backend tests pass again. Preparation is not rollout authorization.
Main is still `7b91955`; Whiskey Jack advanced to `9834e36` with no `src/` changes
since the inspected source pin. See discovery and verification for current evidence.

Either deploy this useful display slice when requested, or first investigate a
separate read-only community-data interface. The stored forecast model deliberately
has null community snapshots. Inspected resolution aggregates and the saved SDK
community field also had no values. Do not synthesize community probabilities or
claim the source values are current. Establish platform visibility, authentication,
aggregation semantics, question/post identity, timestamps and shared quotas before
adding a fetcher; keep credentials server-side and bot inputs untouched.

If deploying, back up the app DB with SQLite backup, stop only Passerine API/worker,
merge the reviewed feature, build, start those services and verify private HTTPS.
Do not alter bot services. The prior rollout was specifically approved; this new
question-display feature has not been deployed or requested for rollout yet.

Android S24+ private HTTPS and installation are already confirmed. Desktop login
uses the same configured tailnet HTTPS origin, not localhost. Job-success evidence
and WETHR heartbeat remain unknown, Quire disconnected, notifications disabled and
Compose unverified. WETHR live/net/fees/unrealized accounting remains out of scope.

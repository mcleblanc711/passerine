# Source provenance

The scaffold and UI were authored for Passerine. No FastAPI template was copied.

- WETHR `05813605497b4ec5f1091c78a8af23055f64ef81`: accounting semantics adapted from `collector/src/paper_trader.py:get_stats`; SQL projection independently implemented. MIT notice retained in `licenses/WETHR-MIT.txt`.
- Whiskey Jack `04f294e53ac8903ae9f55ed7a556ecb65115476f`: runtime reuse of `ledger.connect_readonly` and `show.assemble_show`; reservation/settlement arithmetic adapted from `tournament_state.spending` to avoid importing notification/runtime code. MIT notice retained in `licenses/WhiskeyJack-MIT.txt`. No source code package is vendored or installed into its environment.
- React, Vite, TypeScript, Lucide and Playwright are package-managed dependencies. Dependency lockfiles record resolved versions. Lucide supplies UI icons; the PWA bird icon is an original SVG.

The recorded tournament heartbeat projection and synthetic fixtures were independently
implemented against Whiskey Jack `9e9fcfe51064620fa3d17b98d2321ec1f51095ff`:
migration 012, `tournament.run_once`, `tournament.status`, and `deploy/wj-watchdog`.
They reuse source semantics, without importing notification or execution modules.

No raw production database, forecast payload, credential, or screenshot of production data belongs in version control.

# Phase 2 report: CI hardening (2026-10-26)

All five repos merged. Each repo's evidence is in its `docs/audit/phase-2.md`.

| Repo | PR | What CI checks now | Required checks (for owner decision D1) |
|---|---|---|---|
| movera-contracts | #9 | openapi.yaml equals the generator's output; CONTRACT.md title names the version; pinned PyYAML | `verify` |
| movera-server | #17 | ESLint, `npm audit` (high), tests with coverage floors (rules, trips, dispatch, auth), gitleaks, timeouts | `checks`, `secret-scan` |
| Movera-driver-app | #386 | pinned Flutter, `dart format`, coverage floor 91.5 % lib/core, gitleaks, live web build on every PR, timeouts | `Analyze, test and build web`, `Secret scan`, `Build live web (MOVERA_AUTH_REQUIRED=true)`, `Android release signing and preview`, `iOS release compile preflight` |
| movera-rider-app | #422 | one gate (lockfile, format, analyze, tests once, coverage floor 92.8 %, integration, web builds, gitleaks); 7 duplicate workflows removed | `CI gate / gate` |
| Admin-panel-movera-dispatch | #146 | typecheck, lint cap, unit, build, npm audit, gitleaks, Playwright e2e + live; Pages deploys only after checks pass | the 5 jobs of "Webapp checks" |

## Fixed in Phase 2
- Flaky tests made deterministic: server (5, incl. hook timeouts and fixed sleeps), driver (2 wall-clock tests).
- Security advisories: zod 4 (server, admin), maplibre-gl 6 (admin), vitest 5 (server). `npm audit`: 0 in server and admin.
- Admin app bugs found by the e2e failures: the surge pulse repainted the map ~12×/s even when hidden (main thread blocked, clicks timed out); maps waited on the external tile server before drawing zones and pins. All 245 e2e pass.
- Contract copies synced: rider 0.5.0→0.5.5, driver 0.5.3→0.5.5, admin to 0.5.6 (via the other session's #145). The apps' own copies of the trip transitions gained `raise_price`.
- Code formatted in rider and driver (format-only commits).

## Open, moved to later phases
- Rider `qa-*` workflows that test the published live site fail on main (critical-rider-flow since #411; book-now script outdated). Needs the live site and the Maps key → Phase 3/5.
- Driver app: no handling of a re-offer after the rider raises the price; no `rider_raise` fare line → Phase 3.
- Admin: does not show raise-price or on-the-way; its dispatch still offers a `raise_price` waiting step the contract says is skipped → Phase 3/5.
- Admin: 39 `react-hooks/exhaustive-deps` warnings capped, not fixed; fixed sleeps in drawing e2e specs.
- Server: helper dedup reverted (would lower coverage floors).
- Branch protection: owner decision D1 (the check names are above).

## Other account's PRs (same day)
Merged when green after updating with main: contracts #7, server #14, #15, driver #381, #382, #383, rider #415, #416, #418, admin #145. Not merged (red): rider #414, #417, #419, #420. Driver #385 updated with main, waiting for CI.

## Next: Phase 3 (ride lifecycle and the three apps together), started at once.

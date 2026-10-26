# Phase 1 report: baseline audit (2026-10-26)

Each repo's full baseline is in `docs/audit/baseline-2026-10.md` on its branch `audit/phase-1`. No code was changed in this phase.

| Repo | Branch commit | Checks | Tests | Line coverage |
|---|---|---|---|---|
| movera-contracts | 4c9e752 | all pass | 24 scenarios | 20 of 21 transition commands |
| movera-server | 0cdf397 | typecheck, build pass | 568; flaky under load (fails 2 of 3 runs on timeouts) | 94 % |
| Movera-driver-app | 5150eb2f | analyze clean; format: 451 files differ | 2178 pass, 2 timing-flaky | 89 % |
| movera-rider-app | 253db3ec | analyze clean; format: 519 files differ | 2958 pass; the 3 real-server tests always skipped | 91 % |
| Admin-panel-movera-dispatch | f40cc68 | typecheck, build pass; 39 lint warnings | 257 unit; e2e 239/245 (2 fail, 4 flaky) | 98 % of tested files; pages not measured |

Since the audit started, the owner merged driver PR #380 and rider PR #413 (today's live-test fixes).

## Findings ranked

### S1 (must fix before testers)
1. **Admin live panel cannot manage trips or refunds.** Only people, fleets, vehicles and documents are live; ~29 menu pages still show demo data in the live build, unmarked. Pricing and zone edits stay in the browser.
2. **No test runs a real ride across the apps and the server.** The rider's 3 real-server tests are always skipped; the apps' tests use mocks with older request formats.
3. **iPhone crash/reload (N3) not verified on a device** after the map changes.

### S2
4. Driver live build shows demo scheduled rides and reminders.
5. Driver ride-check safety alerts go to a demo store, never to the server.
6. Driver earnings and history are local only and always shown in kr (wrong for Paris; empty on a new phone).
7. Apps compute money themselves as a fallback (driver pay at 25 %, rider cancel/waiting fees, raise sum, wallet in floating point).
8. Contract copies out of date: rider 0.5.0, driver and admin 0.5.3, server 0.5.5.
9. Admin password setup link is written to the server log.
10. Google Maps keys in the git history of both apps.
11. Security advisories: zod (high, server and admin), maplibre-gl (critical, admin), vitest/tinypool (dev).
12. Rider QA workflows that test the published live build all fail on main.
13. Raise price (N4): reachable now, but why the server refused it live is still unknown.
14. Admin e2e: 2 reproducible failures, 4 flaky map tests.

### S3 and S4
- CI gaps in every repo: format, coverage, security audit, secret scan, timeouts, required checks; rider runs its full suite 5 times per PR.
- Server: raise cap skipped when the quote is 0; reported cash unbounded; approvals list not zone-filtered.
- Driver ride check triggers at 3 km, owner's scenario is 300 m.
- Large widget files with logic; duplicated map code between the two Flutter apps.

## Not verified in Phase 1
iPhone and native behaviour, the live Render server, branch protection settings, GitHub Actions logs (blocked by the proxy), Dart security advisories (no tool), Maps key restrictions.

## Next: Phase 2 (CI hardening), started at once per the owner's standing instruction.

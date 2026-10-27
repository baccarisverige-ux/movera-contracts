# Audit progress log

Read `HANDOFF.md` (project, rules, open work) and `AUDIT_PLAN.md` (phases) first. This file says where the audit stands, so a new session can continue after a pause. Update it at the end of every step.

## Owner's standing instruction (2026-10-26)

"When you finish a phase, start the next one. Do not wait for my permission. Write the report, always save the work, never stop until all phases are done."

So: after each phase, write its report into this folder (`phase-N-report.md`), push, update this file, and start the next phase at once. **Merge permission (owner, 2026-10-26, "U can merge safely"):** PRs are merged by the audit as soon as every CI check is green and the PR is reviewed against the plan's rules. A red or pending PR is never merged.

## Status

| Phase | State | Where the results are |
|---|---|---|
| 0 Finish in-flight work | **done**: driver #380 and rider #413 merged by the owner | Driver draft PR #380 (branch `driver-live-fixes-1`); rider branch `rider-live-fixes-1` (N4 is WIP, gates not run; N10 done) |
| 1 Baseline audit | **done** — `phase-1-report.md` | `docs/audit/baseline-2026-10.md` on branch `audit/phase-1` in each repo |
| 2 CI hardening | **done** — `phase-2-report.md` | contracts #9, server #17, driver #386, rider #422, admin #146 |
| 3 Ride lifecycle and sync | **done** — `phase-3-report.md` | server #18, #19, driver #387, rider #423 |
| 4 Security and data integrity | **done** — `phase-4-report.md` | server #22, rider #424, admin #147 (merged); report `movera-server/docs/audit/phase-4.md` |
| 5 Every screen | **done** — `phase-5-report.md` | driver #388, admin #151, rider #425 |
| 6 Maps and GPS | **done** — `phase-6-report.md` | rider #426, driver #389 |
| 7 Performance | **done** | server #23, rider #427, driver #390, admin #152; each repo's `docs/audit/phase-7.md` |
| 8 Final report | **done** — `FINAL_REPORT.md` | movera-contracts branch `audit/final-report` |

## Phase 1 per repo

| Repo | Branch | State |
|---|---|---|
| movera-contracts | audit/phase-1 | **done** (docs/audit/baseline-2026-10.md) |
| movera-server | audit/phase-1 | **done** (0cdf397; 568 tests, 94 % line coverage; top: admin setup link in logs, no e2e harness, zod advisory, flaky hooks) |
| movera-rider-app | audit/phase-1 | **done** (253db3ec; 2958 tests, 91 % coverage). Rider PR #413 merged 2026-10-26 |
| Movera-driver-app | audit/phase-1 | **done** (5150eb2f; 2178 tests, 89 % coverage; S2: demo scheduled rides in live build, ride-check alerts go to demo repo, earnings local-only and always SEK, Maps key in git history). PR #380 was merged 2026-10-26 11:47 UTC |
| Admin-panel-movera-dispatch | audit/phase-1 | **done** (f40cc68; 257 unit + 239/245 e2e; S1: live panel has no trips or refunds pages; only people area is live) |

## How to continue after a pause

1. Read this file, then open each repo's `audit/phase-1` branch and its `docs/audit/baseline-2026-10.md`. Each has a "Done / Not done yet" list at the top.
2. Continue the first repo whose state is not "done". Commit and push after every finished section.
3. When all five are done, open one docs-only PR per repo and ask the owner for "merge".

## Owner decisions (2026-10-27)
- No-show fee: **65 kr** (server value); app sample configs to be aligned. Admin can already change it per zone via the server's config API; live admin Pricing page and per-trip "waive fee" button to be added (owner: yes).
- Zone-limited admins see/block **only riders who rode in their zones** (P4-6).
- D2: owner will add a **restricted Google Maps test key** as a GitHub secret.
- Driver app routes go **through the server** (`/routes/driving`) instead of the public OSRM demo; needs `OSRM_URL` on Render.
- D1: **branch protection with required checks** on main in all 5 repos (owner sets it; steps to be sent).
- D4: **no raise after expiry**; offer "Search again" instead.

## Owner rule (2026-10-27, always)
Before building or changing anything: first check the owner's existing demo screens (e.g. the admin demo Pricing section), then all apps (rider, driver, admin), the contract and the server. Never build from our own ideas; reproduce what the owner built and list every mismatch for the owner before coding.

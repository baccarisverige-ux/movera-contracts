# Movera: complete testing, bug fixing and quality audit plan

Date: 2026-10-26. Scope: Rider app, Driver app, Admin panel, and the server and contract they share.
Read together with `MOVERA_HANDOFF.md` (repos, links, test accounts, the owner's rules, open work).

## How this plan works

- **Order of priority:** crashes and the ride lifecycle first, then sync and security, then every screen, then performance. Each phase delivers value even if the work stops in the middle.
- **One phase = one or more small PRs per repo.** Each PR lists, per problem: steps to reproduce, root cause, severity, fix, regression test, evidence. CI must be green. The owner writes "merge".
- **Evidence or nothing.** Every fix gets a test that fails before and passes after. Nothing is reported as passing unless it ran. Untested areas are listed as untested.
- **No new architecture** to make a test pass. Smallest safe fix that respects the contract.
- **Never:** skip or weaken a test, suppress a warning, force-push a shared branch, put a secret in code, logs or workflows.

### Severity scale
| Level | Meaning |
|---|---|
| S1 Critical | Crash, data corruption, wrong money, a user acting on someone else's ride, a ride stuck or reopened |
| S2 High | A flow cannot be finished, wrong state shown, sync broken between apps |
| S3 Medium | Wrong text or number with a workaround, slow screen, missing error state |
| S4 Low | Cosmetic, code cleanliness |

### What can and cannot be verified from the cloud machine
| Can run in the cloud | Needs the owner, a real phone or a device service |
|---|---|
| Analyze, unit and widget tests, builds, Playwright for the admin panel and the web builds in Chromium, the server's full test suite with Postgres, multi-app ride simulations against a local server | iPhone Safari crashes and memory limits, native iOS/Android behaviour, real GPS while driving, battery, real-device frame timing, Google Maps rendering (needs a Maps key in CI), real SMS, Apple and Google sign-in |

Items in the right column are reported as "needs device" with a precise test script for the owner or a device-farm service (e.g. Firebase Test Lab, BrowserStack). Owner decision D3 below.

---

## Phase 0. Finish what is in flight (4–6 h)

Before any new work, close today's open items so nothing is half done.

| Item | Repo | Status |
|---|---|---|
| Fix the one red test, take screenshots, make CI green | Driver, draft PR #380 | N1, N5, N9, N11 done; N6 partly |
| Push and open the PR; finish N3, N4, N8, N10, rest of N6 | Rider, branch `rider-live-fixes-1` | N5, N6, N7, N9 done |
| Send the rider's first name to the driver (waybill) | Server + contract | Found by the driver audit |
| Owner adds `OSRM_URL` on Render | Render | Straight-line routes until then |

**Done when:** both PRs green and merged by the owner.

---

## Phase 1. Baseline audit (3–5 h, no code changes)

For each of the 5 repos:
1. Structure, dependencies, architecture notes (state management, API layer, navigation).
2. CI workflows: what runs, what does not, what is slow.
3. Run every existing check and record the result as the **baseline** (pass, fail, flaky, time taken).
4. Test coverage of critical logic: fare, transitions, dispatch, money, auth.
5. Open issues and PRs, stale branches, dead code, unused dependencies, duplicated logic between the two Flutter apps.
6. List of untested features.

**Deliverable:** `docs/audit/baseline-2026-10.md` in each repo (one PR per repo, docs only).

---

## Phase 2. CI hardening (3–4 h)

Per repo, only what fits its stack:

| Check | Server (Node) | Rider / Driver (Flutter) | Admin (React) | Contracts |
|---|---|---|---|---|
| Lockfile install | `npm ci` | `pub get --enforce-lockfile` | `npm ci` | — |
| Format | Prettier check (if adopted) | `dart format --set-exit-if-changed` | Prettier/ESLint | — |
| Static analysis | `tsc --noEmit`, ESLint | `flutter analyze --fatal-infos` | `tsc`, ESLint | `verify.sh` |
| Unit tests | Vitest + Postgres service | `flutter test` | node tests | `reference_check.py` |
| Coverage report | fare, transitions, dispatch, auth | core/ logic | domain logic | — |
| Build | `npm run build` | web, APK, iOS no-codesign | `vite build` | — |
| End-to-end | server API scenarios | web probes (exist) | Playwright (exists) | — |
| Security | `npm audit`, secret scan | `dart pub outdated`/advisories, secret scan | `npm audit`, secret scan | — |
| Caching and timeouts | yes | yes | yes | yes |

- **Formatting is applied in one separate PR per repo** with no other changes, so reviews stay readable.
- **Branch protection:** require these checks on `main` (owner decision D1).

**Done when:** every repo's `main` has the checks green and required.

---

## Phase 3. Ride lifecycle and the three apps together (6–10 h) — top priority

A **simulation harness** in `movera-server/test/e2e/`: drives a real local server with several riders, drivers and an admin at once, through the HTTP API and the live event stream, exactly as the apps do. It runs in CI.

Scenarios (each one a test):
1. Sign-up and sign-in (rider, driver, admin); expired session; refresh token reuse.
2. Quote, category, pickup and destination validation, route with and without the route service.
3. Request → offer → accept → arrive → start → complete; final fare and earnings.
4. Rider cancels at each stage; driver cancels; no-show; fees.
5. Driver declines, offer times out, reassignment; no drivers; search expires after 10 min.
6. Raise price while searching; after expiry (N4).
7. End early by rider; complete far from drop-off by driver; minimum fare (N9).
8. Duplicate requests (same Idempotency-Key), two drivers accepting at once, delayed and out-of-order events, stream reconnect, app restart mid-trip.
9. Admin actions: manual booking, reassign, cancel, refund, block a driver mid-trip.
10. Authorization: a rider or driver touching another user's trip; a driver outside their fleet.
11. Invalid transitions: completed or cancelled trips never become active again.

Then **the apps against the harness**: the Rider and Driver web builds in Chromium (and the admin with Playwright) running one ride together, checking that all three show the same trip id, status, driver, car and money at each step.

**Done when:** all scenarios pass in CI; every defect found has a fix and a regression test.

---

## Phase 4. Security and data integrity (3–5 h)

- Role checks on every server route (rider, driver, fleet owner, admin roles and zones), by an automated route-by-route test.
- Server-side validation of fares, transitions, document access, fleet links.
- Idempotency on every money and state change.
- Secret scan of all repos and their history; logs checked for phone numbers, tokens, documents.
- Dependency vulnerabilities, with upgrades where safe.
- Rate limits: sign-in, join codes, uploads.

**Deliverable:** findings table with severity; S1/S2 fixed with tests.

---

## Phase 5. Every screen and every button (10–15 h)

For each app, an inventory of screens and controls, then automated widget tests (Flutter) and Playwright (admin) for:
- each control does its action; repeated taps do not repeat the action;
- loading, empty and error states; network failure and timeout;
- Back works and never crashes (N3); reopening the app restores the right screen;
- forms validate and show useful errors;
- small screens, large text, keyboard open, three languages.

**Deliverable:** per app, a screen list with each screen's test status (tested / needs device / not applicable).

---

## Phase 6. Maps, GPS, search, routing (4–6 h)

- Address search: no lost first keystrokes, debounce, outdated requests cancelled, correct location selected.
- Markers, route, pickup and destination stay in sync; camera never tilts or over-zooms (N6).
- GPS updates: count rebuilds and network calls per minute, set a budget.
- Permission denied, GPS unavailable, stale driver positions, map load failure.
- Needs a **Google Maps key for CI** (owner decision D2) to test real map rendering.

---

## Phase 7. Performance, measured (5–8 h)

Measure first, in release/profile builds:
- Start time; time to first interactive screen.
- Frame timings on booking and trip screens; rebuild counts.
- Memory over 10 bookings in a row on the web build (the iPhone reload issue).
- API calls per minute per screen; server response times and slow queries.

Set budgets from the baseline (for example: no frame over 32 ms while dragging a sheet; memory flat over 10 bookings). Add the checks that can run in CI. Device-level CPU, battery and real frame rates go to the owner's device test list.

---

## Phase 8. Final report (2–3 h)

The 13-point report requested by the owner: findings with severity per app, architecture weaknesses, lifecycle defects, measured performance, security findings, tests added, workflows changed, every fix with root cause and evidence, builds and coverage, remaining problems and untested areas, commit hashes and PR links, prioritized remaining work.

---

## Time and order

| Phase | Work time | Can start |
|---|---|---|
| 0 Finish in-flight work | 4–6 h | now |
| 1 Baseline audit | 3–5 h | now |
| 2 CI hardening | 3–4 h | after 1 |
| 3 Ride lifecycle and sync | 6–10 h | after 1 |
| 4 Security | 3–5 h | after 3 |
| 5 Every screen | 10–15 h | after 2 |
| 6 Maps and GPS | 4–6 h | after 5 |
| 7 Performance | 5–8 h | after 6 |
| 8 Final report | 2–3 h | last |
| **Total** | **about 40–60 h** | **4–7 working days with usage limits** |

Each phase ends with a short status to the owner: what was found, what was fixed, what is waiting for "merge".

## Decisions needed from the owner (one at a time)

- **D1.** Turn on branch protection with required checks on `main` in all 5 repos? Recommended: yes, after Phase 2.
- **D2.** Add a restricted Google Maps key as a GitHub secret for CI map tests? Recommended: yes, a separate test key limited to the test domains.
- **D3.** Real-device testing: you test from a script I write, or a paid device service (Firebase Test Lab / BrowserStack)? Recommended: your own phone for the test week, a service later.
- **D4.** Raise price after the 10-minute search has expired: allow (contract + server change) or not? Recommended: no; offer "Search again" instead.
- **D5.** Render paid plan for the real test week (no sleeping server)? Recommended: yes, before testers start.

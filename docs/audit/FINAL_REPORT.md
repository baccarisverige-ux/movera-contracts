# Movera audit: final report (Phase 8)

Date: 2026-10-27. Scope: rider app, driver app, admin panel, server, contract. Plan: `AUDIT_PLAN.md`. Phase reports: `phase-1-report.md` … `phase-6-report.md` here, and each repo's `docs/audit/`. Every number below comes from those files. If a number is not there, this report says "not measured".

## Summary for the owner (plain language)

1. All 8 audit phases are done. 33 audit PRs are merged across the 5 repositories. Every one had green checks.
2. A full ride now runs as an automatic test on every server change: book, offer, accept, drive, pay, cancel and no-show. Trip id, driver, car and money matched in all three apps.
3. 39 fixes are listed in section 8, almost all with a test that failed before the fix. On the server they include wrong money (unlimited cash, negative fare) and one way to take over the owner's admin account.
4. The admin panel can now show live trips and make refunds. Demo pages are hidden or marked "Demo, not live".
5. The apps no longer show demo rides or wrong earnings to real drivers. A driver who signs in again gets their ongoing trip back.
6. Speed is fine. The server answers in about 5 ms (typical) and 29 ms (slow cases). The rider app sends a third fewer requests during a trip than before.
7. Nothing was tested on a real iPhone, Android phone or Google map. You need to run the device checklist yourself (`movera-server/docs/audit/device-checklist.md`).
8. Two Google Maps keys are still in old git history. Please change (rotate) them in Google Cloud.
9. Before testers start: move Render to a paid plan, set `OSRM_URL` and `GOOGLE_MAPS_API_KEY`, and turn on branch protection (exact steps in section 13).
10. The largest remaining work items: an SMS provider, driver routes through the server, rider live updates by event stream, the admin Pricing and Refunds pages, and the driver safety alert.

---

## 1. Findings with severity, per app

Severity: S1 critical (crash, wrong money, someone else's ride, stuck ride) · S2 high (flow cannot finish, wrong state, sync broken) · S3 medium · S4 low.

| Repo | S1 | S2 | S3 | S4 | Main items |
|---|---:|---:|---:|---:|---|
| movera-server | 0 | 5 | 8 | 9 | wrong-zone admin takeover (P4-1), blocked driver back online (P3-3), unbounded cash (P3-2), no password recovery (P4-4), admin link in log |
| movera-rider-app | 2 | 7 | 18 | 9 | mock-only tests, iPhone reload N3 (device), contract 5 versions behind, stuck "Back to home", double-tap booking, map camera N6 |
| Movera-driver-app | 0 | 7 | 5 | 3 | demo scheduled rides in the live build, local SEK-only earnings, safety alerts to a demo store, trip not restored (D-3), Maps key in history |
| Admin-panel-movera-dispatch | 2 | 6 | 4 | 1 | no live trips or refunds, ~29 demo pages shown as live, pricing kept in the browser, critical advisory |
| movera-contracts | 0 | 1 | 3 | 1 | consumer copies out of date (C1), `raise_price` without a scenario |

These counts are taken from the phase tables (baselines §10, phase 3–7 findings). The count of S3 and S4 items in the baselines is approximate, because some baseline rows group several small items.

## 2. Architecture weaknesses

| # | Weakness | Where | Effect |
|---|---|---|---|
| A1 | The rider app's tests mostly run against an in-app mock that speaks an older request format (`ApiClient.contractWire` is false in tests) | rider `lib/core/api/in_process_mock_client.dart` (2,787 lines) | High coverage (92.9 % of lib/core) does not prove the live wire works. Phase 3 harness and cross-app runs filled part of the gap. |
| A2 | The rider polls the trip every 2 s and messages every 10 s. It does not use the server's event stream. | rider `api_ride_realtime.dart` | 36 requests a minute per rider on trip screens (P7-R2) |
| A3 | Both apps and the admin keep their own copies of money and dispatch rules (fares, cancel fees, 25 % commission fallback, refund policy) | driver `waybill.dart`, rider calculators, admin `pricing/`, `dispatch/` | They can drift from the server. The live paths now show server amounts. The fallbacks still exist. |
| A4 | The two Flutter apps share no code: api client, money, token store, map bridge and camera logic are written twice and have diverged | rider vs driver | Every map fix has to be made twice (as in N6) |
| A5 | Very large widget files that contain logic | driver `scheduled_rides.dart` 2,706, `home_map_sheet.dart` 2,396; rider screens > 3,000 lines | Hard to test; state is held in screens |
| A6 | Several driver live-build parts are still in memory or demo: session repository, waybills, safety alerts (`DemoSafetyAlertRepository`) | driver `lib/main.dart` | Lost on reload; safety alerts never reach Movera |
| A7 | The driver app calls the public OSRM demo directly, not the server | driver `RoadRouteService` | Driver positions go to a third party; no control over limits |
| A8 | Rate limits and Places sessions are per server instance, in memory | server | Fine for one instance; wrong with two |
| A9 | Server helpers are duplicated (`keyOf` ×7, `ID` ×7, two sweeps, two haversines) and there are 6 dead exports | server | Small drift risk (S4) |
| A10 | The admin "commands registry" (412 actions) runs only in demo mode; live pages call server paths directly | admin | Two code paths for the same action |

## 3. Ride lifecycle defects

| Id | Sev | Repo | Defect | State |
|---|---|---|---|---|
| P3-1 | S3 | server | Raise-price 2× cap was skipped when the quote was 0 | fixed |
| P3-2 | S2 | server | Driver-reported cash had no upper limit (feeds cash balance and refund room) | fixed |
| P3-3 | S2 | server | Driver or car blocked mid-trip came back online after the trip and got offers | fixed |
| D-1 | S3 | driver | After a reload the radar showed "off" while the server kept the driver online | fixed |
| D-3 | S2 | driver | Fresh sign-in during an accepted trip showed "searching"; the trip was not restored | fixed (Phase 5) |
| R-1 | S3 | rider | Receipt offered tips the server refuses; a chosen tip was never sent | fixed |
| P5-R1 | S2 | rider | "Back to home" stuck on an ended ride after a reload | fixed |
| P5-R6 | S2 | rider | Double tap on "Select ride" requested a ride without showing Set pickup | fixed (taps ≤ 350 ms) |
| O10 | S3 | rider | Two taps ≥ 600 ms apart can still book | open |
| O1 | S3 | rider | Reload on Plan / Select / Set pickup returns to Home (no booking draft kept) | open |
| N4 / D4 | — | rider, server | Raise after the 10-minute expiry: owner decided "no raise, offer Search again" | to build (section 12) |
| — | S3 | contract fixtures | No-show fee in sample app configs 50 kr; server charges 65 kr | owner decided 65 kr; configs to align |

The e2e harness tests 11 scenario groups (sign-in, quotes, full ride, cancels, dispatch, raise, endings, concurrency, admin actions, authorization, terminal states). They all pass. It found no ride that could be reopened after it ended.

## 4. Measured performance

Method: release builds, headless Chromium (Playwright 1.56, SwiftShader, 390×844), audit container with 4 cores, no GPU and no Maps key. The server numbers come from the e2e harness on Postgres 16. These are lab times, not phone times.

| What | Number | Method |
|---|---|---|
| Server, all responses (2,557) | p50 4.8 ms, p95 28.7 ms, p99 61.3 ms | Fastify `elapsedTime` over the whole e2e suite |
| Server, slowest real route | `POST /trips` p95 72.4 ms; admin sign-in p95 165.2 ms (argon2, on purpose) | same |
| One whole ride | 54 requests, p95 19.5–20.9 ms, slowest 44–47 ms (3 runs) | `15_timing.test.ts` |
| Slow query fixed (P7-S1) | earnings bonus sum on 300,000 rows: 17.1 ms → 0.085 ms | `EXPLAIN ANALYZE`, migration 0020 |
| Rider start | first frame 1,445 ms, Home 2,220 ms, quiet 2,669 ms, heap 25.0 MB | 5 cold loads, median, demo build |
| Rider bundle | `main.dart.js` 5,885,576 B (1,671,896 gzip) | production build |
| Rider Select ride sheet, 10 drags | Flutter frame p50 6.2 ms, p95 12.8 ms, 2 of 1,265 frames over 32 ms | `select_ride_sheet_probe.mjs` |
| Rider memory, 10 bookings | heap 40.8 → 48.5 MB: +0.86 MB a booking on average, about 0.5 MB from booking 5 (about 4 MB a booking before Phase 6); 2 maps reused | `web_lifecycle_probe.mjs --cycles 10` |
| Rider API calls a minute on trip screens | 54 → 36 (Finding 46 → 36); Home 0 | counted on the server |
| Rider GPS, Home 1 min | 1,653 puck repaints, 0 network requests; web: 906 frame callbacks, p95 5.5 ms, 5.8 s main thread | widget test + `--gps-minute` |
| Driver start | first frame 2,032 ms; main thread never quiet before 22.5 s (P7-D1); heap 27.8 MB | 5 cold loads, median |
| Driver bundle | `main.dart.js` 5,631,828 B (1,595,503 gzip) | release build |
| Driver Home offline, idle 60 s | 2,025 frames, 11.1 s main thread (about 18 % of a core) | rAF wrapper |
| Driver trip screen, 1 Hz GPS, 60 s | 3,119 frames, p95 2.9 ms, 0 over 32 ms | same |
| Driver API calls a minute | 0 besides the event streams (location report not measured: no GPS fix in the lab) | counted on the server |
| Driver GPS, 1 min driving | 1 route request, 62 navigation updates | widget test |
| Admin first load | live sign-in: first screen 521–537 ms, 4 requests, 1.2 MB, heap 3.1 MB | 5 cold loads |
| Admin entry script | 877,765 B (270,926 gzip); maps load only on map pages | `vite build` |
| Rebuild counts on web | not measured (release builds have no build timeline) | — |
| Real phone frame rate, CPU, battery | not measured | device checklist |

## 5. Security findings

| Id | Sev | Repo | Finding | State |
|---|---|---|---|---|
| P4-1 | S2 | server | A zone-limited Super admin could make a password link for the all-zones owner and take over the account | fixed |
| P4-4 | S2 | server, admin | No way back in after a forgotten admin password (free plan, no shell) | fixed: `ADMIN_PASSWORD_RESET` and help on the sign-in page |
| P4-8 | S2 | rider, driver | Two Google Maps keys in git history; one is still at 4 branch tips | **owner must rotate** |
| — | S2 | server, admin | zod high advisory; maplibre-gl critical XSS advisory; vitest/tinypool dev advisories | fixed (Phase 2); `npm audit` 0 |
| Base #1 | S2 | server | Admin password setup link written to the start-up log | kept on purpose (free-plan bootstrap); staging only, 72 h, single use |
| P3-4 | S3 | server | `GET /admin/approvals` not zone-filtered | fixed |
| P4-2 | S3 | server | Document uploads without a rate limit | fixed (30 an hour, `429 upload_limit`) |
| P4-3 | S3 | server | Admin could set a negative fare | fixed |
| P4-7 | S3 | server | Phone numbers and e-mails from query strings in the request log | fixed |
| P4-10 | S3 | admin | 2 high advisories in vite (dev server) | fixed |
| P4-5 | S4 | server | `POST /telemetry/*` not served (app logs lost) | fixed |
| P4-6 | S4 | server | Riders not zone-scoped for zone-limited admins | owner decided: zone-limited admins see only riders who rode in their zones; to build |
| P4-9 | S4 | rider | Off-contract calls `/ride-types`, `/rider/promotions/active` | fixed |
| P4-11 | S4 | server | Approval id can be probed (404 vs 403) | open |
| P4-12 | S4 | server | `POST /notifications/{id}/read` has no Idempotency-Key | open |
| P4-13 | S4 | server | Three attempt tables are never swept | open |

How it was checked: a route-by-route authorization matrix (`12_route_matrix.test.ts`, every served route × every caller); `git log --all -p` of every repo with gitleaks-style patterns (gitleaks itself was not run locally; CI runs it); every server log line read; `npm audit`. **Not checked:** Flutter dependency advisories (no advisory source reachable).

## 6. Tests added

| Repo | Before (baseline) | Now | Main additions |
|---|---|---|---|
| movera-server | 568 tests, 40 files; flaky (red in 2 of 3 runs) | 671 tests, 58 files; deterministic | e2e harness, 14 files / 70 tests (incl. route matrix, security, telemetry, timing); query-plan test (22 hot queries); log privacy test |
| movera-rider-app | 2,958 passed, 3 skipped | 3,007 passed, 3 skipped | off-contract calls, tip state, Back/reload, double tap, camera pose, approximate route, map unavailable, GPS budget, telemetry request budget; CI memory probe |
| Movera-driver-app | 2,178 passed, 2 failed (flaky), 1 skipped | 2,310 passed, 1 skipped | screen sweep (21 screens × 4 = 84), live account screens, D-1/D-3 restore, trip map label, GPS budget, web gesture harness case |
| Admin-panel-movera-dispatch | 257 unit; e2e 239 passed, 4 flaky, 2 failed of 245; 6 live e2e | 258 unit; e2e 245 of 245; live e2e specs `live-people`, `live-trips`, `live-controls` (23 `test(` blocks in the files; the run count was not recorded) | live Trips, Refund dialog, controls, forgot-password |
| movera-contracts | 24 scenarios | 24 scenarios (raise_price scenarios C2 and fixtures C3 not added) | CI checks only |

## 7. Workflows changed

| Repo | PR | Change |
|---|---|---|
| movera-contracts | #9 | `verify`: openapi.yaml must equal the generator's output; CONTRACT.md title must name the version; pinned PyYAML; cancel superseded runs |
| movera-server | #17, #23 | ESLint (new config), `npm audit` (high), coverage floors (rules, trips, dispatch, auth), gitleaks over full history, timeouts, concurrency. #23: query-plan and ride-timing budgets run in `test:coverage` |
| movera-rider-app | #422, #427 | One `CI gate` (lockfile, format, analyze `--fatal-infos`, tests once instead of 5–6 times, coverage floor 92.8 %, integration, web builds, gitleaks); 7 duplicate workflows deleted; Flutter pinned; every job has a timeout. #427: web size budget and the "Web memory over repeated bookings" job (required by the gate) |
| Movera-driver-app | #386, #390 | Format check, pinned Flutter, coverage floor 91.5 % lib/core, gitleaks, live web build on every PR, timeouts, concurrency. #390: web size budget |
| Admin-panel-movera-dispatch | #146, #152 | Five-job "Webapp checks" (typecheck/lint ratchet 39/unit/build, npm audit, gitleaks, Playwright e2e, live e2e); Pages deploys only after the checks pass on main. #152: first-load size budget |

## 8. Every fix, with root cause and evidence

All fixes have a test that failed before the fix and passes after, except where the Test column says otherwise.

| Id | Sev | Repo | Defect | Cause | Fix | Test | PR |
|---|---|---|---|---|---|---|---|
| — | S3 | server | 5 flaky tests (hooks, sleeps) | default 10 s hookTimeout; fixed `sleep(100)` waits | hookTimeout 60 s, wait-until polling | 3 runs × 568 green | server #17 |
| — | S2 | server | zod high advisory; vitest dev advisories | old versions | zod 4.6.7, vitest 5.0.5 | `npm audit` 0; suite green | server #17 |
| P3-1 | S3 | server | Raise cap skipped at quote 0 | `booked > 0 &&` guard | guard removed | `06_raise` "a quote of 0" | server #18 |
| P3-2 | S2 | server | Unbounded reported cash | `cashCollected` taken as given | `400 cash_above_fare` | `09_admin` cash test | server #18 |
| P3-3 | S2 | server | Blocked driver/car back online after the trip | `releaseDriver` always set `online` | online only if driver, car and fleet may drive | `09_admin` two block tests | server #18 |
| P3-4 | S3 | server | Approvals list leaked other zones | no zone condition | filter by admin zones | `10_authorization` approvals | server #18 |
| P4-1 | S2 | server | Zone admin could reset the owner's password | only `team.edit` checked | caller's zones must cover target's | `13_security` P4-1, route matrix | server #22 |
| P4-2 | S3 | server | No upload rate limit | none existed | 30 an hour, migration 0018 | `13_security` P4-2 | server #22 |
| P4-3 | S3 | server | Negative fare by admin | Money schema allows negatives | `notBelowZero`, `400 invalid_amount` | `13_security` P4-3 | server #22 |
| P4-4 | S2 | server | No admin password recovery | link only when no password exists | `ADMIN_PASSWORD_RESET` gives one link per value | `testWeek.test.ts` forgot password | server #22 |
| P4-5 | S4 | server | Telemetry not served | routes missing | `src/telemetry/routes.ts`, migration 0019 | `14_telemetry` (5) | server #22 |
| P4-7 | S3 | server | PII in request log | query string logged | path without query | `logs_privacy.test.ts` | server #22 |
| P7-S1 | S4 | server | Bonus sum scanned whole earnings table | no index starting with `trip_id` | migration 0020 `(trip_id, kind)` | `query_plans.test.ts` "trip bonus paid" | server #23 |
| C1 | S2 | rider, driver, admin | Contract copies 0.5.0 / 0.5.3 | not synced | synced to 0.5.5 / 0.5.6 | contract tests | rider #422, driver #386, admin #145/#146 |
| — | S4 | driver | 2 wall-clock-flaky tests | real clock vs fake clock | same clock in app and tests | 5 parallel runs green | driver #386 |
| D-1 | S3 | driver | Radar off but server online after restart | start state never read from the server | `settleAfterStart()` sets a stale online to offline | `live_driver_services_test` D11 (3) | driver #387 |
| D-2 | S4 | driver | "Demo offers" on a live trip map | label always drawn | demo only | `trip_map_controls_test` | driver #387 |
| D-3 | S2 | driver | Trip not restored on fresh sign-in | `activeTripId` never read | restore from server | Home restore test | driver #388 |
| — | S2 | driver | Demo scheduled rides and SEK-only local earnings in the live build | demo store, local sums | server earnings / honest empty state | live empty state tests | driver #388 |
| — | S3 | driver | Two quick car picks sent two PATCH | no in-flight guard | pick waits for the one in flight | `live_account_screens_test`, `my_fleet_screen_test` | driver #388 |
| M6 | S4 | driver | Pickup pay called "Movera-bonus"; fr overflow in Documents | wording, layout | "paid by Movera"; layout | screen sweep | driver #388 |
| P6-D1 | S3 | driver | Web camera fought the finger (N6) | touch not visible to Dart on web | app claim re-arms release | `verify_driver_map_web.cjs` | driver #389 |
| R-1 | S3 | rider | Tips offered, never sent | options from config regardless of server | `tipsOnServer` false on contract wire | `tip_honest_state_test` | rider #423 |
| P4-9 | S4 | rider | Off-contract calls (404) | always called | not on the contract wire | `phase4_off_contract_calls_test` | rider #424 |
| P5-R1 | S2 | rider | Stuck on ended ride after reload | Back to home on dead ride | fixed navigation | phase 5 test | rider #425 |
| P5-R2, R5 | S4 | rider | `/rides/{id}/nearby`, `/account/security` 404s | not served by the server | not called live | phase 5 tests | rider #425 |
| P5-R3, R4, R7 | S3 | rider | Safety settings, Change route, Help "Send" fail | server does not serve them | honest "not available" states | phase 5 tests | rider #425 |
| P5-R6 | S2 | rider | Double tap booked a ride | second tap hit Confirm while screen slid in | Confirm ignored until open | `phase5_pickup_tap_through_test` | rider #425 |
| P6-R1 | S3 | rider | Camera flew in from world view | zoom 0 / (0,0) report taken as pose | `MapCameraReport.isFrame` | `custom_google_map_release_test` | rider #426 |
| P6-R2 | S3 | rider | Camera snapped back after pinch | late route refit | no refit after a hand move | `select_ride_road_route_test` | rider #426 |
| P6-R3 | S3 | rider | Straight line drawn like a road (N2) | no label on Select/Finding | "Approximate route" badge | `n2_approximate_route_test` | rider #426 |
| P6-R4 | S3 | rider | Grey map forever if Maps fails | no timeout | "Map unavailable" after 12 s | `map_unavailable_message_test` | rider #426 |
| P7-R1 | S3 | rider | Telemetry line for every answered call | sink sent routine `api.*` lines | only status ≥ 400 and other lines | `telemetry_request_budget_test`; 54 → 36/min | rider #427 |
| — | S2 | admin | maplibre critical, zod high advisories | old versions | maplibre 6.16, zod 4.6.7, worker URL fix | `npm audit` 0; e2e green | admin #146 |
| — | S2 | admin | Map pages blocked the main thread; maps waited for tiles | surge pulse repainted ~12×/s while hidden; `load` waits for TileJSON | animate visible layer only; `style.load` | e2e 245/245 (was 2 failed, 4 flaky) | admin #146 |
| P4-10 | S3 | admin | vite high advisories | old lock | vite 6.4.5 | `npm audit` 0 | admin #147 |
| F1 | S1 | admin | No live Trips pages | not built | Trips list, detail, refund | `live-trips.spec.ts` | admin #151 |
| F3 | S2 | admin | ~29 demo pages shown as live | menu not filtered | live menu limited, "Demo, not live" banner | `live-controls.spec.ts` | admin #151 |
| F4 | S3 | admin | Sign-in landed on "No access" | first page not allowed | first readable live page | live e2e | admin #151 |
| G1, G2 | S3 | contracts | openapi.yaml hand edits and title version not checked | no CI step | verify.sh regenerates and diffs | hand edit rejected | contracts #9 |

## 9. Builds and coverage now

| Repo | Builds in CI | Coverage now | Baseline |
|---|---|---|---|
| movera-server | typecheck, lint, build | lines 94.54 %, statements 89.88 % (vitest 5 counting); floors per area unchanged | 94.2 % statements/lines (vitest 3 counting, not comparable 1:1) |
| movera-rider-app | production + staging web, Linux integration | lib/core 92.92 % (floor 92.8 %) | lib/core 92.9 %, lib 90.8 % |
| Movera-driver-app | web, live web, Android release, iOS compile preflight | lib/core 92.26 % (floor 91.5 %) | lib/core 91.8 %, lib 89.1 % |
| Admin-panel-movera-dispatch | `vite build` live and demo | not re-measured (baseline 97.55 % of unit-loaded files; pages not measured) | same |
| movera-contracts | verify.sh | n/a | — |

Size budgets in CI: rider `main.dart.js` ≤ 6,500,000 B / 1,850,000 gzip; driver ≤ 6,200,000 / 1,760,000; admin entry script ≤ 970,000 / 300,000 and stylesheet ≤ 390,000 / 66,000. Rider memory: ≤ 2.0 MB a booking, ≤ 2 maps, no WebGL loss. Server: one ride ≤ 60 requests, p95 < 250 ms.

## 10. Remaining problems and untested areas

**Open problems**
- Driver P7-D1 (S3, battery): the Radar pulse redraws every frame on idle Home, about 18 % of a core.
- Rider O1 (no booking draft after reload), O10 (taps ≥ 600 ms apart), O2/O3/O6/O7 (server or contract endpoints missing: route-quote, PATCH trip, Safety, wallet, saved places), O8 (16 error lines per quote), P7-R3 (trip booked elsewhere not noticed on Home), straight line through stops not labelled.
- Driver: safety alerts go to a demo store; `GET /driver/reservations` not served; rider first name not in TripProjection; Add car Save is disabled without saying why; routes go to the public OSRM.
- Admin: no live Refunds list (server lacks `GET /admin/refunds`); pricing/zones still kept in the browser; no live riders, live map, dispatch control, approvals or audit pages; 39 lint warnings (capped); fixed sleeps in drawing e2e specs; no request timeout in the live client.
- Server: P4-11, P4-12, P4-13; helper duplication; rate limits per instance; the admin link is still in the start-up log.
- Contracts: C2 `raise_price` scenarios, C3 fixtures (invitations, provider sign-in, early-end, on-the-way), C5 tags v0.5.x (only v0.4.4 and v0.5.2 exist).
- Rider `qa-*` workflows against the published site: still red on main (they need the live site and a Maps key).

**Untested end to end:** scheduled rides, card payments, two server instances, admin manual booking (not served), real SMS, Apple/Google sign-in, real road routing with `OSRM_URL`, LISTEN reconnect, Flutter dependency advisories, behaviour on Render.

**Needs a real device** (script: `movera-server/docs/audit/device-checklist.md`)
1. Pinch zoom on rider Select ride, Finding, trip map and driver trip map (N6).
2. WebGL loss on iOS Safari: 10 book-and-cancel cycles plus 2 trips.
3. Safari reload (N3) on every booking step: app switch and 5-minute lock.
4. GPS while driving: car movement on both phones, offers after 5 min online, re-route, arrive/complete at 100 m.
5. Battery and heat, 30 min each: driver Home offline (P7-D1), online, trip; rider Home, Finding.
6. Frame rate: Select ride sheet drags, driver Radar list.
7. Rider Home after a full trip with a real Maps key (P7-R4: ~200 Maps rAF callbacks a second in the lab).
8. Driver location report rate on a phone (P7-D2).
9. Real Google Maps rendering, the "Map unavailable" text with a revoked key, the dialer (112), document camera and file picker.

## 11. Commit hashes and PR links

Squash commits on `main`. Links: `https://github.com/baccarisverige-ux/<repo>/pull/<n>`.

| Repo | PR | Commit | Title |
|---|---|---|---|
| movera-contracts | [#8](https://github.com/baccarisverige-ux/movera-contracts/pull/8) | 744192c | Phase 1: handoff, plan, progress, baseline |
| movera-contracts | [#9](https://github.com/baccarisverige-ux/movera-contracts/pull/9) | 9c0acb6 | Phase 2 CI |
| movera-contracts | [#10](https://github.com/baccarisverige-ux/movera-contracts/pull/10) | 1e650f5 | Progress: merge permission |
| movera-contracts | [#11](https://github.com/baccarisverige-ux/movera-contracts/pull/11) | ba9f953 | Phase 2 report |
| movera-contracts | [#12](https://github.com/baccarisverige-ux/movera-contracts/pull/12) | 5a0f72b | Phase 3 report |
| movera-contracts | [#13](https://github.com/baccarisverige-ux/movera-contracts/pull/13) | 3229721 | Phase 4 report |
| movera-contracts | [#14](https://github.com/baccarisverige-ux/movera-contracts/pull/14) | 727b0d0 | Phase 5 report |
| movera-contracts | [#15](https://github.com/baccarisverige-ux/movera-contracts/pull/15) | 42fbd04 | Phase 6 report |
| movera-contracts | [#16](https://github.com/baccarisverige-ux/movera-contracts/pull/16) | 25b0f6e | Owner decisions |
| movera-server | [#16](https://github.com/baccarisverige-ux/movera-server/pull/16) | 6dc06a4 | Phase 1 baseline |
| movera-server | [#17](https://github.com/baccarisverige-ux/movera-server/pull/17) | 6b114d6 | Phase 2 CI |
| movera-server | [#18](https://github.com/baccarisverige-ux/movera-server/pull/18) | c13d1e0 | Phase 3 harness + 4 fixes |
| movera-server | [#19](https://github.com/baccarisverige-ux/movera-server/pull/19) | 2bac32c | Phase 3 cross-app run |
| movera-server | [#22](https://github.com/baccarisverige-ux/movera-server/pull/22) | 616eb29 | Phase 4 security |
| movera-server | [#23](https://github.com/baccarisverige-ux/movera-server/pull/23) | cbaece4 | Phase 7 performance |
| movera-rider-app | [#421](https://github.com/baccarisverige-ux/movera-rider-app/pull/421) | 69028e22 | Phase 1 baseline |
| movera-rider-app | [#422](https://github.com/baccarisverige-ux/movera-rider-app/pull/422) | 265fd2ac | Phase 2 CI gate |
| movera-rider-app | [#423](https://github.com/baccarisverige-ux/movera-rider-app/pull/423) | 21618721 | Phase 3 R-1 |
| movera-rider-app | [#424](https://github.com/baccarisverige-ux/movera-rider-app/pull/424) | e7c0b03f | Phase 4 P4-9 |
| movera-rider-app | [#425](https://github.com/baccarisverige-ux/movera-rider-app/pull/425) | 02f98320 | Phase 5 screens |
| movera-rider-app | [#426](https://github.com/baccarisverige-ux/movera-rider-app/pull/426) | c097dd2c | Phase 6 maps |
| movera-rider-app | [#427](https://github.com/baccarisverige-ux/movera-rider-app/pull/427) | 8c3c1316 | Phase 7 performance |
| Movera-driver-app | [#384](https://github.com/baccarisverige-ux/Movera-driver-app/pull/384) | 5cd1758a | Phase 1 baseline |
| Movera-driver-app | [#386](https://github.com/baccarisverige-ux/Movera-driver-app/pull/386) | 11ccb12a | Phase 2 CI |
| Movera-driver-app | [#387](https://github.com/baccarisverige-ux/Movera-driver-app/pull/387) | 61461f15 | Phase 3 D-1, D-2 |
| Movera-driver-app | [#388](https://github.com/baccarisverige-ux/Movera-driver-app/pull/388) | 01eaf3ee | Phase 5 screens |
| Movera-driver-app | [#389](https://github.com/baccarisverige-ux/Movera-driver-app/pull/389) | 05f157af | Phase 6 maps |
| Movera-driver-app | [#390](https://github.com/baccarisverige-ux/Movera-driver-app/pull/390) | 71e5568d | Phase 7 performance |
| Admin-panel-movera-dispatch | [#144](https://github.com/baccarisverige-ux/Admin-panel-movera-dispatch/pull/144) | e4504cc | Phase 1 baseline |
| Admin-panel-movera-dispatch | [#146](https://github.com/baccarisverige-ux/Admin-panel-movera-dispatch/pull/146) | e89de99 | Phase 2 CI |
| Admin-panel-movera-dispatch | [#147](https://github.com/baccarisverige-ux/Admin-panel-movera-dispatch/pull/147) | 40d7cbf | Phase 4 |
| Admin-panel-movera-dispatch | [#151](https://github.com/baccarisverige-ux/Admin-panel-movera-dispatch/pull/151) | b69311b | Phase 5 live Trips |
| Admin-panel-movera-dispatch | [#152](https://github.com/baccarisverige-ux/Admin-panel-movera-dispatch/pull/152) | ab30cb5 | Phase 7 performance |

Phase 0 (merged by the owner): driver #380 `436bfb54`, rider #413 `c1063fb8`.

## 12. Prioritized remaining work

| Prio | Item | Repo(s) | Note |
|---|---|---|---|
| 1 | No-show fee **65 kr** in the app sample configs (now 50 kr) | contracts, apps | owner approved |
| 2 | Driver routes through the server `GET /routes/driving/…` instead of the public OSRM | driver | owner approved; needs `OSRM_URL` |
| 3 | Rider "Search again" after the 10-minute expiry (no raise after expiry, D4) | rider | owner approved |
| 4 | Driver safety alert endpoint (ride-check alerts reach Movera) | contract, server, driver | safety |
| 5 | Admin Refunds list: server `GET /admin/refunds` first, then the panel page | server, admin | in the contract, not served |
| 6 | Live admin Pricing page + per-trip "waive fee" button (server config API exists) | admin, server | owner approved |
| 7 | Zone-limited admins see/block only riders who rode in their zones (P4-6) | server | owner approved |
| 8 | P7-D1: Radar pulse only while online, or stop after a few cycles | driver | battery |
| 9 | Rider polling → event stream `GET /trips/{id}/events` (P7-R2) | rider | 30 polls a minute per rider today |
| 10 | Scheduled rides end to end (`GET /driver/reservations` not served; untested) | contract, server, apps | |
| 11 | Rider booking draft across reload (O1); double-book at ≥ 600 ms (O10) | rider | |
| 12 | Contract: `raise_price` scenarios, missing fixtures, v0.5.x tags | contracts | |
| 13 | Server S4 cleanups (P4-11..13, duplicated helpers); admin lint warnings | server, admin | |
| 14 | Shared Flutter package for map, api and money code | rider, driver | architecture |

## 13. Owner actions

| # | Action | How |
|---|---|---|
| 1 | Render paid plan (no sleeping, no expiring database) before testers start | Render → movera-server → Settings → plan; the same for the database |
| 2 | `OSRM_URL` | Render → movera-server → Environment → `OSRM_URL` = `https://router.project-osrm.org` (or Movera's own OSRM if logs say "OSRM unavailable") |
| 3 | `GOOGLE_MAPS_API_KEY` (address search) | Render → Environment |
| 4 | Rotate the 2 Maps keys in git history (`AIzaSyB2…g3eQ`, `AIzaSyBJ…Dml8`) | Google Cloud → Credentials: make new keys, restrict them (Android package + SHA-1, iOS bundle id, web by HTTP referrer), update the secrets, delete the old keys |
| 5 | Delete the branches that still carry the keys | rider: `web-preview-reservation`, `web-live`, `audit-live-rider-runtime-20260925`, `audit/all-paths-inverse`, `audit/deep-booking-lifecycle`; driver: `chore/drider-phase0-1-baseline`, `chore/extract-uploaded-project` |
| 6 | Maps test key for CI (D2) | a separate key restricted to the test domains → GitHub → each app → Settings → Secrets and variables → Actions → new secret |
| 7 | Branch protection on `main` (D1), all 5 repos | GitHub → repo → Settings → Branches (or Rules → Rulesets) → add rule for `main` → "Require a pull request before merging", "Require status checks to pass", "Require branches to be up to date" → add the checks below → Save |
| 8 | Dependabot alerts | each repo → Settings → Code security → Dependabot alerts: Enable (needed for the Flutter advisories) |
| 9 | Testers' real phone numbers | send them to the audit; they are seeded like `src/drivers/seedTest.ts` |
| 10 | SMS provider (46elks recommended for Sweden, or Twilio) | until then only test numbers can sign in |
| 11 | Apple and Google developer ids | then `APPLE_CLIENT_IDS` and `GOOGLE_CLIENT_IDS` on Render |
| 12 | Run the device checklist | `movera-server/docs/audit/device-checklist.md` |

**Required checks per repo** (type these names exactly):

| Repo | Required check names |
|---|---|
| movera-contracts | `verify` |
| movera-server | `checks`, `secret-scan` |
| movera-rider-app | `gate` (shown as "CI gate / gate"; it fails unless static, test, integration, web builds, web memory and secret scan pass) |
| Movera-driver-app | `Analyze, test and build web`, `Secret scan`, `Build live web (MOVERA_AUTH_REQUIRED=true)`, `Android release signing and preview`, `iOS release compile preflight` |
| Admin-panel-movera-dispatch | `typecheck, lint, unit tests, build`, `npm audit (production dependencies, high and above)`, `secret scan`, `Playwright e2e`, `Playwright e2e (live, faked server)` |

**Forgotten admin password (`ADMIN_PASSWORD_RESET`):**
1. Render → movera-server → Environment → add `ADMIN_PASSWORD_RESET` with any new text (for example today's date) → Save. The service restarts.
2. Render → Logs → search `admin password reset link` → open the `setupLink`. It is valid for 72 h and works once.
3. Choose the new password. The old one works until then. After that, every admin session of that account ends.
4. Remove the variable. For another reset later, use a different value: each value makes only one link.
Only staging and development. Details: `movera-server/docs/DEPLOY_RENDER.md` "Forgot the admin password".

## OWNER RULE — FOREVER (2026-10-27, applies to every task, every session)
Before ANY decision or change:
1. Check the server, the contract, and ALL apps (rider, driver, admin) — and the owner's demo screens.
2. Look for any conflict, anything wrong, anything that does not match the server, the contract or any app.
3. Ask the owner in simple questions, one at a time, naming the exact section and part.
4. Only then do anything. Never decide alone. Never build from our own ideas.

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

## Owner pricing decisions (2026-10-27)
Reference: the admin demo Pricing section (7 tabs: Prices, Fees, Surge, Commission, Pickup pay, Tips & limits, History; plus Test a ride, Manage categories, Fixed routes). Follow it exactly, as a clean live version; ask the owner only when something conflicts.
- Child seat and baby seat fees exist only on the Child Seat category.
- Category names everywhere: Movera, Comfort, Premium, Priority, Movera XL, Electric, Movera Pet, Child Seat (one id `child_seat`; driver "Booster Seat" and rider `kids` map to it). Admin can add, delete and deactivate categories; apps follow the admin catalog.
- Surge as in the demo; the admin sets the maximum, also for smart surge.
- Waiting money: 100 % to the driver (demo example maths to be corrected).
Findings behind these: pricing comparison of 2026-10-27 (surge never applied by the server; seat, airport, fixed-route and stop-wait prices never charged; publish does not update app configs; live page lacked 6 tabs and validation).

## Owner plan for the admin (2026-10-27)
Step 1: the live admin is an exact copy of the whole demo admin (all 33 sections, every page, control and text; nothing removed or renamed). Connected where the server already serves the data; everything else looks exactly like the demo, not yet connected.
Step 2: section by section with the owner: contract → server → driver and rider apps → owner decides what to add, remove or adjust.

## Owner Trips decisions so far (for step 2)
- Server adds the rider's name to the admin trip; adds list counts and KPI totals.
- Server adds Flag, Note, Do not match again, Open a ticket, Resend receipt, and the Flagged group.
- "Problems" group includes failed payments. Saved views stored on the server, shareable. Payment filter adds "Partly refunded".
- "How the price was made" exactly like the demo: server sends km, minutes and rates per line.
- Admin shows app fee, pickup fee and reservation fee separately. The driver never sees admin details: only one total.
- "Who gets what": server adds promotion, tip, fleet share, VAT. Admin can deactivate all payment methods and keep only cash / pay the driver; then VAT handling is off (the driver handles VAT).
- Admin shows "Pickup pay" as its own line (admin only).
- Note on cancel / reassign / no-show / complete: optional, like the demo.
- Refunds: part or full; earlier refunds of the trip are shown; an expired trip that was charged is refunded automatically, and the admin can also refund.
- Price change (±15 %) only while the trip is going on; after it ends, Refund.
- Waiting time is a general rule from Pricing, never changed on a single trip: remove the per-trip "Waiting minutes" control.
- Server adds real distance, ride time, the rider's rating and "PIN verified".
- Car type names: Movera, Comfort, Premium, Priority, Movera XL, Electric, Movera Pet, Child Seat.

## Owner decisions on the 33-section check (2026-10-27)
1. Settings flow first: admin Publish saves to the server; rider and driver apps fetch their settings from the server.
2. Real data only, nothing invented: connect online status, payment method, live positions, etc. to the server; where the server lacks data (risk, reviews), build it on the server; never show fake values.
3. Refunds: no second admin; any admin with refund rights refunds at once.
4. SOS: build the real path rider SOS → server → admin Incidents + alarm, before testers start.
5. Chat: only support roles, only their zones; every opening logged.
6. Drivers › Activate: the server refuses until all documents and a car are approved.
7. Fleet drivers: the fleet company gets only the driver's earnings; remove the extra fleet-owner % from the admin.
8. Admin sign-in: e-mail + password only; remove the 2-step code switch.
9. Zones: the server's list is the truth; the admin reads it and creates zones on the server.
10. Reports › Money: Movera's real earnings summed from each trip on the server.
11. Alerts: "car lost" (rider on board, no driver position for 30 min) → red alert + alarm sound in Alerts and Dispatch.
12. Audit page connected to the server.
13. Payouts: list "Refunds to send by hand" (Swish/bank) with "Mark as paid".
14. Riders › Call rider: keep as today (riders.read).
15. Onboarding: same document list as driver app and server (SE + FR); Approve/Reject connected.
16. Status words: the server's words everywhere in the admin (sv/fr/en).
Earlier, still valid: Dispatch = one section built from the whole Dashboard plus what only Dispatch has; no separate Dashboard. The owner will explain later how Super admin gives roles.

## Owner safety part 1 decisions (2026-10-27)
- Rider SOS and driver SOS: open the 112 call on the phone AND alert Movera.
- SOS carries the phone's GPS once; admin also sees the car's live position.
- Alarm goes first to safety/operations admins of that zone; every signed-in admin after 2 minutes untaken. No SMS when nobody is online.
- Case steps: New, Taken, Solved, False alarm.
- "Car lost": same as SOS (red, repeating alarm, same admins); closes by itself when the car's position comes back.
- After SOS the app shows only "SOS sent" (no later update).
- Ride check answers → safety part 2.

## Owner settings-flow decisions (part 2, 2026-10-27)
- A booked trip keeps ALL its rules (price, cancel fee, no-show fee and shares) from booking time.
- Apps get new settings at once while open (live stream), and also check on start.
- No server: apps use the last settings received, else their built-in settings.
- "Standard" settings per country (SE in kr, FR in €), set in admin; a zone without its own settings uses its country's standard automatically, marked "Uses standard". A zone with its own settings never uses the standard.
- Admin settings with no server field (scheduled publish/expiry, campaigns, rider texts, per-driver overrides): shown "Not connected yet"; added one by one later.
- Publishing settings: no second admin (like refunds); anyone with the publish right publishes at once.
- Country rules (tips, raise steps, driver bonus limits) are set once per country and apply to all its zones.
- Auto-offline: 10 missed or declined in a row, ONLY Exclusive offers (never Radar, never scheduled); app and server both enforce it.
- Cancel fee driver share: shown and set in Admin › Dispatch, per zone; default 100 %.
- Publishing prices also updates waiting and no-show values in the rider and driver app settings.
- Rider app takes its car types from the rider settings the admin publishes.
- The server's version number counts.

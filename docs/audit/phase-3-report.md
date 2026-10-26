# Phase 3 report: ride lifecycle and the three apps together

Date: 2026-10-26. Status: **done**.

## Merged
- movera-server #18: e2e harness (`test/e2e/`), 11 scenario groups, 58 tests, in CI.
- movera-server #19: cross-app run scripts (`test/crossapp/`) and `docs/audit/phase-3-crossapp.md`.
- Movera-driver-app #387, movera-rider-app #423: app fixes from the cross-app run.

## Defects fixed (each with a regression test)
| Id | Sev | Repo | Defect |
|---|---|---|---|
| P3-1 | S3 | server | Raise-price 2x cap skipped when the quote is 0 |
| P3-2 | S2 | server | Driver-reported cash had no upper bound (now `400 cash_above_fare`) |
| P3-3 | S2 | server | Driver blocked mid-trip (or car blocked) came back online after the trip |
| P3-4 | S3 | server | `GET /admin/approvals` not zone-filtered |
| D-1 | S3 | driver | After reload, app showed radar off while server kept driver online (got offers) |
| D-2 | S4 | driver | "Demo offers" label on a real trip map |
| R-1 | S3 | rider | Receipt offered tips the server refuses (`tips_not_available`) |

## Cross-app result
Trip id, status, driver, car and money matched between rider app, driver app and server at every step (fare 75,00 = earnings 54,79 + pickup pay 1,55 + commission 18,66). Screenshots: scratchpad `p3x/`.

## Open (not fixed)
- **D-3 (S2, driver):** fresh sign-in while the server holds an accepted trip shows "searching"; the app ignores the server's `activeTripId`. Feature-sized; goes to Phase 5.
- **M1 (S1, admin):** live admin has no trip pages (known since Phase 1). Phase 5.
- Server lacks `POST /telemetry/logs` (in contract); rider calls `/ride-types` and `/rider/promotions/active` (not in contract, 404). Phase 4/5.
- No-show fee: sample app configs say 50 kr, server charges 65 kr. Owner to confirm.
- Admin password link stays in the start-up log (only way to get it on Render free plan). Phase 4: add "forgot password".
- Not tested end to end: scheduled rides, card payments, several server instances, real phones.

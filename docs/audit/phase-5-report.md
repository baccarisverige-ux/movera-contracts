# Phase 5 report: every screen and every button

Date: 2026-10-27. Status: **done**.

## Merged
- Movera-driver-app #388, Admin-panel-movera-dispatch #151 (replaces #148–#150; secret-scan fixture issue), movera-rider-app #425.
- Screen lists: `docs/audit/phase-5-screens.md` in each app repo.

## Fixed (each with a test that fails before the fix)
| Id | Sev | App | Defect |
|---|---|---|---|
| D-3 | S2 | driver | Fresh sign-in during an accepted trip showed "searching"; now restored from the server's activeTripId |
| — | S2 | driver | Demo scheduled rides and SEK-only local earnings in the live build; now server earnings / honest empty state |
| — | S3 | driver | Two quick car picks sent two PATCH /driver/profile |
| — | S4 | driver | Documents overflow (fr, 320 px, text x2); "Movera-bonus" label |
| F1 | S1 | admin | No live Trips pages; list + detail + refund from trip added |
| F3 | S2 | admin | ~29 demo pages in the live build; live menu limited, others bannered "Demo, not live" |
| F4 | S3 | admin | Sign-in landed on "No access" |
| P5-R1 | S2 | rider | "Back to home" stuck on an ended ride after reload |
| P5-R6 | S2 | rider | Double tap on Select ride requested a ride |
| P5-R2..R5, R7 | S3/S4 | rider | Live build called 5 paths the server does not serve (404); now honest unavailable states |

## N3 (rider Back/reload)
Back never crashed at any booking step (Chromium). Reload on Plan/Select/Set pickup returns to Home (draft not saved, O1); Finding, Waiting, trip and completed return to the same screen. WebKit/Safari and real iPhone not tested.

## Open (need server/contract or owner)
- Admin Refunds list: `GET /admin/refunds` in the contract, not served.
- Driver safety-alert endpoint; `GET /driver/reservations` not served; rider first name not in TripProjection.
- Rider: booking draft not saved across reload (O1); route-quote / PATCH /trips off (O2); no Safety endpoints, support tickets off (O3); server wallet and saved places unused (O6/O7); double-book still possible with taps ≥600 ms apart (O10).
- Driver: Add car Save stays disabled without saying why.

# Phase 6 report: maps, GPS, search, routing

Date: 2026-10-27. Status: **done**. Merged: movera-rider-app #426, Movera-driver-app #389. Details: `docs/audit/phase-6.md` in each app.

No real Google Maps rendering was possible (no Maps key in CI or the container, no iPhone/Safari). Evidence is code, Flutter tests with a fake maps platform, and the driver's web gesture harness.

## Fixed (test fails before, passes after)
| Id | Sev | App | Defect |
|---|---|---|---|
| P6-R1 | S3 | rider | Web plugin's zoom 0 / (0,0) report taken as camera position; next move flew in from world view (N6) |
| P6-R2 | S3 | rider | Select ride camera snapped back after a pinch when a slow route answer arrived (N6) |
| P6-R3 | S3 | rider | Straight two-point route (no OSRM) drawn like a road; now labelled "Approximate route" (N2) |
| P6-R4 | S3 | rider | Map that never loads stayed grey; now "Map unavailable" after 12 s (sv/fr/en) |
| P6-D1 | S3 | driver | Web: auto return-to-car under a resting thumb fought the finger (N6) |

## Verified, already fixed earlier
N6 tilt 0 / zoom cap 17 / minimum span (rider #413); thin route line (driver #380); N5 traffic layer (both); N7 wrong first address (rider #413/#415, now pinned by a test); address search debounce and stale answers.

## GPS budgets (new tests)
Rider Home, 1 min: 1653 dot repaints, 0 network requests. Driver, 1 min driving: 1 route request, 62 navigation updates.

## Open / needs a real device
- Pinch "crash" not reproduced; suspected WebGL context loss on iOS Safari. Owner to test on iPhone: Select ride, Finding, rider trip map, driver trip map.
- Driver app calls the public OSRM demo directly instead of the server's `/routes/driving` (owner decision; proxy answers 503 while OSRM_URL is unset).
- Rider: straight line through stops not labelled.

# Movera shared contract

One contract for the three Movera apps and the server: **Rider** (Flutter),
**Driver** (Flutter), **Admin** (React/TypeScript), and the backend that will
serve all three. This repository is the only place the contract changes.
Each app and the server carries a byte-for-byte copy under `contracts/` and checks it
against `CHECKSUMS`.

Current version: **0.18.162** (`contract.json#version`, tag `v0.18.162`; 0.18.162 driver country first: `PUT /driver/country` is the first-sign-in step, `country_required` on `POST /driver/vehicles`, `POST /admin/drivers/{driverId}/country` (reason, audit), migration 0137 and the alert `driver_no_country` (`contract.json#driverCountryFirst`); after 0.18.161 0.18.161 admin cars and fleets by zone: `GET /admin/vehicles` and `GET /admin/fleets` take `zoneId` / `zoneIds` / `country` (403 `zone_out_of_scope`, total under the same filter), `Vehicle.zoneId` / `Vehicle.country` and `Fleet.zoneId`, a car with no country is an admin error + alert `car_no_country` (`contract.json#adminListFilters.carZones`); after 0.18.160 0.18.160 free pickup move 300 m: the pickup move default `booking.maxPickupMoveMeters` is 300 m (was 200), server migration 0133 moves documents still on 200, booked trips keep their booking-time value (`contract.json#pickupWaiting.pickupMove.freeMoveNote`); after 0.18.159 0.18.159 fleet needs a car: the fleet owner of a fleet with no car gets the red Home line `fleet_no_car` (Add car) from his first sign-in, and approving a fleet with no car is 409 `fleet_has_no_car` while `OnboardingSettings.fleetNeedsCarForApproval` (default on) is on (`contract.json#fleetNeedsCar`); after 0.18.154 0.18.154 P16c minimum app version (follows v0.18.153): `RiderAppConfig.appUpdate` / `DriverAppConfig.appUpdate` get `minVersion { android, ios }` and `storeUrls { android, ios }` per zone (null = off), the Android / iOS apps send `X-App-Version` + `X-App-Platform`, and below the minimum booking, go-online and offer accept answer 426 `upgrade_required` / `app_update_required` (never mid-trip), `contract.json#appUpdate`; after 0.18.153 0.18.153 P29 driver income year file (EU DAC7): `GET /admin/finance/driver-income` (+ `.csv` for the accountant) and `GET /driver/income-statement`, one row per payee (fleet, else driver) and currency, quarters / months / days / trips that add up, pay-in-car rides included (`contract.json#driverIncomeYear`); after 0.18.152 0.18.152 booked ride shown like a normal ride once its search starts: `GET /rider/trips/active` also returns a booked trip in searching / offered / accepted that no list driver holds or ever held, its driver shown at accept and the normal `driver_found` push instead of `reservation_driver_found`; a ride a list driver holds or gave back keeps the booked card until `driver_to_pickup` (`contract.json#bookedRideSeen.searchSeen`); after 0.18.151 0.18.151 SOS contacts SMS sent through the sign-in SMS sender when the server switch SOS_CONTACTS_SMS_SEND is on (default off), one SMS per contact per case, counted in the daily SMS limit (`contract.json#sosContactsSms.send`); after 0.18.150 0.18.150 L20 stream backup: after `realtime.oneStreamFallback.failuresInARow` (default 3, 1-10) failed tries of GET /driver/stream in a row the driver app opens the two old streams, and asks the one stream again after `retryOneAfterMinutes` (default 10, 1-60) or at app restart, `contract.json#driverOneStreamFallback`; after 0.18.149 0.18.149 admin sessions: an admin lists a rider's / driver's signed-in sessions and signs one or all out with a reason, the phone hears 401 `signed_out_by_movera` and shows "You were signed out by Movera" (`contract.json#adminSessions`); after 0.18.148 0.18.148 SOS by press time: an SOS that reaches Movera after the trip ended is taken when its press time (the earlier of `at` and the received time, so a fast phone clock is never refused) is from the driver assignment until 30 min after the end and it arrives within 30 min of the press, else 409 `sos_too_old` / `sos_not_during_trip`; `Incident.pressedAt` (`contract.json#sosPressTime`); after 0.18.146 0.18.146 audit N5: `GET /driver/earnings` counts every ride of each period by kind, `EarningsPeriod.rideCounts { completed, cancelled, noShow }` from trips, so the driver app's Rides and View all N rides show all kinds (`contract.json#driverRideCounts`); after 0.18.145 0.18.145 S4c load cut: `GET /driver/home-badges` (one read for Home's four badges), `airport_queue_changed` on the driver config stream with a 60 s queue fallback, rider trip watch every 60 s while the config stream is up, nearby cars kept 2.5 s per grid cell (`contract.json#loadCut`); after 0.18.144 0.18.144 adjust-pickup banner + two-way live location (`contract.json#liveLocation`, `PUT /trips/{tripId}/live-location`, `?live=true` frames, never stored); after 0.18.143 0.18.143: the rider changes the route, pickup to any place, while a live trip is still searched (`onTrip.routeChange.whileSearching`, transition `change_route`); after 0.18.141 0.18.141 the driver pays what he owes Movera with Stripe: `POST /driver/pay-movera/pay` → `StripeDriverPayment`, `DriverPayMovera.stripe`, the payment link stays as hidden legacy, `contract.json#driverPayRequest.stripe` (built as a draft under 0.18.139, renumbered for the launch); after 0.18.140 0.18.140 debt line M3: CompletePreview.cashDueRide + cashDueOutstandingFee, see CHANGELOG.md; after 0.18.139 0.18.139 driver wallet D5: `GET /driver/earnings` carries `EarningsReport.moveraBalance { owedToMovera, moveraOwesYou }`, the driver's balance with Movera now (the same sum as `debtModel.driverOwes.owed`), and the wallet shows the week's cash collected, `contract.json#driverWalletBalance`; plus the TEMPORARY monthly pay request: `CountryRules.driverPayRequest` (off), the notice `driver_pay_movera`, `GET /driver/pay-movera`, confirmed by the admin's "Driver paid Movera", `contract.json#driverPayRequest`; after 0.18.136 0.18.136 Stripe for rider fees (test or live keys, production live only): CountryRules.riderFeeStripe, POST /rider/fees/{tripId}/pay, POST /webhooks/stripe, admin status + refund, see CHANGELOG.md; after 0.18.134 0.18.134 account deletion E1: the request closes the account at once, a debt is kept as a record, the rest is erased 30 days later by `account_erase` (dry-run by default), admin list `GET /admin/deletion-requests`, `contract.json#accountDeletion`; after 0.18.133 0.18.133 real SMS sign-in codes: a real number gets its code by SMS when the server has the SMS keys and the country's `CountryRules.smsSignIn.enabled` is on (default off), with a daily SMS limit per country; a code sent by SMS is 6 digits (owner 2026-11-19; the test code stays 4, `OtpChallenge.codeLength` tells the app), `contract.json#smsSignIn` (0.18.133 and 0.18.134 reserved for S5); after 0.18.132 0.18.132 S7 W2 Q117 + Q118 follow-up, wording only: on the four sign-in / refresh calls an access token is not read (always phone or session + address and the ceilings), and a body that cannot be read counts against the address at its budget (429 when full), `contract.json#rateLimit.key`; after 0.18.131 0.18.131 S7 alert-cap MF3: the admin alert book sends every open safety alert (never cut), at most 1000 other open alerts (Critical first, then the newest) and at most 1000 solved ones, and carries `AlertBookState.alertsMore { open, solved }` only when a part was cut (`contract.json#alertDesk.serverDetection.liveList`); after 0.18.130 0.18.130: `configDocs.keptKeys.driver_app_config` = `realtime.oneStream` (a driver document save that leaves out `realtime` keeps the one-live-connection switch); after 0.18.129 0.18.129 saved-places design: a saved place may carry one fixed ride category, `SavedPlace.preferredCategoryId` (null = none; unknown id 400 `unknown_category`), for now and Later rides; after 0.18.128 S7 W2 Q125, wording only: app streams (rider, driver) are counted per session on each server copy, one opened while 3 are open is answered 200, logged and counted, nothing refused yet (`contract.json#realtime.appStreamsPerSession`); after 0.18.127 S7 W2 Q119, wording only: `rider_trip_changed` is not sent for a GPS update (trip event kind `location`), every other event of the rider's trips still sends it, no app change (`contract.json#bookedRideSeen.riderTripEvent`); after 0.18.126 S7 W2 Q126: the admin alarm feed `GET /admin/incidents/stream` with no cursor starts from the open incidents, not the whole history (`contract.json#safety.feedStart`); after 0.18.125 L20-6 health, wording only: `/readyz` stays 200 with `database: busy` when the database is only slow or full and answers 503 `database_unavailable` only when it is down (`contract.json#fastDispatch.health`), and a late trip-timer or dispatch lane also raises a critical `system_health` alert (`alertDesk.serverDetection.kindDefaults.system_health.laneLate`); after 0.18.124 C10: the driver's ride history from the server, `GET /driver/trips` (own ended trips, paged, `earned` per trip = the earnings entries), `contract.json#driverTripHistory`; after 0.18.123 SF-F1-3 safe config saves: `PUT /admin/config/{doc}` keeps the listed kept keys a save leaves out (`contract.json#configDocs.keptKeys`), optional `removeKeys`, answer `keptKeys`; Restore of country_rules keeps the live payout and debt settings (Q-SCS-2); the alert settings save keeps stored kinds; after 0.18.122 L20 stream: GET /driver/stream carries the offer feed and the driver config stream on one connection (id '<offer sequence>.<config version>'), used only while DriverAppConfig.realtime.oneStream is true (default false, admin switch per zone), `contract.json#driverOneStream`; after 0.18.121 S4 B1.1 SF-1 + SF-2, wording only: a parked `pickup_geofence` job (automatic arrival at the pickup and middle stops, the waiting clock's away / back) runs once more 60 s after it is parked and its system_health alert is critical, as `near_dropoff`, and so does a parked `trip_eta` job (the live ETA tick; SF-2, a session decision under the owner's night rule) (`contract.json#alertDesk.serverDetection.kindDefaults.system_health.rule`); after 0.18.120 S4 B1.16 Q-B13 + B1.18 wording: an Exclusive or hand-sent offer that expired while a server copy's live link was down never counts toward auto-offline (`contract.json#autoOffline.outage`), only Exclusive offers the driver let expire count and a decline never counts nor resets the count (owner 2026-11-16, `contract.json#autoOffline.declined`), and after a LISTEN reconnect the settings streams close within a random 0–30 s (`contract.json#realtime.reconnectClose`); after 0.18.119 S7 W2 Q117 + Q118, wording only: the write limit keys a rightly signed access token that ran out by its user (401, not 429), the code calls by phone + address and the refresh calls by session + address, with phone-alone and address-alone ceilings (fixed server factors), and a number is locked for every address after 4 × `wrongCodesPerDay` wrong codes in 24 h, for up to 24 h, with the admin unlock (`contract.json#rateLimit.key`, `auth.otp.note`); after 0.18.118 the contract text recent jobs owed, wording only plus `country` on config History / Restore: J8b paid-movera rest and the next payout made, the long stop on a repeated fix (10-minute limit, not when moving), the ride-check scan only with the rider on board, the inbox tie-break direction, no call window after the rider's early end; after 0.18.117 S7 notes + alert-cap MF3, wording only: the admin alert list sends every open alert and at most 1000 solved ones, safety kinds first (`contract.json#alertDesk.serverDetection.liveList`), a GPS fix that is not newer writes no `location` event, the ride-check scan is booked on every send, and `POST /driver/location` checks the `Idempotency-Key` but never stores or replays it (`contract.json#driverHome.locationSend`); after 0.18.116 BQ-S10 the rider shares a live trip link: `POST|GET|DELETE /rider/trips/{tripId}/share`, public `GET /api/v1/share/{token}` + `GET /s/{token}` with a fixed allow-list, per-zone `RiderAppConfig.shareTrip.on` (default true), `contract.json#shareTrip`; after 0.18.115 BQ-V21 the rider's approximate pickup entrance chips get an admin on/off per zone, `RiderAppConfig.booking.pickupSpots.on` (default true), `contract.json#pickupSpots`; 0.18.114 not shipped; after 0.18.113 BQ-S13 the call window after the trip is sent as `TripProjection.callOpenUntil` (`contract.json#inAppCalls.callOpenUntil`); after 0.18.112 BQ-A04: the support inbox lists the oldest-waiting ticket first (`SupportTicket.waitingSince`, one cursor over both parts); after 0.18.111 BQ-M28 + BQ-M29: a later bonus or pay change moves Movera gets once, in the payout that pays it (`priceDisplay.payoutSummary.laterBonus` / `laterPayChange`), renumbered from 0.18.107 (stall exit); after 0.18.110 BQ-V44: bonus campaigns per zone (trips or hours online, dates, amount; paid once into the next payout), renumbered from 0.18.103 (stall exit); after 0.18.109 BQ-FLEETCUR a fleet works in one country and earns in one currency, `409 fleet_other_country`, `contract.json#driverOnboarding.fleetInvitations.oneCountry`; after 0.18.108 job C9b auto arrived and the waiting clock at middle stops (CONTRACT.md §93, `contract.json#autoArrive.stops`); after 0.18.106 contract text batch: heading-check setting wording, paid-movera 400 reasons invalid_amount / currency_mismatch; after 0.18.105 BQ-V43 the driver's Android offer push: `GET /push/config?platform=android` gives `androidConfig`, `contract.json#auth.devices.config.android`; after 0.18.102 BQ-V38: approving a payout run carries `expectedCount` + `expectedTotal`, a changed run = 409 `run_changed` with the fresh `PayoutRunCard`; after BQ-V34 the driver's SOS texts his emergency contacts, `contract.json#sosContactsSms`; on top of v0.18.100 BQ-V37 ride-check scan cadence per zone). The server and driver carry
0.18.72; admin and rider carry 0.18.66 (later versions land in them after the merge).

Was (v0.18.99): **0.18.99** (`contract.json#version`, tag `v0.18.99`; 0.18.99 BQ-M25b no cash to collect on a trip not paid in the car, on 0.18.97 (0.18.98 not shipped); after v0.18.96 BQ-M23; J8 wording: a `paid_to_movera` entry is never in `Payout.summary` or fleet earnings, paid-movera closing a payout freezes it).

## What is here

| File | What |
|---|---|
| `contract.json` | Machine-readable source of truth: enums, terminal set, transition table, cancel codes, realtime rules, error codes, currencies, categories, languages, admin dispatch rules, config defaults |
| `CONTRACT.md` | The written contract: entities, lifecycle per app, events, admin control matrix, config documents, API surface, and the notes of every version |
| `openapi.yaml` | REST and realtime surface for the three apps and the server |
| `fixtures/` | Lifecycle scenarios, realtime gate cases, money cases, cancel fees, pickup pay cases, surge schedule cases, fare cases, dispatch timelines, sample config documents (also the server-only pricing and dispatch documents); the apps and the server replay them in their contract tests |
| `reference_check.py` | Reference engine: proves the fixtures agree with `contract.json` |
| `tools/gen_openapi.py` | Generates `openapi.yaml` from `contract.json` plus the hand-written surface |
| `CHECKSUMS` | sha256 of every file above, the list the apps' copy tests read |
| `scripts/` | `verify.sh` (the checks CI runs), `checksums.sh` (rewrites `CHECKSUMS`), `sync.sh` (copies the contract into an app), `check_version_order.py` (the new version is higher than every tag) |
| `docs/` | Audit notes (not part of the contract, not in `CHECKSUMS`) |

## Versions and tags

The version lives in `contract.json#version` and in the first lines of
`CONTRACT.md`. Every released version is a git tag `v<version>` on `main`.
A consumer pins a tag, never `main`.

Version order (2026-11-09, step 21): a new `version` must be higher than every released tag, compared number by
number (0.18.10 > 0.18.9); `scripts/check_version_order.py` fails the PR otherwise. A released or given-up number
(0.18.46) is never reused. After every merge, tag it (`git tag v<version> && git push origin v<version>`).

- Additive change (a new optional field, a new endpoint): patch or minor bump.
- Breaking change (a renamed field, a removed value, a changed transition):
  minor bump at least, named in `CONTRACT.md` with what the apps must do.

## Changing the contract

1. Branch from `main`. Edit `contract.json` and `CONTRACT.md`; regenerate
   `openapi.yaml` with `python3 tools/gen_openapi.py . openapi.yaml`
   (needs `pyyaml`); add or update fixtures for the change.
2. `python3 reference_check.py` must pass. Bump `version`.
3. `scripts/checksums.sh`, then `scripts/verify.sh`.
4. Open a pull request. CI (`.github/workflows/verify.yml`, "Contract checks") runs
   `scripts/verify.sh` on pull requests and on `v*` tags, not on pushes to `main`
   (owner 2026-11-06); drafts are skipped.
5. After the merge, `.github/workflows/tag-release.yml` ("Tag released version") tags
   `v<version>` on the merge commit if that tag is missing (step 21, 2026-11-09). By hand it
   is `git tag v<version> && git push origin v<version>`; `verify.sh` on the tag checks that
   it matches `contract.json#version`.
6. Land the same version in every consumer in one go (Rule 43(4): the copy PRs start right
   after the merge, one per repo): in each consumer run its sync script with the tag
   (`tools/sync_contract.sh v<version>` in the server and the admin, `tool/sync_contract.sh
   v<version>` in the driver and rider apps; each runs this repo's `scripts/sync.sh`) and
   commit `contracts/` exactly as it comes out. Never edit a consumer's `contracts/` by hand.
   The admin panel also bumps `CONTRACT_VERSION` in `webapp/src/domain/contract.ts`. Each
   consumer's "Contract copy" workflow checks the copy on every PR and push, and once a day
   opens or closes the issue "Contract copy behind movera-contracts main".

## Consumers

| Consumer | Copy | Pinned |
|---|---|---|
| `baccarisverige-ux/movera-rider-app` | `contracts/` (`tool/sync_contract.sh`) | v0.18.54 |
| `baccarisverige-ux/Movera-driver-app` | `contracts/` (`tool/sync_contract.sh`) | v0.18.54 |
| `baccarisverige-ux/Admin-panel-movera-dispatch` | `contracts/` (`tools/sync_contract.sh`) + `CONTRACT_VERSION` in `webapp/src/domain/contract.ts` | v0.18.54 |
| `baccarisverige-ux/movera-server` | `contracts/` (`tools/sync_contract.sh`); `test/contract_copy.test.ts` fails on drift | v0.18.54 |

## Working rules

- The owner's memory for the whole project is the Rules repository (`Movera-team/Rules`:
  `RULES.md`, `decisions/`, `plan/`). Read it before changing anything here.
- Rule 25: a hand-written file over 1,500 lines is split first; `contract.json`,
  `openapi.yaml` and `CHECKSUMS` are exempt.
- Rule 21: never delete anything without asking the owner.
- Pull requests use `.github/pull_request_template.md`; security problems go through
  `SECURITY.md` (private reporting), never a public issue.

## Freeze

From the day the server implements a version until the end of the first
real test week, the contract does not change. Changes collected during the
test become the next version, landed in all consumers together.

## History

v0.5.4 to v0.18.63 (October–November 2026): the notes of every version are at the top of
`CONTRACT.md`, newest first.

v0.5.3 (25 October 2026): driver sign-up details, fleets with a join code, the documents each
country and account type needs, uploaded to the server (`§14`). Additive; notes at the top of
`CONTRACT.md`.

v0.5.2 (25 October 2026): the free cars near the rider, for the rider's map while it
chooses a ride (`GET /rider/nearby-vehicles`), with nothing that tells who drives.
Additive; notes at the top of `CONTRACT.md`.

v0.5.1 (24 October 2026): the server-only pricing and dispatch documents with the fare
formula and the automatic dispatch rules as the owner decided them, unpaid cash fees on
the next ride, admin sign-in with e-mail and password and the panel's 34 permissions,
address search and road routes through the server, telemetry, and the admin live map's
driver positions and trip traces. Additive; notes at the top of `CONTRACT.md`.

v0.5.0 (23 October 2026): pickup pay (rider fixed fee, driver tiered ranges with a
maximum per ride), the driver's stopped / driving signal and the Radar limits per
state, the surge schedule (curve over time), sign-in / tokens / push devices with
test numbers outside production, and the meaning of the config document version.
Additive; notes at the top of `CONTRACT.md`.

v0.4.4 is the first commit of this repository: the contract exactly as the
three apps carried it on 23 October 2026 (their copies were byte-identical).
Earlier versions live in the apps' histories; the notes for v0.3 to v0.4.4
are at the top of `CONTRACT.md`.

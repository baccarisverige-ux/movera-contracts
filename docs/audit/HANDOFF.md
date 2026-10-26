# Movera: handoff for the next developer

Date: 2026-10-26. Give this whole file to the next Claude Code session as its first message. It is self-contained: read it fully before touching anything.

---

## 1. The project

Movera is a ride app (rider app, driver app, admin panel, one server) for a test week in **Stockholm county** (Södertälje included) and **Paris**. Tunisia is listed but not open.

| Repo (GitHub owner `baccarisverige-ux`) | What | Live test link |
|---|---|---|
| `movera-contracts` | Shared API contract, now **v0.5.5** | none |
| `movera-server` | Node/TypeScript, Fastify, Kysely, Postgres 16 | https://movera-server.onrender.com (health: `/healthz`) |
| `movera-rider-app` | Flutter | https://baccarisverige-ux.github.io/movera-rider-app/live/ |
| `Movera-driver-app` | Flutter, package `movera` | https://baccarisverige-ux.github.io/Movera-driver-app/live/ |
| `Admin-panel-movera-dispatch` | React 19 + Vite, app in `webapp/` | https://baccarisverige-ux.github.io/Admin-panel-movera-dispatch/live/ |

- The server runs on **Render** (free plan, Frankfurt): `render.yaml` and `docs/DEPLOY_RENDER.md` in `movera-server`. The free plan sleeps when idle; the first request then takes about a minute.
- The apps' live builds are published by each repo's GitHub Pages workflow under `/live/`, pointed at the server by the repo variable `MOVERA_LIVE_API_URL`.
- The contract changes first; then each consumer syncs its copy with `tools/sync_contract.sh <commit>`. Contract checks: `python3 tools/gen_openapi.py . openapi.yaml && python3 reference_check.py && scripts/checksums.sh && scripts/verify.sh`.

### Test accounts (staging only, code `1234`)

| Phone | Account |
|---|---|
| +46 70 174 06 05 | Driver, active, **fleet owner** of "Movera Test AB" (fleet code `MV-TESTA`), Volvo V60 `TST 001`. Owner name / e-mail for a join request: Test Åkare, akare@movera.test |
| +46 70 174 06 06 | Driver, active, same fleet, Toyota Corolla `TST 002` |
| +46 70 174 06 07 | Driver, active, same fleet, Tesla Model 3 `TST 003` |
| +46 70 174 06 08, 09, 10 | Riders, active |

A second code request for the same number within 30 seconds is refused. The test drivers work in every open zone and every category. The admin is the owner's e-mail; the first password link is in Render → movera-server → Logs ("admin password link").

---

## 2. The owner's rules (always)

1. Ask **one question at a time**, with your recommendation first, in plain words. Ask every owner-only question before building a part.
2. **Merge only when CI is green AND the owner writes "merge".** "Ok" is not a merge.
3. **Investigate deeply before each fix and never create new problems**: reproduce with evidence, smallest fix, a test that would have caught it, every CI gate green.
4. Show **screenshots or a mockup before building** a new screen, and screenshots after UI changes.
5. Never ask for the server's root password. No owner e-mail or secrets in git. Never use Uber's car images.
6. Every app text in three languages: Swedish, French, English.

---

## 3. Product decisions already made (do not re-ask)

### Driver sign-up (rounds 4 and 4b, merged)
- Sign-in in **3 steps**: 1 phone, 2 code, 3 details. Same header on all three: Movera wordmark with "Driver" under it. Step 3 is one scrollable white screen.
- **Apple and Google** on step 1. The first time, the phone is still confirmed with a code; afterwards Apple or Google alone signs in. Step 3 is prefilled with the names and e-mail the provider gave, editable. Until the owner's developer keys exist the buttons show "Coming soon" (server answers `503 provider_not_configured`).
- Step 3 fields: first name, last name, date of birth (minimum age **21**), e-mail, country (list with flags; Sweden and France open, Tunisia "coming soon"), city (list: Stockholm län, Paris), language (list of three, no flags; switches the app at once), account type **Driver** or **Fleet**. A fleet adds company name, org number (Sweden 10 digits; France SIREN 9 or SIRET 14), company address. No home address.
- Also: phone shown read-only on step 3; draft kept if the app closes; Back from step 3 signs out; Profile "Your details" stays editable while the account is on hold.
- After step 3 the app opens with the account **on hold** until Movera approves it.

### Documents per country
- Sweden, driver: terms, information session, driving licence, profile photo, taxi driver licence.
- Sweden, fleet: company registration, taxi traffic permit, tax settings (F-skatt), bank statement, plus the owner's own driver documents if the owner drives.
- Sweden, car: registration certificate, insurance.
- France, driver: terms, VTC card, driving licence, ID, profile photo.
- France, fleet: Kbis/SIRENE, VTC operators register certificate, RC pro insurance, URSSAF certificate, manager's ID, company bank statement (RIB).
- France, car: registration (carte grise), insurance, VTC sticker.
- Terms for everyone; information session Sweden only. Real upload to the server, encrypted at rest. Only Movera approves documents and activates accounts; a fleet owner only sees the status.

### Fleets
- The server makes the fleet code (`MV-` + 5 characters) when an admin approves the fleet; an admin can make a new one.
- **Joining is a two-sided invitation**: the driver asks with the code plus the owner's full name and e-mail and the owner accepts or declines; or the owner invites a phone number and the driver accepts or declines (a number without an account gets it when it signs up). Both sides are told in the app (badge on Home and My fleet, notification) and by one SMS. Invitations last 7 days. An admin sees pending ones on the fleet page and may accept or cancel.
- The fleet owner adds cars, an admin approves each, a linked driver picks one car; one car, one driver at a time.
- A fleet driver's money is paid to the fleet. Owner, driver or admin can end the link, never during a trip.

### Money shown to the driver
- The driver sees their own earnings after commission everywhere. **Exception (owner, 2026-10-26): the waybill shows both what the rider pays and what the driver gets.**

---

## 4. Work in progress (pushed to GitHub, NOT merged)

Two branches hold today's live-test fixes. Each has, or will have, a **draft PR** listing per note the finding, cause, fix and test, plus an "Open" list. Finish them in this order, make CI green, then ask the owner for "merge".

### 4.1 Driver app, branch `driver-live-fixes-1`
Done on the branch:
- **N1** Radar offers: the "Toutes les offres" pill above the offer card is removed. The top island keeps its left menu icon and right destination icon with their own actions; only its middle text becomes the radar message (for example "1 offre · radar"), and tapping the middle opens the full-screen radar. It returns to the earnings line by itself when no offers remain. No close button.
- **N5** Google's live traffic layer (green/yellow/red highways) removed from every map; only the owner's map style remains.
- **N9 + N11** After an early finish the screens show the server's final money, not the price from accept. The waybill shows what the rider pays and what the driver gets, and the real rider name, pickup address, driver name and plate (it showed "Passager", raw coordinates, "Chauffeur Movera", "MVR 418").

Still open:
- **N6** Pinch zoom on the trip map: sometimes crashes, sometimes the camera fights the finger or snaps back, sometimes the route line turns very thin.
- **N8** Verify the ride check from the driver side: driver ends the ride early on board; driver completes more than 300 m from the drop-off.

### 4.2 Rider app, branch `rider-live-fixes-1`
- **N3** Go through every booking step on the live web build (iPhone Safari): find what crashes back to Home and what reloads (Movera logo) back to the same page; check Back on every screen. Use the repo's Chromium probes (`tool/web_lifecycle_probe.mjs`), see `docs/web-lifecycle-investigation.md`.
- **N4** During a long search the app suggests adding money, but the raise fails. Server facts: a search lasts 10 minutes, then the trip is `expired` and `POST /trips/{id}/raise-price` is refused; a raise needs status searching or offered, the same currency, an increase above 0, a new fare at most 2× the quote, and the current `expectedVersion`. Find which one the app hits. If the owner wants a raise after expiry, that is a contract and server change: ask first.
- **N5** Remove the traffic layer (`waiting_for_driver.dart` sets `trafficEnabled: true`; `web/rider_map_camera.js` re-attaches a TrafficLayer when it reuses a map).
- **N6** On Select ride with pickup and destination a few metres apart, the camera tilts to street level at building zoom and the route becomes a huge green wedge. Lock tilt to 0, cap the zoom (about 17), give tiny routes a minimum map span. Also the pinch-zoom faults while searching.
- **N7** Right after sign-in, Home shows a wrong address for a second, then corrects: the default map point is looked up before the first GPS fix. Show nothing or the last known position until the fix arrives.
- **N8** Verify the ride check end to end from the rider side.
- **N9** Early finish shows the full booked price. Show the server's final fare: kilometres plus minutes on board, never below the minimum fare, never above the booked fare (the server computes it, fare line `minimum_adjust`).
- **N10** After a driver cancel or a no-show, the end sheet gets a primary **"Search again"** button that re-requests the same trip (same pickup, destination, category, payment) and goes straight to searching; "Back to Home" becomes secondary. Also: no "connection lost" banner over a finished trip, and the sheet behind must not still say "driver almost there".

### 4.3 Server: nothing open
`main` is green (568 tests). Round 4b added: fleet invitations, in-app notifications (`GET /notifications`), an SMS outbox, Apple/Google sign-in with link tokens (migration `0012_invitations.sql`).

---

## 5. What the owner still has to do

1. **Render → movera-server → Environment: add `OSRM_URL` = `https://router.project-osrm.org`** (or Blueprints → Manual Sync). Without it the rider map draws straight lines (note N2). If the logs then say "OSRM unavailable; distance estimated", the public demo router is too slow and Movera needs its own OSRM.
2. Render: `GOOGLE_MAPS_API_KEY`, for address search.
3. Apple and Google developer accounts, then `APPLE_CLIENT_IDS` and `GOOGLE_CLIENT_IDS` on Render.
4. Choose an SMS provider (46elks recommended for Sweden, or Twilio). Until then only the test numbers can sign in, and SMS wait in the `sms_outbox` table.
5. Send the testers' real phone numbers (they are seeded like `src/drivers/seedTest.ts`).
6. For the real test week, move Render to paid plans (no sleeping, no expiring database).

---

## 6. Later backlog

- Driver app contract copy is still v0.5.3 (pinned by its tests); sync to v0.5.5.
- Fleet earnings screen in the driver app; open an uploaded document file; re-check the account status periodically.
- Admin fee and payout screens; refund destination for riders.
- Long-term host: the owner's Oxahost server (access by SSH key, never by password).
- Deep audit of all apps before the testers start.

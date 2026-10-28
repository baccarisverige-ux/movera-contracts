# Movera — handoff to the next Claude session (2026-10-28)

Read this file first, then `docs/audit/PROGRESS.md` (same branch `audit/owner-rule-check-all`), which holds every owner decision word for word.

## OWNER RULES (always)
1. Before ANY decision or change: check the server, the contract and ALL apps (rider, driver, admin) and the owner's demo screens. Look for conflicts. Then ask the owner simple questions, ONE at a time, each written as "SECTION / SITUATION / QUESTION" with 2 clear options and a recommendation. Never decide alone; never build from your own ideas.
2. Show screenshots of EVERY changed screen before asking to merge. Merge only after the owner's explicit OK.
3. The admin live panel must be an exact copy of the owner's demo admin; add/remove/adjust only after asking.
4. Driver app shows the driver only totals, never breakdowns (exceptions decided: Ride completed = Trip total · Movera commission · You get; waybill = Rider pays · Your earnings).
5. All texts sv/fr/en. No secrets or owner e-mail in git. Never ask for the server root password. Low-entropy fake values in tests (full-history gitleaks scan).
6. Explain in very plain words; the owner is on a phone and gets angry at unclear questions.

## Repos (owner baccarisverige-ux)
movera-contracts, movera-server (Render: srv-dbf8pmdg1s2s73et26vg, https://movera-server.onrender.com), movera-rider-app, Movera-driver-app, Admin-panel-movera-dispatch (app in webapp/). Live test apps: https://baccarisverige-ux.github.io/{movera-rider-app,Movera-driver-app,Admin-panel-movera-dispatch}/live/

## Done and merged
Audit phases 1–8 (final report: docs/audit/FINAL_REPORT.md on main). After that: driver Ride completed 3 lines + waybill totals + routes via server + radar pulse only online (driver #391); rider "Search again" after expiry (#428); zone-limited rider list (server #24); SAFETY PART 1 — rider/driver SOS (112 + alert Movera), driver toolkit Option A, ride-check Call 112 alerts Movera, server incidents + "car lost" + 2-min escalation (contracts #20 v0.7.0, server #26, rider #429, driver #392). Server on Render runs 99f78c9 (safety).

## Open work — all built, CI green, NOT merged (owner must see screenshots and say OK)
Merge order: 1 Pricing → 2 Settings flow → 3 Real data. Each later branch must merge the earlier one in (no rebase/force) and fix conflicts (server config code; migration numbers 0021/0022 may need renumbering; contract versions 0.7.1 → 0.8.x → 0.9.x).
1. PRICING: contracts #19 (pricing/v0.6, now 0.7.1), server #25, rider #432 (stacked on #430), driver #395; admin branch owner/live-pricing-exact (2d9b663, includes owner/live-equals-demo 43fe997). Screenshots: scratchpad pricing-final/. 4 small choices built with the recommended option, owner not yet confirmed: surge max = slider value up to ×6, no hidden limit; "Är du säker?" above 3× Movera price or >50 % change; smart-surge demand = requests in the last check window ÷ free drivers; surge notice to online drivers of that zone only.
2. SETTINGS FLOW (part 2): contracts #21, server #27 (both settings/flow → pricing/v0.6), rider #430, driver #393; admin on owner/live-equals-demo (43fe997). Publish applies only to the zones chosen at the top. OPEN QUESTION: Tips & limits — whole country (recommended, current) or per chosen zone? Not done: Content page publish, app contract copies still 0.5.x, Dispatch "Save draft"/"Undo".
3. REAL DATA (part 3): contracts #22 (v0.9.0), server #28, rider #431, driver #394; admin branch owner/live-realdata (5fe9263). One admin CI job (demo Playwright e2e) fails; same specs fail on base; log not readable here. Screenshots: scratchpad realdata/.
4. ADMIN live = exact demo copy: branch owner/live-equals-demo (all 33 sections, 7 re-added live features, one search box, SOS cases + alarm). No PR yet. Owner wants Dispatch = ONE section built from the whole Dashboard + what only Dispatch has (no separate Dashboard) — not built yet; check first.

## Next steps (in this order, asking the owner as you go)
1. Ask the open questions above (Tips & limits; the 4 pricing choices).
2. Show Pricing screenshots (live vs demo per tab, rider Child Seat card, driver "Framme vid stoppet", surge notice); on OK merge Pricing (#19, #25, then #395, then #432 after #430).
3. Same for part 2, then part 3.
4. Then the admin PR from owner/live-equals-demo (+ pricing + realdata branches) after the owner checks all 33 sections.
5. Remaining build order the owner chose: (4) refunds without second admin + manual-refund list + audit page (partly in part 3), (5) the rest: driver activation needs approved documents+car, onboarding documents = contract list, zones from server, server status words everywhere, chat only support roles in their zones, reports real money, Dispatch merged section. Safety part 2 = ride-check answers open incidents.

## Owner actions pending
Render paid plan; rotate the 2 Google Maps keys found in git history; add a restricted Maps test key as GitHub secret; turn on branch protection and Dependabot; send testers' phone numbers; SMS provider; Apple/Google ids. Admin password: Render → Environment → add ADMIN_PASSWORD_RESET with a NEW value → Save, rebuild, deploy → Logs, search "link" (last 7 days too). Owner said "forget about pass now".

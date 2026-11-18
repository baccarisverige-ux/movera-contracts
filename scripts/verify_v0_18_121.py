#!/usr/bin/env python3
"""v0.18.121 (S4 B1.1 SF-1; owner 2026-11-16 "Yes, same as drop-off (Rec.)", Rules decisions/session-2026-11-06.md,
audits/impact/s4-b101-supervisor.md SF-1): the system_health rule names pickup_geofence among the trip kinds that are
critical when parked and run once more 60 s after parking (as near_dropoff), says why its restart is safe, keeps the
released text (Rule 21) and changes nothing else in alertDesk. Same version, round 4 (SF-2; OQ-B101-2 "Yes, restart once
+ urgent alert (Rec.)", a session decision under the owner's night rule 2026-11-16, the owner reviews it): trip_eta too,
with why its restart never pushes twice, never takes a booked ride back twice and never doubles the tick. Run by
scripts/verify.sh from the repository root (own file, Rule 25)."""
import json
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 121), 'version 0.18.121 or later'

sh = c['alertDesk']['serverDetection']['kindDefaults']['system_health']
# A later version may add its own key after these three (its text starts with its version, > 0.18.121; e.g. 0.18.125 laneLate).
assert list(sh)[:3] == ['level', 'rule', 'ruleBefore0_18_121'] and all(isinstance(sh[k], str) and sh[k].startswith('v0.18.') and int(sh[k][len('v0.18.'):].split(' ')[0]) > 121 for k in list(sh)[3:]), 'system_health: only ruleBefore0_18_121 added (later versions add their own keys after it)'
assert sh['level'] == 'important', 'system_health level unchanged'
r, before = sh['rule'], sh['ruleBefore0_18_121']
assert 'withdraw_driver_offers, dispatch_round, pickup_geofence, trip_eta), otherwise critical from 10.' in r, 'pickup_geofence and trip_eta critical (loud) when parked'
assert '(all listed kinds except ride_check_no_answer and withdraw_driver_offers) runs once more 60 s' in r, 'pickup_geofence restarts once (listed, not excepted)'
assert "pickup_geofence since 0.18.121, S4 B1.1 SF-1, owner 2026-11-16 'Yes, same as drop-off (Rec.)'" in r, 'source'
assert 'automatic arrival at the pickup' in r and "waiting clock's away / back from GPS (paid waiting)" in r and 'automatic arrival at the middle stops' in r, 'the three uses'
assert 'locks the trip and re-checks its status' in r and 'positionMaxAgeSeconds' in r and '2-fix confirm' in r and 'a restart never arrives twice' in r, 'why the restart is safe'
assert 'parks it for good (no loop)' in r and 'solved at the next sweep' in r and 'dispatch_round since 0.18.73, server B1.14' in r, 'the rest kept'
assert 'pickup_geofence' not in before and 'withdraw_driver_offers, dispatch_round), otherwise critical from 10.' in before, 'released text kept'
assert r.replace('withdraw_driver_offers, dispatch_round, pickup_geofence, trip_eta)', 'withdraw_driver_offers, dispatch_round)').split('; pickup_geofence since 0.18.121')[0] == before.split('). Failing again')[0], 'only the kind and its sentence added (head)'
assert r.split('the apps show the straight-line estimate). ')[1] == before.split('only makes it wait). ')[1], 'only the kinds and their sentences added (tail)'
# Round 4 (SF-2): trip_eta, between the pickup_geofence sentence and the closing bracket.
e = r.split('so a restart never arrives twice; ')[1].split('). Failing again')[0]
assert e.startswith("trip_eta since 0.18.121 too, S4 B1.1 SF-2, a session decision under the owner's night rule, 2026-11-16 'Yes, restart once + urgent alert (Rec.)', which the owner reviews"), 'trip_eta: source, marked as a session decision'
assert 'pickupWaiting.eta' in e and "'almost there' push (riderTripPush, driver_arriving)" in e and 'take a late booked ride back (bookedTakeBack)' in e, 'trip_eta: what the tick does'
assert 'locks the trip and re-reads where the car is going first' in e and 'once per driver' in e and 'a ride taken back has no driver' in e and 'a failed run leaves nothing behind' in e and 'a trip has one tick' in e, 'trip_eta: why the restart is safe'
assert 'never pushes twice, never takes a ride back twice and never doubles the tick' in e and e.endswith('the apps show the straight-line estimate'), 'trip_eta: the three promises, the fallback'
assert r.count('trip_eta') == 2 and 'trip_eta' not in before, 'trip_eta only in the list and its sentence'
for k in ('pickupWaiting', 'riderTripPush', 'bookedTakeBack'):
    assert k in c, 'the rule names contract.json#' + k
assert 'driver_arriving' in json.dumps(c['riderTripPush']), 'riderTripPush has driver_arriving'

t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.130: the v0.18.121 note moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.121 (S4 B1.1 SF-1 + SF-2;' in tc and 'follows v0.18.120)' in tc, 'CONTRACT.md v0.18.121 note'
assert '`ruleBefore0_18_121`' in tc, 'CONTRACT.md names the kept text (its note in CHANGELOG.md since v0.18.130)'
n121 = next(l for l in tc.split('\n') if l.startswith('v0.18.121 ('))
assert 'a parked `trip_eta` job' in n121 and "a session decision under the owner's night rule" in n121 and 'never doubles the tick' in n121, 'CONTRACT.md note: round 4 trip_eta'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.121 pickup_geofence and trip_eta restart-once and loud ok')

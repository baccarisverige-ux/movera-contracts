#!/usr/bin/env python3
"""v0.18.121 (S4 B1.1 SF-1; owner 2026-11-16 "Yes, same as drop-off (Rec.)", Rules decisions/session-2026-11-06.md,
audits/impact/s4-b101-supervisor.md SF-1): the system_health rule names pickup_geofence among the trip kinds that are
critical when parked and run once more 60 s after parking (as near_dropoff), says why its restart is safe, keeps the
released text (Rule 21) and changes nothing else in alertDesk. Run by scripts/verify.sh from the repository root (own
file, Rule 25)."""
import json
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 121), 'version 0.18.121 or later'

sh = c['alertDesk']['serverDetection']['kindDefaults']['system_health']
assert list(sh) == ['level', 'rule', 'ruleBefore0_18_121'], 'system_health: only ruleBefore0_18_121 added'
assert sh['level'] == 'important', 'system_health level unchanged'
r, before = sh['rule'], sh['ruleBefore0_18_121']
assert 'withdraw_driver_offers, dispatch_round, pickup_geofence), otherwise critical from 10.' in r, 'pickup_geofence critical (loud) when parked'
assert '(all listed kinds except ride_check_no_answer and withdraw_driver_offers) runs once more 60 s' in r, 'pickup_geofence restarts once (listed, not excepted)'
assert "pickup_geofence since 0.18.121, S4 B1.1 SF-1, owner 2026-11-16 'Yes, same as drop-off (Rec.)'" in r, 'source'
assert 'automatic arrival at the pickup' in r and "waiting clock's away / back from GPS (paid waiting)" in r and 'automatic arrival at the middle stops' in r, 'the three uses'
assert 'locks the trip and re-checks its status' in r and 'positionMaxAgeSeconds' in r and '2-fix confirm' in r and 'a restart never arrives twice' in r, 'why the restart is safe'
assert 'parks it for good (no loop)' in r and 'solved at the next sweep' in r and 'dispatch_round since 0.18.73, server B1.14' in r, 'the rest kept'
assert 'pickup_geofence' not in before and 'withdraw_driver_offers, dispatch_round), otherwise critical from 10.' in before, 'released text kept'
assert r.replace('withdraw_driver_offers, dispatch_round, pickup_geofence)', 'withdraw_driver_offers, dispatch_round)').split('; pickup_geofence since 0.18.121')[0] == before.split('). Failing again')[0], 'only the kind and its sentence added (head)'
assert r.split('so a restart never arrives twice). ')[1] == before.split('only makes it wait). ')[1], 'only the kind and its sentence added (tail)'

t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.121 (S4 B1.1 SF-1;' in t and 'follows v0.18.120)' in t, 'CONTRACT.md v0.18.121 note'
assert '`ruleBefore0_18_121`' in t, 'CONTRACT.md names the kept text'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.121 pickup_geofence restart-once and loud ok')

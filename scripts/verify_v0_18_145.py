#!/usr/bin/env python3
"""v0.18.145 (S4c load cut; contract.json#loadCut): GET /driver/home-badges, the airport_queue_changed hint, the rider
trip-watch fallback, the nearby-cars cache note, the CONTRACT.md note and the v0.18.139 note (launch restack; the draft moved v0.18.127) moved word for word to
CHANGELOG.md (Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 145), 'version 0.18.145 or later'
lc = c['loadCut']
for k in ('note', 'homeBadges', 'airportQueueLive', 'riderTripWatch', 'nearbyCache'):
    assert k in lc, 'loadCut.' + k
assert lc['airportQueueFallbackSeconds'] == 60 and lc['riderTripWatchStreamUpSeconds'] == 60, 'fallbacks'
assert c['bookedRideSeen'] and 'never a driver id' in lc['nearbyCache'], 'cache keeps blurred positions only'
o = yaml.safe_load(open('openapi.yaml'))
g = o['paths']['/driver/home-badges']['get']
assert g['operationId'] == 'getDriverHomeBadges' and g['x-actor'] == ['driver'], 'route'
sc = o['components']['schemas']
assert set(sc['DriverHomeBadges']['required']) == {'profile', 'notifications', 'reminders', 'onboardingSettings'}, 'badges shape'
assert sc['AirportQueueChangedEvent']['properties']['kind']['const'] == 'airport_queue_changed', 'hint kind'
for p in ('/driver/profile', '/notifications', '/driver/reminders', '/driver/onboarding/settings', '/driver/airport-queue'):
    assert 'get' in o['paths'][p], p + ' stays (additive)'
assert 'airport_queue_changed' in o['paths']['/driver/config/stream']['get']['description'], 'stream doc'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.145 (S4c load cut' in t, 'CONTRACT.md note'
import hashlib
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
assert 'follows v0.18.144)' in next(l for l in (t + ch).split('\n') if l.startswith('v0.18.145 (S4c load cut,')), 'v0.18.145 note follows v0.18.144 (launch restack)'
# launch restack (plan K): this version moves the v0.18.139 note (the draft moved v0.18.127)
n139 = next(l for l in cl if l.startswith('v0.18.139 (driver wallet D5; owner butto'))
assert '\n' + n139 not in t and cl.count(n139) == 1, 'v0.18.139 note moved once'
assert hashlib.sha256(n139.encode()).hexdigest() == '3093a325755ec799bddb1a7bfd18926194eec51f00700c3ac914058cd6f6d444', 'v0.18.139 note moved word for word'
j = cl.index(n139)
assert cl[j - 2].startswith('v0.18.145 (load cut; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '4fb02ff62cdd309df33ff58c1192c266b5fea6d24705266783b27c2d29a859ae', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.139 and before (the v0.18.139 note moved in v0.18.145, the v0.18.136 note in v0.18.144, the v0.18.134' in t + ch, 'new pointer line (in CHANGELOG.md once a later version moves it)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.145 load cut ok')

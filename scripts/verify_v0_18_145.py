#!/usr/bin/env python3
"""v0.18.145 (S4c load cut; contract.json#loadCut): GET /driver/home-badges, the airport_queue_changed hint, the rider
trip-watch fallback, the nearby-cars cache note, the CONTRACT.md note and the v0.18.127 note moved word for word to
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
assert '\nv0.18.127 (' not in t, 'v0.18.127 note moved'
ch = open('CHANGELOG.md', encoding='utf-8').read().split('\n')
n127 = next(l for l in ch if l.startswith('v0.18.127 (S7 W2 Q119, plan 0.21;'))
assert ch.count(n127) == 1 and ch[ch.index(n127) - 2].startswith('v0.18.145 (load cut; Rule 21 / Rule 25'), 'CHANGELOG move'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.145 load cut ok')

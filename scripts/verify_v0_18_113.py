#!/usr/bin/env python3
"""v0.18.113 (BQ-S13; owner 2026-11-01 "Keep call open for 1 hour but not chat", Rules decisions/driver-g9.md:38,
conversation/session-2026-11-01b.md:108): the trip says until when the rider and the driver can still call each other
after the drop-off (TripProjection.callOpenUntil); chat stays closed. Run by scripts/verify.sh from the repository root
(own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 113), 'version 0.18.113 or later'
ic = c['inAppCalls']
co = ic['callOpenUntil']
assert 'driver-g9.md:38' in co and 'Keep call open for 1 hour but not chat' in co, 'callOpenUntil owner note'
assert 'trips.ended_at + ' in co and 'CountryRules.calls.callWindowAfterTripMin' in co and 'read when the trip is served' in co, 'callOpenUntil formula, read live'
assert 'completed trip' in co and 'calls.on is true' in co and 'absent' in co and 'cancelled trip' in co, 'callOpenUntil only on a completed trip with calls on'
assert 'GET /trips/{tripId}' in co and 'GET /rider/trips' in co, 'callOpenUntil: where it is served'
assert 'the same instant the server checks' in co and 'call_window_closed' in co, 'callOpenUntil = the server window'
assert "'Call rider'" in co and "'Call driver'" in co and 'hides by itself' in co and 'absent → no call button' in co, 'callOpenUntil: apps'
assert 'Chat stays closed' in co and 'no new setting' in co and 'Call window after the trip (min)' in co, 'chat closed; admin setting exists'
assert ic['window'].startswith('Open from driver assignment (tripStatus.driverAssigned) until callWindowAfterTripMin') and 'v0.18.113' in ic['window'], 'window points to callOpenUntil'
assert c['configDefaults']['calls']['callWindowAfterTripMin'] == 60 and ic['settings']['ranges']['callWindowAfterTripMin'] == [0, 240], 'default 60, 0-240 unchanged'
spec = yaml.safe_load(open('openapi.yaml'))
assert spec['info']['version'] == c['version'], 'openapi version'
S = spec['components']['schemas']
p = S['TripProjection']['properties']['callOpenUntil']
assert p['type'] == 'string' and p['format'] == 'date-time' and 'v0.18.113' in p['description'], 'TripProjection.callOpenUntil'
assert 'callOpenUntil' not in S['TripProjection']['required'], 'callOpenUntil optional (additive)'
assert 'callOpenUntil' in spec['paths']['/trips/{tripId}']['get']['description'], 'GET /trips/{tripId} names callOpenUntil'
assert 'callOpenUntil' in spec['paths']['/rider/trips']['get']['description'], 'GET /rider/trips names callOpenUntil'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.117: the v0.18.109-v0.18.115 notes moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.113 (BQ-S13' in tc, 'CONTRACT.md v0.18.113 note'
w = t[t.index('## 62. In-app calls'):t.index('## 63.')]
assert '`TripProjection.callOpenUntil`' in w and 'v0.18.113' in w, 'CONTRACT.md §62 names callOpenUntil'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print("v0.18.113 call window after the trip ok")

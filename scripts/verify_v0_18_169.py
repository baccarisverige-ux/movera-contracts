#!/usr/bin/env python3
"""v0.18.169 (the rider's trip view keeps the route line; Finding leaves on any status past searching; owner 2026-11-27
"App rider blocked here", "Oui, corriger"): contract.json#riderTripRouteLine, openapi TripProjection.routePolyline (optional,
rider only, until the trip ends, no extra Google call), the CONTRACT.md note and the v0.18.164 note moved word for word to
CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh (Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 169), 'version 0.18.169 or later'
g = c['riderTripRouteLine']
assert g['since'] == '0.18.169', 'since'
for k in ('note', 'trip', 'calls', 'findingExit', 'rider', 'driver', 'admin'):
    assert isinstance(g[k], str) and g[k], k
assert 'Sent only in the rider' in g['trip'] and 'in realtime events' in g['trip'] and 'terminal status' in g['trip'], 'rider only, until the trip ends'
assert 'No extra Google call' in g['calls'], 'no extra call'
assert 'any status past searching, completed included' in g['findingExit'], 'Finding exit rule'
assert 'never treated as the rider' in g['findingExit'] and 'never starts the search again' in g['findingExit'], 'not a cancel'
assert '#12201C' in g['rider'] and '#2FBF5B' in g['rider'], 'Movera colours'
spec = yaml.safe_load(open('openapi.yaml'))
t = spec['components']['schemas']['TripProjection']
p = t['properties']['routePolyline']
assert p['type'] == 'string' and p['minLength'] == 1 and 'routePolyline' not in t.get('required', []), 'optional'
assert p['description'].startswith('v0.18.169 (contract.json#riderTripRouteLine): '), 'description'
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
assert "\nv0.18.169 (the rider's route line and the Finding screen after a reopen;" in md + ch, 'note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert 'v0.18.169 (rider trip route line; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch, 'CHANGELOG move line'
assert '\nv0.18.164 (France document lists;' in ch, 'v0.18.164 note in CHANGELOG.md'
print('v0.18.169 ok')

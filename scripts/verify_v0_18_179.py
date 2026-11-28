#!/usr/bin/env python3
"""v0.18.179 (the driver's booked rides draw the real road route; owner 2026-11-28): contract.json#reservationRouteLine,
openapi DriverReservation.routePolyline (optional, no extra Google call), the CONTRACT.md note and the v0.18.168 note moved
word for word to CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh (Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 179), 'version 0.18.179 or later'
g = c['reservationRouteLine']
assert g['since'] == '0.18.179', 'since'
for k in ('note', 'reservation', 'calls', 'driver', 'rider', 'admin'):
    assert isinstance(g[k], str) and g[k], k
assert 'GET /driver/reservations' in g['reservation'] and 'trips.route_polyline' in g['reservation'], 'source'
assert 'No extra Google call' in g['calls'], 'no extra call'
assert 'never a line' in g['driver'] and 'never asks GET /routes/driving' in g['driver'], 'no straight line'
assert 'DriverRouteStyle' in g['driver'], 'same route colour'
spec = yaml.safe_load(open('openapi.yaml'))
t = spec['components']['schemas']['DriverReservation']
p = t['properties']['routePolyline']
assert p['type'] == 'string' and p['minLength'] == 1 and 'routePolyline' not in t.get('required', []), 'optional'
assert p['description'].startswith('v0.18.179 (contract.json#reservationRouteLine): '), 'description'
assert '/driver/reservations' in spec['paths'], 'path'
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'title'
assert "\nv0.18.179 (the driver's booked rides draw the real road route;" in md + ch, 'note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert 'v0.18.179 (booked-ride route line; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch
assert "\nv0.18.169 (the rider's route line and the Finding screen after a reopen;" in ch, 'v0.18.169 note in CHANGELOG.md'
assert 'the v0.18.169 note moved in v0.18.179' in md, 'pointer'
print('v0.18.179 ok')

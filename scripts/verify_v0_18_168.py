#!/usr/bin/env python3
"""v0.18.168 (the driver's offer card draws the real Google route; owner 2026-11-26 "Route in driver !!"):
contract.json#offerRouteLine, openapi Offer.routePolyline (optional, open offers only, no extra Google call), the CONTRACT.md
note and the v0.18.163 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh (Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 168), 'version 0.18.168 or later'
g = c['offerRouteLine']
assert g['since'] == '0.18.168', 'since'
for k in ('note', 'offer', 'calls', 'driver', 'rider', 'admin'):
    assert isinstance(g[k], str) and g[k], k
assert 'only on an open offer' in g['offer'] and 'Not in the offer push' in g['offer'], 'open offers, not in push'
assert 'No extra Google call' in g['calls'], 'no extra call'
spec = yaml.safe_load(open('openapi.yaml'))
o = spec['components']['schemas']['Offer']
p = o['properties']['routePolyline']
assert p['type'] == 'string' and p['minLength'] == 1 and 'routePolyline' not in o['required'], 'Offer.routePolyline optional'
assert p['description'].startswith('v0.18.168 (contract.json#offerRouteLine): '), 'description'
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
assert "\nv0.18.168 (the driver's offer card draws the real Google route;" in md + ch, 'note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert 'v0.18.168 (offer route line; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch, 'CHANGELOG move line'
assert '\nv0.18.163 (live traffic for trip times; owner 2026-11-25' in ch, 'v0.18.163 note in CHANGELOG.md'
print('v0.18.168 ok')

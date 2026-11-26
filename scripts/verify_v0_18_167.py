#!/usr/bin/env python3
"""v0.18.167 (the rider map draws the real Google route; owner 2026-11-26 "Oui, corriger"): contract.json#googleRouteLine,
openapi Quote.routePolyline (optional, only when routeSource is google, no extra Google call), the CONTRACT.md note and the
v0.18.162 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh from the repository root
(own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 167), 'version 0.18.167 or later'
g = c['googleRouteLine']
assert g['since'] == '0.18.167', 'since'
for k in ('note', 'quote', 'calls', 'rider', 'driver', 'admin'):
    assert isinstance(g[k], str) and g[k], k
assert 'only when Quote.routeSource is google' in g['quote'], 'only google'
assert 'No extra Google call' in g['calls'], 'no extra call'
assert 'Approximate route' in g['rider'] and 'fallback' in g['rider'], 'rider + fallback'
spec = yaml.safe_load(open('openapi.yaml'))
q = spec['components']['schemas']['Quote']
p = q['properties']['routePolyline']
assert p['type'] == 'string' and p['minLength'] == 1 and 'routePolyline' not in q['required'], 'Quote.routePolyline optional string'
assert p['description'].startswith('v0.18.167 (contract.json#googleRouteLine): '), 'description'
md = open('CONTRACT.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
assert '\nv0.18.167 (the rider map draws the real Google route;' in md + open('CHANGELOG.md', encoding='utf-8').read(), 'note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert 'v0.18.167 (Google route line; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch, 'CHANGELOG move line'
assert '\nv0.18.162 (driver country first; owner 2026-11-25' in ch, 'v0.18.162 note in CHANGELOG.md'
print('v0.18.167 ok')

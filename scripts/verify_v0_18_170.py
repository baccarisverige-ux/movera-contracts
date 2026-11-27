#!/usr/bin/env python3
"""v0.18.170 (the rider's waiting-for-driver and on-trip maps draw the stored Google road line, 0 extra Google calls):
contract.json#riderLegRouteLine, openapi TripProjection.legRoute (optional, rider only, current leg only, until the trip
ends), the CONTRACT.md note and the v0.18.165 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25).
Run by scripts/verify.sh (Rule 25)."""
import json, re, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 170), 'version 0.18.170 or later'
g = c['riderLegRouteLine']
assert g['since'] == '0.18.170', 'since'
for k in ('note', 'trip', 'calls', 'rider', 'driver', 'admin'):
    assert isinstance(g[k], str) and g[k], k
assert 'Sent only in the rider' in g['trip'] and 'in realtime events' in g['trip'] and 'terminal status' in g['trip'], 'rider only, until the trip ends'
assert "only when its target is the trip's current leg" in g['trip'] and 'never in command answers' in g['trip'], 'current leg, no command answers'
assert 'trips.eta_route' in g['trip'], 'stored ETA route'
assert 'No extra Google call' in g['calls'] and 'POST /routes is unchanged' in g['calls'], 'no extra call'
assert '#12201C' in g['rider'] and '#2FBF5B' in g['rider'], 'Movera colours'
spec = yaml.safe_load(open('openapi.yaml'))
t = spec['components']['schemas']['TripProjection']
p = t['properties']['legRoute']
assert p['type'] == 'object' and 'legRoute' not in t.get('required', []), 'optional object'
assert p['required'] == ['target', 'polyline'] and p['additionalProperties'] is False, 'shape'
assert p['properties']['target']['enum'] == ['pickup', 'dropoff'], 'target enum'
assert p['properties']['polyline']['type'] == 'string' and p['properties']['polyline']['minLength'] == 1, 'polyline'
assert p['description'].startswith('v0.18.170 (contract.json#riderLegRouteLine): '), 'description'
assert 'routePolyline' in t['properties'], 'v0.18.169 field kept'
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
assert "\nv0.18.170 (the rider's waiting-for-driver and on-trip maps draw the stored Google road line;" in md + ch, 'note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert 'v0.18.170 (rider leg route line; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch, 'CHANGELOG move line'
assert '\nv0.18.165 (sign-in code 60 s;' in ch, 'v0.18.165 note in CHANGELOG.md'
paths = spec['paths']
named = set(re.findall(r'(?:GET|POST|PUT|PATCH|DELETE) (/[A-Za-z0-9_/{}-]+)', g['trip'] + ' ' + g['calls']))
assert named, 'trip names its reads'
for path in named:
    assert path in paths, 'path not in openapi: ' + path
    dep = any(isinstance(op, dict) and op.get('deprecated') for op in paths[path].values())
    if dep:
        assert ('deprecated alias GET ' + path) in g['trip'], 'deprecated path not named as the alias: ' + path
print('v0.18.170 ok')

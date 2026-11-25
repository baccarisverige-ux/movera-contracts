#!/usr/bin/env python3
"""v0.18.163 (live traffic for trip times; owner 2026-11-25 "Google trafic réel"): contract.json#liveTraffic (provider,
route sources, fallback, uses, setting, defaults, rider, apps), Quote.tripSeconds / tripMeters / routeSource and
DispatchDocument.liveTraffic in openapi, the CONTRACT.md note and the v0.18.158 note moved word for word to
CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 163), 'version 0.18.163 or later'
lt = c['liveTraffic']
assert lt['since'] == '0.18.163' and lt['provider'] == 'google_traffic', 'provider'
assert lt['routeSources'] == ['google', 'osrm', 'estimate'], 'sources'
assert 'TRAFFIC_AWARE' in lt['request'] and 'routes.duration,routes.distanceMeters' in lt['request'] and 'never logged' in lt['request'], 'request'
assert lt['fallback'].startswith('google -> osrm -> estimate') and 'system_health:live_traffic' in lt['fallback'], 'fallback'
assert 'stay on OSRM' in lt['uses'], 'ETA choice documented'
assert lt['defaultOnCountries'] == ['SE', 'FR'] and 'DispatchDocument.liveTraffic' in lt['setting'], 'setting'
assert 'Driver app: not affected' in lt['apps'] and 'placeholder 600' in lt['rider'], 'apps'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
q = S['Quote']
assert q['properties']['routeSource']['enum'] == ['google', 'osrm', 'estimate'], 'Quote.routeSource'
for k in ('tripSeconds', 'tripMeters', 'routeSource'):
    assert k not in q['required'], 'Quote.' + k + ' optional'
d = S['DispatchDocument']
assert d['properties']['liveTraffic']['required'] == ['on'] and 'liveTraffic' not in d['required'], 'DispatchDocument.liveTraffic'
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
assert '\nv0.18.163 (live traffic for trip times;' in md + ch, 'CONTRACT.md note'
assert 'v0.18.163 (live traffic; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch, 'CHANGELOG move line'
assert '\nv0.18.158 (crash catcher;' in ch, 'v0.18.158 note moved'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.163 live traffic: ok')

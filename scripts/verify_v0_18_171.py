#!/usr/bin/env python3
"""v0.18.171 (Google road lines on key screens; owner 2026-11-27 "Google on key screens"): contract.json#googleRoadLines,
OsrmRouteResponse.source, TripEta.legRoute (rider location events only), DispatchDocument.liveTraffic.roadLines (1..4,
default 4, the quote included), the daily Google budget (GET/PUT /admin/maps/google-budget), the 0.18.170 text reworded,
the CONTRACT.md note and the v0.18.166 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25).
Run by scripts/verify.sh (Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 171), 'version 0.18.171 or later'
g = c['googleRoadLines']
assert g['since'] == '0.18.171'
for k in ('note', 'navigation', 'offRouteRule', 'trust', 'source', 'codeRule', 'calls', 'counter', 'atCap', 'spacing', 'dailyBudget', 'dayBoundary', 'budgetSetting', 'budgetAlert', 'quotaExceeded', 'riderEvent', 'setting', 'driver', 'rider', 'admin'):
    assert isinstance(g[k], str) and g[k], k
assert g['offRouteMeters'] == 50 and '50 m' in g['offRouteRule'], '50 m rule'
assert 'the quote call INCLUDED' in g['calls'] and 'starts at 1' in g['calls'] and 'default 4' in g['calls'], 'cap includes the quote'
assert 'outside trips.eta_route' in g['counter'] and 'ONE update' in g['counter'], 'counter'
assert 'never jumps to the straight-line estimate' in g['atCap'], 'at cap'
assert 'trips.eta_route.at' in g['spacing'] and 'best effort per copy' in g['spacing'], '60 s rule'
assert 'SUM over all countries' in g['dailyBudget'] and '1400' in g['dailyBudget'] and '600' in g['dailyBudget'] and '2000' in g['dailyBudget'], 'budget'
assert 'America/Los_Angeles' in g['dayBoundary'], 'day'
assert 'system_health:google_routes_budget:<CC>' in g['budgetAlert'] and "every country's alert book" in g['budgetAlert'] and 'system_health:live_traffic:<CC>' in g['budgetAlert'], 'alerts'
assert '429' in g['quotaExceeded'] and 'RESOURCE_EXHAUSTED' in g['quotaExceeded'], 'quota'
assert '150 m' in g['trust'] and 'driver_locations' in g['trust'], 'trust'
assert 'code stays Ok' in g['codeRule'], 'Q1'
assert "Never on the driver's or admin's copy" in g['riderEvent'], 'rider only'
assert '1..4, default 4' in g['setting'], 'range'
assert '#12201C' in g['rider'] and 'no blue' in g['driver'], 'colours'
r = c['riderLegRouteLine']
assert 'tripBefore171' in r and 'TripEta.legRoute' in r['trip'] and 'never for the driver or admin' in r['trip'], '0.18.170 reworded'
assert 'never calls Google' in c['liveTraffic']['navigation'], 'old navigation kept (Rule 21)'
spec = yaml.safe_load(open('openapi.yaml'))
sc = spec['components']['schemas']
assert sc['OsrmRouteResponse']['properties']['source']['enum'] == ['google', 'stored', 'estimate']
assert 'source' not in sc['OsrmRouteResponse'].get('required', [])
lr = sc['TripEta']['properties']['legRoute']
assert lr['required'] == ['target', 'polyline'] and lr['additionalProperties'] is False and 'legRoute' not in sc['TripEta'].get('required', [])
rl = sc['DispatchDocument']['properties']['liveTraffic']['properties']['roadLines']
m = rl['properties']['maxCallsPerTrip']
assert m['minimum'] == 1 and m['maximum'] == 4, 'maxCallsPerTrip 1..4'
b = sc['GoogleRoutesBudget']
assert b['properties']['dailyLimit']['maximum'] == 100000 and sc['GoogleRoutesBudgetCommand']['properties']['dailyLimit']['maximum'] == 100000, 'raise by admin only'
assert 'invalid_budget' in g['budgetSetting'] and 'not_all_countries' in g['budgetSetting'], 'PUT errors'
assert 'with nothing saved it answers the defaults' in g['budgetSetting'], 'GET defaults'
assert c['liveTraffic']['navigationFrom171'] == 'see googleRoadLines.navigation' and 'googleRoadLines.calls' in c['liveTraffic']['callsFrom171'], 'pointers'
p = spec['paths']['/admin/maps/google-budget']
assert p['get']['x-permission'] == 'settings.read' and p['put']['x-permission'] == 'settings.publish'
assert 'v0.18.171' in spec['paths']['/routes/driving/{coordinates}']['get']['description']
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'title'
assert '\nv0.18.171 (Google road lines on key screens;' in md + ch, 'note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert 'v0.18.171 (Google road lines; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch and '\nv0.18.166 (sign-up pro v2 + document scan;' in ch
assert 'the v0.18.166 note moved in v0.18.171' in md, 'pointer'
print('v0.18.171 ok')

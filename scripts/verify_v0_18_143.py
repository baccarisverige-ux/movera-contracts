#!/usr/bin/env python3
"""v0.18.143 (owner 2026-11-20 "must rider can change !!!!"): the rider changes the route while searching. Checks the
change_route transition, onTrip.routeChange.whileSearching with its texts, the scenarios, the openapi fields, the
CONTRACT.md note and section line and the v0.18.127 note moved word for word (Rule 25). Run by scripts/verify.sh."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 143), 'version 0.18.143 or later'
rows = [t for t in c['transitions'] if t['command'] == 'change_route']
assert len(rows) == 1 and rows[0]['actor'] == 'rider' and rows[0]['from'] == ['requested', 'searching', 'offered'] and rows[0]['to'] == 'searching' and rows[0]['when'] == 'live', 'change_route row'
ws = c['onTrip']['routeChange']['whileSearching']
assert ws['statuses'] == rows[0]['from'] and ws['kind'] == 'live', 'whileSearching statuses'
for key in ('riderConfirmNewPrice', 'adminEvent'):
    assert set(ws['texts'][key]) == {'en', 'sv', 'fr'}, key
ids = {s['id'] for s in json.load(open('fixtures/scenarios.json'))['scenarios']}
assert {'change_route_while_searching', 'change_route_scheduled_refused'} <= ids, 'scenarios'
spec = yaml.safe_load(open('openapi.yaml'))
sc = spec['components']['schemas']
assert 'pickup' in sc['RouteQuote']['properties'] and 'pickup' in sc['TripRouteChange']['properties'] and sc['TripRouteChange']['properties']['reason']['enum'] == ['rider_changed_route'], 'openapi fields'
t = open('CONTRACT.md', encoding='utf-8').read()
assert '\nv0.18.143 (owner 2026-11-20 "must rider can change !!!!"' in t and '- **While searching** (v0.18.143' in t, 'CONTRACT.md'
assert 'v0.18.127 and before (the v0.18.127 note moved in v0.18.143,' in t and '\nv0.18.127 (S7 W2 Q119' not in t, 'pointer'
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert ch.count('\nv0.18.127 (S7 W2 Q119, plan 0.21;') == 1, 'v0.18.127 note in CHANGELOG.md once'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.143 change route while searching ok')

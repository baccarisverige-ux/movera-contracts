#!/usr/bin/env python3
"""v0.18.143 (owner 2026-11-20 "must rider can change !!!!"): the rider changes the route while searching. Checks the
change_route transition, onTrip.routeChange.whileSearching with its texts, the scenarios, the openapi fields, the
CONTRACT.md note and section line and the v0.18.134 and v0.18.133 notes moved word for word (Rule 25). Run by scripts/verify.sh."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 143), 'version 0.18.143 or later'
rows = [t for t in c['transitions'] if t['command'] == 'change_route']
assert len(rows) == 1 and rows[0]['actor'] == 'rider' and rows[0]['from'] == ['requested', 'searching', 'offered'] and rows[0]['to'] == 'searching' and rows[0]['when'] == 'live', 'change_route row'
ws = c['onTrip']['routeChange']['whileSearching']
assert "keeps the booked zone's pricing" in ws['zone'] and 'service_not_available' in ws['zone'], 'whileSearching.zone'
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
import hashlib
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
assert 'follows v0.18.141)' in next(l for l in (t + ch).split('\n') if l.startswith('v0.18.143 (owner 2026-11-20')), 'v0.18.143 note follows v0.18.141 (launch restack)'
# launch restack (plan K): this version moves the v0.18.134 and v0.18.133 notes (the draft moved v0.18.127); two notes, because it adds one CONTRACT.md line and the file is at its 1,500-line limit (Rule 25)
n134 = next(l for l in cl if l.startswith('v0.18.134 (account deletion E1; owner bu'))
assert '\n' + n134 not in t and cl.count(n134) == 1, 'v0.18.134 note moved once'
assert hashlib.sha256(n134.encode()).hexdigest() == 'd4ad93a47a1f87d480f20c23666e2b898b59858929e69f5a9837950cb3ae136a', 'v0.18.134 note moved word for word'
j = cl.index(n134)
assert cl[j - 2].startswith('v0.18.143 (change route while searching; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '3ef6973534d68083bee01787ca5597a4ff859bbfeb4c790df6405363e945bf7a' and cl[j + 2].startswith('v0.18.133 (') and '\n' + cl[j + 2] not in t, 'v0.18.133 note moved word for word too (this version adds a CONTRACT.md line, so two notes move; CHANGELOG.md keeps the CONTRACT.md order)'
assert hashlib.sha256(cl[j + 4].encode()).hexdigest() == '5b501b14c085cd32b7bb2f980631d6d5e0ea9e8d7302b5692ecc67f5751970f5', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.134 and before (the v0.18.134 and v0.18.133 notes moved in v0.18.143, the v0.18.132 note in v0.18.141' in t + ch, 'new pointer line (in CHANGELOG.md once a later version moves it)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.143 change route while searching ok')

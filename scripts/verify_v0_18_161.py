#!/usr/bin/env python3
"""v0.18.161 (admin cars and fleets by zone and country; owner 2026-11-25 "Yes, fix it"): GET /admin/vehicles and
GET /admin/fleets in adminListFilters.lists with zoneId / zoneIds / country, the car-zone rule, Vehicle.zoneId /
Vehicle.country / Fleet.zoneId, the openapi copy, the CONTRACT.md note and the v0.18.156 note moved word for word to
CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 161), 'version 0.18.161 or later'
f = c['adminListFilters']
for p in ('GET /admin/vehicles', 'GET /admin/fleets'):
    assert p in f['lists'] and p in f['total']['lists'], p
z = f['carZones']
assert z['since'] == '0.18.161', 'since'
assert "its fleet's zone; else (a car with no fleet) its driver's first zone" in z['carZone'] and 'else none (null)' in z['carZone'], 'car zone rule'
assert 'left out as soon as zoneId, zoneIds or country is given' in z['noZone'], 'no zone excluded'
assert 'zone_out_of_scope' in z['existingZoneId'], 'zoneId documented'
assert 'never as SE' in z['panel'] and 'unknown_filter' in z['panel'] and 'rows without zoneId' in z['panel'], 'panel'
assert 'Driver app: not affected' in z['apps'] and 'Rider app: not affected' in z['apps'], 'apps'
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']
want = [{'$ref': '#/components/parameters/' + n} for n in ('ListZoneId', 'ListZoneIds', 'ListCountry')]
for path in ('/admin/vehicles', '/admin/fleets'):
    op = P[path]['get']
    for w in want:
        assert op['parameters'].count(w) == 1, (path, w)
    assert {'$ref': '#/components/parameters/ZoneIdQuery'} not in op['parameters'], path
    assert [p for p in op['parameters'] if p.get('name') == 'country'] == [], path + ' one country'
    assert 'v0.18.161 (adminListFilters.carZones)' in op['description'] and '403' in op['responses'], path
for k in ('zoneId', 'country'):
    v = S['Vehicle']['properties'][k]
    assert {'type': 'null'} in v['oneOf'] and k not in S['Vehicle']['required'], 'Vehicle.' + k
assert S['Fleet']['properties']['zoneId']['allOf'] == [{'$ref': '#/components/schemas/Id'}] and 'zoneId' not in S['Fleet']['required'], 'Fleet.zoneId'
md = open('CONTRACT.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
assert '\nv0.18.161 (admin cars and fleets by zone and country;' in md, 'CONTRACT.md note'
assert '`kpis` and (v0.18.161) `vehicles` and `fleets` take' in md, '§7'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert 'v0.18.161 (admin cars by zone; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch, 'CHANGELOG move line'
n156 = next(l for l in ch.split('\n') if l.startswith('v0.18.156 (iOS push;') and 'moved from' not in l)
assert '\n' + n156 not in md, 'v0.18.156 note moved'
assert 'Check what happened' in z['noCountry'] and c['alertDesk']['kindGroups']['car_no_country'] == 'system' and c['alertDesk']['serverDetection']['kindDefaults']['car_no_country']['level'] == 'important', 'noCountry + alert'
assert 'vehicleId' in c['alertDesk']['serverDetection']['kindDefaults']['car_no_country']['rule'], 'alert ref'
print('v0.18.161 admin cars by zone: ok')

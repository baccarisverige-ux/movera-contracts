#!/usr/bin/env python3
"""v0.18.172 (driver preferred areas; owner 2026-11-27/28): contract.json#preferredAreas, Area, Driver.preferredAreaIds /
preferredAreas, DriverReservation.inPreferredArea, GET /driver/areas/search, POST /driver/areas/at, PUT /driver/preferred-areas,
GET/PATCH /admin/areas, DriverAppConfig.reservations.preferredAreasMax (1..30, default 10), the CONTRACT.md note and the
v0.18.167 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh (Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 172), 'version 0.18.172 or later'
p = c['preferredAreas']
assert p['since'] == '0.18.172'
for k in ('note', 'maxPerDriver', 'area', 'search', 'at', 'put', 'addressInput', 'order', 'visibility', 'driverView', 'admin', 'driver', 'rider', 'seed'):
    assert isinstance(p[k], str) and p[k], k
assert p['kinds'] == ['kommun', 'stadsdelsomrade', 'city', 'arrondissement', 'commune', 'departement']
assert set(p['areaRank']) == set(p['kinds']) and p['areaRank']['stadsdelsomrade'] < p['areaRank']['kommun'] and p['areaRank']['arrondissement'] < p['areaRank']['city'] < p['areaRank']['departement'] and p['areaRank']['commune'] < p['areaRank']['departement']
assert p['searchLimit'] == 20 and p['searchMinChars'] == 1 and p['addressMinChars'] == 3 and p['addressDebounceMs'] == 250
assert 'never stores the point, never logs it at any level' in p['at'] and 'area null' in p['at'] and 'invalid_point' in p['at'], 'GM edit 2'
assert 'too_many_areas' in p['maxPerDriver'] and 'area_not_found' in p['put'] and 'no address text, no point' in p['put']
assert 'never who may see a ride' in p['note'] and 'homeNear' in p['visibility'] and 'stays (Rule 21)' in p['visibility']
assert 'No OSM' in p['sources']['osm'] and 'CC0' in p['sources']['SE'] and 'Licence Ouverte 2.0' in p['sources']['FR']
for t in ('outlineNote', 'attribution'):
    assert set(p[t]) == {'en', 'fr', 'sv'} and all(p[t].values()), t
assert 'zones.read' in p['admin'] and 'zones.edit' in p['admin'] and 'settings.edit' in p['admin'], 'GM edit 4'
assert c['configDefaults']['reservations']['preferredAreasMax'] == 10
assert 'homeNear still uses Driver.homeArea' in c['bookLater']['listTo']['rules']
assert 'v0.18.172 (preferred areas' in c['configDefaults']['reservations']['note']
spec = yaml.safe_load(open('openapi.yaml'))
sc = spec['components']['schemas']
a = sc['Area']
assert a['required'] == ['areaId', 'name', 'kind', 'kindLabel', 'zoneId', 'country'] and a['additionalProperties'] is False
assert 'polygons' not in a['properties'] and 'polygon' not in a['properties'], 'no polygon to the apps'
assert sc['Driver']['properties']['preferredAreaIds']['type'] == 'array' and sc['Driver']['properties']['preferredAreas']['items'] == {'$ref': '#/components/schemas/Area'}
assert 'preferredAreaIds' not in sc['Driver'].get('required', [])
assert sc['DriverReservation']['properties']['inPreferredArea']['type'] == 'boolean' and 'inPreferredArea' not in sc['DriverReservation']['required']
m = sc['DriverReservations']['properties']['preferredAreasMax']
assert m['minimum'] == 1 and m['maximum'] == 30 and m['default'] == 10
assert sc['AreaAt']['required'] == ['area', 'containing']
assert set(sc['PreferredAreasCommand']['properties']) == {'areaIds'} and sc['PreferredAreasCommand']['additionalProperties'] is False, 'ids only'
paths = spec['paths']
at = paths['/driver/areas/at']
assert 'get' not in at and at['post']['requestBody']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/AreaAtCommand'}, 'point in the body, not the URL (GM)'
assert sc['AreaAtCommand']['required'] == ['lat', 'lng'] and sc['AreaAtCommand']['additionalProperties'] is False
assert 'never in the URL' in p['at'] and '?lat=' not in json.dumps(c['preferredAreas'])
assert 'put' in paths['/driver/preferred-areas'] and 'put' in paths['/driver/home-area'], 'home-area kept (Rule 21)'
assert paths['/admin/areas']['get']['x-permission'] == 'zones.read' and paths['/admin/areas/{areaId}']['patch']['x-permission'] == 'zones.edit'
assert 'v0.18.172' in paths['/driver/reservations']['get']['description']
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'title'
assert '\nv0.18.172 (driver preferred areas;' in md + ch, 'note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert 'v0.18.172 (preferred areas; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch and '\nv0.18.167 (the rider map draws the real Google route;' in ch
assert 'the v0.18.167 note moved in v0.18.172' in md, 'pointer'
print('v0.18.172 ok')

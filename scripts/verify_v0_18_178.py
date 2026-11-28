#!/usr/bin/env python3
"""v0.18.178 (car make/model picker; owner 2026-11-28): contract.json#carCatalogue, CarCatalogue, the admin catalogue paths
(no DELETE), optional makeId / modelId on VehicleRequest / Vehicle / AdminVehicleUpdate, fixtures/car_catalogue.json (slug
ids, vehicle cases, accent-insensitive search) and the v0.18.169 note moved word for word to CHANGELOG.md (Rule 21 / 25).
Run by scripts/verify.sh (Rule 25)."""
import json, re, unicodedata, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 178), 'version 0.18.178 or later'
p = c['carCatalogue']
assert p['since'] == '0.18.178'
for k in ('note', 'ids', 'driverRead', 'vehicleIds', 'adminVehicle', 'admin', 'seed', 'search', 'pickerClose', 'source', 'driver', 'rider'):
    assert isinstance(p[k], str) and p[k], k
assert 'makeId/modelId null means the driver typed it (Annat)' in p['note'] and 'never refuses a car' in p['note']
assert 'ON CONFLICT (id) DO NOTHING' in p['seed'] and 'never writes name or hidden' in p['seed'], 'GM 3'
assert 'never changed by a rename' in p['ids'], 'GM 4'
assert 'clears make_id AND model_id' in p['adminVehicle'], 'GM 6c'
assert 'hidden rows included' in p['admin'] and 'make_exists' in p['admin'] and 'never changed' in p['admin'] and 'No DELETE' in p['admin'], 'GM 6a/b'
assert 'changes nothing' in p['pickerClose'] and 'Only when NOTHING matches' in p['pickerClose'], 'GM 1'
assert 'CC-BY 4.0' in p['source'] and set(p['attribution']) == {'en', 'fr', 'sv'} and all('CC BY 4.0' in v for v in p['attribution'].values()), 'GM 2'
spec = yaml.safe_load(open('openapi.yaml'))
sc, paths = spec['components']['schemas'], spec['paths']
assert sc['CarCatalogue']['required'] == ['version', 'attribution', 'makes'] and sc['CarCatalogue']['additionalProperties'] is False
for n in ('VehicleRequest', 'Vehicle', 'AdminVehicleUpdate'):
    pr = sc[n]['properties']
    assert 'makeId' in pr and 'modelId' in pr and 'makeId' not in sc[n].get('required', []), n
assert sc['VehicleRequest']['properties']['make']['type'] == 'string' and 'enum' not in sc['VehicleRequest']['properties']['make'], 'no enum'
assert 'get' in paths['/driver/car-catalogue'] and '304' in paths['/driver/car-catalogue']['get']['responses']
assert paths['/admin/car-catalogue']['get']['x-permission'] == 'drivers.read'
for pth, m in (('/admin/car-catalogue/makes', 'post'), ('/admin/car-catalogue/makes/{makeId}/models', 'post'),
               ('/admin/car-catalogue/makes/{makeId}', 'patch'), ('/admin/car-catalogue/models/{modelId}', 'patch')):
    assert paths[pth][m]['x-permission'] == 'vehicles.edit', pth
for pth, item in paths.items():
    if 'car-catalogue' in pth: assert 'delete' not in item, 'Rule 21: no delete ' + pth
assert 'v0.18.178' in paths['/admin/vehicles/{vehicleId}']['patch']['description']
def slug(x):
    x = unicodedata.normalize('NFKD', x.replace('+', ' plus ')).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', x).strip('-')
fx = json.load(open('fixtures/car_catalogue.json'))
for name, want in fx['slugCases']:
    assert slug(name) == want, (name, slug(name), want)
idre = re.compile(r'^[a-z0-9][a-z0-9.-]{0,79}$')
seen = set()
for m in fx['catalogue']['makes']:
    assert m['makeId'] == slug(m['name']) and idre.match(m['makeId'])
    for md in m['models']:
        assert md['modelId'] == m['makeId'] + '.' + slug(md['name']) and md['modelId'] not in seen
        seen.add(md['modelId'])
def key(x): return unicodedata.normalize('NFKD', x).encode('ascii', 'ignore').decode().lower()
for q, want in fx['search']:
    assert [m['name'] for m in fx['catalogue']['makes'] if key(q) in key(m['name'])] == want, q
assert any(v.get('error', {}).get('reason') == 'unknown_make' for v in fx['vehicleCases'])
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'title'
assert '\nv0.18.178 (car make/model picker;' in md + ch, 'note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert 'v0.18.178 (car catalogue; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch and "\nv0.18.169 (the rider's route line" in ch
assert 'the v0.18.169 note moved in v0.18.178' in md, 'pointer'
print('v0.18.178 ok')

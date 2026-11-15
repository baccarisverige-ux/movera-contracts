#!/usr/bin/env python3
# v0.18.105 (BQ-V43; G4 decision 1, owner R7, Rules decisions/driver-g4.md:2, driver-g2.md:61): the driver's Android
# store build gets push: GET /push/config?platform=android gives the Firebase Android app's public settings.
# Kept out of verify.sh (Rule 25: scripts/ files <= 1,500 lines); run by verify.sh from the repository root.
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 105), 'version 0.18.105 or later'
a = c['auth']['devices']['config']['android']
assert 'driver-g4.md:2' in a['note'] and 'androidConfig' in a['note'] and 'never a secret' in a['note'], 'android note'
assert a['platforms'] == ['web', 'android', 'ios'], 'platforms'
assert set(c['auth']['devices']['platforms']) == set(a['platforms']), 'same platforms as POST /push/devices'
assert a['androidPackages'] == {'driver': 'se.movera.driver', 'rider': 'com.movera.rider'}, 'packages'
assert 'APNs' in a['ios'] and 'enabled false' in a['ios'], 'ios waits for APNs'
n = c['driverOffers']['push']['native']
assert 'androidChannel' in a['appStart'] and n['androidChannel'] == 'movera_offers' and n['androidQuietChannel'] == 'movera_offers_quiet', 'channels'
for w in ('Contract', 'Server', 'Admin', 'Driver app', 'Rider app'):
    assert w in a['apps'], 'Rule 0 part ' + w
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert S['PushConfig']['properties']['androidConfig']['allOf'] == [{'$ref': '#/components/schemas/PushWebConfig'}], 'PushConfig.androidConfig'
assert 'androidConfig' not in S['PushConfig']['required'], 'androidConfig optional'
ps = [p for p in spec['paths']['/push/config']['get']['parameters'] if p.get('name') == 'platform']
assert len(ps) == 1 and ps[0]['required'] is False and ps[0]['schema']['enum'] == a['platforms'], 'platform query'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.105 (BQ-V43' in t and 'androidConfig' in t, 'CONTRACT.md v0.18.105'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert spec['info']['version'] == c['version'], 'openapi version'
print("v0.18.105 ok")

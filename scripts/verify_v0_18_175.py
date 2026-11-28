#!/usr/bin/env python3
"""v0.18.175 (PIN per zone + the rider's own PIN; owner 2026-11-28): contract.json#pinPerZone, openapi
RiderAppConfig.features.pin description, Rider.safety / RiderProfileUpdate.safety { pinAlways }, TripProjection.pinSource,
fixtures/pin_per_zone.json follows the rule, the CONTRACT.md note and the v0.18.169 note moved word for word to
CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh (Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 175), 'version 0.18.175 or later'
g = c['pinPerZone']
assert g['since'] == '0.18.175', 'since'
for k in ('note', 'riderConfigFeature', 'riderChoice', 'bookingRule', 'pinSource', 'rider', 'driver', 'admin', 'oldApps'):
    assert isinstance(g[k], str) and g[k], k
assert g['sources'] == ['zone', 'rider', 'both'], 'sources'
assert 'OR rider.safety.pinAlways' in g['bookingRule'] and 'never changes a booked trip' in g['bookingRule'], 'booking rule'
for k in ('riderSwitch', 'riderSwitchHelp', 'riderAreaNote', 'driverTypeCodeFirst', 'adminRiderLine', 'adminTripWhy', 'adminOldSwitch'):
    for lang in ('sv', 'fr', 'en'):
        assert g['texts'][k][lang], k + ' ' + lang
assert g['texts']['riderSwitch']['sv'] == 'PIN på alla mina resor', 'owner-OK rider switch text'
assert g['texts']['driverTypeCodeFirst']['sv'] == 'Skriv resenärens kod först', 'driver hint'
spec = yaml.safe_load(open('openapi.yaml'))
sch = spec['components']['schemas']
assert sch['RiderAppConfig']['properties']['features']['properties']['pin']['type'] == 'boolean', 'features.pin stays a boolean'
assert 'pickupPin.required' in sch['RiderAppConfig']['properties']['features']['properties']['pin']['description'], 'features.pin source'
assert sch['Rider']['properties']['safety'] == {'$ref': '#/components/schemas/RiderSafety'}, 'Rider.safety'
assert sch['RiderSafety']['required'] == ['pinAlways'] and sch['RiderSafety']['additionalProperties'] is False, 'RiderSafety'
assert sch['RiderProfileUpdate']['properties']['safety'] == {'$ref': '#/components/schemas/RiderSafetyUpdate'}, 'update safety'
assert 'safety' not in sch['RiderProfileUpdate'].get('required', []), 'safety optional'
assert sch['TripProjection']['properties']['pinSource']['enum'] == g['sources'], 'pinSource'
assert 'pinSource' not in sch['TripProjection'].get('required', []), 'pinSource optional'
f = json.load(open('fixtures/pin_per_zone.json'))
assert f['since'] == '0.18.175' and len(f['cases']) >= 7
for case in f['cases']:
    zone = case['zoneOwn'] if case['zoneOwn'] is not None else (case['standard'] if case['standard'] is not None else False)
    assert case['featuresPin'] == zone, case['name'] + ': features.pin = the zone'
    req = zone or case['pinAlways']
    assert case['pinRequired'] == req, case['name'] + ': pinRequired = zone OR rider'
    src = ('both' if zone and case['pinAlways'] else 'zone' if zone else 'rider') if req else None
    assert case['pinSource'] == src, case['name'] + ': pinSource'
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'title'
assert "\nv0.18.175 (PIN per zone + the rider's own PIN;" in md + ch and '`contract.json#pinPerZone`' in md, 'notes'
assert '\nv0.18.169 (' not in md and '\nv0.18.169 (' in ch, 'v0.18.169 note moved'
assert md.count('\n') <= 1500, 'CONTRACT.md at most 1500 lines'
print('v0.18.175 pinPerZone ok')

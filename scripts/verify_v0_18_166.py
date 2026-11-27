#!/usr/bin/env python3
"""v0.18.166 (sign-up pro v2 + document scan; owner 2026-11-26 "Oui, tout construire", "I approve it", "Peut pas"):
contract.json#signupV2, PUT /driver/country cityId, personalNumber / taxiLicenseNumber, OnboardingSettings.signUpFields
and twoSidedTypes, profile_photo_locked, the notes and the v0.18.161 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25).
Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 166), 'version 0.18.166 or later'
sv = c['signupV2']
assert sv['since'] == '0.18.166'
assert sv['infoScreen']['order'][:2] == ['country', 'region'], 'Pays then Région first'
assert '+46 = SE, +33 = FR' in sv['infoScreen']['countryFromPhone'] and 'ALREADY granted' in sv['infoScreen']['countryFromPhone']
f = sv['signUpFields']
for cc in ('SE', 'FR'):
    assert set(f['defaults'][cc]) == set(f['fields']), cc + ' signUpFields defaults'
assert f['defaults']['SE']['personalNumber'] == {'on': True, 'required': True}
assert f['defaults']['FR']['dateOfBirth'] == {'on': True, 'required': True}
assert set(sv['twoSided']['defaults']) == {'SE', 'FR'} and 'driving_license' in sv['twoSided']['defaults']['FR']
types = c['driverOnboarding']['documents']['types']
for cc, ts in sv['twoSided']['defaults'].items():
    for t in ts: assert t in types and types[t]['kind'] == 'file', t
assert set(sv['accountTypeLabels']) >= set(c['driverOnboarding']['accountTypes']), 'labels map the existing accountType'
assert sv['accountTypeLabels']['fleet']['fr'] == 'Chauffeur avec Kbis' and sv['accountTypeLabels']['driver']['sv'] == 'Förare utan eget företag'
assert 'profile_photo_locked' in sv['profilePhoto']['locked'] and 'Peut pas' in sv['profilePhoto']['note']
spec = yaml.safe_load(open('openapi.yaml'))
sc = spec['components']['schemas']
assert 'cityId' in sc['DriverCountryCommand']['properties'] and sc['DriverCountryCommand']['required'] == ['country']
for k in ('personalNumber', 'taxiLicenseNumber'):
    assert k in sc['DriverOnboardingRequest']['properties'] and k not in sc['DriverOnboardingRequest']['required'], k
    assert k in sc['Driver']['properties'], k
assert {'signUpFields', 'twoSidedTypes'} <= set(sc['OnboardingSettings']['properties'])
assert 'profile_photo_locked' in spec['paths']['/driver/documents']['post']['description']
# v0.18.171 (Rule 25): the v0.18.166 note moved word for word to CHANGELOG.md; it is checked in both files.
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v0.18.166') or tuple(map(int, c['version'].split('.'))) > (0, 18, 166), 'title'
assert '\nv0.18.166 (sign-up pro v2 + document scan;' in md + ch and 'the v0.18.161 note moved in v0.18.166' in md
assert 'v0.18.166 (sign-up pro v2; Rule 21 / Rule 25' in ch and '\nv0.18.161 (admin cars and fleets by zone and country;' in ch
assert f['defaults']['SE']['address'] == f['defaults']['FR']['address'] == {'on': True, 'required': True}, 'address required SE + FR'
assert sv['infoScreen']['order'].index('address') > sv['infoScreen']['order'].index('personalNumber')
assert set(sc['DriverAddress']['required']) == {'street', 'postalCode', 'city'} and 'address' in sc['DriverOnboardingRequest']['properties'] and 'address' not in sc['DriverOnboardingRequest']['required']
assert 'post' in spec['paths']['/admin/drivers/{driverId}/address'], 'admin address route'
assert "Oui, ajouter l'adresse" in sv['address']['owner'] and 'driver.address' in md + ch
print('v0.18.166 sign-up v2 ok')

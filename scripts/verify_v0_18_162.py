#!/usr/bin/env python3
"""v0.18.162 (driver country first; owner 2026-11-25 "Yes"): contract.json#driverCountryFirst, the alert kind
driver_no_country, PUT /driver/country, POST /admin/drivers/{driverId}/country, country_required on POST /driver/vehicles,
the CONTRACT.md note and the v0.18.157 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25). Run by
scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 162), 'version 0.18.162 or later'
d = c['driverCountryFirst']
assert d['since'] == '0.18.162', 'since'
assert 'PUT /driver/country' in d['step']['route'] and 'country_not_open' in d['step']['route'], 'step'
assert 'details_locked' in d['step']['when'] and 'fleet_other_country' in d['step']['when'], 'step when'
assert 'read-only' in d['step']['onboarding'] and 'fleet_other_country' in d['step']['onboarding'], 'onboarding'
assert d['required']['reason'] == 'country_required' and 'POST /driver/vehicles' in d['required']['rule'], 'required'
a = d['adminSet']
assert 'POST /admin/drivers/{driverId}/country' in a['route'] and 'drivers.activate' in a['route'], 'admin route'
assert 'zone_out_of_scope' in a['scope'] and 'on_trip' in a['rules'] and 'reason_required' in a['rules'], 'admin rules'
assert 'driver.country' in a['audit'] and 'pending' in a['cars'], 'audit + cars'
assert '0137' in d['oneTimeFix'] and 'driver_no_country' in d['oneTimeFix'], 'one-time fix'
assert 'Rider app: not affected' in d['apps'] and 'Which country do you work in?' in d['apps'], 'apps'
ad = c['alertDesk']
assert ad['kindGroups']['driver_no_country'] == 'system' and ad['serverDetection']['kindDefaults']['driver_no_country']['level'] == 'important', 'alert'
assert 'car_no_country' in ad['kindGroups'], 'car_no_country kept'
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']
assert P['/driver/country']['put']['requestBody']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/DriverCountryCommand'}, 'PUT /driver/country'
o = P['/admin/drivers/{driverId}/country']['post']
assert o['x-permission'] == 'drivers.activate' and set(S['AdminDriverCountryCommand']['required']) == {'expectedVersion', 'country', 'reason'}, 'admin op'
assert 'country_required' in P['/driver/vehicles']['post']['description'], 'vehicles'
assert 'v0.18.162' in P['/driver/onboarding']['post']['description'], 'onboarding'
md = open('CONTRACT.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
assert '\nv0.18.162 (driver country first;' in md, 'CONTRACT.md note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert 'v0.18.162 (driver country first; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch, 'CHANGELOG move line'
n157 = next(l for l in ch.split('\n') if l.startswith('v0.18.157 (SMS sign-in for every country;'))
assert '\n' + n157 not in md, 'v0.18.157 note moved'
print('v0.18.162 driver country first: ok')

#!/usr/bin/env python3
"""v0.18.159 (fleet needs a car; owner 2026-11-24, Rules decisions/driver-g2.md "Fleet owner must add a car"): the reminder
fleet_no_car (fleet owner, zero cars, any fleet status, gated by X-Contract-Version), the per-country setting
OnboardingSettings.fleetNeedsCarForApproval (default true), the 409 fleet_has_no_car on fleet approval, the texts in
sv / fr / en, the openapi copy, the CONTRACT.md note and the v0.18.150 note moved word for word to CHANGELOG.md (Rule 21 /
Rule 25). Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 159), 'version 0.18.159 or later'
f = c['fleetNeedsCar']
assert f['since'] == '0.18.159', 'since'
assert 'fleet_has_no_car' in f['refusal'] and '409 invalid_transition' in f['refusal'] and 'rejected / blocked are never refused' in f['refusal'], 'refusal'
assert 'default true' in f['setting'] and 'Admin › Drivers › Onboarding' in f['setting'], 'setting'
assert 'Rider: not affected' in f['apps'], 'rider not affected'
rm = c['driverOnboarding']['reminders']
k = rm['kinds']['fleet_no_car']
assert k.startswith('v0.18.159') and 'blocks_online' in k and 'FLEET OWNER' in k and 'ZERO cars' in k and 'whatever the fleet' in k, 'kind'
assert 'fix fleet_vehicles' in k and 'Never sent to a member' in k and 'X-Contract-Version 0.18.159 or later' in k, 'kind fix / gate'
assert 'fleet_no_approved_car is not sent' in k and 'account_not_active is not sent' in k, 'kind one car line'
assert 'nor while a fleet_no_car line is sent' in rm['kinds']['account_not_active'], 'account_not_active'
assert 'fleet_vehicles' in rm['fixTargets'], 'fix target'
for t in ('fleet_no_car', 'fleet_no_car_body', 'fleet_add_car', 'fleet_not_approved', 'fleet_not_approved_body', 'fleet_cars_empty', 'fleet_cars_empty_body'):
    assert set(rm['texts'][t]) == {'sv', 'fr', 'en'}, t
assert rm['texts']['fleet_no_car']['en'] == 'Add your first car' and rm['texts']['fleet_not_approved_body']['en'] == 'We review it after your car and documents are in.', 'mockup words'
for cc, d in c['driverOnboarding']['settings']['defaults'].items():
    assert d['fleetNeedsCarForApproval'] is True, 'default on ' + cc
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']
assert 'fleet_no_car' in S['DriverReminder']['properties']['kind']['enum'], 'openapi kind'
o = S['OnboardingSettings']['properties']['fleetNeedsCarForApproval']
assert o['type'] == 'boolean' and o['default'] is True and 'fleetNeedsCarForApproval' not in S['OnboardingSettings'].get('required', []), 'openapi setting'
assert 'v0.18.159 (fleetNeedsCar)' in P['/admin/fleets/{fleetId}/review']['post']['description'] and 'fleet_has_no_car' in P['/admin/fleets/{fleetId}/review']['post']['description'], 'openapi review'
assert 'v0.18.159 (fleetNeedsCar): fleet_no_car' in P['/driver/reminders']['get']['description'], 'openapi reminders'
md = open('CONTRACT.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
assert '\nv0.18.159 (fleet needs a car;' in md and 'Rider: not affected.' in md, 'CONTRACT.md note'
assert 'v0.18.159 (`fleetNeedsCar`): approving a fleet with no car' in md, 'CONTRACT.md admin line'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert 'v0.18.159 (fleet needs a car; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch, 'CHANGELOG move line'
assert '\nv0.18.150 (L20 stream backup;' in ch and '\nv0.18.150 (L20 stream backup;' not in md, 'v0.18.150 note moved'
print('v0.18.159 fleet needs a car: ok')

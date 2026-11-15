#!/usr/bin/env python3
# v0.18.94 job A5 / BQ-M13 (owner G10-2 "Admin sets day and time (Recommended)" ... "driver app shows next payout",
# Rules decisions/driver-g10.md:6): GET /driver/payouts sends the driver's next payout moment.
# Moved word for word out of verify.sh in v0.18.101 (Rule 25: verify.sh well under 1,500 lines); run by verify.sh from the repository root.
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 94), 'version 0.18.94 or later'
np_ = c['payouts']['schedule']['nextPayout']
assert 'driver-g10.md:6' in np_['note'] and 'never works the schedule out' in np_['note'], 'nextPayout note'
for f in ('DriverPayoutPage.nextPayoutAt', 'DriverPayoutPage.nextPayoutLocal', 'DriverPayoutPage.nextPayoutTimeZone', 'GET /driver/payouts only'):
    assert f in np_['fields'], 'nextPayout fields ' + f
assert 'payoutHold' in np_['rule'] and 'absent, never null' in np_['rule'] and 'anchorWeek' in np_['rule'], 'nextPayout rule'
assert set(np_['examples']) == {'SE', 'FR', 'TN'} and 'nextPayoutLocal 2026-11-16T08:00' in np_['examples']['SE'] and 'Africa/Tunis' in np_['examples']['TN'], 'nextPayout examples'
for w in ('contract', 'server', 'admin', 'driver app', 'rider app'):
    assert w in np_['apps'], 'nextPayout Rule 0 part ' + w
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
props = S['DriverPayoutPage']['allOf'][1]['properties']
assert set(props) == {'nextPayoutAt', 'nextPayoutLocal', 'nextPayoutTimeZone'}, 'DriverPayoutPage fields'
assert spec['paths']['/driver/payouts']['get']['responses']['200']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/DriverPayoutPage'}, 'driver payouts schema'
assert spec['paths']['/admin/payouts']['get']['responses']['200']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/PayoutPage'}, 'admin payouts unchanged'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read(); assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.94 (job A5' in tc and 'nextPayoutLocal' in tc, 'CONTRACT.md v0.18.94'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert spec['info']['version'] == c['version'], 'openapi version'

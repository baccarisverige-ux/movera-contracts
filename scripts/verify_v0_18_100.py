#!/usr/bin/env python3
"""v0.18.100 (BQ-V37, owner Sitting W1 Q66 "Yes" = Q-B6): the ride-check scan cadence is a per-zone admin
setting, default 30 s, range 10-120. Run by scripts/verify.sh from the repository root (own file: verify.sh is at
its 1,500-line limit, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
rc = c['onTrip']['rideCheck']
assert c['configDefaults']['rideCheck']['scanEverySeconds'] == 30, 'scanEverySeconds default 30'
assert rc['settings']['ranges']['scanEverySeconds'] == [10, 120], 'scanEverySeconds range'
assert 'per zone' in rc['settings']['where'] and 'scanEverySeconds' in rc['detection']['cadence'], 'cadence rule per zone'
for f in ('fixtures/config/driver_app_config.json', 'fixtures/config/rider_app_config.json'):
    assert json.load(open(f))['rideCheck']['scanEverySeconds'] == 30, f
p = spec['components']['schemas']['RideCheck']['properties']['scanEverySeconds']
assert (p['minimum'], p['maximum'], p['default'], p['type']) == (10, 120, 30, 'integer'), 'openapi RideCheck.scanEverySeconds'
t = open('CONTRACT.md', encoding='utf-8').read()
assert '\nv0.18.100 (BQ-V37' in t and 'scanEverySeconds (30' in t, 'CONTRACT.md v0.18.100'
print("v0.18.100 ride-check cadence ok")

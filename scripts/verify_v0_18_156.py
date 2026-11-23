#!/usr/bin/env python3
"""v0.18.156 (free pickup move 300 m; owner 2026-11-23, Rules decisions/session-2026-11-06.md "2026-11-23 OWNER DECISION":
the rider can adjust the pickup up to 300 m for free): the pickup move default is 300 m everywhere (configDefaults, the
pickupMove rule, both app config fixtures, the openapi copy), the range stays 0-2000, a booked trip keeps its booking-time
value (bookingSnapshot), the CONTRACT.md note, and the v0.18.150 note moved word for word to CHANGELOG.md (Rule 21 /
Rule 25). Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 156), 'version 0.18.156 or later'
pm = c['pickupWaiting']['pickupMove']
assert c['configDefaults']['maxPickupMoveMeters'] == 300, 'configDefaults.maxPickupMoveMeters 300'
assert pm['default'] == 300 and pm['range'] == [0, 2000], 'pickupMove default 300, range 0-2000'
assert pm['freeMoveNote'].startswith('v0.18.156') and '300' in pm['freeMoveNote'] and 'migration 0133' in pm['freeMoveNote'], 'freeMoveNote'
assert 'booking time' in pm['freeMoveNote'], 'booked trips keep their booking-time value'
assert 'maxPickupMoveMeters' in c['bookingSnapshot']['fields'], 'snapshot keeps the value'
for f in ('fixtures/config/rider_app_config.json', 'fixtures/config/driver_app_config.json'):
    assert json.load(open(f))['booking']['maxPickupMoveMeters'] == 300, f
spec = yaml.safe_load(open('openapi.yaml'))
for cfg in ('RiderAppConfig', 'DriverAppConfig'):
    d = spec['components']['schemas'][cfg]['properties']['booking']['properties']['maxPickupMoveMeters']['description']
    assert 'v0.18.156: default 300' in d, cfg + ' openapi default 300'
md = open('CONTRACT.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
assert '\nv0.18.156 (free pickup move 300 m;' in md, 'CONTRACT.md v0.18.156 note'
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert 'v0.18.156 (free pickup move 300 m; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch, 'CHANGELOG move line'
assert '\nv0.18.150 (L20 stream backup;' in ch and '\nv0.18.150 (L20 stream backup;' not in md, 'v0.18.150 note moved'
print('v0.18.156 free pickup move 300 m: ok')

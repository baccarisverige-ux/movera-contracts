#!/usr/bin/env python3
"""v0.18.115 (BQ-V21, owner full-audit Q6 2026-11-02 "Keep as 'approximate'" => admin on/off per zone (default on),
Rules decisions/rider-g4-pickup.md:7): the rider's approximate pickup entrance chips get a per-zone switch,
RiderAppConfig.booking.pickupSpots.on (default true). Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 115), 'version 0.18.115 or later'
assert c['configDefaults']['pickupSpotsOn'] is True, 'configDefaults.pickupSpotsOn is true (owner: default on)'
ps = c['pickupSpots']
assert "rider-g4-pickup.md:7" in ps['note'] and "Keep as 'approximate'" in ps['note'] and 'default on' in ps['note'], 'pickupSpots owner decision'
assert 'RiderAppConfig.booking.pickupSpots.on' in ps['setting'] and 'POST /admin/config/rider_app_config/publish' in ps['setting'], 'pickupSpots setting path'
assert "Dispatch › Rides 'Pickup entrance chips (approximate)'" in ps['setting'] and 'per zone' in ps['setting'], 'pickupSpots admin place'
assert 'invalid_document' in ps['server'] and 'true when it is missing' in ps['server'] and 'GET /rider/config' in ps['server'], 'pickupSpots server rule'
assert 'off: no entrance chips' in ps['rider'] and 'older server' in ps['rider'] and 'reads as on' in ps['rider'], 'pickupSpots rider rule'
assert "'Previously used'" in ps['rider'] and "'Near Home'" in ps['rider'] and 'stay' in ps['rider'], 'pickupSpots: only the entrance chips are switched'
assert ps['driver'].startswith('No change'), 'pickupSpots: driver not changed'
spec = yaml.safe_load(open('openapi.yaml'))
assert spec['info']['version'] == c['version'], 'openapi version'
S = spec['components']['schemas']
rb = S['RiderAppConfig']['properties']['booking']['properties']
assert rb['pickupSpots']['type'] == 'object' and rb['pickupSpots']['properties']['on']['type'] == 'boolean', 'openapi RiderAppConfig.booking.pickupSpots.on boolean'
assert rb['pickupSpots']['properties']['on']['default'] is True, 'openapi pickupSpots.on default true'
assert 'v0.18.115' in rb['pickupSpots']['description'] and 'invalid_document' in rb['pickupSpots']['description'], 'openapi pickupSpots description'
assert 'pickupSpots' not in S['DriverAppConfig']['properties']['booking']['properties'], 'driver document has no pickupSpots'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.117: the v0.18.109-v0.18.115 notes moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.115 (BQ-V21' in tc, 'CONTRACT.md v0.18.115 note'
assert 'pickupSpots: { on } },   // v0.18.115' in t, 'CONTRACT.md §6 RiderAppConfig booking line'
assert '| Pickup entrance chips, approximate (Dispatch › Rides; v0.18.115' in t, 'CONTRACT.md §5 control matrix row'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print("v0.18.115 pickup spots switch ok")

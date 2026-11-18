#!/usr/bin/env python3
"""v0.18.130 (SCS guard re-check follow-up; owner 2026-11-17 Q-SCS-1 "Keep values, save rest (Rec.)"): checks that
configDocs.keptKeys lists the driver document's realtime.oneStream (v0.18.122 switch), that the two v0.18.123 lists are
unchanged, the openapi copy, the CONTRACT.md note and the v0.18.124 note moved word for word to CHANGELOG.md (Rule 21 /
Rule 25). Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 130), 'version 0.18.130 or later'
kk = c['configDocs']['keptKeys']
assert kk['driver_app_config'] == ['realtime.oneStream'], 'driver_app_config kept keys'
assert kk['country_rules'] == ['payoutMode', 'payoutSchedule', 'maxRiderDebt', 'driverOwesLimit', 'calls.adminCallRoles', 'calls.phoneProvider'], 'country_rules unchanged'
assert kk['dispatch'] == ['radar.reaskAfterSeconds', 'exclusive.reaskAfterSeconds'], 'dispatch unchanged'
assert set(kk) == {'note', 'country_rules', 'dispatch', 'driver_app_config', 'driverAppConfigNote', 'removeKeys'}, 'keptKeys keys'
assert kk['driverAppConfigNote'].startswith('v0.18.130 (') and 'offers.autoOffline is not listed' in kk['driverAppConfigNote'], 'driverAppConfigNote'
assert c['configDefaults']['driverOneStream'] is False, 'default off unchanged'
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']
assert S['DriverAppConfig']['properties']['realtime']['properties']['oneStream']['type'] == 'boolean', 'the kept path exists'
u = S['ConfigDraftUpdate']['properties']['removeKeys']
assert sorted(u['items']['enum']) == sorted(kk['country_rules'] + kk['dispatch'] + kk['driver_app_config']) and u['maxItems'] == len(u['items']['enum']), 'openapi removeKeys'
assert 'v0.18.130 (configDocs.keptKeys; driver_app_config: realtime.oneStream)' in P['/admin/config/{doc}']['put']['description'], 'openapi PUT'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.130 (SCS guard re-check follow-up;' in t and 'follows v0.18.129)' in t, 'CONTRACT.md note'
assert '`realtime.oneStream` (`configDocs.keptKeys.driver_app_config`)' in t, 'CONTRACT.md kept keys line'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n124 = next(l for l in cl if l.startswith('v0.18.124 (C10 empty driver history;'))
assert '\n' + n124 not in t and hashlib.sha256(n124.encode()).hexdigest() == '9c4fc4c5e9c33121a7b3c916a0006fe9e841069b8c701a62d988f1a0eb9e534a', 'v0.18.124 note moved word for word'
j = cl.index(n124)
assert cl[j - 2].startswith('v0.18.130 (driver_app_config kept keys; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.123 and before (the v0.18.123 note moved in v0.18.129,'), 'old pointer line kept'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.124 and before (the v0.18.124 note moved in v0.18.130, the v0.18.123 note in v0.18.129, the v0.18.122 and v0.18.121 notes in v0.18.128,' in t, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.130 driver document kept keys ok')

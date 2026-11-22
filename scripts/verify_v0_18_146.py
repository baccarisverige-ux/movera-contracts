#!/usr/bin/env python3
"""v0.18.146 (audit apps-every-control 2026-11-20 N5; owner 2026-11-20 "Must see all kind"): EarningsPeriod.rideCounts
{ completed, cancelled, noShow } (contract.json#driverRideCounts), the openapi copy, the CONTRACT.md note, and the v0.18.140 (launch restack; the draft moved v0.18.127)
note moved word for word to CHANGELOG.md (Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 146), 'version 0.18.146 or later'
rc = c['driverRideCounts']
assert list(rc) == ['note', 'field', 'rule', 'app'], 'driverRideCounts keys'
assert 'EarningsPeriod.rideCounts { completed, cancelled, noShow }' in rc['field'] and 'Optional' in rc['field'], 'field'
assert 'Counted from trips, not earnings entries' in rc['rule'] and 'no_show (noShow)' in rc['rule'] and 'cancelled_by_system (cancelled)' in rc['rule'], 'rule'
assert 'A period with such rides but no earnings entry is sent too, with zero money.' in rc['rule'], 'rule: periods without entries'
assert 'Rides = completed + cancelled + noShow' in rc['app'], 'app'
spec = yaml.safe_load(open('openapi.yaml'))
ep = spec['components']['schemas']['EarningsPeriod']
r = ep['properties']['rideCounts']
assert r['required'] == ['completed', 'cancelled', 'noShow'] and r['additionalProperties'] is False, 'openapi rideCounts'
assert 'rideCounts' not in ep['required'], 'rideCounts optional'
assert 'v0.18.146 (driverRideCounts)' in spec['paths']['/driver/earnings']['get']['description'], 'endpoint description'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.146 (audit apps-every-control 2026-11-20 N5;' in t, 'CONTRACT.md note'
n146 = next(l for l in t.split('\n') if l.startswith('v0.18.146 (audit apps-every-control 2026-11-20 N5;'))
assert 'follows v0.18.145)' in n146 and '`contract.json#driverRideCounts`' in n146, 'CONTRACT.md note text'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
# launch restack (plan K): this version moves the v0.18.140 note (the draft moved v0.18.127)
n140 = next(l for l in cl if l.startswith('v0.18.140 (debt line M3; owner 2026-11-1'))
assert '\n' + n140 not in t and cl.count(n140) == 1, 'v0.18.140 note moved once'
assert hashlib.sha256(n140.encode()).hexdigest() == 'ec6c94d9fab6d54949af18cb70a33728edcd1dc5fda20ce52528ef0f411e4a4c', 'v0.18.140 note moved word for word'
j = cl.index(n140)
assert cl[j - 2].startswith('v0.18.146 (driver ride counts; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == 'c6b19044d3e3911574818c54103ce06cdb4d578e1618d5bec5fb94344b388bf2', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.140 and before (the v0.18.140 note moved in v0.18.146, the v0.18.139 note in v0.18.145, the v0.18.136' in t + ch, 'new pointer line (in CHANGELOG.md once a later version moves it)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.146 driver ride counts ok')

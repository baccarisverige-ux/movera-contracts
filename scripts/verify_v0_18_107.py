#!/usr/bin/env python3
# v0.18.107 server BQ-M28 (M28 supervisor MF3, Rules audits/impact/m28-late-bonus-supervisor.md §3.4): a paid trip's own
# later bonus lowers Movera gets once, in the payout that pays it (priceDisplay.payoutSummary.laterBonus).
# Kept out of verify.sh (Rule 25: scripts/ files <= 1,500 lines); run by verify.sh from the repository root.
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 107), 'version 0.18.107 or later'
ps = c['priceDisplay']['payoutSummary']
lb = ps['laterBonus']
assert lb.startswith('v0.18.107 (server BQ-M28') and 's06:1263' in lb, 'laterBonus source'
for w in ("a paid trip's own bonus entries", 'written at or after the paid end', 'each lower moveraGets once, in the payout that pays that entry',
          'added back when they are booked in another payout or in none yet', "takes it off", 'Both in one payout: once', 'Driver and admin views alike',
          'A lost-driver payment is never one of them', 'the driver who later ends the trip', 'frozenWhenPaid reads the same rule', 'driverGets is unchanged', 'the apps change nothing'):
    assert w in lb, 'laterBonus: ' + w
r, fz = ps['rule'], ps['frozenWhenPaid']
assert 'except laterBonus (v0.18.107' in r and 'added back here and taken off once, in the payout that pays them' in r, 'rule points to laterBonus'
assert 'v0.18.107: with laterBonus' in fz and 'not in its frozen number' in fz and fz.startswith('v0.18.95'), 'frozenWhenPaid points to laterBonus'
for k, now in (('ruleBefore0_18_107', r), ('frozenWhenPaidBefore0_18_107', fz)):
    old = ps[k]
    assert old.startswith('Replaced in v0.18.107 (kept, Rule 21') and 'laterBonus' not in old.split(': ', 1)[1], k + ' kept (Rule 21)'
assert ps['ruleBefore0_18_107'].split(': ', 1)[1] == r.replace(" — except laterBonus (v0.18.107, server BQ-M28): a paid trip's own bonus entries booked in another payout or in none yet are added back here and taken off once, in the payout that pays them", ''), 'rule: only the pointer added'
assert set(c['priceDisplay']['payoutSummary']['texts']) >= {'driverGets', 'moveraGets'}, 'texts unchanged'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert spec['info']['version'] == c['version'], 'openapi version'
d = S['PayoutSummary']['description']
assert lb in d and r in d and fz in d, 'openapi PayoutSummary wording'
assert S['PayoutSummary']['required'] == ['driverGets', 'moveraGets'], 'shape unchanged'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.107 (server BQ-M28' in t and '**a later bonus lowers Movera gets in the payout that pays it**' in t, 'CONTRACT.md v0.18.107 note'
assert 'v0.18.107: a later bonus counts in the payout that pays it, `payoutSummary.laterBonus`' in t, 'CONTRACT.md payouts line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print("v0.18.107 ok")

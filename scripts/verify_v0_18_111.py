#!/usr/bin/env python3
# v0.18.111 server BQ-M28 (M28 supervisor MF3, Rules audits/impact/m28-late-bonus-supervisor.md §3.4): a paid trip's own
# later bonus lowers Movera gets once, in the payout that pays it (priceDisplay.payoutSummary.laterBonus).
# Kept out of verify.sh (Rule 25: scripts/ files <= 1,500 lines); run by verify.sh from the repository root.
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 111), 'version 0.18.111 or later'
ps = c['priceDisplay']['payoutSummary']
lb = ps['laterBonus']
assert lb.startswith('v0.18.111 (server BQ-M28') and 's06:1263' in lb, 'laterBonus source'
for w in ("a paid trip's own bonus entries", 'written at or after the paid end', 'each lower moveraGets once, in the payout that pays that entry',
          'added back when they are booked in another payout or in none yet', "takes it off", 'Both in one payout: once', 'Driver and admin views alike',
          'A lost-driver payment is never one of them', 'the driver who later ends the trip', 'frozenWhenPaid reads the same rule', 'driverGets is unchanged', 'the apps change nothing'):
    assert w in lb, 'laterBonus: ' + w
r, fz = ps['rule'], ps['frozenWhenPaid']
assert 'except laterBonus (v0.18.111' in r and 'added back here and taken off once, in the payout that pays them' in r, 'rule points to laterBonus'
assert 'v0.18.111: with laterBonus' in fz and 'not in its frozen number' in fz and fz.startswith('v0.18.95'), 'frozenWhenPaid points to laterBonus'
for k, now in (('ruleBefore0_18_111', r), ('frozenWhenPaidBefore0_18_111', fz)):
    old = ps[k]
    assert old.startswith('Replaced in v0.18.111 (kept, Rule 21') and 'laterBonus' not in old.split(': ', 1)[1], k + ' kept (Rule 21)'
assert ps['ruleBefore0_18_111'].split(': ', 1)[1] == r.replace(" — except laterBonus (v0.18.111, server BQ-M28) and laterPayChange (v0.18.111, server BQ-M29): a paid trip's own bonus entries booked in another payout or in none yet are added back here and taken off once, in the payout that pays them (its own pay-change entries the same way: each counted once, in the payout that pays it)", ''), 'rule: only the pointer added'
# BQ-M29 (Rules audits/impact/m29-late-adjustment.md): the same rule for the trip's own pay-change entries (laterPayChange).
lp = ps['laterPayChange']
assert lp.startswith('v0.18.111 (server BQ-M29; M28 supervisor §3.2') and 's06:1263' in lp, 'laterPayChange source'
for w in ("laterBonus also holds for a paid trip's own pay-change entries (kind adjustment, the trip's driver, written at or after the paid end",
          'the change kept at the paid end', 'every admin pay change after the end (finish.driverMoney.payChange)',
          "the driver's share taken back by a refund (finish.refund, fromDriver)", 'Each one moves moveraGets once, in the payout that pays that entry',
          'a + change lowers it, a − change raises it (its moveraGets can be below 0)', 'added back when they are booked in another payout or in none yet',
          'Both in one payout: once', 'Driver and admin views alike', "a no-show's share taken back, arrivedWaiting.reverseNoShow) is not one of them",
          "A refund is not an entry: it stays in the trip's moveraKeepsNow", 'frozenWhenPaid reads the same rule', 'driverGets is unchanged', 'the apps change nothing'):
    assert w in lp, 'laterPayChange: ' + w
for ref_ in (('finish', 'driverMoney', 'payChange'), ('finish', 'refund'), ('arrivedWaiting', 'reverseNoShow')):
    node = c
    for k in ref_: node = node[k]
assert ' and laterPayChange (v0.18.111, server BQ-M29)' in r and 'its own pay-change entries the same way' in r, 'rule points to laterPayChange'
assert 'v0.18.111: with laterPayChange, a later pay change not booked in this payout is not in its frozen number and counts in the payout that pays it' in fz, 'frozenWhenPaid points to laterPayChange'
assert 'laterPayChange' not in ps['ruleBefore0_18_111'] and 'laterPayChange' not in ps['frozenWhenPaidBefore0_18_111'], 'old texts kept without M29 (Rule 21)'
assert ps['frozenWhenPaidBefore0_18_111'].split(': ', 1)[1] == fz.replace('; v0.18.111: with laterBonus, so a later bonus not booked in this payout is not in its frozen number and is taken off in the payout that pays it; v0.18.111: with laterPayChange, a later pay change not booked in this payout is not in its frozen number and counts in the payout that pays it', ''), 'frozenWhenPaid: only the pointers added'
assert set(c['priceDisplay']['payoutSummary']['texts']) >= {'driverGets', 'moveraGets'}, 'texts unchanged'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert spec['info']['version'] == c['version'], 'openapi version'
d = S['PayoutSummary']['description']
assert lb in d and lp in d and r in d and fz in d, 'openapi PayoutSummary wording'
assert S['PayoutSummary']['required'] == ['driverGets', 'moveraGets'], 'shape unchanged'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.117: the v0.18.109-v0.18.115 notes moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.111 (server BQ-M28' in tc and '**a later bonus lowers Movera gets in the payout that pays it**' in tc, 'CONTRACT.md v0.18.111 note'
assert 'v0.18.111: a later bonus counts in the payout that pays it, `payoutSummary.laterBonus`' in tc, 'CONTRACT.md payouts line'
assert '**a later pay change moves Movera gets in the payout that pays it**' in tc and 'so does a later pay change, `payoutSummary.laterPayChange`' in tc, 'CONTRACT.md BQ-M29 wording'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print("v0.18.111 ok")

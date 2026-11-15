#!/usr/bin/env python3
# v0.18.97 (J8 wording, Rules audits/impact/j8-rebase-money-fix-supervisor.md §6): a paid_to_movera entry is never in
# Payout.summary or fleet earnings; paid-movera closing a payout freezes its summary in the same step.
# Moved word for word out of verify.sh in v0.18.101 (Rule 25: verify.sh well under 1,500 lines); run by verify.sh from the repository root.
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 97), 'version 0.18.97 or later'
ps = c['priceDisplay']['payoutSummary']
r = ps['rule']
assert 'v0.18.97' in r and "A 'Driver paid Movera' entry (kind paid_to_movera" in r and 'never in driverGets or moveraGets, in the payout it closes or in the next payout' in r, 'rule: paid_to_movera never in the summary'
assert '= Payout.amount + the cash he collected − his paid_to_movera entries in Payout.amount' in r, 'rule: identity fixed'
assert '= Payout.amount + the cash he collected)' not in r, 'rule: old identity gone'
ptm = ps['paidToMovera']
assert 'never in driverGets or moveraGets' in ptm and 'not in the payout it closes' in ptm and 'not in the next payout' in ptm, 'paidToMovera both payouts'
assert 'driverGets = Payout.amount + the cash he collected − his paid_to_movera entries in Payout.amount' in ptm and 'line paid_to_movera, +amount' in ptm, 'paidToMovera identity'
fz = ps['frozenWhenPaid']
assert 'POST /admin/payouts/{payoutId}/paid' in fz and 'POST /admin/drivers/{driverId}/paid-movera covers the payout\'s carried rest in full and closes it as paid' in fz and 'frozen in the same step' in fz, 'frozenWhenPaid paid-movera'
assert ps['frozenWhenPaidBefore0_18_97'].startswith('Replaced in v0.18.97 (kept, Rule 21') and 'paid-movera' not in ps['frozenWhenPaidBefore0_18_97'], 'old frozenWhenPaid kept'
assert ps['ruleBefore0_18_97'].startswith('Replaced in v0.18.97 (kept, Rule 21') and '= Payout.amount + the cash he collected)' in ps['ruleBefore0_18_97'], 'old rule kept'
fe = c['debtModel']['driverOwes']['fleetEarnings']
assert 'GET /driver/fleet/earnings' in fe and 'a paid_to_movera entry' in fe and 'is not earnings' in fe, 'fleet earnings'
assert 'paid_to_movera' in c['debtModel']['driverOwes']['paidMovera'], 'paidMovera kept'
pmv = c['debtModel']['driverOwes']['paidMovera']
assert 'v0.18.97' in pmv and 'open payouts below 0' in pmv and 'oldest first (period start, then payoutId)' in pmv and 'LINKED to that payout' in pmv, 'paidMovera: linked to open payouts below 0, oldest first'
assert 'covers in full is closed as paid' in pmv and 'audit payout.paid' in pmv and 'frozen in the same step' in pmv and 'covered only in part stays open' in pmv, 'paidMovera: full cover closes, audits, freezes'
assert "Any amount left over becomes one UNLINKED entry, counted in the next payout's amount and lines" in pmv, 'paidMovera: left over is unlinked'
assert c['debtModel']['driverOwes']['paidMoveraBefore0_18_97'].startswith('Replaced in v0.18.97 (kept, Rule 21') and 'oldest first' not in c['debtModel']['driverOwes']['paidMoveraBefore0_18_97'], 'old paidMovera kept'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert spec['info']['version'] == c['version'], 'openapi version'
d = S['PayoutSummary']['description']
assert r in d and ptm in d and fz in d, 'openapi PayoutSummary wording'
assert fe in S['FleetEarnings']['description'], 'openapi FleetEarnings wording'
P = spec['paths']
assert fe in P['/driver/fleet/earnings']['get']['description'], 'openapi fleet earnings op'
pm = P['/admin/drivers/{driverId}/paid-movera']['post']['description']
assert pmv in pm and 'v0.18.97' in pm and 'frozen in the same step' in pm and 'never in driverGets or moveraGets' in pm, 'openapi paid-movera op'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.110: the v0.18.97-v0.18.108 notes moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.97 (J8 wording' in tc and 'is frozen in the same step' in tc and '**paid-movera settles the carried rest first**' in tc, 'CONTRACT.md v0.18.97'
assert '\nv0.18.70 (server S4 B1.23' not in t and '\nv0.18.70 (server S4 B1.23' in open('CHANGELOG.md', encoding='utf-8').read(), 'v0.18.70 note moved to CHANGELOG.md (Rule 21)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'

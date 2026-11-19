#!/usr/bin/env python3
"""v0.18.133 (S5 J12-J15, BQ-M05): payout lines + carry. Checks contract.json#payoutLines, the switch default (off),
the openapi Payout fields, CountryRules.payoutLinesOn, GET /admin/payouts/runs, the CONTRACT.md note and line, and the
v0.18.127 note moved word for word to CHANGELOG.md (Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 133), 'version 0.18.133 or later'
pl = c['payoutLines']
assert set(pl) == {'note', 'switch', 'lines', 'carry', 'owed', 'once', 'runs', 'driver', 'admin', 'rider'}, 'payoutLines keys'
assert c['configDefaults']['payoutLinesOn'] is False, 'switch off by default'
assert 'earned - owedToMovera = paidOut - carriedOut' in pl['lines'] and 'Payout.amount = paidOut (never below 0)' in pl['lines'], 'lines identity'
assert 'no UPDATE' in pl['carry'] and 'taken once' in pl['carry'], 'carry: old rows only read, taken once'
assert 'going online is never refused' in pl['owed'] and 'card / Apple Pay / wallet trips still come' in pl['owed'], 'owed limit rule'
assert "only when carriedOut > 0" in pl['driver'] and 'nothing worked out on the phone' in pl['driver'], 'driver display'
assert 'not the first page' in pl['runs'], 'runs: server count'
o = yaml.safe_load(open('openapi.yaml'))
S, P = o['components']['schemas'], o['paths']
for k in ('earned', 'owedToMovera', 'paidOut', 'carriedIn', 'carriedOut'):
    assert k in S['Payout']['properties'] and k not in S['Payout'].get('required', []), 'Payout.' + k
assert S['CountryRules']['properties']['payoutLinesOn']['default'] is False, 'CountryRules.payoutLinesOn'
g = P['/admin/payouts/runs']['get']
assert g['x-permission'] == 'finance.read' and g['responses']['200']['content']['application/json']['schema']['$ref'].endswith('/PayoutRunList'), 'runs route'
assert {'earned', 'owedToMovera', 'paidOut', 'carriedOut', 'periodStart'} <= set(S['PayoutRunCard']['properties']), 'PayoutRunCard lines'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.133 (S5 J12-J15, BQ-M05;' in t, 'CONTRACT.md note'
assert '- **Payout lines and carry** (v0.18.133, `payoutLines`' in t, 'CONTRACT.md line'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n127 = next(l for l in cl if l.startswith('v0.18.127 (S7 W2 Q119'))
assert '\n' + n127 not in t and hashlib.sha256(n127.encode()).hexdigest() == 'b51a0ff2ebb7016f49c9a557fb973e2a146ceaece339a99b3829d3760b5e644e', 'v0.18.127 note moved word for word'
j = cl.index(n127)
assert cl[j - 2].startswith('v0.18.133 (S5 payout lines + carry; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '500ff2fd72593fe8c33c06d0cb1634754ea5da6aa47af9bb54ceee2fa8ded620', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.127 and before (the v0.18.127 note moved in v0.18.133, the v0.18.126 note in v0.18.132,' in t, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
# Review M1 / M2 / S2.
kk = c['configDocs']['keptKeys']
assert kk['country_rules'] == ['payoutMode', 'payoutSchedule', 'maxRiderDebt', 'driverOwesLimit', 'calls.adminCallRoles', 'calls.phoneProvider', 'payoutLinesOn'], 'M1: payoutLinesOn kept key'
assert 'payoutLinesOn' in S['ConfigDraftUpdate']['properties']['removeKeys']['items']['enum'], 'M1: removeKeys names payoutLinesOn'
assert 'CountryRules.payoutLinesOn is kept' in c['pricingHistory']['restoreKeeps'], 'M1: Restore keeps payoutLinesOn'
assert 'configDocs.keptKeys.country_rules' in pl['switch'], 'M1: switch note'
assert 'order they were made (created_at, then period_end, then payout_id' in pl['carry'], 'M2: carry order'
assert c['payouts']['lines'][-2:] == ['carried_in', 'carried_out'] and S['PayoutLine']['properties']['code']['enum'][-2:] == ['carried_in', 'carried_out'], 'S2: carry lines'
print('v0.18.133 payout lines + carry ok')

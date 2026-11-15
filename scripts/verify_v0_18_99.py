#!/usr/bin/env python3
# v0.18.99 BQ-M25b (M25 supervisor F1 + F2, Rules audits/impact/m25-card-cash-supervisor.md): on a trip not paid in the
# car the cash numbers are 0 (cashDue, TripFinish.cashToCollect, TripProjection.cashToCollect); refund room wording.
# Moved out of verify.sh (Rule 25: scripts/ files <= 1,500 lines); run by verify.sh from the repository root.
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 99), 'version 0.18.99 or later'
nz = c['priceDisplay']['nonCashZero']
assert 'm25-card-cash-supervisor.md' in nz['note'] and 'coming_soon' in nz['note'] and 'no migration' in nz['note'] and 'no admin setting' in nz['note'], 'nonCashZero note'
for f in ('CompletePreview.cashDue = 0', 'TripFinish.cashToCollect = 0', 'TripProjection.cashToCollect = 0', 'card, apple_pay, wallet', 'On a cash trip they are unchanged'):
    assert f in nz['rule'], 'nonCashZero rule: ' + f
assert 'never 409 price_changed' in nz['complete'] and 'cash_above_fare' in nz['complete'] and 'books 0 cash' in nz['complete'], 'complete on a non-cash trip'
assert set(nz['apps']) == {'driver', 'rider', 'admin', 'server'} and 'No change' in nz['apps']['driver'] and 'cashPart' in nz['apps']['server'], 'nonCashZero apps (Rule 0)'
cp = c['completePreview']
assert cp['sameBefore0_18_99'].count("cashDue = total − the part the rider's wallet would pay.") == 1 and '0 on every other trip' in cp['same'], 'completePreview.same (old kept)'
assert cp['frozen'].startswith(cp['frozenBefore0_18_99']) and 'is not compared' in cp['frozen'], 'completePreview.frozen extends the old text'
pd = c['priceDisplay']
assert pd['tripCashToCollect'].startswith(pd['tripCashToCollectBefore0_18_99']) and 'is 0 in every view' in pd['tripCashToCollect'], 'tripCashToCollect (old kept)'
r = c['finish']['refund']
assert 'At most what the rider paid (cash + wallet)' in r['existingBefore0_18_99'] and '(cash + wallet)' not in r['existing'], 'refund room old text kept, new text replaces it'
assert 'the cash taken, or the card part, plus the wallet part' in r['existing'], 'F2 refund room wording'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert spec['info']['version'] == c['version'], 'openapi version'
for s_, k in (('CompletePreview', 'cashDue'), ('TripFinish', 'cashToCollect'), ('TripProjection', 'cashToCollect')):
    d = ' '.join(S[s_]['properties'][k]['description'].split())
    assert 'v0.18.99' in d and 'CompletePreview.cashDue = 0' in d, s_ + '.' + k + ' description'
assert 'cashDue' in S['CompletePreview']['required'], 'shape unchanged'
d = ' '.join(spec['paths']['/admin/trips/{tripId}/refund']['post']['description'].split())
assert 'the cash taken, or the card part, plus the wallet part' in d, 'refund path description'
d = ' '.join(spec['paths']['/driver/trips/{tripId}/complete-preview']['get']['description'].split())
assert 'v0.18.99' in d, 'complete-preview path description'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.99 (BQ-M25b' in t and 'the cash taken, or the card part, plus the wallet part' in t, 'CONTRACT.md v0.18.99'
ch = open('CHANGELOG.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read(); assert '\nv0.18.71 (wording fix' in ch and 'Older version notes (v0.18.70 and before)' in ch and 'Older version notes (v0.18.71 and before)' in tc, 'Rule 21: moved lines are in CHANGELOG.md'  # v0.18.101: this pointer line moved to CHANGELOG.md (Rule 21 kept word for word)
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print("v0.18.99 ok")

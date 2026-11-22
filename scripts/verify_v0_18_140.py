#!/usr/bin/env python3
"""v0.18.140 (DRAFT, debt line M3; owner 2026-11-19 "Yes, build M2 + M3 (Rec.)"): CompletePreview.cashDueRide and
cashDueOutstandingFee, optional Money, described by contract.json#completePreview.cashDueSplit; the top note in CONTRACT.md
(launch restack; the draft kept it in CHANGELOG.md). Run by scripts/verify.sh (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 140), 'version 0.18.140 or later'
d = c['completePreview']['cashDueSplit']
for w in ('cashDueRide + cashDueOutstandingFee = cashDue exactly', 'Both are absent when that fee part is 0', 'never a sum or difference on the phone', 'cashCollected stays cashDue', 'collect cash screen shows ONLY cashDue', 'shown only on the trip\'s waybill'):
    assert w in d, 'cashDueSplit: ' + w
o = yaml.safe_load(open('openapi.yaml'))['components']['schemas']['CompletePreview']
for f in ('cashDueRide', 'cashDueOutstandingFee'):
    assert f in o['properties'] and f not in o.get('required', []), f + ' optional in CompletePreview'
    assert o['properties'][f]['allOf'] == [{'$ref': '#/components/schemas/Money'}], f + ' is Money'
assert o.get('additionalProperties') is False, 'CompletePreview stays closed'
assert 'collect sheet shows them as two rows' not in d, 'no rows on the collect sheet (owner 2026-11-21)'
assert '\nv0.18.140 (debt line M3;' in open('CONTRACT.md', encoding='utf-8').read() and 'follows v0.18.139)' in next(l for l in open('CONTRACT.md', encoding='utf-8').read().split('\n') if l.startswith('v0.18.140 (')), 'CONTRACT.md top note (launch restack: was a DRAFT note in CHANGELOG.md), follows v0.18.139'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and t.count('\n') <= 1500, 'CONTRACT.md title / size'
print('v0.18.140 cash due split ok')

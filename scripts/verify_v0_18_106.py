#!/usr/bin/env python3
"""v0.18.106 (contract text batch, wording only): headingCheck.setting reads reassign false and the admin label
'Heading to the pickup (%)' (Rules audits/impact/v35-v36-safety.md); paid-movera names its 400 reasons
invalid_amount / currency_mismatch (J8 supervisor W1, audits/impact/j8-rebase-money-fix-supervisor.md).
Run by scripts/verify.sh from the repository root (own file: verify.sh stays under 1,500 lines, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 106), 'version 0.18.106 or later'
hc = c['pickupWaiting']['headingCheck']
st = hc['setting']
assert '(on, 80 %, 2 min, reassign false)' in st and 'reassign on' not in st, 'headingCheck.setting: reassign false'
assert "'Smart cancel check' / 'Heading to the pickup (%)' controls map to on / headingPct" in st and 'v0.18.106' in st, 'headingCheck.setting: admin label'
assert c['configDefaults']['headingCheck']['reassign'] is False, 'configDefaults reassign false'
sb = hc['settingBefore0_18_106']
assert sb.startswith('Replaced in v0.18.106 (kept, Rule 21): ') and '(on, 80 %, 2 min, reassign on)' in sb and "'Came closer by' controls" in sb, 'old headingCheck.setting kept'
do = c['debtModel']['driverOwes']
pmv = do['paidMovera']
assert 'an amount ≤ 0 → 400 invalid_request, reason invalid_amount' in pmv and 'an amount in another currency than expectedOwed → 400 invalid_request, reason currency_mismatch' in pmv and 'v0.18.106' in pmv, 'paidMovera: 400 reasons named'
assert 'reason paid_above_owed' in pmv and 'open payouts below 0' in pmv and pmv.endswith(' Answer: the fresh OwingDriver.'), 'paidMovera: v0.18.97 text kept'
pb = do['paidMoveraBefore0_18_106']
assert pb.startswith('Replaced in v0.18.106 (kept, Rule 21): ') and 'invalid_amount' not in pb and 'currency_mismatch' not in pb and 'open payouts below 0' in pb, 'old paidMovera kept'
spec = yaml.safe_load(open('openapi.yaml'))
assert spec['info']['version'] == c['version'], 'openapi version'
assert st in spec['components']['schemas']['HeadingCheckSettings']['description'], 'openapi HeadingCheckSettings wording'
op = spec['paths']['/admin/drivers/{driverId}/paid-movera']['post']
assert pmv in op['description'], 'openapi paid-movera description'
d400 = op['responses']['400']['description']
assert all(k in d400 for k in ('invalid_amount', 'currency_mismatch', 'paid_above_owed', 'reason_required', 'v0.18.106')), 'openapi paid-movera 400 reasons'
assert op['responses']['400']['content']['application/json']['schema']['$ref'] == '#/components/schemas/Error', 'openapi paid-movera 400 schema'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.106 (contract text batch' in t, 'CONTRACT.md v0.18.106'
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert '\nv0.18.71 (wording fix, live bug 2026-11-12' not in t and '\nv0.18.71 (wording fix, live bug 2026-11-12' in ch and 'Older version notes (v0.18.71 and before) are in `CHANGELOG.md`.' in t, 'v0.18.71 note moved to CHANGELOG.md (Rule 21)'
assert '\nOlder version notes (v0.18.70 and before) are in `CHANGELOG.md`.\n' in ch, 'old pointer line kept in CHANGELOG.md (Rule 21)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'

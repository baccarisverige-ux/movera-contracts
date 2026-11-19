#!/usr/bin/env python3
"""v0.18.134 (S5 J16/J17 admin list ids; owner item 109, Rules handover/build-plans-2026-11-12/S5-money.md J16): checks
adminListFilters.ids (riders, drivers, trips; 1-200; never 403), the ids query key on the three routes in openapi.yaml,
the CONTRACT.md note and §7 line, and the v0.18.127 note moved word for word to CHANGELOG.md (Rule 25). Run by
scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 134), 'version 0.18.134 or later'
alf = c['adminListFilters']
ids = alf['ids']
assert ids['lists'] == ['GET /admin/riders', 'GET /admin/drivers', 'GET /admin/trips'] and ids['max'] == 200, 'ids lists / max'
assert 'never 403, never 404' in ids['rule'] and 'at least 1 and at most 200' in ids['rule'] and 'the admin\'s own zones still apply' in ids['rule'], 'ids rule'
assert list(alf).index('ids') == list(alf).index('total') + 1, 'ids right after total'
spec = yaml.safe_load(open('openapi.yaml'))
for r in ids['lists']:
    op = spec['paths'][r.split(' ', 1)[1]]['get']
    p = [x for x in op['parameters'] if x.get('name') == 'ids']
    assert len(p) == 1 and p[0]['schema']['maxItems'] == 200 and p[0]['schema']['minItems'] == 1 and p[0]['explode'] is False, r + ' ids param'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.134 (S5 J16/J17 admin list paging;' in t, 'CONTRACT.md note'
assert 'v0.18.134: riders, drivers and trips also take `ids` (1–200, the same narrowing; an id outside the admin\'s zones is left out, never 403; `adminListFilters.ids`).' in t, 'CONTRACT.md §7'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n127 = next(l for l in cl if l.startswith('v0.18.127 (S7 W2 Q119, plan 0.21;'))
assert '\n' + n127 not in t and cl.count(n127) == 1, 'v0.18.127 note moved once'
j = cl.index(n127)
assert cl[j - 2].startswith('v0.18.134 (S5 J16/J17 admin list ids; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.126 and before (the v0.18.126 note moved in v0.18.132,'), 'old pointer line kept'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.127 and before (the v0.18.127 note moved in v0.18.134, the v0.18.126 note in v0.18.132,' in t, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.134 admin list ids ok')

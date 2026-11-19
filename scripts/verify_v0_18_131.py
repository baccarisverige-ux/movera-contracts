#!/usr/bin/env python3
"""v0.18.131 (S7 alert-cap MF3, Rules plan/NUMBERS.md; Rule A safety): checks that the admin alert book bounds the open
non-safety alerts (liveList.openOtherCap 1000), never cuts an open safety alert, names AlertBookState.alertsMore with
its admin line (en / sv / fr), the openapi copy, the CONTRACT.md note and §44, and the v0.18.125 note moved word for
word to CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 131), 'version 0.18.131 or later'
ll = c['alertDesk']['serverDetection']['liveList']
assert ll['openOtherCap'] == 1000 and ll['solvedCap'] == 1000, 'caps'
assert 'sos, car_lost, ride_check, sos_slow' in ll['open'] and 'no limit, never cut' in ll['open'] and 'at most openOtherCap (1000)' in ll['open'], 'open text'
assert ll['more'].startswith('v0.18.131: AlertBookState.alertsMore { open: boolean, solved: boolean }') and 'Missing = nothing was left out' in ll['more'], 'more text'
al = ll['adminLine']
assert "en 'More alerts than shown." in al and "sv 'Det finns fler larm" in al and "fr 'Il y a plus d'alertes" in al and 'Driver and rider apps: no change.' in al, 'admin line'
spec = yaml.safe_load(open('openapi.yaml'))
abs_ = spec['components']['schemas']['AlertBookState']
m = abs_['properties']['alertsMore']
assert m['required'] == ['open', 'solved'] and m['additionalProperties'] is False and set(m['properties']) == {'open', 'solved'}, 'openapi alertsMore'
assert 'alertsMore' not in abs_['required'], 'alertsMore is optional'
assert 'v0.18.131 (alertDesk.serverDetection.liveList)' in spec['paths']['/admin/alerts/book']['get']['description'], 'openapi GET book text'
t = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.131 (S7 alert-cap MF3;' in t and 'follows v0.18.130)' in t, 'CONTRACT.md note'
s44 = t[t.index('\n## 44. '):t.index('\n## 46. ')]
assert 'v0.18.131 (MF3, `liveList.openOtherCap` / `more`)' in s44 and '`alertsMore { open, solved }`' in s44, 'CONTRACT.md §44'
assert '\nv0.18.125 (L20-6 health' not in t and '\nv0.18.125 (L20-6 health' in ch, 'v0.18.125 note moved'
cl = ch.split('\n')
j = next(i for i, l in enumerate(cl) if l.startswith('v0.18.125 (L20-6 health'))
assert cl[j - 2].startswith('v0.18.131 (S7 alert-cap MF3; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.124 and before (the v0.18.124 note moved in v0.18.130,'), 'old pointer line kept'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.125 and before (the v0.18.125 note moved in v0.18.131, the v0.18.124 note in v0.18.130,' in t + ch, 'new pointer line (kept in CHANGELOG.md since v0.18.132)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.131 alert book more marker ok')

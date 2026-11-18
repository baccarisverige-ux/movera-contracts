#!/usr/bin/env python3
"""v0.18.126 (S7 W2 Q126 = Q-B4; owner 2026-11-15 "Yes, open ones only (Rec.)"): the admin alarm feed
GET /admin/incidents/stream with no cursor starts from the open incidents. Checks contract.json#safety.feedStart, that no
other safety key changed, the openapi copy and CONTRACT.md. Run by scripts/verify.sh from the repository root (Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 126), 'version 0.18.126 or later'
spec = yaml.safe_load(open('openapi.yaml'))
P = spec['paths']

s = c['safety']
f = s['feedStart']
assert f.startswith('v0.18.126 (S7 W2 Q126 = Q-B4;') and 'Yes, open ones only (Rec.)' in f, 'feedStart: source'
assert 'no `after`, `after=0`, no Last-Event-ID' in f and 'newest event of each open or investigating incident' in f, 'feedStart: no cursor = open start'
assert 'oldest first, then live after that newest sequence' in f and "Closed incidents' history is not replayed" in f, 'feedStart: order, live, no closed replay'
assert 'never cut by `limit`' in f and '`nextCursor` = the newest sequence when it is newer than the last item, else null' in f, 'feedStart: JSON page'
assert 'With a cursor (`after` > 0 or Last-Event-ID) nothing changes' in f and 'Rule 33' in f, 'feedStart: cursor unchanged, Rule 33'
assert list(s) == ['note', 'incidentKinds', 'kindSeverity', 'raisedBy', 'statuses', 'statusLabels', 'transitions', 'sos', 'escalateAfterSeconds', 'escalationNote', 'streamEventKinds', 'alarmKinds', 'driverSilent', 'alarmNote', 'rideCheck', 'onlyDuringTrip', 'feedStart'], 'safety: only feedStart added'

d = P['/admin/incidents/stream']['get']['description'].replace('\n', ' ')
assert 'v0.18.126 (contract.json#safety.feedStart)' in d and 'starts from the OPEN incidents' in d, 'openapi /admin/incidents/stream'
assert [p.get('$ref') for p in P['/admin/incidents/stream']['get']['parameters']][:2] == ['#/components/parameters/After', '#/components/parameters/LastEventId'], 'openapi: no parameter change'

t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.126 (S7 W2 Q126 = Q-B4;' in t and 'follows v0.18.125)' in t, 'CONTRACT.md v0.18.126 note'
assert 'v0.18.126 (`safety.feedStart`): with no cursor' in t and 'closed incidents are not replayed' in t, 'CONTRACT.md §15 alarm feed'
# the move (Rule 25 size, Rule 21 word for word): the v0.18.119 note and the old pointer line now only in CHANGELOG.md
import hashlib
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n119 = next(l for l in cl if l.startswith('v0.18.119 (S7 W2 Q117 + Q118;'))
assert '\n' + n119 not in t and hashlib.sha256(n119.encode()).hexdigest() == '9ca22b1cdcecd90fcbfa8fec0054cdf4a274b2bfae2600a6b4b8a23a53338774', 'v0.18.119 note moved word for word'
j = cl.index(n119)
assert cl[j - 2].startswith('v0.18.126 (S7 W2 Q126; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.118 and before (the v0.18.118 note moved in v0.18.125,'), 'old pointer line kept in CHANGELOG.md'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.119 and before (the v0.18.119 note moved in v0.18.126, the v0.18.118 note in v0.18.125, the v0.18.117 note in v0.18.124,' in t + ch, 'the v0.18.126 pointer line (kept in CHANGELOG.md since v0.18.127)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.126 incident feed open start ok')

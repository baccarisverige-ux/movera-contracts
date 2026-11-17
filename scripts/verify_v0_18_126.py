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
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.126 incident feed open start ok')

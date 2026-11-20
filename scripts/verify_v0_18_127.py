#!/usr/bin/env python3
"""v0.18.127 (S7 W2 Q119, plan 0.21; owner 2026-11-15 "All except GPS (Rec.)", server only; Rules
decisions/session-2026-11-06.md:1381): wording only. Checks that rider_trip_changed is not sent for a GPS update (trip
event kind location), that the hint's fields, SSE id and reconnect rule are kept, the released text kept (Rule 21), that no
other key was added, the openapi copy and CONTRACT.md. Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 127), 'version 0.18.127 or later'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']

bs = c['bookedRideSeen']
r = bs['riderTripEvent']
assert r.startswith('v0.18.127 (S7 W2 Q119') and '"All except GPS (Rec.)"' in r, 'riderTripEvent: source'
assert 'EXCEPT a GPS update (trip event kind location' in r, 'riderTripEvent: no hint for location'
assert 'every status change' in r and 'the rider app needs no change' in r, 'riderTripEvent: other events still sent'
assert "{ eventId, kind: 'rider_trip_changed', tripId, occurredAt, serverTime }" in r and 'Last-Event-ID stays that version' in r, 'riderTripEvent: fields and SSE id kept'
assert 'hints are not replayed' in r and 'not the first connect' in r, 'riderTripEvent: reconnect rule kept'
rb = bs['riderTripEventBefore0_18_127']
assert rb.startswith('Replaced in v0.18.127 (kept, Rule 21): P21 / B-n: GET /rider/config/stream also carries rider_trip_changed') and 'for every event of any trip of the signed-in rider' in rb, 'released text kept'
assert list(bs) == ['note', 'activeTrip', 'liveWins', 'driverChanged', 'noLateMessage', 'riderTripEvent', 'riderTripEventBefore0_18_127', 'pollFallback', 'pollSeconds', 'pollBackoff', 'leaveNowName', 'rulesSource', 'versionRetry', 'admin'], 'bookedRideSeen: only the released key added'

d = S['RiderTripEvent']['description'].replace('\n', ' ')
assert 'v0.18.127 (contract.json#bookedRideSeen.riderTripEvent): not sent for a GPS update' in d, 'openapi RiderTripEvent'
assert S['RiderTripEvent']['properties']['kind']['const'] == 'rider_trip_changed', 'openapi kind unchanged'

t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.148: the v0.18.127 note moved to CHANGELOG.md word for word
n127 = next(l for l in tc.split('\n') if l.startswith('v0.18.127 (S7 W2 Q119'))
assert 'follows v0.18.126)' in n127 and 'riderTripEventBefore0_18_127' in n127, 'CONTRACT.md v0.18.127 note'
assert "for every event of the rider's trips except a GPS update (kind `location`, v0.18.127)" in t, 'CONTRACT.md P21 line'
# the move (Rule 25 size, Rule 21 word for word): the v0.18.120 note and the old pointer line now only in CHANGELOG.md
import hashlib
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n120 = next(l for l in cl if l.startswith('v0.18.120 (S4 wave B1;'))
assert '\n' + n120 not in t and hashlib.sha256(n120.encode()).hexdigest() == '8abc4e1c079a09bec781ed29a7b4b33869bcf767c0ce4d5ac46398cae9bd1680', 'v0.18.120 note moved word for word'
j = cl.index(n120)
assert cl[j - 2].startswith('v0.18.127 (S7 W2 Q119; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.119 and before (the v0.18.119 note moved in v0.18.126,'), 'old pointer line kept in CHANGELOG.md'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.120 and before (the v0.18.120 note moved in v0.18.127, the v0.18.119 note in v0.18.126, the v0.18.118 note in v0.18.125,' in t + ch, 'new pointer line (kept in CHANGELOG.md since v0.18.128)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.127 rider hint without GPS updates ok')

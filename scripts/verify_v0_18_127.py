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
assert '\nv0.18.127 (S7 W2 Q119' in t and 'riderTripEventBefore0_18_127' in t, 'CONTRACT.md v0.18.127 note'
assert "for every event of the rider's trips except a GPS update (kind `location`, v0.18.127)" in t, 'CONTRACT.md P21 line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.127 rider hint without GPS updates ok')

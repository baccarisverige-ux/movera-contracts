#!/usr/bin/env python3
"""v0.18.152 (booked ride shown like a normal ride once its search starts; owner 2026-11-21 15:00 (A) + (B), Rules
decisions/session-2026-11-06.md): bookedRideSeen.activeTrip + searchSeen, bookLater.liveFixes.driverShown, the released
texts kept (Rule 21), the openapi copy (part 1720), the CONTRACT.md notes, and the v0.18.127 note moved word for word to
CHANGELOG.md (Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 152), 'version 0.18.152 or later'
b = c['bookedRideSeen']
keys = list(b)
assert keys.index('activeTripBefore0_18_152') == keys.index('activeTrip') + 1 and keys.index('searchSeen') == keys.index('activeTrip') + 2, 'bookedRideSeen key order'
a = b['activeTrip']
assert a.startswith('v0.18.152 (owner 2026-11-21 15:00 (A)') and '(status searching, offered or accepted) and no list driver holds it or ever held it' in a, 'activeTrip: search window'
assert 'the trip reached driver_to_pickup' in a and 'owner Q2 2026-11-05: the rider sees nothing' in a, 'activeTrip: started rule and Q2 kept'
ab = b['activeTripBefore0_18_152']
assert ab.startswith('Replaced in v0.18.152 (kept, Rule 21): GET /rider/trips/active returns the rider') and 'whose driver has started driving to the pickup at least once' in ab, 'released activeTrip kept'
s = b['searchSeen']
assert list(s) == ['note', 'rule', 'listHeld', 'givenBack', 'push', 'riderApp', 'admin', 'driverApp'], 'searchSeen keys'
assert 'no migration; no admin setting' in s['note'], 'searchSeen note'
assert 'EXACTLY like a normal ride' in s['rule'] and 'ONLY the booked card' in s['rule'], 'rule (A) + (B)'
assert 'trips.reservation.listHeld' in s['listHeld'] and 'owner Q7' in s['listHeld'] and 'stored before v0.18.152' in s['listHeld'] and 'Never in any API view' in s['listHeld'], 'listHeld'
assert 'ONE push only' in s['push'] and 'moment driver_found' in s['push'] and 'NO reservation_driver_found' in s['push'], 'push once'
assert 'never \'free\'' in s['riderApp'] and "never shows 'No driver nearby'" in s['riderApp'] and 'TripProjection.driverAssigned' in s['riderApp'], 'rider app'
assert s['admin'].startswith('Admin unchanged') and s['driverApp'].startswith('Driver app unchanged'), 'admin / driver unchanged'
lf = c['bookLater']['liveFixes']
lk = list(lf)
assert lk.index('driverShownBefore0_18_152') == lk.index('driverShown') + 1, 'driverShownBefore0_18_152 right after driverShown'
assert lf['driverShown'].startswith('v0.18.152 (bookedRideSeen.searchSeen): the rider sees the driver') and 'from the accept on, like a normal ride' in lf['driverShown'], 'driverShown'
assert lf['driverShownBefore0_18_152'] == "Replaced in v0.18.152 (kept, Rule 21): Owner D: the rider sees the driver (name, photo, car: TripProjection.driver) only from driver_to_pickup on; while a driver holds the booked ride for later the rider view has driverAssigned true and no driver details, and reservation_driver_found names nobody. The admin switch 'Rider sees the driver at once' becomes this fixed rule.", 'released driverShown kept word for word'
spec = yaml.safe_load(open('openapi.yaml'))
d = spec['paths']['/rider/trips/active']['get']['description']
assert 'v0.18.152 (contract.json#bookedRideSeen.searchSeen)' in d and 'no list driver holds or ever held' in d, 'openapi active trip'
tp = spec['components']['schemas']['TripProjection']
assert tp['properties']['driverAssigned']['type'] == 'boolean' and 'driverAssigned' not in tp.get('required', []), 'TripProjection.driverAssigned optional'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.152 (booked ride shown like a normal ride once its search starts;' in t, 'CONTRACT.md note'
n152 = next(l for l in t.split('\n') if l.startswith('v0.18.152 (booked ride shown like a normal ride once its search starts;'))
assert 'follows v0.18.132' in n152 and '`contract.json#bookedRideSeen.searchSeen`' in n152, 'CONTRACT.md note text'
assert t.count('- **Active trip**: `GET /rider/trips/active`') == 1 and 'v0.18.152 (`bookedRideSeen.searchSeen`): also a booked trip being searched or accepted' in t, '§53 line (once)'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n127 = next(l for l in cl if l.startswith('v0.18.127 (S7 W2 Q119'))
assert '\n' + n127 not in t and hashlib.sha256(n127.encode()).hexdigest() == 'b51a0ff2ebb7016f49c9a557fb973e2a146ceaece339a99b3829d3760b5e644e', 'v0.18.127 note moved word for word'
assert cl.count(n127) == 1, 'v0.18.127 note once in CHANGELOG.md'
j = cl.index(n127)
assert cl[j - 2].startswith('v0.18.152 (booked ride shown like a normal ride; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '500ff2fd72593fe8c33c06d0cb1634754ea5da6aa47af9bb54ceee2fa8ded620', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.127 and before (the v0.18.127 note moved in v0.18.152, the v0.18.126 note in v0.18.132,' in t, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.152 booked ride shown like a normal ride ok')

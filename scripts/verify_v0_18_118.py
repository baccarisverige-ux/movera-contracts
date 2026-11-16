#!/usr/bin/env python3
"""v0.18.118 (the contract text recent jobs owed; Rules audits/impact/contract-0-18-118.md): wording only, plus `country` on
config History / Restore (a real server parameter, server branch ...-cfgundo fad59d5). Checks the J8b paid-movera / owed
text (j8b-supervisor gate C1), the long stop on a repeated fix (longstop-frozen-fix Round 2, supervisor SF-R2-3), the
ride-check scan only with the rider on board (contract chain supervisor SF2), History / Restore with country
(country-undo), the inbox tie-break direction (A04 SF-A2), the rider's early end (S13 SF-S1), that no other field was
added, and CONTRACT.md. Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 118), 'version 0.18.118 or later'
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']

# --- J8b (gate C1): paidMovera / owed
do = c['debtModel']['driverOwes']
pm = do['paidMovera']
assert "Any amount left over becomes one UNLINKED entry, counted in the next payout's amount and lines" in pm, 'v0.18.97 text kept (Rule 21)'
assert pm.endswith(' Answer: the fresh OwingDriver.') and 'j8b-supervisor.md' in pm and '336b1dc' in pm, 'paidMovera v0.18.118 source'
assert 'linked to that payout AFTER it was made' in pm and 'less its own paid_to_movera line' in pm, 'paidMovera: rest = money linked after the payout was made'
assert 'the next payout MADE for him' in pm and 'dated at or after its period end, oldest first (time, then entry id), up to what brings it to 0' in pm, 'paidMovera: the next payout made pulls later entries'
assert 'may be split in two' in pm and 'same time' in pm and 'whole minor units, same total' in pm, 'paidMovera: the split'
assert 'v0.18.118' in do['owed'] and 'linked to it after it was made' in do['owed'] and 'less its own paid_to_movera line' in do['owed'], 'owed: the carried rest'
assert set(do) == {'note', 'owed', 'limit', 'cashOffers', 'homeLine', 'adminList', 'paidMovera', 'paidMoveraBefore0_18_106', 'paidMoveraBefore0_18_97', 'fleetEarnings', 'reasonMax'}, 'driverOwes: no key added'
assert 'the next payout MADE for him' in P['/admin/drivers/{driverId}/paid-movera']['post']['description'], 'openapi paid-movera text'

# --- long stop on the same fix (S7 SF-2 round 2, SF-R2-3)
rc = c['onTrip']['rideCheck']
ls = rc['detection']['long_stop']
assert 'ea0cd91' in ls and 'SF-R2-3' in ls and 'sends again unchanged' in ls, 'long_stop: same fix, source'
assert 'A gap of up to 2 x scanEverySeconds between two sends is counted; a longer one starts the count again.' in ls, 'long_stop: SF-R2-3 gap words'
assert 'silence is never standing time' not in ls, 'long_stop: the too-strong round-2 words are not used (SF-R2-3)'
assert 'skipped if the fix said the car was moving (moving true, or speedMps ≥ 1)' in ls, 'long_stop: skip if the fix said moving'
assert 'only when stopMinutes is below about 10' in ls and 'accuracy ≤ 50 m' in ls, 'long_stop: 10-minute limit, accuracy'
assert 'v0.18.118' in rc['detection']['off_route'] and 'also when the trip has no other fix in the last stopMinutes + 2 minutes' in rc['detection']['off_route'], 'off_route note'
assert 'below about 10' in rc['settings']['fields']['stopMinutes'] and 'Keep, note at setting' in rc['settings']['fields']['stopMinutes'], 'stopMinutes 10-minute limit'
scan = c['driverHome']['locationSend']['rideCheckScan']
assert 'every batch with at least one fix taken books' in scan, 'v0.18.117 rideCheckScan text kept'
assert 'with the rider on board (rider_onboard, in_trip or approaching_dropoff' in scan and 'counts as standing time for long_stop, unless the fix said the car was moving' in scan, 'rideCheckScan: on board only; same fix'
assert list(c['driverHome']['locationSend'].keys()) == ['note', 'newFix', 'rideCheckScan', 'idempotencyKey'], 'locationSend: no key added'
assert any('below about 10' in (s.get('properties', {}).get('stopMinutes', {}).get('description') or '') for s in S.values() if isinstance(s, dict)), 'openapi stopMinutes'

# --- config History / Restore take a country (country-undo)
ph = c['pricingHistory']
assert 'fad59d5' in ph['list'] and 'exactly one of zoneId or country' in ph['list'] and 'carries country instead of zoneId' in ph['list'], 'pricingHistory.list'
assert '{ zoneId | country, version, expectedVersion, note? }' in ph['restore'], 'pricingHistory.restore'
hist = P['/admin/config/{doc}/history']['get']
refs = [p.get('$ref', '').split('/')[-1] for p in hist['parameters']]
assert 'ConfigZoneId' in refs and 'ConfigCountry' in refs and not any(p.get('name') == 'zoneId' for p in hist['parameters']), 'History: zoneId or country'
he, rcmd = S['ConfigHistoryEntry'], S['ConfigRestoreCommand']
assert he['properties']['country'] == {'$ref': '#/components/schemas/CountryCode'} and 'zoneId' in he['properties'] and 'zoneId' not in he['required'], 'ConfigHistoryEntry: zoneId or country'
assert sorted(he['properties']) == sorted(['doc', 'zoneId', 'country', 'version', 'publishedAt', 'publishedBy', 'note', 'action', 'restoredFrom', 'document']), 'ConfigHistoryEntry: only country added'
assert rcmd['required'] == ['expectedVersion', 'version'] and sorted(rcmd['properties']) == sorted(['expectedVersion', 'zoneId', 'country', 'version', 'note']), 'ConfigRestoreCommand: zoneId or country'
assert 'exactly one of zoneId or country' in rcmd['description'], 'ConfigRestoreCommand description'

# --- A04 SF-A2, S13 SF-S1
io = c['supportDesk']['inboxOrder']['rule']
assert 'ties by ticketId; then' in io and 'ascending in the first part (waitingSince oldest first), descending in the second' in io, 'inboxOrder tie-break direction'
co = c['inAppCalls']['callOpenUntil']
assert "the rider's early end (POST /trips/{tripId}/end-early, status cancelled_by_rider)" in co and "A driver's end before the drop-off is a completed trip" in co, 'callOpenUntil: the rider\'s early end'

# --- k117 SF4: verify_v0_18_112.py reads the moved A04 note from CONTRACT.md + CHANGELOG.md
v112 = open('scripts/verify_v0_18_112.py', encoding='utf-8').read()
assert "'which is not merged yet' not in tc" in v112 and "'which is not merged yet' not in t," not in v112, 'verify_v0_18_112.py uses tc (SF4)'

# --- CONTRACT.md
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.118 (the contract text recent jobs owed' in t and 'follows v0.18.117)' in t, 'CONTRACT.md v0.18.118 note'
assert 'v0.18.118: only while the rider is on board' in t, 'CONTRACT.md §12 scan on board'
assert 'v0.18.118: both name exactly one of `zoneId` or `country`' in t, 'CONTRACT.md §16 History / Restore'
assert 'found only when `stopMinutes` is below about 10' in t and 'skipped if the fix said the car was moving' in t, 'CONTRACT.md §35 long stop'
assert 'v0.18.118: ties by `ticketId` ascending in the first part, descending in the second.' in t, 'CONTRACT.md §37 tie-break'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print("v0.18.118 owed contract text ok")

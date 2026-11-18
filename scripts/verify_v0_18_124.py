#!/usr/bin/env python3
"""v0.18.124 (C10 empty driver history; owner G11 Q10 "Load from server (Recommended)", full-audit Q9 "Yes, on the server
(Recommended)"; Rules decisions/driver-g11.md, audits/impact/findings-g18-g23-2026-11-17.md): checks GET /driver/trips
(own ended trips, paged, statuses, earned = the earnings entries), the openapi copy and CONTRACT.md. Run by
scripts/verify.sh from the repository root (Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 124), 'version 0.18.124 or later'
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']
h = c['driverTripHistory']
assert list(h) == ['note', 'endpoint', 'statuses', 'statusRule', 'item', 'earned', 'cashCollected', 'scale', 'clients'], 'driverTripHistory keys'
assert 'Load from server (Recommended)' in h['note'] and 'Yes, on the server (Recommended)' in h['note'], 'owner source'
assert h['statuses'] == ['completed', 'cancelled_by_rider', 'cancelled_by_driver', 'cancelled_by_admin', 'cancelled_by_system', 'no_show'], 'statuses'
ts = set(c['enums']['tripStatus']) if 'enums' in c and 'tripStatus' in c['enums'] else None
if ts is not None:
    assert set(h['statuses']) <= ts, 'statuses are trip statuses'
assert 'limit 1-50, default 20' in h['endpoint'] and 'nextCursor' in h['endpoint'], 'paging'
assert 'reason invalid_status' in h['statusRule'], 'bad status reason'
for k in ('trip', 'pickup_pay', 'fee_share', 'tip', 'adjustment', 'bonus'):
    assert k in h['earned'], 'earned kind ' + k
assert 'endedAt' in h['item'] and 'distanceMeters' in h['item'], 'item: endedAt, distanceMeters'
assert 'GET /driver/earnings' in h['earned'] and "Never the rider's fare" in h['earned'], 'earned = earnings net'
assert 'Rule 33' in h['scale'], 'Rule 33'
g = P['/driver/trips']['get']
assert g['operationId'] == 'listDriverTrips' and g['x-actor'] == ['driver'], 'openapi op'
names = [p.get('name') or p.get('$ref', '').rsplit('/', 1)[-1] for p in g['parameters']]
assert names[:5] == ['Cursor', 'limit', 'status', 'From', 'To'], names
lim = g['parameters'][1]['schema']
assert (lim['minimum'], lim['maximum'], lim['default']) == (1, 50, 20), 'limit schema'
assert g['parameters'][2]['schema']['items']['enum'] == h['statuses'], 'status enum'
assert g['responses']['200']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/DriverTripHistoryPage'}, 'page'
item = S['DriverTripHistoryItem']['allOf']
assert item[0] == {'$ref': '#/components/schemas/TripProjection'} and item[1]['required'] == ['earned'], 'item'
assert set(item[1]['properties']) == {'earned', 'cashCollected', 'endedAt', 'distanceMeters'}, 'item fields'
md = open('CONTRACT.md').read()
mdc = md + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.130: the v0.18.124 note moved to CHANGELOG.md (Rule 25 size, Rule 21 word for word)
assert md.startswith('# Movera shared contract v0.18.') and '**`GET /driver/trips`**' in mdc and 'contract.json#driverTripHistory' in mdc, 'CONTRACT.md note (in CHANGELOG.md since v0.18.130)'
n124 = next(l for l in mdc.split('\n') if l.startswith('v0.18.124 ('))  # its own note, wherever later versions put theirs (was line 3; changed by 0.18.125)
assert 'follows v0.18.123' in n124, 'CONTRACT.md v0.18.124 note follows v0.18.123'
# the move (Rule 25 size, Rule 21 word for word): the v0.18.117 note and the old pointer line now only in CHANGELOG.md
import hashlib
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n117 = next(l for l in cl if l.startswith('v0.18.117 (S7 notes + alert-cap MF3; owner'))
assert '\n' + n117 not in md and hashlib.sha256(n117.encode()).hexdigest() == '6e6548f72978dcdf782046930753121e1aca1c8aad76e69b8feb6ee0667a4cde', 'v0.18.117 note moved word for word'
j = cl.index(n117)
assert cl[j - 2].startswith('v0.18.124 (C10; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.116 and before'), 'old pointer line kept in CHANGELOG.md'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.117 and before (the v0.18.117 note moved in v0.18.124, the v0.18.116 note in v0.18.123,' in md + ch, 'the v0.18.124 pointer line (kept in CHANGELOG.md since v0.18.125)'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.124 ok')

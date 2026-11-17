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
assert set(item[1]['properties']) == {'earned', 'cashCollected'}, 'item fields'
md = open('CONTRACT.md').read()
assert md.startswith('# Movera shared contract v0.18.') and '**`GET /driver/trips`**' in md and 'contract.json#driverTripHistory' in md, 'CONTRACT.md note'
print('v0.18.124 ok')

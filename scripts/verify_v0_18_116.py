#!/usr/bin/env python3
"""v0.18.116 (BQ-S10, owner 2026-11-02 Q1 "Build it for real (Recommended)", Rules decisions/driver-g14.md:11, and the S10
button answers of 2026-11-15, same file): the rider's live trip link. Checks the fixed public allow-list (no phone number,
name, address, destination, fare or rating can be sent), the routes, the limits, the 30 days and the per-zone switch.
Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, re, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 116), 'version 0.18.116 or later'
assert c['configDefaults']['shareTripOn'] is True, 'configDefaults.shareTripOn is true (owner Q6: default on)'
st = c['shareTrip']
assert 'driver-g14.md:11' in st['note'] and 'Build it for real' in st['note'] and 'migration 0114' in st['note'], 'shareTrip owner decision'
assert sorted(st['owner'].keys()) == ['Q-A', 'Q-B', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7'], 'the 7 owner answers + Q-A, Q-B'
assert st['statuses'] == c['safety']['sos']['riderStatuses'] == c['tripStatus']['driverAssigned'], 'share only while a driver is assigned'
assert st['maxHours'] == 6 and st['retentionDays'] == 30, '6 h cap, rows kept 30 days (owner Q7)'
assert 'tripStatus.terminal' in st['ends'] and 'zone' in st['ends'] and 'stops sharing' in st['ends'] and '410' in st['ends'], 'the four ends'
assert 'SHA-256' in st['link']['token'] and 'never the token' in st['link']['token'] and 'never written to a log' in st['link']['token'], 'token is hashed and never logged'
assert re.fullmatch(st['link']['tokenPattern'], 'A' * 22), 'token pattern'
pub = st['public']
# The allow-list, exactly. A new field must be added here on purpose.
assert pub['fields'] == ['state', 'phase', 'car', 'eta', 'position', 'updatedAt', 'refreshSeconds'], 'public fields'
assert pub['car'] == ['make', 'model', 'color', 'plate'] and pub['eta'] == ['minutes', 'target', 'arriveAround'] and pub['position'] == ['lat', 'lng', 'at'], 'public sub-fields'
assert pub['refreshSeconds'] == 20 and pub['positionLink'] == c['sosContactsSms']['positionLink'], 'refresh 20 s (owner Q1); the Maps link form'
assert [s for p in pub['phases'].values() for s in p] == st['statuses'], 'every share status has one phase'
# Supervisor MF-1 / SF-1: a queued trip never shows the car's spot; no driver = "searching", not ended.
assert pub['queuedPhase'] == 'queued' and 'next_after_trip_id' in pub['positionRule'] and 'position is null by rule (1)' in pub['positionRule'], 'queued trip: no position'
# Owner Q-A / Q-B (2026-11-15): no position before the rider is in the car, none within 500 m of the drop-off.
assert pub['hideWithinMetersOfDropoff'] == 500 and 'hideWithinMetersOfDropoff' in pub['positionRule'], 'Q-B: hide the last 500 m'
assert "Hide until rider is in" in pub['positionRule'] and 'tripStatus.riderOnboard' in pub['positionRule'] and pub['phases']['on_trip'] == c['tripStatus']['riderOnboard'], 'Q-A: position only with the rider in the car'
assert 'the drop-off, the stops and the distances are never sent' in pub['positionRule'], 'Q-B: nothing about the drop-off or the stops is sent'
assert 'every middle stop' in pub['positionRule'] and 'session decision' in pub['positionRule'] and 'no coordinates for hides the position' in pub['positionRule'], 'the same 500 m around every middle stop (session decision, not an owner answer)'
assert all('noPosition' not in st['texts'][l] for l in ('sv', 'fr', 'en')), 'no position line when the position is hidden' 
assert "state: 'searching'" in pub['searching'] and 'NOT ended' in pub['searching'], 'no driver = searching'
assert 'load-shed 503' in pub['headers'], 'headers on every answer of the share paths'
assert 'fixed label' in st['link']['token'], 'the link key is derived' 
never = ' '.join(pub['never'])
for w in ('phone number', 'name', 'addresses', 'destination', 'fare', 'rating', 'photo', 'tripId'):
    assert w in never, 'never list: ' + w
for h in ('no-store', 'no-referrer', 'noindex, nofollow', 'nosniff', "default-src 'none'"):
    assert h in pub['headers'], 'public headers: ' + h
assert 'no Open Graph' in pub['preview'], 'no preview tags with trip data'
lim = st['limits']
assert (lim['maxActivePerTrip'], lim['perAddressPerMinute'], lim['perTokenPerMinute']) == (3, 60, 30), 'limits'
assert 'shed first' in lim['note'] and 'never in the safety set' in lim['note'] and 'share_too_many' in lim['note'], 'limits note'
for lang in ('sv', 'fr', 'en'):
    tx = st['texts'][lang]
    assert set(tx) == set(st['texts']['en']), lang + ' texts: same keys as en'
    assert '{url}' in tx['message'] and '{min}' in tx['arriving'] and '{time}' in tx['around'], lang + ' placeholders'
assert 'invalid_document' in st['setting'] and 'features.shareTrip' in st['setting'] and 'Dispatch › Safety' in st['setting'], 'setting'
assert 'shareTrips' in st['contacts'] and st['driver'].startswith('No change'), 'contacts flag; driver not changed'
assert 'retentionDays' in st['privacy'] and '{ tripId, count }' in st['privacy'], 'privacy'

spec = yaml.safe_load(open('openapi.yaml'))
assert spec['info']['version'] == c['version'], 'openapi version'
S, P = spec['components']['schemas'], spec['paths']
sp = P['/rider/trips/{tripId}/share']
assert set(sp) == {'post', 'get', 'delete'} and all(o['x-actor'] == ['rider'] for o in sp.values()), 'rider share routes'
assert '201' in sp['post']['responses'] and '204' in sp['delete']['responses'], 'create 201, stop 204'
assert 'url' in S['TripShareLink']['required'] and 'url' not in S['TripShareItem']['properties'], 'the list has no url'
assert S['TripShareList']['properties']['items']['maxItems'] == 3, 'at most 3 live links'

def closed(node, path, out):
    """Every object under the public schema is closed, and collects every property name."""
    if not isinstance(node, dict):
        return
    if node.get('type') == 'object':
        assert node.get('additionalProperties') is False, path + ': additionalProperties must be false'
        for k, v in node['properties'].items():
            out.add(k); closed(v, path + '.' + k, out)
    for v in node.get('oneOf', []):
        closed(v, path, out)
names = set()
ps = S['PublicTripShare']
closed(ps, 'PublicTripShare', names)
assert list(ps['properties']) == pub['fields'] and ps['required'] == pub['fields'], 'PublicTripShare = the allow-list'
assert names == set(pub['fields']) | set(pub['car']) | set(pub['eta']) | set(pub['position']), 'PublicTripShare carries only allow-listed names: ' + str(sorted(names))
FORBIDDEN = re.compile(r'phone|name|address|pickup|dropoff|destination|stops|fare|price|total|payment|tip|rating|photo|rider|driver|Id$|zone', re.I)
bad = [x for x in names if FORBIDDEN.search(x)]
assert not bad, 'forbidden field in the public answer: ' + str(bad)
assert set(re.findall(r'#/components/schemas/(\w+)', json.dumps(ps))) <= {'Timestamp'}, 'the public schema refers to no other schema'
assert ps['properties']['phase']['enum'] == list(pub['phases']) + ['queued'], 'phase enum'
se = S['PublicTripShareSearching']
assert list(se['properties']) == ['state', 'updatedAt', 'refreshSeconds'] == se['required'] and se['additionalProperties'] is False, 'searching body: no trip data'
assert P['/share/{token}']['get']['responses']['200']['content']['application/json']['schema'] == {'oneOf': [{'$ref': '#/components/schemas/PublicTripShare'}, {'$ref': '#/components/schemas/PublicTripShareSearching'}]}, '200 = live or searching'
assert list(S['PublicTripShareEnded']['properties']) == ['state', 'reason'] and S['PublicTripShareEnded']['additionalProperties'] is False, 'ended body'
for path, ok in (('/share/{token}', 'application/json'), ('/s/{token}', 'text/html')):
    o = P[path]['get']
    assert list(P[path]) == ['get'] and o['security'] == [] and o['x-public'] is True and o['x-actor'] == [], path + ' is public, read-only'
    assert set(o['responses']) == {'200', '404', '410', '429', '503'}, path + ' answers'
    assert ok in o['responses']['200']['content'], path + ' content'
    assert o['parameters'][0]['schema']['pattern'] == st['link']['tokenPattern'], path + ' token'
assert P['/s/{token}']['get']['servers'][0]['url'].endswith('.invalid'), '/s/{token} is outside /api/v1'
ec = S['EmergencyContact']
assert ec['properties']['shareTrips']['type'] == 'boolean' and 'shareTrips' not in ec['required'], 'EmergencyContact.shareTrips optional'
rc = S['RiderAppConfig']['properties']
assert rc['shareTrip']['properties']['on']['type'] == 'boolean' and rc['shareTrip']['properties']['on']['default'] is True, 'RiderAppConfig.shareTrip.on default true'
assert rc['features']['properties']['shareTrip']['type'] == 'boolean', 'features.shareTrip stays'
assert 'shareTrip' not in S['DriverAppConfig']['properties'], 'the driver document has no shareTrip'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.116 (BQ-S10' in t and 'follows v0.18.115)' in t, 'CONTRACT.md v0.18.116 note'
assert '\n## 94. Share my trip' in t and 'shareTrip: { on },   // v0.18.116' in t and '`rider.shareTrip.on`' in t, 'CONTRACT.md §94, §6, §5'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print("v0.18.116 share my trip ok")

#!/usr/bin/env python3
"""v0.18.122 (L20 stream; owner 2026-11-17 "Yes, with switch (Rec.)", Rules decisions/session-2026-11-06.md, design
audits/load/l20-1-design.md section 3): GET /driver/stream is the offer feed and the driver config stream on one
connection, with the events of both unchanged and the id '<offer sequence>.<config version>'; the driver app uses it only
while DriverAppConfig.realtime.oneStream is true (default false, admin switch per zone, off until tested); the two old
routes and the trip stream are unchanged; the rider app is not affected. Run by scripts/verify.sh (own file, Rule 25)."""
import json
import yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 122), 'version 0.18.122 or later'

o = c['driverOneStream']
assert list(o) == ['note', 'route', 'eventId', 'resume', 'close', 'zone', 'setting', 'server', 'driver', 'rider', 'admin'], 'driverOneStream keys'
assert "owner 2026-11-17 'Yes, with switch (Rec.)'" in o['note'], 'source'
r = o['route']
assert r.startswith('GET /driver/stream is the offer feed and the config stream on one connection: the events of GET /driver/offers/stream and GET /driver/config/stream, unchanged.'), 'design wording'
assert "id is '<offer sequence>.<config version>'." in r and 'The trip stream GET /trips/{tripId}/events is unchanged.' in r, 'design wording (id, trip stream)'
assert 'opens neither of the two' in r and 'false or missing: the two streams as before' in r, 'design wording (switch)'
assert "'41.7'" in o['eventId'] and 'kind' in o['eventId'], 'id example and kind'
assert 'Last-Event-ID' in o['resume'] and 'exactly once' in o['resume'] and 'higher' in o['resume'], 'resume both halves'
assert 'reconnectClose' in o['close'] and 'streamClose' in o['close'], 'close rules as the config stream'
assert 'zoneId' in o['zone'], 'zone rule kept'
assert 'DriverAppConfig.realtime.oneStream' in o['setting'] and 'default false' in o['setting'], 'setting'
assert c['configDefaults']['driverOneStream'] is False, 'configDefaults.driverOneStream false'
assert '404' in o['driver'] and 'two streams' in o['driver'], 'driver falls back to two on 404'
assert o['rider'].startswith('Not affected'), 'rider not affected'
assert 'One live connection per driver phone' in o['admin'] and 'default off' in o['admin'], 'admin switch'
assert 'invalid_document' in o['server'] and 'no migration' in o['server'], 'server rule'

s = yaml.safe_load(open('openapi.yaml'))
p = s['paths']['/driver/stream']['get']
assert p['operationId'] == 'streamDriverOneStream' and 'text/event-stream' in p['responses']['200']['content'], '/driver/stream SSE'
res = lambda x: s['components']['parameters'][x['$ref'].split('/')[-1]] if '$ref' in x else x
names = [res(x).get('name') for x in p['parameters']]
assert 'zoneId' in names and 'after' in names and 'Last-Event-ID' in names, '/driver/stream params'
for old in ('/driver/offers/stream', '/driver/config/stream'):
    assert old in s['paths'], old + ' stays (Rule 21)'
rt = s['components']['schemas']['DriverAppConfig']['properties']['realtime']
assert rt['properties']['oneStream']['type'] == 'boolean' and rt['properties']['oneStream']['default'] is False, 'DriverAppConfig.realtime.oneStream'
assert 'realtime' not in s['components']['schemas']['RiderAppConfig']['properties'], 'rider document unchanged'

t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.128: the v0.18.122 note moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.122 (L20 stream;' in tc and 'follows v0.18.121)' in tc, 'CONTRACT.md v0.18.122 note'
assert len(t.split('\n')) <= 1501, 'CONTRACT.md at most 1500 lines'
print('v0.18.122 ok')

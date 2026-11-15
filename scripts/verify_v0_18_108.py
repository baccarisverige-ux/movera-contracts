#!/usr/bin/env python3
"""v0.18.108 job C9b (owner 2026-11-02 "At the pickup AND at stops", Rules decisions/driver-g7.md:84): auto arrival and the
waiting clock at middle stops; the stop tap carries a position check; the stop wait stands still while the driver is away.
Run by scripts/verify.sh from the repository root (moved out of verify.sh unchanged, Rule 25: verify.sh stays under
1,500 lines). The money and tap cases are replayed by reference_check.py (fixtures/auto_arrive.json)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 108), 'version 0.18.108 or later'
aa = c['autoArrive']; st = aa['stops']; sw = c['stopWaits']
assert 'driver-g7.md:84' in st['note'] and 'At the pickup AND at stops' in st['note'] and 'no migration' in st['note'], 'autoArrive.stops owner note'
assert 'Pickup only in this version' not in aa['note'] and 'Pickup only in this version' in aa['noteBefore0_18_108'], 'autoArrive.note no longer pickup only (old kept, Rule 21)'
assert 'later version' not in aa['notInThisVersion'] and 'later version' in aa['notInThisVersionBefore0_18_108'], 'notInThisVersion adjusted (old kept)'
assert 'autoArriveMeters' in st['distances'] and 'leaveMeters' in st['distances'] and 'at the pickup and at stops' in st['distances'], 'same distances at stops'
assert 'autoArrive.confirm' in st['auto'] and '15 km/h' in st['auto'] and 'in_trip or approaching_dropoff' in st['auto'] and 'NEXT stop' in st['auto'] and 'arrivedBy auto' in st['auto'] and 'pickup_geofence' in st['auto'], 'auto stop arrival (2-fix slow confirm, in order)'
assert 'No version change' in st['away'] and 'farther than leaveMeters' in st['away'] and 'first fix of the confirming pair' in st['away'], 'away at an open stop'
assert "within the trip's leaveMeters" in st['back'] and 'not_at_stop' in st['back'] and 'pausedSeconds grows' in st['back'] and 'pauseCount by 1' in st['back'] and 'stop_already_arrived' in st['back'], 'back tap within leaveMeters'
assert st['tapMaxMeters'] == 300 and st['minContractVersion'] == '0.18.108' and '300 m' in st['tap'] and 'not_at_stop' in st['tap'] and 'position_stale' in st['tap'] and 'X-Contract-Version ≥ 0.18.108' in st['tap'] and 'older app is never stuck' in st['tap'], 'stop tap position check'
assert 'v0.18.108 reason: not_at_stop' in c['errors']['reason'], 'reason not_at_stop listed'
assert 'pausedSeconds' in st['money'] and 'stopFreeWaitMin × 60' in st['money'] and 'never costs the rider' in st['money'], 'stop money'
assert '(min(until, stops[i].away.since while away) − arrivedAt) − pausedSeconds' in sw['charge'] and 'stopFreeWaitMin × 60' in sw['charge'] and 'TND: 3 decimals' in sw['charge'], 'stopWaits.charge formula'
for k in ('arrive', 'charge', 'projection'):
    assert k + 'Before0_18_108' in sw, 'Rule 21: stopWaits.' + k + ' first wording kept'
assert sw['chargeBefore0_18_108'].startswith('stop_waiting = Σ (leftAt − arrivedAt)'), 'old charge kept word for word'
assert 'not_at_stop' in sw['arrive'] and 'location' in sw['arrive'] and sw['arrive'].startswith(sw['arriveBefore0_18_108']), 'stopWaits.arrive extends the old text'
assert 'pausedSeconds' in c['arrivedWaiting']['rules']['stops'] and 'stopsBefore0_18_108' in c['arrivedWaiting']['rules'], 'arrivedWaiting.rules.stops follows (old kept)'
for k in ('stops[i].arrivedBy', 'stops[i].away', 'stops[i].pausedSeconds', 'stops[i].pauseCount', 'mirror'):
    assert k in st['projection'], 'projection ' + k
for k in ('driver', 'rider', 'admin', 'server'):
    assert k in st['apps'], 'apps ' + k
assert 'at the pickup and at stops' in st['apps']['admin'] and 'driverStopBack' in st['apps']['driver'] and 'No amounts' in st['apps']['rider'], 'apps wording'
assert set(st['texts']) == {'driverStopPaused', 'driverStopBack', 'riderStopPaused', 'notAtStop'}, '4 texts'
for k, t in st['texts'].items():
    assert set(t) == {'sv', 'fr', 'en'} and all(t[l].strip() for l in t), k
assert all('{leave}' in st['texts']['driverStopPaused'][l] and '{arrive}' in st['texts']['driverStopPaused'][l] for l in ('sv', 'fr', 'en')), 'driverStopPaused placeholders'
assert st['texts']['notAtStop']['en'] == 'You are not at the stop yet.' and st['texts']['riderStopPaused']['en'] == 'Waiting time paused: your driver is away from the stop.', 'texts as planned'
f = json.load(open('fixtures/auto_arrive.json'))
assert {x['currency'] for x in f['stops']} == {'SEK', 'TND'} and len(f['stops']) >= 6 and len(f['firstTap']) >= 5, 'SEK + TND stop fixtures, first-tap cases'
assert any(x['expect']['awayAtEnd'] for x in f['stops']) and any('not_at_stop' in x['expect']['taps'] for x in f['stops']) and any(x['stopFreeWaitMin'] > 0 for x in f['stops']), 'fixture coverage: leave while away, refused back tap, free minutes'
assert {x['expect'] for x in f['firstTap']} == {'ok', 'not_at_stop', 'position_stale'}, 'first tap answers'
# v0.18.108 round 2 (C9b supervisor M1, M2, S1, S2; Rules audits/impact/c9b-middle-stops-supervisor.md)
assert 'BOTH fixes of the confirming pair farther than autoArriveMeters from that open stop' in st['auto'] and "only the driver's tap marks the next stop arrived" in st['auto'] and 'not away from it' in st['auto'], 'M1: no auto next stop while still at the open stop'
ls = c['onTrip']['rideCheck']['detection']
assert 'counts as "at the stop" only while stops[i].away is absent' in ls['long_stop'] and 'tap or auto' in ls['long_stop'], 'M2: long_stop skips an open stop only while not away'
assert 'the car is not at a middle stop the driver tapped arrived at' in ls['long_stopBefore0_18_108'], 'M2: old long_stop kept (Rule 21)'
assert "old-app path" in st['tap'] and 'at any age, must be within 300 m' in st['tap'] and 'no stored fix at all the tap is taken as before' in st['tap'], 'S1: old apps check the stored fix within 300 m'
assert 'a sent location that is older never counts' in st['tap'] and 'only if that fix is fresh' in st['tap'] and 'Only when no fresh position exists but one was sent or stored' in st['tap'], 'S2: exact position_stale wording'
assert 'an old sent location never counts' in sw['arrive'] and 'position_stale only when no fresh position exists' in sw['arrive'], 'S2 in stopWaits.arrive'
assert {x['expect'] for x in f['nextStopAuto']} == {'auto', 'none'} and any(x['openStop'] and not x['openStop']['away'] and x['expect'] == 'none' for x in f['nextStopAuto']), 'M1 fixture cases'
assert any(x['contractVersion'] is None and x['expect'] == 'not_at_stop' for x in f['firstTap']) and any(x['sent'] and x['sent']['ageSeconds'] > 60 and x['expect'] == 'ok' for x in f['firstTap']), 'S1 / S2 fixture cases'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert spec['info']['version'] == c['version'], 'openapi version'
v = S['StopVisit']
assert v['properties']['arrivedBy']['enum'] == ['auto', 'tap'] and v['properties']['away']['required'] == ['since'] and v['properties']['pausedSeconds']['minimum'] == 0 and v['properties']['pauseCount']['minimum'] == 0, 'StopVisit fields'
assert all(k not in v['required'] for k in ('arrivedBy', 'away', 'pausedSeconds', 'pauseCount')), 'StopVisit additive'
sc = S['StopCommand']
assert sc['properties']['location']['allOf'] == [{'$ref': '#/components/schemas/GeoFix'}] and sc['required'] == ['expectedVersion'], 'StopCommand.location optional GeoFix'
d = ' '.join(spec['paths']['/driver/trips/{tripId}/stops/{stopIndex}/arrive']['post']['description'].split())
assert 'not_at_stop' in d and 'v0.18.108' in d, 'stop arrive path description'
d = ' '.join(spec['paths']['/driver/trips/{tripId}/stops/{stopIndex}/leave']['post']['description'].split())
assert 'away.since' in d and 'v0.18.108' in d, 'stop leave path description'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.108 (job C9b' in t and '## 93. Auto arrived and the waiting clock at middle stops' in t and 'Round 2 (M1)' in t and '**Ride check** (M2)' in t and 'Middle stops keep their taps in this version.' not in t, 'CONTRACT.md v0.18.108'
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert 'Middle stops keep their taps in this version.' in ch and 'Older version notes (v0.18.70 and before)' in ch and '\nv0.18.70 (server S4 B1.23' in ch and '\nv0.18.71 (wording fix' in ch, 'Rule 21: moved lines are in CHANGELOG.md'
assert 'Older version notes (v0.18.69 and before) are in `CHANGELOG.md`.' in ch.split('\n') and 'Older version notes (v0.18.69 and before)' not in t, 'Rule 21: the pre-v0.18.97 pointer line is kept in CHANGELOG.md'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'

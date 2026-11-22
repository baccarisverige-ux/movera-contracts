#!/usr/bin/env python3
"""v0.18.148 (SOS by press time; Rules LAUNCH-RULE.md "Queued (after freeze)" item 1, owner 2026-11-20): an SOS after the trip
ended is judged by its press time `at` (contract.json#sosPressTime), Incident.pressedAt, the openapi copy, the CONTRACT.md
notes, and the v0.18.141 note moved word for word to CHANGELOG.md (Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 148), 'version 0.18.148 or later'
sp = c['sosPressTime']
assert list(sp) == ['note', 'at', 'liveTrip', 'endedTrip', 'afterEndSeconds', 'maxAgeSeconds', 'clock', 'refusals', 'idempotency', 'incident', 'admin', 'apps', 'scenarios'], 'sosPressTime keys'
assert sp['afterEndSeconds'] == 1800 and sp['maxAgeSeconds'] == 1800, 'windows (owner: 30 min)'
assert 'p = min(at, receivedAt)' in sp['clock'] and 'never refuses' in sp['clock'], 'fast phone clock clamped, never refused'
assert 'always taken, whatever `at` says' in sp['liveTrip'], 'live trip unchanged'
assert 'trips.ended_at, else the trip' in sp['endedTrip'] and 'trips.accepted_at' in sp['endedTrip'], 'ended trip rule'
assert set(sp['refusals']) == {'sos_too_old', 'sos_not_during_trip', 'unchanged'}, 'refusal reasons'
for r in ('sos_too_old', 'sos_not_during_trip'):
    assert sp['refusals'][r].startswith('409 invalid_transition, reason ' + r), r
assert 'trip_not_live' in sp['refusals']['unchanged'] and '404 trip_not_found' in sp['refusals']['unchanged'], 'unchanged refusals'
assert 'replays the first SosReceipt (no second incident, no second SMS)' in sp['idempotency'], 'idempotency'
assert 'No admin setting' in sp['admin'] and 'Any refusal (409 any reason, 404, 403, 400) is final' in sp['apps'], 'admin / apps'
ids = [s['id'] for s in sp['scenarios']]
assert len(ids) == len(set(ids)) >= 10, 'scenarios'
exp = {s['id']: s['expect'] for s in sp['scenarios']}
assert exp['pressed_in_trip_arrives_after_end'] == 'taken' and exp['arrives_too_late'] == '409 sos_too_old' and exp['phone_clock_fast'] == 'taken' and exp['small_clock_skew'] == 'taken' and exp['arrives_at_max_age'] == 'taken' and exp['pressed_after_window'] == '409 sos_not_during_trip', 'scenario answers'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert 'pressedAt' in S['Incident']['properties'] and 'pressedAt' not in S['Incident']['required'], 'Incident.pressedAt optional'
assert 'v0.18.148 (sosPressTime.at)' in S['SosRequest']['properties']['at']['description'], 'SosRequest.at'
for p in ('/rider/trips/{tripId}/sos', '/driver/trips/{tripId}/sos'):
    d = spec['paths'][p]['post']['description']
    assert 'v0.18.148 (sosPressTime)' in d and 'sos_not_during_trip' in d, p
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.148 (SOS by press time; Rules' in t + open('CHANGELOG.md', encoding='utf-8').read(), 'CONTRACT.md note'  # the note moved to CHANGELOG.md in v0.18.153
n148 = next(l for l in (t + open('CHANGELOG.md', encoding='utf-8').read()).split('\n') if l.startswith('v0.18.148 (SOS by press time; Rules'))
assert 'follows v0.18.146)' in n148 and '`contract.json#sosPressTime`' in n148, 'CONTRACT.md note text'
assert ' v0.18.148 (`sosPressTime`): after the trip ended the SOS is judged by `at`' in t, '§15 line'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
# launch restack (plan K): this version moves the v0.18.141 note (the draft moved v0.18.127)
n141 = next(l for l in cl if l.startswith("v0.18.141 (Stripe for the driver's month"))
assert '\n' + n141 not in t and cl.count(n141) == 1, 'v0.18.141 note moved once'
assert hashlib.sha256(n141.encode()).hexdigest() == 'de88f425ebd8135e26fdd05311c46c8981b77a9dce213eb42e96b90b338cc78e', 'v0.18.141 note moved word for word'
j = cl.index(n141)
assert cl[j - 2].startswith('v0.18.148 (SOS by press time; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '961051a2d5e7b399d28808ee1c856b1ae2c3db554c61e7adce8b02715bc99d5a', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.141 and before (the v0.18.141 note moved in v0.18.148, the v0.18.140 note in v0.18.146, the v0.18.139' in t + ch, 'new pointer line (in CHANGELOG.md once a later version moves it)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.148 SOS by press time ok')

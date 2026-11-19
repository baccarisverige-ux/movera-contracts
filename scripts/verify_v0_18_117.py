#!/usr/bin/env python3
"""v0.18.117 (S7 notes + alert-cap MF3; owner Sitting W2 Q113 "Yes, skip repeats (Rec.)" and Q114 "Yes, stop storing
(Rec.)", Rules decisions/session-2026-11-06.md; Rules audits/impact/alert-cap-safety-supervisor.md MF3 + N2): wording only.
Checks the limit and order of AlertBookState.alerts, the GPS send rules of POST /driver/location and its Idempotency-Key
exception (contract.json, openapi.yaml, CONTRACT.md), that no field was added, and the note move to CHANGELOG.md
(v0.18.109-v0.18.115 notes and the old pointer line, word for word, Rule 21 / Rule 25).
Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import glob, hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 117), 'version 0.18.117 or later'

# --- contract.json: the alert list
ll = c['alertDesk']['serverDetection']['liveList']
assert [k for k in ll if k not in ('openOtherCap', 'adminLine')] == ['note', 'open', 'solvedCap', 'solved', 'order', 'more'], 'liveList keys (v0.18.131 adds openOtherCap, adminLine)'
assert ll['solvedCap'] == 1000 and 'alert-cap-safety-supervisor.md' in ll['note'] and 'MF3' in ll['note'], 'liveList note + cap'
assert 'no limit, never cut' in ll['open'], 'open alerts are never cut'
assert 'per kind the 1000 newest by solvedAt' in ll['solved'] and 'safety kinds first and then the newest solvedAt' in ll['solved'], 'solved cut'
safety = sorted(k for k, g in c['alertDesk']['kindGroups'].items() if g == 'safety')
assert safety == ['car_lost', 'ride_check', 'sos', 'sos_slow'] and 'sos, car_lost, ride_check, sos_slow' in ll['order'], 'safety kinds named'
assert ll['order'].startswith('Open before solved.') and 'then level critical, important, info, then the newest since, then alertId' in ll['order'], 'open order'
assert 'Solved: the safety kinds first, then the newest solvedAt' in ll['order'], 'solved order'
assert (ll['more'].startswith('Not built yet') and "no 'more' marker" in ll['more']) or ll['more'].startswith('v0.18.131: AlertBookState.alertsMore'), 'the marker: not built before v0.18.131, built since'

# --- contract.json: the GPS send
ls = c['driverHome']['locationSend']
assert list(ls.keys()) == ['note', 'newFix', 'rideCheckScan', 'idempotencyKey'], 'locationSend keys'
assert 'Q113' in ls['note'] and 'Q114' in ls['note'] and 'af019a4' in ls['note'] and '8857f2e' in ls['note'], 'locationSend owner answers + server lines'
assert 'only when that fix is new: measured after the driver\'s stored fix, or the first one' in ls['newFix'], 'event only for a new fix'
assert 'same measuredAt' in ls['newFix'] and 'only fills the trip trace' in ls['newFix'], 'repeat and older batch: no event'
assert 'every batch with at least one fix taken books' in ls['rideCheckScan'] and 'older batch' in ls['rideCheckScan'], 'scan on every send'
ik = ls['idempotencyKey']
assert 'never stored' in ik and 'never replayed and never 409' in ik and 'also with another body' in ik and '400' in ik, 'key checked, not stored'
assert c['headers']['Idempotency-Key'] == 'required on every mutation, 16–128 chars', 'the general header rule is unchanged'

# --- openapi.yaml
spec = yaml.safe_load(open('openapi.yaml'))
book = spec['paths']['/admin/alerts/book']['get']
assert 'v0.18.117 (alertDesk.serverDetection.liveList)' in book['description'] and ll['order'] in book['description'] and ll['more'] in book['description'], 'GET /admin/alerts/book text'
abs_ = spec['components']['schemas']['AlertBookState']
assert ll['solved'] in abs_['description'], 'AlertBookState text'
assert sorted(k for k in abs_['properties'] if k != 'alertsMore') == ['country', 'mutes', 'people', 'quiet', 'records', 'rev', 'rules', 'settings'], 'AlertBookState: no field added in v0.18.117 (alertsMore is v0.18.131)'
loc = spec['paths']['/driver/location']['post']
assert 'v0.18.117 (driverHome.locationSend)' in loc['description'] and ls['newFix'] in loc['description'] and ls['rideCheckScan'] in loc['description'], 'POST /driver/location text'
hdr = [p for p in loc['parameters'] if p.get('name') == 'Idempotency-Key']
assert len(hdr) == 1 and hdr[0]['in'] == 'header' and hdr[0]['required'] is True and hdr[0]['schema'] == {'type': 'string', 'minLength': 16, 'maxLength': 128}, 'POST /driver/location: own Idempotency-Key header'
assert 'replays' not in hdr[0]['description'] and ik in hdr[0]['description'], 'POST /driver/location: the exception text, not the replay text'
assert not any(p.get('$ref', '').endswith('/IdempotencyKey') for p in loc['parameters']) and loc['x-idempotency'] == 'checked, not stored', 'no shared replay header here'
shared = spec['components']['parameters']['IdempotencyKey']['description']
assert 'the same key replays the committed response' in shared, 'the shared header text is unchanged for every other mutation'
assert sorted(spec['components']['schemas']['DriverLocationAck']['properties'].keys()) == sorted(['accepted', 'serverTime', 'outsideArea', 'areaZones']), 'DriverLocationAck: no field added'

# --- CONTRACT.md
t = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
tc = t + ch  # v0.18.124: the v0.18.117 note moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert '\nv0.18.117 (S7 notes + alert-cap MF3;' in tc and 'follows v0.18.116)' in tc and 'Q126' in tc and 'its own job' in tc, 'CONTRACT.md v0.18.117 note (Q126 left out)'
assert 'v0.18.117 exception, owner W2 Q114: `POST /driver/location` checks the key but never stores it' in t, 'CONTRACT.md §1 Headers exception'
assert 'v0.18.117 (`driverHome.locationSend`, owner W2 Q113): on a trip a GPS batch writes a `location` event only when' in t, 'CONTRACT.md §12 GPS send'
s44 = t[t.index('\n## 44. '):t.index('\n## 46. ')]
assert 'v0.18.117 (`serverDetection.liveList`)' in s44 and 'no limit, never cut' in s44 and ('a "more" marker is not built yet' in s44 or 'Before v0.18.131 no "more" marker was built.' in s44), 'CONTRACT.md §44 alert list'
assert '\nv0.18.116 (BQ-S10' in t + ch, 'the v0.18.116 note kept (moved to CHANGELOG.md in v0.18.123, word for word)'
# the move: the 13 lines of k116 (cc4b769 CONTRACT.md lines 5-17), word for word, now only in CHANGELOG.md
for v in ('v0.18.115 (BQ-V21', 'v0.18.113 (BQ-S13', 'v0.18.112 (BQ-A04', 'v0.18.111 (server BQ-M28', 'v0.18.110 (BQ-V44', 'v0.18.109 (server BQ-FLEETCUR'):
    assert '\n' + v not in t and '\n' + v in ch, v + ' note moved to CHANGELOG.md'
old_ptr = 'Older version notes are in `CHANGELOG.md`: v0.18.108 and before (the v0.18.97–v0.18.108 notes moved in v0.18.110, the v0.18.82–v0.18.96 notes in v0.18.101), except the v0.5.0 and v0.4.1–v0.4.4 notes below.'
assert old_ptr not in t and ('\n' + old_ptr + '\n') in ch, 'old pointer line kept in CHANGELOG.md (Rule 21)'
cl = ch.split('\n')
i = cl.index(next(l for l in cl if l.startswith('v0.18.115 (BQ-V21')))
assert hashlib.sha256('\n'.join(cl[i:i + 13]).encode()).hexdigest() == 'de936be97c49c3534cdfe64043d59add82008e562b8dae6c44e1e7f8d0676c61', 'moved block is word for word (Rule 21)'
assert cl[i - 2].startswith('v0.18.117 (S7 notes + alert-cap MF3; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.116 and before (the v0.18.116 note moved in v0.18.123, the v0.18.109–v0.18.115 notes moved in v0.18.117, the v0.18.97–v0.18.108 notes in v0.18.110' in tc, 'the v0.18.117 pointer line (kept in CHANGELOG.md since v0.18.124)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
for f in sorted(glob.glob('scripts/*')):
    assert open(f, encoding='utf-8').read().count('\n') <= 1500, f + ' over 1,500 lines'
print('v0.18.117 ok')

#!/usr/bin/env python3
"""v0.18.150 (L20 stream backup; owner 2026-11-21 "Switch to old two (Rec.)", Rules plan/NUMBERS.md): after
realtime.oneStreamFallback.failuresInARow failed tries of GET /driver/stream in a row the driver app opens the two old
streams and asks the one stream again after retryOneAfterMinutes (contract.json#driverOneStreamFallback), the defaults,
the kept key, the openapi copy, the CONTRACT.md notes, and the v0.18.144 note moved word for word to CHANGELOG.md
(Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 150), 'version 0.18.150 or later'
fb = c['driverOneStreamFallback']
assert list(fb) == ['note', 'setting', 'server', 'failedTry', 'driver', 'rider', 'admin', 'scenarios'], 'driverOneStreamFallback keys'
assert c['configDefaults']['driverOneStreamFallback'] == {'failuresInARow': 3, 'retryOneAfterMinutes': 10}, 'defaults (owner: 3 / 10)'
assert 'whole number 1-10, default 3' in fb['setting'] and 'whole number 1-60, default 10' in fb['setting'], 'ranges'
assert '400 invalid_request with reason invalid_document' in fb['server'] and 'GET /driver/config always serves realtime.oneStreamFallback' in fb['server'], 'server'
assert 'with at least one line received (a heartbeat comment counts)' in fb['failedTry'] and 'a stream that received no line never counts as connected' in fb['failedTry'], 'silent stream (review 2)'
assert 'a 200 alone is not connected' in fb['failedTry'] and 'resets the count to 0' in fb['failedTry'], 'failed try'
assert 'at once, without waiting for a Retry-After' in fb['driver'] and 'while the two old streams stay open' in fb['driver'] and 'one failed return try is enough' in fb['driver'], 'way back'
assert 'opens the two old streams' in fb['driver'] and 'An app restart forgets the count and the backup' in fb['driver'] and '404 zone_not_found means the two streams once' in fb['driver'] and 'No text on screen' in fb['driver'], 'driver'
assert fb['rider'].startswith('Not affected'), 'rider'
assert "'Backup after failed tries' (1-10, default 3)" in fb['admin'] and "'Try the one connection again after (minutes)' (1-60, default 10)" in fb['admin'] and 'en / sv / fr' in fb['admin'], 'admin'
ids = [s['id'] for s in fb['scenarios']]
assert {'return_try_fails', 'backup_ignores_retry_after'} <= set(ids), 'way-back scenarios'
assert len(ids) == len(set(ids)) >= 7, 'scenarios'
kk = c['configDocs']['keptKeys']
assert kk['driver_app_config'] == ['realtime.oneStream', 'realtime.oneStreamFallback'], 'kept keys'
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']
f = S['DriverAppConfig']['properties']['realtime']['properties']['oneStreamFallback']
assert f['type'] == 'object' and f['additionalProperties'] is False and 'required' not in f, 'openapi object'
assert (f['properties']['failuresInARow']['minimum'], f['properties']['failuresInARow']['maximum'], f['properties']['failuresInARow']['default']) == (1, 10, 3), 'openapi failuresInARow'
assert (f['properties']['retryOneAfterMinutes']['minimum'], f['properties']['retryOneAfterMinutes']['maximum'], f['properties']['retryOneAfterMinutes']['default']) == (1, 60, 10), 'openapi retryOneAfterMinutes'
assert all(f['properties'][k]['type'] == 'integer' for k in ('failuresInARow', 'retryOneAfterMinutes')), 'integers'
assert 'realtime.oneStreamFallback' in S['ConfigDraftUpdate']['properties']['removeKeys']['items']['enum'], 'removeKeys'
assert 'v0.18.150 (driverOneStreamFallback)' in P['/driver/stream']['get']['description'], 'openapi /driver/stream'
assert 'v0.18.150 (driverOneStreamFallback.server)' in P['/admin/config/{doc}']['put']['description'], 'openapi PUT'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.150 (L20 stream backup;' in t, 'CONTRACT.md note'
n150 = next(l for l in t.split('\n') if l.startswith('v0.18.150 (L20 stream backup;'))
assert 'follows v0.18.149)' in n150 and '`contract.json#driverOneStreamFallback`' in n150 and 'Rider: not affected' in n150, 'CONTRACT.md note text'
assert 'v0.18.150: also `realtime.oneStreamFallback`' in t, 'CONTRACT.md kept keys line'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
# launch restack (plan K): this version moves the v0.18.144 note (the draft moved v0.18.127)
n144 = next(l for l in cl if l.startswith('v0.18.144 (owner 2026-11-20 "Also add ba'))
assert '\n' + n144 not in t and cl.count(n144) == 1, 'v0.18.144 note moved once'
assert hashlib.sha256(n144.encode()).hexdigest() == '0ffd4d64525e9ae90ed235b355f77960f5cb5cb82b0fadefbcc1017a61106562', 'v0.18.144 note moved word for word'
j = cl.index(n144)
assert cl[j - 2].startswith('v0.18.150 (L20 stream backup; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '550c435264278bc870232b929fcf0d818d42228274494850342cc158cc76e531', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.144 and before (the v0.18.144 note moved in v0.18.150, the v0.18.143 note in v0.18.149, the v0.18.141' in t + ch, 'new pointer line (in CHANGELOG.md once a later version moves it)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
# Review fix: no line of CONTRACT.md / CHANGELOG.md is its own text twice (a doubled line once slipped in).
for name, text in (('CONTRACT.md', t), ('CHANGELOG.md', ch)):
    for k, line in enumerate(text.split('\n')):
        h = len(line) // 2
        assert not (line and len(line) % 2 == 0 and line[:h] == line[h:]), f'{name}:{k + 1} doubled'
assert t.split('\n')[0] == '# Movera shared contract v' + c['version'], 'CONTRACT.md heading'
# Review fix: against the v0.18.132 file (tag or origin/main, when git has it) only a few lines changed.
import difflib, subprocess
base = None
for ref in ('v0.18.132', 'origin/main'):
    try:
        base = subprocess.run(['git', 'show', ref + ':CONTRACT.md'], capture_output=True, text=True, check=True).stdout
        if base.startswith('# Movera shared contract v0.18.132'):
            break
        base = None
    except Exception:
        base = None
# Launch restack (plan K slot 13): 0.18.150 no longer sits directly on v0.18.132 (0.18.133-0.18.149 are between), so the
# count against the v0.18.132 file only holds for the standalone draft; it is skipped once those versions are in the tree.
if base is not None and '\nv0.18.133 (real SMS sign-in codes;' not in t + ch:
    changed = [d for d in difflib.unified_diff(base.split('\n'), t.split('\n'), lineterm='', n=0) if d[:1] in '+-' and d[:3] not in ('+++', '---')]
    assert len(changed) <= 12, f'CONTRACT.md: {len(changed)} lines changed against v0.18.132 (expected the heading, the note, the kept-keys line and the move)'
print('v0.18.150 offer stream backup ok')

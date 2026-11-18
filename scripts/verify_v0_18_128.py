#!/usr/bin/env python3
"""v0.18.128 (S7 W2 Q125, plan B3.11; owner 2026-11-15 Sitting W2 Q125 (Q-B3) "A) count and log above N = 3, refuse
later"; Rules decisions/session-2026-11-06.md:1388): wording only. Checks realtime.appStreamsPerSession (limit 3, log only,
no refusal yet, fixed in the server, admin caps kept), that no other realtime key was added, the openapi copies on the
three app stream calls and CONTRACT.md. Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 128), 'version 0.18.128 or later'
spec = yaml.safe_load(open('openapi.yaml'))

rt = c['realtime']
a = rt['appStreamsPerSession']
assert a['limit'] == 3 and a['action'] == 'log', 'appStreamsPerSession: 3, log only'
n = a['note']
assert n.startswith('v0.18.128 (S7 W2 Q125') and '"A) count and log above N = 3, refuse later"' in n, 'appStreamsPerSession: source'
assert 'still answered 200 (nothing is refused in this step)' in n and 'fixed in the server (no admin setting)' in n, 'appStreamsPerSession: log only, fixed'
assert 'Admin streams keep their own caps' in n and 'B3.11b' in n, 'appStreamsPerSession: admin caps kept, later step named'
assert list(rt) == ['envelope', 'optional', 'kinds', 'afterTerminal', 'rules', 'streamClose', 'reconnectClose', 'connectedRule', 'sessionEnd', 'appStreamsPerSession'], 'realtime: only appStreamsPerSession added'

for p in ['/rider/config/stream', '/driver/config/stream', '/driver/offers/stream']:
    d = spec['paths'][p]['get']['description'].replace('\n', ' ')
    assert 'v0.18.128 (contract.json#realtime.appStreamsPerSession): more than 3 open app streams of one session' in d, 'openapi ' + p

t = open('CONTRACT.md', encoding='utf-8').read()
assert '\nv0.18.128 (S7 W2 Q125' in t and '- **Streams per session** (v0.18.128, S7 W2 Q125)' in t, 'CONTRACT.md v0.18.128 note and line'
# the move (Rule 25 size, Rule 21 word for word): the v0.18.122 and v0.18.121 notes and the old pointer line now only in CHANGELOG.md
import hashlib
assert 'follows v0.18.127)' in next(l for l in t.split('\n') if l.startswith('v0.18.128 (')), 'CONTRACT.md v0.18.128 note follows v0.18.127'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n122 = next(l for l in cl if l.startswith('v0.18.122 (L20 stream;'))
n121 = next(l for l in cl if l.startswith('v0.18.121 (S4 B1.1 SF-1 + SF-2;'))
assert '\n' + n122 not in t and hashlib.sha256(n122.encode()).hexdigest() == '63792cc44377e8e61378cb315a92b439d79f294b42fe8629e6963b88a9f28c06', 'v0.18.122 note moved word for word'
assert '\n' + n121 not in t and hashlib.sha256(n121.encode()).hexdigest() == '0a67a1876c65d982eba976c70d33eac6f1b92b93daae40f4e2b75bf93d5c77e7', 'v0.18.121 note moved word for word'
j = cl.index(n122)
assert cl[j - 2].startswith('v0.18.128 (S7 W2 Q125; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2] == n121, 'CHANGELOG.md keeps the CONTRACT.md order'
assert cl[j + 4].startswith('Older version notes are in `CHANGELOG.md`: v0.18.120 and before (the v0.18.120 note moved in v0.18.127,'), 'old pointer line kept in CHANGELOG.md'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.122 and before (the v0.18.122 and v0.18.121 notes moved in v0.18.128, the v0.18.120 note in v0.18.127, the v0.18.119 note in v0.18.126,' in t + ch, 'the v0.18.128 pointer line (kept in CHANGELOG.md since v0.18.129)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.128 app streams per session ok')

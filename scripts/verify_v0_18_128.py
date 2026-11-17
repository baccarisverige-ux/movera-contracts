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
assert list(rt) == ['envelope', 'optional', 'kinds', 'afterTerminal', 'rules', 'streamClose', 'connectedRule', 'sessionEnd', 'appStreamsPerSession'], 'realtime: only appStreamsPerSession added'

for p in ['/rider/config/stream', '/driver/config/stream', '/driver/offers/stream']:
    d = spec['paths'][p]['get']['description'].replace('\n', ' ')
    assert 'v0.18.128 (contract.json#realtime.appStreamsPerSession): more than 3 open app streams of one session' in d, 'openapi ' + p

t = open('CONTRACT.md', encoding='utf-8').read()
assert '\nv0.18.128 (S7 W2 Q125' in t and '- **Streams per session** (v0.18.128, S7 W2 Q125)' in t, 'CONTRACT.md v0.18.128 note and line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.128 app streams per session ok')

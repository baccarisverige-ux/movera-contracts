#!/usr/bin/env python3
"""v0.18.156 (iOS push; owner 2026-11-24 "Notifications doesn't work on iPhones?"): checks contract.json#auth.devices.config.ios
(bundle ids, note, app start), auth.devices.sending.apns, the openapi copy (PushIosConfig, PushConfig.iosConfig, the platform
parameter), the CONTRACT.md note and the v0.18.151 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25).
Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 156), 'version 0.18.160 or later'
cfg = c['auth']['devices']['config']
io = cfg['ios']
assert io['iosBundleIds'] == {'driver': 'se.movera.driver', 'rider': 'com.movera.rider'}, 'bundle ids'
assert io['note'].startswith('v0.18.156 (owner 2026-11-24') and 'follows v0.18.155)' in io['note'], 'note'
assert 'iosConfig? { apiKey, appId, messagingSenderId, projectId, iosBundleId }' in io['note'], 'iosConfig shape'
assert 'never a secret' in io['note'] and 'no GoogleService-Info.plist' in io['note'], 'no file in repos'
assert 'usernotifications.time-sensitive' in io['apps'], 'driver time-sensitive'
assert 'platform: ios' in io['appStart'] and 'remote-notification' in io['apps'] and 'aps-environment' in io['apps'], 'app start / apps'
assert cfg['android']['ios'].startswith('v0.18.105: platform=ios answers enabled false'), 'v0.18.105 text kept (history)'
ap = c['auth']['devices']['sending']['apns']
for w in ('apns-push-type alert', 'apns-priority 10', 'aps.alert', 'aps.thread-id = data.kind', 'never sets aps.badge', 'content-available'):
    assert w in ap, w
spec = yaml.safe_load(open('openapi.yaml'))
assert spec['info']['version'] == c['version'], 'openapi version'
S, P = spec['components']['schemas'], spec['paths']
pi = S['PushIosConfig']
assert set(pi['required']) == {'apiKey', 'appId', 'messagingSenderId', 'projectId', 'iosBundleId'}, 'PushIosConfig required'
assert pi['properties']['iosBundleId']['enum'] == ['com.movera.rider', 'se.movera.driver'], 'bundle enum'
assert S['PushConfig']['properties']['iosConfig']['allOf'] == [{'$ref': '#/components/schemas/PushIosConfig'}], 'PushConfig.iosConfig'
assert 'androidConfig' in S['PushConfig']['properties'] and 'webConfig' in S['PushConfig']['properties'], 'older fields kept'
g = P['/push/config']['get']
assert 'v0.18.156' in g['description'] and any(p.get('name') == 'platform' and 'ios gives iosConfig' in p['description'] for p in g['parameters']), 'openapi /push/config'
assert 'v0.18.156: every FCM message' in P['/push/devices']['post']['description'], 'openapi /push/devices'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.161: the v0.18.156 note moved to CHANGELOG.md word for word
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.156 (iOS push;' in tc, 'CONTRACT.md note'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n151 = next(l for l in cl if l.startswith('v0.18.151 (SOS contacts SMS sent;') and 'moved from CONTRACT.md' not in l)
assert '\n' + n151 not in t and cl.count(n151) == 1, 'v0.18.151 note moved once'
j = cl.index(n151)
assert cl[j - 2].startswith('v0.18.156 (iOS push; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.150 and before'), 'old pointer line moved'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.151 and before (the v0.18.151 note moved in v0.18.156, the v0.18.150 note in v0.18.155' in t + ch, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.156 iOS push ok')

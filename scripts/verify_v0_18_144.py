#!/usr/bin/env python3
"""v0.18.144 (owner 2026-11-20; contract.json#liveLocation): the adjust-pickup banner and two-way live location. Checks the
section, defaults, texts in sv/en/fr/ar, the openapi route / frame / setting, the CONTRACT.md note and the v0.18.127 note
moved word for word to CHANGELOG.md (Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 144), 'version 0.18.144 or later'
d = c['configDefaults']
assert d['liveLocationShare'] is False and d['adjustPickupMeters'] == 30 and d['liveLocationSendEverySeconds'] == 8, 'defaults'
ll = c['liveLocation']
for k in ('note', 'owner', 'setting', 'adjustPickup', 'route', 'window', 'relay', 'privacy', 'send', 'driverSide', 'texts', 'load'):
    assert k in ll, 'liveLocation.' + k
assert ll['owner'].startswith('Also add bande on searching screen'), 'owner words verbatim'
assert 'never stored' in ll['privacy'] or 'never stored' in ll['note'], 'privacy'
for name, t in ll['texts'].items():
    assert set(t) == {'en', 'sv', 'fr', 'ar'}, name + ': four languages'
    for lang, v in t.items():
        for ph in ('{meters}', '{driver}', '{rider}'):
            assert (ph in v) == (ph in t['en']), f'{name}.{lang}: placeholder {ph}'
o = yaml.safe_load(open('openapi.yaml'))
p = o['paths']['/trips/{tripId}/live-location']['put']
assert p['operationId'] == 'shareLiveLocation' and set(p['x-actor']) == {'rider', 'driver'}, 'route'
assert any(q.get('name') == 'live' for q in o['paths']['/trips/{tripId}/events']['get']['parameters']), '?live=true'
sc = o['components']['schemas']
assert sc['LiveLocationEvent']['required'] == ['tripId', 'side', 'sharing', 'at'], 'frame'
assert set(sc['RiderAppConfig']['properties']['liveLocation']['properties']) == {'share', 'adjustPickupMeters', 'sendEverySeconds'}, 'setting'
assert 'privacyNote' in ll['texts'] and 'driverPrivacyNote' in ll['texts'], 'consent texts'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.144 (owner 2026-11-20' in t, 'CONTRACT.md note'
assert '\nv0.18.127 (' not in t, 'v0.18.127 note moved'
ch = open('CHANGELOG.md', encoding='utf-8').read().split('\n')
n127 = next(l for l in ch if l.startswith('v0.18.127 (S7 W2 Q119, plan 0.21;'))
assert ch.count(n127) == 1 and ch[ch.index(n127) - 2].startswith('v0.18.144 (live location; Rule 21 / Rule 25'), 'CHANGELOG move'
ap = ll['adjustPickup']['when']
assert 'NOT arrived' in ap and 'adjustPickupMeters 0 = the banner is off' in ap, 'no banner at arrived; 0 = off'
assert 'minus riderOnboard and terminal' in ll['window'] and 'relays nothing after pickup' in ll['window'], 'window ends at pickup'
assert 'OPT-IN' in ll['driverSide'], 'driver opts in'
for k in ('riderShareBody', 'privacyNote', 'driverPrivacyNote'):
    assert 'pickup' in ll['texts'][k]['en'] and 'ride ends' not in ll['texts'][k]['en'], k + ': says it stops at pickup'
assert sc['RiderAppConfig']['properties']['liveLocation']['properties']['adjustPickupMeters']['minimum'] == 0, '0 = off'
assert '409' in p['responses'], '409 documented'
assert "(accepted / driver_to_pickup, not arrived)" in t, 'CONTRACT.md: not at arrived'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.144 live location ok')

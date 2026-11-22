#!/usr/bin/env python3
"""v0.18.154 (P16c minimum app version; owner 2026-11-21 20:30 "Yes, build it now (Recommended)"): checks
contract.json#appUpdate (fields, server rule, never-refused list, texts in en / sv / fr), the default off, the kept keys of
both app documents, the new error code and headers, the openapi copy (AppUpdate.minVersion / storeUrls, the two headers
and 426 on the three calls), the CONTRACT.md note and the v0.18.149 note moved word for word to CHANGELOG.md (Rule 21 /
Rule 25). Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import hashlib, json, re, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 154), 'version 0.18.154 or later'
au = c['appUpdate']
assert au['note'].startswith('v0.18.154 (P16c minimum app version;') and 'follows v0.18.153)' in au['note'], 'note'
for k in ('fields', 'scope', 'validation', 'keptKeys', 'headers', 'compare', 'server', 'neverRefused', 'missingHeader', 'apps', 'admin'):
    assert isinstance(au[k], str) and au[k], k
assert 'minVersion { android: "x.y.z" | null, ios: "x.y.z" | null }' in au['fields'] and 'storeUrls' in au['fields'], 'fields'
assert '426 code upgrade_required, reason app_update_required' in au['server'], 'server 426'
for call in ('POST /trips', 'POST /driver/availability with onlineStatus online while the driver is not on a trip', 'POST /offers/{offerId}/accept while the driver has no current trip'):
    assert call in au['server'], call
for word in ('SOS', 'sign-out', 'account deletion', 'go offline', 'already running'):
    assert word in au['neverRefused'], word
assert 'go-online while the driver holds a booked ride' in au['neverRefused'] and 'holds no booked ride' in au['server'], 'held booked ride never refused'
assert 'holds a booked ride not started yet' in au['apps'], 'driver app: held booked ride only the small line'
assert 'no check' in au['missingHeader'] and 'Known limit' in au['missingHeader'], 'missing header limit'
assert 'never while a trip is active (accepted, to pickup, arrived, on trip)' in au['apps'], 'driver trip exemption'
for part in ('title', 'body', 'button'):
    assert set(au['texts'][part]) == {'en', 'sv', 'fr'} and all(au['texts'][part].values()), 'texts.' + part
assert au['texts']['title']['en'] == 'Update Movera to continue' and au['texts']['button']['en'] == 'Update', 'texts en'
assert au['adminTexts']['warning']['en'] == 'Phones below this version must update before they can book or go online.', 'admin warning'
assert set(au['adminTexts']['title']) == {'en', 'sv', 'fr'}, 'admin title'
d = c['configDefaults']['appUpdate']
assert d['minVersion'] == {'android': None, 'ios': None} and d['storeUrls'] == {'android': None, 'ios': None}, 'default off'
kk = c['configDocs']['keptKeys']
assert kk['rider_app_config'] == ['appUpdate.minVersion', 'appUpdate.storeUrls'], 'rider kept keys'
assert kk['driver_app_config'] == ['realtime.oneStream', 'realtime.oneStreamFallback', 'appUpdate.minVersion', 'appUpdate.storeUrls'], 'driver kept keys (realtime.oneStreamFallback: v0.18.150, launch restack)'
assert kk['appUpdateNote'].startswith('v0.18.154 ('), 'kept keys note'
assert c['errors']['codes'][-1] == 'upgrade_required' and c['errors']['codes'].count('upgrade_required') == 1, 'error code'
assert 'HTTP 426' in c['errors']['upgradeRequired'], 'error code status'
assert c['headers']['X-App-Version'].startswith('v0.18.154') and c['headers']['X-App-Platform'].startswith('v0.18.154'), 'headers'
spec = yaml.safe_load(open('openapi.yaml'))
S, P, PR = spec['components']['schemas'], spec['paths'], spec['components']['parameters']
A = S['AppUpdate']['properties']
semver = A['minVersion']['properties']['android']['oneOf'][0]['pattern']
for good in ('0.0.0', '1.4.0', '10.20.30', '99999.0.1'):
    assert re.match(semver, good), good
for bad in ('1.4', '1.04.0', 'v1.4.0', '1.4.0+5', '1.4.0-beta', '100000.0.0', ''):
    assert not re.match(semver, bad), bad
assert A['storeUrls']['properties']['ios']['oneOf'][1] == {'type': 'null'} and A['storeUrl']['type'] == 'string', 'storeUrls; storeUrl kept a string'
assert PR['AppVersionHeader']['name'] == 'X-App-Version' and PR['AppPlatformHeader']['schema']['enum'] == ['android', 'ios'], 'header params'
for p in ('/trips', '/driver/availability', '/offers/{offerId}/accept'):
    o = P[p]['post']
    assert o['responses']['426'] == {'$ref': '#/components/responses/UpgradeRequired'}, p + ' 426'
    assert {'$ref': '#/components/parameters/AppVersionHeader'} in o['parameters'], p + ' header'
assert 'upgrade_required' in S['ErrorCode']['enum'], 'ErrorCode enum'
rk = S['ConfigDraftUpdate']['properties']['removeKeys']['items']['enum']
assert 'appUpdate.minVersion' in rk and 'appUpdate.storeUrls' in rk, 'removeKeys'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.154 (P16c minimum app version;' in t, 'CONTRACT.md note'
assert 'follows v0.18.153)' in t, 'CONTRACT.md follows'
assert 'v0.18.154: 426 `upgrade_required` on book, go-online, offer accept' in t, 'CONTRACT.md §18 row'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
# launch restack (plan K): this version moves the v0.18.149 note (the draft moved v0.18.127)
n149 = next(l for l in cl if l.startswith('v0.18.149 (admin sessions, owner Rules d'))
assert '\n' + n149 not in t and cl.count(n149) == 1, 'v0.18.149 note moved once'
assert hashlib.sha256(n149.encode()).hexdigest() == '23e56ab83cb34cd81735666c2291bb669bec54ce685b93066f48cc9f0f2481f2', 'v0.18.149 note moved word for word'
j = cl.index(n149)
assert cl[j - 2].startswith('v0.18.154 (P16c minimum app version; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == 'afd1aec63d64c9c79a5f218d6aef98a4db13526db4e66cf2dac253634c8e18d8', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.149 and before (the v0.18.149 note moved in v0.18.154, the v0.18.148 note in v0.18.153, the v0.18.146' in t + ch, 'new pointer line (in CHANGELOG.md once a later version moves it)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.154 minimum app version ok')

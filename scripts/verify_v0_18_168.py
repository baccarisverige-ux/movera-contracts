#!/usr/bin/env python3
"""v0.18.168 (SMS company Infobip, 46elks as backup; owner 2026-11-26 "Infobip + 46elks en secours (Recommande)"):
contract.json#smsProviders, openapi CountryRules.smsSignIn.providerOrder and smsSignInOtherCountries.providerOrder
(optional), the CONTRACT.md note and the v0.18.163 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25).
Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 168), 'version 0.18.168 or later'
p = c['smsProviders']
assert p['since'] == '0.18.168', 'since'
for k in ('note', 'serverKeysNote', 'infobip', 'setting', 'fallback', 'logs', 'driver', 'rider', 'admin'):
    assert isinstance(p[k], str) and p[k], k
assert p['providers'] == ['infobip', '46elks'] and p['defaultOrder'] == ['infobip', '46elks'], 'providers + default order'
assert p['serverKeys'] == {'infobip': ['INFOBIP_BASE_URL', 'INFOBIP_API_KEY'], '46elks': c['smsSignIn']['serverKeys']}, 'server key names'
assert 'never two SMS for one code' in p['fallback'], 'no double send'
assert 'never the number, the text or the code' in p['logs'], 'privacy'
spec = yaml.safe_load(open('openapi.yaml'))
cr = spec['components']['schemas']['CountryRules']['properties']
for n in ('smsSignIn', 'smsSignInOtherCountries'):
    o = cr[n]['properties']['providerOrder']
    assert o['type'] == 'array' and o['items']['enum'] == p['providers'] and o['minItems'] == 1 and o['maxItems'] == 2 and o['uniqueItems'] is True, n
    assert o['default'] == p['defaultOrder'] and o['description'].startswith('v0.18.168 (contract.json#smsProviders): '), n + ' description'
    assert 'providerOrder' not in cr[n].get('required', []), n + ' optional'
assert 'v0.18.168' in spec['paths']['/auth/otp/request']['post']['description'], 'otp request'
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
assert '\nv0.18.168 (SMS company Infobip, 46elks as backup;' in md + ch, 'note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert 'v0.18.168 (SMS companies; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch, 'CHANGELOG move line'
assert '\nv0.18.163 (live traffic for trip times;' in ch, 'v0.18.163 note in CHANGELOG.md'
print('v0.18.168 ok')

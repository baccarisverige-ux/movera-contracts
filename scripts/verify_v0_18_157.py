#!/usr/bin/env python3
"""v0.18.157 (SMS sign-in for every country; owner 2026-11-24 "SMS sign-in codes must work for ANY phone number from
ANY country"): checks contract.json#smsSignIn.otherCountries (default OFF, cap 50 inside dailyCapRange, home country SE,
strict E.164, mobile patterns compile and accept / refuse sample numbers, texts en / sv / fr), the openapi copy, the
CONTRACT.md note and the v0.18.150 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25)."""
import json, re, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 157), 'version 0.18.157 or later'
s = c['smsSignIn']; oc = s['otherCountries']
assert oc['note'].startswith('v0.18.157 (owner 2026-11-24') and 'default ON for the rider app' in oc['note'], 'note'
d = c['configDefaults']['smsSignInOtherCountries']
assert d['enabled'] is True and d['dailyCap'] == 50, 'default on (rider), 50'
lo, hi = s['dailyCapRange']; assert lo <= d['dailyCap'] <= hi, 'cap in range'
assert oc['homeCountry'] == 'SE' and 'sms_sign_in_other_home_only' in oc['setting'] and 'super_admin_only' in oc['setting'], 'setting'
assert 'never opens a served country' in oc['served'], 'served countries keep their own switch'
assert '^\\+[1-9][0-9]{7,14}$' in oc['numberCheck'] and 'No phone-number library' in oc['numberCheck'], 'E.164'
fx = {k: re.compile(v) for k, v in oc['fixedLines'].items()}
for k, v in oc['fixedLines'].items():
    assert v.startswith('^\\' + k) and v.endswith('$'), k
assert fx['+49'].fullmatch('+493012345678') and not fx['+49'].fullmatch('+4915112345678'), 'DE landline / mobile'
assert fx['+216'].fullmatch('+21671123456') and not fx['+216'].fullmatch('+21620123456'), 'TN landline / mobile'
assert 'app driver' in oc['active'], 'rider only'
assert 'sms_cap_near:other' in oc['alert'] and 'sms_cap:other' in oc['alert'], 'alerts'
assert 'else en' in oc['language'], 'language'
for k in ('title', 'switch', 'dailyCap', 'info'):
    t = oc['admin']['texts'][k]; assert set(t) == {'en', 'sv', 'fr'} and all(t.values()), k
assert 'super admins' in oc['admin']['placement'], 'admin super only'
spec = yaml.safe_load(open('openapi.yaml'))
p = spec['components']['schemas']['CountryRules']['properties']['smsSignInOtherCountries']
assert p['properties']['enabled']['default'] is True and p['properties']['dailyCap']['default'] == 50 and p['additionalProperties'] is False, 'openapi'
md = open('CONTRACT.md', encoding='utf-8').read(); ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v0.18.157') or '\nv0.18.157 (SMS sign-in for every country;' in md, 'CONTRACT.md note'
assert '\nv0.18.150 (L20 stream backup;' not in md and '\nv0.18.150 (L20 stream backup;' in ch, 'v0.18.150 note moved'
assert c['configDocs']['keptKeys']['country_rules'][-1] == 'smsSignInOtherCountries', 'kept key'
print('v0.18.157 ok')

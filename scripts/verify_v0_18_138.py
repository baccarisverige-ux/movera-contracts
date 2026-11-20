#!/usr/bin/env python3
"""v0.18.138 (SMS abuse guards; owner 2026-11-20 "Ok" to Rules audits/impact/sms-abuse-open-launch-2026-11-20.md, Rules
decisions/session-2026-11-06.md, plan/NUMBERS.md): checks contract.json#deviceCheck (per-install code limit with a safe
default, the real-phone check OFF by default, key NAMES only, iPhone App Attest marked inactive, the binding, the error
text sv / fr / en), the openapi fields, the CONTRACT.md note and section 8 line, and the v0.18.128 note moved word for
word to CHANGELOG.md (Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, re, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 138), 'version 0.18.138 or later'
dc = c['deviceCheck']
cl = c['countryLimits']
assert cl['defaults']['codesPerDevicePerHour'] == 5 and cl['ranges']['codesPerDevicePerHour'] == [1, 100], 'per-install limit: default 5, range 1-100'
assert list(cl['fields']) == list(cl['defaults']) == list(cl['ranges']), 'countryLimits: fields, defaults and ranges list the same keys'
assert c['configDefaults']['smsSignIn']['requireDeviceCheck'] is False, 'the real-phone check is OFF by default'
assert c['configDefaults']['smsSignIn']['enabled'] is False and c['configDefaults']['smsSignIn']['dailyCap'] == 200, 'v0.18.133 defaults unchanged'
assert dc['serverKeys'] == {'android': ['PLAY_INTEGRITY_SERVICE_ACCOUNT', 'PLAY_INTEGRITY_PACKAGES'], 'ios': ['APPLE_APP_ATTEST_APP_IDS', 'APPLE_APP_ATTEST_ROOT_CA']}, 'server key names (names only)'
assert dc['ios']['active'] is False and 'INACTIVE' in dc['ios']['note'] and 'do NOT switch requireDeviceCheck on' in dc['ios']['note'], 'iPhone App Attest marked inactive'
assert 'fail closed' in dc['check'] and 'used once' in dc['check'] and 'fail closed' in dc['serverKeysNote'], 'fail closed, one use'
assert '"movera-sms-code|" + app + "|" + phone + "|" + installId' in dc['binding'], 'binding text'
assert 'PLAY_RECOGNIZED' in dc['check'] and 'MEETS_DEVICE_INTEGRITY' in dc['check'] and 'Apple App Attestation root' in dc['check'], 'verdicts'
assert dc['maxAgeSeconds'] == 600 and dc['timeoutSeconds'] == 5, 'token age and time-out'
assert list(dc['errors']) == ['device_check_failed'] and dc['errors']['device_check_failed'].startswith('403 forbidden'), 'reason'
assert 'no SMS' in dc['setting'] and 'nothing counted on dailyCap' in dc['setting'] and 'web sign-in' in dc['setting'], 'setting'
assert 'never hold the token' in dc['logs'], 'logs'
assert set(c['smsSignIn']['errors']) == {'sign_in_restricted', 'sms_daily_limit', 'sms_not_sent'}, 'smsSignIn.errors kept as released'
for lang in ('sv', 'fr', 'en'):
    t = dc['texts']['deviceCheckFailed'][lang]
    assert t.strip() and 'http' not in t, 'deviceCheckFailed ' + lang
for k in ('installId', 'deviceLimit', 'setting', 'binding', 'check', 'order', 'apps'):
    assert len(dc[k]) > 40, k
spec = yaml.safe_load(open('openapi.yaml'))
sch = spec['components']['schemas']
o = sch['OtpRequest']
assert sch['AccountPhoneChange']['properties']['installId'] == o['properties']['installId'] and 'phoneChange' in dc, 'phone change takes the same fields'
assert 'canonical bytes' in dc['check'] and 'circuit breaker' in dc['order'], 'review fixes'
assert o['required'] == ['phone', 'app'], 'OtpRequest required fields as released'
assert o['properties']['installId']['pattern'] == '^[A-Za-z0-9_-]{16,64}$', 'installId shape'
assert o['properties']['deviceCheck']['allOf'] == [{'$ref': '#/components/schemas/DeviceCheck'}], 'deviceCheck'
d = sch['DeviceCheck']
assert d['required'] == ['platform', 'token'] and d['properties']['platform']['enum'] == ['android', 'ios'] and d['additionalProperties'] is False, 'DeviceCheck'
p = sch['CountryRules']['properties']['smsSignIn']['properties']['requireDeviceCheck']
assert p['default'] is False and p['type'] == 'boolean', 'CountryRules.smsSignIn.requireDeviceCheck'
assert sch['CountryLimits']['properties']['codesPerDevicePerHour']['default'] == 5, 'CountryLimits.codesPerDevicePerHour'
assert 'v0.18.138 (contract.json#deviceCheck)' in spec['paths']['/auth/otp/request']['post']['description'], 'openapi otp request wording'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.138 (SMS abuse guards at the open launch;' in t and '**iPhone App Attest is INACTIVE**' in t, 'CONTRACT.md note'
assert 'v0.18.138 (`contract.json#deviceCheck`): the request may carry `installId`' in t, 'CONTRACT.md section 8 line'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl2 = ch.split('\n')
n128 = next(l for l in cl2 if l.startswith('v0.18.128 (S7 W2 Q125, plan B3.11;'))
assert '\n' + n128 not in t and cl2.count(n128) == 1, 'v0.18.128 note moved once'
assert hashlib.sha256(n128.encode()).hexdigest() == '055f16ae7e3902a95d2effe1a1d5ea91fb1409c4bb7272d14163a5d0521f4d9f', 'v0.18.128 note moved word for word'
j = cl2.index(n128)
assert cl2[j - 2].startswith('v0.18.138 (SMS abuse guards; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl2[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.127 and before (the v0.18.127 note moved in v0.18.133,'), 'old pointer line kept'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.128 and before (the v0.18.128 note moved in v0.18.138, the v0.18.127 note in v0.18.133,' in t, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.138 SMS abuse guards ok')

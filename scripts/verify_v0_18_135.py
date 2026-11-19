#!/usr/bin/env python3
"""v0.18.135 (real SMS sign-in codes; owner 2026-11-19 "Yes, build it now (Rec.)", Rules decisions/session-2026-11-06.md,
audits/impact/sms-sign-in.md): checks contract.json#smsSignIn (default OFF, daily cap, key NAMES only, texts sv / fr / en
without a link, one GSM-7 SMS part), CountryRules.smsSignIn in openapi.yaml, auth.signInErrors left as released, the
CONTRACT.md note and section 8 line, and the v0.18.127 note moved word for word to CHANGELOG.md (Rule 25). Run by
scripts/verify.sh (own file, Rule 25)."""
import json, re, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 135), 'version 0.18.135 or later'
s = c['smsSignIn']
d = c['configDefaults']['smsSignIn']
assert d['enabled'] is False, 'default OFF (nothing changes until the admin switch is on)'
lo, hi = s['dailyCapRange']
assert (lo, hi) == (10, 100000) and lo <= d['dailyCap'] <= hi and d['dailyCap'] == 200, 'daily cap default inside its range'
assert s['serverKeys'] == ['ELKS_API_USERNAME', 'ELKS_API_PASSWORD'], 'server key names (names only, never values)'
assert s['countries'] == {'+46': 'SE', '+33': 'FR', '+216': 'TN'}, 'calling codes of the served countries'
assert re.fullmatch(r'[A-Za-z][A-Za-z0-9]{2,10}', s['sender']), 'sender name 46elks accepts (3-11 letters and digits)'
assert set(s['errors']) == {'sign_in_restricted', 'sms_daily_limit', 'sms_not_sent'}, 'reasons'
assert s['errors']['sms_daily_limit'].startswith('503 unavailable') and s['errors']['sms_not_sent'].startswith('503 unavailable'), 'both retryable 503'
assert 'fail closed' in s['dailyCap'] and 'exactly as before' in s['active'] and 'never gets an SMS' in s['active'], 'fail closed / unchanged until active'
# GSM 03.38 basic set (one SMS part = 160 of these)
GSM7 = set("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
for lang in ('sv', 'fr', 'en'):
    text = s['texts']['sms'][lang]
    assert text.count('{code}') == 1 and text.startswith('Movera'), lang + ': app name and the code once'
    assert 'http' not in text.lower() and 'www' not in text.lower() and '/' not in text, lang + ': no link'
    filled = text.replace('{code}', '0' * c['auth']['otp']['codeLength'])
    assert len(filled) <= 160 and set(filled) <= GSM7, lang + ': one GSM-7 SMS part'
    for k in ('smsNotSent', 'smsDailyLimit'):
        assert s['texts'][k][lang].strip(), k + ' ' + lang
a = s['alert']
assert a['nearPercent'] == 80 and '{0}' in a['titles']['near'] and '{1}' in a['titles']['reached'] and 'system_health' in a['rule'], 'alert'
assert 'never hold the code' in s['logs'], 'logs'
assert list(c['auth']['signInErrors']) == ['note', 'invalid_otp_code', 'invalid_otp_session', 'otp_expired', 'otp_too_many_attempts', 'otp_resend_too_soon', 'otp_too_many', 'sign_in_restricted', 'otp_locked_today', 'account_suspended'], 'auth.signInErrors kept as released (Rule 21)'
assert c['auth']['otp']['codeLength'] == 4, 'owner 2026-11-02 "Keep 4 digits"'
spec = yaml.safe_load(open('openapi.yaml'))
p = spec['components']['schemas']['CountryRules']['properties']['smsSignIn']
assert p['properties']['enabled']['default'] is False and p['properties']['dailyCap']['minimum'] == lo and p['properties']['dailyCap']['maximum'] == hi and p['properties']['dailyCap']['default'] == 200, 'openapi CountryRules.smsSignIn'
assert p.get('additionalProperties') is False and 'required' not in p, 'both parts optional, no other key'
assert 'v0.18.135 (contract.json#smsSignIn)' in spec['paths']['/auth/otp/request']['post']['description'], 'openapi otp request wording'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.135 (real SMS sign-in codes;' in t, 'CONTRACT.md note'
assert 'v0.18.135 (`contract.json#smsSignIn`): **real SMS codes.**' in t, 'CONTRACT.md section 8 line'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n127 = next(l for l in cl if l.startswith('v0.18.127 (S7 W2 Q119, plan 0.21;'))
assert '\n' + n127 not in t and cl.count(n127) == 1, 'v0.18.127 note moved once'
j = cl.index(n127)
assert cl[j - 2].startswith('v0.18.135 (real SMS sign-in codes; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.126 and before (the v0.18.126 note moved in v0.18.132,'), 'old pointer line kept'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.127 and before (the v0.18.127 note moved in v0.18.135, the v0.18.126 note in v0.18.132,' in t, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.135 real SMS sign-in codes ok')

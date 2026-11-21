#!/usr/bin/env python3
"""v0.18.133 (real SMS sign-in codes; owner 2026-11-19 "Yes, build it now (Rec.)", Rules decisions/session-2026-11-06.md,
audits/impact/sms-sign-in.md): checks contract.json#smsSignIn (default OFF, daily cap, key NAMES only, texts sv / fr / en
without a link, one GSM-7 SMS part), CountryRules.smsSignIn in openapi.yaml, auth.signInErrors left as released, the
CONTRACT.md note and section 8 line, and the v0.18.127 note moved word for word to CHANGELOG.md (Rule 25). Run by
scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, re, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 133), 'version 0.18.133 or later'
s = c['smsSignIn']
d = c['configDefaults']['smsSignIn']
assert d['enabled'] is False, 'default OFF (nothing changes until the admin switch is on)'
lo, hi = s['dailyCapRange']
assert (lo, hi) == (10, 100000) and lo <= d['dailyCap'] <= hi and d['dailyCap'] == 200, 'daily cap default inside its range'
assert s['serverKeys'] == ['ELKS_API_USERNAME', 'ELKS_API_PASSWORD'], 'server key names (names only, never values)'
assert s['countries'] == {'+46': 'SE', '+33': 'FR', '+216': 'TN'}, 'calling codes of the served countries'
m = s['mobileNumbers']
assert set(m) == {'SE', 'FR', 'TN'}, 'one mobile pattern per served country'
for number, country, ok in (('+46701234567', 'SE', True), ('+46721234567', 'SE', True), ('+46731234567', 'SE', True), ('+46761234567', 'SE', True), ('+46791234567', 'SE', True),
                            ('+46771234567', 'SE', False), ('+46751234567', 'SE', False), ('+46741234567', 'SE', False), ('+46711234567', 'SE', False), ('+46781234567', 'SE', False),
                            ('+46701234567\n', 'SE', False), ('x+46701234567', 'SE', False), ('+4681234567', 'SE', False), ('+46900123456', 'SE', False), ('+467012345678', 'SE', False),
                            ('+33612345678', 'FR', True), ('+33712345678', 'FR', True), ('+33123456789', 'FR', False), ('+33899123456', 'FR', False),
                            ('+21620123456', 'TN', True), ('+21671123456', 'TN', False), ('+21688123456', 'TN', False)):
    assert bool(re.fullmatch(m[country], number)) is ok, 'mobile rule ' + repr(number)
    assert number.lstrip('x').startswith(next(k for k, v in s['countries'].items() if v == country)), 'calling code ' + number
assert re.fullmatch(r'[A-Za-z][A-Za-z0-9]{2,10}', s['sender']), 'sender name 46elks accepts (3-11 letters and digits)'
assert set(s['errors']) == {'sign_in_restricted', 'sms_daily_limit', 'sms_not_sent'}, 'reasons'
assert s['errors']['sms_daily_limit'].startswith('503 unavailable') and s['errors']['sms_not_sent'].startswith('503 unavailable'), 'both retryable 503'
assert 'every hand-over the company did not answer or answered with a server error' in s['dailyCap'] and 'only an SMS the company answered with a refusal (a 4xx answer) is not counted' in s['dailyCap'], 'a time-out or a 5xx counts on the daily limit'
assert 'fail closed' in s['dailyCap'] and 'exactly as before' in s['active'] and 'never gets an SMS' in s['active'], 'fail closed / unchanged until active'
# GSM 03.38 basic set (one SMS part = 160 of these)
GSM7 = set("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà")
for lang in ('sv', 'fr', 'en'):
    text = s['texts']['sms'][lang]
    assert text.count('{code}') == 1 and text.startswith('Movera'), lang + ': app name and the code once'
    assert 'http' not in text.lower() and 'www' not in text.lower() and '/' not in text, lang + ': no link'
    filled = text.replace('{code}', '0' * s['codeLength'])
    assert len(filled) <= 160 and set(filled) <= GSM7, lang + ': one GSM-7 SMS part'
    for k in ('smsNotSent', 'smsDailyLimit'):
        assert s['texts'][k][lang].strip(), k + ' ' + lang
a = s['alert']
assert a['nearPercent'] == 80 and '{0}' in a['titles']['near'] and '{1}' in a['titles']['reached'] and 'system_health' in a['rule'], 'alert'
assert 'never hold the code' in s['logs'], 'logs'
assert list(c['auth']['signInErrors']) == ['note', 'invalid_otp_code', 'invalid_otp_session', 'otp_expired', 'otp_too_many_attempts', 'otp_resend_too_soon', 'otp_too_many', 'sign_in_restricted', 'otp_locked_today', 'account_suspended'], 'auth.signInErrors kept as released (Rule 21)'
assert hashlib.sha256(json.dumps(c['auth']['signInErrors'], ensure_ascii=False, sort_keys=True).encode()).hexdigest() == 'c88d73625146cb119597368447cbf8bc7601263a8f7f6f102ea8428a96cc2712', 'auth.signInErrors texts kept word for word (Rule 21)'
assert 'never signs one in, in any environment' in s['code'] and 'in one step per country' in s['dailyCap'] and 'do not ask again by themselves' in s['errors']['sms_not_sent'], 'test code / atomic limit / no auto retry'
assert c['auth']['otp']['codeLength'] == 4 and re.fullmatch(r'[0-9]{4}', c['auth']['testSignIn']['code']), 'the test code and auth.otp.codeLength stay 4 digits (test numbers unchanged)'
assert s['codeLength'] == 6, 'owner 2026-11-19 "6 digits (Rec.)": a real SMS code is 6 digits'
assert 'smsSignIn.codeLength digits' in s['code'] and 'auth.otp.codeLength digits' not in s['code'], 'code wording says 6'
n = s['codeLengthNote']
assert '"6 digits (Rec.)"' in n and 'stay 4 digits' in n and 'An answer without the field' in n and 'never guess the length from the phone number' in n and 'counts as a try' in n and 'cannot enter an SMS code' in n and 'this note decides the shape of a code' in n and 'checks the WHOLE code' in n and 'it is a sign-in code' in n, 'codeLengthNote'
spec = yaml.safe_load(open('openapi.yaml'))
p = spec['components']['schemas']['CountryRules']['properties']['smsSignIn']
assert p['properties']['enabled']['default'] is False and p['properties']['dailyCap']['minimum'] == lo and p['properties']['dailyCap']['maximum'] == hi and p['properties']['dailyCap']['default'] == 200, 'openapi CountryRules.smsSignIn'
assert p.get('additionalProperties') is False and 'required' not in p, 'both parts optional, no other key'
assert 'v0.18.133 (contract.json#smsSignIn)' in spec['paths']['/auth/otp/request']['post']['description'], 'openapi otp request wording'
sch = spec['components']['schemas']
oc = sch['OtpChallenge']
assert oc['properties']['codeLength'] == {'type': 'integer', 'enum': [4, 6], 'description': oc['properties']['codeLength']['description']} and 'codeLength' not in oc['required'], 'OtpChallenge.codeLength optional, 4 or 6'
assert oc['required'] == ['requestId', 'sessionId', 'expiresAt', 'retryAfterSeconds'], 'OtpChallenge required fields as released'
assert spec['paths']['/account/phone/change']['post']['responses']['200']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/OtpChallenge'}, 'the phone change answers the same OtpChallenge'
for name in ('OtpVerifyRequest', 'AccountPhoneVerify'):
    pat = sch[name]['properties']['code']['pattern']
    for code, ok in (('1234', True), ('123456', True), ('12345', False), ('1234567', False), ('123', False), ('', False), ('12345a', False), ('1234\n', False), (' 123456', False)):
        assert bool(re.fullmatch(pat, code)) is ok, name + ' code ' + repr(code)
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.133 (real SMS sign-in codes;' in t, 'CONTRACT.md note'
n133 = next(l for l in t.split('\n') if l.startswith('v0.18.133 (real SMS sign-in codes;'))
assert 'follows v0.18.132; SMS-alone' in n133 and 'reserved for S5' not in n133, 'CONTRACT.md note follows v0.18.132 (SMS-alone, owner 2026-11-20)'
# No line of CONTRACT.md doubled by an edit (contracts #187 lesson): every long line is there once.
_long = [l for l in t.split('\n') if len(l) > 40]
_dup = sorted({l for l in _long if _long.count(l) > 1})
assert not _dup, 'CONTRACT.md has doubled lines: %r' % [l[:60] for l in _dup[:3]]
assert 'v0.18.133 (`contract.json#smsSignIn`): **real SMS codes.**' in t and 'random 6-digit code (`smsSignIn.codeLength`)' in t and '**A code sent by SMS is 6 digits**' in t and 'codeLength?' in t, 'CONTRACT.md section 8 line + 6 digits'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n127 = next(l for l in cl if l.startswith('v0.18.127 (S7 W2 Q119, plan 0.21;'))
assert '\n' + n127 not in t and cl.count(n127) == 1, 'v0.18.127 note moved once'
assert hashlib.sha256(n127.encode()).hexdigest() == 'b51a0ff2ebb7016f49c9a557fb973e2a146ceaece339a99b3829d3760b5e644e', 'v0.18.127 note moved word for word'
j = cl.index(n127)
assert cl[j - 2].startswith('v0.18.133 (real SMS sign-in codes; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.126 and before (the v0.18.126 note moved in v0.18.132,'), 'old pointer line kept'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.127 and before (the v0.18.127 note moved in v0.18.133, the v0.18.126 note in v0.18.132,' in ch, 'new pointer line (v0.18.134 moved it to CHANGELOG.md word for word)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.133 real SMS sign-in codes ok')

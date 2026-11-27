#!/usr/bin/env python3
"""v0.18.165 (sign-in code 60 s; owner 2026-11-25 "Je voit les autre app mais 60 s", "Nn on laisse 60 seconde demander nv aussi",
"Mm si on demande pas nv code apres 60 s doit être bloquer"): auth.otp.expiresSeconds 60 and retryAfterSeconds 60, the notes,
the openapi OtpChallenge text and the v0.18.160 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25).
Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 165), 'version 0.18.165 or later'
o = c['auth']['otp']
assert o['expiresSeconds'] == 60, 'the code lives 60 s'
assert o['retryAfterSeconds'] == 60, 'a new code after 60 s'
assert o['codeLength'] == 4 and o['maxAttempts'] == 5 and o['channel'] == 'sms', 'other otp values unchanged'
assert 'v0.18.165' in o['note'] and 'otp_resend_too_soon' in o['note'] and '410 otp_expired' in o['note'], 'otp note'
md = open('CONTRACT.md').read()
# v0.18.170 (Rule 25): the v0.18.165 note moved word for word to CHANGELOG.md; it is checked in both files.
ch = open('CHANGELOG.md').read()
assert md.startswith('# Movera shared contract v0.18.165') or tuple(map(int, c['version'].split('.'))) > (0, 18, 165), 'title'
assert 'v0.18.165 (sign-in code 60 s;' in md + ch and 'the v0.18.160 note moved in v0.18.165' in md, 'CONTRACT.md note + pointer'
assert '60 s (v0.18.165, was 300 s), resend after 60 s (v0.18.165, was 30 s)' in md, '§8 values'
ch = open('CHANGELOG.md').read()
assert 'v0.18.165 (sign-in code 60 s; Rule 21 / Rule 25' in ch and 'v0.18.160 (free pickup move 300 m;' in ch, 'v0.18.160 note moved'
spec = yaml.safe_load(open('openapi.yaml'))
assert spec['components']['schemas']['OtpChallenge']['description'].startswith('The code lives 60 s;'), 'openapi OtpChallenge'
e = c['auth']['emailCode']
assert e['expiresSeconds'] == 90 and e['retryAfterSeconds'] == 90 and e['since'] == '0.18.165', 'e-mail change code 90 s'
assert 'Mail 90 s' in e['note'] and 'otp_resend_too_soon' in e['note'], 'emailCode note'
assert 'auth.emailCode' in md + ch, 'CONTRACT.md e-mail 90 s'
print('v0.18.165 ok')
assert 'v0.18.165 (auth.emailCode): the e-mail code lives 90 s' in spec['paths']['/account/email/change']['post']['description'], 'openapi e-mail change 90 s'
print('v0.18.165 e-mail 90 s ok')

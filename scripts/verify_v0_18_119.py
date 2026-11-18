#!/usr/bin/env python3
"""v0.18.119 (S7 W2 Q117 + Q118; owner 2026-11-15 "Yes, per user (Rec.)" / "Yes, phone + address (Rec.)", 2026-11-16 OQ-1
"Lock at 60 for 24 h (Rec.)" / OQ-2 "Keep fixed in server (Rec.)"; Rules audits/impact/s7-q117-q118.md, -supervisor.md MF-3):
wording only. Checks the write-limit key (an expired, rightly signed token per user with 401 not 429; the code calls per
phone + address; both refresh calls per session + address; the phone-alone and address-alone ceilings, fixed in the
server), the number lock over all addresses (4 x wrongCodesPerDay in 24 h, up to 24 h, admin unlock) in every place that
named the lock per number + address only, the released text kept (Rule 21), that no field was added, the openapi copy and
CONTRACT.md. Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 119), 'version 0.18.119 or later'
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']

# --- rateLimit.key (Q117 + Q118)
rl = c['rateLimit']
k = rl['key']
assert k.startswith('v0.18.119 (S7 W2 Q117 + Q118;') and 'Lock at 60 for 24 h (Rec.)' in k and 'Keep fixed in server (Rec.)' in k, 'key: source'
assert 'ran out but carries the server\'s signature, at most the refresh lifetime' in k and 'on a key of its own apart from the live one' in k, 'key: expired token per user'
assert 'the answer is still 401 (the app refreshes), not 429' in k and 'no safety-write pass' in k, 'key: 401 not 429, no safety pass'
assert 'POST /auth/otp/request and /auth/otp/verify: the phone in the body + the client address' in k, 'key: OTP per phone + address'
assert "POST /auth/refresh and /admin/auth/refresh: the refresh token's session + the client address" in k, 'key: refresh per session + address'
assert 'the phone alone and the address alone are only ceilings of 10 × the address budget (a fixed server factor, not an admin setting)' in k, 'key: ceilings, fixed'
assert "one address alone never fills a number's ceiling" in k and 'refresh look-ups a minute' in k, 'key: order and look-ups (MF-1 c, SF-3)'
kb = rl['keyBefore0_18_119']
assert kb == 'Replaced in v0.18.119 (kept, Rule 21): a valid access token: its actor and user (sub), so many accounts behind one address never share a budget; no or an invalid token: the client address (the address the trusted proxy saw, TRUST_PROXY_HOPS)', 'released key kept (Rule 21)'
assert list(rl) == ['version', 'note', 'applies', 'safetyWrites', 'ownBudget', 'key', 'keyBefore0_18_119', 'window', 'signInOutsideProduction', 'defaults', 'settings', 'error', 'clients'], 'rateLimit: only keyBefore0_18_119 added'

# --- the number lock over all addresses (Q118 + OQ-1 / OQ-2)
au = c['auth']
n = au['otp']['note']
assert 'wrong codes are locked per number AND source (client address)' in n, 'auth.otp.note v0.18.14 text kept'
assert '4 × countryLimits.wrongCodesPerDay wrong codes in 24 h over all addresses and both apps (default 60; the factor 4 is fixed in the server' in n, 'otp.note: the ceiling'
assert 'locked for EVERY address' in n and 'even with the right code' in n and '(at most 24 h) or an admin unlocks it' in n and 'lifts both locks for all addresses at once' in n, 'otp.note: lock and unlock'
assert 'Phones already signed in keep working' in n, 'otp.note: signed-in phones'
assert list(au['otp']) == ['codeLength', 'expiresSeconds', 'retryAfterSeconds', 'maxAttempts', 'channel', 'note'], 'auth.otp: no key added'
lt = au['signInErrors']['otp_locked_today']
assert lt.startswith('429 rate_limited (v0.18.14): too many wrong codes for this number today') and 'v0.18.119' in lt and 'every address gets it for that number' in lt, 'signInErrors.otp_locked_today'
assert list(au['signInErrors']) == ['note', 'invalid_otp_code', 'invalid_otp_session', 'otp_expired', 'otp_too_many_attempts', 'otp_resend_too_soon', 'otp_too_many', 'sign_in_restricted', 'otp_locked_today', 'account_suspended'], 'signInErrors: no reason added'
w = c['countryLimits']['fields']['wrongCodesPerDay']
assert w.startswith('Wrong sign-in codes for one phone number from one client address in 24 h') and "4 × this value (a fixed server factor) is also the number's ceiling over all addresses" in w, 'wrongCodesPerDay field text'
assert c['countryLimits']['defaults']['wrongCodesPerDay'] == 15 and list(c['countryLimits']['fields']) == list(c['countryLimits']['defaults']), 'countryLimits: no field added'
si = c['deepFix1']['signIn']
assert si.startswith('Codes stay 4 digits (owner). otp_locked_today per number + address;') and 'otp_locked_today also per number over all addresses at 4 × wrongCodesPerDay' in si, 'deepFix1.signIn'

# --- openapi copy
for path in ['/auth/otp/request', '/auth/otp/verify', '/auth/refresh', '/admin/auth/refresh']:
    d = P[path]['post']['description'].replace('\n', ' ')
    assert 'v0.18.119 (contract.json#rateLimit.key)' in d and 'not 429' in d, 'openapi ' + path
for path in ['/auth/otp/request', '/auth/otp/verify']:
    assert 'every address gets it for that number' in P[path]['post']['description'].replace('\n', ' '), 'openapi lock ' + path
assert 'lifts both locks for all addresses at once' in P['/admin/auth/sign-in-locks/unlock']['post']['description'].replace('\n', ' '), 'openapi unlock'
assert "the number's ceiling over all addresses" in S['CountryLimits']['properties']['wrongCodesPerDay']['description'].replace('\n', ' '), 'openapi CountryLimits'

# --- CONTRACT.md
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.126: the v0.18.119 note moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.119 (S7 W2 Q117 + Q118;' in tc and 'follows v0.18.118)' in tc, 'CONTRACT.md v0.18.119 note'
assert 'v0.18.119 (S7 W2 Q117 + Q118, `rateLimit.key`): an access token that ran out but is rightly signed' in t and 'the answer stays **401**' in t, 'CONTRACT.md §47 expired token'
assert '`POST /auth/refresh` and `/admin/auth/refresh` → the refresh token\'s session + address' in t and 'per number for every address at 4 × `wrongCodesPerDay` in 24 h' in t, 'CONTRACT.md §47 keys and lock'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.119 sign-in keys and number lock ok')

#!/usr/bin/env python3
"""v0.18.132 (S7 W2 Q117 + Q118 follow-up SF-1 + SF-2; Rules audits/impact/s7-q117-followup.md): wording only. Checks
rateLimit.key says a token is not read on the four sign-in / refresh calls and an unreadable body counts on the address
at its budget, the v0.18.119 key kept word for word as keyBefore0_18_132 (Rule 21), the CONTRACT.md note and §47 line,
and the v0.18.126 note moved word for word to CHANGELOG.md (Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 132), 'version 0.18.132 or later'
rl = c['rateLimit']
k, kb = rl['key'], rl['keyBefore0_18_132']
assert 'v0.18.132 (follow-up SF-1 + SF-2' in k and 'whether or not an access token is sent (a valid or expired token is not read on these four calls)' in k, 'key: SF-1'
assert 'whose body cannot be read (not valid JSON, too large, wrong media type) counts against the client address at the address budget: over it, 429 rate_limited instead of the 400' in k, 'key: SF-2'
assert 'Without a token, POST /auth/otp/request' not in k, 'key: old "Without a token" wording replaced'
assert kb.startswith('Replaced in v0.18.132 (kept, Rule 21): v0.18.119 (S7 W2 Q117 + Q118;') and 'Without a token, POST /auth/otp/request and /auth/otp/verify' in kb, 'released key kept (Rule 21)'
assert list(rl).index('keyBefore0_18_132') == list(rl).index('key') + 1, 'keyBefore0_18_132 right after key'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.132 (S7 W2 Q117 + Q118 follow-up SF-1 + SF-2;' in t, 'CONTRACT.md note'
n132 = next(l for l in t.split('\n') if l.startswith('v0.18.132 (S7 W2 Q117 + Q118 follow-up SF-1 + SF-2;'))
assert 'follows v0.18.131)' in n132 and 'follows v0.18.130)' not in n132, 'CONTRACT.md note follows v0.18.131'
assert "v0.18.132: a token sent on these four calls is not read; a body that cannot be read counts against the address at its budget (429 when full);" in t, 'CONTRACT.md §47'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n126 = next(l for l in cl if l.startswith('v0.18.126 (S7 W2 Q126 = Q-B4;'))
assert '\n' + n126 not in t and hashlib.sha256(n126.encode()).hexdigest() == '4ad1e6cae2bf6f3a5468b2d002fdb332178ff1f46921f22014eb3beea07a43e2', 'v0.18.126 note moved word for word'
assert cl.count(n126) == 1, 'v0.18.126 note once in CHANGELOG.md'
j = cl.index(n126)
assert cl[j - 2].startswith('v0.18.132 (Q117 + Q118 follow-up wording; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.125 and before (the v0.18.125 note moved in v0.18.131, the v0.18.124 note in v0.18.130,'), 'old pointer line kept'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '8d890a6d7d2eb11df3a270da51c03d02106ca7809b200d5732b3c7c2cb72abda', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.126 and before (the v0.18.126 note moved in v0.18.132, the v0.18.125 note in v0.18.131, the v0.18.124 note in v0.18.130,' in t + ch, 'new pointer line (kept in CHANGELOG.md since v0.18.143)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.132 Q117 + Q118 follow-up wording ok')

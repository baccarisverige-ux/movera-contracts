#!/usr/bin/env python3
"""v0.18.149 (owner Rules decisions/driver-g12.md Q6; contract.json#adminSessions): an admin lists a rider's / driver's
signed-in sessions and signs one or all out with a reason; the phone hears 401 signed_out_by_movera and shows
auth.signedOut.byMoveraTexts. The CONTRACT.md note and the v0.18.143 note moved word for word to CHANGELOG.md (Rule 25).
Run by scripts/verify.sh (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 149), 'version 0.18.149 or later'
a = c['adminSessions']
for k in ('note', 'routes', 'permissions', 'scope', 'list', 'signOut', 'apps', 'errors', 'scenario', 'admin'):
    assert k in a, 'adminSessions.' + k
assert a['permissions']['signOutRider'] == 'riders.block' and a['permissions']['signOutDriver'] == 'drivers.activate', 'permissions'
for p in a['permissions'].values():
    assert p in c['adminPermissions']['values'] or ' ' in p, 'permission exists: ' + p
assert a['list']['fields'] == ['sessionId', 'app', 'device', 'platform', 'appVersion', 'lastSeenAt', 'createdAt'], 'list fields'
assert 'IP address' in a['list']['privacy'], 'no IP address'
assert a['errors']['sign_out_on_trip'] == '409 conflict' and c['auth']['signOutOnTrip']['reason'] == 'sign_out_on_trip', 'driver on trip reuses sign_out_on_trip'
so = c['auth']['signedOut']
assert so['reasons']['signed_out_by_movera'] == 'revoked', 'reason kind'
assert so['byMoveraTexts']['en'] == 'You were signed out by Movera', 'en text'
assert set(so['byMoveraTexts']) >= {'sv', 'fr', 'en'}, 'sv / fr / en'
o = yaml.safe_load(open('openapi.yaml'))
P = o['paths']
for who, perm_l, perm_s in (('riders', 'riders.read', 'riders.block'), ('drivers', 'drivers.read', 'drivers.activate')):
    idn = who[:-1] + 'Id'
    g = P['/admin/' + who + '/{' + idn + '}/sessions']['get']
    assert g['x-actor'] == ['admin'] and g['x-permission'] == perm_l, who + ' list'
    po = P['/admin/' + who + '/{' + idn + '}/sessions/sign-out']['post']
    assert po['x-permission'] == perm_s and any(p.get('$ref', '').endswith('/IdempotencyKey') for p in po['parameters']), who + ' sign-out'
sc = o['components']['schemas']
assert set(sc['AdminSession']['properties']) == set(a['list']['fields']) and sc['AdminSession']['additionalProperties'] is False, 'AdminSession shape (no ip)'
assert sc['AdminSessionSignOutCommand']['required'] == ['reason'], 'reason required'
assert 'signed_out_by_movera' in P['/auth/refresh']['post']['description'], 'refresh doc'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.149 (admin sessions' in t, 'CONTRACT.md note'
assert '`signed_out_by_movera` (an admin signed the phone out, v0.18.149' in t, 'Why signed out bullet'
import hashlib
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
assert 'follows v0.18.148)' in next(l for l in (t + ch).split('\n') if l.startswith('v0.18.149 (admin sessions, owner')), 'v0.18.149 note follows v0.18.148 (launch restack)'
# launch restack (plan K): this version moves the v0.18.143 note (the draft moved v0.18.127)
n143 = next(l for l in cl if l.startswith('v0.18.143 (owner 2026-11-20 "must rider '))
assert '\n' + n143 not in t and cl.count(n143) == 1, 'v0.18.143 note moved once'
assert hashlib.sha256(n143.encode()).hexdigest() == 'ff378d1d675bc48f1c5a1f2daa515c3565f545c6f2f96b687da2273f0f478230', 'v0.18.143 note moved word for word'
j = cl.index(n143)
assert cl[j - 2].startswith('v0.18.149 (admin sessions; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == 'eef52439e76a3b7c42dc0535ce3cf2133c7b6946d2ca2c27688c88779efe3ad2', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.143 and before (the v0.18.143 note moved in v0.18.149, the v0.18.141 note in v0.18.148, the v0.18.140' in t + ch, 'new pointer line (in CHANGELOG.md once a later version moves it)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.149 admin sessions ok')

#!/usr/bin/env python3
"""v0.18.149 (owner Rules decisions/driver-g12.md Q6; contract.json#adminSessions): an admin lists a rider's / driver's
signed-in sessions and signs one or all out with a reason; the phone hears 401 signed_out_by_movera and shows
auth.signedOut.byMoveraTexts. The CONTRACT.md note and the v0.18.127 note moved word for word to CHANGELOG.md (Rule 25).
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
assert '\nv0.18.127 (' not in t, 'v0.18.127 note moved'
ch = open('CHANGELOG.md', encoding='utf-8').read().split('\n')
n127 = next(l for l in ch if l.startswith('v0.18.127 (S7 W2 Q119, plan 0.21;'))
assert ch.count(n127) == 1 and ch[ch.index(n127) - 2].startswith('v0.18.149 (admin sessions; Rule 21 / Rule 25'), 'CHANGELOG move'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.149 admin sessions ok')

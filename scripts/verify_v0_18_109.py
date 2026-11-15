#!/usr/bin/env python3
"""v0.18.109 (server BQ-FLEETCUR, owner 2026-11-15 "What u mean fleet can earn in two currencies!", Rules
decisions/session-2026-11-06.md:1322): a fleet works in ONE country and earns in ONE currency. A driver joins only a
fleet of his own country, else 409 conflict fleet_other_country; fleet earnings count only the fleet's currency.
Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 109), 'version 0.18.109 or later'
oc = c['driverOnboarding']['fleetInvitations']['oneCountry']
assert 'session-2026-11-06.md:1322' in oc and 'ONE country' in oc and 'ONE currency' in oc, 'oneCountry owner rule'
assert "his country, else his first zone's" in oc, 'oneCountry: which country is the driver'
assert '409 conflict' in oc and 'fleet_other_country' in oc, 'oneCountry: 409 fleet_other_country'
for p in ('POST /driver/fleet/join', 'fleetJoin', 'POST /driver/fleet/invite',
          'POST /driver/fleet/invitations/{invitationId}/accept', 'POST /admin/fleets/{fleetId}/invitations/{invitationId}/accept',
          'POST /driver/onboarding'):
    assert p in oc, 'oneCountry names ' + p
assert 'changes his country away' in oc and 'other drivers' in oc, 'oneCountry: onboarding country change'
fe = c['debtModel']['driverOwes']['fleetEarnings']
assert 'v0.18.109' in fe and "fleet's currency" in fe and 'SE SEK, FR EUR, TN TND' in fe, 'fleetEarnings: fleet currency only'
assert 'paid_to_movera' in fe, 'fleetEarnings keeps the v0.18.97 rule'
spec = yaml.safe_load(open('openapi.yaml'))
assert spec['info']['version'] == c['version'], 'openapi version'
P, S = spec['paths'], spec['components']['schemas']
for path in ('/driver/fleet/join', '/driver/fleet/invite', '/driver/fleet/invitations/{invitationId}/accept',
             '/admin/fleets/{fleetId}/invitations/{invitationId}/accept', '/driver/onboarding'):
    op = P[path]['post']
    assert 'fleet_other_country' in op['description'] and 'v0.18.109' in op['description'], 'openapi description ' + path
    assert op['responses']['409'] == {'$ref': '#/components/responses/Conflict'}, 'openapi 409 ' + path
assert 'v0.18.109 reason: fleet_other_country' in S['Error']['properties']['reason']['description'], 'Error.reason list'
assert 'v0.18.109' in S['FleetEarnings']['description'], 'FleetEarnings description'
assert 'v0.18.109' in P['/driver/fleet/earnings']['get']['description'], '/driver/fleet/earnings description'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.109 (server BQ-FLEETCUR' in t, 'CONTRACT.md v0.18.109 note'
j = t.index('- **Joining is an invitation**'); fv = t.index('- **Fleet view.**')
assert 'fleet_other_country' in t[j:fv] and 'oneCountry' in t[j:fv], 'CONTRACT.md §14 joining line'
fl = t[fv:t.index('\n', fv)]
assert "fleet's currency" in fl and 'v0.18.109' in fl, 'CONTRACT.md §14 fleet view earnings line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print("v0.18.109 fleet one country ok")

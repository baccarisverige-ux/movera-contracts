#!/usr/bin/env python3
"""v0.18.134 (account deletion E1; owner button 2026-11-20 "Accept, keep debt (Rec.)", Rules
decisions/session-2026-11-06.md, audits/impact/privacy-erase-export.md): the request closes the account at once (rider and
driver), a debt never blocks it and is kept as a small record until paid or written off, everything else is erased 30
days after the request by a job (dry-run until the admin switch is on), the admin lists the requests. Run by
scripts/verify.sh (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 134), 'version 0.18.134 or later'
a = c['accountDeletion']
assert a['status'] == ['requested'], 'request answer status unchanged (additive)'
for k in ('owner', 'request', 'closeAtOnce', 'refused', 'debt', 'erase', 'kept', 'job', 'setting', 'admin', 'driver', 'rider', 'publicPage', 'open'):
    assert k in a, 'accountDeletion.' + k
assert 'Accept, keep debt (Rec.)' in a['owner'], 'owner answer quoted'
assert 'never refused because of a debt' in a['refused'] and 'deletion_open_trip' in a['refused'], 'debt never blocks; open trip does'
assert 'account_closed' in a['closeAtOnce'] and 'offline' in a['closeAtOnce'], 'closed at once'
assert 'name, phone number and amount' in a['debt'] and 'paid or written off' in a['debt'] and 'drivers who owe Movera' in a['debt'], 'debt record'
assert '30 days after the request' in a['erase'], '30 days from the request'
assert 'bookkeeping' in a['kept'] and '7 years' in a['kept'] and 'lawyer' in a['kept'], 'kept money records, flagged'
assert 'account_erase' in a['job'] and 'idempotent' in a['job'] and 'heartbeat' in a['job'], 'job'
assert a['adminStatus'] == ['requested', 'waiting', 'erased'], 'admin status'
d = c['configDefaults']['accountDeletion']
assert d == {'eraseEnabled': False, 'eraseAfterDays': 30}, 'defaults: dry-run, 30 days'
o = yaml.safe_load(open('openapi.yaml'))
S, P = o['components']['schemas'], o['paths']
assert P['/driver/account/deletion']['post']['x-actor'] == ['driver'], 'driver route'
assert '202' in P['/driver/account/deletion']['post']['responses'], 'driver 202'
ad = S['AccountDeletion']
assert ad['required'] == ['status'] and {'requestedAt', 'eraseDueAt'} <= set(ad['properties']), 'AccountDeletion fields additive'
g = P['/admin/deletion-requests']['get']
assert g['x-actor'] == ['admin'] and g['x-read-only'] is True and g['x-permission'] == 'riders.read', 'admin list'
dr = S['DeletionRequest']
assert set(dr['required']) == {'accountKind', 'accountId', 'requestedAt', 'eraseDueAt', 'status'}, 'DeletionRequest'
assert dr['properties']['status']['enum'] == a['adminStatus'], 'DeletionRequest.status'
cr = S['CountryRules']['properties']['accountDeletion']
assert cr == {'$ref': '#/components/schemas/AccountDeletionSetting'}, 'CountryRules.accountDeletion'
st = S['AccountDeletionSetting']['properties']
assert st['eraseEnabled']['default'] is False and st['eraseAfterDays']['default'] == 30 and st['eraseAfterDays']['minimum'] == 30, 'setting'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.134 (account deletion E1;' in t, 'CONTRACT.md note'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.134 ok')

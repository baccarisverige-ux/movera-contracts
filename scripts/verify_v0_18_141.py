#!/usr/bin/env python3
"""v0.18.141 DRAFT (owner 2026-11-20: a payment link when the rider cancels with a fee): contract.json#riderPayLink,
the setting (off, https link with the strict check), the read route, the kept key and Restore. Run by scripts/verify.sh."""
import json, re, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 141), 'version 0.18.141 or later'
r = c['riderPayLink']
assert set(r) == {'note', 'setting', 'read', 'cancel', 'debtLine', 'confirm', 'money', 'admin', 'driver', 'oldApps'}, 'riderPayLink keys'
assert c['configDefaults']['riderPayLink'] == {'enabled': False, 'payLink': ''}, 'off by default, no link'
assert 'rider_pay_link_invalid' in r['setting'] and 'rider_pay_link_needs_link' in r['setting'] and 'no backslash' in r['setting'] and "'user:password@'" in r['setting'], 'setting check'
assert "reference = '<riderId>-<tripId>'" in r['read'] and 'never worked out on the phone' in r['read'], 'read'
assert 'POST /admin/riders/{riderId}/fees/{tripId}/mark-paid' in r['confirm'] and 'No payment company is called' in r['confirm'], 'manual confirm (reused)'
assert 'stays a debt exactly as today' in r['note'], 'unpaid stays debt'
assert 'riderPayLink' in c['configDocs']['keptKeys']['country_rules'], 'kept key'
assert 'CountryRules.riderPayLink' in c['pricingHistory']['restoreKeeps'], 'Restore keeps it'
o = yaml.safe_load(open('openapi.yaml'))
S, P = o['components']['schemas'], o['paths']
st = S['RiderPayLinkSetting']
assert st['required'] == ['enabled'] and st['additionalProperties'] is False and st['properties']['enabled']['default'] is False, 'setting shape'
pat = st['properties']['payLink']['pattern']
for ok in ('', 'https://pay.sumup.com/b2c/XYZ'):
    assert re.match(pat, ok), ok
for bad in ('http://pay.example.com', 'javascript:alert(1)', 'https://evil.example\\@pay.example.com', 'https://a b', 'https://exämple.com'):
    assert not re.match(pat, bad), bad
assert S['CountryRules']['properties']['riderPayLink'] == {'$ref': '#/components/schemas/RiderPayLinkSetting'}, 'CountryRules.riderPayLink'
g = P['/rider/pay-movera']['get']
assert g['x-actor'] == ['rider'] and g['responses']['200']['content']['application/json']['schema']['$ref'].endswith('/RiderPayMovera'), 'rider route'
pm = S['RiderPayMovera']
assert pm['required'] == ['owed', 'reference'] and {'tripId', 'payLink'} <= set(pm['properties']), 'RiderPayMovera'
assert 'riderPayLink' in S['ConfigDraftUpdate']['properties']['removeKeys']['items']['enum'], 'removeKeys names it'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and t.count('\n') <= 1500, 'CONTRACT.md heading, size'
assert '\nv0.18.141 (DRAFT, rider fee payment link;' in open('CHANGELOG.md', encoding='utf-8').read(), 'CHANGELOG.md note'
print('v0.18.141 rider fee payment link ok')

#!/usr/bin/env python3
"""v0.18.139 (driver wallet D5; owner button 2026-11-20, Rules audits/impact/driver-wallet-cash.md): the driver's balance
with Movera on GET /driver/earnings. Checks contract.json#driverWalletBalance, the openapi field (optional, two Money
amounts), the CONTRACT.md note and line, and the v0.18.127 note moved word for word to CHANGELOG.md (Rule 25). Run by
scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 139), 'version 0.18.139 or later'
w = c['driverWalletBalance']
assert set(w) == {'note', 'field', 'sum', 'cash', 'driver', 'admin', 'rider'}, 'driverWalletBalance keys'
assert 'EarningsReport.moveraBalance { owedToMovera: Money, moveraOwesYou: Money }' in w['field'] and 'at least one of them is 0' in w['field'], 'field'
assert 'does not follow ?period, ?from or ?to' in w['field'] and 'never added' in w['field'], 'field: now, one currency'
assert 'owedToMovera = max(0, -S)' in w['sum'] and 'moveraOwesYou = max(0, S)' in w['sum'], 'sum: two sides of one signed sum'
assert 'always equal to debtModel.driverOwes.owed' in w['sum'] and 'GET /admin/drivers-owing' in w['sum'], 'sum: one number for driver and admin'
assert 'the app never adds or subtracts (never net - cashCollected, never a sum of trips)' in w['driver'], 'driver: no phone sums'
assert 'shows the cash line only, no owed line' in w['driver'], 'driver: older server'
assert 'EarningsPeriod.cashCollected' in w['cash'], 'cash line source'
o = yaml.safe_load(open('openapi.yaml'))
S, P = o['components']['schemas'], o['paths']
er = S['EarningsReport']
mb = er['properties']['moveraBalance']
assert 'moveraBalance' not in er['required'], 'moveraBalance optional (older servers)'
assert mb['required'] == ['owedToMovera', 'moveraOwesYou'] and mb['additionalProperties'] is False, 'moveraBalance: both amounts'
for k in ('owedToMovera', 'moveraOwesYou'):
    assert mb['properties'][k]['allOf'] == [{'$ref': '#/components/schemas/Money'}], 'moveraBalance.' + k
assert 'cashCollected' in S['EarningsPeriod']['properties'], 'EarningsPeriod.cashCollected stays'
assert 'v0.18.139 (driverWalletBalance)' in P['/driver/earnings']['get']['description'], 'route text'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.139 (driver wallet D5;' in t, 'CONTRACT.md note'
assert '- **Driver wallet balance** (v0.18.139, `driverWalletBalance`)' in t, 'CONTRACT.md line'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n127 = next(l for l in cl if l.startswith('v0.18.127 (S7 W2 Q119'))
assert '\n' + n127 not in t and hashlib.sha256(n127.encode()).hexdigest() == 'b51a0ff2ebb7016f49c9a557fb973e2a146ceaece339a99b3829d3760b5e644e', 'v0.18.127 note moved word for word'
assert cl.count(n127) == 1, 'v0.18.127 note once in CHANGELOG.md'
j = cl.index(n127)
assert cl[j - 2].startswith('v0.18.139 (driver wallet balance; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '500ff2fd72593fe8c33c06d0cb1634754ea5da6aa47af9bb54ceee2fa8ded620', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.127 and before (the v0.18.127 note moved in v0.18.139, the v0.18.126 note in v0.18.132,' in t, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
# Second part: the temporary monthly pay request (owner 2026-11-20).
r = c['driverPayRequest']
assert set(r) - {'stripe'} == {'note', 'setting', 'job', 'notice', 'read', 'driver', 'confirm', 'payouts', 'admin', 'rider', 'oldApps'}, 'driverPayRequest keys (stripe: the DRAFT Stripe payment)'
assert c['configDefaults']['driverPayRequest'] == {'enabled': False, 'dayOfMonth': 1, 'payLink': '', 'minAmount': None}, 'off by default, no link'
assert 'TEMPORARY' in r['note'] and 'Movera takes no payment in the app' in r['note'], 'note'
assert 'no longer needed to switch it on' in r['setting'] and 'pay_request_needs_amount' in r['setting'] and 'pay_request_invalid' in r['setting'], 'setting reasons'
assert 'ABOVE minAmount' in r['job'] and 'asks nobody twice' in r['job'] and 'GET /healthz/jobs' in r['job'], 'job: above the minimum, once, heartbeat'
n = r['notice']
assert n['kind'] == 'driver_pay_movera' and n['deepLink'] == 'movera-driver://pay-movera', 'notice kind + deep link'
for lang in ('sv', 'fr', 'en'):
    assert n['title'][lang] and '{amount}' in n['body'][lang], 'notice text ' + lang
assert "reference = '<driverId>-<YYYYMM>'" in r['read'], 'reference'
assert 'the app adds no amount to it' in r['driver'] and 'never worked out on the phone' in r['driver'], 'driver screen'
assert 'POST /admin/drivers/{driverId}/paid-movera' in r['confirm'] and 'Nothing is confirmed automatically' in r['confirm'], 'manual confirm'
assert 'No payout rule changes' in r['payouts'], 'payout rules untouched'
kk = c['configDocs']['keptKeys']
assert 'driverPayRequest' in kk['country_rules'] and kk['country_rules'][:6] == ['payoutMode', 'payoutSchedule', 'maxRiderDebt', 'driverOwesLimit', 'calls.adminCallRoles', 'calls.phoneProvider'], 'kept key'
assert 'CountryRules.driverPayRequest is kept the same way' in c['pricingHistory']['restoreKeeps'], 'Restore keeps it'
assert 'driverPayRequest' in S['ConfigDraftUpdate']['properties']['removeKeys']['items']['enum'], 'removeKeys names it'
st = S['DriverPayRequestSetting']
assert st['required'] == ['enabled'] and st['additionalProperties'] is False, 'setting shape'
assert st['properties']['enabled']['default'] is False and st['properties']['dayOfMonth']['minimum'] == 1 and st['properties']['dayOfMonth']['maximum'] == 28, 'setting defaults'
import re
pat = st['properties']['payLink']['pattern']
assert re.match(pat, '') and re.match(pat, 'https://pay.example.com/b2c/XYZ') and not re.match(pat, 'http://pay.example.com') and not re.match(pat, 'javascript:alert(1)'), 'payLink https only'
assert S['CountryRules']['properties']['driverPayRequest'] == {'$ref': '#/components/schemas/DriverPayRequestSetting'}, 'CountryRules.driverPayRequest'
g = P['/driver/pay-movera']['get']
assert g['x-actor'] == ['driver'] and g['responses']['200']['content']['application/json']['schema']['$ref'].endswith('/DriverPayMovera'), 'driver route'
pm = S['DriverPayMovera']
assert pm['required'] == ['enabled', 'owedToMovera', 'reference'] and {'payLink', 'minAmount', 'request'} <= set(pm['properties']), 'DriverPayMovera'
assert ' **Monthly pay request** (v0.18.139, `driverPayRequest`' in t, 'CONTRACT.md line 2'
print('v0.18.139 driver wallet balance + monthly pay request ok')
# DRAFT Stripe driver payment (…-dpay-stripe-c): the route, the answer, the flag.
if 'stripe' in r:
    assert '/driver/pay-movera/pay' in P and 'stripe' in S['DriverPayMovera']['properties'] and 'clientSecret' in S['StripeDriverPayment']['properties'], 'driver Stripe payment'
    assert 'Driver paid Movera' in r['stripe'] and 'paidTwice' in r['stripe'], 'same effect as Driver paid Movera; the rest flagged'

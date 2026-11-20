#!/usr/bin/env python3
"""v0.18.141 DRAFT (owner 2026-11-20 "So we use stripe"): contract.json#stripeFees, the rider pays an owed fee with
Stripe in the app (test mode), the signed webhook, the admin status + refund, the country switch (off). Run by verify.sh."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 141), 'version 0.18.141 or later'
assert 'riderPayLink' not in c, 'the SumUp-link draft is replaced by Stripe'
f = c['stripeFees']
assert set(f) == {'note', 'keys', 'setting', 'pay', 'payment', 'webhook', 'refund', 'adminRead', 'rider', 'profile', 'admin', 'driver', 'oldApps'}, 'stripeFees keys'
assert c['configDefaults']['riderFeeStripe'] == {'enabled': False}, 'off by default'
assert 'STRIPE_SECRET_KEY' in f['keys'] and 'STRIPE_WEBHOOK_SECRET' in f['keys'] and 'STRIPE_PUBLISHABLE_KEY' in f['keys'] and "'sk_test_" in f['keys'], 'keys: env names, test mode only'
assert 'min(the fee\'s amount, her debt now' in f['pay'] and 'never a phone number' in f['pay'], 'pay: server amount'
assert 'bad_signature' in f['webhook'] and 'handled once' in f['webhook'] and 'paidTwice' in f['webhook'], 'webhook: signed, once, paid twice'
assert 'does NOT put the fee back in her debt' in f['refund'], 'refund rule'
assert 'stays a debt exactly as today' in f['note'], 'unpaid stays debt'
assert 'riderFeeStripe' in c['configDocs']['keptKeys']['country_rules'] and 'CountryRules.riderFeeStripe' in c['pricingHistory']['restoreKeeps'], 'kept key + restore'
o = yaml.safe_load(open('openapi.yaml'))
S, P = o['components']['schemas'], o['paths']
assert S['CountryRules']['properties']['riderFeeStripe'] == {'$ref': '#/components/schemas/RiderFeeStripeSetting'}, 'setting'
assert S['RiderFeeStripeSetting']['properties']['enabled']['default'] is False, 'setting default'
pm = S['StripeFeePayment']
assert pm['required'] == ['tripId', 'paymentIntentId', 'amount', 'status', 'createdAt'] and 'clientSecret' in pm['properties'], 'StripeFeePayment'
assert 'feesPayableByCard' in S['Rider']['properties'], 'Rider.feesPayableByCard'
for path in ('/rider/fees/{tripId}/pay', '/webhooks/stripe', '/admin/riders/{riderId}/fees/{tripId}/stripe-refund'):
    assert 'post' in P[path], path
assert P['/webhooks/stripe']['post']['security'] == [], 'webhook public'
assert 'get' in P['/admin/riders/{riderId}/fee-payments'], 'admin read'
assert 'riderFeeStripe' in S['ConfigDraftUpdate']['properties']['removeKeys']['items']['enum'], 'removeKeys'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and t.count('\n') <= 1500, 'CONTRACT.md heading, size'
assert '\nv0.18.141 (DRAFT, Stripe for rider fees;' in open('CHANGELOG.md', encoding='utf-8').read(), 'CHANGELOG.md note'
print('v0.18.141 Stripe rider fee ok')
# Money review fixes (2026-11-20): overpaid part and amount mismatch are visible to the admin.
assert 'overpaid' in pm['properties'] and 'amountMismatch' in pm['properties'], 'StripeFeePayment overpaid + amountMismatch'
assert 'Lock order' in f['webhook'] and 'charge_already_refunded' in f['refund'] and 'not kept in the Idempotency-Key store' in f['pay'], 'review fixes'

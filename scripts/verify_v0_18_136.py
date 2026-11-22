#!/usr/bin/env python3
"""v0.18.136 DRAFT (owner 2026-11-20 "So we use stripe"): contract.json#stripeFees, the rider pays an owed fee with
Stripe in the app (test mode), the signed webhook, the admin status + refund, the country switch (off). Run by verify.sh."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 136), 'version 0.18.136 or later'
assert 'riderPayLink' not in c, 'the SumUp-link draft is replaced by Stripe'
f = c['stripeFees']
assert set(f) == {'note', 'keys', 'setting', 'pay', 'payment', 'webhook', 'refund', 'adminRead', 'rider', 'profile', 'admin', 'driver', 'oldApps', 'status'}, 'stripeFees keys'
assert c['configDefaults']['riderFeeStripe'] == {'enabled': False}, 'off by default'
assert 'STRIPE_SECRET_KEY' in f['keys'] and 'STRIPE_WEBHOOK_SECRET' in f['keys'] and 'STRIPE_PUBLISHABLE_KEY' in f['keys'] and "'sk_test_" in f['keys'] and "'sk_live_" in f['keys'], 'keys: env names, test or live mode'
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
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # the note moved to CHANGELOG.md in v0.18.144
assert '\nv0.18.136 (Stripe for rider fees; Stripe test or live keys' in tc and 'follows v0.18.134)' in next(l for l in tc.split('\n') if l.startswith('v0.18.136 (Stripe for rider fees; Stripe test or live keys')), 'CONTRACT.md top note (launch restack: was a DRAFT note in CHANGELOG.md), follows v0.18.134'
print('v0.18.136 Stripe rider fee ok')
# Money review fixes (2026-11-20): overpaid part and amount mismatch are visible to the admin.
assert 'overpaid' in pm['properties'] and 'amountMismatch' in pm['properties'], 'StripeFeePayment overpaid + amountMismatch'
assert 'Lock order' in f['webhook'] and 'charge_already_refunded' in f['refund'] and 'not kept in the Idempotency-Key store' in f['pay'], 'review fixes'
# Stripe live mode (owner 2026-11-21 "Yes, build live mode now (Recommended)"): one mode, production = live, never a mix.
assert 'MOVERA_ENV production takes live keys only' in f['keys'] and 'mixed_keys' in f['keys'] and 'test_keys_in_production' in f['keys'] and 'live_keys_outside_production' in f['keys'], 'keys: mode rules'
assert 'wrong_mode' in f['webhook'] and 'system_health:stripe_keys' in f['status'], 'webhook mode + admin alert'
st = S['StripeStatus']
assert st['properties']['mode']['enum'] == ['live', 'test', 'off'] and 'no_keys' in st['properties']['reason']['enum'] and st['required'] == ['mode'], 'StripeStatus'
assert 'get' in P['/admin/payments/stripe-status'], 'admin Stripe status'
assert 'test publishable' not in json.dumps(pm), 'publishableKey: either mode'
print('v0.18.136 Stripe live mode ok')

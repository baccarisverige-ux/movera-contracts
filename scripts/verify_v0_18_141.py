#!/usr/bin/env python3
"""v0.18.141 (the driver pays his monthly amount owed to Movera with Stripe; owner 2026-11-20 "So we use stripe ... And
for the driver to pay his monthly invoice"): contract.json#driverPayRequest.stripe, POST /driver/pay-movera/pay,
StripeDriverPayment, DriverPayMovera.stripe, payLink as hidden legacy. Built as a draft under the number 0.18.139; the
checks below were in scripts/verify_v0_18_139.py and moved here word for word in the launch restack (Rules
plan/MERGE-PLAN-LAUNCH-2026-11-21.md, plan K slot 6). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 141), 'version 0.18.141 or later'
o = yaml.safe_load(open('openapi.yaml'))
S, P = o['components']['schemas'], o['paths']
r = c['driverPayRequest']
# DRAFT Stripe driver payment (…-dpay-stripe-c): the route, the answer, the flag.
assert 'stripe' in r, 'driverPayRequest.stripe'
if 'stripe' in r:
    assert '/driver/pay-movera/pay' in P and 'stripe' in S['DriverPayMovera']['properties'] and 'clientSecret' in S['StripeDriverPayment']['properties'], 'driver Stripe payment'
    assert 'Driver paid Movera' in r['stripe'] and 'paidTwice' in r['stripe'], 'same effect as Driver paid Movera; the rest flagged'
assert r['stripe'].startswith('v0.18.141 DRAFT (v0.18.136 + v0.18.139 together;') and '; v0.18.141 DRAFT (owner 2026-11-20' in r['setting'], 'the Stripe driver payment texts carry v0.18.141 (renumbered from the 0.18.139 draft)'
assert 'no longer needed to switch it on' in r['setting'], 'payLink is hidden legacy'
t = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
tc = t + ch
assert t.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md title'
n141 = next(l for l in tc.split('\n') if l.startswith("v0.18.141 (Stripe for the driver's monthly payment;"))
assert 'follows v0.18.140)' in n141 and '`contract.json#driverPayRequest.stripe`' in n141, 'v0.18.141 note follows v0.18.140'
# the move (Rule 25 size, Rule 21 word for word): the v0.18.132 note and the old pointer line now in CHANGELOG.md
n132 = next(l for l in cl if l.startswith('v0.18.132 (S7 W2 Q117 + Q118 follow-up S'))
assert '\n' + n132 not in t and cl.count(n132) == 1, 'v0.18.132 note moved once'
assert hashlib.sha256(n132.encode()).hexdigest() == '398158dfea2921e7d0252481cb1b70963d01a27802687914a3a76d422adbe3ba', 'v0.18.132 note moved word for word'
j = cl.index(n132)
assert cl[j - 2].startswith("v0.18.141 (Stripe for the driver's monthly payment; Rule 21 / Rule 25: moved from CONTRACT.md word for word"), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '87cb369f6b9ede28ce100d4adc622ae69f11b42505f89a0d367026000e5a4e32', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.132 and before (the v0.18.132 note moved in v0.18.141, the v0.18.131 note in v0.18.140, the v0.18.130' in t + ch, 'new pointer line (in CHANGELOG.md once a later version moves it)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.141 Stripe driver payment ok')

#!/usr/bin/env python3
"""v0.18.174 (price change at booking asks only on a rise; owner 2026-11-28): contract.json#priceChangeAsk, openapi
CreateTripRequest / RescheduleCommand.agreedQuoteId + priceAccepted (optional, no money field), the 409 reason
price_changed_ask, fixtures/price_change_ask.json follows the rule, the CONTRACT.md note and the v0.18.168 note moved
word for word to CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh (Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 174), 'version 0.18.174 or later'
g = c['priceChangeAsk']
assert g['since'] == '0.18.174', 'since'
for k in ('note', 'request', 'rule', 'agreedQuote', 'oldApps', 'rider', 'driver', 'admin'):
    assert isinstance(g[k], str) and g[k], k
assert list(g['reasons']) == ['price_changed_ask'], 'one new reason'
assert 'priceChangeAskAbovePct' not in json.dumps(c).replace('priceChangeAskAbovePct was dropped', ''), 'no tolerance key (owner dropped it)'
assert 'WITHOUT the expiry' in g['agreedQuote'] and 'MISSING' in g['agreedQuote'] and 'quote_mismatch' in g['agreedQuote'], 'agreed quote lifetime'
spec = yaml.safe_load(open('openapi.yaml'))
sch = spec['components']['schemas']
for name in ('CreateTripRequest', 'RescheduleCommand'):
    t = sch[name]
    assert 'agreedQuoteId' not in t.get('required', []) and 'priceAccepted' not in t.get('required', []), name + ' optional'
    assert t['properties']['priceAccepted']['type'] == 'boolean', name + ' priceAccepted boolean'
    assert t['properties']['agreedQuoteId']['allOf'] == [{'$ref': '#/components/schemas/Id'}], name + ' agreedQuoteId Id'
    for money in ('total', 'totalMinor', 'fareMinor', 'price', 'amount'):
        assert money not in t['properties'], name + ' carries no client amount: ' + money
for name in ('CreateTripRequest', 'RescheduleCommand'):
    assert sch[name]['not'] == {'anyOf': [{'required': [f]} for f in g['noClientAmount']['fields']]}, name + ' forbids a client amount'
assert {'total', 'fareMinor', 'price'} <= set(g['noClientAmount']['fields']), 'money fields listed'
assert 'price_changed_ask' in sch['Error']['properties']['reason']['description'], 'Error.reason lists price_changed_ask'
f = json.load(open('fixtures/price_change_ask.json'))
assert f['since'] == '0.18.174' and len(f['cases']) >= 8
for case in f['cases']:
    a, n, ok = case['agreed'], case['fresh'], case['priceAccepted'] is True
    ask = (a is None or n > a) and not ok
    assert case['result'] == ('price_changed_ask' if ask else 'booked'), case['name']
    assert case['fareMinor'] == (None if ask else n), case['name'] + ': the fare is always the fresh quote'
md = open('CONTRACT.md', encoding='utf-8').read()
ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'title (v0.18.175: the newest version, as verify_v0_18_172.py)'
assert 'v0.18.174 (price change at booking asks only on a rise;' in md and '**Price change at booking** (v0.18.174' in md, 'notes'
assert '\nv0.18.168 (' not in md and '\nv0.18.168 (' in ch, 'v0.18.168 note moved'
assert md.count('\n') <= 1500, 'CONTRACT.md at most 1500 lines'
print('v0.18.174 priceChangeAsk ok')

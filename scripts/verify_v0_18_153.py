#!/usr/bin/env python3
"""v0.18.153 (P29 driver income year file, EU DAC7; owner 2026-11-21 "Don't only save ! Execute ! ..." + "Also another one
( yearly but with monthly details ) ...", Rules LAUNCH-RULE.md P29): contract.json#driverIncomeYear, the openapi copy
(part 1730: GET /admin/finance/driver-income, its .csv and GET /driver/income-statement), the CONTRACT.md note and KPIs
line, and the v0.18.148 note moved word for word to CHANGELOG.md (Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 153), 'version 0.18.153 or later'
keys = list(c)
assert keys.index('driverIncomeYear') == keys.index('kpis') + 1, 'driverIncomeYear right after kpis'
d = c['driverIncomeYear']
assert list(d) == ['note', 'why', 'payee', 'money', 'periods', 'addUp', 'partial', 'admin', 'driver', 'texts', 'apps'], 'driverIncomeYear keys'
assert 'follows v0.18.152)' in d['note'] and 'migration 0132' in d['note'] and 'no admin setting' in d['note'], 'note'
assert 'lag (2022:1681)' in d['why'] and 'never builds the tax office' in d['why'], 'why: DAC7, no XML'
assert 'kind company' in d['payee'] and 'kind driver' in d['payee'] and 'never the full account number' in d['payee'], 'payee'
FIELDS = ['rides', 'grossFares', 'tips', 'bonuses', 'adjustments', 'pickupPay', 'feeShare', 'moveraCommission', 'moveraFees', 'netEarnings', 'cashCollectedByDriver', 'paidOutByMovera']
assert list(d['money']) == ['note'] + FIELDS, 'money fields'
assert 'Never added across currencies' in d['money']['note'] and 'paid_to_movera' in d['money']['note'], 'money note'
assert 'pay in the car (cash) included' in d['money']['rides'] and '= GET /driver/earnings net' in d['money']['netEarnings'], 'cash rides, net = earnings net'
assert 'earnings_entries.at, when it was credited' in d['periods'] and 'the old year' in d['periods'] and 'do not move' in d['periods'], 'periods by entry time (SHOULD-1)'
assert 'netEarnings = GET /driver/earnings net for the same period' in d['money']['netEarnings'], 'net = earnings net'
assert 'never below 0' in d['money']['paidOutByMovera'] and 'payouts.paid_at' in d['money']['paidOutByMovera'] and 'Not derived from the entries' in d['money']['paidOutByMovera'], 'paid out (SHOULD-2)'
assert 'lineKind: trip' in d['addUp'] and 'payout (one paid payout' in d['addUp'], 'line kinds'
assert 'partial: true' in d['partial'] and d['texts']['partial'] == {'en': 'Only your zones', 'sv': 'Bara dina zoner', 'fr': 'Seulement vos zones'}, 'partial (SHOULD-4)'
assert 'Σ trip lines = the day, Σ days = the month, Σ months = the quarter, Σ quarters = the year' in d['addUp'], 'add up'
a = d['admin']
assert a['endpoint'].startswith('GET /admin/finance/driver-income (permission finance.read)'), 'admin endpoint'
assert '403 forbidden, reason zone_out_of_scope' in a['scope'] and a['maxTripLines'] == 10000, 'scope, max'
assert 'detail=trips needs month or payeeId: else 400 invalid_request, reason income_detail_too_big' in a['tooBig'], 'too big'
for r in ('income_year_invalid', 'income_month_invalid', 'unknown_country', 'income_detail_too_big'): assert r in a['errors'], r
assert 'a leading single quote' in a['csv'] and 'finance.driver_income.csv' in a['audit'] and 'finance.driver_income.read' in a['audit'], 'csv guard, audit'
assert a['panel'].startswith('Admin › Finance › Driver income (year), next to Payouts') and 'Months + days' in a['panel'] and 'All trips per day' in a['panel'], 'panel'
assert d['driver']['endpoint'].startswith('GET /driver/income-statement?year&detail=month|day|trips&month') and 'ownPartOnly true' in d['driver']['fleetDriver'], 'driver'
for k, v in d['texts'].items(): assert set(v) == {'en', 'sv', 'fr'} and all(v.values()), 'texts ' + k
assert 'rider app (no effect' in d['apps'], 'Rule 0 rider'
spec = yaml.safe_load(open('openapi.yaml'))
P, S = spec['paths'], spec['components']['schemas']
g = P['/admin/finance/driver-income']['get']
assert g['x-permission'] == 'finance.read' and g['responses']['200']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/DriverIncomePage'}, 'openapi admin'
assert [p for p in g['parameters'] if p.get('name') == 'year'][0]['required'] is True, 'year required'
cv = P['/admin/finance/driver-income.csv']['get']
assert cv['x-permission'] == 'finance.read' and 'text/csv' in cv['responses']['200']['content'], 'openapi csv'
dv = P['/driver/income-statement']['get']
assert dv['x-actor'] == ['driver'] and dv['responses']['200']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/DriverIncomeStatement'}, 'openapi driver'
assert set(S['DriverIncomeTotals']['required']) == set(FIELDS), 'totals fields'
assert S['DriverIncomeRow']['allOf'][1]['properties']['partial']['type'] == 'boolean' and S['DriverIncomeTripLine']['allOf'][1]['properties']['lineKind']['enum'] == ['trip', 'credit', 'payout'], 'openapi partial, lineKind'
for n in ('DriverIncomeRow', 'DriverIncomeQuarter', 'DriverIncomeMonth', 'DriverIncomeDay', 'DriverIncomeTripLine', 'DriverIncomePage', 'DriverIncomeStatement'): assert n in S, n
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.153 (P29 driver income year file, EU DAC7;' in t, 'CONTRACT.md note'
n153 = next(l for l in t.split('\n') if l.startswith('v0.18.153 (P29 driver income year file'))
assert 'follows v0.18.152)' in n153 and '`contract.json#driverIncomeYear`' in n153, 'CONTRACT.md note text'
assert t.count('- **Driver income (year)** (v0.18.153, `contract.json#driverIncomeYear`, DAC7)') == 1, 'KPIs line once'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
# launch restack (plan K): this version moves the v0.18.148 note (the draft moved v0.18.127)
n148 = next(l for l in cl if l.startswith('v0.18.148 (SOS by press time; Rules LAUN'))
assert '\n' + n148 not in t and cl.count(n148) == 1, 'v0.18.148 note moved once'
assert hashlib.sha256(n148.encode()).hexdigest() == '57f91cb534618f65d1bbd1a887564fc143ac948a20f3e9656672a71e221af336', 'v0.18.148 note moved word for word'
j = cl.index(n148)
assert cl[j - 2].startswith('v0.18.153 (P29 driver income year file; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '9c44e771ac2ef5a8f03583d5905298a271ad8809c9da6561da70499efaa4905d', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.148 and before (the v0.18.148 note moved in v0.18.153, the v0.18.146 note in v0.18.152, the v0.18.145' in t + ch, 'new pointer line (in CHANGELOG.md once a later version moves it)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.153 driver income year file ok')

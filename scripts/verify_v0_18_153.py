#!/usr/bin/env python3
"""v0.18.153 (P29 driver income year file, EU DAC7; owner 2026-11-21 "Don't only save ! Execute ! ..." + "Also another one
( yearly but with monthly details ) ...", Rules LAUNCH-RULE.md P29): contract.json#driverIncomeYear, the openapi copy
(part 1730: GET /admin/finance/driver-income, its .csv and GET /driver/income-statement), the CONTRACT.md note and KPIs
line, and the v0.18.127 note moved word for word to CHANGELOG.md (Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 153), 'version 0.18.153 or later'
keys = list(c)
assert keys.index('driverIncomeYear') == keys.index('kpis') + 1, 'driverIncomeYear right after kpis'
d = c['driverIncomeYear']
assert list(d) == ['note', 'why', 'payee', 'money', 'periods', 'addUp', 'admin', 'driver', 'texts', 'apps'], 'driverIncomeYear keys'
assert 'follows v0.18.132; 0.18.133-0.18.152 reserved for other drafts' in d['note'] and 'migration 0132' in d['note'] and 'no admin setting' in d['note'], 'note'
assert 'lag (2022:1681)' in d['why'] and 'never builds the tax office' in d['why'], 'why: DAC7, no XML'
assert 'kind company' in d['payee'] and 'kind driver' in d['payee'] and 'never the full account number' in d['payee'], 'payee'
FIELDS = ['rides', 'grossFares', 'tips', 'bonuses', 'adjustments', 'pickupPay', 'feeShare', 'moveraCommission', 'moveraFees', 'netEarnings', 'cashCollectedByDriver', 'paidOutByMovera']
assert list(d['money']) == ['note'] + FIELDS, 'money fields'
assert 'Never added across currencies' in d['money']['note'] and 'paid_to_movera' in d['money']['note'], 'money note'
assert 'pay in the car (cash) included' in d['money']['rides'] and '= GET /driver/earnings net' in d['money']['netEarnings'], 'cash rides, net = earnings net'
assert "trips.ended_at" in d['periods'] and 'belongs to the old year' in d['periods'], 'periods by trip end, zone-local'
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
for n in ('DriverIncomeRow', 'DriverIncomeQuarter', 'DriverIncomeMonth', 'DriverIncomeDay', 'DriverIncomeTripLine', 'DriverIncomePage', 'DriverIncomeStatement'): assert n in S, n
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.153 (P29 driver income year file, EU DAC7;' in t, 'CONTRACT.md note'
n153 = next(l for l in t.split('\n') if l.startswith('v0.18.153 (P29 driver income year file'))
assert 'follows v0.18.132; 0.18.133-0.18.152 reserved for other drafts' in n153 and '`contract.json#driverIncomeYear`' in n153, 'CONTRACT.md note text'
assert t.count('- **Driver income (year)** (v0.18.153, `contract.json#driverIncomeYear`, DAC7)') == 1, 'KPIs line once'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n127 = next(l for l in cl if l.startswith('v0.18.127 (S7 W2 Q119'))
assert '\n' + n127 not in t and hashlib.sha256(n127.encode()).hexdigest() == 'b51a0ff2ebb7016f49c9a557fb973e2a146ceaece339a99b3829d3760b5e644e', 'v0.18.127 note moved word for word'
assert cl.count(n127) == 1, 'v0.18.127 note once in CHANGELOG.md'
j = cl.index(n127)
assert cl[j - 2].startswith('v0.18.153 (P29 driver income year file; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '500ff2fd72593fe8c33c06d0cb1634754ea5da6aa47af9bb54ceee2fa8ded620', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.127 and before (the v0.18.127 note moved in v0.18.153, the v0.18.126 note in v0.18.132,' in t, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.153 driver income year file ok')

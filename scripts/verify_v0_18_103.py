#!/usr/bin/env python3
"""v0.18.103 (BQ-V44; owner G10-5 "Make bonuses real (Recommended)", Rules decisions/driver-g10.md:9; Q12 bonus zones,
decisions/admin-fake-by-group.md:40; plan Rules audits/impact/v44-driver-bonuses.md): bonus campaigns.
Run by scripts/verify.sh from the repository root. The money cases are replayed by reference_check.py
(fixtures/bonus_campaigns.json); this file checks the contract text, the API shape and the notes."""
import json
import yaml

c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 103), 'version 0.18.103 or later'
bc = c['bonusCampaigns']
# Owner rules with their citations.
own = ' '.join(bc['owner'])
for cite in ('decisions/driver-g10.md:9', 'decisions/admin-fake-by-group.md:40', 'decisions/admin-fake-by-group.md:11',
             'decisions/other-support-promos.md:11', 'decisions/driver-g3.md:32', 'decisions/session-2026-11-06.md:1263', 'decisions/driver-g10.md:3'):
    assert cite in own, 'owner citation ' + cite
assert 'Make bonuses real (Recommended)' in bc['note'] and 'not the trip bonus of adminDispatch.driverBonus' in bc['note'], 'note: campaigns, not the trip bonus'
assert 'separate from the operating zones' in bc['note'], 'note: own area (Q12)'
# Shape, measures, states.
assert bc['measures'] == ['trips', 'online_hours'], 'measures (owner: trips count or hours online)'
assert bc['states'] == ['scheduled', 'active', 'paused', 'ended'] and bc['statuses'] == ['active', 'paused', 'ended'], 'states'
L = bc['limits']
assert L['target']['trips'] == [1, 500] and L['target']['online_hours'] == [1, 200] and L['maxDays'] == 92, 'limits'
assert 'bonus_amount_above_max' in L['amount'] and 'CountryRules.bonusCampaignMax' in L['amount'], 'amount limit = the setting'
assert 'never an operating zone' in L['polygon'] and 'zones.polygon' in L['polygon'], 'area is its own shape'
assert 'day after endDate 00:00, local time of its zone' in bc['window'], 'window in zone time'
# Counting and award.
k = bc['counting']
assert k['gapMaxSeconds'] == 120 and k['accuracyMaxMeters'] == 50, 'online hours numbers'
assert 'PAID end' in k['trips'] and 'PICKUP point is inside the area' in k['trips'] and 'once per campaign' in k['trips'], 'trips rule'
assert 'online or on_trip' in k['onlineHours'] and 'adds 0' in k['onlineHours'] and 'twice or out of order adds nothing' in k['onlineHours'], 'hours rule'
assert 'fleetPayoutWhole' in k['who'], 'fleet: whole earnings to the fleet owner (driver-g10.md:3)'
a = bc['award']
assert 'SAME transaction' in a and 'ONE earnings entry { kind bonus, tripId null, bonusId' in a, 'award once'
# Supervisor must-fixes (Rules audits/impact/v44-driver-bonuses-supervisor.md §8).
assert 'AND earned_at IS NULL AND done ≥ target RETURNING' in a and 'ON CONFLICT (driver_id, bonus_id) WHERE bonus_id IS NOT NULL DO NOTHING' in a, 'MF1 gate + insert'
assert 'never makes the trip end or the location post fail' in a and 'locked in bonus_id order' in a and "SERVER's now" in a, 'MF1 no rollback, lock order, server time'
assert "status = 'active'" in k['sqlGuard'] and 'only a pre-filter' in k['sqlGuard'] and 'inside the window' in k['sqlGuard'], 'MF2'
oh = k['onlineHours']
assert 'drivers.online_since' in oh and "fix time ≤ the server's now" in oh and 'min(fix time − last counted fix time, receivedAt − last counted receivedAt)' in oh, 'MF3 online_since, server now, most a fix adds'
assert 'maxSpeedKmh' in oh and 'writeEverySeconds' in oh and k['maxSpeedKmh'] == 200 and k['writeEverySeconds'] == 30, 'MF3 jump + one write per 30 s'
assert "zones (Driver.zoneIds) include the campaign's zone" in k['who'], 'MF5'
assert 'EVERY point of it lies inside its zone' in L['polygon'] and 'D3 area lies inside the zone polygon' in bc['defaults'], 'MF6'
rl = k['riderLimit']
assert 'at most ONCE per driver, campaign and zone-local day' in rl and "the driver's own phone number never counts" in rl, 'MF7'
assert 'inside countDay' in bc['money']['kpi'] and "award's SERVER time" in bc['money']['kpi'], 'MF8'
sv = bc['server']
assert 'ADD COLUMN IF NOT EXISTS bonus_id text' in sv and 'NOT VALID' in sv and 'VALIDATE CONSTRAINT earnings_bonus_fk' in sv and 'no inline REFERENCES' in sv, 'MF9 FK NOT VALID + VALIDATE'
assert '-- undo:' in sv and 'migrations/undo/0110_bonus_campaigns.sql' in sv and 'indisvalid' in sv, 'MF9 undo form + valid index'
assert 'minutes' in bc['progressFormat'] and "'4 h 20 min'" in bc['progressFormat'] and set(bc['texts']['duration']) == {'sv', 'fr', 'en'}, 'hours text formats minutes'
assert 'h online' not in bc['texts']['progressHours']['sv'], 'progressHours no longer says {target} h'
assert 'nothing more counts for him in that campaign' in a and 'No push notice in this version' in a, 'award: stops counting, no push (D10)'
# Money: payout, Driver gets / Movera gets, KPI (M19), driver earnings.
m = bc['money']
assert 'Payout.lines bonus += amount' in m['payout'] and 'payoutHold' in m['payout'], 'payout line'
assert 'driverGets + amount; moveraGets − amount (both views)' in m['payoutSummary'], 'payout summary'
assert 'driverBonus + amount and moveraEarnings − amount, each once' in m['kpi'], 'KPI'
assert 'EarningsPeriod.bonus' in m['earnings'] and 'net includes it' in m['earnings'] and 'earnings.ts:39' in m['earnings'], 'driver earnings'
ps = c['priceDisplay']['payoutSummary']
cb = ps['campaignBonus']
assert cb.startswith('v0.18.103') and 'driverGets counts it once' in cb and 'moveraGets takes it off once, in BOTH views' in cb and 'below 0' in cb, 'campaignBonus'
assert 'session-2026-11-06.md:1263' in cb and 'frozenWhenPaid' in cb, 'campaignBonus: owner rule + frozen'
assert "kind = 'bonus' AND bonus_id IS NOT NULL" in cb and "never keys on 'no trip'" in cb and 'paid_to_movera' in cb, 'MF4'
assert ps['rule'].startswith('v0.18.92') and 'v0.18.97' in ps['rule'], 'payoutSummary.rule unchanged'
bo = c['moneyBase']['bonusOutsideCommission']
assert set(bo['which']) == {'lostDriver', 'afterPaidEnd'}, 'which unchanged'
assert bo['campaign'].startswith('v0.18.103') and "inside no trip's commission" in bo['campaign'] and 'taken off KPI moveraEarnings once' in bo['campaign'], 'M19 campaign'
mx = c['configDefaults']['bonusCampaignMax']
assert (mx['SE'], mx['FR'], mx['TN']) == ({'amountMinor': 200000, 'currency': 'SEK'}, {'amountMinor': 20000, 'currency': 'EUR'}, {'amountMinor': 200000, 'currency': 'TND'}), 'bonusCampaignMax defaults'
assert c['currencies']['TND']['exponent'] == 3, 'TND minor units (200000 = 200.000 DT)'
# Endpoints, permissions, audit, errors.
ep = bc['endpoints']
assert set(ep) == {'adminList', 'adminCreate', 'adminRead', 'adminUpdate', 'adminPause', 'adminDrivers', 'driverList', 'driverOpened'}, 'endpoints'
assert 'bonus_field_fixed' in ep['adminUpdate'] and 'LATER endDate' in ep['adminUpdate'] and 'never deleted (Rule 21)' in ep['adminPause'], 'edit and end rules'
assert 'drivers.bonuses' in c['adminPermissions']['values'] and 'drivers.read' in c['adminPermissions']['values'], 'permissions exist'
assert 'zone_out_of_scope' in bc['permissions'] and 'one admin is enough' in bc['permissions'], 'scope + one admin'
assert bc['auditActions'] == ['bonus.create', 'bonus.update', 'bonus.pause', 'bonus.resume', 'bonus.end'], 'audit actions'
assert bc['errors']['400'] == ['bonus_target_invalid', 'bonus_amount_invalid', 'bonus_amount_above_max', 'bonus_dates_invalid', 'bonus_area_invalid', 'bonus_field_fixed'], 'errors 400'
assert set(bc['errors']['409']) == {'bonus_ended', 'version_mismatch', 'invalid_transition'}, 'errors 409'
assert 'migration 0110' in bc['server'] and 'CONCURRENTLY' in bc['server'] and 'Rule 46' in bc['server'] and 'Rule 33' in bc['server'], 'server: migration + safety'
# Rule 0: all 5 parts named; rider not affected; demo kept (Rule 21).
ap = bc['apps']
assert 'DriversPage.tsx:48-50' in ap['admin'] and 'bonusCampaignMax' in ap['admin'] and 'demo-only (Rule 21)' in ap['admin'], 'admin part'
assert 'GET /driver/bonuses' in ap['driver'] and 'isNew' in ap['driver'] and 'PEAK80' in ap['driver'] and 'demo-only (Rule 21)' in ap['driver'], 'driver part'
assert ap['rider'].startswith('Not affected') and 'hideDriverMoney' in ap['rider'], 'rider not affected'
for d in ['D%d ' % n for n in range(1, 16)]:
    assert d in bc['defaults'], 'default listed ' + d
for key, t in bc['texts'].items():
    assert set(t) == {'sv', 'fr', 'en'} and all(t[l].strip() for l in t), 'texts sv/fr/en ' + key
assert '{done}' in bc['texts']['progressTrips']['sv'] and '{target}' in bc['texts']['progressHours']['fr'], 'placeholders'
# openapi.
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']
assert spec['info']['version'] == c['version'], 'openapi version'
want = {('/admin/bonuses', 'get'): 'drivers.read', ('/admin/bonuses', 'post'): 'drivers.bonuses', ('/admin/bonuses/{bonusId}', 'get'): 'drivers.read',
        ('/admin/bonuses/{bonusId}', 'put'): 'drivers.bonuses', ('/admin/bonuses/{bonusId}/pause', 'post'): 'drivers.bonuses',
        ('/admin/bonuses/{bonusId}/resume', 'post'): 'drivers.bonuses', ('/admin/bonuses/{bonusId}/end', 'post'): 'drivers.bonuses',
        ('/admin/bonuses/{bonusId}/drivers', 'get'): 'drivers.read'}
for (path, method), perm in want.items():
    o = P[path][method]
    assert o['x-permission'] == perm and o['x-actor'] == ['admin'], 'openapi ' + method + ' ' + path
    mutation = method != 'get'
    assert any(p.get('$ref') == '#/components/parameters/IdempotencyKey' for p in o['parameters']) == mutation, 'idempotency ' + path
assert P['/admin/bonuses']['post']['responses']['201']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/BonusCampaign'}, 'create 201'
assert P['/driver/bonuses']['get']['x-actor'] == ['driver'] and P['/driver/bonuses/opened']['post']['x-actor'] == ['driver'], 'driver ops'
assert '204' in P['/driver/bonuses/opened']['post']['responses'], 'opened 204'
assert S['BonusMeasure']['enum'] == bc['measures'] and S['BonusState']['enum'] == bc['states'], 'enums'
assert {'measure', 'target', 'amount', 'startDate', 'endDate', 'polygon', 'state', 'paidTotal'} <= set(S['BonusCampaign']['required']), 'BonusCampaign required'
assert S['BonusCampaignCreate']['additionalProperties'] is False and set(S['BonusCampaignCreate']['required']) == {'zoneId', 'names', 'measure', 'target', 'amount', 'startDate', 'endDate', 'polygon'}, 'create body'
assert set(S['BonusCampaignUpdate']['properties']) == {'expectedVersion', 'names', 'endDate'}, 'update: names and end date only (D8)'
assert 'paidTotal' not in S['DriverBonus']['properties'] and 'driversEarned' not in S['DriverBonus']['properties'] and 'isNew' in S['DriverBonus']['required'], 'driver view: no other drivers'
assert 'bonusCampaignMax' in S['CountryRules']['properties'] and 'bonusCampaignMax' not in S['CountryRules']['required'], 'setting additive'
assert 'bonus' in S['EarningsPeriod']['properties'] and 'bonus' not in S['EarningsPeriod']['required'], 'EarningsPeriod.bonus additive'
assert cb in S['PayoutSummary']['description'], 'openapi PayoutSummary campaignBonus'
for f in ('driverBonus', 'moveraEarnings'):
    assert bo['campaign'] in S['KpiDay']['properties'][f]['description'], 'openapi KpiDay ' + f
# Fixtures cover the money cases in SEK and TND (and EUR).
fx = json.load(open('fixtures/bonus_campaigns.json'))
cur = {x['zone']['currency'] for x in fx['validate']} | {x['currency'] for x in fx['payout']} | {x['campaign']['amount']['currency'] for x in fx['trips'] + fx['hours']}
assert {'SEK', 'EUR', 'TND'} <= cur, 'fixture currencies'
assert any(x['expect']['moveraGets']['driver']['amountMinor'] < 0 for x in fx['payout']), 'fixture: Movera gets below 0'
assert any(x['expect']['moveraGets']['admin'] != x['expect']['moveraGets']['driver'] for x in fx['payout']), 'fixture: admin and driver views differ'
assert any(e['kind'] == 'paid_to_movera' for x in fx['payout'] for e in x['entries'] if any(y.get('campaign') for y in x['entries'])), 'fixture MF4: campaign + paid_to_movera in one payout'
assert {'trips_sek_rider_limit_and_zone'} <= {x['id'] for x in fx['trips']} and {'hours_sek_abuse'} <= {x['id'] for x in fx['hours']}, 'fixtures MF3/MF5/MF7'
assert {'se_area_outside_zone', 'se_area_partly_outside_zone', 'se_area_on_zone_edge'} <= {x['id'] for x in fx['validate']}, 'fixtures MF6'
# CONTRACT.md: the note, size, the v0.18.71 note moved word for word (Rule 21).
t = open('CONTRACT.md', encoding='utf-8').read()
cl = open('CHANGELOG.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.103 (BQ-V44' in t and '**bonus campaigns**' in t, 'CONTRACT.md v0.18.103'
assert 'Driver gets + amount, Movera gets − amount in both views' in t and 'decisions/driver-g10.md:9' in t, 'CONTRACT.md money line'
assert '\nv0.18.71 (wording fix, live bug 2026-11-12' not in t and '\nv0.18.71 (wording fix, live bug 2026-11-12' in cl, 'v0.18.71 note moved to CHANGELOG.md'
assert 'Older version notes (v0.18.71 and before) are in `CHANGELOG.md`.' in t, 'pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert open('scripts/verify.sh', encoding='utf-8').read().count('\n') <= 1500, 'verify.sh over 1,500 lines'
print('v0.18.103 bonus campaigns ok')

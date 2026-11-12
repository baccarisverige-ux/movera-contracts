#!/usr/bin/env sh
# The contract's own checks: files match CHECKSUMS, the reference engine
# agrees with the fixtures, openapi.yaml parses, and (on a tag) the tag is
# the contract's version.
set -eu
cd "$(dirname "$0")/.."
sha256sum -c --quiet CHECKSUMS
listed=$(awk '{print $2}' CHECKSUMS | LC_ALL=C sort)
present=$(find CONTRACT.md contract.json openapi.yaml reference_check.py fixtures tools -type f ! -path '*/__pycache__/*' | LC_ALL=C sort)
[ "$listed" = "$present" ] || { echo "CHECKSUMS lists different files than the tree"; exit 1; }
python3 reference_check.py
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
assert spec['openapi'].startswith('3.'), 'openapi.yaml is not OpenAPI 3'
# v0.9.0: no operation lists the same parameter twice (name + in).
params = spec['components']['parameters']
for path, item in spec['paths'].items():
    for method, op in item.items():
        seen = set()
        for p in op.get('parameters', []):
            p = params[p['$ref'].split('/')[-1]] if '$ref' in p else p
            key = (p['name'], p['in'])
            assert key not in seen, f'{method} {path} lists {key} twice'
            seen.add(key)
print(f"contract.json version {c['version']}, openapi {spec['info'].get('version')}, {len(spec['paths'])} paths")
PY
# openapi.yaml must be exactly what the generator makes (no hand edits).
tmp=$(mktemp)
python3 tools/gen_openapi.py . "$tmp" >/dev/null
cmp -s "$tmp" openapi.yaml || { rm -f "$tmp"; echo "openapi.yaml is not what tools/gen_openapi.py generates; run it and commit the result"; exit 1; }
rm -f "$tmp"
# v0.18.59 §81/§82: TND with a dot; first language = phone language (owner 2026-11-10).
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
f = c['moneyDisplay']['formats']
assert (f['TND']['decimalSign'], f['TND']['decimals'], f['TND']['thousandsSeparator']) == ('.', 3, ' '), 'TND dot'
assert f['TND']['examples']['12350'] == '12.350 DT' and f['TND']['examples']['1250000'] == '1 250.000 DT', 'TND examples'
assert f['SEK']['decimalSign'] == ',' and f['EUR']['decimalSign'] == ',', 'SEK/EUR comma'
assert c['currencies']['TND']['exponent'] == f['TND']['decimals'], 'TND decimals = exponent'
fl = c['auth']['firstLanguage']
assert fl['fallback'] == 'en' and fl['supported'] == ['sv', 'fr', 'en'] and 'countryDefaultUnused' in fl, 'first language'
PY
# v0.18.60: the §76 masked-phone example follows its own rule (one dot per hidden digit, last 2 shown).
python3 - <<'PY'
import json, re
c = json.load(open('contract.json'))
ph = c['adminMasking']['shapes']['phone']
m = re.search(r'e\.g\. (\+46)(•+)(\d\d) for \+46(\d+)', ph)
assert m, 'masked phone example'
assert len(m.group(2)) == len(m.group(4)) - 2 and m.group(4).endswith(m.group(3)), 'masked phone example dot count'
md = open('CONTRACT.md', encoding='utf-8').read()
assert md.count('+46•••••••12') >= 2 and not re.search(r'\+46•{5}12', md), 'CONTRACT.md masked phone example'
PY
# v0.18.58 §80: counts-as-arrived distance per zone, larger at airports (owner 2026-11-10).
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
d = c['configDefaults']['earlyEnd']
assert (d['arrivedWithinMeters'], d['airportArrivedWithinMeters'], d['repriceOverKm'], d['repriceOverMin']) == (300, 1000, 2, 10), 'earlyEnd defaults'
p = spec['components']['schemas']['EarlyEndSettings']['properties']
assert (p['arrivedWithinMeters']['minimum'], p['arrivedWithinMeters']['maximum'], p['arrivedWithinMeters']['default']) == (50, 2000, 300), 'arrivedWithinMeters'
assert (p['airportArrivedWithinMeters']['minimum'], p['airportArrivedWithinMeters']['maximum'], p['airportArrivedWithinMeters']['default']) == (100, 3000, 1000), 'airportArrivedWithinMeters'
assert 'invalid_arrived_distance' in p['arrivedWithinMeters']['description'] and 'kind airport' in p['airportArrivedWithinMeters']['description'], 'reason + airport rule'
cp = spec['components']['schemas']['CompletePreview']['properties']
assert 'arrivedLimitMeters' in cp and 'distanceToDropoffMeters' in cp, 'CompletePreview limit fields'
for t in c['arrivedDistance']['texts'].values():
    assert set(t) == {'sv', 'fr', 'en'} and all(t.values()), 'texts sv/fr/en'
PY
# v0.18.57 §79: emergency numbers per country from admin (owner 2026-11-10).
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
d = c['configDefaults']['emergencyNumbers']
assert [(x['kind'], x['number']) for x in d['SE']] == [('general', '112')], 'SE default 112'
assert [(x['kind'], x['number']) for x in d['FR']] == [('general', '112')], 'FR default 112'
assert [(x['kind'], x['number']) for x in d['TN']] == [('police', '197'), ('ambulance', '190')], 'TN defaults 197 / 190'
assert set(d) == set(c['supportDesk']['settings']['countries']), 'a default for every country'
for k, rows in d.items():
    for x in rows:
        assert set(x['label']) == {'sv', 'fr', 'en'} and all(x['label'].values()), f'{k} label sv/fr/en'
cs = spec['components']['schemas']
assert cs['EmergencyNumber']['properties']['kind']['enum'] == ['police', 'ambulance', 'fire', 'general'], 'EmergencyNumber.kind'
for n in ('CountryRules', 'RiderAppConfig', 'DriverAppConfig'):
    assert cs[n]['properties']['emergencyNumbers']['items'] == {'$ref': '#/components/schemas/EmergencyNumber'}, f'{n}.emergencyNumbers'
assert 'emergency_numbers_country_only' in cs['CountryRules']['properties']['emergencyNumbers']['description'], 'country only'
for t in c['emergencyNumbers']['texts'].values():
    assert set(t) == {'sv', 'fr', 'en'} and all(t.values()), 'texts sv/fr/en'
PY
# v0.18.56 §78: G9 part 2 chat & calls (owner Q79–Q85, 2026-11-10): settings with defaults, new routes, texts in sv/fr/en.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
d = c['configDefaults']['chat']
assert (d['keepDays'], d['maxLength'], d['spamPerMin'], d['sound'], d['sheetAutoOpen'], d['readAloudDefault'], d['translation']) == (90, 2000, 10, True, 'new_message', False, True), 'chat defaults'
assert d['autoArrived']['on'] is True and all(len(d['quickReplies'][k]) <= 8 for k in ('driver', 'rider')), 'quick replies / autoArrived defaults'
cs = spec['components']['schemas']
assert cs['CountryRules']['properties']['chat'] == {'$ref': '#/components/schemas/ChatSettings'}, 'CountryRules.chat'
for k, v in cs['ChatSettings']['properties'].items():
    assert 'default' in v, f'ChatSettings.{k} has a default (rule 16)'
for path, m, perm in (('/admin/chats', 'get', 'support.reply'), ('/admin/drivers/{driverId}/message', 'post', 'support.reply'),
                      ('/admin/riders/{riderId}/message', 'post', 'support.reply'), ('/trips/{tripId}/messages/options', 'get', None),
                      ('/trips/{tripId}/messages/translate', 'post', None)):
    o = spec['paths'][path][m]
    assert o.get('x-permission') == perm, f'{m} {path} x-permission {perm}'
for _p in ('/admin/chats', '/admin/drivers/{driverId}/message', '/admin/riders/{riderId}/message'):
    assert 'zone_out_of_scope' in str(spec['paths'][_p]), f'{_p} names zone_out_of_scope'
assert cs['Message']['properties']['auto']['enum'] == ['arrived', 'on_my_way'], 'Message.auto'
assert 'coming_soon' in spec['paths']['/trips/{tripId}/messages/translate']['post']['description'], 'translate 503 coming_soon'
assert 'once per trip' in spec['paths']['/trips/{tripId}/arrive']['post']['description'], 'auto arrived once per trip'
assert c['inAppCalls']['turnEnv']['names'] == ['MOVERA_STUN_URLS', 'MOVERA_TURN_URLS', 'MOVERA_TURN_SECRET'], 'TURN names'
def langs(x, at):
    if isinstance(x, dict):
        if set(x) & {'sv', 'fr', 'en'}:
            assert set(x) == {'sv', 'fr', 'en'} and all(x.values()), f'{at} sv/fr/en'
        for k, v in x.items(): langs(v, at + '.' + k)
    elif isinstance(x, list):
        for n, v in enumerate(x): langs(v, f'{at}[{n}]')
for k in ('quickReplies', 'autoArrived'): langs(d[k], 'configDefaults.chat.' + k)
for k in ('header', 'translate'): langs(c['chat'][k], 'chat.' + k)
for k in ('push', 'background'): langs(c['inAppCalls'][k], 'inAppCalls.' + k)
PY
# v0.18.64 §85: chat messages arrive translated (owner 2026-11-11); setting default on, Message.lang, auto flag, cache.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
assert c['configDefaults']['chat']['autoTranslate'] is True, 'configDefaults.chat.autoTranslate default true'
at = c['chat']['autoTranslate']
for k in ('rule', 'when', 'sourceLanguage', 'request', 'sameLanguage', 'cache', 'failure', 'admin'):
    assert at.get(k), f'chat.autoTranslate.{k}'
for k, v in at['texts'].items():
    assert set(v) == {'sv', 'fr', 'en'} and all(v.values()), f'chat.autoTranslate.texts.{k} sv/fr/en'
sc = spec['components']['schemas']
assert sc['ChatSettings']['properties']['autoTranslate']['default'] is True, 'ChatSettings.autoTranslate default'
assert 'autoTranslate' in sc['ChatOptions']['properties'], 'ChatOptions.autoTranslate'
assert sc['Message']['properties']['lang']['enum'] == ['sv', 'fr', 'en'], 'Message.lang'
assert sc['TranslateMessageRequest']['properties']['auto']['type'] == 'boolean', 'TranslateMessageRequest.auto'
d = spec['paths']['/trips/{tripId}/messages/translate']['post']['description']
for w in ('auto_translate_off', 'See original', '0097'):
    assert w in d, f'translateTripMessage names {w}'
PY
# v0.18.62 §84: POST /admin/auth/sign-in-locks/unlock as the server answers: settings.edit, 200 { phone, lifted }, no 404.
python3 - <<'PY'
import yaml
spec = yaml.safe_load(open('openapi.yaml'))
o = spec['paths']['/admin/auth/sign-in-locks/unlock']['post']
assert o.get('x-permission') == 'settings.edit', 'unlockSignIn x-permission settings.edit'
r = o['responses']
assert r['200']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/SignInUnlockResult'}, 'unlockSignIn 200 body'
assert '404' not in r and '204' not in r, 'unlockSignIn: no 404/204'
sc = spec['components']['schemas']['SignInUnlockResult']
assert sc['required'] == ['phone', 'lifted'] and sc['properties']['lifted']['type'] == 'integer', 'SignInUnlockResult shape'
for w in ('invalid_phone', 'invalid_body', 'missing_permission'):
    assert w in o['description'], f'unlockSignIn names {w}'
PY
# v0.18.61 §83: GET /payments/{paymentId}: admin needs finance.read (owner 2026-11-11 "Finance permission"); cash-only typed 400.
python3 - <<'PY'
import yaml
spec = yaml.safe_load(open('openapi.yaml'))
o = spec['paths']['/payments/{paymentId}']['get']
assert o.get('x-permission') == spec['paths']['/admin/payments']['get']['x-permission'] == 'finance.read', 'getPayment x-permission finance.read'
for w in ('payment_method_not_available', 'missing_permission', 'zone_out_of_scope', 'own payment'):
    assert w in o['description'], f'getPayment names {w}'
PY
# v0.18.55 §77: admin reads of a trip and its events need trips.read + the trip's zone (owner Q34, 2026-11-10).
python3 - <<'PY'
import yaml
spec = yaml.safe_load(open('openapi.yaml'))
for p in ('/trips/{tripId}', '/trips/{tripId}/events'):
    o = spec['paths'][p]['get']
    assert o.get('x-permission') == 'trips.read', f'{p} x-permission trips.read'
    assert 'zone_out_of_scope' in o['description'] and 'missing_permission' in o['description'], f'{p} names the 403 reasons'
PY
# v0.18.52 §74: restored trip never offline on a trip; offline fixes not stored (owner Q14 + Q15, 2026-11-09).
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
o = c['driverHome']['offlineLocation']
assert set(o) == {'note', 'app', 'server', 'appsNoChange'}, 'offlineLocation index'
assert 'never go offline' in o['note'] and 'Not stored' in o['note'], 'owner words'
assert o['server']['accepted'] == 0 and 'no active trip' in o['server']['rule'] and 'always stored' in o['server']['rule'], 'server rule'
assert 'stops the location sender' in o['app']['rule'], 'app rule'
assert 'stops when a trip restored after a restart ends' in c['driverHome']['backgroundLocation']['note'], 'backgroundLocation note'
spec = yaml.safe_load(open('openapi.yaml'))
assert 'accepted 0' in spec['paths']['/driver/location']['post']['description'], 'openapi /driver/location names the not-stored rule'
PY
# v0.18.51 §73: booked waiting from the later of arrival and pickup time, booked fees, L6 row, riderTripPush bell.
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
b = c['bookedRide0_18_51']
assert set(b) == {'note', 'waitFrom', 'beforePickup', 'noShow', 'fees', 'texts', 'l6', 'riderTripPushBell', 'driverReservationsLive', 'apps'}, 'bookedRide index'
assert 'the later of' in b['waitFrom']['rule'] and 'Replaces Owner B' in b['waitFrom']['rule'], 'waitFrom rule (owner: later of Arrived and pickup time)'
assert 'no admin switch' in b['waitFrom']['fixed'], 'owner: fixed rule'
for k, t in b['texts'].items():
    assert set(t) == {'sv', 'fr', 'en'} and all(v.strip() for v in t.values()), f'texts {k} sv/fr/en'
assert b['texts']['beforePickup']['en'] == 'Before the pickup time', 'beforePickup text'
lf = c['bookLater']['liveFixes']
assert 'also when the driver arrives late)' not in lf['includedWaiting'] and 'waitFrom' in lf['includedWaiting'], 'Owner B late rule replaced'
assert 'counted from the pickup time;' not in lf['includedWaitingPolicy'], 'policy text follows waitFrom'
assert c['bookLater']['texts']['includedWaiting']['en'] != '{minutes} min free waiting count from the pickup time', 'rider included waiting text'
f = c['pickupWaiting']['terms']['fields']
assert 'later of arrival and pickup time' in f['noShowAfterMin'] and 'later of arrival and pickup time' in f['freeWaitMin'], 'terms fields for reservations'
assert 'never the no-show fee' in c['pickupWaiting']['cancelAfterArrived']['note'], 'cancelAfterArrived excludes booked rides'
tr = c['transitions']
ra = [(t['from'], t['to'], t.get('when')) for t in tr if t['command'] == 'reassign' and t['actor'] == 'admin']
assert ra == [(['accepted'], 'searching', 'live'), (['accepted'], 'requested', 'scheduled'), (['offered', 'driver_to_pickup', 'arrived'], 'searching', None)], 'L6 rows'
# No two transition rows match the same (status, command, actor, kind) (the server's own table test).
seen = {}
for i, t in enumerate(tr):
    for s in t['from']:
        for k in ([t['when']] if 'when' in t else ['live', 'scheduled']):
            key = (s, t['command'], t['actor'], k)
            assert key not in seen, f'transition rows {seen[key]} and {i} both match {key}'
            seen[key] = i
assert 'bell false' not in c['riderTripPush']['note'] and 'bell true' in c['riderTripPush']['note'], 'riderTripPush bell true'
assert c['driverReservationsLive']['when'].startswith('Sent to every driver stream of the zone when a trip with scheduledAt in that zone changes (created, accepted, released, cancelled, rescheduled, started)'), 'driverReservationsLive.when unchanged'
# The cases (fixtures/booked_waiting.json) against this oracle.
fx = json.load(open('fixtures/booked_waiting.json'))
bad = 0
for k in fx['waitFrom']:
    wf = k['arrivedAtMin'] if k['kind'] == 'live' else max(k['arrivedAtMin'], 0)
    got = {'waitFromMin': wf, 'freeUntilMin': wf + k['freeWaitMin'], 'noShowAtMin': wf + k['noShowAfterMin']}
    if got != k['expect']: bad += 1; print('WAIT FROM', k['id'], got)
    for ch in k['checks']:
        g = {'chargedSeconds': max(0, ch['atMin'] - got['freeUntilMin']) * 60, 'noShowAllowed': ch['atMin'] >= got['noShowAtMin']}
        if g != {x: ch[x] for x in g}: bad += 1; print('WAIT FROM check', k['id'], ch, g)
def rfee(rule, fare, before):
    if rule is None or before >= rule['freeMin']: return 0
    fee = rule['value'] if rule['type'] == 'fixed' else (fare * rule['value'] * 2 + 100) // 200
    if rule['min']: fee = max(fee, rule['min']['amountMinor'])
    if rule['max']: fee = min(fee, rule['max']['amountMinor'])
    return fee
for k in fx['fees']:
    rule = k['cancelRule']
    if k['kind'] == 'scheduled':
        before = k['minutesBeforePickup'] if k['event'] == 'rider_cancel_arrived' else (rule['freeMin'] - 1 if rule else 0)
        fee = rfee(rule, 30000, before); kind = 'cancel' if k['event'] == 'rider_cancel_arrived' else 'no_show'
        if rule is None and k['event'] == 'no_show': fee = k['noShowFee']  # owner Q2: no booked rule = normal no-show fee
    elif k['event'] == 'no_show' or (k['switch'] and k['pastFreeWait']):
        fee = k['noShowFee']; kind = 'no_show'
    else:
        fee = 0 if k['minutesSinceAccept'] < rule['freeMin'] else rule['value']; kind = 'cancel'
    got = {'fee': fee or None, 'feeKind': kind if fee else None}
    if got != k['expect']: bad += 1; print('BOOKED FEES', k['id'], got)
assert not bad, f'{bad} booked waiting / fee case mismatches'
PY
# v0.18.50 §72: trip lifecycle decisions L1, L4–L7, L9–L12.
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
d = c['driverTripPush']
assert d['kind'] == 'driver_trip_update' and d['bell'] is True and d['deepLink'] == 'movera-driver://trips/{tripId}', 'L1 driverTripPush'
assert d['moments'] == ['rider_cancelled', 'rider_ended_early', 'admin_cancelled', 'admin_reassigned', 'admin_no_show'], 'L1 moments'
assert d['title']['fr'] == 'Course annulée', 'L1 title fr (owner « Course annulée »)'
for m in d['moments'] + ['fee']:
    assert set(d['texts'][m]) == {'sv', 'fr', 'en'}, f'L1 texts {m}'
assert '{amount}' in d['texts']['fee']['fr'], 'L1 fee line'
rp = c['riderTripPush']
assert rp['moments'][-2:] == ['no_driver_found', 'trip_failed'], 'L11 moments'
assert rp['texts']['no_driver_found']['title']['fr'] == 'Aucun chauffeur disponible pour le moment', 'L11 no driver fr'
assert rp['texts']['trip_failed']['title']['fr'] == 'Un problème est survenu, votre course n’a pas pu être réservée', 'L11 failed fr'
assert {'rater': 'driver', 'status': 'cancelled_by_rider', 'command': 'end_early'}.items() <= [r for r in c['ratingAllowed']['rules'] if r['rater'] == 'driver' and r['status'] == 'cancelled_by_rider'][0].items(), 'L5 driver rates end_early'
assert [r for r in c['transitions'] if r['command'] == 'release' and r['actor'] == 'system' and r.get('when') == 'live' and r['to'] == 'searching'], 'L12 transition'
assert 'Access-Control-Expose-Headers' in c['headers']['Date'], 'L9 Date header'
assert 'driver_cancelled' in c['realtime']['kinds'], 'L7 kind listed'
lc = c['lifecycle0_18_50']
assert set(lc) == {'note', 'l1', 'l4', 'l5', 'l6', 'l7', 'l9', 'l10', 'l11', 'l12'}, 'lifecycle index'
assert 'driverNextTrip' in lc['l4']['rule'] and 'reservation_unassigned' in lc['l6']['rule'] and 'driver_cancelled' in lc['l7']['rule'], 'L4/L6/L7 rules'
assert lc['l10']['texts']['youPay']['fr'] == 'Vous payez {amount}.', 'L10 text'
assert 'rule' not in lc['l10']['texts'] and 'ONLY' in lc['l10']['rule'], 'L10 (owner): only the amount, no explanation line'
sc = json.load(open('fixtures/scenarios.json'))['scenarios']
assert [x for x in sc if x['id'] == 'rider_rates_trip_ended_early'][0]['rating'] == {'rider': 'allowed', 'driver': 'allowed'}, 'L5 scenario'
PY
# v0.18.49 §71: owner decisions Q6–Q13 (old texts and links gone, new ones present).
python3 - <<'PY'
import json, re, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
def strs(o):
    if isinstance(o, dict):
        for v in o.values(): yield from strs(v)
    elif isinstance(o, list):
        for v in o: yield from strs(v)
    elif isinstance(o, str): yield o
def frs(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'fr' and isinstance(v, str): yield v
            else: yield from frs(v)
    elif isinstance(o, list):
        for v in o: yield from frs(v)
# Q9: one spelling, trips/{tripId}.
assert not [x for x in strs(c) if re.search(r'://trip/', x)], 'Q9: a contract link still says trip/ (use trips/{tripId})'
assert c['onTrip']['rideCheck']['push']['deepLink'] == {'rider': 'movera-rider://trips/{tripId}', 'driver': 'movera-driver://trips/{tripId}'}, 'Q9 rideCheck links'
assert c['pickupWaiting']['headingCheck']['notHeadingNotice']['deepLink'] == 'movera-driver://trips/{tripId}', 'Q9 heading notice link'
assert c['riderTripPush']['deepLink'] == 'movera://trips/{tripId}', 'Q9 riderTripPush link'
assert 'movera-rider://trips/{tripId}/receipt' in c['finish']['receipt']['resend'], 'Q9 receipt resend link'
# Q11: « Course programmée », no « réservée » left in contract French.
assert not [x for x in strs(c) if re.search(r'(?i)courses? réservées?', x)], 'Q11: « Course réservée » still in the contract (owner: « Course programmée »)'
assert c['arrivedWaiting']['rules']['texts']['scheduled']['fr'] == 'Course programmée', 'Q11 scheduled fr'
assert c['bookLater']['texts']['badge']['fr'] == 'Course programmée · {time}', 'Q11 badge fr'
# Q12: rider pushes « Votre chauffeur … ».
t = c['riderTripPush']['texts']
assert t['driver_arrived']['title']['fr'] == 'Votre chauffeur est arrivé', 'Q12 driver_arrived fr'
assert t['driver_arriving']['title']['fr'] == 'Votre chauffeur arrive bientôt', 'Q12 driver_arriving fr'
assert not [x for x in frs(c) if x in ('Le chauffeur est arrivé', 'Le chauffeur arrive')], 'Q12: old rider push titles still in the contract'
assert t['driver_arriving']['body']['fr'] == 'Préparez-vous à le rejoindre.', 'Q12 driver_arriving body fr'
assert not [x for x in frs(c) if 'dans la voiture' in x], 'Q13: « à bord » everywhere, no « dans la voiture » in contract French'
assert c['finish']['receipt']['texts']['paidInCar']['fr'] == 'Payé à bord', 'Q13 receipt line'
# Q13: « Payer à bord ».
pm = c['finish']['paymentMethods']['texts']
assert pm['cash'] == {'sv': 'Betala i bilen', 'fr': 'Payer à bord', 'en': 'Pay in car'}, 'Q13 cash label'
assert pm['payment_method_coming_soon']['fr'].endswith('Choisissez Payer à bord.'), 'Q13 coming soon names the cash label'
assert not [x for x in strs(c) if re.search(r'Payer en espèces à bord|Payer dans la voiture', x)], 'Q13: an old cash label is still in the contract'
# Q6: lost refresh answer accepted once.
tk = c['auth']['tokens']
assert tk['refreshRetryWindowSeconds'] == 60 and 'ONCE' in tk['refreshRetry'] and 'refresh_token_reused' in tk['refreshRetry'], 'Q6 refreshRetry'
assert 'late_retry_at' in tk['lostAnswer']['once'] and tk['lostAnswer']['rule33'], 'Q6 lostAnswer'
assert 'v0.18.49' in spec['paths']['/auth/refresh']['post']['description'], 'Q6 openapi refresh'
# Q8: driver sign-out refused during a trip.
so = c['auth']['signOutOnTrip']
assert (so['status'], so['code'], so['reason'], so['actors']) == (409, 'conflict', 'sign_out_on_trip', ['driver']), 'Q8 signOutOnTrip'
assert so['texts']['finishTripFirst'] == {'sv': 'Avsluta resan först.', 'fr': 'Terminez d’abord la course.', 'en': 'Finish the trip first.'}, 'Q8 texts'
assert so['code'] in c['errors']['codes'] and 'sign_out_on_trip' in c['errors']['reason'], 'Q8 error reason listed'
assert '409' in spec['paths']['/auth/sign-out']['post']['responses'], 'Q8 openapi 409 on sign-out'
# Q10: booked cancel by the category rule only.
assert 'no longer makes a cancel free' in c['bookLater']['rider']['cancel'] and 'freeMin' in c['bookLater']['rider']['cancel'], 'Q10 bookLater.rider.cancel'
assert 'freeMin' in c['afterTestRules']['bookedCancel']['rule'] and 'does not decide' in c['afterTestRules']['bookedCancel']['rule'], 'Q10 bookedCancel.rule'
assert c['afterTestRules']['bookedCancel']['graceAfterBookingMin'] == 5 and 'graceAfterBookingMin' in c['bookLater']['rider']['cancel'], 'Q10 update: 5 min free cancel after booking'
bl = json.load(open('fixtures/book_later.json'))
assert all('freeMin' in x and x['expect'] in ('free', 'fee') for x in bl['riderCancel']), 'Q10 riderCancel fixture'
assert {'id': 'q10_change_window_no_longer_free', 'minutesBefore': 90, 'freeChangeBeforeMin': 60, 'freeMin': 120, 'expect': 'fee'} in bl['riderCancel'], 'Q10 B6 case'
assert set(c['ownerDecisions0_18_49']) == {'note', 'q6', 'q8', 'q9', 'q10', 'q11', 'q12', 'q13'}, 'ownerDecisions0_18_49 index'
PY
# v0.18.48 §70: owner French wording (fr only).
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
assert c['statusWords']['families']['tripStatus']['no_show']['fr'] == 'Absence du passager', 'no_show fr'
assert c['pickupWaiting']['terms']['texts']['pickupMove']['fr'] == 'Vous pouvez déplacer le lieu de prise en charge de {meters} m au plus après la réservation', 'terms.pickupMove fr'
assert c['arrivedWaiting']['pin']['texts']['driverWrong']['fr'] == 'Code incorrect. Il vous reste {left} tentatives.', 'pin.driverWrong fr'
assert c['statusWords']['families']['tripStatus']['approaching_dropoff']['fr'] == 'Approche de la destination', 'approaching_dropoff fr'
assert c['finish']['driverMoney']['texts']['pickup_pay']['fr'] == 'Rémunération d’approche', 'pickup_pay fr'
assert c['auth']['signedOut']['texts']['expired']['fr'] == c['auth']['signedOut']['texts']['revoked']['fr'] == 'Vous avez été déconnecté de votre compte. Reconnectez-vous.', 'signedOut fr'
def frs(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'fr' and isinstance(v, str): yield v
            else: yield from frs(v)
    elif isinstance(o, list):
        for v in o: yield from frs(v)
old = ['Marquer comme client absent ? Vous recevez {amount}', 'Frais de client absent {amount}', 'Trop d’essais. Réessayez dans {min} min', 'Ouvrir les réglages', 'Annuler le client absent', 'Mise en ligne', 'Approche de la dépose', 'Le point de départ a été déplacé', 'Vous avez été déconnecté – reconnectez-vous']
left = [v for v in frs(c) if v in old]
assert not left, f'old French texts still in the contract: {left}'
for _p in (('legal', 'defaults', 'SE', 'terms', 'text'), ('legal', 'defaults', 'FR', 'terms', 'text'), ('pickupWaiting', 'servedConfig', 'cancelAfterArrivedIsNoShow', 'adminText'), ('arrivedWaiting', 'termsTexts', 'lines', 'category'), ('arrivedWaiting', 'termsTexts', 'lines', 'rule')):
    _t = c
    for _k in _p: _t = _t[_k]
    assert 'client absent' not in _t['fr'].lower() and 'absence du passager' in _t['fr'].lower(), f'{_p} fr still says client absent'
assert c['arrivedWaiting']['reverseNoShow']['texts']['done']['fr'] == 'Absence du passager annulée', 'reverseNoShow.done fr'
assert 'frais de non-présentation du passager' in c['pickupWaiting']['servedConfig']['cancelAfterArrivedIsNoShow']['adminText']['fr'], 'adminText fee wording'
assert not [x for x in frs(c) if 'frais d’absence' in x], 'owner fee wording is « frais de non-présentation du passager »'
import re
assert not [x for x in frs(c) if re.search('(?i)client absent', x)], 'a contract French text still says « client absent » (owner: « absence du passager »)'
PY
# v0.18.47 §69: admin stream replay limit (no cursor = from now; > replayMax unseen = one resync).
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
a = c['adminLiveEvents']
assert a['replayMax'] == 500, 'adminLiveEvents.replayMax'
assert 'FROM NOW' in a['replay'] and 'replayMax' in a['replay'], 'adminLiveEvents.replay names the no-cursor and replayMax rules'
assert 'replayMax' in a['types']['resync']['when'], 'resync.when names replayMax'
assert a['rule33'], 'adminLiveEvents.rule33'
PY
# v0.18.45 §68: the driver config stream lists driver_reservations_changed; §67 note says "renumbered from 0.18.42".
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
assert c['driverReservationsLive']['kind'] == 'driver_reservations_changed', 'driverReservationsLive.kind'
assert c['driverReservationsLive']['stream'] == 'GET /driver/config/stream', 'driverReservationsLive.stream'
assert 'driver_reservations_changed' in spec['paths']['/driver/config/stream']['get'].get('description', ''), 'driver stream kinds miss driver_reservations_changed'
assert spec['components']['schemas']['DriverReservationsChangedEvent']['properties']['kind']['const'] == 'driver_reservations_changed'
assert 'renumbered from 0.18.42' in c['sameAddress']['note'] and 'renumbered from 0.18.44' not in c['sameAddress']['note'], 'sameAddress.note typo (C10)'
PY
# CONTRACT.md's title names the same version as contract.json.
v=$(python3 -c "import json;print(json.load(open('contract.json'))['version'])")
head -1 CONTRACT.md | grep -q "v$v\b" || { echo "CONTRACT.md title does not name v$v"; exit 1; }
tag="${GITHUB_REF_NAME:-}"
case "$tag" in
  v*) v=$(python3 -c "import json;print(json.load(open('contract.json'))['version'])")
      [ "$tag" = "v$v" ] || { echo "tag $tag does not match contract.json version $v"; exit 1; } ;;
esac
# Step 21 (2026-11-09): the version must be higher than every released tag (0.18.10 > 0.18.9); a tag push of the same version passes;
# a change that leaves the contract files untouched (CHECKSUMS = the tag's; README, workflows) may keep the released number (2026-11-10).
python3 scripts/check_version_order.py --self-test
python3 scripts/size_ratchet.py --self-test
python3 scripts/check_version_order.py
# v0.18.65 §86: the trip radar's "stop next trips" reaches the server (owner phone test 2026-11-11).
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
nt = c['nextTripsSwitch']
assert 'migration 0098' in nt['note'] and 'next_trips_off' in nt['noOffers'], 'nextTripsSwitch'
spec = yaml.safe_load(open('openapi.yaml'))
op = spec['paths']['/driver/next-trips']['post']
assert op['requestBody']['content']['application/json']['schema']['$ref'].endswith('/NextTripsRequest'), 'next-trips body'
S = spec['components']['schemas']
assert S['NextTripsRequest']['required'] == ['on'] and S['Driver']['properties']['nextTripsOff']['default'] is False, 'nextTripsOff'
assert 'nextTripsOff' in S['LiveDriver']['properties'], 'LiveDriver.nextTripsOff'
PY
# v0.18.66 §87: call connect timeout setting, failure hint, notice language TN fr, admin chat translations (owner 2026-11-11).
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert c['configDefaults']['calls']['connectTimeoutSeconds'] == 25 and c['inAppCalls']['settings']['ranges']['connectTimeoutSeconds'] == [10, 60], 'connectTimeoutSeconds default 25, 10-60'
ct = S['CountryRules']['properties']['calls']['properties']['connectTimeoutSeconds']
assert (ct['minimum'], ct['maximum'], ct['default']) == (10, 60, 25), 'CountryRules.calls.connectTimeoutSeconds'
for n in ('TripCall', 'CallView'):
    assert S[n]['properties']['connectTimeoutSeconds']['default'] == 25, f'{n}.connectTimeoutSeconds'
h = c['inAppCalls']['texts']['connectFailedHint']
assert set(h) == {'sv', 'fr', 'en'} and all(h.values()) and h['en'] == "Couldn't connect. Check your network or use chat.", 'connectFailedHint sv/fr/en'
assert 'Tablet ON, phone OFF' in c['callConnect']['speakerDefault']['owner'] and '600 dp' in c['callConnect']['speakerDefault']['rule'], 'speaker default'
cl = c['configDefaults']['countries']
assert (cl['SE']['defaultLanguage'], cl['FR']['defaultLanguage'], cl['TN']['defaultLanguage']) == ('sv', 'fr', 'fr'), 'country languages'
assert 'TN fr' in c['noticeLanguage']['rule'] and 'else en' in c['noticeLanguage']['rule'], 'noticeLanguage TN fr'
mt = S['Message']['properties']['translations']
assert mt['items'] == {'$ref': '#/components/schemas/MessageTranslation'} and S['MessageTranslation']['required'] == ['to', 'text'], 'Message.translations'
assert 'never asks the provider' in c['chat']['autoTranslate']['adminView'], 'admin view read-only'
PY
# v0.18.67: §86 next-trips end wording (server #187) + migration lock timeout (server #189), wording only.
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
e = c['nextTripsSwitch']['end']
assert 'the trip he is DRIVING ends' in e and 'keeps it' in e and 'begins with the radar on' in e, 'nextTripsSwitch.end wording'
bp = c['fastDispatch']['backPressure']
assert 'DATABASE_STATEMENT_TIMEOUT_MS' in bp and 'DATABASE_MIGRATION_LOCK_TIMEOUT_MS instead (default 5000 ms, 0 = none)' in bp and 'VALIDATE CONSTRAINT' in bp, 'backPressure migration lock timeout'
PY
python3 - <<'PYEOF' || exit 1
import json, sys
c = json.load(open("contract.json"))
r = c["alertDesk"]["serverDetection"]["kindDefaults"]["system_health"]["rule"]
if "one alert per parked job kind" not in r or "runs once more 60 s" not in r: sys.exit("v0.18.67: system_health rule (B1.6b) missing")
PYEOF
# v0.18.68: stream close on failed reads (server B1.9) + housekeeping timer lane (server B1.7, G11), wording only.
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
sc = c['realtime']['streamClose']
assert 'STREAM_READ_RETRIES (default 3)' in sc and 'STREAM_CLOSE_SPREAD_MS (default 30 s)' in sc and ': stream read failed; reconnect to catch up' in sc and 'Last-Event-ID / after' in sc and 'stayed up ≥ 30 s' in sc, 'realtime.streamClose wording'
t = c['fastDispatch']['timers']
assert 'HOUSEKEEPING_LANES, default 1' in t and 'general lanes never take them' in t and 'never wait behind a clean-up' in t, 'fastDispatch.timers housekeeping lane'
md = open('CONTRACT.md').read()
assert 'STREAM_READ_RETRIES' in md and ': stream read failed; reconnect to catch up' in md and 'HOUSEKEEPING_LANES' in md, 'CONTRACT.md v0.18.68 wording'
PY
echo "contract ok"

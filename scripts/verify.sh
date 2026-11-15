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
md = open('CONTRACT.md', encoding='utf-8').read() + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.74: the v0.18.60 note moved to CHANGELOG.md
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
assert 'STREAM_READ_RETRIES' in md and ': stream read failed; reconnect to catch up' in md and 'HOUSEKEEPING_LANES' in open('CHANGELOG.md').read(), 'CONTRACT.md v0.18.68 wording (its note moved to CHANGELOG.md in v0.18.74)'
PY
# v0.18.69: safety writes outside the write limit + telemetry's own budget (server B1.22, owner W1 Q82), wording only.
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
r = c['rateLimit']
sw = r['safetyWrites']
for p in ['/rider/trips/{tripId}/sos', '/driver/trips/{tripId}/sos', '/rider/trips/{tripId}/ride-check', '/driver/trips/{tripId}/ride-check', '/trips/{tripId}/cancel,', '/rides/{rideId}/cancel', '/admin/trips/{tripId}/cancel']:
    assert p in sw, 'rateLimit.safetyWrites route ' + p
assert 'RIDE_CHECK_APP_MAX_PER_TRIP (server setting, default 30)' in sw and 'Matched on the route' in sw and 'including /trips/{tripId}/cancel-reason, still counts' in sw, 'rateLimit.safetyWrites wording'
assert 'contract.json#telemetry.limits' in r['ownBudget'], 'rateLimit.ownBudget'
t = c['telemetry']
assert t['perAddressPerMinute'] == 120, 'telemetry.perAddressPerMinute'
assert 'TELEMETRY_PER_ADDRESS_PER_MINUTE' in t['limits'] and 'reason telemetry_too_many' in t['limits'] and '1/WEB_COPIES' in t['limits'] and 'payload_too_large' in t['limits'], 'telemetry.limits wording'
md = open('CONTRACT.md').read()
assert 'telemetry_too_many' in md and 'RIDE_CHECK_APP_MAX_PER_TRIP' in md and '**Safety writes**' in md and 'TELEMETRY_PER_ADDRESS_PER_MINUTE' in md, 'CONTRACT.md v0.18.69 wording'
PY
# v0.18.70: no mass offline after an outage; the booked offline check waits the same grace (server S4 B1.23, owner Q83), additive.
python3 - <<'PY'
import json
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 70), 'version'
s = c['driverHome']['setOffline']
g = s['outageGrace']
assert g['lateSeconds'] == 60 and g['fixCheckEverySeconds'] == 10 and sorted(g) == ['fixCheckEverySeconds', 'lateSeconds', 'note'], 'outageGrace values'
assert 'heardAgainAt' in g['note'] and 'WEB_COPIES > 1' in g['note'] and 'configDefaults.noFixMinutesBeforeOffline' in g['note'] and 'No new setting, no app change' in g['note'] and 'One signal only' in g['note'] and 'The first fix stored after an outage also marks it' in g['note'] and 'whichever is earlier' in g['note'] and 'While the row is overdue every stored fix checks' in g['note'] and 'only after it found the row missing or not overdue' in g['note'] and 'a separate run it books right away' in g['note'] and 'not covered' in g['note'] and 'never later than the ride\'s dispatchAt' in g['note'] and 'A parked job row gives no signal' in g['note'], 'outageGrace note'
assert s['auditAction'] == 'driver.auto_offline' and s['default'] == 5 and s['jobEverySeconds'] == 30, 'setOffline kept'
assert 'v0.18.70 (B1.23)' in s['note'] and '(outageGrace)' in s['note'], 'setOffline.note v0.18.70'
rm = c['bookLater']['driver']['reminders']
assert 'driverHome.setOffline.outageGrace' in rm and 'reservation_lost' in rm and 'dispatchAt' in rm, 'bookLater.driver.reminders v0.18.70'
md = open('CONTRACT.md').read()
assert '## 88. No mass offline after an outage' in md and 'contract.json#driverHome.setOffline.outageGrace' in md and 'heardAgainAt' in md and 'not covered' in md and '`dispatchAt`' in md and 'first fix stored after it' in md and 'separate run right after it' in md, 'CONTRACT.md v0.18.70 wording'
PY
# v0.18.71: same-language shortcut only for quick-reply chips and automatic messages (live bug 2026-11-12, server 43186c9), wording only.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 71), 'version'
sl = c['chat']['autoTranslate']['sameLanguage']
assert sl.startswith('v0.18.71') and 'Message.quickReplyId or Message.auto present' in sl and 'Typed text whose Message.lang equals to goes to the kept translation or the provider' in sl and 'chat.autoTranslate.sourceLanguage' in sl and '503 unavailable, reason coming_soon' in sl, 'chat.autoTranslate.sameLanguage v0.18.71'
spec = yaml.safe_load(open('openapi.yaml'))
d = ' '.join(spec['paths']['/trips/{tripId}/messages/translate']['post']['description'].split())
tm = ' '.join(spec['components']['schemas']['TranslatedMessage']['description'].split())
for x in (d, tm):
    assert 'Message.quickReplyId or Message.auto present' in x and 'Typed text whose Message.lang equals to' in x, 'openapi sameLanguage v0.18.71'
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.99: this note moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert '**§85 same-language shortcut**' in md and 'typed text with `Message.lang` = `to` is translated like any other' in md, 'CONTRACT.md v0.18.71 wording'
PY
# v0.18.72 §89 (G17, live bug 2026-11-12, server 165fb9c): the driver's config and stream follow the zone he works in, wording + additive key.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 72), 'version'
d = c['driverConfigZone']
assert sorted(d) == ['app', 'asked', 'note', 'serverDefault'], 'driverConfigZone keys'
assert d['note'].startswith('v0.18.72') and 'Driver.zoneIds[0]' in d['note'] and 'emergencyNumbers' in d['note'] and 'currency' in d['note'], 'driverConfigZone.note'
assert 'tripStatus.driverAssigned' in d['app'] and 'GET /driver/zones' in d['app'] and 'reopens the stream with the new zoneId' in d['app'] and 'Versions are compared per zone: on a zone change the app compares against, and sends as Last-Event-ID, the last version it holds for THAT zone (none if none).' in d['app'], 'driverConfigZone.app'
sd = d['serverDefault']
order = [sd.index(x) for x in ('active trip', 'driver_locations.zone_id', 'Driver.zoneIds[0]', 'server default zone')]
assert order == sorted(order) and 'not a held booked ride, not a queued next trip' in sd and '(at most one: trips_one_active_per_driver)' in sd and 'most recently updated' not in sd and 'does not move an open stream' in sd, 'driverConfigZone.serverDefault'
assert '?zoneId= always wins' in d['asked'] and 'zone_not_found' in d['asked'] and 'config_not_published' in d['asked'], 'driverConfigZone.asked'
assert c['tripStatus']['driverAssigned'] == ['accepted', 'driver_to_pickup', 'arrived', 'rider_onboard', 'in_trip', 'approaching_dropoff'], 'driverAssigned'
assert 'driverConfigZone' in c['emergencyNumbers']['apps'] and 'police 197 / ambulance 190' in c['emergencyNumbers']['apps'], 'emergencyNumbers.apps v0.18.72'
assert 'driverConfigZone' in c['pickupWaiting']['servedConfig']['note'], 'servedConfig v0.18.72'
spec = yaml.safe_load(open('openapi.yaml'))
for p in ('/driver/config', '/driver/config/stream'):
    g = spec['paths'][p]['get']
    assert 'v0.18.72 §89' in g['description'] and d['serverDefault'] in g['description'], p + ' description v0.18.72'
    z = [x for x in g['parameters'] if x.get('name') == 'zoneId']
    assert len(z) == 1 and z[0]['required'] is False and 'v0.18.72' in z[0]['description'], p + ' zoneId v0.18.72'
    assert {'$ref': '#/components/parameters/ZoneIdQuery'} not in g['parameters'], p + ' still shared ZoneIdQuery'
assert {'$ref': '#/components/parameters/ZoneIdQuery'} in spec['paths']['/rider/config']['get']['parameters'], 'rider keeps ZoneIdQuery'
assert 'driverConfigZone' in spec['components']['schemas']['DriverAppConfig']['properties']['emergencyNumbers']['description'], 'openapi emergencyNumbers v0.18.72'
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.93: the v0.18.72-v0.18.81 notes moved to CHANGELOG.md
assert "## 89. The driver's config follows the zone he works in (v0.18.72, G17)" in md and 'contract.json#driverConfigZone' in md and '`driver_locations.zone_id`' in md and 'does not move an open stream' in md and 'Versions are compared per zone: on a zone change the app compares against, and sends as\n  `Last-Event-ID`, the last version it holds for THAT zone (none if none).' in md and '(at most one: `trips_one_active_per_driver`)' in md, 'CONTRACT.md v0.18.72 wording'
PY
# v0.18.73 (wording only, server B1.14 d5400cd + B1.15 73d28e1, rider G26-back f513af55): dispatch_round restarts once, streams end with their session, rider back before pickup.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 73), 'version'
r = c['alertDesk']['serverDetection']['kindDefaults']['system_health']['rule']
assert '(all listed kinds except ride_check_no_answer and withdraw_driver_offers)' in r and 'dispatch_round since 0.18.73, server B1.14' in r and 'withdraw_driver_offers and dispatch_round)' not in r and 'parks it for good (no loop)' in r and 'solved at the next sweep' in r, 'system_health rule v0.18.73'
se = c['realtime']['sessionEnd']
assert se.startswith('v0.18.73') and 'STREAM_SESSION_CHECK_MS (default 30 s, at most 60 s)' in se and "': session ended; sign in again'" in se and 'session_ended or signed_in_elsewhere' in se and 'auth.signedOut' in se and 'role change or deactivation' in se and 'preview token' in se and 'never closes a stream' in se, 'realtime.sessionEnd'
rb = c['riderBack']
assert sorted(rb) == ['apps', 'beforePickup', 'cancelInFlight', 'note', 'onBoard', 'rideCheckOpen', 'searching'], 'riderBack keys'
b = rb['beforePickup']
assert b['statuses'] == ['accepted', 'driver_to_pickup', 'arrived'] and b['back'] == 'lower_sheet_or_nothing' and b['opensCancel'] is False and b['leavesScreen'] is False and b['cancelEntry'] == 'close_button', 'riderBack.beforePickup'
assert rb['onBoard']['statuses'] == c['tripStatus']['riderOnboard'] and rb['onBoard']['back'] == 'open_trip_details' and rb['rideCheckOpen']['back'] == 'nothing' and rb['searching']['back'] == 'open_cancel_sheet', 'riderBack other screens'
assert set(b['statuses']) <= set(c['tripStatus']['driverAssigned']) and not set(b['statuses']) & set(c['tripStatus']['riderOnboard']), 'riderBack statuses'
spec = yaml.safe_load(open('openapi.yaml'))
assert str(spec['info']['version']) == c['version'], 'openapi version'
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.93: the v0.18.72-v0.18.81 notes moved to CHANGELOG.md
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 73), 'CONTRACT.md title'
assert '**Streams end with their session** (v0.18.73' in md and '`: session ended; sign in again`' in md and '`contract.json#realtime.sessionEnd`' in md, 'CONTRACT.md §4 v0.18.73'
assert '**Rider back before pickup** (v0.18.73, G26-back' in md and '`contract.json#riderBack`' in md and '**a stopped dispatch round restarts once** (B1.14' in md, 'CONTRACT.md v0.18.73 wording'
PY
# v0.18.74 (wording only, server B1.24 9f35e1e, owner W1 Q84 + 2026-11-12 "None of these"): exactly six admin safety reads are never shed.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 74), 'version'
s = c['fastDispatch']['shedOnly']
reads = ['GET /admin/incidents,', 'GET /admin/incidents/{incidentId},', 'GET /admin/incidents/{incidentId}/emergency-contacts,', 'GET /admin/ride-checks,', 'GET /admin/alerts/book,', 'GET /admin/trips/{tripId} (']
assert all(r in s for r in reads) and 'exactly six, no more' in s and 'matched on the route pattern' in s and 'a path that matches no route is still shed' in s and 'Every other GET /admin/* read is still shed' in s and 'can still answer server_busy' in s, 'fastDispatch.shedOnly v0.18.74'
assert s.startswith('Only new low-priority work is ever refused with server_busy: POST /quotes'), 'shedOnly start kept'
spec = yaml.safe_load(open('openapi.yaml'))
assert str(spec['info']['version']) == c['version'], 'openapi version'
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.93: the v0.18.72-v0.18.81 notes moved to CHANGELOG.md
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 74), 'CONTRACT.md title'
assert '**admin safety reads are never shed** — exactly six' in md and '`GET /admin/incidents/{incidentId}/emergency-contacts`' in md and '`GET /admin/alerts/book`' in md, 'CONTRACT.md v0.18.74 note'
assert "GPS and streams are never shed; v0.18.74 (B1.24): nor are the six admin safety reads (incidents list, an incident, its emergency contacts, ride checks, the alert book, a trip's detail; `contract.json#fastDispatch.shedOnly`). Apps treat it like 429" in md, 'CONTRACT.md Overload bullet v0.18.74'
PY
# v0.18.75 (server B1.25 641f1e6, owner W1 Q85): a total per server copy for no-token telemetry; additive keys, no API shape change.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 75), 'version'
t = c['telemetry']
assert t['anonRowsPerMinute'] == 600 and t['anonBytesPerMinute'] == 2097152 and t['perAddressPerMinute'] == 120, 'telemetry anon caps'
l = t['limits']
assert 'TELEMETRY_ANON_ROWS_PER_MINUTE / TELEMETRY_ANON_BYTES_PER_MINUTE' in l and 'NOT divided by WEB_COPIES' in l and 'still answers 202 with an empty body but is not stored' in l and 'A signed-in caller is never counted here' in l and 'none sent, or stale/bad' in l, 'telemetry.limits v0.18.75'
assert l.startswith('B1.22: its own budget'), 'telemetry.limits start kept'
spec = yaml.safe_load(open('openapi.yaml'))
assert str(spec['info']['version']) == c['version'], 'openapi version'
for p in ('/telemetry/logs', '/telemetry/analytics', '/telemetry/crashes'):
    d = spec['paths'][p]['post']['description']
    assert 'v0.18.75 (B1.25): without a valid token, a server copy stores at most contract.json#telemetry.anonRowsPerMinute (600) lines and anonBytesPerMinute (2097152) bytes per minute in total; over it the call still answers 202 but is not stored.' in d, 'openapi ' + p
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.93: the v0.18.72-v0.18.81 notes moved to CHANGELOG.md
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 75), 'CONTRACT.md title'
assert '**no-token telemetry has a total per server copy**' in md and '`TELEMETRY_ANON_ROWS_PER_MINUTE` / `TELEMETRY_ANON_BYTES_PER_MINUTE`, not divided by `WEB_COPIES`' in md, 'CONTRACT.md v0.18.75 note'
PY
# v0.18.76 (G30, owner 2026-11-12 Q1–Q6): an e-mail is saved only after a code check; emailVerifiedAt; per-country approval setting (off).
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 76), 'version'
e = c['emailVerified']
for k in ('field', 'writePaths', 'existing', 'verifyCurrent', 'unique', 'delivery', 'approvalSetting', 'apps', 'texts'):
    assert k in e, 'emailVerified.' + k
assert set(e['writePaths']) == {'codeChange', 'riderPatch', 'driverSignUp', 'provider', 'seed'}, 'emailVerified.writePaths'
assert '400 invalid_request, reason email_needs_code' in e['writePaths']['riderPatch'] and 'never blocked' in e['writePaths']['driverSignUp'], 'write paths'
assert 'email_verified true' in e['writePaths']['provider'] and 'Rule 21' in e['existing'], 'provider / existing'
assert 'SAME app' in e['unique'] and 'own rider and driver accounts' in e['unique'] and 'never blocks' in e['unique'], 'unique'
assert 'no 10-minute sign-in rule' in e['verifyCurrent'] and 'no other session ends' in e['verifyCurrent'], 'verifyCurrent'
assert 'OFF by default' in e['approvalSetting'] and '409 invalid_transition, reason email_not_verified' in e['approvalSetting'], 'approvalSetting'
assert 'Home sheet' in e['apps']['driver'] and 'never blocks going online' in e['apps']['driver'], 'driver Home notice'
rm = c['driverOnboarding']['reminders']
assert 'verify_email' in rm['fixTargets'] and rm['kinds']['email_not_verified'].startswith('v0.18.76 (G30') and 'X-Contract-Version is 0.18.76 or higher' in rm['kinds']['email_not_verified'], 'reminder email_not_verified'
assert set(rm['texts']['email_not_verified']) == {'sv', 'fr', 'en'}, 'reminder text'
for t in e['texts'].values():
    assert set(t) == {'en', 'fr', 'sv'} and all(t.values()), 'texts en/fr/sv'
for cc, d in c['driverOnboarding']['settings']['defaults'].items():
    assert d['emailVerifiedForApproval'] is False, 'default off ' + cc
a = c['deepFix1']['accountChange']
assert '→ { email, emailVerifiedAt } (v0.18.76)' in a and 'any account (rider or driver) gets' not in a, 'accountChange v0.18.76'
assert 'email_needs_code (400 invalid_request), email_not_verified (409 invalid_transition)' in c['errors']['reason'], 'error reasons'
spec = yaml.safe_load(open('openapi.yaml'))
assert str(spec['info']['version']) == c['version'], 'openapi version'
sc = spec['components']['schemas']
for n in ('Rider', 'Driver'):
    assert sc[n]['properties']['emailVerifiedAt']['allOf'] == [{'$ref': '#/components/schemas/Timestamp'}], n + '.emailVerifiedAt'
    assert 'emailVerifiedAt' not in sc[n].get('required', []), n + ' optional'
assert 'email' not in sc['RiderProfileUpdate']['properties'] and 'email_needs_code' in sc['RiderProfileUpdate']['description'], 'RiderProfileUpdate'
assert 'email_needs_code' in spec['paths']['/rider/profile']['patch']['description'], 'PATCH /rider/profile'
assert sc['AccountEmailVerified']['required'] == ['email', 'emailVerifiedAt'], 'AccountEmailVerified'
r = spec['paths']['/account/email/verify']['post']['responses']['200']['content']['application/json']['schema']
assert r == {'$ref': '#/components/schemas/AccountEmailVerified'}, 'verify answer'
assert 'email' in sc['DriverOnboardingRequest']['required'] and 'never blocked' in sc['DriverOnboardingRequest']['properties']['email']['description'], 'onboarding email'
o = sc['OnboardingSettings']['properties']['emailVerifiedForApproval']
assert o['type'] == 'boolean' and o['default'] is False and 'emailVerifiedForApproval' not in sc['OnboardingSettings']['required'], 'setting'
assert 'email_not_verified' in spec['paths']['/admin/drivers/{driverId}/status']['post']['description'], 'approval check'
assert 'email_verified true' in spec['paths']['/auth/provider']['post']['description'], 'provider'
assert 'email_not_verified' in sc['DriverReminder']['properties']['kind']['enum'] and 'verify_email' in sc['ReminderFix']['properties']['target']['enum'], 'reminder enums'
assert 'v0.18.76 (G30): email_not_verified' in spec['paths']['/driver/reminders']['get']['description'], 'GET /driver/reminders'
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.93: the v0.18.72-v0.18.81 notes moved to CHANGELOG.md
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 76), 'CONTRACT.md title'
assert '**an e-mail is saved only after a code check**' in md and 'email?, emailVerifiedAt? (v0.18.76), rating?' in md and 'email?, emailVerifiedAt? (v0.18.76), country?' in md, 'CONTRACT.md v0.18.76'
PY
# v0.18.76 owner answers 2026-11-12 ~14:10 (supervisor S1–S3 + French): failed send = pending_provider; red Home line "needed for approval"; approval check = never active before.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
e = c['emailVerified']
dl = e['delivery']
assert "'sent' only when the sending service accepted" in dl and 'refused the send or it failed' in dl and 'Resend without an own domain' in dl and "never 'sent' unless the provider accepted it" in dl and 'texts.codeNotSentYet' in dl, 'S1 delivery'
a = c['deepFix1']['accountChange']
assert 'delivery: pending_provider' not in a and "delivery 'sent' only when the sending service accepted the e-mail, else 'pending_provider', also on a refused or failed send" in a, 'S3 accountChange'
ap = e['approvalSetting']
assert 'NEVER active before' in ap and 'pending → suspended → active' in ap and 'Not checked when a once-active driver is made active again' in ap and 'contract.json#emailVerified.neverActive' in ap, 'approval scope'
assert 'is not checked when a suspended driver is made active again' not in ap, 'old suspended rule gone'
na = e['neverActive']
assert 'server-internal column' in na and 'first_activated_at' in na and 'never cleared' in na and 'not sent in any view' in na and 'counts as never active' in na, 'neverActive'
assert list(e).index('neverActive') == list(e).index('approvalSetting') + 1, 'neverActive order'
rm = c['driverOnboarding']['reminders']
k = rm['kinds']['email_not_verified']
assert 'blocks_online' in rm['levels'] and 'due_soon' in rm['levels'], 'levels'
assert 'blocks_online (red) with text texts.email_not_verified_approval' in k and 'OnboardingSettings.emailVerifiedForApproval is on and he was never active before' in k and 'otherwise due_soon (orange' in k, 'reminder level'
assert 'nor a red email_not_verified line' in rm['kinds']['account_not_active'], 'account_not_active vs red e-mail line'
t = rm['texts']['email_not_verified_approval']
assert set(t) == {'sv', 'fr', 'en'} and t['en'].endswith('needed for approval. Tap to verify it.') and 'approbation' in t['fr'] and 'för att bli godkänd' in t['sv'] and 'godkännande' not in t['sv'], 'approval text sv/fr/en'
assert rm['texts']['email_not_verified']['fr'] == 'Votre e-mail n’est pas vérifié. Appuyez pour le vérifier.', 'fr Appuyez'
assert not any('Touchez' in v for tx in rm['texts'].values() if isinstance(tx, dict) for v in tx.values()), 'no Touchez'
assert 'texts.email_not_verified_approval' in e['apps']['driver'] and 'never blocks going online' in e['apps']['driver'], 'driver app red/orange'
assert 'first-activated column' in e['rule0'], 'rule0 server column'
spec = yaml.safe_load(open('openapi.yaml'))
st = spec['paths']['/admin/drivers/{driverId}/status']['post']['description']
assert 'NEVER active before' in st and 'first_activated_at' in st, 'openapi approval scope'
assert 'refused the send or it failed' in spec['components']['schemas']['AccountEmailChallenge']['properties']['delivery']['description'], 'openapi delivery'
assert 'email_not_verified_approval' in spec['paths']['/driver/reminders']['get']['description'], 'openapi reminder level'
assert 'delivery: pending_provider' not in spec['paths']['/account/email/change']['post']['description'], 'openapi accountChange'
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.93: the v0.18.72-v0.18.81 notes moved to CHANGELOG.md
assert '(also a refused or failed send)' in md and 'red “needed for approval”' in md and 'for a driver never active before, not for re-activating one' in md, 'CONTRACT.md owner answers'
PY
# v0.18.76 round 3 (supervisor R2-1..R2-3): once-active backfill also from audit 'from active' and trips; seed paths named;
# account_not_active left out only when the red line is actually sent; a pending_provider start does not count toward 3/hour.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
e = c['emailVerified']
na = e['neverActive']
assert 'seedDriver' in na and 'seedTest' in na and 'start my own company' in na and 'active → on_hold' in na and 'by any path' in na, 'R2-1 paths'
assert "detail.from is 'active'" in na and 'detail.to is active' in na and 'any trip carrying his driver_id' in na and 'earliest such time' in na, 'R2-1 backfill'
assert 'only fills it (never deletes or changes other data)' in na and 'counts as never active' in na, 'R2-1 no delete'
ana = c['driverOnboarding']['reminders']['kinds']['account_not_active']
assert 'nor a red email_not_verified line actually sent in this answer' in ana and 'below 0.18.76 never gets that line, so it still gets account_not_active' in ana, 'R2-2'
dl = e['delivery']
assert "only when its answer is delivery 'sent'" in dl and "'pending_provider' start (no service, or a refused or failed send) does not count" in dl and 'never got a code' in dl, 'R2-3 delivery'
assert 'which does not count toward the 3 starts per hour' in c['deepFix1']['accountChange'], 'R2-3 accountChange'
spec = yaml.safe_load(open('openapi.yaml'))
assert "detail.from is 'active'" in spec['paths']['/admin/drivers/{driverId}/status']['post']['description'], 'openapi R2-1'
assert 'never got a code' in spec['components']['schemas']['AccountEmailChallenge']['properties']['delivery']['description'], 'openapi R2-3'
PY
# v0.18.77 (G30, owner 2026-11-12 ~15:02 "Max 10 tries/hour"): besides 3 accepted e-mail code sends per hour, at most 10 e-mail
# code starts per hour per account, counting every start (sent or pending_provider); over it 429 change_too_many.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 77), 'version'
dl = c['emailVerified']['delivery']
assert 'v0.18.77 (owner 2026-11-12 ~15:02' in dl and 'at most 10 e-mail code starts per hour per account, counting EVERY start, sent or pending_provider' in dl, 'v0.18.77 delivery cap'
assert 'The 11th start within the hour → 429 change_too_many (Retry-After), before any e-mail is sent' in dl and 'whichever limit is reached first refuses' in dl, 'v0.18.77 over the cap'
assert 'gets the same answer and no code, so the answer never tells' in dl and 'does not count' in dl.split('v0.18.77')[1] and 'phone starts are unchanged' in dl, 'v0.18.77 what counts'
assert "only when its answer is delivery 'sent'" in dl, 'v0.18.76 3 accepted sends kept'
a = c['deepFix1']['accountChange']
assert 'v0.18.77: for e-mail also at most 10 starts per hour per account, counting every start, sent or pending_provider (429 change_too_many; contract.json#emailVerified.delivery)' in a, 'v0.18.77 accountChange'
assert 'at most 3 starts per hour per account and kind (429 change_too_many);' in a, 'accountChange 3/hour kept'
spec = yaml.safe_load(open('openapi.yaml'))
op = spec['paths']['/account/email/change']['post']
assert 'at most 10 e-mail code starts per hour per account' in op['description'] and 'v0.18.77: for e-mail also at most 10 starts' in op['description'], 'openapi email change description'
r = op['responses']['429']
assert 'change_too_many' in r['description'] and 'at most 10 code starts' in r['description'] and 'Retry-After' in r['headers'], 'openapi email change 429'
assert r['content']['application/json']['schema'] == {'$ref': '#/components/schemas/Error'}, 'openapi 429 Error shape'
assert spec['paths']['/account/phone/change']['post']['responses']['429'] == {'$ref': '#/components/responses/RateLimited'}, 'phone 429 unchanged'
assert 'at most 10 e-mail code starts' in spec['components']['schemas']['AccountEmailChallenge']['properties']['delivery']['description'], 'openapi delivery'
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.93: the v0.18.72-v0.18.81 notes moved to CHANGELOG.md
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 77), 'CONTRACT.md title'
assert '**at most 10 e-mail code starts per hour**' in md and 'counting every start (`sent` or `pending_provider`)' in md, 'CONTRACT.md v0.18.77 note'
PY
# v0.18.78 (owner 2026-11-12 ~17:30 items 4 + 5): G33 rider "Pay the driver {amount} in the car"
# text + rule; admin list pages carry an optional total; GET /admin/incidents takes driverId / riderId.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 78), 'version'
tx = c['finish']['paymentMethods']['texts']['payDriverInCar']
assert tx == {'sv': 'Betala föraren {amount} i bilen', 'fr': 'Payez {amount} au chauffeur', 'en': 'Pay the driver {amount} in the car'}, 'G33 texts'
assert set(tx) == set(c['languages']['values']), 'G33 every app language'
pl = c['finish']['payInCarLine']
assert '{amount} = TripProjection.finish.cashToCollect' in pl and 'CompletePreview.cashDue' in pl and "receipt's cashPaid" in pl, 'G33 amount source'
assert 'Not shown when cashToCollect is 0' in pl and 'lifecycle0_18_50.l10 texts.youPay' in pl and '(status completed), never earlier, and only when cashToCollect is above 0' in pl and 'completed by the driver or by an admin' in pl, 'G33 when'
assert 'Server: no change' in pl and 'Admin: none' in pl and 'Driver: none' in pl, 'G33 Rule 0 line'
al = c['adminListFilters']
tot = al['total']
assert tot['lists'] == ['GET /admin/' + n for n in ['trips', 'riders', 'drivers', 'fleets', 'vehicles', 'payments', 'refunds', 'payouts', 'tickets', 'incidents']], 'total lists'
assert 'counted without cursor and limit' in tot['rule'] and 'absent = not counted' in tot['rule'] and 'never send total' in tot['rule'] and 'there is no totalAtLeast' in tot['rule'], 'total rule'
assert 'within the list\'s time budget; never a guess' in tot['rule'] and 'total is left out and the page is still served; the count never fails or slows the list' in tot['rule'], 'total Rule 33'
assert '/rider/refunds' not in tot['rule'] and '/admin/refunds/payouts' not in tot['rule'], 'total other shapes'
assert 'never filtered in code after the read' in tot['server'], 'total vehicles zone in SQL'
ib = al['incidentsByPerson']
assert 'driverId (cases whose Incident.driverId is that driver)' in ib and 'riderId (cases whose Incident.riderId is that rider)' in ib and 'unknown_filter' in ib and 'may add an index on incidents.driver_id and incidents.rider_id' in ib, 'incidents filters'
spec = yaml.safe_load(open('openapi.yaml'))
sch = spec['components']['schemas']
for route in tot['lists']:
    op = spec['paths'][route.split(' ', 1)[1]]['get']
    page = op['responses']['200']['content']['application/json']['schema']['$ref'].split('/')[-1]
    t = sch[page]['allOf'][1]['properties']['total']
    assert t['type'] == 'integer' and t['minimum'] == 0, route + ' total'
    assert 'total' not in sch[page]['allOf'][1].get('required', []), route + ' total optional'
assert sch['Page']['required'] == ['items', 'nextCursor'] and 'total' not in sch['Page']['properties'], 'generic Page unchanged'
names = [p.get('name') for p in spec['paths']['/admin/incidents']['get']['parameters']]
assert 'driverId' in names and 'riderId' in names, 'openapi incidents filters'
inc = [p for p in spec['paths']['/admin/incidents']['get']['parameters'] if p.get('name') in ('driverId', 'riderId')]
assert all(p['required'] is False and p['schema'] == {'$ref': '#/components/schemas/Id'} for p in inc), 'incidents filters optional Id'
cc = sch['TripFinish']['properties']['cashToCollect']
assert cc['allOf'] == [{'$ref': '#/components/schemas/Money'}] and 'payDriverInCar' in cc['description'], 'openapi TripFinish.cashToCollect'
assert 'cashToCollect' in sch['TripFinish']['required'], 'cashToCollect still required'
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.93: the v0.18.72-v0.18.81 notes moved to CHANGELOG.md
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 78), 'CONTRACT.md title'
assert 'supersedes the S5 J16 `totalAtLeast` idea' in md and '**G33 rider pay-in-car line**' in md and 'first page when counted exactly' in md and '**admin lists “50 of N”**' in md, 'CONTRACT.md v0.18.78 note'
assert open('CONTRACT.md').read().count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.79 (server B1.33, owner Q93 "A) Yes"): a ticket without a zone can be assigned and auto-sorted to an admin of its
# country team (wording only).
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 79), 'version'
sd = c['supportDesk']
cov = "covers the ticket (its zone; a ticket without a zone: a zone in the ticket's country, or all zones — the countryTeam rule)"
asg = sd['adminCommands']['assign']
assert cov + ' (else 400 invalid_request, reason assignee_not_allowed); null = nobody.' in asg and "covers the ticket's zone" not in asg, 'B1.33 assign'
au = sd['settings']['autoSort']
assert 'has support.reply and ' + cov + ' (else nobody).' in au and "covers the ticket's zone" not in au, 'B1.33 autoSort'
ct = sd['countryTeam']
assert 'see and answer it (list and one ticket), get it assigned (assign) and auto-sorted to them (settings.autoSort), Super admins too' in ct and "Q93 'A) Yes'" in ct, 'B1.33 countryTeam'
spec = yaml.safe_load(open('openapi.yaml'))
d = spec['paths']['/admin/tickets/{ticketId}/assign']['post']['description']
assert cov in d and 'a ticket without a zone: an admin with a zone in its country, or all zones (contract.json#supportDesk.countryTeam); else 403 zone_out_of_scope.' in d, 'B1.33 openapi assign'
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.93: the v0.18.72-v0.18.81 notes moved to CHANGELOG.md
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 79), 'CONTRACT.md title'
assert '**a support ticket without a zone can be assigned and auto-sorted to its country team**' in md and '\nv0.18.79 (wording only, server B1.33, owner Q93' in md, 'CONTRACT.md v0.18.79 note'
assert open('CONTRACT.md').read().count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.81 (server B1.34, owner Q94 "A) Yes" + 2026-11-13 answers): at most maxOpenPerRider (default 3, 1-50) open booked
# rides per rider; the next POST /trips kind scheduled -> 409 conflict, reason booked_rides_limit, the number in the message.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 81), 'version'
r = c['configDefaults']['reservations']
assert r['maxOpenPerRider'] == 3 and 'maxOpenPerRider 3' in r['note'], 'B1.34 default'
bl = c['bookLater']
assert 'booked_rides_limit' in bl['errors'], 'B1.34 error'
cap = bl['riderCap']
for part in ('409 conflict, reason booked_rides_limit', 'range 1-50', 'Live rides do not count', 'Two bookings at the same moment never pass it',
             'not at POST /quotes', 'reschedule'):
    assert part in cap, 'B1.34 riderCap: ' + part
t = bl['texts']['bookedRidesLimit']
assert t == {'sv': 'Du kan ha högst {n} bokade resor. Avboka en för att boka en ny.',
             'fr': 'Vous pouvez avoir au maximum {n} courses programmées. Annulez-en une pour en réserver une autre.',
             'en': 'You can have at most {n} booked rides. Cancel one to book another.'}, 'B1.34 texts'
spec = yaml.safe_load(open('openapi.yaml'))
m = spec['components']['schemas']['DriverReservations']['properties']['maxOpenPerRider']
assert (m['type'], m['minimum'], m['maximum'], m['default']) == ('integer', 1, 50, 3), 'B1.34 openapi setting'
d = spec['paths']['/trips']['post']['responses']['409']
assert 'booked_rides_limit' in d['description'], 'B1.34 openapi 409'
md = open('CONTRACT.md').read() + open('CHANGELOG.md').read()  # v0.18.93: the v0.18.72-v0.18.81 notes moved to CHANGELOG.md
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 81), 'CONTRACT.md title'
assert '**at most 3 open booked rides per rider**' in md and '\nv0.18.81 (server B1.34' in md and '`maxOpenPerRider` (3)' in md, 'CONTRACT.md v0.18.81 note'
assert open('CONTRACT.md').read().count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.82 (S5 J3 money fixes; owner Sitting 3 2026-11-12: 106, 107, Q-M7, Q-S5-6, Q-S5-7, J1 0.14a, S07 M8/M14):
# expectedVersion on the two admin money buttons, one commission + KPI money rule, admin fare = driver side only,
# Tunisia defaults (tip max 30 DT, driver pay change max 100 DT, payouts on Africa/Tunis), payouts on their own timer, a trip ends once.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 82), 'version'
mb = c['moneyBase']
vg = mb['versionGuard']
for part in ('POST /admin/riders/{riderId}/wallet-credit { expectedVersion, amount, reason }', 'POST /admin/trips/{tripId}/driver-pay { expectedVersion, change, reason }',
             'Rider.version', 'TripProjection.version', '409 version_mismatch with the fresh projection', 'missing expectedVersion → 400 invalid_request'):
    assert part in vg, 'J3 versionGuard: ' + part
assert '{ expectedVersion, amount, reason }' in c['walletCredit']['note'], 'J3 walletCredit note'
assert 'driver-pay { expectedVersion (v0.18.82, required' in c['finish']['driverMoney']['payChange'] and 'TN 100 DT' in c['finish']['driverMoney']['payChange'], 'J3 payChange'
cm = mb['commission']
assert 'commission = fare − debtCollected − driverEarnings − pickupPay − driverBonus' in cm and 'never work it out themselves' in cm and 'earnings entry' in cm, 'J3 commission'
k = mb['kpiMoney']
for part in ('captured, partially_refunded or refunded', 'ended early by the rider', 'ended by the driver with the rider on board', 'without the outstanding_fee line',
             'counted once', 'earnings entries', 'refunds', 'Stored days are re-summed once', 'trip data is never changed'):
    assert part in k, 'J3 kpiMoney: ' + part
assert c['kpis']['money']['gross'].startswith('v0.18.82'), 'J3 kpis.money.gross'
af = mb['adminFare']
for part in ('changes ONLY the driver', "The rider's price is never changed by it", 'POST /admin/trips/{tripId}/adjust', 'POST /admin/trips/{tripId}/complete',
             'driverAdjustments', 'kept as its own delta across every re-price', 'arrive', 'board', 'end'):
    assert part in af, 'J3 adminFare: ' + part
assert 'moneyBase.adminFare' in c['onTrip']['adminTrip']['existing']['adjust'] and 'moneyBase.adminFare' in c['onTrip']['adminTrip']['existing']['complete'], 'J3 admin commands'
# Q-S5-8 (owner 2026-11-13 "Admin types driver pay (Rec.)"): driverPay typed directly; the old fare is refused, never read as pay.
for part in ("Q-S5-8", "{ expectedVersion, driverPay?, waitingSeconds?, waiveCancelFee?, reason }", "{ expectedVersion, note, driverPay? }", "delta = driverPay − the driver's pay now",
             'driver_pay_above_max', 'driver_pay_below_zero', 'reason fare_is_driver_pay', 'never read as a driver pay'):
    assert part in af, 'Q-S5-8 adminFare: ' + part
assert 'OPEN' not in af and mb['openQuestions'] == [], 'Q-S5-8 answered: no open question left'
for kk in ('adjust', 'complete'):
    assert 'driverPay?' in c['onTrip']['adminTrip']['existing'][kk] and 'fare_is_driver_pay' in c['onTrip']['adminTrip']['existing'][kk], 'Q-S5-8 admin ' + kk
cd = c['configDefaults']
assert cd['tipRules']['customMax']['TN'] == {'amountMinor': 30000, 'currency': 'TND'}, 'TN-1 tip custom max 30 DT'
assert cd['driverPayChangeMax']['TN'] == {'amountMinor': 100000, 'currency': 'TND'}, 'TN-1 driver pay change max 100 DT (owner re-confirmed 2026-11-13)'
assert c['moneyDisplay']['formats']['TND']['decimals'] == 3, 'TND 3 decimals'
assert c['payouts']['schedule']['countryTimeZones'] == {'SE': 'Europe/Stockholm', 'FR': 'Europe/Paris', 'TN': 'Africa/Tunis'}, 'TN-1 payout time zone'
assert 'TN Africa/Tunis' in c['payouts']['schedule']['note'] and 'TN 30 DT' in c['finish']['tips']['settings'], 'TN-1 notes'
assert 'admin-changeable' in mb['tunisia'] and '30.000 DT' in mb['tunisia'] and '100.000 DT' in mb['tunisia'] and '|new pay − current pay| ≤ max' in mb['tunisia'], 'TN-1 moneyBase.tunisia'
pn = c['payouts']['note']
assert 'own payout timer, one driver per transaction' in pn and 'nightly job makes' not in pn, 'J3 payouts.note'
assert 'a trip ends once; a second end is refused' in mb['endOnce'] and '409 invalid_transition' in mb['endOnce'], 'M14 rule line'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
for name in ('WalletCreditCommand', 'DriverPayCommand'):
    sc = S[name]
    assert 'expectedVersion' in sc['required'] and sc['properties']['expectedVersion']['minimum'] == 1, 'J3 openapi ' + name
for p in ('/admin/riders/{riderId}/wallet-credit', '/admin/trips/{tripId}/driver-pay'):
    d = spec['paths'][p]['post']['responses']['409']
    assert 'version_mismatch' in d['description'] and 'v0.18.82' in d['description'], 'J3 openapi 409 ' + p
assert 'TN 100 DT' in S['CountryRules']['properties']['driverPayChangeMax']['description'], 'TN-1 openapi driverPayChangeMax'
for name in ('AdminAdjustCommand', 'AdminCompleteCommand'):
    pr = S[name]['properties']
    assert 'driver side only' in pr['driverPay']['description'] and pr['driverPay']['allOf'] == [{'$ref': '#/components/schemas/Money'}], 'Q-S5-8 openapi driverPay ' + name
    assert pr['fare'].get('deprecated') is True and 'fare_is_driver_pay' in pr['fare']['description'] and 'driverPay' not in S[name].get('required', []), 'Q-S5-8 openapi old fare ' + name
assert 'debtCollected' in S['TripProjection']['properties']['commission']['description'], 'J3 openapi commission'
assert S['KpiDay']['properties']['gross']['description'].startswith('v0.18.82'), 'J3 openapi KPI gross'
md = open("CONTRACT.md").read()
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 82), 'CONTRACT.md title'
ch = open('CHANGELOG.md').read(); assert '\nv0.18.82 (S5 J3 money fixes' in ch and '**money fixes**' in ch and '`driverPay` on adjust / complete' in ch and 'Q-S5-8, open' not in md, 'CONTRACT.md v0.18.82 note'  # v0.18.101: the v0.18.82 note moved to CHANGELOG.md
assert '  //         commission = Movera\'s share of the fare: fare − debtCollected − driverEarnings − pickupPay − driverBonus' in md and '(fare − driverEarnings)' not in md, 'CONTRACT.md one commission'
# Third commit (owner values re-confirmed 2026-11-13 + supervisor M1-M3, S1-S4): 150 DT is the J7 cash-owed limit, never in J3.
oa = open('openapi.yaml').read()
assert '(fare − driverEarnings)' not in oa and 'commission = moneyBase.commission (v0.18.82)' in S['TripProjection']['description'], 'M1 openapi commission text'
assert 'TripProjection.commission carries it' not in c['pricing']['moneySplit']['moveraShare'] and 'it is NOT TripProjection.commission' in c['pricing']['moneySplit']['moveraShare'], 'M2 moveraShare'
assert 'Movera keeps fare − debtCollected − driverEarnings − pickupPay − driverBonus' in c['pickupPay']['moneySplit'], 'M2 pickupPay.moneySplit'
assert 'Movera keeps `fare − debtCollected − driverEarnings − pickupPay − driverBonus`' in md and 'Movera keeps `fare − driverEarnings' not in md, 'M2 CONTRACT.md pickup pay'
me = c['kpis']['money']['moveraEarnings']
assert me.startswith('v0.18.82') and "− Movera's pay changes" in me and 'nets out against that refund' in me and "− Movera's pay changes" in mb['kpiMoney'], 'M3 moveraEarnings'
assert "− Movera's pay changes" in md and '− pickup pay − driver bonuses Movera paid' not in md and 'v0.10.3 money rules' not in md, 'M3 CONTRACT.md KPIs'
assert "'No, without tip'" in af and "'32 DT, keep change'" in af and 'the tip stays on top' in af and 'the change is kept' in af, 'owner Q1/Q3 help text'
assert 'customMax (SE 200 kr, FR 20 €, TN 30 DT)' in md, 'S1 tips TN'
assert 'the hourly sweep with the payout pass' not in c['fastDispatch']['timers'], 'S2 timers'
adj = spec['paths']['/admin/trips/{tripId}/adjust']['post']
assert adj['summary'] == "Change the driver's pay / waiting / waive cancel fee" and 'paymentStatus/fare change' not in adj['description'] and S['AdminAdjustCommand']['description'].startswith('Driver pay'), 'S3 adjust wording'
assert 'v0.18.82 reason: fare_is_driver_pay' in c['errors']['reason'] and 'fare_is_driver_pay' in S['Error']['properties']['reason']['description'], 'S4 Error.reason'
j3 = json.dumps(c['moneyBase'], ensure_ascii=False) + json.dumps(c['configDefaults']['driverPayChangeMax'], ensure_ascii=False) + c['finish']['driverMoney']['payChange'] + md.split('\n')[2]
assert '150 DT' not in j3 and '150.000 DT' not in j3 and '150000' not in j3, 'no 150 DT in J3 (it is the J7 cash-owed limit)'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.83 (G34 fix-plan texts; owner 2026-11-13 12:18-12:24 UTC: S2 "Yes, 7 checks", S3 "60 s / 30 s", R4 "32 s",
# R3 "Yes, update rule", A2 "Exact contract filter", P4-B "Yes"): shed list of 7 repeat phone checks (GET /rider/trips/active
# never), late-timer alarm on /healthz/jobs, Home active-trip backoff 8/16/32 s, one stream "connected" rule, list total only
# when the list page asks (total=false), GET /admin/trips scheduledBefore.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 83), 'version'
fd = c['fastDispatch']
sp = fd['shedPolls']
SEVEN = ['GET /driver/airport-queue', 'GET /driver/surge-map', 'GET /notifications', 'GET /driver/reminders',
         'GET /driver/onboarding/settings', 'GET /rider/trips', 'GET /trips/{tripId}/messages']
assert sp['routes'] == SEVEN, 'S2 exactly 7 shed polls'
assert 'GET /rider/trips/active' not in sp['routes'] and 'GET /rider/trips/active' in sp['neverShed'], 'S2 active trip never shed'
for r in ('POST /driver/location', 'POST /offers/{offerId}/accept', 'POST /rider/trips/{tripId}/sos', 'POST /driver/trips/{tripId}/sos'):
    assert r in sp['neverShed'], 'S2 neverShed ' + r
for part in ('503 unavailable, reason server_busy', 'Retry-After 2', 'route pattern', 'keeps the last value', "Yes, 7 checks"):
    assert part in sp['rule'] + sp['note'], 'S2 rule: ' + part
assert 'v0.18.83' in fd['shedOnly'] and 'fastDispatch.shedPolls' in fd['shedOnly'], 'S2 shedOnly points to shedPolls'
la = fd['lateAlarm']
assert la['tripTimers']['lateSeconds'] == 60 and la['tripTimers']['kinds'][:3] == ['trip_eta', 'ride_check_scan', 'near_dropoff'], 'S3 trip timers 60 s'
assert la['dispatch']['lateSeconds'] == 30 and la['dispatch']['kinds'] == ['dispatch_round', 'withdraw_driver_offers'], 'S3 dispatch 30 s'
for part in ('/healthz/jobs', '503', 'lateSeconds', 'overdue', 'TRIP_LANES', 'default 1', '60 s / 30 s', 'never restarts'):
    assert part in la['rule'] + la['note'], 'S3 lateAlarm: ' + part
assert 'fastDispatch.lateAlarm' in fd['timers'], 'S3 timers points to lateAlarm'
bs = c['bookedRideSeen']
pb = bs['pollBackoff']
assert pb['stepsSeconds'] == [8, 16, 32] and pb['maxSeconds'] == 32, 'R4 8/16/32 cap 32'
for part in ('rider_trip_changed', 'at once', 'first answer', '"32 s (Rec.)"'):
    assert part in pb['rule'] + pb['note'], 'R4 pollBackoff: ' + part
assert 'bookedRideSeen.pollBackoff' in bs['pollFallback'] and bs['pollSeconds'] == 8, 'R4 pollFallback'
cr = c['realtime']['connectedRule']
for part in ('an event', '30 s', 'driver and rider', 'reconnects in 5 s', 'back off', 'Retry-After', 'never sooner', 'Yes, update rule'):
    assert part in cr, 'R3 connectedRule: ' + part
assert 'realtime.connectedRule' in c['realtime']['streamClose'], 'R3 streamClose points to connectedRule'
tot = c['adminListFilters']['total']
ask = tot['onlyWhenAsked']
for part in ('total=false', 'opens', 'filter', 'live event', 'keeps the number', 'absent or total=true', 'unknown_filter', 'v0.18.83', '"Yes (Rec.)"'):
    assert part in ask, 'P4-B onlyWhenAsked: ' + part
sb = c['adminListFilters']['scheduledBefore']
for part in ('GET /admin/trips', 'kind live', 'scheduledAt', 'at or before', 'late', 'Dashboard', '400 invalid_request', 'unknown_filter', 'Exact contract filter'):
    assert part in sb, 'A2 scheduledBefore: ' + part
spec = yaml.safe_load(open('openapi.yaml'))
P = spec['paths']
for r in SEVEN:
    d = P[r.split(' ', 1)[1]]['get']['description']
    assert 'v0.18.83' in d and 'server_busy' in d and 'shedPolls' in d, 'S2 openapi ' + r
assert 'never refused with server_busy' in P['/rider/trips/active']['get']['description'], 'S2 openapi active never shed'
for route in tot['lists']:
    ps = [p for p in P[route.split(' ', 1)[1]]['get']['parameters'] if p.get('name') == 'total']
    assert len(ps) == 1 and ps[0]['schema']['type'] == 'boolean' and ps[0]['schema'].get('default') is True, 'P4-B openapi total param ' + route
ps = [p for p in P['/admin/trips']['get']['parameters'] if p.get('name') == 'scheduledBefore']
assert len(ps) == 1 and ps[0]['schema'] == {'$ref': '#/components/schemas/Timestamp'} and 'scheduledAt' in ps[0]['description'], 'A2 openapi scheduledBefore'
md = open("CONTRACT.md").read(); ch = open("CHANGELOG.md").read()  # v0.18.101: the v0.18.83 note moved to CHANGELOG.md
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 83), 'CONTRACT.md title'
assert '\nv0.18.83 (G34 fix plan' in ch and '**busy-server fixes**' in ch and '`GET /rider/trips/active` is never refused' in ch and '`scheduledBefore`' in ch and '`total=false`' in ch, 'CONTRACT.md v0.18.83 note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.84 (S5 J7 debt model; owner Sitting 3 2026-11-12 Q-M1, Q-M2, Q-M4, Q-S5-1..5 + 2026-11-13 14:22/14:32 "150 DT ... admin can change",
# "ship OFF"): an unpaid rider fee is a negative wallet balance, read at payment (never copied into a quote or booking), max rider debt
# per country blocks only pay-in-car bookings; the driver owes-limit per country (TN 150 DT stored, OFF everywhere), admin owing list +
# "Driver paid Movera" correction; refund of a pay-in-car trip into the wallet first. Fixtures: fixtures/debt_model.json (reference_check.py).
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 84), 'version'
dm = c['debtModel']
for part in ('negative balance', 'WalletEntry kind fee', 'per currency', 'Rider.outstanding', 'outstandingByCurrency', 'rider_fees', 'history'):
    assert part in dm['riderWallet'], 'J7 riderWallet: ' + part
for part in ('never copied', 'POST /quotes', 'booked', 'reschedule', 'completed', 'ended early by the rider', 'ended by the driver with the rider on board',
             'admin complete', 'row lock', 'outstanding_fee', 'debt_paid', 'cashDue', 'not in his driverEarnings', 'once'):
    assert part in dm['readAtPayment'], 'J7 readAtPayment: ' + part
assert 'Quote.walletDebt' in dm['quoteInfo'] and 'not in Quote.total' in dm['quoteInfo'], 'J7 quoteInfo'
assert 'walletFirst' in dm['walletSwitch'] and 'ignored' in dm['walletSwitch'] and 'below 0' in dm['walletSwitch'], 'J7 walletSwitch'
for part in ('CountryRules.maxRiderDebt', 'at or above', 'pay in car', '409 conflict, reason rider_debt_above_max', 'card', 'apple_pay', 'wallet',
             'always saved', 'country standard'):
    assert part in dm['maxRiderDebt'], 'J7 maxRiderDebt: ' + part
cd = c['configDefaults']
assert cd['maxRiderDebt'] == {'SE': {'amountMinor': 30000, 'currency': 'SEK'}, 'FR': {'amountMinor': 3000, 'currency': 'EUR'},
                              'TN': {'amountMinor': 84000, 'currency': 'TND'}}, 'Q-S5-5 max rider debt SE 300 kr / FR 30 € / TN 84 DT'
fl = dm['dbFloor']
assert (fl['SEK'], fl['EUR'], fl['TND']) == (-90000, -9000, -252000) and 'never −max' in fl['note'] and 'not an admin setting' in fl['note'], 'Q-S5-3 DB floor'
for cur, cc in (('SEK', 'SE'), ('EUR', 'FR'), ('TND', 'TN')):
    assert fl[cur] == -3 * cd['maxRiderDebt'][cc]['amountMinor'], 'floor = 3 x default max ' + cur
for part in ('mark-paid', 'waive', 'reverse', 'adjustment', 'fee_on_running_trip', 'no longer'):
    assert part in dm['adminCorrections'], 'J7 adminCorrections: ' + part
for part in ('pay-in-car', 'wallet', 'transfer', 'lowers the debt', 'card'):
    assert part in dm['refunds'], 'Q-M4 refunds: ' + part
assert 'adding a card pays the debt' in dm['cardLater'], 'Q-M1 card later'
for part in ('Rider.outstanding', 'outstanding_fee', 'walletFirst', 'X-Contract-Version'):
    assert part in dm['oldApps'], 'J7 oldApps: ' + part
t = dm['texts']
assert t['quoteDebtLine']['en'] == '+ {amount} unpaid from an earlier trip, added when you pay', 'Q-S5-5 owner words'
for k in ('quoteDebtLine', 'riderDebtAboveMax', 'walletFee', 'walletDebtPaid', 'owesMoveraLine', 'paidMoveraLabel'):
    assert set(t[k]) == {'sv', 'fr', 'en'} and all(v.strip() for v in t[k].values()), 'J7 texts sv/fr/en ' + k
assert '{amount}' in t['quoteDebtLine']['sv'] and '{amount}' in t['quoteDebtLine']['fr'] and '{owed}' in t['owesMoveraLine']['en'] and '{limit}' in t['owesMoveraLine']['en'], 'J7 text slots'
assert 'Text batch' in dm['textsNote'], 'J7 wording goes to the text batch (Rule 45.8)'
# Q-S5-1 (a)+(b), owner 2026-11-13 14:22 / 14:32: per-country owes-limit, TN 150 DT stored, OFF everywhere.
do = dm['driverOwes']
for part in ('next payout', 'below 0', 'carried', 'commission', 'rider debt he collected', 'Driver paid Movera', 'per currency'):
    assert part in do['owed'], 'Q-S5-1 owed: ' + part
assert cd['driverOwesLimit'] == {'SE': {'enabled': False, 'max': None}, 'FR': {'enabled': False, 'max': None},
                                 'TN': {'enabled': False, 'max': {'amountMinor': 150000, 'currency': 'TND'}}}, 'Q-S5-1 OFF everywhere, TN 150 DT stored'
for part in ('CountryRules.driverOwesLimit', 'country standard', 'OFF', 'nobody is blocked', '150 DT', 'owes_limit_needs_amount', 'admin-changeable'):
    assert part in do['limit'], 'Q-S5-1 limit: ' + part
# Owner 2026-11-13 14:54 (decisions/session-2026-11-06.md, same rule as rider Q-S5-4): at or over the limit he is NOT refused online and
# keeps getting trips, but NO pay-in-car (cash) offers until he pays Movera; card / Apple Pay / wallet still come; at once, online or not.
assert 'goOnline' not in do, 'owner 14:54: no online refusal for the owes-limit'
co = do['cashOffers']
for part in ('at or above', 'NO offer', 'paymentMethod cash', 'card, apple_pay and wallet', 'never refused', 'at once', 'online or not',
             'current trip', 'finishes', 'withdrawn', 'driver_owes_movera', 'until he pays', 'switches it off', "14:54", 'Q-S5-4'):
    assert part in co, 'owner 14:54 cashOffers: ' + part
for part in ('owes_movera_over_limit', 'due_soon', 'not block', 'Home sheet', 'owed', 'limit', '0.18.84'):
    assert part in do['homeLine'], 'Q-S5-1 homeLine: ' + part
assert 'blocks_online' not in do['homeLine'] and 'blocks_online' not in c['driverOnboarding']['reminders']['kinds']['owes_movera_over_limit'], 'home line is a warning, not a block'
assert 'no cash trips until you pay Movera' in dm['texts']['owesMoveraLine']['en'] and 'go online' not in dm['texts']['owesMoveraLine']['en'], 'owner 14:54 home text (EN base)'
assert 'switch it on or off' in do['limit'] and 'change the amount' in do['limit'], 'owner 14:54: admin switch + amount, any time'
mr = dm['maxRiderDebt']
assert 'paymentMethod cash' in mr and 'card, apple_pay and wallet bookings stay allowed' in mr and 'at or above' in mr, 'rider rule Q-S5-4: only cash bookings blocked'
for part in ('GET /admin/drivers-owing', 'finance.read', 'zones', 'largest first', 'total'):
    assert part in do['adminList'], 'Q-S5-1 adminList: ' + part
for part in ('POST /admin/drivers/{driverId}/paid-movera', 'expectedOwed', 'reason', 'finance.edit', 'Idempotency-Key', 'audit driver.paid_movera',
             'paid_to_movera', '409 conflict, reason owed_changed', '400 invalid_request, reason paid_above_owed', 'never'):
    assert part in do['paidMovera'], 'Q-S5-1 paidMovera: ' + part
assert do['reasonMax'] == 300, 'reason max'
assert '14:54' in dm['answeredQuestions'][0], 'owner 14:54 answered the online question'
# Supervisor NO-GO on d5fcd98 (audits/impact/contracts-0.18.84-s5j7-supervisor.md) M2-M5 + Q3.
# Owner answers 2026-11-13 14:59 (Q1 owed), 15:00 (Q2 'Any amount': no admin cap, floor follows the setting), 15:01 (Q3 'He keeps it').
assert dm['openQuestions'] == [], 'all J7 owner questions answered'
aq = ' | '.join(dm['answeredQuestions'])
assert all(t in aq for t in ('14:54', '14:59', '15:00', '15:01')), 'answered questions recorded'
assert '14:59' in do['owed'] and 'What he owes Movera' in do['owed'], 'Q1 owed is an owner decision'
wf = c['afterTestRules']['walletFirst']['rule']
assert 'walletApplied = max(0, min(balance' in wf and 'a negative balance pays nothing' in wf, 'M2 walletApplied never negative'
ch = dm['changeover']
for part in ('before server J8', 'copied outstanding_fee line', 'dropped', 'read from the wallet', 'paid once', '0103'):
    assert part in ch, 'M3 changeover: ' + part
assert 'maxRiderDebtCap' not in dm and 'max_rider_debt_too_high' not in json.dumps(c, ensure_ascii=False), 'Q2 Any amount: no admin cap'
for part in ('follows the admin setting', '3 × the current max', 'same transaction', '0102', 'always saved', '15:00'):
    assert part in fl['note'], 'Q2 floor follows the setting: ' + part
# Supervisor round 2 (R2-1..R2-4, audits/impact/contracts-0.18.84-s5j7-supervisor.md): the floor only moves down, with room for 4 fees.
for part in ('only ever moves DOWN', 'max + 4 × the largest cancel or no-show fee', 'when Max rider debt or a cancel / no-show fee setting is saved', 'never raises it'):
    assert part in fl['note'], 'R2-1 floor headroom: ' + part
assert 'never above the lowest' not in fl['note'], 'R2-2 the floor is never set ON a balance'
ffm = json.load(open('fixtures/debt_model.json'))['floorFollowsMax']
assert all('saved' in x['expect'] for x in ffm) and not any(x['id'] == 'tn_lowered_never_above_lowest' for x in ffm), 'R2-2 every floor case checks the fee is saved'
assert any(x['id'] == 'se_max_20kr_rider_19kr_noshow_65kr' and x['expect']['saved'] is True for x in ffm), 'R2-2 the 20 kr / -19 kr / 65 kr case'
assert 'never more' not in dm['changeover'] and 'the copied amount is never charged on top' in dm['changeover'], 'R2-3 changeover: no false cap'
assert any(x['id'] == 'wallet_debt_bigger_than_copied_line' for x in json.load(open('fixtures/debt_model.json'))['changeover']), 'R2-3 fixture'
mg = dm['migrations']
assert 'dbFloor CHECK added' not in mg and 'floor table' in mg and 'only moves down' in mg and 'locks the floor row' in mg, 'R2-4 migrations 0102 matches the floor'
assert 'no upper bound' in dm['maxRiderDebt'] and '15:00' in dm['maxRiderDebt'], 'Q2 maxRiderDebt any amount'
assert 'he keeps' in co and '15:01' in co and 'pending owner Q3' not in co, 'Q3 owner decision: accepted booked cash rides stay'
# old rule texts superseded, not left contradicting
of = c['outstandingFee']
assert not any(r.startswith('every quote and the fare of the next trip carry outstanding_fee') for r in of['rules']), 'old quote-carries rule replaced'
assert 'v0.18.84' in of['note'] and 'debtModel' in of['note'] and 'fee_on_running_trip' in of['adminMarkPaid']['note'] and 'v0.18.84' in of['adminMarkPaid']['note'], 'outstandingFee points at debtModel'
assert 'v0.18.84' in c['pickupWaiting']['debtByCurrency']['note'] and 'v0.18.84' in c['walletCredit']['note'], 'J7 old notes updated'
assert 'owes_movera_limit' not in json.dumps(c, ensure_ascii=False), 'no owes_movera_limit refusal left in contract.json'
for r in ('rider_debt_above_max', 'driver_owes_movera', 'owed_changed', 'paid_above_owed', 'owes_limit_needs_amount'):
    assert r in c['errors']['reason'], 'J7 Error.reason ' + r
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']; P = spec['paths']
assert {'fee', 'debt_paid'} <= set(S['WalletEntry']['properties']['kind']['enum']), 'openapi WalletEntry kinds'
assert 'may be below 0' in S['Wallet']['properties']['balance']['description'], 'openapi Wallet.balance negative'
assert S['Quote']['properties']['walletDebt']['allOf'] == [{'$ref': '#/components/schemas/Money'}], 'openapi Quote.walletDebt'
assert S['CountryRules']['properties']['maxRiderDebt']['allOf'] == [{'$ref': '#/components/schemas/Money'}], 'openapi maxRiderDebt'
ol = S['DriverOwesLimit']
assert set(ol['properties']) == {'enabled', 'max'} and ol['properties']['enabled']['default'] is False, 'openapi DriverOwesLimit OFF'
assert S['CountryRules']['properties']['driverOwesLimit'] == {'$ref': '#/components/schemas/DriverOwesLimit'}, 'openapi CountryRules.driverOwesLimit'
assert 'rider_debt_above_max' in P['/trips']['post']['responses']['409']['description'], 'openapi POST /trips 409'
assert 'owes_movera_limit' not in open('openapi.yaml').read() and 'owes' not in P['/driver/availability']['post']['description'], 'openapi: going online is never refused for the owes-limit'
assert 'driver_owes_movera' in P['/admin/trips/{tripId}/assign']['post']['responses']['409']['description'] and 'no cash' in S['DriverOwesLimit']['description'], 'openapi no cash offers'
assert 'owes_movera_over_limit' in S['DriverReminder']['properties']['kind']['enum'] and {'owed', 'limit'} <= set(S['DriverReminder']['properties']), 'openapi reminder'
g = P['/admin/drivers-owing']['get']
assert g['x-permission'] == 'finance.read' and g['responses']['200']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/OwingDriverList'}, 'openapi owing list'
pm = P['/admin/drivers/{driverId}/paid-movera']['post']
assert pm['x-permission'] == 'finance.edit' and pm['requestBody']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/PaidMoveraCommand'}, 'openapi paid-movera'
assert set(S['PaidMoveraCommand']['required']) == {'expectedOwed', 'amount', 'reason'} and 'owed_changed' in pm['responses']['409']['description'], 'openapi paid-movera body/409'
assert {'driverId', 'owed', 'limit', 'overLimit'} <= set(S['OwingDriver']['properties']), 'openapi OwingDriver'
assert 'paid_to_movera' in S['PayoutLine']['properties']['code']['enum'], 'openapi payout line'
assert 'v0.18.84' in P['/admin/riders/{riderId}/fees/{tripId}/mark-paid']['post']['description'] and 'v0.18.84' in P['/quotes']['post']['description'], 'openapi mark-paid / quotes'
md = open('CONTRACT.md').read()
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 84), 'CONTRACT.md title'
mdc = md + open('CHANGELOG.md').read(); assert '\nv0.18.84 (S5 J7 debt model' in mdc and '**an unpaid fee is a negative wallet balance, read when the trip is paid**' in mdc, 'CONTRACT.md v0.18.84 note'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
assert 'while the rider owes one, the `outstanding_fee` line is added after the rounding; `Quote.total` and `fare` include it' not in md, 'CONTRACT.md §3.5 step 8 rewritten'
assert 'While it is open, every quote and the next trip carry it' not in md and 'v0.18.84 (`debtModel.readAtPayment`' in md, 'CONTRACT.md §3.7 rewritten'
assert '`walletApplied = max(0, min(balance in the trip\'s currency, fare))`' in md, 'M2 CONTRACT.md walletApplied'
assert 'follows the admin setting' in S['CountryRules']['properties']['maxRiderDebt']['description'] and 'max(0, min(' in S['CreateTripRequest']['properties']['walletFirst']['description'], 'M2/Q2 openapi'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.85 (audit A1; owner 2026-11-02 "Show price incl. fee (Recommended)", Rules decisions/driver-g6.md:96): the waiting
# prices shown with the app fee; the fare rule, fare fixtures and moneyBase.commission unchanged.
python3 - <<'PY'
import json, yaml
from fractions import Fraction
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 85), 'version'
w = c['waitingPriceShown']
for k in ('note', 'rule', 'charge', 'fields', 'apps', 'money', 'texts'):
    assert k in w, 'waitingPriceShown.' + k
assert 'driver-g6.md:96' in w['note'] and 'Show price incl. fee' in w['note'], 'owner words'
assert 'appFeePct' in c['bookingSnapshot']['fields'], 'snapshot keeps appFeePct'
def shown(minor, pct):
    x = Fraction(minor) * (1 + Fraction(pct) / 100)
    return (x + Fraction(1, 2)).__floor__()
# The rule's examples (SEK, EUR, TND minor units) and the SE defaults.
assert [shown(1226, 10), shown(1690, 12), shown(500, 10), shown(50, 10), shown(250, 10)] == [1349, 1893, 550, 55, 275]
for t in ('13,49 kr', '18,93 kr', '5,50 kr', '0,55 €', '0.275 DT'):
    assert t in w['rule'], t
se = c['configDefaults']['pricing']['countries']['SE']['categories']
assert shown(se['economy']['waitPerMin'], se['economy']['appFeePct']) == 1349
spec = yaml.safe_load(open('openapi.yaml'))['components']['schemas']
for s_, k in (('TripTerms', 'waitPerMinShown'), ('TripTerms', 'stopWaitPerMinShown'), ('RiderWaiting', 'perMinShown'), ('CategoryWaiting', 'perMinShown')):
    assert k in spec[s_]['properties'], s_ + '.' + k
assert 'waitPerMinShown' not in spec['TripTerms'].get('required', []), 'additive'
md = open('CONTRACT.md').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md heading'
mdc = md + open('CHANGELOG.md', encoding='utf-8').read(); assert 'v0.18.85' in mdc and 'waitPerMinShown' in mdc, 'CONTRACT.md text'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.86 (J5b; owner 2026-11-13 ~20:41 UTC "Admin can set commission even by amount !" + ~20:48 "Yes, like this (Rec.)",
# ~21:40 placement + "Yes, warn (Rec.)", ~22:46 calculator; times from the Rules commit log; Rules decisions/session-2026-11-06.md): commission steps
# per zone and car type, % or fixed, picked by the commission base; edited in each car-type card; advisory warning.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 86), 'version'
cs = c['commissionSteps']
for k in ('note', 'field', 'pick', 'money', 'where', 'noSteps', 'example', 'validation', 'adminPlacement', 'warn', 'adminCalculator', 'apps', 'texts', 'textsNote'):
    assert k in cs, 'commissionSteps.' + k
assert 'Yes, like this (Rec.)' in cs['note'] and 'even by amount' in cs['note'], 'owner words'
assert "never by the driver's gain" in cs['pick'] and 'min(amountMinor, base)' in cs['pick'], 'pick rule'
assert 'NOT a shipped default' in cs['example'], 'TN example is not a default'
assert '~21:00' not in cs['note'] and '~21:05' not in cs['note'] and '20:41' in cs['note'] and '20:48' in cs['note'] and '21:40' in cs['note'], 'owner times (commit log)'
assert 'Commission panel' in cs['adminPlacement'] and 'EACH car-type card' in cs['adminPlacement'] and 'NEVER a global' in cs['adminPlacement'], 'placement'
assert 'Commission panel' in cs['apps']['admin'] and 'never global' in cs['apps']['admin'], 'apps.admin placement'
AC = cs['adminCalculator']
assert 'EACH car-type card' in AC['rule'] and 'not moneyBase.commission' in AC['rule'] and '22:46' in cs['note'] and '23:05' not in json.dumps(cs, ensure_ascii=False) and '22:00' not in cs['note'], 'calculator'
assert 'reproduce fixtures/commission_steps.json exactly' in AC['fixtures'] and 'J5b admin build must run a test' in AC['fixtures'], 'calculator fixtures'
assert {'title', 'priceInput', 'driverGets'} <= set(cs['texts']['calculator']), 'calculator texts (v0.18.88: moveraKeeps, aroundLimits, atLimit, justAbove, stepUsed, commission removed)'
for tt in cs['texts']['calculator'].values(): assert set(tt) == {'sv', 'fr', 'en'} and all(tt.values()), 'calculator texts sv/fr/en'
W = cs['warn']
assert 'driverRidePart(L, step i) > driverRidePart(L + 1, step i+1)' in W['rule'] and 'Yes, warn (Rec.)' in W['rule'], 'warn rule'
assert 'STILL ALLOWS SAVING' in W['advisory'] and 'server does NOT refuse' in W['advisory'], 'warn is advisory'
assert '5.000 DT → driver 4.500 DT' in W['example'] and '5.001 DT → driver 3.751 DT' in W['example'], 'owner warn example'
assert all('{limit}' in v and '{atLimit}' in v and '{justAbove}' in v for v in cs['texts']['warnDrop'].values()), 'warnDrop placeholders'
assert 'warn' not in str(cs['validation']['problems']) and 'warn' not in str(c['errors']['reason']).lower(), 'no server warn code'
V = cs['validation']
assert 'commission_steps_invalid' in V['rule'] and 'commission_steps_invalid' in c['errors']['reason'], 'reason'
for t in cs['texts'].values():
    for tt in (t.values() if 'en' not in t else [t]):
        assert set(tt) == {'sv', 'fr', 'en'} and all(tt.values()), 'texts sv/fr/en'
assert set(cs['texts']['errors']) == set(V['problems']), 'one admin text per problem'
assert "commissionSteps" in c['pricing']['moneySplit']['driverEarnings'] and 'max(0,' in c['pricing']['moneySplit']['driverEarnings'], 'driverEarnings formula'
for cid, row in c['configDefaults']['pricing']['countries']['SE']['categories'].items():
    ks = list(row)
    assert row['commissionSteps'] == [] and ks.index('commissionSteps') == ks.index('commissionPct') + 1, 'defaults: [] beside commissionPct ' + cid
fx = json.load(open('fixtures/commission_steps.json'))
assert {x['id'] for x in fx['pick']} >= {'tn_up_to_5_fixed', 'tn_fixed_capped_by_base', 'tn_half_up_tie', 'tn_above', 'no_steps_is_commission_pct'}, 'cases'
assert {x['expect']['problem'] for x in fx['validate'] if x['expect'] != 'ok'} == set(V['problems']), 'a case per problem'
wx = {x['id']: x for x in fx['warn']}
assert wx['owner_warn_example']['expect'] == [{'step': 0, 'upToMinor': 5000, 'atLimit': 4500, 'justAbove': 3751}], 'owner warn case'
assert wx['small_pct_rise_rounds_equal']['expect'] == [] and len(wx['two_warnings_pct_to_fixed_to_pct']['expect']) == 2 and 'Any step with a higher %' not in W['example'], 'warn cases'
assert wx['equal_is_no_warn']['expect'] == [] and 'tn_fraction_just_above_5' in {x['id'] for x in fx['pick']}, 'warn/exact cases'
fares = {x['id']: x for x in json.load(open('fixtures/fares.json'))['cases']}
assert fares['commission_steps_empty_is_pct']['expect'] == fares['economy_plain']['expect'], 'no steps = v0.18.85'
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']
st = S['CommissionStep']
assert st['additionalProperties'] is False and st['required'] == ['upToMinor'] and len(st['oneOf']) == 2, 'CommissionStep'
assert 'commissionSteps' in S['CategoryPricing']['properties'] and 'commissionSteps' not in S['CategoryPricing']['required'], 'additive'
assert S['CategoryPricing']['properties']['commissionSteps']['oneOf'][0]['maxItems'] == V['maxSteps']
for m, p in (('put', '/admin/config/{doc}'), ('post', '/admin/config/{doc}/publish')):
    assert 'commission_steps_invalid' in P[p][m]['responses']['400']['description'], p
md = open('CONTRACT.md').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'CONTRACT.md heading'
mdc = md + open('CHANGELOG.md', encoding='utf-8').read(); assert 'v0.18.86' in mdc and 'commissionSteps' in mdc and 'commission_steps_invalid' in mdc, 'CONTRACT.md text'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.87 (BQ-M19, owner 107 + approved B2.4 plan; owner 2026-11-13 "Movera commission is how much movera keep"): bonus
# entries outside a trip's commission (lost-driver payment, admin bonus after the paid end) are Movera pay changes, taken
# off moveraEarnings once; an admin bonus on a completed trip never rewrites the commission. takeBack: FOR NO KEY UPDATE (#218).
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
mb, km = c['moneyBase'], c['kpis']['money']
bo = mb['bonusOutsideCommission']
assert set(bo['which']) == {'lostDriver', 'afterPaidEnd'} and 'NOT a pay change' in bo['inside'], 'BQ-M19 which/inside'
me = km['moveraEarnings']
assert me.startswith('v0.18.82') and 'v0.18.87' in me and 'payLostDriver' in me and 'after the trip' in me and 'taken off once' in me, 'BQ-M19 moveraEarnings'
assert 'bonusOutsideCommission' in mb['kpiMoney'] and 'never rewritten by it' in mb['commission'] and mb['commission'].startswith('B2.4 (S07 M5)'), 'BQ-M19 commission/kpiMoney'
assert list(mb).index('bonusOutsideCommission') == list(mb).index('kpiMoney') + 1, 'BQ-M19 key order'
tb = c['bookedTakeBack']['takeBack']
assert '(FOR NO KEY UPDATE' in tb and '(FOR UPDATE)' not in tb, 'takeBack lock wording'
spec = yaml.safe_load(open('openapi.yaml'))
assert 'payLostDriver' in spec['components']['schemas']['KpiDay']['properties']['moveraEarnings']['description'], 'openapi KpiDay.moveraEarnings'
md = open('CONTRACT.md').read()
mdc = md + open('CHANGELOG.md', encoding='utf-8').read(); assert '\nv0.18.87 (BQ-M19' in mdc and 'moneyBase.bonusOutsideCommission' in mdc, 'CONTRACT.md v0.18.87 note'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
cr = mb['commissionRow']
assert '23:42 UTC' in cr['note'] and 'how much movera keep' in cr['note'] and 'never rewritten' in cr['note'], 'commissionRow owner quote'
assert 'moneySplit.movera' in cr['admin'] and 'moveraKeepsNow' in cr['driver'] and 'never TripProjection.commission' in cr['driver'], 'commissionRow admin/driver'
assert 'moneyBase.commissionRow' in mb['commission'] and 'moveraKeepsNow' in spec['components']['schemas']['TripProjection']['properties'], 'commissionRow commission/openapi'
assert 'moveraKeepsNow' not in spec['components']['schemas']['TripProjection'].get('required', []), 'moveraKeepsNow additive'
qs = [v for v in json.dumps(c, ensure_ascii=False).split('"serverSafety": ')[1:] if v.startswith('"Rule 33: the queued trip starts')]
assert len(qs) == 1 and '(FOR UPDATE)' in qs[0].split('",')[0], 'queued-trip start lock wording (money.ts FOR UPDATE, not changed by #218)'
bo = mb['bonusOutsideCommission']
assert 'never by when an entry was written' in bo['inside'] and 'fare − debtCollected − driverEarnings − pickupPay − commission' in bo['inside'] and 'every bonus entry is outside' in bo['inside'], 'inside rule'
assert 'created_at' not in bo['server'] and 'tells apart' not in bo['server'] and 'Driver and rider: no change' not in bo['apps'], 'server/apps text'
assert 'bonus being typed' in cr['admin'] and 'waybill row is hidden too' in cr['driver'] and 'every driver and admin screen use this same number' not in mb['commission'], 'box/waybill/commission'
mdc = md + open('CHANGELOG.md', encoding='utf-8').read(); assert 'moveraKeepsNow' in mdc, 'CONTRACT.md commission row'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.88 (owner 2026-10-29 "Movera dont care about what fleet owner take from drivers! ... if there is any % u delete that",
# owner 2026-11-14 ~02:49 UTC "What the fuck is fleet owner keep !??? And why its complicate ?!"): no fleet-owner % anywhere
# (fleetCommissionPct removed, ignored; fleet payouts = the whole driver earnings) and ONE simple commission calculator.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 88), 'version'
fp = c['fleetPayoutWhole']
assert 'Movera dont care about what fleet owner take from drivers' in fp['note'] and 'fleet owner keep' in fp['note'] and 'driver-g10.md:3' in fp['note'], 'owner quotes'
assert 'REMOVED (v0.18.13), IGNORED' in fp['pricing'] and 'never reads it for any money' in fp['pricing'], 'removed, ignored'
assert 'the whole driver earnings' in fp['payouts'] and 'paid to the fleet owner' in fp['payouts'] and 'outside Movera' in fp['payouts'], 'fleet payout whole'
assert list(c).index('fleetPayoutWhole') == list(c).index('fleetShareRemoved') + 1 and c['fleetShareRemoved'].startswith('v0.18.13'), 'key order, old note kept'
assert 'fleetCommissionPct' not in json.dumps(c['configDefaults']) and 'fleetCommissionPct' not in json.load(open('fixtures/config/pricing_document.json')), 'no fleet % in defaults / sample'
assert not any('fleet' in l for l in c['payouts']['lines']) and 'fleet' not in json.dumps(c['payouts']['schedule']['default']), 'no fleet payout line'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert 'fleetCommissionPct' not in S['PricingDocument']['properties'] and S['PricingDocument'].get('additionalProperties') is not False, 'old key accepted, not in the schema'
ac = c['commissionSteps']['adminCalculator']
assert set(ac) == {'rule', 'formula', 'removed', 'steps', 'fixtures'} and 'aroundLimits' not in ac, 'calculator keys'
assert 'ONLY one price input and exactly two result lines, AMOUNTS ONLY' in ac['rule'] and 'no rows around the limits' in ac['rule'] and 'why its complicate' in ac['rule'] and 'dont write any percentage' in ac['rule'], 'one calculator, amounts only'
assert 'REMOVED' in ac['removed'] and 'warn.rule and texts.warnDrop' in ac['removed'], 'removed + warn kept'
assert 'capNote' not in c['commissionSteps']['texts'] and 'already minimum trip price' in ac['removed'] and 'min(amountMinor, base)' in c['commissionSteps']['pick'], 'no cap note, cap kept'
assert 'Yes add app fee in same card' in ac['rule'] and 'appFeePct' in ac['rule'] and 'Movera gets <amount>' in ac['rule'] and 'SAME value as Pricing › Limits › App fee' in c['commissionSteps']['adminPlacement'], 'app fee in the card'
tc = c['commissionSteps']['texts']['calculator']
assert not ({'moveraKeeps', 'aroundLimits', 'atLimit', 'justAbove', 'stepUsed', 'commission'} & set(tc)) and {'title', 'priceInput', 'noStepsPct', 'driverGets', 'moveraGets', 'waitingNote'} == set(tc), 'calculator texts'
assert 'warnDrop' in c['commissionSteps']['texts'] and 'STILL ALLOWS SAVING' in c['commissionSteps']['warn']['advisory'], 'warn kept'
assert 'ONE calculator' in c['commissionSteps']['apps']['admin'] and 'Movera gets' in c['commissionSteps']['apps']['admin'] and 'rows around each limit' not in c['commissionSteps']['apps']['admin'], 'apps.admin'
md = open('CONTRACT.md').read()
mdc = md + open('CHANGELOG.md', encoding='utf-8').read(); assert '\nv0.18.88 (owner 2026-10-29' in mdc and 'fleetPayoutWhole' in mdc and 'adminCalculator.removed' in mdc, 'CONTRACT.md v0.18.88 note'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.89 (owner 2026-11-14 "make sure rider and driver app show correct prices every where" + "Check all apps"; Rules
# audits/price-display-2026-11-14/REPORT.md): price fields from the server; payouts 2 lines (Driver gets / Movera gets); whole amounts keep decimals.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
pd = c['priceDisplay']
assert 'never work money out' in pd['note'] and 'driverEarnings + pickupPay' in pd['offer']['driverTotal'] and 'ONLY this number' in pd['offer']['driverTotal'], 'Offer.driverTotal'
assert 'never works pickup pay out' in pd['offer']['pickupPay'] and 'walletApplied' in pd['offer']['cashToCollect'], 'offer pickupPay / cashToCollect'
assert 'driverEarnings + pickupPay + driverBonus' in pd['routeChange'] and 'feeNow' in pd['cancelPreview']['shape'] and 'cancel_fee.dart' in pd['cancelPreview']['apps'], 'routeChange / cancelPreview'
assert '− finish.driverTotal' in pd['owedToMovera'] and 'cash_balance.dart' in pd['owedToMovera'], 'owedToMovera'
ps = pd['payoutSummary']
assert 'thats all no details' in ps['owner'] and 'all trips' in ps['rule'] and 'commissionRow' in ps['rule'] and 'never do' in ps['rule'], 'payoutSummary 2 lines'
assert ps['display'].startswith('Exactly two lines') and 'No other detail' in ps['display'], 'payout card no details'
assert 'PLUS the app fee' in ps['rule'] and 'never added a second time' in ps['rule'] and 'session-2026-11-06.md:1278' in ps['rule'] and 'never a %' in ps['display'], 'Movera gets = commission + app fee, no %'
assert 'amounts only, never a %' in c['moneyDisplay']['resultLinesNoPercent'] and 'session-2026-11-06.md:1278' in c['moneyDisplay']['resultLinesNoPercent'] and ps['ruleBefore0_18_89b'].startswith('Replaced'), 'result lines no %'
assert {k: ps['texts'][k] for k in ('driverGets', 'moveraGets')} == {'driverGets': {'sv': 'Föraren får', 'fr': 'Le chauffeur reçoit', 'en': 'Driver gets'}, 'moveraGets': {'sv': 'Movera får', 'fr': 'Movera reçoit', 'en': 'Movera gets'}}, 'payout texts'
assert 'Three separate lines' in pd['payoutSummaryBefore0_18_89']['display'] and 'Earnings / Owed to Movera / Paid out' in c['payouts']['noteBefore0_18_89'], 'old 3-line text kept (Rule 21)'
pn = c['payouts']['note']
assert 'v0.18.89' in pn and 'Driver gets /' in pn and 'Movera gets' in pn and 'Owed to Movera' not in pn and 'is replaced' in pn, 'payouts.note 2 lines'
tm = c['arrivedWaiting']['termsTexts']['money']
assert 'follows the currency, not the' in tm and "'65,00 kr'" in tm and "'5.000 DT'" in tm and 'driver-g6.md:96' in tm and "'13,49 kr'" in tm, 'termsTexts.money'
assert c['arrivedWaiting']['termsTexts']['moneyBefore0_18_89'].startswith('Replaced in v0.18.89'), 'old termsTexts.money kept'
md = c['moneyDisplay']
assert 'owner 2026-11-14' in md['wholeAmounts'] and 'every server text' in md['wholeAmounts'] and 'every app' in md['wholeAmounts'], 'wholeAmounts'
assert md['examplesWhole'] == {'SEK': {'3500': '35,00 kr'}, 'EUR': {'800': '8,00 €'}, 'TND': {'5000': '5.000 DT'}}, 'whole examples'
assert 'legalTerms' in c['waitingPriceShown'], 'Terms shown waiting price'
S = yaml.safe_load(open('openapi.yaml'))['components']['schemas']
for sch, f in (('Offer', 'driverTotal'), ('Offer', 'cashToCollect'), ('TripRouteChange', 'driverTotal'), ('TripProjection', 'cancelPreview'),
               ('TripProjection', 'cashToCollect'), ('TripFinish', 'owedToMovera'), ('Payout', 'summary')):
    assert f in S[sch]['properties'] and f not in S[sch].get('required', []), sch + '.' + f + ' additive'
assert S['CancelPreview']['required'] == ['feeNow', 'kind'] and S['PayoutSummary']['required'] == ['driverGets', 'moveraGets'], 'new schemas'
assert 'only the total' not in S['Payout']['properties']['lines']['description'], 'Payout.lines 2 lines'
assert '3 lines' not in S['Payout']['properties']['summary']['description'] and 'the 2 lines Driver gets / Movera gets' in S['Payout']['properties']['summary']['description'], 'Payout.summary 2 lines'
assert S['CancelPreview']['properties']['kindAfterFree']['enum'] == ['cancel', 'no_show'] and 'kindAfterFree' not in S['CancelPreview']['required'] and 'kindAfterFree is no_show' in pd['cancelPreview']['rule'], 'cancelPreview.kindAfterFree additive'
assert 'never added again' in pd['payoutSummary']['rule'] and 'tips, a later bonus' not in pd['payoutSummary']['rule'], 'driverGets: no tip / bonus added twice'
assert 'The admin sees the lines" is replaced' in c['payouts']['note'] and 'session-2026-11-06.md:1277' in c['payouts']['note'], 'payouts.note admin lines replaced'
assert 'tip, later pay change' in pd['offer']['driverTotal'], 'offer driverTotal no tip'
t = open('CONTRACT.md', encoding='utf-8').read()
assert '## 90. Prices the apps show' in t and '`fare + pickupPay`' not in t and 'Offer.driverTotal' in t, 'CONTRACT.md §90 / §3.2'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.90 BQ-M21 (owner 2026-11-13 23:42 UTC "Movera commission is how much movera keep", Rules decisions/session-2026-11-06.md:1263):
# on a reassigned trip the lost driver's payment is taken off moneySplit.movera / the admin view's moveraKeepsNow.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
mb = c['moneyBase']
ld = mb['lostDriverPaid']
assert 'session-2026-11-06.md:1263' in ld['note'] and 'REASSIGNED' in ld['note'], 'lostDriverPaid note'
assert '/reassign and /cancel' in ld['rule'] and 'however many times' in ld['rule'] and 'riderPaid − driverTotal − debtCollected − lostDriverPaid' in ld['rule'], 'lostDriverPaid rule'
assert 'never sent to him' in ld['driverView'] and 'hideDriverMoney' in ld['driverView'] and 'kept as is' in ld['driverView'] and ld['driverViewBefore0_18_90b'].startswith('Replaced'), 'driver view keeps his own trip (GM: kept)'
assert 'admin audit rows trip.reassign / trip.cancel' in ld['server'] and 'without a transaction' in ld['server'] and 'got the trip back' in ld['server'] and ld['serverBefore0_18_90b'].startswith('Replaced'), 'lostDriverPaid backfill source'
assert 'Not taken off twice' in ld['kpi'] and 'never reads moneySplit' in ld['kpi'] and 'payoutSummary' in ld['kpi'], 'KPI once'
assert '20,00 kr' in ld['example'] and '2.000 DT' in ld['example'], 'SEK + TND example'
cr = mb['commissionRow']
assert '− lostDriverPaid' in cr['number'] and cr['numberBefore0_18_90'].startswith('Replaced in v0.18.90'), 'commissionRow.number'
assert 'v0.18.90' in cr['admin'] and 'v0.18.90 driver view' in cr['driver'] and cr['driverBefore0_18_90'].startswith('Replaced'), 'commissionRow admin / driver'
assert 'GREATEST(0, LEAST(entries, entries − inside))' in mb['bonusOutsideCommission']['server'] and 'logs a warning' in mb['bonusOutsideCommission']['server'], 'M19 clamp stated'
fd = c['finish']['debt']
assert 'driverTotal + movera + debtCollected + lostDriverPaid = riderPaid always' in fd['moneySplit'] and fd['moneySplitBefore0_18_90'].startswith('Replaced'), 'moneySplit sum'
assert set(fd['texts']['lostDriverLine']) == {'sv', 'fr', 'en'}, 'lostDriverLine sv/fr/en'
S = yaml.safe_load(open('openapi.yaml'))['components']['schemas']
assert 'lostDriverPaid' in S['MoneySplit']['properties'] and 'lostDriverPaid' not in S['MoneySplit']['required'], 'MoneySplit.lostDriverPaid additive'
assert '− lostDriverPaid' in S['TripProjection']['properties']['moveraKeepsNow']['description'], 'moveraKeepsNow description'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read(); assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.90 (BQ-M21' in tc and 'lostDriverPaid? }' in tc, 'CONTRACT.md v0.18.90'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
pd = c['priceDisplay']
assert 'cash the driver holds' in pd['owedToMovera'] and 'plus a cash tip' in pd['owedToMovera'] and 'fare − walletApplied' in pd['owedToMovera'] and pd['owedToMoveraBefore0_18_90'].startswith('Replaced in v0.18.90'), 'owedToMovera cash held (P89 must-fix 1)'
assert "'counted as cash the driver already holds'" in pd['owedToMovera'] and 'counted as cash the driver already holds' in S['TripTip']['properties']['driverShare']['description'], 'owedToMovera matches TripTip.driverShare'
aw = json.load(open('fixtures/arrived_waiting.json'))
assert [x['text'] for x in aw['termsMoney']] == ['12,26 kr', '65,00 kr', '0,50 €', '8,10 €', '8,00 €', '12,26 kr', '5.000 DT'] and 'N4' in aw['termsMoneyNote'], 'termsMoney fixture follows moneyDisplay (P89 N4)'
assert '`TripFinish.owedToMovera` = cash the driver holds' in t, 'CONTRACT.md §90 owedToMovera'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
# v0.18.92 (GM 2026-11-14, owner rule s06:1263; server BQ-M24): TripProjection.lostDriverPaid on the admin view of every trip.
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 92), 'version'
tc = t + open('CHANGELOG.md', encoding='utf-8').read(); assert '\nv0.18.92 (GM 2026-11-14' in tc and '`TripProjection.lostDriverPaid`' in tc, 'CONTRACT.md v0.18.92 note'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
cr2 = c['moneyBase']['commissionRow']; ld2 = c['moneyBase']['lostDriverPaid']
assert 'commission − TripProjection.lostDriverPaid' in cr2['admin'] and 'ONE server number' in cr2['admin'] and 'the admin never adds or subtracts' in cr2['admin'] and 'keep no quoted pay' in cr2['admin'] and cr2['adminBefore0_18_92'].startswith('Replaced in v0.18.92'), 'commissionRow.admin unpaid rows (G1)'
assert 'ADMIN view only' in ld2['tripField'] and 'paid or not' in ld2['tripField'] and 'equals moneySplit.lostDriverPaid' in ld2['tripField'], 'lostDriverPaid.tripField'
assert 'only on a paid trip end' in ld2['unpaid'] and ld2['appsBefore0_18_92'].startswith('Replaced in v0.18.92'), 'lostDriverPaid.unpaid / apps'
assert 'lostDriverPaid' in S['TripProjection']['properties'] and 'lostDriverPaid' not in S['TripProjection'].get('required', []), 'TripProjection.lostDriverPaid additive'
ps2 = c['priceDisplay']['payoutSummary']
assert "the payout's OWN entries" in ps2['rule'] and 'The two views may differ' in ps2['rule'] and ps2['ruleBefore0_18_92'].startswith('Replaced in v0.18.92'), 'payoutSummary own entries / views (MF1, MF2)'
assert 'migration 0108' in ps2['index0_18_92'] and 'ADMIN view' in cr2['fieldAdmin0_18_92'] and 'still under way' in cr2['fieldAdmin0_18_92'], 'payout index / admin moveraKeepsNow on an unpaid end'
assert "the payout's OWN entries" in S['PayoutSummary']['description'] and cr2['fieldAdmin0_18_92'] in S['TripProjection']['properties']['moveraKeepsNow']['description'], 'openapi follows'
tc = t + open('CHANGELOG.md', encoding='utf-8').read(); assert '**Payout.summary = the payout\'s own entries**' in tc, 'CONTRACT.md v0.18.92 payout line'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
# v0.18.95 (server BQ-M26; M24 supervisor N1): a paid payout's summary is frozen when it is marked paid.
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 95), 'version'
fz = c['priceDisplay']['payoutSummary']['frozenWhenPaid']
assert fz.startswith('v0.18.95') and 'marks the payout paid' in fz and 'never moves a paid payout' in fz and 'stays live' in fz and 'freeze at deploy' in fz and 'migration 0109' in fz, 'payoutSummary.frozenWhenPaid'
tc = t + open('CHANGELOG.md', encoding='utf-8').read(); assert '\nv0.18.95 (server BQ-M26' in tc and '**a paid payout\'s summary is frozen**' in tc and 'payoutSummary.frozenWhenPaid' in tc, 'CONTRACT.md v0.18.95 note'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
assert fz in S['PayoutSummary']['description'], 'openapi PayoutSummary follows frozenWhenPaid'
PY
# v0.18.91 job A7 (owner 2026-11-02 "taken from the driver's NEXT payout (driver sees why)", Rules decisions/driver-g8.md:95-98;
# Q-M4 decisions/session-2026-11-06.md:1102) + job C8 (owner "Anything admin can adjust becomes an admin setting"):
# the driver gets a bell + push when a refund is taken from his earnings; the cash-tip time in the car is an admin setting.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 91), 'version 0.18.91 or later'
dn = c['finish']['refund']['driverNotice']
assert dn['kind'] == 'driver_refund_taken' and dn['deepLink'] == 'movera-driver://trips/{tripId}', 'driverNotice kind / link'
assert 'driver-g8.md:95-98' in dn['note'] and 'audience driver' in dn['rule'] and 'share taken from him' in dn['rule'], 'driverNotice note / rule'
assert 'noticeLanguage' in dn['rule'] and 'wholeAmounts' in dn['rule'] and 'No notice' in dn['rule'], 'driverNotice language / money / when'
for k in ('title', 'body'):
    assert set(dn[k]) == {'sv', 'fr', 'en'}, k + ' sv/fr/en'
for lang in ('sv', 'fr', 'en'):
    assert '{amount}' in dn['body'][lang] and '{reason}' in dn['body'][lang], 'body placeholders ' + lang
assert set(dn['examples']) == {'SEK', 'EUR', 'TND'} and '65,00 kr' in dn['examples']['SEK'] and '5.000 DT' in dn['examples']['TND'], 'examples keep decimals'
assert 'data { tripId, refundId, amount, reason }' in dn['rule'], 'driverNotice data'
assert 'driver app' in dn['apps'] and 'rider app' in dn['apps'] and 'admin' in dn['apps'], 'driverNotice Rule 0 parts'
ta = c['finish']['tips']['cashInCarAdmin']
assert 'Anything admin can adjust' in ta and 'cashInCarMinutes' in ta and 'per zone or the country standard' in ta and '0–60' in ta and 'default 5' in ta, 'tips.cashInCarAdmin'
assert c['finish']['tips']['settings_ranges']['cashInCarMinutes'] == [0, 60] and c['configDefaults']['tipRules']['cashInCarMinutes'] == 5, 'tip window range / default'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read(); assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.91 (jobs A7 + C8' in tc and 'driver_refund_taken' in tc, 'CONTRACT.md v0.18.91'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
spec = yaml.safe_load(open('openapi.yaml'))
assert spec['info']['version'] == c['version'], 'openapi version'
PY
# v0.18.93 job C9 (owner 2026-11-02 review Q3 "Both: auto + button", Rules decisions/driver-g7.md:83-84): the server marks the
# driver arrived within waiting.autoArriveMeters; the waiting clock stops while he is farther than waiting.leaveMeters.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 93), 'version 0.18.93 or later'
aa = c['autoArrive']
assert 'driver-g7.md:83-84' in aa['note'] and 'Both: auto + button' in aa['note'], 'autoArrive owner note'
st = aa['settings']
assert st['arriveMeters']['configPath'] == 'DriverAppConfig.waiting.autoArriveMeters' and st['arriveMeters']['default'] == 100 and st['arriveMeters']['range'] == [30, 300], 'arriveMeters'
assert st['leaveMeters']['configPath'] == 'DriverAppConfig.waiting.leaveMeters' and st['leaveMeters']['default'] == 200 and st['leaveMeters']['range'] == [100, 2000], 'leaveMeters'
assert 'invalid_auto_arrive_distance' in st['validation'] and 'invalid_auto_arrive_distance' in c['errors']['reason'] and 'driver_away_from_pickup' in c['errors']['reason'], 'reasons'
assert 'actor driver' in aa['auto'] and 'arrivedBy auto' in aa['auto'] and 'chat.autoArrived' in aa['auto'], 'auto step'
assert 'pickup_geofence' in c['fastDispatch']['lateAlarm']['tripTimers']['kinds'] and 'pickup_geofence' in aa['auto'], 'job kind on the trip lane, watched'
assert 'No version change' in aa['away'] and 'max(away.since, waitFrom)' in aa['back'] and 'clockAt' in aa['money'], 'away / back / money'
assert {'autoArriveMeters', 'leaveMeters'} <= set(c['bookingSnapshot']['fields']), 'kept at booking'
for k in ('driver', 'rider', 'admin'):
    assert k in aa['apps'], 'apps ' + k
for k in ('driverPaused', 'riderPaused', 'noShowAway'):
    assert set(aa['texts'][k]) == {'sv', 'fr', 'en'}, k
# v0.18.93 round 2 (C9 supervisor M1-M3): one fix never decides; the back tap within leaveMeters; a rider cancel while away is free.
cf = aa['confirm']
assert cf['fixes'] == 2 and cf['minGapSeconds'] == 5 and cf['maxArriveSpeedKmh'] == 15, 'autoArrive.confirm numbers'
assert 'confirm' in aa['auto'] and 'confirm' in aa['away'] and 'confirm' in aa['back'] and 'never decides' in aa['position'], 'confirm used'
assert 'leaveMeters' in aa['back'] and 'not_at_pickup' in aa['back'] and 'driverBack' in aa['button'], 'back tap'
assert 'driver-g15.md:64' in aa['riderCancel'] and 'FREE' in aa['riderCancel'], 'rider cancel while away is free'
for k in ('position', 'auto', 'button', 'away', 'back', 'riderCancel'):
    assert k + 'Before0_18_93r1' in aa, 'Rule 21: first wording kept ' + k
assert set(aa['texts']['driverBack']) == {'sv', 'fr', 'en'}, 'driverBack'
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert spec['info']['version'] == c['version'], 'openapi version'
w = S['Waiting']['properties']
assert w['arrivedBy']['enum'] == ['auto', 'tap'] and w['away']['required'] == ['since'] and 'pausedSeconds' in w and 'pauseCount' in w, 'Waiting fields'
assert all(k not in S['Waiting']['required'] for k in ('arrivedBy', 'away', 'pausedSeconds', 'pauseCount')), 'Waiting additive'
assert 'autoArriveMeters' in S['TripTerms']['properties'] and 'leaveMeters' in S['TripTerms']['properties'], 'TripTerms'
dw = S['DriverWaiting']['allOf'][-1]['properties']
assert dw['autoArriveMeters']['minimum'] == 30 and dw['leaveMeters']['maximum'] == 2000, 'DriverWaiting'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read(); assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.93 (job C9' in tc and '## 91. Auto arrived' in tc, 'CONTRACT.md v0.18.93'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
# v0.18.96 (BQ-M23; owner s06:1164 "only how much he get"): a booked ride in the driver's lists carries driverTotal.
python3 - <<'PY'
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 96), 'version 0.18.96 or later'
br = c['priceDisplay']['bookedRide']
assert 'session-2026-11-06.md:1164' in br['note'] and 'BQ-M23' in br['note'], 'bookedRide owner note'
dt = br['driverTotal']
assert 'driverEarnings + pickupPay + driverBonus' in dt and 'Offer.driverTotal' in dt and 'driver view only' in dt, 'driverTotal rule'
assert 'driverAdjustments' in dt and 'TripProjection.driverTotal' in dt and 'never shows below 0' in dt and 'no tip' in dt and 'no later pay change' not in dt, 'driverTotal includes the J6 driver-pay change (M23 MF1)'
assert 'driver_adjustments' in br['apps']['server'] and 'driverTotalOf' in br['apps']['server'], 'server: same driverTotalOf'
assert 'never sent to the rider' in dt and "'—'" in dt and 'never' in br['apps']['driver'], 'privacy + no phone maths'
for k in ('driver', 'rider', 'admin', 'server'):
    assert k in br['apps'], 'apps ' + k
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert spec['info']['version'] == c['version'], 'openapi version'
r = S['DriverReservation']
assert r['properties']['driverTotal']['allOf'] == [{'$ref': '#/components/schemas/Money'}], 'DriverReservation.driverTotal is Money'
assert 'driverTotal' not in r['required'], 'additive (optional)'
assert 'v0.18.96' in r['properties']['driverTotal']['description'] and 'v0.18.96' in r['properties']['earnings']['description'], 'descriptions'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read(); assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.96 (BQ-M23' in tc, 'CONTRACT.md v0.18.96'  # v0.18.101: this note moved to CHANGELOG.md (Rule 21 kept word for word)
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
echo "contract ok"
# v0.18.101: every version's own checks are in scripts/verify_v<major>_<minor>_<patch>.py (Rule 25) and all run here, in
# version order (numeric sort). A new version adds its file and no line here. v0.18.94 and v0.18.97: their blocks, moved word for
# word from here in v0.18.101 (Rule 25). v0.18.99 BQ-M25b: verify_v0_18_99.py (cash 0 on a
# trip not paid in the car; refund room wording). v0.18.100 BQ-V37: verify_v0_18_100.py (ride-check scan cadence per zone). v0.18.101 §92 BQ-V34: verify_v0_18_101.py (the driver's SOS texts his contacts). v0.18.102 BQ-V38: verify_v0_18_102.py (approving a payout run carries what the admin saw). v0.18.105 BQ-V43: verify_v0_18_105.py (the driver's Android offer push config). v0.18.106 contract text batch: verify_v0_18_106.py (heading-check setting wording; paid-movera 400 reasons).
vfiles=$(python3 - <<'PY'
import glob, re
fs = sorted(glob.glob('scripts/verify_v*.py'))
bad = [f for f in fs if not re.fullmatch(r'scripts/verify_v\d+_\d+_\d+\.py', f)]
assert not bad, 'verify_v*.py not named verify_v<major>_<minor>_<patch>.py: ' + ' '.join(bad)
key = lambda f: tuple(int(x) for x in re.findall(r'\d+', f))
print('\n'.join(sorted(fs, key=key)))
PY
)
for f in scripts/verify_v0_18_94.py scripts/verify_v0_18_97.py scripts/verify_v0_18_99.py scripts/verify_v0_18_100.py scripts/verify_v0_18_101.py scripts/verify_v0_18_102.py scripts/verify_v0_18_105.py scripts/verify_v0_18_106.py; do
  printf '%s\n' "$vfiles" | grep -qx "$f" || { echo "$f is not in the verify_v*.py list"; exit 1; }
done
ran=0
for f in $vfiles; do python3 "$f"; ran=$((ran + 1)); done
found=$(find scripts -maxdepth 1 -name 'verify_v*.py' -type f | wc -l)
[ "$ran" -eq "$found" ] || { echo "verify_v*.py: ran $ran of $found files"; exit 1; }
echo "verify_v*.py: $ran files ran in version order"

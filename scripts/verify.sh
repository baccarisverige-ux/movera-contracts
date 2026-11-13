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
md = open('CONTRACT.md').read()
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
md = open('CONTRACT.md').read()
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
md = open('CONTRACT.md').read()
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
md = open('CONTRACT.md').read()
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
md = open('CONTRACT.md').read()
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
md = open('CONTRACT.md').read()
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
md = open('CONTRACT.md').read()
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
md = open('CONTRACT.md').read()
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
md = open('CONTRACT.md').read()
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 78), 'CONTRACT.md title'
assert 'supersedes the S5 J16 `totalAtLeast` idea' in md and '**G33 rider pay-in-car line**' in md and 'first page when counted exactly' in md and '**admin lists “50 of N”**' in md, 'CONTRACT.md v0.18.78 note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
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
md = open('CONTRACT.md').read()
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 79), 'CONTRACT.md title'
assert '**a support ticket without a zone can be assigned and auto-sorted to its country team**' in md and '\nv0.18.79 (wording only, server B1.33, owner Q93' in md, 'CONTRACT.md v0.18.79 note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
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
md = open('CONTRACT.md').read()
assert md.startswith('# Movera shared contract v' + c['version'] + '\n') or tuple(map(int, c['version'].split('.'))) > (0, 18, 81), 'CONTRACT.md title'
assert '**at most 3 open booked rides per rider**' in md and '\nv0.18.81 (server B1.34' in md and '`maxOpenPerRider` (3)' in md, 'CONTRACT.md v0.18.81 note'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
PY
echo "contract ok"

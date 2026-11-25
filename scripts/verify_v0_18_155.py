#!/usr/bin/env python3
"""v0.18.155 (driver profile v3; contract.json#driverProfile): the rider profile read, compliments, moderated reviews, the
driver's Min profil, the admin moderation routes, the per-zone switches, the privacy rules and the CONTRACT.md note (the
v0.18.150 note moved word for word to CHANGELOG.md, Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 147), 'version 0.18.155 or later'
dp = c['driverProfile']
codes = [x['code'] for x in dp['compliments']['list']]
assert codes == ['great_service', 'knew_the_way', 'friendly', 'clean_car', 'safe_driving', 'good_music'], 'six chips in order'
assert set(codes) == set(c['ratings']['tags']['aboutDriver']) and c['ratings']['tags']['maxPerRating'] == 6, 'chips = aboutDriver'
assert [x['emoji'] for x in dp['compliments']['list']] == ['⭐', '\U0001F9ED', '\U0001F4AC', '✨', '\U0001F6E1', '\U0001F3B5'], 'phone emoji'
assert c['ratings']['tags']['aboutRider'] == ['on_time', 'polite', 'clear_pickup'], 'aboutRider unchanged'
rv = dp['review']
assert rv['maxLength'] == 280 and rv['minStarsShown'] == 4 and 'only after an admin approves' in rv['moderation'], 'moderated reviews'
for never in ('rider id', 'phone', 'photo', 'address'):
    assert never in rv['reviewName'], 'privacy: ' + never
assert c['configDefaults']['driverProfileOn'] is True and c['configDefaults']['driverReviewsOn'] is False, 'defaults'
assert 'no new polling' in dp['load'] and 'max-age=300' in dp['load'], 'load rule'
o = yaml.safe_load(open('openapi.yaml'))
P, sc = o['paths'], o['components']['schemas']
g = P['/rider/trips/{tripId}/driver-profile']['get']
assert g['x-actor'] == ['rider'] and '304' in g['responses'] and 'ETag' in g['responses']['200']['headers'], 'rider read, cacheable'
assert {'get', 'patch'} <= set(P['/driver/public-profile']), 'Min profil'
for v in ('approve', 'hide'):
    assert P['/admin/driver-reviews/{reviewId}/' + v]['post']['x-permission'] == 'settings.publish', v
assert P['/admin/driver-reviews']['get']['x-permission'] == 'settings.read', 'admin list'
pp = sc['DriverPublicProfile']
assert pp['additionalProperties'] is False and not ({'riderId', 'phone', 'email'} & set(pp['properties'])), 'no rider data'
assert sc['DriverReviewShown']['additionalProperties'] is False and set(sc['DriverReviewShown']['properties']) == {'text', 'name', 'month'}, 'review shown = text, name, month'
assert 'riderId' not in sc['AdminDriverReview']['properties'], 'admin list has no rider id'
rq = sc['RatingRequest']['properties']
assert rq['review']['maxLength'] == 280 and rq['reviewName']['enum'] == ['first_name', 'anonymous'] and rq['reviewName']['default'] == 'first_name', 'rating fields'
assert rq['comment']['maxLength'] == 2000, 'private comment unchanged'
for d in ('RiderAppConfig', 'DriverAppConfig'):
    assert sc[d]['properties']['driverProfile'] == {'$ref': '#/components/schemas/DriverProfileSettings'}, d
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.155 (driver profile v3' in t, 'CONTRACT.md note'
assert '\nv0.18.150 (' not in t, 'v0.18.150 note moved'
assert 'follows v0.18.154)' in t, 'follows'
ch = open('CHANGELOG.md', encoding='utf-8').read().split('\n')
n150 = next(l for l in ch if l.startswith('v0.18.150 (L20 stream backup;'))
assert ch.count(n150) == 1 and ch[ch.index(n150) - 2].startswith('v0.18.155 (driver profile; Rule 21 / Rule 25'), 'CHANGELOG move'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.155 driver profile ok')

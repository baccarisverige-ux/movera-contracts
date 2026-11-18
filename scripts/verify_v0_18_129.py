#!/usr/bin/env python3
"""v0.18.129 (saved-places design steps 4-7; owner 2026-11-18 "Build", Rules decisions/session-2026-11-18-saved-places-design.md):
a saved place may carry one fixed ride category, preferredCategoryId (CategoryId | null), optional on writes, with the
unknown_category check, the rider texts sv / en / fr and the admin read-only view. Run by scripts/verify.sh (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 129), 'version 0.18.129 or later'
rp = c['phoneDataToServer']['riderPlaces']
pc = rp['preferredCategory']
assert list(pc) == ['note', 'field', 'write', 'check', 'app', 'texts', 'admin', 'migration'], 'preferredCategory keys'
assert 'Not money' in pc['note'] and 'now rides and to Later (scheduled) rides alike' in pc['app'], 'not money; now + Later'
assert 'absent' not in pc['field'] and 'keep the stored value' in pc['write'] and 'null clears it' in pc['write'], 'write rules'
assert 'reason unknown_category' in pc['check'] and 'NOT cleared' in pc['check'], 'check rule'
assert 'rider_places.preferred_category_id (migration 0118)' in pc['migration'], 'migration'
want = {'saveAddress': 'Spara adressen?', 'savedAs': 'Sparad som {type}', 'undo': 'Ångra',
        'askFixCategory': 'Alltid välja kategori för den här platsen?', 'noThanks': 'Nej tack',
        'changeCategory': 'Byt kategori', 'categoryNotHere': '{category} finns inte här just nu'}
assert list(pc['texts']) == list(want), 'text keys'
for k, sv in want.items():
    tx = pc['texts'][k]
    assert set(tx) == {'sv', 'en', 'fr'} and all(tx.values()) and tx['sv'] == sv, 'texts ' + k
    for ph in ('{type}', '{category}'):
        assert (ph in tx['sv']) == (ph in tx['en']) == (ph in tx['fr']), 'placeholder ' + k
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
for n in ('SavedPlace', 'SavedPlaceRequest'):
    p = S[n]['properties']['preferredCategoryId']
    assert p['oneOf'] == [{'$ref': '#/components/schemas/CategoryId'}, {'type': 'null'}], n + ' nullable CategoryId'
    assert 'preferredCategoryId' not in S[n].get('required', []), n + ' optional (additive)'
assert 'placeId' not in S['SavedPlaceRequest']['properties'], 'request has its own properties'
for path, m in (('/rider/places', 'post'), ('/rider/places/{placeId}', 'put'), ('/rider/places/import', 'post')):
    assert 'v0.18.129' in spec['paths'][path][m]['description'], path
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.129 (saved-places design' in t and 'follows v0.18.128' in t, 'CONTRACT.md v0.18.129 note'
# the move (Rule 25 size, Rule 21 word for word): the v0.18.123 note and the old pointer line now only in CHANGELOG.md
import hashlib
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n123 = next(l for l in cl if l.startswith('v0.18.123 (SF-F1-3 safe config saves;'))
assert '\n' + n123 not in t and hashlib.sha256(n123.encode()).hexdigest() == '0ad117477514a5add533027140aec837bd8ed8baf057f0882effea56032478d7', 'v0.18.123 note moved word for word'
j = cl.index(n123)
assert cl[j - 2].startswith('v0.18.129 (saved-places design; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.122 and before (the v0.18.122 and v0.18.121 notes moved in v0.18.128,'), 'old pointer line kept in CHANGELOG.md'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.123 and before (the v0.18.123 note moved in v0.18.129, the v0.18.122 and v0.18.121 notes in v0.18.128, the v0.18.120 note in v0.18.127,' in t, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.129 saved place fixed category ok')

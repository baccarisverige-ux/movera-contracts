#!/usr/bin/env python3
"""v0.18.164 (France document lists; owner 2026-11-25): vehicleRules.maxAge, FR defaults (maxAgeYears 6,
hybridElectricExempt, REVTC validMonths 60, insurance guide), fleet owners of the company papers, the openapi
fields, the CONTRACT.md note and the v0.18.159 note moved word for word to CHANGELOG.md. Run by scripts/verify.sh."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 164), 'version 0.18.164 or later'
do = c['driverOnboarding']; st = do['settings']; d = st['defaults']
assert 'maxAgeYears' not in d['SE']['vehicles'] and 'hybridElectricExempt' not in d['SE']['vehicles'], 'SE unchanged'
assert d['FR']['vehicles']['maxAgeYears'] == 6 and d['FR']['vehicles']['hybridElectricExempt'] is True, 'FR age'
assert d['FR']['validMonths']['vtc_register_certificate'] == 60, 'REVTC 60'
f = d['FR']['documents']['fleet']
assert f == ['company_registration', 'vtc_register_certificate', 'rc_pro_insurance', 'bank_statement'] and f == do['documents']['required']['FR']['fleet'], 'FR fleet = Uber FR'
assert 'urssaf_certificate' in do['documents']['types'] and 'vtc_sticker' in d['FR']['documents']['vehicle'], 'type kept, macaron kept'
assert 'no_file' in do['documents']['reviewNeedsFile'], 'no_file'
assert 'controle_technique' not in do['documents']['types'], 'no contrôle technique'
g = d['FR']['guides']['insurance']['checklist']
assert all(set(x) == {'sv', 'fr', 'en'} and len(v) <= st['guideLimits']['lineChars'] for x in g for v in x.values()), 'guide lines'
assert all('transport de personnes à titre onéreux' in g[0][l] for l in ('fr', 'en', 'sv')), 'insurance guide'
T = do['documents']['types']
for t in ('vtc_register_certificate', 'rc_pro_insurance', 'urssaf_certificate', 'company_registration'):
    assert T[t]['owner'] == 'fleet', t
assert st['limits']['maxAgeYears'] == [1, 30], 'limit'
ma = do['vehicleRules']['maxAge']
assert 'hybrid or electric' in ma and 'not put back to pending' in ma and 'Sweden' in ma, 'maxAge rule'
spec = yaml.safe_load(open('openapi.yaml'))
vp = spec['components']['schemas']['OnboardingSettings']['properties']['vehicles']
assert vp['properties']['maxAgeYears']['maximum'] == 30 and 'maxAgeYears' not in vp['required'], 'openapi maxAgeYears'
assert vp['properties']['hybridElectricExempt']['default'] is False, 'openapi exempt'
md = open('CONTRACT.md', encoding='utf-8').read(); ch = open('CHANGELOG.md', encoding='utf-8').read()
assert md.startswith('# Movera shared contract v' + c['version']), 'title'
assert '\nv0.18.164 (France document lists;' in md + ch, 'note'
assert 'v0.18.164 (France documents; Rule 21 / Rule 25: moved from CONTRACT.md word for word' in ch and '\nv0.18.159 (fleet needs a car;' in ch, 'move'
assert md.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.164 France documents: ok')

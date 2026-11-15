#!/usr/bin/env python3
# v0.18.101 §92 (BQ-V34 = BQ-S12; owner 2026-11-02 Q2 "Use them in SOS (Recommended)", Rules decisions/driver-g14.md:12):
# the driver's SOS texts his emergency contacts; admin on/off on the country standard; "SMS not connected" seam.
# Moved out of verify.sh (Rule 25: scripts/ files <= 1,500 lines); run by verify.sh from the repository root.
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 101), 'version 0.18.101 or later'
x = c['sosContactsSms']
assert 'driver-g14.md:12' in x['note'] and 'rider' in x['note'].lower(), 'sosContactsSms note'
assert 'COUNTRY STANDARD only' in x['setting'] and 'sos_sms_country_only' in x['setting'], 'sosContactsSms setting'
assert x['statuses'] == ['off', 'no_contacts', 'not_connected', 'queued', 'sent', 'failed'], 'sosContactsSms statuses'
assert 'skipped' in x['delivery'] and 'AFTER the SOS is saved' in x['delivery'], 'sosContactsSms delivery seam'
assert x['callingCodes'] == {'SE': '+46', 'FR': '+33', 'TN': '+216'}, 'calling codes'
assert '{lat}' in x['positionLink'] and '{lng}' in x['positionLink'], 'position link'
assert all(c['configDefaults']['sosContactsSms'][k] is True for k in ('SE', 'FR', 'TN', 'other')), 'defaults on'
def langs(t, keys):
    assert set(t) == {'sv', 'fr', 'en'}, 'sv/fr/en'
    for v in t.values():
        for k in keys: assert '{' + k + '}' in v, 'placeholder ' + k
langs(x['texts']['sms'], ['driver', 'link', 'emergency'])
langs(x['texts']['noPosition'], [])
for k in ('sent', 'notConnected', 'failed'): langs(x['texts']['driver'][k], [])
langs(x['texts']['driverContactsOn'], []); langs(x['texts']['driverContactsOff'], [])
for k in ('switch', 'off', 'no_contacts'): langs(x['texts']['admin'][k], [])
for k in ('not_connected', 'queued', 'failed'): langs(x['texts']['admin'][k], ['n'])
langs(x['texts']['admin']['sent'], ['n', 'sent'])
for w in ('Contract', 'Server', 'Admin', 'Driver app', 'Rider app'):
    assert w in x['apps'], 'Rule 0 part ' + w
spec = yaml.safe_load(open('openapi.yaml'))
S = spec['components']['schemas']
assert S['SosContactsSms']['properties']['status']['enum'] == x['statuses'] and S['SosContactsSms']['required'] == ['status', 'contacts', 'at'], 'SosContactsSms schema'
assert 'contactsSms' in S['SosReceipt']['properties'] and 'contactsSms' not in S['SosReceipt']['required'], 'SosReceipt.contactsSms optional'
assert 'contactsSms' in S['Incident']['properties'] and 'contactsSms' not in S['Incident'].get('required', []), 'Incident.contactsSms optional'
assert S['CountryRules']['properties']['sosContactsSms']['type'] == 'boolean', 'CountryRules.sosContactsSms'
assert set(S['DriverAppConfig']['properties']['sosContactsSms']['required']) == {'on', 'connected'}, 'DriverAppConfig.sosContactsSms'
assert 'sosContactsSms' not in S['RiderAppConfig']['properties'], 'rider config unchanged'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.101 (BQ-V34' in t and '## 92. The driver\'s SOS texts his emergency contacts' in t, 'CONTRACT.md v0.18.101'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
assert spec['info']['version'] == c['version'], 'openapi version'
print('v0.18.101 ok')
# Supervisor S1, S2, M2 (Rules audits/impact/v34-driver-sos-supervisor.md).
assert 'invalid_number' in x['phone'] and 'NEVER handed' in x['phone'] and '46701234567' in x['phone'], 'phone check S2'
assert "never the rider's phone GPS first" in x['text'], 'position order S1'
assert 'never fails the SOS' in x['delivery'] and 'savepoint' in x['delivery'], 'SMS step isolated M2'
print('v0.18.101 supervisor fixes ok')

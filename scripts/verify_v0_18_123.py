#!/usr/bin/env python3
"""v0.18.123 (SF-F1-3 safe config saves; owner 2026-11-17 Q-SCS-1 "Keep values, save rest (Rec.)", 2026-11-16 Q-SCS-2
"No, keep current (Rec.)"; Rules audits/impact/safe-config-saves.md): checks the kept-keys rule of PUT /admin/config/{doc}
(the list, every path exists in its document's schema, removeKeys, the answer and the audit), the Restore keep rule, the
alert settings kind keep, the openapi copy and CONTRACT.md. Run by scripts/verify.sh from the repository root (Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 123), 'version 0.18.123 or later'
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']

kk = c['configDocs']['keptKeys']
assert kk['country_rules'][:6] == ['payoutMode', 'payoutSchedule', 'maxRiderDebt', 'driverOwesLimit', 'calls.adminCallRoles', 'calls.phoneProvider'], 'country_rules kept keys (later versions add: v0.18.136 riderFeeStripe, verify_v0_18_136.py; v0.18.139 driverPayRequest, verify_v0_18_139.py)'
assert kk['dispatch'] == ['radar.reaskAfterSeconds', 'exclusive.reaskAfterSeconds'], 'dispatch kept keys'
assert set(kk) - {'driver_app_config', 'driverAppConfigNote', 'rider_app_config', 'appUpdateNote'} == {'note', 'country_rules', 'dispatch', 'removeKeys'}, 'keptKeys: the two documents (v0.18.130 adds driver_app_config, verify_v0_18_130.py; v0.18.154 adds rider_app_config, verify_v0_18_154.py)'
n = kk['note']
assert n.startswith('v0.18.123 (SF-F1-3') and 'Keep values, save rest (Rec.)' in n and 'never refused' in n and 'keeps nothing' in n and 'details.kept' in n, 'keptKeys.note'
assert 'unknown_kept_key' in kk['removeKeys'], 'removeKeys reason'

def has(schema_name, path):
    sch = S[schema_name]
    for part in path.split('.'):
        props = sch.get('properties', {})
        assert part in props, f'{schema_name}.{path} not in the schema'
        sch = props[part]
        if '$ref' in sch: sch = S[sch['$ref'].split('/')[-1]]
for p in kk['country_rules']: has('CountryRules', p)
for p in kk['dispatch']: has('DispatchDocument', p)

r = c['pricingHistory']['restoreKeeps']
assert 'No, keep current (Rec.)' in r and 'payoutMode, payoutSchedule, maxRiderDebt or driverOwesLimit' in r and 'left out of the restored document' in r and 'calls.adminCallRoles or calls.phoneProvider' in r, 'restoreKeeps'
a = c['alertDesk']['commands']['settingsKeepKinds']
assert '(job 6)' in a and 'settings.kinds' in a and 'never refused' in a and 'keptKinds' in a, 'settingsKeepKinds'

u = S['ConfigDraftUpdate']['properties']['removeKeys']
assert u['type'] == 'array' and sorted(u['items']['enum']) == sorted(set(kk['country_rules'] + kk['dispatch'] + kk.get('driver_app_config', []) + kk.get('rider_app_config', []))) and 'removeKeys' not in S['ConfigDraftUpdate']['required'], 'openapi removeKeys'
assert S['ConfigDraft']['properties']['keptKeys']['type'] == 'array' and 'keptKeys' not in S['ConfigDraft']['required'], 'openapi keptKeys'
assert 'v0.18.123 (configDocs.keptKeys' in P['/admin/config/{doc}']['put']['description'], 'openapi PUT'
assert 'v0.18.123 (pricingHistory.restoreKeeps)' in P['/admin/config/{doc}/restore']['post']['description'], 'openapi restore'
assert 'v0.18.123 (alertDesk.commands.settingsKeepKinds)' in P['/admin/alerts/settings']['put']['description'], 'openapi alert settings'

t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.129: the v0.18.123 note moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.123 (SF-F1-3 safe config saves;' in tc and 'follows v0.18.122' in tc, 'CONTRACT.md v0.18.123 note'
assert '**Kept keys** (v0.18.123' in t and 'unknown_kept_key' in t, 'CONTRACT.md §6.5 kept keys'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.123 safe config saves ok')

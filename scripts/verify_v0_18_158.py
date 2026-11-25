#!/usr/bin/env python3
"""v0.18.158 (crash catcher; owner 2026-11-24 "Add to admin all kind of crash", Rules LAUNCH-RULE.md 2026-11-24,
plan/NUMBERS.md): checks contract.json#crashCatcher (kinds, marker, native reason, breadcrumbs, fields, outbox, server
limits, admin reads, the per-zone switch, the app_crash alert kind), the openapi copy (TelemetryCrash new fields,
ErrorReport, GET /admin/errors?kind=, GET /admin/errors/{errorId}/reports, crashReports in both app documents), the
CONTRACT.md note and the v0.18.153 note moved word for word to CHANGELOG.md (Rule 21 / Rule 25). Run by scripts/verify.sh
from the repository root (own file, Rule 25)."""
import hashlib, json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 158), 'version 0.18.158 or later'
cc = c['crashCatcher']
assert cc['note'].startswith('v0.18.158 (crash catcher;') and 'follows v0.18.157)' in cc['note'], 'note'
assert list(cc['kinds']) == ['dart_error', 'native_crash', 'freeze', 'crash', 'error'], 'kinds'
assert c['telemetry']['crashReport']['kinds'] == ['crash', 'error', 'dart_error', 'native_crash', 'freeze'], 'crashReport.kinds keeps crash and error first'
assert cc['freezeSeconds'] == 5, 'freeze 5 s'
assert cc['breadcrumbs']['max'] == 30 and cc['breadcrumbs']['maxMessage'] == 200, 'breadcrumbs'
assert cc['breadcrumbs']['types'] == ['route', 'lifecycle', 'platform', 'network', 'log'], 'breadcrumb types'
for word in ('NSSetUncaughtExceptionHandler', 'SIGABRT', 'Thread.setDefaultUncaughtExceptionHandler', 'ApplicationExitInfo', 'never overwrites'):
    assert word in cc['nativeReason'], word
assert 'swiped away from the background never counts' in cc['runningMarker'] and 'Web: no marker' in cc['runningMarker'], 'marker'
assert 'at most 20 reports' in cc['outbox'] and 'at the next launch' in cc['outbox'], 'outbox'
assert cc['server']['perDevicePerMinute'] == 10 and '202 with an empty body and nothing stored' in cc['server']['perDevice'], 'per device'
assert 'GET /admin/errors/{errorId}/reports?limit= (1-50, default 20)' in cc['admin']['reports'], 'reports read'
assert cc['setting']['key'] == 'crashReports.on' and c['configDefaults']['crashReportsOn'] is True, 'switch default on'
assert 'invalid_document' in cc['setting']['rule'] and 'last known value' in cc['setting']['rule'], 'switch rule'
assert cc['alert']['kind'] == 'app_crash' and c['alertDesk']['kindGroups']['app_crash'] == 'system', 'alert kind group'
kd = c['alertDesk']['serverDetection']['kindDefaults']['app_crash']
assert kd['level'] == 'important' and kd['limits'] == {'info': None, 'important': 1, 'critical': 20}, 'alert defaults'
spec = yaml.safe_load(open('openapi.yaml'))
S, P = spec['components']['schemas'], spec['paths']
T = S['TelemetryCrash']['properties']
assert T['kind']['enum'] == c['telemetry']['crashReport']['kinds'], 'TelemetryCrash.kind'
for k in ('osVersion', 'deviceModel', 'tripId', 'zoneId', 'breadcrumbs', 'nativeReason', 'freezeMs'):
    assert k in T and k not in S['TelemetryCrash'].get('required', []), k + ' optional'
assert T['breadcrumbs']['maxItems'] == 30 and S['CrashBreadcrumb']['properties']['message']['maxLength'] == 200, 'breadcrumbs openapi'
assert S['ErrorGroup']['properties']['kind']['enum'] == c['telemetry']['crashReport']['kinds'], 'ErrorGroup.kind'
names = [p.get('name') for p in P['/admin/errors']['get']['parameters']]
assert 'kind' in names, 'kind filter'
o = P['/admin/errors/{errorId}/reports']['get']
assert o['operationId'] == 'adminListErrorReports', 'reports op'
assert o['responses']['200']['content']['application/json']['schema'] == {'$ref': '#/components/schemas/ErrorReportList'}, 'reports body'
assert set(S['ErrorReport']['required']) == {'at', 'kind', 'message', 'breadcrumbs'}, 'ErrorReport required'
for doc in ('RiderAppConfig', 'DriverAppConfig'):
    cr = S[doc]['properties']['crashReports']
    assert cr['properties']['on']['default'] is True and cr['additionalProperties'] is False, doc
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.158 (crash catcher;' in t, 'CONTRACT.md note'
assert 'v0.18.158 (`contract.json#crashCatcher`): kinds `dart_error`' in t, 'CONTRACT.md §11 line'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n153 = next(l for l in cl if l.startswith('v0.18.153 (P29 driver income year file'))
assert '\n' + n153 not in t and cl.count(n153) == 1, 'v0.18.153 note moved once'
assert hashlib.sha256(n153.encode()).hexdigest() == '167f587e94c0209863055f54ac85a79ba9bd2441a656407412521e35e4ff2632', 'v0.18.153 note moved word for word'
j = cl.index(n153)
assert cl[j - 2].startswith('v0.18.158 (crash catcher; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.153 and before (the v0.18.153 note moved in v0.18.158, the v0.18.152 note in v0.18.157' in t + ch, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.158 crash catcher ok')

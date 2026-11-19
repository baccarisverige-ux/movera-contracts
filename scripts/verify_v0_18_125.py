#!/usr/bin/env python3
"""v0.18.125 (L20-6 health; Rules audits/impact/l20-6-health.md): wording only. Checks /readyz busy (200) vs down (503),
the database states, the system_health lane-late alert, the released lateAlarm text kept (Rule 21), that no alert kind
was added, and CONTRACT.md. Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 125), 'version 0.18.125 or later'
fd = c['fastDispatch']
h = fd['health']
assert h.startswith('v0.18.125 (L20-6') and 'database: ok | busy | unavailable | not_configured' in h, 'health: states'
assert '200 { status: ready, database: busy } while busy' in h and '503 unavailable, reason database_unavailable, Retry-After 5 only while unavailable' in h, 'health: readyz busy vs down'
assert '57014' in h and '53300 / 53400' in h and 'GET /healthz/jobs (the outside monitor) still answers 503' in h, 'health: busy codes, jobs unchanged'
assert 'they never touch request handling' in h, 'health: no effect on requests'
la = fd['lateAlarm']
assert 'the admin alert desk shows it too' in la['rule'] and 'does not show it yet' not in la['rule'], 'lateAlarm.rule'
assert la['ruleBefore0_18_125'].startswith('Replaced in v0.18.125 (kept, Rule 21): GET /healthz/jobs') and la['ruleBefore0_18_125'].endswith('The admin alert desk does not show it yet (a later job).'), 'released rule kept'
assert list(la) == ['note', 'tripTimers', 'dispatch', 'rule', 'ruleBefore0_18_125'], 'lateAlarm: only ruleBefore0_18_125 added'
assert list(fd).index('health') == list(fd).index('lateAlarm') + 1, 'health after lateAlarm'
sd = c['alertDesk']['serverDetection']['kindDefaults']
sh = sd['system_health']
assert sh['level'] == 'important' and 'laneLate' in sh, 'system_health.laneLate'
ll = sh['laneLate']
assert 'Critical' in ll and 'system_health:lane_late:<group>:<country>' in ll and "'Server trip timers are running {0} s late'" in ll and "'{0} dispatch rounds overdue'" in ll and 'solved by itself' in ll and 'No new kind or setting' in ll, 'laneLate text'
assert not any(k.startswith('lane') for k in sd), 'no new alert kind'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.131: the v0.18.125 note moved to CHANGELOG.md word for word
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.125 (L20-6 health' in tc and '`/readyz` (the hosting health check) stays **200**' in tc, 'CONTRACT.md v0.18.125 note'
n125 = next(l for l in tc.split('\n') if l.startswith('v0.18.125 ('))
assert 'follows v0.18.124)' in n125 and 'restack' not in n125, 'CONTRACT.md v0.18.125 note follows v0.18.124'
# the move (Rule 25 size, Rule 21 word for word): the v0.18.118 note and the old pointer line now only in CHANGELOG.md
import hashlib
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n118 = next(l for l in cl if l.startswith('v0.18.118 (the contract text recent jobs owed'))
assert '\n' + n118 not in t and hashlib.sha256(n118.encode()).hexdigest() == 'ee5d741198818b7126dd250d60e060feedffe4a982cb0d1911e63193e6103a86', 'v0.18.118 note moved word for word'
j = cl.index(n118)
assert cl[j - 2].startswith('v0.18.125 (L20-6 health; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert cl[j + 2].startswith('Older version notes are in `CHANGELOG.md`: v0.18.117 and before (the v0.18.117 note moved in v0.18.124,'), 'old pointer line kept in CHANGELOG.md'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.118 and before (the v0.18.118 note moved in v0.18.125, the v0.18.117 note in v0.18.124, the v0.18.116 note in v0.18.123,' in t + ch, 'the v0.18.125 pointer line (kept in CHANGELOG.md since v0.18.126)'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'

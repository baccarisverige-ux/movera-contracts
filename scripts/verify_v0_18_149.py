#!/usr/bin/env python3
"""v0.18.149 (SOS contacts SMS sent; owner 2026-11-02 Q2 "Use them in SOS (Recommended)", Rules decisions/driver-g14.md:12):
the driver's SOS texts his emergency contacts through the sign-in SMS sender when the server switch is on (default off)
(contract.json#sosContactsSms.send), the CONTRACT.md notes, and the v0.18.128 note moved word for word to CHANGELOG.md
(Rule 25). Run by scripts/verify.sh (own file, Rule 25)."""
import hashlib, json
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 149), 'version 0.18.149 or later'
s = c['sosContactsSms']['send']
assert list(s) == ['note', 'sender', 'serverSwitch', 'serverSwitchNote', 'once', 'dailyCap', 'delivery', 'logs', 'apps'], 'send keys'
assert s['serverSwitch'] == 'SOS_CONTACTS_SMS_SEND' and 'unset or any other value = off, the default' in s['serverSwitchNote'], 'server switch default off'
assert 'smsSignIn.serverKeys' in s['sender'] and 'CountryRules.sosContactsSms (setting, default on) stays' in s['serverSwitchNote'], 'same sender, country switch kept'
assert 'At most one SMS per contact number per SOS case' in s['once'] and 'never resent (fail closed)' in s['once'], 'once'
assert 'smsSignIn.dailyCap' in s['dailyCap'] and 'error daily_limit' in s['dailyCap'], 'daily cap'
assert 'never holds a contact' in s['logs'] and 'or a position' in s['logs'], 'logs'
assert "Rider: not affected" in s["apps"], "rider not affected"
assert c['sosContactsSms']['statuses'] == ['off', 'no_contacts', 'not_connected', 'queued', 'sent', 'failed'], 'no new status'
assert 'fleet invitation SMS stays not connected' in c['smsSignIn']['otherSmsV0_18_149'], 'otherSms follow-up'
assert c['smsSignIn']['otherSms'].endswith('until a later version says so.'), 'released otherSms kept as it was'
t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.149 (SOS contacts SMS sent;' in t, 'CONTRACT.md note'
n149 = next(l for l in t.split('\n') if l.startswith('v0.18.149 (SOS contacts SMS sent;'))
assert 'follows v0.18.133' in n149 and '`contract.json#sosContactsSms.send`' in n149, 'CONTRACT.md note text'
assert ' v0.18.149 (`sosContactsSms.send`): connected = the sign-in SMS keys are set AND the server switch' in t, '§92 line'
ch = open('CHANGELOG.md', encoding='utf-8').read()
cl = ch.split('\n')
n128 = next(l for l in cl if l.startswith('v0.18.128 (S7 W2 Q125'))
assert '\n' + n128 not in t and hashlib.sha256(n128.encode()).hexdigest() == '055f16ae7e3902a95d2effe1a1d5ea91fb1409c4bb7272d14163a5d0521f4d9f', 'v0.18.128 note moved word for word'
assert cl.count(n128) == 1, 'v0.18.128 note once in CHANGELOG.md'
j = cl.index(n128)
assert cl[j - 2].startswith('v0.18.149 (SOS contacts SMS sent; Rule 21 / Rule 25: moved from CONTRACT.md word for word'), 'CHANGELOG.md move line'
assert hashlib.sha256(cl[j + 2].encode()).hexdigest() == '73c0e6e74692806d25a0b425cfaa22b6bac89c37d539426b3fabe86d08e2ecf0', 'old pointer line moved word for word'
assert 'Older version notes are in `CHANGELOG.md`: v0.18.128 and before (the v0.18.128 note moved in v0.18.149, the v0.18.127 note in v0.18.133,' in t, 'new pointer line'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.149 SOS contacts SMS sent ok')

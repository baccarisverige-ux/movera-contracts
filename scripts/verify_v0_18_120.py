#!/usr/bin/env python3
"""v0.18.120 (S4 wave B1; owner W1 Q78 [Q-B13] "Do not count it" and Q80 [Q-B1] "Yes", 2026-11-11; Rules
audits/impact/s4-b116.md, s4-b118.md): checks the Q-B13 rule (an Exclusive or hand-sent offer that expired while a
server copy's live link was down never counts toward auto-offline; a decline still counts; the admin count follows it;
no setting), the B1.18 settings-stream close after a LISTEN reconnect (random 0-STREAM_CLOSE_SPREAD_MS, hold at most
2 min, the SSE comment, the apps re-read), that only those two keys were added, the released texts kept (Rule 21),
and CONTRACT.md. Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 120), 'version 0.18.120 or later'

ao = c['autoOffline']
assert list(ao) == ['note', 'counts', 'countsStatuses', 'resets', 'neverCounts', 'outage', 'changes', 'adminText', 'on'], 'autoOffline: only outage added'
o = ao['outage']
assert o.startswith("v0.18.120 (S4 B1.16 Q-B13, owner W1 Q78 'Do not count it'"), 'outage: source'
assert 'offer that EXPIRED while the live link (LISTEN) of a server copy was down does not count' in o and 'it neither counts nor ends the run' in o, 'outage: skipped'
assert 'overlaps an outage window' in o and 'any server copy recorded' in o and "last proof that its link worked" in o, 'outage: window'
assert 'until 60 s after the copy last reported it still down' in o, 'outage: open window bound'
assert 'A declined offer always counts' in o and 'DispatchDriverFacts.missedInRow' in o and 'No setting.' in o, 'outage: decline, admin count, no setting'
assert ao['counts'] == ['exclusive', 'assigned'] and ao['countsStatuses'] == ['declined', 'expired'], 'autoOffline lists unchanged'
assert ao['note'].startswith('v0.8.0 (owner 2026-10-27), v0.18.6') and ao['changes']['v0.18.6'].startswith('assigned (hand-sent) offers now count'), 'released text kept'
assert 'v0.18.120' in ao['changes'], 'changes line'

rt = c['realtime']
assert list(rt) == ['envelope', 'optional', 'kinds', 'afterTerminal', 'rules', 'streamClose', 'reconnectClose', 'connectedRule', 'sessionEnd'], 'realtime: only reconnectClose added'
r = rt['reconnectClose']
assert r.startswith("v0.18.120 (S4 B1.18, owner W1 Q80 = Q-B1 'Yes'") and 'GET /rider/config/stream, GET /driver/config/stream' in r, 'reconnectClose: source and streams'
assert 'random 0–STREAM_CLOSE_SPREAD_MS delay (default 30 s; 0 = at once)' in r and 'at most 2 min' in r, 'reconnectClose: spread and hold'
assert "': realtime reconnected; reconnect to catch up'" in r and 'the app re-reads on that reconnect' in r, 'reconnectClose: comment and re-read'
assert rt['streamClose'].startswith('v0.18.68 (server B1.9, owner W1 Q73)'), 'streamClose kept'

t = open('CONTRACT.md', encoding='utf-8').read()
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.120 (S4 wave B1;' in t and 'follows v0.18.119)' in t, 'CONTRACT.md v0.18.120 note'
assert 'No warning before; a short line on the island when it happens (decision 7). SE and FR alike. v0.18.120 (Q-B13' in t and '(`autoOffline.outage`)' in t, 'CONTRACT.md §6.7'
assert t.count('realtime.reconnectClose`') >= 3, 'CONTRACT.md P21 + driver stream + note'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.120 Q-B13 outage rule and B1.18 reconnect close ok')

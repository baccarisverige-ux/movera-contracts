#!/usr/bin/env python3
"""v0.18.120 (S4 wave B1; owner W1 Q78 [Q-B13] "Do not count it" and Q80 [Q-B1] "Yes", 2026-11-11; Rules
audits/impact/s4-b116.md, s4-b118.md): checks the Q-B13 rule (an Exclusive or hand-sent offer that expired while a
server copy's live link was down never counts toward auto-offline; a decline still counts; the admin count follows it;
no setting), the B1.18 settings-stream close after a LISTEN reconnect (random 0-STREAM_CLOSE_SPREAD_MS, hold at most
2 min, the SSE comment, the apps re-read), that only those two keys were added, the released texts kept (Rule 21),
and CONTRACT.md. Also (owner 2026-11-16 "It's not when driver decline ! It count when driver ignore" + "And only
exclusive / And it's about exclusive ride not radar"): only Exclusive offers the driver let EXPIRE count toward
auto-offline; a decline never counts and does not reset the count; Radar never counts nor resets; the replaced released
texts are kept under ...Before0_18_120 keys. Run by scripts/verify.sh from the repository root (own file, Rule 25)."""
import json
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 120), 'version 0.18.120 or later'

ao = c['autoOffline']
assert list(ao) == ['note', 'noteBefore0_18_120', 'counts', 'countsStatuses', 'countsStatusesBefore0_18_120', 'declined', 'resets', 'neverCounts', 'outage', 'changes', 'adminText', 'adminTextBefore0_18_120', 'on'], 'autoOffline: only outage, declined and the Before0_18_120 keys added'
o = ao['outage']
assert o.startswith("v0.18.120 (S4 B1.16 Q-B13, owner W1 Q78 'Do not count it'"), 'outage: source'
assert 'offer that EXPIRED while the live link (LISTEN) of a server copy was down does not count' in o and 'it neither counts nor ends the run' in o, 'outage: skipped'
assert 'overlaps an outage window' in o and 'any server copy recorded' in o and "last proof that its link worked" in o, 'outage: window'
assert 'until 60 s after the copy last reported it still down' in o, 'outage: open window bound'
assert 'A declined offer always counts' not in o and 'A declined offer never counts either (autoOffline.declined)' in o and 'DispatchDriverFacts.missedInRow' in o and 'No setting.' in o, 'outage: decline, admin count, no setting'
assert ao['changes']['v0.18.6'].startswith('assigned (hand-sent) offers now count') and 'v0.18.120' in ao['changes'], 'changes lines'

# Owner 2026-11-16: only Exclusive offers the driver let expire count; a decline never counts and does not reset.
assert ao['counts'] == ['exclusive', 'assigned'] and ao['countsStatuses'] == ['expired'], 'only expired Exclusive (also hand-sent to one driver) offers count'
assert ao['countsStatusesBefore0_18_120'] == ['declined', 'expired'], 'released statuses kept (Rule 21)'
assert ao['neverCounts'][:3] == ['radar', 'reservation', 'any offer sent while on a trip'] and 'any declined offer' in ao['neverCounts'], 'neverCounts'
assert ao['resets'] == ['any offer accepted', 'driver goes online'], 'resets unchanged (a decline is not one)'
n = ao['note']
assert n.startswith("v0.18.120 (owner 2026-11-16 \"It's not when driver decline ! It count when driver ignore\"") and "And it's about exclusive ride not radar" in n, 'note: the owner words'
assert 'that the driver let expire (ignored)' in n and 'A declined offer never counts and does not reset the count' in n, 'note: expired only, decline skipped'
assert 'Radar offers' in n and 'never count and never reset the count' in n and 'ANY accepted offer (any kind) and going online set the count back to 0' in n, 'note: radar, resets'
assert 'kind=assigned' in n and 'one chosen driver' in n and 'an admin radar group' in n, 'note: hand-sent = Exclusive to one driver; a radar group is Radar'
assert ao['noteBefore0_18_120'].startswith('v0.8.0 (owner 2026-10-27), v0.18.6') and 'that were declined or expired (missed)' in ao['noteBefore0_18_120'], 'released note kept (Rule 21)'
d = ao['declined']
assert 'neither counts nor ends the run' in d and 'expired, declined, expired' in d and '2' in d and 'DispatchDriverFacts.missedInRow' in d and 'acceptance' in d, 'declined: rule, example, admin count, acceptance untouched'
for lang, old, new in (('sv', 'missade eller nekade', 'låtit {n} Exklusiva erbjudanden i rad gå ut'), ('fr', 'manquées ou refusées', 'laissé expirer'), ('en', 'missed or declined', 'letting {n} Exclusive offers in a row run out')):
    assert old in ao['adminTextBefore0_18_120'][lang] and old not in ao['adminText'][lang] and new in ao['adminText'][lang] and '{n}' in ao['adminText'][lang], 'adminText ' + lang
    m = c['driverHome']['setOffline']['reasons']['missed_offers']
    was = {'sv': 'Du missade eller nekade {count} erbjudanden i rad', 'fr': 'Vous avez manqué ou refusé {count} offres d’affilée', 'en': 'You missed or declined {count} offers in a row'}[lang]
    assert m[lang + 'Before0_18_120'] == was and m[lang] != was and '{count}' in m[lang] and ('xclusi' in m[lang] or 'xklusi' in m[lang]), 'missed_offers text ' + lang
assert c['driverHome']['setOffline']['reasons']['missed_offers']['en'] == 'You let {count} Exclusive offers run out in a row', 'missed_offers en'
da = c['adminDispatch']['directAssign']
assert 'a declined one never counts' in da['note'] and 'a declined or missed hand-sent offer counts' in da['noteBefore0_18_120'], 'directAssign note'
f = c['dispatchDriverFacts']['real']
assert 'the driver let expire in a row' in f['missedInRow'] and 'declined ones are skipped' in f['missedInRow'] and f['missedInRowBefore0_18_120'].startswith('Exclusive or assigned offers of live trips missed in a row'), 'missedInRow text'
sf = json.load(open('fixtures/settings_flow.json'))
ids = {x['id']: x for x in sf['autoOffline']}
assert ids['ignore-decline-ignore-is-2']['offers'] == ['xe', 'xd', 'xe'] and ids['ignore-decline-ignore-is-2']['limit'] == 2 and ids['ignore-decline-ignore-is-2']['expectOfflineAt'] == 2, 'fixture: ignore, decline, ignore = 2'
assert ids['ignore-decline-ignore-is-not-3']['limit'] == 3 and ids['ignore-decline-ignore-is-not-3']['expectOfflineAt'] is None, 'fixture: not 3'
assert ids['exclusive-radar-exclusive-ignored-is-2']['offers'] == ['xe', 're', 'xe'] and ids['exclusive-radar-exclusive-ignored-is-2']['expectOfflineAt'] == 2, 'fixture: radar ignored between'
assert ids['declines-never-set-offline']['expectOfflineAt'] is None and set(ids['declines-never-set-offline']['offers']) == {'xd', 'ad'}, 'fixture: declines only'
assert not any(o in ('xd', 'ad') for x in sf['autoOffline'] if x['expectOfflineAt'] is not None and not x['id'].startswith(('ignore-decline', 'decline')) for o in x['offers'][-1:]), 'no case ends on a decline'
assert len(sf['autoOfflineBefore0_18_120']) == 10 and sf['autoOfflineBefore0_18_120'][0]['offers'][0] == 'xd', 'released fixture cases kept (Rule 21)'

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
assert 'that the driver **let expire** (ignored)' in t and 'a decline never counts and does not reset the count' in t and 'declined or let expire, the driver goes offline' not in t, 'CONTRACT.md §6.7 expired only'
n120 = next(l for l in t.split('\n') if l.startswith('v0.18.120 ('))  # its own note, wherever later versions put theirs (was line 3; changed by 0.18.121)
assert 'owner 2026-11-16' in n120 and 'only Exclusive offers the driver let expire count' in n120, 'CONTRACT.md top note'
y = open('openapi.yaml', encoding='utf-8').read()
assert 'Missed or declined exclusive offers in a row' not in y and 'this declined or expired Exclusive offer was the last' not in y, 'openapi wording'
assert t.count('realtime.reconnectClose`') >= 3, 'CONTRACT.md P21 + driver stream + note'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print('v0.18.120 Q-B13 outage rule and B1.18 reconnect close ok')
# Neutral wording (owner rule: the driver, not he/him; sv "föraren"): the admin rule text names no "he"/"han"/"il".
import re as _re
for _lang, _bad in (('sv', r'\bhan\b'), ('fr', r"\bqu.il\b"), ('en', r'\b(he|him|his)\b')):
    assert not _re.search(_bad, ao['adminText'][_lang]), 'adminText neutral ' + _lang
assert 'sets the driver offline' in ao['declined'], 'declined example neutral'
print('v0.18.120 neutral wording: OK')

#!/usr/bin/env python3
"""v0.18.112 (BQ-A04, J16-J18; owner item 109 "Yes, pages + oldest first (Rec.)", Rules
decisions/session-2026-11-06.md:1116): the support inbox GET /admin/tickets lists the oldest-waiting ticket first
(SupportTicket.waitingSince, admin views only), then the others newest change first; one cursor over both parts.
Follows v0.18.111 (rebuilt on it in the k-chain, 2026-11-15). Run by scripts/verify.sh from the repository
root (own file, Rule 25)."""
import json, yaml
c = json.load(open('contract.json'))
assert tuple(map(int, c['version'].split('.'))) >= (0, 18, 112), 'version 0.18.112 or later'
io = c['supportDesk']['inboxOrder']
assert set(io) >= {'rule', 'waitingSince', 'paging', 'admin', 'apps', 'compatibility'}, 'inboxOrder keys'
r = io['rule']
assert 'session-2026-11-06.md:1116' in r and 'pages + oldest first' in r, 'inboxOrder: owner item 109'
assert 'GET /admin/tickets' in r and 'waitingSince oldest first' in r and 'updatedAt newest first' in r, 'inboxOrder: two-part order'
assert 'GET /support/tickets' in r and 'keeps newest change first' in r, "inboxOrder: the person's own list keeps its order"
w = io['waitingSince']
assert 'admin views only' in w and 'first rider or driver message that has no support answer after it' in w and 'not open' in w, 'waitingSince meaning'
p = io['paging']
assert 'nextCursor' in p and 'both parts' in p and 'never 400' in p, 'paging: one cursor over both parts, old cursor accepted'
assert 'Load more' in io['admin'] and 'no sort in the panel' in io['admin'], 'admin part'
assert 'no change' in io['apps'], 'apps part'
assert 'migration 0112' in io['compatibility'] and 'CONCURRENTLY' in io['compatibility'] and 'X-Api-Version stays 0.5' in io['compatibility'], 'compatibility'
spec = yaml.safe_load(open('openapi.yaml'))
assert spec['info']['version'] == c['version'], 'openapi version'
P, S = spec['paths'], spec['components']['schemas']
d = P['/admin/tickets']['get']['description']
d = ' '.join(d.split())
assert 'v0.18.112 order' in d and r in d, 'openapi /admin/tickets order (the inboxOrder rule)'
assert p in d, 'openapi /admin/tickets paging'
ws = S['SupportTicket']['properties']['waitingSince']
assert ws['allOf'] == [{'$ref': '#/components/schemas/Timestamp'}] and 'v0.18.112' in ws['description'], 'SupportTicket.waitingSince'
assert 'waitingSince' not in S['SupportTicket'].get('required', []), 'waitingSince optional'
names = {q.get('name') for q in P['/admin/tickets']['get']['parameters'] if 'name' in q}
assert not ({'sort', 'order', 'orderBy'} & names), 'no new sort query key'
t = open('CONTRACT.md', encoding='utf-8').read()
tc = t + open('CHANGELOG.md', encoding='utf-8').read()  # v0.18.117: the v0.18.109-v0.18.115 notes moved to CHANGELOG.md (Rule 25 size, Rule 21 kept word for word)
assert t.startswith('# Movera shared contract v' + c['version']) and '\nv0.18.112 (BQ-A04' in tc, 'CONTRACT.md v0.18.112 note'
assert 'follows v0.18.111)' in tc and 'which is not merged yet' not in tc, 'CONTRACT.md: follows note'  # v0.18.118: tc (contract chain supervisor 2026-11-16 SF4)
s37 = t[t.index('## 37.'):t.index('## 38.')]
assert '**Inbox order** (v0.18.112, `inboxOrder`' in s37 and 'waitingSince' in s37, 'CONTRACT.md §37 inbox order'
assert t.count('\n') <= 1500, 'CONTRACT.md over 1,500 lines'
print("v0.18.112 support inbox oldest waiting first ok")

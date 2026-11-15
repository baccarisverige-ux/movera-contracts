#!/usr/bin/env python3
"""v0.18.102 BQ-V38 checks (owner item 105 "Refresh, approve again"): approving a payout run carries what the admin
saw; a changed run = 409 run_changed with the fresh PayoutRunCard. Run by scripts/verify.sh from the repository root."""
import json

import yaml

c = json.load(open('contract.json'))
g = c['payoutMode']['approveGuard']['note']
S = yaml.safe_load(open('openapi.yaml'))['components']['schemas']
assert all(x in g for x in ('run_changed', 'expected_total_required', 'PayoutRunCard')), 'approveGuard names its reasons and the card'
assert {'expectedCount', 'expectedTotal'} <= set(S['PayoutRunApproveCommand']['required']), 'PayoutRunApproveCommand requires expectedCount and expectedTotal'
assert set(S['PayoutRunCard']['required']) == {'country', 'periodEnd', 'count', 'total'}, 'PayoutRunCard'

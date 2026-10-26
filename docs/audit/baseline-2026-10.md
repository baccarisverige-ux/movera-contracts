# movera-contracts: baseline audit (Phase 1), 2026-10-26

**Done:** all sections. **Not done:** nothing in this repo for Phase 1.

## 1. Structure

| File | Lines | Role |
|---|---|---|
| `contract.json` | 2206 | The rules: 46 top-level blocks (transitions, fares, dispatch, onboarding, auth, errors, realtime, …). Version **0.5.5**. |
| `tools/gen_openapi.py` | 1540 | Generates `openapi.yaml` from Python schema definitions and `contract.json`. |
| `openapi.yaml` | 13583 | Generated. 138 paths, 150 operations. |
| `CONTRACT.md` | 567 | Human description, §1–§14 plus one paragraph per version. |
| `reference_check.py` | 279 | Reference engine: replays the fixtures against `contract.json`. |
| `fixtures/` | 9 files + config samples | Scenarios (24), events (6), money, cancel fees, pickup pay, surge, fares, dispatch, sample pricing/dispatch documents. |
| `scripts/` | verify, checksums, sync | Checks, and the script consumers use to copy the contract. |

## 2. Dependencies

Python 3 and PyYAML only (CI installs `pyyaml`). Nothing to audit for vulnerabilities.

## 3. CI

One workflow, `verify.yml`, on pull requests and pushes to `main`: `pip install pyyaml` then `scripts/verify.sh` (checksums, file list = CHECKSUMS, reference engine, OpenAPI parses, tag = version).

Gaps:
- **G1** CI does not check that `openapi.yaml` is what the generator produces. Today it matches (checked by hand below), but a hand edit would pass CI. Add: regenerate into a temp file and `diff`.
- **G2** No check that `CONTRACT.md`'s title version equals `contract.json` version.
- **G3** No pinned Python/PyYAML versions (minor).
- **G4** Only tag `v0.4.4` exists on GitHub; v0.5.0–v0.5.5 have no tags, so consumers sync by commit hash. Tags were planned after each merge.

## 4. Baseline run (2026-10-26, commit 5719833)

| Check | Result | Time |
|---|---|---|
| `tools/gen_openapi.py` regenerated vs committed `openapi.yaml` | identical | <2 s |
| `reference_check.py` | OK | <1 s |
| `scripts/verify.sh` | contract ok, 138 paths | <1 s |

## 5. Coverage of the rules

- 24 scenarios cover 20 of the 21 transition commands. **Not covered: `raise_price`** (added in v0.5.5 without a scenario). → add scenarios: raise while searching, raise while offered, raise after expiry refused.
- Every state-changing operation documents at least one 4xx answer.
- No fixtures yet for: fleet invitations (v0.5.3), provider sign-in, early-end fare with `minimum_adjust`, on-the-way (v0.5.4).

## 6. Consumers' copies (on each repo's `main`)

| Consumer | Copy version | Behind by |
|---|---|---|
| movera-server | 0.5.5 | up to date |
| Movera-driver-app | 0.5.3 | 0.5.4, 0.5.5 |
| Admin-panel-movera-dispatch | 0.5.3 | 0.5.4, 0.5.5 |
| **movera-rider-app** | **0.5.0** | 0.5.1 → 0.5.5, although the rider app already calls v0.5.4/0.5.5 endpoints (on-the-way, raise-price) |

**Finding C1 (S2):** the rider app's contract copy is five versions behind the server while its live code uses newer endpoints, so its contract tests do not cover what it actually calls. → Phase 0/2: sync the copy to 0.5.5 in all three apps and make each app's CI fail when its copy is older than the newest contract tag.

## 7. Code quality

- The generator is one 1540-line script; fine for now, no action.
- `raise_price` has no scenario (above).
- Contract history lives in two places (README history and CONTRACT.md version paragraphs); keep both or link one to the other.

## 8. Summary

| # | Finding | Severity | Action | Phase |
|---|---|---|---|---|
| C1 | Rider app's contract copy is 0.5.0; driver and admin 0.5.3; server 0.5.5 | S2 | Sync all to 0.5.5; CI check on copy age | 0 / 2 |
| C2 | `raise_price` not covered by any scenario | S3 | Add three scenarios | 3 |
| C3 | No fixtures for invitations, provider sign-in, early-end fare, on-the-way | S3 | Add fixtures, replayed by server and apps | 3 |
| C4 | CI does not verify openapi.yaml is generated | S3 | Regenerate + diff in CI | 2 |
| C5 | No tags after v0.4.4 | S4 | Tag v0.5.0–v0.5.5 | 2 |

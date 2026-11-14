# Movera shared contract

One contract for the three Movera apps and the server: **Rider** (Flutter),
**Driver** (Flutter), **Admin** (React/TypeScript), and the backend that will
serve all three. This repository is the only place the contract changes.
Each app and the server carries a byte-for-byte copy under `contracts/` and checks it
against `CHECKSUMS`.

Current version: **0.18.89** (`contract.json#version`, tag `v0.18.89`; numbered after 0.18.88, the fleet % removal, merged first in #131). The server and driver carry
0.18.72; admin and rider carry 0.18.66 (later versions land in them after the merge).

## What is here

| File | What |
|---|---|
| `contract.json` | Machine-readable source of truth: enums, terminal set, transition table, cancel codes, realtime rules, error codes, currencies, categories, languages, admin dispatch rules, config defaults |
| `CONTRACT.md` | The written contract: entities, lifecycle per app, events, admin control matrix, config documents, API surface, and the notes of every version |
| `openapi.yaml` | REST and realtime surface for the three apps and the server |
| `fixtures/` | Lifecycle scenarios, realtime gate cases, money cases, cancel fees, pickup pay cases, surge schedule cases, fare cases, dispatch timelines, sample config documents (also the server-only pricing and dispatch documents); the apps and the server replay them in their contract tests |
| `reference_check.py` | Reference engine: proves the fixtures agree with `contract.json` |
| `tools/gen_openapi.py` | Generates `openapi.yaml` from `contract.json` plus the hand-written surface |
| `CHECKSUMS` | sha256 of every file above, the list the apps' copy tests read |
| `scripts/` | `verify.sh` (the checks CI runs), `checksums.sh` (rewrites `CHECKSUMS`), `sync.sh` (copies the contract into an app), `check_version_order.py` (the new version is higher than every tag) |
| `docs/` | Audit notes (not part of the contract, not in `CHECKSUMS`) |

## Versions and tags

The version lives in `contract.json#version` and in the first lines of
`CONTRACT.md`. Every released version is a git tag `v<version>` on `main`.
A consumer pins a tag, never `main`.

Version order (2026-11-09, step 21): a new `version` must be higher than every released tag, compared number by
number (0.18.10 > 0.18.9); `scripts/check_version_order.py` fails the PR otherwise. A released or given-up number
(0.18.46) is never reused. After every merge, tag it (`git tag v<version> && git push origin v<version>`).

- Additive change (a new optional field, a new endpoint): patch or minor bump.
- Breaking change (a renamed field, a removed value, a changed transition):
  minor bump at least, named in `CONTRACT.md` with what the apps must do.

## Changing the contract

1. Branch from `main`. Edit `contract.json` and `CONTRACT.md`; regenerate
   `openapi.yaml` with `python3 tools/gen_openapi.py . openapi.yaml`
   (needs `pyyaml`); add or update fixtures for the change.
2. `python3 reference_check.py` must pass. Bump `version`.
3. `scripts/checksums.sh`, then `scripts/verify.sh`.
4. Open a pull request. CI (`.github/workflows/verify.yml`, "Contract checks") runs
   `scripts/verify.sh` on pull requests and on `v*` tags, not on pushes to `main`
   (owner 2026-11-06); drafts are skipped.
5. After the merge, `.github/workflows/tag-release.yml` ("Tag released version") tags
   `v<version>` on the merge commit if that tag is missing (step 21, 2026-11-09). By hand it
   is `git tag v<version> && git push origin v<version>`; `verify.sh` on the tag checks that
   it matches `contract.json#version`.
6. Land the same version in every consumer in one go (Rule 43(4): the copy PRs start right
   after the merge, one per repo): in each consumer run its sync script with the tag
   (`tools/sync_contract.sh v<version>` in the server and the admin, `tool/sync_contract.sh
   v<version>` in the driver and rider apps; each runs this repo's `scripts/sync.sh`) and
   commit `contracts/` exactly as it comes out. Never edit a consumer's `contracts/` by hand.
   The admin panel also bumps `CONTRACT_VERSION` in `webapp/src/domain/contract.ts`. Each
   consumer's "Contract copy" workflow checks the copy on every PR and push, and once a day
   opens or closes the issue "Contract copy behind movera-contracts main".

## Consumers

| Consumer | Copy | Pinned |
|---|---|---|
| `baccarisverige-ux/movera-rider-app` | `contracts/` (`tool/sync_contract.sh`) | v0.18.54 |
| `baccarisverige-ux/Movera-driver-app` | `contracts/` (`tool/sync_contract.sh`) | v0.18.54 |
| `baccarisverige-ux/Admin-panel-movera-dispatch` | `contracts/` (`tools/sync_contract.sh`) + `CONTRACT_VERSION` in `webapp/src/domain/contract.ts` | v0.18.54 |
| `baccarisverige-ux/movera-server` | `contracts/` (`tools/sync_contract.sh`); `test/contract_copy.test.ts` fails on drift | v0.18.54 |

## Working rules

- The owner's memory for the whole project is the Rules repository (`Movera-team/Rules`:
  `RULES.md`, `decisions/`, `plan/`). Read it before changing anything here.
- Rule 25: a hand-written file over 1,500 lines is split first; `contract.json`,
  `openapi.yaml` and `CHECKSUMS` are exempt.
- Rule 21: never delete anything without asking the owner.
- Pull requests use `.github/pull_request_template.md`; security problems go through
  `SECURITY.md` (private reporting), never a public issue.

## Freeze

From the day the server implements a version until the end of the first
real test week, the contract does not change. Changes collected during the
test become the next version, landed in all consumers together.

## History

v0.5.4 to v0.18.63 (October–November 2026): the notes of every version are at the top of
`CONTRACT.md`, newest first.

v0.5.3 (25 October 2026): driver sign-up details, fleets with a join code, the documents each
country and account type needs, uploaded to the server (`§14`). Additive; notes at the top of
`CONTRACT.md`.

v0.5.2 (25 October 2026): the free cars near the rider, for the rider's map while it
chooses a ride (`GET /rider/nearby-vehicles`), with nothing that tells who drives.
Additive; notes at the top of `CONTRACT.md`.

v0.5.1 (24 October 2026): the server-only pricing and dispatch documents with the fare
formula and the automatic dispatch rules as the owner decided them, unpaid cash fees on
the next ride, admin sign-in with e-mail and password and the panel's 34 permissions,
address search and road routes through the server, telemetry, and the admin live map's
driver positions and trip traces. Additive; notes at the top of `CONTRACT.md`.

v0.5.0 (23 October 2026): pickup pay (rider fixed fee, driver tiered ranges with a
maximum per ride), the driver's stopped / driving signal and the Radar limits per
state, the surge schedule (curve over time), sign-in / tokens / push devices with
test numbers outside production, and the meaning of the config document version.
Additive; notes at the top of `CONTRACT.md`.

v0.4.4 is the first commit of this repository: the contract exactly as the
three apps carried it on 23 October 2026 (their copies were byte-identical).
Earlier versions live in the apps' histories; the notes for v0.3 to v0.4.4
are at the top of `CONTRACT.md`.

# Movera shared contract

One contract for the three Movera apps and the server: **Rider** (Flutter),
**Driver** (Flutter), **Admin** (React/TypeScript), and the backend that will
serve all three. This repository is the only place the contract changes.
Each app carries a byte-for-byte copy under `contracts/` and checks it against
`CHECKSUMS`; the server builds against a tag.

Current version: **0.5.3** (`contract.json#version`, tag `v0.5.3`). Consumers still on v0.4.4, v0.5.0, v0.5.1 or v0.5.2 move to it in one PR set.

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
| `scripts/` | `verify.sh` (the checks CI runs), `checksums.sh` (rewrites `CHECKSUMS`), `sync.sh` (copies the contract into an app) |

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
4. Open a pull request. CI runs `scripts/verify.sh`.
5. After the merge, tag: `git tag v<version> && git push origin v<version>`.
   CI checks that the tag matches `contract.json#version`.
6. Land the same version in every consumer in one go: run `scripts/sync.sh
   <app-dir>` from the tag in each app repository and open one pull request
   per app (the admin panel also bumps `webapp/src/domain/contract.ts`).

## Consumers

| Consumer | Copy | Pinned |
|---|---|---|
| `baccarisverige-ux/movera-rider-app` | `contracts/` | v0.4.4 |
| `baccarisverige-ux/Movera-driver-app` | `contracts/` | v0.4.4 |
| `baccarisverige-ux/admin-panel-movera-dispatch` | `contracts/` + `CONTRACT_VERSION` in `webapp/src/domain/contract.ts` | v0.4.4 |
| Server | builds against a tag | to be set |

## Freeze

From the day the server implements a version until the end of the first
real test week, the contract does not change. Changes collected during the
test become the next version, landed in all consumers together.

## History

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

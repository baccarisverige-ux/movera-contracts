# movera-contracts: Phase 2 (CI hardening)

**Done:** all items below. **Not done:** tags v0.5.0–v0.5.5 (needs the owner's go; see below).

| Item | Change | Evidence |
|---|---|---|
| G1 openapi.yaml must be generated | `scripts/verify.sh` regenerates into a temp file and compares | Appending one line to openapi.yaml makes verify.sh fail ("hand edit rejected"); clean tree passes |
| G2 title version | verify.sh checks `CONTRACT.md` line 1 names `v<contract.json version>` | passes on v0.5.5 |
| G3 pinned tools | `pyyaml==6.0.3` (the version verified locally) | — |
| Concurrency | cancel superseded runs on the same ref | — |

Required check for branch protection (owner decision D1): **`verify`** (workflow "Contract checks").

Tags: only v0.4.4 exists. Tagging v0.5.0…v0.5.5 on their merge commits lets consumers sync by tag. This creates public refs, so it waits for the owner's "go".

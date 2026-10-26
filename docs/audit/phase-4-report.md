# Phase 4 report: security and data integrity

Date: 2026-10-26. Status: **PRs open, CI to be green, not merged** (owner says "merge"). Full report with steps,
root cause and evidence: `movera-server/docs/audit/phase-4.md`.

## PRs
- movera-server #22: route-by-route authorization matrix (`test/e2e/12_route_matrix.test.ts`), P4-1/2/3/4/5/7.
- movera-rider-app #424: P4-9. Admin-panel-movera-dispatch #147: P4-4 (sign-in help), P4-10.
- No contract change was needed (the forgot-password recovery is a deploy setting).

## Findings
| Id | Sev | Repo | Finding | State |
|---|---|---|---|---|
| P4-1 | S2 | server | Zone-limited Super admin could make a password link for the all-zones owner | fixed |
| P4-2 | S3 | server | Document uploads without a rate limit | fixed |
| P4-3 | S3 | server | Admin could set a negative fare | fixed |
| P4-4 | S2 | server, admin | No way back in after a forgotten admin password (free plan, no shell) | fixed (`ADMIN_PASSWORD_RESET`); e-mail self-service needs a provider, proposed |
| P4-5 | S4 | server | `POST /telemetry/*` not served | fixed |
| P4-6 | S4 | server | Riders not zone-scoped for zone-limited admins | owner decision |
| P4-7 | S3 | server | Phone numbers / e-mails from query strings in the request log | fixed |
| P4-8 | S2 | rider, driver | Two Google Maps keys in git history (two still at four branch tips) | owner rotates |
| P4-9 | S4 | rider | Off-contract `/ride-types`, `/rider/promotions/active` calls | fixed |
| P4-10 | S3 | admin | 2 high `npm audit` advisories (vite dev server) | fixed |
| P4-11..13 | S4 | server | approval id probe, notification read without key, attempt tables never swept | open |

## Not done
gitleaks not run locally (pattern scan of every history instead); Flutter dependency advisories not checked (no
advisory source reachable; turn on Dependabot alerts).

# Security audit — 2026-08-12

## Scope

- `contracts/SemanticResourceMutex.py`
- direct and integration tests
- deployment configuration, examples, and integration guidance

The review covered authorization, semantic consensus, output validation, prompt injection, resource-conflict correctness, atomicity, FIFO behavior, time and expiry handling, renewal, release and cancellation ownership, replay protection, storage and compute bounds, digest domains, nonpayability, deployment runner pinning, and truthful evidence claims.

## Final severity summary after remediation

| Severity | Open findings |
|---|---:|
| Critical | 0 |
| High | 0 |
| Medium | 0 |
| Low | 0 |
| Informational / design constraints | 5 |

## Issues fixed during implementation and independent review

1. **Uninitialized active slots** — every bounded slot is explicitly created during deployment.
2. **Public queue-denial exposure** — only deployer-authorized product accounts may submit actions.
3. **Queue-full partial local mutation** — mapped requests preflight queue capacity before allocating an action ID.
4. **FIFO bypass** — every mapped request joins the tail whenever the queue is nonempty.
5. **Expired-lease promotion gaps** — request, renewal, release, cancellation, authorization revocation, and the permissionless sweep path expire and promote as appropriate.
6. **Unsafe unresolved output** — `UNKNOWN_RESOURCE` and `AMBIGUOUS` require empty footprints and cannot acquire or queue a lease.
7. **Revoked backlog promotion and renewal** — revocation cancels all owned queued work, promotion independently rechecks authorization, and a revoked owner cannot renew. The owner may still release an active lease.
8. **Unbounded persistent history** — immutable lifetime caps cover actions, lifecycle events, requester identities, authorization changes, and renewals. Event capacity is reserved for every admitted action's maximum terminal path.
9. **Unaudited authorization mutations** — epoch-numbered digest-linked authorization events record every effective change. Requests and actions bind their admission epoch and authorization digest.
10. **Weak standalone lifecycle event binding** — every event now binds owner, request, footprint, action digest, and request-time/current authorization state.
11. **Stored/effective status confusion** — `stored_status` and `effective_status` are explicit, and integration guidance requires `has_active_lease()` or effective status.
12. **Single-requester global lifetime depletion** — each authorized identity is now limited to 32 admitted actions while the deployment-wide cap remains 256, preventing one requester from consuming the full global capacity.
13. **Character-only semantic and model-output bounds** — registry/action UTF-8 limits, runtime prompt-byte limits, and raw/canonical LLM-response character/byte caps now complement the existing closed schemas.

Remediated issue groups: 13. Open severity findings after remediation remain Critical 0, High 0, Medium 0, Low 0.

## Residual design constraints

### A-01 — Correlated semantic error

Validators may agree on an incomplete footprint. Exact independent results, explicit uncertainty, a closed registry, and bounded schemas reduce risk but are not mathematical proof. Registry-specific golden/red-team evaluation and consequence caps remain required.

### A-02 — External enforcement boundary

The mutex cannot force another contract or off-chain service to honor its lease and does not atomically execute the protected operation. Consumers must wait for finality, pin the deployment and config digest, check the owner and complete footprint, call `has_active_lease()`, and finish before expiry.

### A-03 — Deliberate head-of-line blocking

Strict FIFO prevents starvation and bypass but can delay compatible work behind a conflicting head. Queue and lease lifetimes are bounded; owners can cancel queued work and anyone can sweep expired active work. This is an explicit fairness tradeoff.

### A-04 — Active lease survives revocation until its existing deadline

Revocation cancels queued work and blocks renewal but does not confiscate an active lease because an external operation may already be in flight. The owner can release it; otherwise it expires at its recorded deadline. Deployments should use the shortest practical maximum lease.

### A-05 — Explicit deployment rollover

Hard global and per-requester storage bounds mean a deployment eventually closes some or all new action admission. Operators must monitor public counters and move affected callers to a fresh address and config digest before a required cap. Historical records remain readable and are never overwritten.

## Verification evidence

- Pinned runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`
- GenVM lint and validation: passed
- GenVM typecheck: passed with no diagnostics
- ABI schema extraction: passed
- Direct suite: 49 passed
- Current-source five-validator GLSim: passed 2/2 with five explicit mock validators
- Current-source hosted StudioNet semantic smoke: 1 passed at `0xde0a27C1FFa512a404B1958f33F5ccbcdc8a3986`; exact source; `MAPPED` writes to `ORDER_LEDGER` and `WAREHOUSE_STOCK`; active lease
- Current-source Bradbury deployment: finalized 5/5 `AGREE` at `0x5DdACbe80468872442D88B37589652f7EcaB57ED`; exact 38,820-byte source and expected policy/schema readback
- Current-source Bradbury semantic V3: finalized `AGREE/FINISHED_WITH_RETURN`; exact writes `ORDER_LEDGER` and `WAREHOUSE_STOCK`; durable `LEASE_GRANTED` action/event record
- Superseded pre-final hosted StudioNet V2 semantic smoke: 1 passed with exact `MAPPED` multi-resource write footprint
- Historical hosted StudioNet V1 semantic smoke: 1 passed with exact `MAPPED` multi-resource write footprint
- Current V2 source SHA-256: `b603007a0280eff0b1aed672e365b8ec5da929e5a4dabffc486adf057b7360cc`

The current-source two-test five-validator GLSim run used identical explicit mocks and is not heterogeneous inference evidence. The current-source no-mock StudioNet record proves only the finalized semantic smoke and durable state it captured; it does not establish general mapping accuracy. StudioNet did not expose validator identities, model names, individual votes, vote counts, or transaction IDs through the harness, and none are invented. Earlier StudioNet records match earlier source revisions and remain explicitly superseded.

Bradbury preserves two non-accepted semantic attempts before the finalized positive V3 result. Attempt 1 ended `UNDETERMINED/DISAGREE`; attempt 2 ended `VALIDATORS_TIMEOUT/TIMEOUT`; neither changed accepted action/event state. V3 finalized with three `AGREE`, one `DETERMINISTIC_VIOLATION`, and one `TIMEOUT`, so it is positive finalized evidence but not unanimous evidence. Post-finality latest-final reads verified the exact footprint, action digest, and grant event. The lease had naturally expired by then; the view correctly returned effective `EXPIRED` and inactive without a cleanup write. These records make no claim of model diversity, provider heterogeneity, validator independence, or general semantic accuracy. See [`deployments/bradbury-2026-08-12-deployment-and-negative-smoke.json`](deployments/bradbury-2026-08-12-deployment-and-negative-smoke.json).

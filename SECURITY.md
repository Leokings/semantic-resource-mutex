# Security

## Security boundary

The contract coordinates access to semantic resource names. It does not prove that an external operation used the lease correctly and does not execute that operation. Every consumer must explicitly check the finalized lease before acting.

## Principal risks and mitigations

### Under-locking

Omitting a resource is the most dangerous semantic error because conflicting actions may run together. The registry is closed, the prompt requires every correctness-relevant dependency, uncertainty has explicit `UNKNOWN_RESOURCE` and `AMBIGUOUS` outcomes, output is schema-checked, and validators independently derive the exact same arrays. These controls reduce risk but cannot eliminate correlated model error.

Keep registries small, descriptions mutually distinguishable, and action texts concrete. Run a domain-specific golden and adversarial corpus. Do not use this primitive for irreversible high-value execution without consequence caps or an additional review path.

### Prompt injection

Action text and registry descriptions are treated as quoted data. Output accepts only three keys, closed classifications, exact registered IDs, sorted unique arrays, and no read/write overlap. Controls, bidi overrides, and common invisible characters are rejected. Models receive no arbitrary tools or external side effects. These are schema-bounded prompt-injection defenses, not proof that correlated models cannot semantically under-lock an adversarial action.

### Unauthorized queue denial

Only the permanently authorized deployer is admitted initially. The deployer may explicitly authorize other requesters. Queue, active slots, total actions, per-requester actions, requester identities, authorization changes, renewals, and histories are hard-bounded. Each identity may admit at most 32 actions, preventing one authorized requester from exhausting the 256-action global lifetime. A malicious authorized requester can still obtain one active lease up to its configured deadline, so authorize only product-controlled accounts and use short maximum leases.

Revocation cancels all of that owner's queued actions, is rechecked during promotion, and blocks renewal. It does not confiscate an existing active lease; this preserves in-flight work and lets the owner release it. The lease otherwise expires at its already-recorded deadline. Use `sweep_expired()` if an owner disappears.

### Partial acquisition and deadlock

All resource IDs in one footprint are granted atomically or queued together. The contract never holds a subset while waiting for another, preventing internal hold-and-wait deadlock.

### Starvation and queue bypass

New mapped actions cannot bypass a nonempty queue. Promotion is strict FIFO and may cause head-of-line blocking. Queue length is bounded and owners can cancel their own queued action.

### Expiry and renewal

Views treat a timestamp-expired lease as inactive even if no sweep transaction has persisted `EXPIRED`. Renewal is owner-only, requires an active unexpired lease, and can never move expiry beyond the immutable total lifetime cap. Complete protected work with safety margin before expiry.

### Replay and record confusion

Per-owner request references cannot be reused. Request and action digests bind the current authorization epoch and digest; lifecycle events bind the action, owner, request, footprint, and both request-time and current authorization states. All digests are length-framed and deployment-bound. Integrators must also pin the expected contract address, chain, policy version, and `config_digest`.

### Storage and deployment lifetime

Global and per-requester actions, lifecycle events, requesters, authorization changes, renewals, active slots, and queue entries are hard-bounded. Once global or per-requester action admission reaches its lifetime cap, existing leases remain releasable, cancellable, or expirable because event capacity is reserved mathematically for every admitted action's maximum path. Operators must monitor counts and migrate callers to a fresh deployment before required admission closes.

### Finality and external actions

Do not act on a merely submitted or provisionally accepted request. Wait until the lease-creating transaction is finalized. Confirm `has_active_lease`, owner, footprint, and expiry immediately before the protected operation. Stored `status` alone is insufficient after wall-clock expiry. External systems must reject actions after expiry and should release promptly after completion. The contract does not atomically gate or force external execution, so all consumers must cooperate with this protocol.

### Privacy

Registry descriptions, action text, owners, footprints, queue membership, and event history are public on-chain. Never submit secrets, credentials, private user content, or regulated personal data.

## Integration checklist

- Audit the immutable registry for complete, non-overlapping descriptions.
- Authorize only expected product/controller addresses.
- Pin contract address and `config_digest`.
- Wait for finality.
- Require `classification == MAPPED`, `effective_status == LEASE_ACTIVE`, and `has_active_lease == true`; never trust stored `status` alone.
- Verify the exact owner, read set, write set, and adequate remaining duration.
- Never infer an unlisted resource or side effect from prose.
- Reject external work after expiry even if storage has not yet been swept.
- Release promptly and monitor queue saturation, ambiguity, and validator disagreement.
- Monitor `max_total_actions`, `max_actions_per_requester`, and action counts; rotate to a fresh deployment before a required quota is exhausted.

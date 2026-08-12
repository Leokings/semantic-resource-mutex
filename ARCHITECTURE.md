# Architecture

## Boundary

`SemanticResourceMutex` owns two tightly separated operations:

1. GenLayer consensus maps one action into exact resource reads and writes from a closed deployment registry.
2. Deterministic code applies atomic conflict, lease, and FIFO queue rules to that footprint.

The frontend owns previews and status display. The integrating product owns authentication before it asks the mutex, business execution, and external side effects. The mutex owns requester admission, consensus classification, lease state, queue order, replay controls, and auditable records. It is a cooperative concurrency primitive, not an atomic cross-contract execution wrapper.

## Flow

```text
authorized requester + unique reference + action + bounded duration
                              |
              deterministic validation and replay guard
                              |
            leader maps action to closed read/write IDs
                              |
        each validator independently derives the exact footprint
                              |
          UNKNOWN / AMBIGUOUS? ---- yes ---> terminal fail-closed record
                              |
                             no
                              |
             expire stale leases; promote FIFO head
                              |
     overlap or queued predecessor or no slot? -- yes --> bounded FIFO queue
                              |
                             no
                              |
                    atomic multi-resource lease
                              |
                renew / release / expire / promote
```

## Conflict matrix

For a candidate `C` and active lease `A`:

```text
C.write intersects (A.read union A.write) => conflict
C.read intersects A.write                 => conflict
otherwise                                 => compatible
```

The fixed active-slot index bounds every conflict scan. All resources for one action are granted together. There is no partial acquisition and therefore no hold-and-wait deadlock inside this contract.

## FIFO policy

Once the queue is nonempty, every later mapped request joins its tail. Promotion considers the head first and stops when the head conflicts or no active slot is available. This deliberately accepts head-of-line blocking to make ordering simple, bounded, and starvation-resistant.

Queue positions are not persisted because removal and promotion change them. `get_queue()` is authoritative. `blocking_action_ids` is an audit snapshot and is refreshed for the head during promotion; integrations must not treat it as a permanent dependency graph.

Revocation performs a bounded scan of the entire queue and terminally cancels every queued action owned by that requester. Promotion independently rechecks the head's current authorization and cancels it if revoked, preventing stale or corrupted queue state from bypassing containment. Revoked owners cannot renew, but they may release an already-active lease; otherwise its pre-existing expiry remains authoritative.

## Lease lifecycle

```text
MAPPED -> LEASE_ACTIVE -> RELEASED
   |           |
   |           +-------> EXPIRED
   v
 QUEUED ------> LEASE_ACTIVE
   |
   +----------> CANCELLED

UNKNOWN_RESOURCE and AMBIGUOUS_FOOTPRINT are terminal.
```

Renewal cannot extend a lease past `acquired_at + max_lease_seconds`. `sweep_expired()` is permissionless. Views fail closed even before a sweep by comparing `expires_at` with the current transaction time.

`status`/`stored_status` record the last persisted transition. `effective_status` and `has_active_lease()` apply the current timestamp, so they are the authoritative integration checks before protected work.

## Lifetime bounds and rollover

Every persistent collection has an immutable bound: 256 actions globally, 32 admitted actions per requester, 17,152 lifecycle events, 64 known requesters, four authorization changes per non-deployer requester, 256 authorization events, 64 renewals per action, 32 queued actions, and 32 active slots. The per-requester quota prevents one authorized identity from consuming the entire global action lifetime. The lifecycle-event bound is sized for the maximum possible event path of every admitted action, so terminal release, cancellation, and expiry remain available after action admission closes.

When `max_total_actions` or a requester's `max_actions_per_requester` is approached, deploy a new registry instance and migrate callers by explicitly pinning its new address and `config_digest`. The old deployment remains a read-only historical record; no action or event is deleted or overwritten.

## Digests and replay

- `config_digest` binds chain, deployment, deployer, exact registry, limits, and policy version.
- `request_digest` binds config, owner, reference, canonical action, and requested duration.
- `footprint_digest` binds the complete bounded consensus result.
- `action_digest` additionally binds the action ID, request, footprint, duration, and authorization epoch/digest snapshot.
- authorization events form a separate digest chain over actor, requester, allow/revoke state, epoch, timestamp, and affected queued action IDs.
- every lifecycle event binds its predecessor, owner, request/footprint/action digests, request-time and current authorization state, status, timestamps, and event code.

References are unique per requester; request digests are globally replay-protected inside the deployment.

## Differentiation

This is not the Canon-Constrained World-State Referee. That contract accepts or rejects one predefined fictional state transition using a stale-state digest. It has no semantic read/write footprint, simultaneous compatible leases, lease ownership, expiry, renewal, or FIFO queue.

This is also not a database mutex. A database caller supplies already-known keys. Here, the consensus-critical operation is deciding which immutable semantic resources the proposed language actually touches. Once that judgment is made, deterministic locking takes over.

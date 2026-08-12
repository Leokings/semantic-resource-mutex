# Semantic Resource Mutex

An MIT-licensed reusable GenLayer Intelligent Contract that turns one bounded natural-language action into an exact read/write footprint over an immutable resource registry, then enforces real on-chain leases, conflicts, expiry, renewal, release, and bounded FIFO queueing.

This is not a generic classifier and not an ordinary database lock. A database lock already knows the keys being accessed. This contract exists for agent workflows where an action such as “reserve two units and create the order” must first be mapped by validator consensus to closed resource IDs such as `WAREHOUSE_STOCK` and `ORDER_LEDGER` before deterministic concurrency control can begin.

## Consensus boundary

The leader returns exactly:

```json
{
  "classification": "MAPPED",
  "read_resource_ids": ["CUSTOMER_PROFILE"],
  "write_resource_ids": ["ORDER_LEDGER", "WAREHOUSE_STOCK"]
}
```

Every validator independently performs the same semantic mapping. The transaction agrees only when classification and both canonical sorted arrays match exactly. Unknown resources and ambiguous footprints fail closed with empty arrays and never receive a lease.

All consequences after mapping are deterministic:

- read/read footprints may coexist;
- read/write and write/write overlaps conflict;
- grants reserve all resources atomically or none;
- a bounded FIFO queue prevents later submissions from bypassing its head;
- leases expire, may be renewed only within one deployment-wide lifetime cap, and can be released only by their owner;
- revocation cancels that requester's queued work, blocks renewal, and prevents a revoked queue head from promotion;
- release and expiry promote eligible queued work;
- append-only digest-linked lifecycle and authorization events bind each action to the admission epoch in which it was accepted.

## Immutable deployment policy

```python
SemanticResourceMutex(
    resource_registry_json: str,
    max_queue_size: int,
    max_active_leases: int,
    max_lease_seconds: int,
)
```

The registry contains 1–24 entries with exactly `id`, `label`, and `description`. IDs are closed uppercase identifiers. The registry, concurrency limits, deployer, policy version, chain, and contract address are bound into `config_digest`.

The deployer is permanently authorized and may authorize or revoke additional requester addresses. Revocation immediately removes that requester's queued actions and prevents renewal; an already-active lease remains releasable by its owner and otherwise expires at its existing deadline. Requester identities and authorization changes are hard-bounded.

One deployment accepts at most 256 actions, while each requester may admit at most 32. It also accepts at most 17,152 lifecycle events, 64 known requesters, four authorization changes per non-deployer requester, and 64 renewals per action. The per-requester quota prevents one authorized identity from exhausting the entire global action lifetime. These immutable limits keep total contract state bounded. Deploy a fresh instance and migrate integrations before a global or requester cap is reached; history is never silently discarded.

## Interface

Write methods:

```text
set_requester_authorization(requester_address, allowed)
request_lease(request_reference, action_text, lease_seconds) -> action_id
renew_lease(action_id, additional_seconds) -> expires_at
release_lease(action_id) -> promoted_count
cancel_queued(action_id) -> promoted_count
sweep_expired() -> {expired, promoted}
```

Views:

```text
get_policy()
is_requester_authorized(requester_address)
get_action_count()
get_action(action_id)
has_active_lease(action_id)
get_active_leases()
get_queue()
get_event_count()
get_event(event_id)
get_authorization_event_count()
get_authorization_event(event_id)
```

An integrating product should wait for finality, verify the expected contract and `config_digest`, require `has_active_lease(action_id)`, verify the owner and exact footprint, complete its protected operation before `expires_at`, and then release. This is cooperative on-chain coordination: the mutex neither executes nor atomically gates an external contract call, and it cannot force another system to honor a lease.

## Fail-closed statuses

```text
LEASE_ACTIVE
QUEUED
UNKNOWN_RESOURCE
AMBIGUOUS_FOOTPRINT
RELEASED
EXPIRED
CANCELLED
```

`get_action()` retains `status` for compatibility, returns the same value explicitly as `stored_status`, and separately returns `effective_status`. An unswept lease can therefore have stored status `LEASE_ACTIVE` while its effective status is `EXPIRED`. `has_active_lease()` likewise returns false immediately after expiry. Consumers must use `effective_status` or `has_active_lease()`, not stored status alone.

## Development

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/SemanticResourceMutex.py
genvm-lint typecheck contracts/SemanticResourceMutex.py
pytest tests/direct -q
```

See [TESTING.md](TESTING.md) for five-validator GLSim and StudioNet commands, [ARCHITECTURE.md](ARCHITECTURE.md) for the state machine, and [SECURITY.md](SECURITY.md) before integrating consequences.

The contract pins a concrete production GenVM runner. It contains no `test`, `latest`, or unversioned runner alias.

## Current verification

- GenVM lint and semantic validation: passing
- GenVM typecheck: passing with no diagnostics
- ABI schema extraction: passing
- Direct tests: 49 passing
- Current-source five-validator GLSim: passed 2/2 with five explicit mock validators
- Current-source StudioNet smoke: exact `MAPPED` multi-resource write footprint and active lease passed at `0xde0a27C1FFa512a404B1958f33F5ccbcdc8a3986`
- Current-source Bradbury deployment: finalized 5/5 `AGREE` with byte-identical source at `0x5DdACbe80468872442D88B37589652f7EcaB57ED`
- Current-source Bradbury semantic smoke V3: finalized `AGREE` with successful execution, exact writes `ORDER_LEDGER` and `WAREHOUSE_STOCK`, and a durable `LEASE_GRANTED` record
- Superseded pre-final StudioNet V2 smoke: exact multi-resource semantic mapping and lease grant passed at `0x19636EF3628FdDD8Dbecd9F7bA2BBE6687514B42`
- Historical StudioNet V1 smoke: exact multi-resource semantic mapping and lease grant passed at `0xc5C8A8b496343897c6fefcF35b140D1fC5c9E421`

The retained local five-validator run used explicit mock responses and is not described as heterogeneous model evidence. The current-source no-mock StudioNet run waited for finalized execution, mapped the action to exact writes `ORDER_LEDGER` and `WAREHOUSE_STOCK`, granted an active lease, and matched its deployed 38,820-byte source byte-for-byte at SHA-256 `b603007a0280eff0b1aed672e365b8ec5da929e5a4dabffc486adf057b7360cc`. Its harness did not expose validator identities, model names, individual votes, vote count, or transaction IDs, so none are claimed. Earlier V1 and pre-final V2 records remain explicitly superseded.

On Bradbury, deployment transaction `0xfca0d07139d47d5eee0d5ba691a67731427625e04d2d7c87a49839745c81ddea` finalized with five agreeing votes and exact source readback. Two semantic attempts produced no accepted state: the first ended `UNDETERMINED/DISAGREE`, and the second ended `VALIDATORS_TIMEOUT/TIMEOUT`. V3 transaction `0xd34f5c9037a67c0ccd9fbfcde6f8f7b387579602733f84d46514713408c53a2c` then finalized `AGREE` with successful execution and final votes of three `AGREE`, one `DETERMINISTIC_VIOLATION`, and one `TIMEOUT`. The post-finality view retained the exact mapping and append-only grant event. Its 1,800-second lease had naturally expired by readback, so `stored_status` remained `LEASE_ACTIVE` while `effective_status` was `EXPIRED` and `has_active_lease()` was false. See [`deployments/bradbury-2026-08-12-deployment-and-negative-smoke.json`](deployments/bradbury-2026-08-12-deployment-and-negative-smoke.json). No model-diversity, provider-heterogeneity, or validator-independence claim is made.

## Reuse

Copy the repository, replace `examples/resource-registry.json`, expand the semantic golden cases for your domain, and deploy a new immutable registry. Monitor the global action count and each requester's 32-action quota, then roll integrations to a fresh deployment before a required cap is reached. MIT licensing permits modification and commercial reuse.

## License

[MIT](LICENSE)

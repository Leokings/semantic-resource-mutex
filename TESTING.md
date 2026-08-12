# Testing

## Static and direct checks

```powershell
genvm-lint check contracts/SemanticResourceMutex.py --json
genvm-lint typecheck contracts/SemanticResourceMutex.py --json
genvm-lint schema contracts/SemanticResourceMutex.py --json
pytest tests/direct -q
```

Direct coverage includes registry and input bounds, requester admission, the 32-action per-requester quota, revocation queue purging, promotion-time authorization rechecks, revoked-owner renewal denial, authorization epochs and digest chains, global action/event/requester/renewal lifetime caps, exact semantic schemas, prompt and raw/canonical LLM-response byte limits, validator agreement/disagreement hooks, read/read compatibility, both conflict classes, atomic multi-resource footprints, active capacity, strict FIFO ordering, queue bounds, release, cancellation, expiry, renewal, replay protection, lifecycle digests, nonpayability, prompt-injection schemas, and fail-closed unresolved results.

Current-source result: **49 passed**.

## Five-validator GLSim

Terminal 1:

```powershell
python tests/run_glsim.py --port 4113 --validators 5 --no-browser
```

Terminal 2:

```powershell
gltest tests/integration/test_semantic_resource_mutex_glsim.py -v -s --network localnet
```

The frozen current-source GLSim test supplied the same closed mock response independently to five validators and passed both tests, covering consensus transaction plumbing plus the complete grant → conflict queue → release → promotion state flow. Mocked GLSim is never evidence of heterogeneous real-model agreement.

Current-source result: **2 passed** with the server launched using `--validators 5` and five explicit mock validators.

## StudioNet

```powershell
gltest tests/integration/test_semantic_resource_mutex_live.py -v -s --network studionet -m semantic
```

StudioNet uses actual configured validators and inference. Record the contract address, transaction IDs when exposed, complete finalized result, and vote/agreement evidence when exposed before making a portal claim. A finalized transaction with failed execution is a failure; tests assert execution success explicitly.

Current-source result: **1 passed** in 138.51 seconds. Contract `0xde0a27C1FFa512a404B1958f33F5ccbcdc8a3986` returned `MAPPED`, stored status `LEASE_ACTIVE`, reads `[]`, and exact writes `[ORDER_LEDGER, WAREHOUSE_STOCK]`; `has_active_lease` was true at execution and durable readback. Finalized execution success was asserted. Independent `gen_getContractCode` readback exactly matched the current 38,820-byte source at SHA-256 `b603007a0280eff0b1aed672e365b8ec5da929e5a4dabffc486adf057b7360cc`. Durable CLI views read the policy, action, event, queue, and active-lease state. See [`deployments/studionet-2026-08-12-current-proof.json`](deployments/studionet-2026-08-12-current-proof.json).

The harness did not expose validator identities, model names, individual votes, vote counts, or transaction IDs, so none are claimed. The earlier V1 and pre-hardening V2 runs remain preserved as explicitly superseded historical records. Current-source Bradbury deployment and smoke-test evidence is pending.

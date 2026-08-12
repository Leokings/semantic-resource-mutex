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

The harness did not expose validator identities, model names, individual votes, vote counts, or transaction IDs, so none are claimed. The earlier V1 and pre-hardening V2 runs remain preserved as explicitly superseded historical records.

## Bradbury

Current-source deployment at `0x5DdACbe80468872442D88B37589652f7EcaB57ED` finalized `AGREE` with successful execution and five agreeing commit/reveal votes. `gen_getContractCode` readback matched the current 38,820-byte source exactly at SHA-256 `b603007a0280eff0b1aed672e365b8ec5da929e5a4dabffc486adf057b7360cc`; all 17 expected ABI methods and policy `SEMANTIC_RESOURCE_MUTEX_V2` were re-read.

The semantic test history is deliberately preserved:

- attempt 1, `0x921a4ccda0e131e1e6352ea5185c068716f51a6ce463d89c667666e0711ea8ca`: `FINALIZED/DISAGREE`, successful leader execution, no accepted action or event;
- attempt 2, `0x01a45ed75a1dac7f9149672cb115f81e60126c98137d27de98b9ffc6a7beb23d`: `FINALIZED/TIMEOUT`, successful leader execution, no accepted action or event;
- V3, `0xd34f5c9037a67c0ccd9fbfcde6f8f7b387579602733f84d46514713408c53a2c`: `FINALIZED/AGREE/FINISHED_WITH_RETURN`, five commits and reveals, with three `AGREE`, one `DETERMINISTIC_VIOLATION`, and one `TIMEOUT`.

V3 durably mapped the action to reads `[]` and writes `[ORDER_LEDGER, WAREHOUSE_STOCK]`, then recorded action 1 and event 1 (`LEASE_GRANTED`) with action digest `59dd024da0f6b76d45228fce6108acec43f53ca66cceeb0286b49c122b648bc7`. The post-finality read was intentionally read-only. Because finality arrived after the 1,800-second lease lifetime, `stored_status` was `LEASE_ACTIVE`, `effective_status` was `EXPIRED`, `has_active_lease` was false, and the active-lease view was empty. This demonstrates the documented stored/effective expiry distinction; no sweep transaction was submitted. Full sanitized evidence is in [`deployments/bradbury-2026-08-12-deployment-and-negative-smoke.json`](deployments/bradbury-2026-08-12-deployment-and-negative-smoke.json).

Bradbury receipts expose vote outcomes but do not establish model diversity, provider heterogeneity, or validator independence. None is claimed.

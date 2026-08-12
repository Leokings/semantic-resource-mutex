# Portal submission draft

Current-source StudioNet evidence is captured below. Replace GitHub and Bradbury placeholders only with frozen-source evidence before submission. Contracts `0xB23fBFC3Da5094fADD31fFA67c1E888CB8bE96b4` and `0x19636EF3628FdDD8Dbecd9F7bA2BBE6687514B42` run superseded revisions and must not be submitted for the current source.

## Title

```text
Semantic Resource Mutex — Reusable Intelligent Contract
```

## Notes / Description

```text
Built a reusable MIT-licensed Semantic Resource Mutex for GenLayer. Products submit bounded natural-language actions; validators independently map each action to canonical read/write IDs from an immutable closed registry. Unknown or ambiguous footprints fail closed. Deterministic logic grants all resources or none, detects read/write and write/write conflicts, enforces FIFO, expires and renews leases, authenticates release, and promotes queued work. Revocation cancels queued work and blocks renewal. Digest-linked state is bounded; a 32-action requester quota prevents one identity exhausting the 256-action deployment lifetime. Prompt and LLM-response sizes are capped. Includes 49 direct tests and 2 five-validator mocked GLSim tests. A no-mock StudioNet run deployed byte-identical source at 0xde0a27C1FFa512a404B1958f33F5ccbcdc8a3986, mapped exact writes ORDER_LEDGER and WAREHOUSE_STOCK, and granted an active lease. Builders can replace the registry and reuse lease views.
```

## Evidence entries

```text
GitHub Repository
<CURRENT_SOURCE_PRIVATE_REPOSITORY_URL_PENDING_PUBLICATION>

GitHub File — exact contract source
<CURRENT_SOURCE_PUBLIC_REPOSITORY_URL_PENDING>/blob/main/contracts/SemanticResourceMutex.py

GitHub File — testing and consensus design
<CURRENT_SOURCE_PUBLIC_REPOSITORY_URL_PENDING>/blob/main/TESTING.md

GenLayer Explorer Contract
<CURRENT_SOURCE_BRADBURY_EXPLORER_URL_PENDING>

GenLayer StudioNet Contract Address
0xde0a27C1FFa512a404B1958f33F5ccbcdc8a3986

GitHub File — finalized StudioNet deployment proof
<CURRENT_SOURCE_PUBLIC_REPOSITORY_URL_PENDING>/blob/main/deployments/studionet-2026-08-12-current-proof.json
```

Submit under **Intelligent Contracts** only after replacing placeholders and adding finalized Bradbury evidence before claiming Bradbury. The current StudioNet source already matches byte-for-byte. Do not claim atomic enforcement of external work, heterogeneous validators, model names, vote counts, or transaction IDs; the harness exposed none of the latter evidence.

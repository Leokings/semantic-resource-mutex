# Portal submission draft

The repository is private while submission materials are being finalized. Make it public immediately before portal submission so reviewers can open every GitHub evidence link. The Bradbury deployment and V3 semantic transaction below are finalized and match the current source byte-for-byte.

## Contribution date

```text
08/12/2026
```

## Title

```text
Semantic Resource Mutex - Reusable Intelligent Contract
```

## Notes / Description - 991/1000 characters

```text
Built a reusable MIT-licensed Semantic Resource Mutex for GenLayer. Products submit bounded natural-language actions; validator consensus maps each action to canonical read/write IDs from an immutable closed registry. Unknown or ambiguous footprints fail closed. Deterministic logic grants all resources or none, detects read/write and write/write conflicts, enforces bounded FIFO, handles expiry and renewal, authenticates release, and promotes queued work. Revocation cancels queued work and blocks renewal. Digest-linked state and quotas bound storage; prompt and model-output sizes are capped. Includes 49 direct tests, 2 five-validator mocked GLSim tests, and no-mock StudioNet evidence. On Bradbury, byte-identical v0.2.0 source deployed at 0x5DdACbe80468872442D88B37589652f7EcaB57ED; V3 finalized AGREE with successful execution, exact writes ORDER_LEDGER and WAREHOUSE_STOCK, and a durable LEASE_GRANTED record. Builders can replace the registry and reuse the stable lease interface.
```

## Evidence entries

```text
GitHub Repository
https://github.com/Leokings/semantic-resource-mutex

GitHub File - exact contract source
https://github.com/Leokings/semantic-resource-mutex/blob/main/contracts/SemanticResourceMutex.py

GitHub File - testing and consensus design
https://github.com/Leokings/semantic-resource-mutex/blob/main/TESTING.md

GitHub File - security audit
https://github.com/Leokings/semantic-resource-mutex/blob/main/SECURITY_AUDIT.md

GitHub File - finalized Bradbury deployment and semantic proof
https://github.com/Leokings/semantic-resource-mutex/blob/main/deployments/bradbury-2026-08-12-deployment-and-negative-smoke.json

GenLayer Explorer Contract
https://explorer-bradbury.genlayer.com/address/0x5DdACbe80468872442D88B37589652f7EcaB57ED

GenLayer StudioNet Contract Address
0xde0a27C1FFa512a404B1958f33F5ccbcdc8a3986

GitHub File - finalized StudioNet deployment proof
https://github.com/Leokings/semantic-resource-mutex/blob/main/deployments/studionet-2026-08-12-current-proof.json
```

Submit under **Intelligent Contracts** after making the repository public and checking every link in a logged-out browser. Do not claim atomic enforcement of external work, unanimous semantic voting, heterogeneous validator models/providers, validator independence, or general mapping accuracy. The first two Bradbury semantic attempts remain disclosed in the proof; V3 is the finalized positive transaction.

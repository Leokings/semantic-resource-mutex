"""Hosted-network semantic smoke test; no mocked validators."""

import json
from pathlib import Path

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address


REGISTRY = [
    {
        "id": "ORDER_LEDGER",
        "label": "Order ledger",
        "description": "The authoritative collection of purchase orders and their lifecycle states.",
    },
    {
        "id": "WAREHOUSE_STOCK",
        "label": "Warehouse stock",
        "description": "Current sellable inventory quantities reserved and held by the warehouse.",
    },
]


@pytest.mark.semantic
def test_live_consensus_maps_and_grants_exact_multi_resource_footprint():
    path = Path(__file__).resolve().parents[2] / "contracts" / "SemanticResourceMutex.py"
    factory = get_contract_factory(contract_file_path=path)
    deploy_receipt = factory.deploy_contract_tx(
        args=[json.dumps(REGISTRY, separators=(",", ":")), 4, 4, 1800],
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    assert tx_execution_succeeded(deploy_receipt), deploy_receipt
    contract = factory.build_contract(extract_contract_address(deploy_receipt))
    print(f"contract_address={contract.address}")
    receipt = contract.request_lease(
        args=[
            "LIVE-ORDER-001",
            "Read current warehouse stock, reserve one sellable unit, and create the corresponding purchase order.",
            300,
        ]
    ).transact(wait_transaction_status=TransactionStatus.FINALIZED)
    assert tx_execution_succeeded(receipt), receipt
    action = contract.get_action(args=[1]).call()
    print(
        f"action_id=1 classification={action['classification']} status={action['status']} "
        f"reads={action['read_resource_ids']} writes={action['write_resource_ids']}"
    )
    assert action["classification"] == "MAPPED"
    assert action["status"] == "LEASE_ACTIVE"
    assert action["read_resource_ids"] == []
    assert action["write_resource_ids"] == ["ORDER_LEDGER", "WAREHOUSE_STOCK"]
    assert contract.has_active_lease(args=[1]).call() is True


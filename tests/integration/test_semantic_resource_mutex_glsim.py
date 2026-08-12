"""Five-validator GLSim consensus coverage for SemanticResourceMutex."""

import json
from pathlib import Path

from gltest import get_contract_factory, get_validator_factory
from gltest.assertions import tx_execution_failed, tx_execution_succeeded
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
ORDER_WRITE = json.dumps(
    {
        "classification": "MAPPED",
        "read_resource_ids": [],
        "write_resource_ids": ["ORDER_LEDGER"],
    },
    separators=(",", ":"),
)
PROMPT_KEY = "Classify one proposed action into an exact concurrency footprint"


def _receipt_dump(receipt):
    return json.dumps(receipt, indent=2, sort_keys=True, default=str)


def _validator_context(response=ORDER_WRITE):
    validators = get_validator_factory().batch_create_mock_validators(
        5,
        mock_llm_response={"nondet_exec_prompt": {PROMPT_KEY: response}},
    )
    return {"validators": [validator.to_dict() for validator in validators]}


def _deploy():
    path = Path(__file__).resolve().parents[2] / "contracts" / "SemanticResourceMutex.py"
    factory = get_contract_factory(contract_file_path=path)
    receipt = factory.deploy_contract_tx(
        args=[json.dumps(REGISTRY, separators=(",", ":")), 4, 4, 3600],
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    assert tx_execution_succeeded(receipt), _receipt_dump(receipt)
    return factory.build_contract(extract_contract_address(receipt))


def _request(contract, reference):
    receipt = contract.request_lease(
        args=[
            reference,
            "Create a new purchase order and persist it in the authoritative order ledger.",
            300,
        ]
    ).transact(
        transaction_context=_validator_context(),
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    assert tx_execution_succeeded(receipt), _receipt_dump(receipt)


def test_five_validator_consensus_grants_queues_and_promotes():
    contract = _deploy()
    _request(contract, "ORDER-001")
    _request(contract, "ORDER-002")
    first = contract.get_action(args=[1]).call()
    second = contract.get_action(args=[2]).call()
    assert first["status"] == "LEASE_ACTIVE"
    assert second["status"] == "QUEUED"
    assert second["blocking_action_ids"] == [1]
    receipt = contract.release_lease(args=[1]).transact(
        wait_transaction_status=TransactionStatus.FINALIZED
    )
    assert tx_execution_succeeded(receipt), _receipt_dump(receipt)
    assert contract.get_action(args=[1]).call()["status"] == "RELEASED"
    assert contract.get_action(args=[2]).call()["status"] == "LEASE_ACTIVE"
    assert contract.get_queue(args=[]).call()["count"] == 0
    assert contract.get_event_count(args=[]).call() == 4


def test_five_validator_malformed_classification_fails_closed():
    contract = _deploy()
    receipt = contract.request_lease(
        args=[
            "BAD-001",
            "Create a new purchase order and persist it in the authoritative order ledger.",
            300,
        ]
    ).transact(
        transaction_context=_validator_context('{"classification":"MAPPED"}'),
        wait_transaction_status=TransactionStatus.FINALIZED,
    )
    assert tx_execution_failed(receipt), _receipt_dump(receipt)
    assert contract.get_action_count(args=[]).call() == 0


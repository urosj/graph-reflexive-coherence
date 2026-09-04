"""Load accepted historical and D11 source-admission contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from .canonical import digest, load_json_object, record_digest
from .errors import SourceAdmissionError


def load_et_c0_contract(path: Path) -> dict[str, Any]:
    record = load_json_object(path)
    if record.get("schema") != "grcv4_explorer_ET_C0_contract_v1":
        raise SourceAdmissionError("ET-C0 schema is not admitted")
    if record.get("status") != "accepted":
        raise SourceAdmissionError("ET-C0 is not accepted")
    declared = record.get("record_digest")
    if not isinstance(declared, str) or declared != record_digest(
        record, "record_digest"
    ):
        raise SourceAdmissionError("ET-C0 record digest mismatch")
    source_contract = record.get("source_contract")
    if not isinstance(source_contract, dict):
        raise SourceAdmissionError("ET-C0 source contract is missing")
    records = source_contract.get("records")
    if not isinstance(records, list) or len(records) != source_contract.get(
        "record_count"
    ):
        raise SourceAdmissionError("ET-C0 source inventory is malformed")
    return record


def admitted_rows(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows = contract["source_contract"]["records"]
    return cast(list[dict[str, Any]], rows)


def load_d11_source_contract(path: Path) -> dict[str, Any]:
    """Load the accepted append-only D11 source admission contract."""

    record = load_json_object(path)
    if (
        record.get("schema") != "grcv4_explorer_ET_C10_D11_source_contract_v1"
        or record.get("status") != "accepted"
    ):
        raise SourceAdmissionError("D11 source contract is not accepted")
    if record.get("record_digest") != record_digest(record, "record_digest"):
        raise SourceAdmissionError("D11 source contract digest mismatch")
    source_contract = record.get("source_contract")
    if not isinstance(source_contract, dict):
        raise SourceAdmissionError("D11 source contract is missing")
    records = source_contract.get("records")
    if not isinstance(records, list) or len(records) != source_contract.get(
        "record_count"
    ):
        raise SourceAdmissionError("D11 source inventory is malformed")
    if source_contract.get("source_bundle_candidate_digest") != digest(records):
        raise SourceAdmissionError("D11 source inventory digest mismatch")
    return record

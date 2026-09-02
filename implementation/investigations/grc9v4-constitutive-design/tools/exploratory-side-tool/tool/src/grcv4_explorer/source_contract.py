"""Load the accepted ET-C0 source admission contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from .canonical import load_json_object, record_digest
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

#!/usr/bin/env python3
"""Focused regression tests for the ET-C10 D11 forensic overlay."""

from __future__ import annotations

import copy
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.adapters import adapt_source  # noqa: E402
from grcv4_explorer.errors import GraphInvariantError, SourceAdmissionError  # noqa: E402
from grcv4_explorer.forensic import (  # noqa: E402
    contract_provenance,
    debt_lifecycle,
    reconstruction_path,
)
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_d11_source_contract,
)
from grcv4_explorer.successor import (  # noqa: E402
    D11_SOURCE_CONTRACT,
    load_successor_forensic_context,
    validate_d11_graph,
)


def expect_error(error: type[Exception], operation: object) -> None:
    try:
        operation()  # type: ignore[operator]
    except error:
        return
    raise AssertionError(f"expected {error.__name__}")


def main() -> int:
    repo_root = repository_root()
    records = SIDE_TOOL_ROOT / "records"
    context = load_successor_forensic_context(repo_root, SIDE_TOOL_ROOT)

    c_claim = reconstruction_path(context, "D11-C-CL-O-001")
    g9_claim = reconstruction_path(context, "D11-G9-CL-N-001")
    assert c_claim["rows"][0]["source_ref"]["record_id"] == (
        "GRC9V4-D11-C-PROVENANCE-SUPPLEMENT-v1"
    )
    assert g9_claim["rows"][0]["source_ref"]["record_id"] == (
        "GRC9V4-D11-G9-PROVENANCE-SUPPLEMENT-v1"
    )
    c_contract = contract_provenance(context, "D11-C-EC-C-J0-CURRENT")
    assert c_contract["rows"][0]["payload"]["support_disposition"] == [
        "accepted_bounded_D11_C_successor"
    ]
    g9_contract = contract_provenance(context, "D11-G9-EC-LEGACY-DEFINED-DOMAIN")
    assert "GRC9V4_compatibility_boundary" in str(
        g9_contract["rows"][0]["payload"]["support_disposition"]
    )
    assert (
        debt_lifecycle(context, "D11-C-DEBT-BASELINE-TRANSPORT-AUTHORITY")["row_count"]
        == 5
    )
    assert (
        debt_lifecycle(context, "D11-G9-DEBT-CANONICAL-PORT-ALLOCATION")["row_count"]
        == 6
    )

    contract = load_d11_source_contract(records / D11_SOURCE_CONTRACT)
    bad_admission = copy.deepcopy(admitted_rows(contract)[0])
    bad_admission["file_sha256"] = "0" * 64
    expect_error(
        SourceAdmissionError,
        lambda: adapt_source(repo_root, bad_admission),
    )
    tampered = copy.deepcopy(context.graph)
    for row in tampered["nodes"]:
        if row["node_id"] == "current_claim:D11-C-CL-O-001":
            row["attributes"]["claim_class"] = "normative"
            break
    expect_error(
        GraphInvariantError,
        lambda: validate_d11_graph(tampered, context.graph),
    )
    expect_error(
        KeyError,
        lambda: reconstruction_path(context, "D10_2_CL_N_001"),
    )

    print("ET_C10_D11_TEST_PASS checks=12 fail_closed=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Focused fail-closed tests for the ET-C11 D11 UX candidate."""

from __future__ import annotations

import copy
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import load_json_object, record_digest  # noqa: E402
from grcv4_explorer.errors import GraphInvariantError  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.successor import D11_FORENSIC_ADMISSION  # noqa: E402
from grcv4_explorer.successor_ux import (  # noqa: E402
    D11_UX_BUNDLE,
    validate_d11_ux_bundle,
)


def expect_failure(operation: object, fragment: str) -> None:
    try:
        operation()  # type: ignore[operator]
    except GraphInvariantError as error:
        if fragment not in str(error):
            raise AssertionError(f"unexpected failure: {error}") from error
        return
    raise AssertionError(f"expected failure containing: {fragment}")


def resign(bundle: dict[str, object]) -> None:
    bundle["bundle_digest"] = record_digest(bundle, "bundle_digest")


def main() -> int:
    repository_root()
    records = SIDE_TOOL_ROOT / "records"
    admission = load_json_object(records / D11_FORENSIC_ADMISSION)
    bundle = load_json_object(records / D11_UX_BUNDLE)
    validate_d11_ux_bundle(bundle, admission)

    stale = copy.deepcopy(bundle)
    stale["source_identities"]["ET_C10_record_digest"] = "0" * 64
    resign(stale)
    expect_failure(
        lambda: validate_d11_ux_bundle(stale, admission), "ET-C10 identity mismatch"
    )

    missing = copy.deepcopy(bundle)
    missing["views"].pop("current_claim:D11-C-CL-O-001")
    resign(missing)
    expect_failure(
        lambda: validate_d11_ux_bundle(missing, admission),
        "catalog/view identity mismatch",
    )

    wrong_count = copy.deepcopy(bundle)
    wrong_count["population_counts"]["current_claim"] = 3
    resign(wrong_count)
    expect_failure(
        lambda: validate_d11_ux_bundle(wrong_count, admission),
        "population mismatch",
    )

    tampered_trace = copy.deepcopy(bundle)
    tampered_trace["views"]["current_claim:D11-C-CL-O-001"]["output"]["rows"][0][
        "classification"
    ] = "normative"
    resign(tampered_trace)
    expect_failure(
        lambda: validate_d11_ux_bundle(tampered_trace, admission),
        "output digest mismatch",
    )

    widened = copy.deepcopy(bundle)
    widened["authority"]["browser_claim_promotion"] = True
    resign(widened)
    expect_failure(
        lambda: validate_d11_ux_bundle(widened, admission), "authority boundary widened"
    )
    print("ET_C11_D11_UX_TEST_PASS checks=6 fail_closed=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

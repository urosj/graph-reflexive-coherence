#!/usr/bin/env python3
"""Adversarial fixture pressure for the ET-C9 coverage contract."""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Callable


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import load_json_object  # noqa: E402
from grcv4_explorer.closeout import validate_coverage  # noqa: E402
from grcv4_explorer.errors import SourceAdmissionError  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402


checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        raise RuntimeError(message)


def reject(label: str, operation: Callable[[], None]) -> None:
    global checks
    checks += 1
    try:
        operation()
    except SourceAdmissionError:
        return
    raise RuntimeError(f"ET-C9 fixture did not fail closed: {label}")


def mutate(source: dict[str, object], operation: Callable[[dict[str, object]], None]) -> None:
    value = copy.deepcopy(source)
    operation(value)
    validate_coverage(value)


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    coverage = load_json_object(
        SIDE_TOOL_ROOT / "records/ETC9ScenarioCoverageAndUsability.json"
    )
    validate_coverage(coverage)
    check(coverage["scenario_count"] == 35, "scenario count")
    check(coverage["forensic_api_count"] == 9, "API count")
    check(coverage["web_view_count"] == 8, "view count")

    reject("missing scenario", lambda: mutate(coverage, lambda row: row["scenario_rows"].pop()))
    reject(
        "duplicate scenario",
        lambda: mutate(
            coverage,
            lambda row: row["scenario_rows"].append(copy.deepcopy(row["scenario_rows"][0])),
        ),
    )
    reject(
        "wrong owner",
        lambda: mutate(coverage, lambda row: row["scenario_rows"][0].update(owner_iteration=8)),
    )
    reject(
        "unreconciled status",
        lambda: mutate(coverage, lambda row: row["scenario_rows"][0].update(status="pending")),
    )
    reject(
        "authority promotion",
        lambda: mutate(
            coverage,
            lambda row: row["scenario_rows"][0].update(scientific_claim_added=True),
        ),
    )
    reject(
        "malformed owner digest",
        lambda: mutate(
            coverage,
            lambda row: row["scenario_rows"][0].update(owner_record_digest="bad"),
        ),
    )
    reject(
        "missing API",
        lambda: mutate(coverage, lambda row: row["forensic_api_coverage"].pop("gate_act")),
    )
    reject(
        "empty API coverage",
        lambda: mutate(coverage, lambda row: row["forensic_api_coverage"].update(gate_act=[])),
    )
    reject(
        "unknown API scenario",
        lambda: mutate(
            coverage,
            lambda row: row["forensic_api_coverage"].update(gate_act=["F99"]),
        ),
    )
    reject(
        "missing web view",
        lambda: mutate(coverage, lambda row: row["web_view_coverage"].pop("ripple_view")),
    )
    reject(
        "empty web view coverage",
        lambda: mutate(
            coverage,
            lambda row: row["web_view_coverage"].update(ripple_view=[]),
        ),
    )
    reject(
        "unknown web scenario",
        lambda: mutate(
            coverage,
            lambda row: row["web_view_coverage"].update(ripple_view=["C99"]),
        ),
    )
    print(f"ET_C9_FOCUSED_TEST_PASS checks={checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

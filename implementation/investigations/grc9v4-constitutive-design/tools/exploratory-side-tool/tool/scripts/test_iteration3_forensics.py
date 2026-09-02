#!/usr/bin/env python3
"""Focused ET-C3 forensic API and notebook fixture checks."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes  # noqa: E402
from grcv4_explorer.forensic import (  # noqa: E402
    candidate_career,
    contract_provenance,
    debt_lifecycle,
    gate_act,
    gate_contribution,
    load_forensic_context,
    negative_claims,
    object_dependents,
    pruned_choices_at,
    reconstruction_path,
    write_trace,
)
from grcv4_explorer.paths import repository_root  # noqa: E402


def expect_error(label: str, error_type: type[BaseException], call: Callable[[], Any]) -> None:
    try:
        call()
    except error_type:
        return
    raise RuntimeError(f"ET-C3 fixture did not fail closed: {label}")


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    context = load_forensic_context(repo_root, SIDE_TOOL_ROOT)
    checks = 0

    traces = [
        gate_act(context, "GRC9V4-CD-D7V2-v1"),
        debt_lifecycle(context, "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION"),
        reconstruction_path(context, "D10-CL-N-001"),
        candidate_career(context, "V4-A-temporalized-W"),
        candidate_career(context, "V4-B-independent-derived-carrier"),
        pruned_choices_at(context, "GRC9V4-CD-D1-v1"),
        negative_claims(context),
        object_dependents(context, "CORE-C-AUTHORITY"),
        contract_provenance(context, "D10.2-EC-PARENT-CORE-C-AUTHORITY"),
        gate_contribution(context, "GRC9V4-CD-D7V2-v1"),
    ]
    if any(trace["output_class"] != "forensic_evidence_trace" for trace in traces):
        raise RuntimeError("forensic API emitted a non-forensic class")
    checks += 1
    if any(not row["edge_refs"] for trace in traces for row in trace["rows"]):
        raise RuntimeError("forensic API emitted an unbound row")
    checks += 1
    if [canonical_bytes(value) for value in traces] != [
        canonical_bytes(gate_act(context, "GRC9V4-CD-D7V2-v1")),
        canonical_bytes(
            debt_lifecycle(
                context, "GTRS-COMP-DEBT-MATCHED-RUNTIME-DISCRIMINATION"
            )
        ),
        canonical_bytes(reconstruction_path(context, "D10-CL-N-001")),
        canonical_bytes(candidate_career(context, "V4-A-temporalized-W")),
        canonical_bytes(
            candidate_career(context, "V4-B-independent-derived-carrier")
        ),
        canonical_bytes(pruned_choices_at(context, "GRC9V4-CD-D1-v1")),
        canonical_bytes(negative_claims(context)),
        canonical_bytes(object_dependents(context, "CORE-C-AUTHORITY")),
        canonical_bytes(
            contract_provenance(context, "D10.2-EC-PARENT-CORE-C-AUTHORITY")
        ),
        canonical_bytes(gate_contribution(context, "GRC9V4-CD-D7V2-v1")),
    ]:
        raise RuntimeError("forensic API output is nondeterministic")
    checks += 1

    expect_error(
        "unknown gate",
        KeyError,
        lambda: gate_act(context, "missing"),
    )
    checks += 1
    expect_error(
        "unknown debt",
        KeyError,
        lambda: debt_lifecycle(context, "missing"),
    )
    checks += 1
    expect_error(
        "unknown claim",
        KeyError,
        lambda: reconstruction_path(context, "missing"),
    )
    checks += 1
    expect_error(
        "unknown candidate",
        KeyError,
        lambda: candidate_career(context, "missing"),
    )
    checks += 1
    expect_error(
        "unknown object",
        KeyError,
        lambda: object_dependents(context, "missing"),
    )
    checks += 1
    expect_error(
        "unknown contract",
        KeyError,
        lambda: contract_provenance(context, "missing"),
    )
    checks += 1

    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / "trace.json"
        write_trace(target, traces[0])
        if target.read_bytes() != canonical_bytes(traces[0]) + b"\n":
            raise RuntimeError("write_trace is not canonical")
        checks += 1
        invalid = dict(traces[0])
        invalid["trace_digest"] = "0" * 64
        expect_error(
            "invalid trace digest",
            ValueError,
            lambda: write_trace(target, invalid),
        )
        checks += 1
        invalid_class = dict(traces[0])
        invalid_class["output_class"] = "speculative_structural_counterfactual"
        expect_error(
            "speculative trace write",
            ValueError,
            lambda: write_trace(target, invalid_class),
        )
        checks += 1

    notebook = json.loads(
        (TOOL_ROOT / "notebooks/forensic_recipes.ipynb").read_text(encoding="utf-8")
    )
    code = "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell["cell_type"] == "code"
    )
    required_calls = {
        "load_forensic_context",
        "reconstruction_path",
        "candidate_career",
        "write_trace",
    }
    if not all(name in code for name in required_calls):
        raise RuntimeError("notebook does not call the pure I3 API")
    if any(name in code for name in ("json.load", "ETC2GraphSnapshot", "subprocess")):
        raise RuntimeError("notebook duplicates source or graph logic")
    checks += 1

    report = json.loads(
        (SIDE_TOOL_ROOT / "records/ETC3ForensicScenarioReport.json").read_text()
    )
    if report["scenario_count"] != 12 or report["output_class"] != (
        "forensic_evidence_trace"
    ):
        raise RuntimeError("scenario report population is malformed")
    checks += 1
    if (SIDE_TOOL_ROOT / "records/ETC3ForensicScenarioReport.json").stat().st_size > (
        2 * 1024 * 1024
    ):
        raise RuntimeError("forensic report copied an excessive artifact surface")
    checks += 1

    print(f"ET_C3_TEST_PASS checks={checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

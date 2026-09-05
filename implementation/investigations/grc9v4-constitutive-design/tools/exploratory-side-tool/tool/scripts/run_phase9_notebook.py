#!/usr/bin/env python3
"""Execute the Phase 9 notebook's real code cells using the repository .venv."""

import json
from pathlib import Path
import sys

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.phase9_verification import verification_status, pressure_projection  # noqa: E402


def main():
    root = repository_root()
    if Path(sys.prefix).resolve() != (root / ".venv").resolve():
        raise RuntimeError("use the existing repository .venv")
    notebook = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
    namespace = {"PHASE9_REPO_ROOT": root}
    cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
    for index, cell in enumerate(cells):
        exec(
            compile(
                "".join(cell["source"]),
                f"phase9_verification.ipynb:cell-{index + 1}",
                "exec",
            ),
            namespace,
        )
    observed = namespace["phase9_status"]
    if (
        observed != verification_status(root)
        or observed["current_boundary"] != "passed"
    ):
        raise RuntimeError("notebook/API status mismatch or held current boundary")
    destination = TOOL / "generated/phase9-verification/notebook-status.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(observed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    )
    probe = namespace["phase9_pressure"]
    if (
        probe != pressure_projection(root, "normal_entry_forbidden_source")
        or probe["candidate_decision"] != "rejected"
        or probe["assertion_result"] != "passed"
    ):
        raise RuntimeError(
            "notebook promoted a passing negative assertion into candidate admission"
        )
    destination.with_name("notebook-pressure.json").write_text(
        json.dumps(probe, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    )
    print(
        f"PHASE9_NOTEBOOK_PASS cells={len(cells)} API_identity=byte_exact runtime_authorized={str(observed['runtime_authorized']).lower()} P9_G1={'accepted' if observed['P9_G1_accepted'] else 'pending'} runtime_support=empty"
    )


if __name__ == "__main__":
    main()

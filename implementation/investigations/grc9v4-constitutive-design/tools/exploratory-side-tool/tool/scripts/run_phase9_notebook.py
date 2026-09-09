#!/usr/bin/env python3
"""Execute the Phase 9 notebook's real code cells using the repository .venv."""

import argparse
import json
from pathlib import Path
import sys

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.phase9_verification import verification_status, pressure_projection  # noqa: E402
from grcv4_explorer.receipt_parents import parent_authority  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-only", action="store_true",
                        help="query current authority without requesting cached pressure evidence")
    args = parser.parse_args()
    root = repository_root()
    if Path(sys.prefix).resolve() != (root / ".venv").resolve():
        raise RuntimeError("use the existing repository .venv")
    notebook = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
    namespace = {"PHASE9_REPO_ROOT": root, "PHASE9_STATUS_ONLY": args.status_only}
    cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
    if args.status_only:
        cells = [c for c in cells if c["id"] in {"discover-and-import", "query-status"}]
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
    filename = "notebook-current-status.json" if args.status_only else "notebook-status.json"
    destination = TOOL / "generated/phase9-verification" / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(observed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    )
    if args.status_only:
        if namespace["phase9_pressure"] is not None:
            raise RuntimeError("status-only notebook must not claim pressure evidence")
        print("PHASE9_NOTEBOOK_STATUS_PASS API_identity=byte_exact pressure=not_requested runtime_support=empty")
        return
    probe = namespace["phase9_pressure"]
    parents = namespace["phase9_parent_authority"]
    if parents != parent_authority(root, TOOL.parent):
        raise RuntimeError("notebook/API parent-authority identity mismatch")
    destination.with_name("notebook-parent-authority.json").write_text(
        json.dumps(parents, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    )
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

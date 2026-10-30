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
from grcv4_explorer.abundance import abundance_authority  # noqa: E402
from grcv4_explorer.a_initializer import initializer_authority  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-only", action="store_true",
                        help="query current authority without requesting cached pressure evidence")
    parser.add_argument("--tranche8-only", action="store_true",
                        help="execute the real retained Tranche 8 query cell without historical or numerical reruns")
    parser.add_argument("--aos-only", action="store_true",
                        help="execute the current A_OS retained-evidence cell without numerical reruns")
    parser.add_argument("--cpc-only", action="store_true", help="execute the C_PC retained-evidence cell")
    parser.add_argument("--ccipc-only", action="store_true", help="execute the C_CI+PC retained-evidence cell")
    parser.add_argument("--acipc-only", action="store_true", help="execute the A_CI+PC retained-evidence cell")
    args = parser.parse_args()
    if sum((args.status_only, args.tranche8_only, args.aos_only, args.cpc_only, args.ccipc_only, args.acipc_only)) > 1:
        parser.error("select one focused notebook mode")
    root = repository_root()
    if Path(sys.prefix).resolve() != (root / ".venv").resolve():
        raise RuntimeError("use the existing repository .venv")
    notebook = json.loads((TOOL / "notebooks/phase9_verification.ipynb").read_text())
    namespace = {"PHASE9_REPO_ROOT": root, "PHASE9_STATUS_ONLY": args.status_only}
    cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
    if args.status_only:
        cells = [c for c in cells if c["id"] in {"discover-and-import", "query-status"}]
    if args.tranche8_only:
        cells = [c for c in cells if c["id"] in {"discover-and-import", "query-tranche8"}]
    if args.aos_only:
        cells = [c for c in cells if c["id"] in {"discover-and-import", "query-aos"}]
    if args.cpc_only:
        cells = [c for c in cells if c["id"] in {"discover-and-import", "query-cpc"}]
    if args.ccipc_only:
        cells = [c for c in cells if c["id"] in {"discover-and-import", "query-ccipc"}]
    if args.acipc_only:
        cells = [c for c in cells if c["id"] in {"discover-and-import", "query-acipc"}]
    for index, cell in enumerate(cells):
        exec(
            compile(
                "".join(cell["source"]),
                f"phase9_verification.ipynb:cell-{index + 1}",
                "exec",
            ),
            namespace,
        )
    if args.acipc_only:
        from grcv4_explorer.acipc import acipc_status
        if namespace["phase9_acipc"] != acipc_status(root):
            raise RuntimeError("notebook/API A_CI+PC mismatch")
        print("PHASE9_ACIPC_NOTEBOOK_PASS native_rerun=false")
        return
    if args.ccipc_only:
        from grcv4_explorer.ccipc import ccipc_status
        if namespace["phase9_ccipc"] != ccipc_status(root):
            raise RuntimeError("notebook/API C_CI+PC mismatch")
        print("PHASE9_CCIPC_NOTEBOOK_PASS native_rerun=false")
        return
    if args.cpc_only:
        from grcv4_explorer.cpc import cpc_status
        if namespace["phase9_cpc"] != cpc_status(root):
            raise RuntimeError("notebook/API C_PC mismatch")
        print("PHASE9_CPC_NOTEBOOK_PASS native_rerun=false")
        return
    if args.aos_only:
        from grcv4_explorer.aos import aos_status
        if namespace["phase9_aos"] != aos_status(root):
            raise RuntimeError("notebook/API A_OS mismatch")
        print("PHASE9_AOS_NOTEBOOK_PASS native_rerun=false")
        return
    if args.tranche8_only:
        from grcv4_explorer.tranche8 import tranche8_status
        observed = namespace["phase9_tranche8"]
        if observed != tranche8_status(root):
            raise RuntimeError("notebook/API Tranche 8 mismatch")
        print("PHASE9_TRANCHE8_NOTEBOOK_PASS cells=2 native_rerun=false "
              f"accepted_cells={observed['coverage']['accepted_cells']}")
        return
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
        print("PHASE9_NOTEBOOK_STATUS_PASS API_identity=byte_exact pressure=not_requested "
              f"accepted_exact_profiles={len(observed['accepted_generic_runtime_support'])}")
        return
    probe = namespace["phase9_pressure"]
    parents = namespace["phase9_parent_authority"]
    if parents != parent_authority(root, TOOL.parent):
        raise RuntimeError("notebook/API parent-authority identity mismatch")
    abundance = namespace["phase9_abundance_authority"]
    if abundance != abundance_authority(root, TOOL.parent):
        raise RuntimeError("notebook/API abundance-authority identity mismatch")
    initializer = namespace["phase9_initializer_authority"]
    if initializer != initializer_authority(root, TOOL.parent):
        raise RuntimeError("notebook/API initializer-authority identity mismatch")
    destination.with_name("notebook-initializer-authority.json").write_text(
        json.dumps(initializer, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    )
    destination.with_name("notebook-abundance-authority.json").write_text(
        json.dumps(abundance, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    )
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
        f"PHASE9_NOTEBOOK_PASS cells={len(cells)} API_identity=byte_exact runtime_authorized={str(observed['runtime_authorized']).lower()} P9_G1={'accepted' if observed['P9_G1_accepted'] else 'pending'} accepted_exact_profiles={len(observed['accepted_generic_runtime_support'])}"
    )


if __name__ == "__main__":
    main()

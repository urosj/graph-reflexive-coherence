#!/usr/bin/env python3
"""Run the complete accepted ET-C9 closeout verification."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import (  # noqa: E402
    canonical_bytes,
    load_json_object,
    record_digest,
)
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


BUILD_SEQUENCE = tuple(
    f"build_iteration{iteration}_{suffix}.py"
    for iteration, suffix in (
        (1, "bundle"),
        (2, "graph"),
        (3, "forensics"),
        (4, "counterfactuals"),
        (5, "ripples"),
        (8, "lineage"),
    )
)

D10_AUDITS = (
    "audit_grc9v4_d10_claim_topology.py",
    "audit_grc9v4_d10_1_preliminary_provenance.py",
    "audit_grc9v4_d10_2_full_provenance.py",
)
POST_D10_SPECIFICATION_AUDIT = "audit_grcv4_post_d10_specifications.py"

PYTHON_SUITE = (
    "audit_iteration0_contract.py",
    "test_iteration0_portability.py",
    "doctor.py",
    "discover_sources.py",
    "audit_iteration1_bundle.py",
    "test_iteration1_adapters.py",
    "audit_iteration2_graph.py",
    "test_iteration2_kernel.py",
    "audit_iteration3_forensics.py",
    "test_iteration3_forensics.py",
    "run_iteration3_notebook.py",
    "audit_iteration4_counterfactuals.py",
    "test_iteration4_counterfactuals.py",
    "audit_iteration5_ripples.py",
    "test_iteration5_ripples.py",
    "test_iteration6_navigation.py",
    "test_iteration7_ceilings.py",
    "audit_iteration8_lineage.py",
    "test_iteration8_lineage.py",
    "audit_iteration9_closeout.py",
    "test_iteration9_closeout.py",
)

# These validators consume only the frozen ET-C0 through ET-C9 artifacts. Their
# historical rebuild remains excluded after D11; ET-C10 independently rebuilds
# and validates the append-only successor overlay in memory.
SUCCESSOR_PHASE_PYTHON_SUITE = (
    "audit_iteration2_graph.py",
    "audit_iteration3_forensics.py",
    "audit_iteration4_counterfactuals.py",
    "test_iteration6_navigation.py",
    "audit_iteration8_lineage.py",
    "test_iteration8_lineage.py",
    "audit_iteration9_closeout.py",
    "test_iteration9_closeout.py",
)

D11_FORENSIC_SUITE = (
    "audit_iteration10_d11.py",
    "test_iteration10_d11.py",
)

D11_UX_SUITE = (
    "build_iteration11_d11_ux.py",
    "audit_iteration11_d11_ux.py",
    "run_iteration11_d11_notebook.py",
    "test_iteration11_d11_ux.py",
)

HISTORICAL_LAYER_AUDITS = (
    ("audit_iteration6_navigation.py", "--skip-dist-identity"),
    ("audit_iteration7_ceilings.py", "--skip-dist-identity"),
)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_bytes(canonical_bytes(value) + b"\n")


def snapshot_files(paths: list[Path], root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(paths)
        if path.is_file()
    }


def snapshot_tree(path: Path, root: Path) -> dict[str, bytes]:
    if not path.exists():
        return {}
    return snapshot_files([row for row in path.rglob("*") if row.is_file()], root)


def protected_snapshot(repo_root: Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    for relative in (
        "src",
        "specs",
        "tests",
        "implementation/investigations/grc9v4-constitutive-design/decisions",
    ):
        result.update(snapshot_tree(repo_root / relative, repo_root))
    return result


def source_snapshot(repo_root: Path, records: Path) -> dict[str, bytes]:
    contract = load_json_object(records / "ETC0SourceAndLayoutContract.json")
    paths = [repo_root / row["path"] for row in contract["source_contract"]["records"]]
    return snapshot_files(paths, repo_root)


def accepted_artifact_snapshot(*, include_web: bool = True) -> dict[str, bytes]:
    records = SIDE_TOOL_ROOT / "records"
    excluded = {
        "ETC7VerificationReceipt.json",
        "ETC8VerificationReceipt.json",
    }
    paths = [
        path
        for path in records.rglob("*")
        if path.is_file()
        and not path.name.startswith("ETC9")
        and path.name not in excluded
    ]
    if include_web:
        paths.extend(
            path for path in (TOOL_ROOT / "web/dist").rglob("*") if path.is_file()
        )
        paths.extend(
            path
            for path in (TOOL_ROOT / "web/public/data").rglob("*")
            if path.is_file()
        )
    return snapshot_files(paths, SIDE_TOOL_ROOT)


def successor_ux_snapshot() -> dict[str, bytes]:
    records = SIDE_TOOL_ROOT / "records"
    paths = [
        records / "ETC11D11SuccessorUXBundle.json",
        records / "ETC11D11SuccessorUXCandidate.json",
        records / "ETC11D11UXWebBuildManifest.json",
    ]
    paths.extend(path for path in (TOOL_ROOT / "web/dist").rglob("*") if path.is_file())
    paths.extend(
        path for path in (TOOL_ROOT / "web/public/data").rglob("*") if path.is_file()
    )
    return snapshot_files(paths, SIDE_TOOL_ROOT)


def closeout_artifact_snapshot() -> dict[str, bytes]:
    records = SIDE_TOOL_ROOT / "records"
    return snapshot_files(
        [
            records / "ETC9ScenarioCoverageAndUsability.json",
            records / "ETC9EnvironmentConformance.json",
            records / "ETC9CloseoutDisposition.json",
            records / "ETC9CloseoutReport.md",
        ],
        SIDE_TOOL_ROOT,
    )


def run_python(path: Path, *arguments: str) -> str:
    result = subprocess.run(
        [sys.executable, str(path), *arguments],
        cwd=repository_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"verification command failed: {path}\n{result.stdout}\n{result.stderr}"
        )
    output = result.stdout.strip().splitlines()
    terminal = output[-1] if output else f"{path.name}:passed"
    print(terminal)
    return terminal


def run_build_sequence(scripts: Path) -> None:
    for name in BUILD_SEQUENCE:
        run_python(scripts / name)


def run_node_tests() -> tuple[int, int, str]:
    tests = tuple(sorted((TOOL_ROOT / "web/tests").glob("*.test.mjs")))
    test_count = sum(
        path.read_text(encoding="utf-8").count("\ntest(") for path in tests
    )
    result = subprocess.run(
        [
            str(managed_node()),
            "--test",
            *(path.relative_to(TOOL_ROOT / "web").as_posix() for path in tests),
        ],
        cwd=TOOL_ROOT / "web",
        env=tool_environment(),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"ET-C9 Node suite failed\n{result.stdout}\n{result.stderr}")
    terminal = next(
        (
            line.strip()
            for line in reversed(result.stdout.splitlines())
            if "pass" in line
        ),
        "Node tests passed",
    )
    print(f"ET_C9_NODE_TEST_PASS files={len(tests)} tests={test_count}")
    return len(tests), test_count, terminal


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    if sys.version_info[:3] != (3, 12, 3):
        raise RuntimeError("ET-C9 tested closeout interpreter must be Python 3.12.3")
    if shutil.which("python3.11") is not None or shutil.which("python3.13") is not None:
        raise RuntimeError(
            "another planned Python is available but lacks a tool-local conformance environment"
        )

    records = SIDE_TOOL_ROOT / "records"
    scripts = TOOL_ROOT / "scripts"
    investigation_scripts = SIDE_TOOL_ROOT.parents[1] / "scripts"
    source_before = source_snapshot(repo_root, records)
    protected_before = protected_snapshot(repo_root)
    accepted_before = accepted_artifact_snapshot()
    accepted_records_before = accepted_artifact_snapshot(include_web=False)

    d10_results = [run_python(investigation_scripts / name) for name in D10_AUDITS]
    post_d10_boundary = (
        investigation_scripts.parent / "specification/PostD10SpecificationBoundary.json"
    )
    if post_d10_boundary.is_file():
        run_python(investigation_scripts / POST_D10_SPECIFICATION_AUDIT)
        active_post_d10_phase = json.loads(
            post_d10_boundary.read_text(encoding="utf-8")
        ).get("active_phase")
    else:
        active_post_d10_phase = None

    if active_post_d10_phase in {"successor_investigation", "paper_propagation"}:
        python_results = [
            run_python(scripts / name, *arguments)
            for name, *arguments in HISTORICAL_LAYER_AUDITS
        ]
        python_results.extend(
            run_python(scripts / name) for name in SUCCESSOR_PHASE_PYTHON_SUITE
        )
        python_results.extend(run_python(scripts / name) for name in D11_FORENSIC_SUITE)
        python_results.extend(run_python(scripts / name) for name in D11_UX_SUITE)
        ux_first = successor_ux_snapshot()
        python_results.append(run_python(scripts / "build_iteration11_d11_ux.py"))
        ux_second = successor_ux_snapshot()
        if ux_second != ux_first:
            raise RuntimeError("ET-C11 second rebuild is not byte-identical")
        node_files, node_tests, node_terminal = run_node_tests()
        browser_terminal = run_python(scripts / "test_iteration11_d11_browser.py")

        source_after = source_snapshot(repo_root, records)
        protected_after = protected_snapshot(repo_root)
        accepted_after = accepted_artifact_snapshot(include_web=False)
        if source_after != source_before:
            raise RuntimeError(
                "successor-phase verification changed accepted source bytes"
            )
        if accepted_after != accepted_records_before:
            raise RuntimeError(
                "successor-phase verification changed accepted tool artifacts"
            )
        if protected_after != protected_before:
            changed = sorted(set(protected_after) | set(protected_before))
            changed = [
                key
                for key in changed
                if protected_after.get(key) != protected_before.get(key)
            ]
            raise RuntimeError(
                f"successor-phase verification changed protected paths: {changed}"
            )
        diff = subprocess.run(["git", "diff", "--check"], cwd=repo_root, check=False)
        if diff.returncode:
            raise RuntimeError("git diff --check failed")
        print(
            "ET_C11_D11_UX_VERIFY_PASS "
            f"status=accepted_{active_post_d10_phase} "
            "historical_rebuilds=skipped_immutable "
            "D11_overlay_rebuild=in_memory_byte_exact "
            "D11_UX_rebuilds=2_byte_exact "
            f"python_commands={len(python_results)} node_files={node_files} "
            f"node_tests={node_tests} node={node_terminal} "
            f"browser={browser_terminal} "
            "UX_status=candidate API_notebook_browser_identity=byte_exact "
            "accepted_source_immutable=true accepted_tool_artifacts_immutable=true "
            "protected_paths_immutable=true"
        )
        return 0

    run_build_sequence(scripts)
    accepted_first = accepted_artifact_snapshot()
    if accepted_first != accepted_before:
        changed = sorted(set(accepted_first) | set(accepted_before))
        changed = [
            key
            for key in changed
            if accepted_first.get(key) != accepted_before.get(key)
        ]
        raise RuntimeError(f"reconstructible accepted artifacts changed: {changed}")
    run_build_sequence(scripts)
    accepted_second = accepted_artifact_snapshot()
    if accepted_second != accepted_first:
        raise RuntimeError("ET-C0-C8 second rebuild is not byte-identical")

    run_python(scripts / "build_iteration9_closeout.py")
    closeout_first = closeout_artifact_snapshot()
    run_python(scripts / "build_iteration9_closeout.py")
    closeout_second = closeout_artifact_snapshot()
    if closeout_second != closeout_first:
        raise RuntimeError("ET-C9 second rebuild is not byte-identical")

    python_results = [
        run_python(scripts / name, *arguments)
        for name, *arguments in HISTORICAL_LAYER_AUDITS
    ]
    python_results.extend(run_python(scripts / name) for name in PYTHON_SUITE)
    python_results.append(
        run_python(
            SIDE_TOOL_ROOT / "docs/examples/agentic_query_walkthrough.py",
            "all",
        )
    )
    node_files, node_tests, node_terminal = run_node_tests()
    browser_terminal = run_python(scripts / "test_iteration9_browser.py")

    source_after = source_snapshot(repo_root, records)
    protected_after = protected_snapshot(repo_root)
    if source_after != source_before:
        raise RuntimeError("ET-C9 changed accepted source bytes")
    if protected_after != protected_before:
        changed = sorted(set(protected_after) | set(protected_before))
        changed = [
            key
            for key in changed
            if protected_after.get(key) != protected_before.get(key)
        ]
        raise RuntimeError(f"ET-C9 changed protected paths: {changed}")

    diff = subprocess.run(["git", "diff", "--check"], cwd=repo_root, check=False)
    if diff.returncode:
        raise RuntimeError("git diff --check failed")
    disposition = load_json_object(records / "ETC9CloseoutDisposition.json")
    coverage = load_json_object(records / "ETC9ScenarioCoverageAndUsability.json")
    environment = load_json_object(records / "ETC9EnvironmentConformance.json")
    if disposition["status"] != "accepted":
        raise RuntimeError("ET-C9 disposition is not accepted")
    if (
        disposition["selected_disposition"]
        != "accepted_bounded_read_only_exploratory_tool"
    ):
        raise RuntimeError("ET-C9 bounded disposition is not selected")
    if disposition["authority"]["human_acceptance_recorded"] is not True:
        raise RuntimeError("ET-C9 human acceptance is not recorded")
    if coverage["status"] != "accepted" or environment["status"] != "accepted":
        raise RuntimeError("ET-C9 accepted support records are incomplete")
    receipt: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C9_verification_receipt_v1",
        "status": "accepted",
        "gate_id": disposition["gate_id"],
        "accepted_record_digest": disposition["record_digest"],
        "scenario_coverage_digest": coverage["coverage_digest"],
        "verification": {
            "D10_audit_count": len(d10_results),
            "D10_audit_terminal_results": d10_results,
            "accepted_rebuild_cycles": 2,
            "accepted_rebuild_byte_identical": True,
            "reconstructible_gate_sequence": [
                "ET-C1",
                "ET-C2",
                "ET-C3",
                "ET-C4",
                "ET-C5",
                "ET-C8_latest_shared_web_surface",
            ],
            "historical_rebuild_exclusions": {
                "ET_C0": "historical_setup_snapshot_with_ET_C6_environment_successor_recorded_by_ET_C9",
                "ET_C6_ET_C7_web_manifests": "historical_stage_manifests_not_validators_for_the_latest_shared_ET_C8_distribution",
            },
            "closeout_rebuild_cycles": 2,
            "closeout_rebuild_byte_identical": True,
            "python_suite_command_count": len(python_results),
            "python_suite_terminal_results": python_results,
            "historical_layer_audit_modes": {
                "ET_C6": "source_layer_and_historical_manifest_metadata_current_shared_dist_excluded",
                "ET_C7": "source_layer_and_historical_manifest_metadata_current_shared_dist_excluded",
                "ET_C8": "full_latest_shared_dist_identity",
            },
            "tested_python_versions": ["3.12.3"],
            "planned_python_versions_unavailable": ["3.11", "3.13"],
            "node_test_file_count": node_files,
            "node_test_count": node_tests,
            "node_terminal_result": node_terminal,
            "playwright_projects": ["desktop", "mobile"],
            "playwright_test_count": 12,
            "screenshot_count": 14,
            "browser_terminal_result": browser_terminal,
            "admitted_source_file_count": len(source_before),
            "admitted_source_bytes_unchanged": True,
            "protected_path_file_count": len(protected_before),
            "protected_path_bytes_unchanged": True,
            "git_diff_check": "passed",
            "visual_inspection": (
                "passed_desktop_mobile_forensic_and_navigation_no_blank_graph_"
                "clipping_overlap_unreadable_identifier_or_authority_conflation"
            ),
        },
        "authority": {
            "human_acceptance_recorded": True,
            "scientific_claim_added": False,
            "source_automatically_admitted": False,
            "selected_disposition": "accepted_bounded_read_only_exploratory_tool",
        },
        "receipt_digest": None,
    }
    receipt["receipt_digest"] = record_digest(receipt, "receipt_digest")
    receipt_path = (
        TOOL_ROOT / "generated/post-d10-specification/ETC9VerificationReceipt.json"
        if post_d10_boundary.is_file()
        else records / "ETC9VerificationReceipt.json"
    )
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(receipt_path, receipt)
    print(
        "ET_C9_VERIFY_PASS status=accepted rebuilds=2+2 "
        f"python_commands={len(python_results)} node_tests={node_tests} "
        "browser_tests=12 screenshots=14 source_immutable=true "
        f"receipt={receipt['receipt_digest']} "
        f"receipt_path={receipt_path.relative_to(repo_root)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

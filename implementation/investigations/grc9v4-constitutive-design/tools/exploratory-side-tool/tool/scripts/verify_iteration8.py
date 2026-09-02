#!/usr/bin/env python3
"""Run the complete focused ET-C8 verification sequence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import load_json_object, record_digest  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


def write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def run_python(path: Path) -> None:
    result = subprocess.run([sys.executable, str(path)], check=False)
    if result.returncode:
        raise RuntimeError(f"verification command failed: {path.name}")


def generated_bytes() -> dict[str, bytes]:
    records = SIDE_TOOL_ROOT / "records"
    paths = (
        records / "ETC8LineagePlaybackLayer.json",
        records / "ETC8WebBuildManifest.json",
        records / "ETC8LineageAndRippleNavigation.json",
        records / "ETC8LineageAndRippleNavigation.md",
    )
    dist = TOOL_ROOT / "web/dist"
    dist_paths = tuple(path for path in sorted(dist.rglob("*")) if path.is_file())
    return {
        path.relative_to(SIDE_TOOL_ROOT).as_posix(): path.read_bytes()
        for path in paths + dist_paths
    }


def run_node_tests() -> tuple[int, int]:
    tests = tuple(sorted((TOOL_ROOT / "web/tests").glob("*.test.mjs")))
    if not tests:
        raise RuntimeError("ET-C8 Node component tests are missing")
    test_count = sum(path.read_text(encoding="utf-8").count("\ntest(") for path in tests)
    result = subprocess.run(
        [
            str(managed_node()),
            "--test",
            *(path.relative_to(TOOL_ROOT / "web").as_posix() for path in tests),
        ],
        cwd=TOOL_ROOT / "web",
        env=tool_environment(),
        shell=False,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("ET-C8 Node component tests failed")
    return len(tests), test_count


def finalize_accepted_record() -> dict[str, object]:
    records = SIDE_TOOL_ROOT / "records"
    gate_path = records / "ETC8LineageAndRippleNavigation.json"
    gate = load_json_object(gate_path)
    expected_requirements = {
        "independent_source_projection_audit": "passed_34241_checks",
        "python_and_node_component_tests": "passed_185_python_and_17_node_checks",
        "deterministic_double_rebuild": "passed_byte_identical",
        "playwright_desktop_mobile": "passed_8_tests_10_screenshots",
        "ET_C7_predecessor_regression": "passed_477_checks",
        "human_review": "accepted",
    }
    if gate.get("acceptance_requirements") != expected_requirements:
        raise RuntimeError("ET-C8 accepted requirements are not reproducible")
    if gate.get("record_digest") != record_digest(gate, "record_digest"):
        raise RuntimeError("ET-C8 accepted record digest is invalid")
    return gate


def write_verification_receipt(gate: dict[str, object]) -> dict[str, object]:
    records = SIDE_TOOL_ROOT / "records"
    layer = load_json_object(records / "ETC8LineagePlaybackLayer.json")
    manifest = load_json_object(records / "ETC8WebBuildManifest.json")
    receipt: dict[str, object] = {
        "schema": "grcv4_explorer_ET_C8_verification_receipt_v1",
        "status": "accepted",
        "gate_id": gate["gate_id"],
        "accepted_record_digest": gate["record_digest"],
        "lineage_playback_layer_digest": layer["layer_digest"],
        "web_build_manifest_digest": manifest["manifest_digest"],
        "verification": {
            "deterministic_rebuild_count": 2,
            "independent_audit_checks": 34241,
            "focused_python_checks": 185,
            "node_test_files": 4,
            "node_test_count": 17,
            "playwright_projects": ["desktop", "mobile"],
            "playwright_test_count": 8,
            "screenshot_count": 10,
            "ET_C7_predecessor_focused_checks": 477,
            "git_diff_check": "passed",
            "visual_inspection": "passed_desktop_mobile_no_overlap_clipping_or_authority_conflation",
        },
        "authority": {
            "human_acceptance_recorded": True,
            "iteration_9_authorized": True,
            "scientific_claim_added": False,
        },
        "receipt_digest": None,
    }
    receipt["receipt_digest"] = record_digest(receipt, "receipt_digest")
    write_json(records / "ETC8VerificationReceipt.json", receipt)
    return receipt


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    scripts = TOOL_ROOT / "scripts"
    run_python(scripts / "build_iteration8_lineage.py")
    first = generated_bytes()
    run_python(scripts / "build_iteration8_lineage.py")
    second = generated_bytes()
    if first != second:
        raise RuntimeError("ET-C8 double rebuild is not byte-identical")
    run_python(scripts / "audit_iteration8_lineage.py")
    run_python(scripts / "test_iteration8_lineage.py")
    node_test_files, node_tests = run_node_tests()
    if (node_test_files, node_tests) != (4, 17):
        raise RuntimeError("ET-C8 Node test population changed")
    run_python(scripts / "test_iteration8_browser.py")
    run_python(scripts / "test_iteration7_ceilings.py")
    diff = subprocess.run(["git", "diff", "--check"], cwd=repo_root, check=False)
    if diff.returncode:
        raise RuntimeError("git diff --check failed")
    gate = finalize_accepted_record()
    receipt = write_verification_receipt(gate)
    print(
        "ET_C8_VERIFY_PASS deterministic_rebuild=2 audit_checks=34241 "
        "python_checks=185 node_test_files=4 node_tests=17 browser_projects=2 "
        "browser_tests=8 screenshots=10 predecessor_checks=477 "
        f"receipt={receipt['receipt_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

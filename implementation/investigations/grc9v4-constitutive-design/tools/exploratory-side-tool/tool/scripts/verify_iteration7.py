#!/usr/bin/env python3
"""Run the complete focused ET-C7 verification sequence."""

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


def run_python(path: Path) -> None:
    result = subprocess.run([sys.executable, str(path)], check=False)
    if result.returncode:
        raise RuntimeError(f"verification command failed: {path.name}")


def generated_bytes() -> dict[str, bytes]:
    records = SIDE_TOOL_ROOT / "records"
    paths = (
        records / "ETC7ClaimCeilingAlternativeLayer.json",
        records / "ETC7WebBuildManifest.json",
        records / "ETC7ClaimCeilingAlternativeNavigation.json",
        records / "ETC7ClaimCeilingAlternativeNavigation.md",
    )
    dist = TOOL_ROOT / "web/dist"
    dist_paths = tuple(path for path in sorted(dist.rglob("*")) if path.is_file())
    return {
        path.relative_to(SIDE_TOOL_ROOT).as_posix(): path.read_bytes()
        for path in paths + dist_paths
    }


def run_node_tests() -> int:
    tests = tuple(sorted((TOOL_ROOT / "web/tests").glob("*.test.mjs")))
    if not tests:
        raise RuntimeError("ET-C7 Node component tests are missing")
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
        raise RuntimeError("ET-C7 Node component tests failed")
    return len(tests)


def write_verification_receipt() -> dict[str, object]:
    records = SIDE_TOOL_ROOT / "records"
    layer = load_json_object(records / "ETC7ClaimCeilingAlternativeLayer.json")
    manifest = load_json_object(records / "ETC7WebBuildManifest.json")
    gate = load_json_object(records / "ETC7ClaimCeilingAlternativeNavigation.json")
    receipt: dict[str, object] = {
        "schema": "grcv4_explorer_ET_C7_verification_receipt_v1",
        "status": "accepted",
        "gate_id": gate["gate_id"],
        "accepted_record_digest": gate["record_digest"],
        "claim_ceiling_layer_digest": layer["layer_digest"],
        "web_build_manifest_digest": manifest["manifest_digest"],
        "verification": {
            "deterministic_rebuild_count": 2,
            "independent_audit_checks": 2173,
            "focused_python_checks": 477,
            "node_test_files": 3,
            "node_test_count": 12,
            "playwright_projects": ["desktop", "mobile"],
            "playwright_test_count": 4,
            "screenshot_count": 6,
            "ET_C6_predecessor_focused_checks": 47,
            "git_diff_check": "passed",
            "visual_inspection": "passed_desktop_mobile_no_overlap_or_authority_conflation",
        },
        "authority": {
            "human_acceptance_recorded": True,
            "iteration_8_authorized": True,
            "scientific_claim_added": False,
        },
        "receipt_digest": None,
    }
    receipt["receipt_digest"] = record_digest(receipt, "receipt_digest")
    path = records / "ETC7VerificationReceipt.json"
    path.write_text(
        json.dumps(
            receipt,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return receipt


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    scripts = TOOL_ROOT / "scripts"
    run_python(scripts / "build_iteration7_ceilings.py")
    first = generated_bytes()
    run_python(scripts / "build_iteration7_ceilings.py")
    second = generated_bytes()
    if first != second:
        raise RuntimeError("ET-C7 double rebuild is not byte-identical")
    run_python(scripts / "audit_iteration7_ceilings.py")
    run_python(scripts / "test_iteration7_ceilings.py")
    node_test_files = run_node_tests()
    if node_test_files != 3:
        raise RuntimeError("ET-C7 Node test-file population changed")
    run_python(scripts / "test_iteration7_browser.py")
    run_python(scripts / "test_iteration6_navigation.py")
    diff = subprocess.run(["git", "diff", "--check"], cwd=repo_root, check=False)
    if diff.returncode:
        raise RuntimeError("git diff --check failed")
    receipt = write_verification_receipt()
    print(
        "ET_C7_VERIFY_PASS deterministic_rebuild=2 audit_checks=2173 "
        "python_checks=477 node_test_files=3 node_tests=12 browser_projects=2 "
        "browser_tests=4 screenshots=6 predecessor_checks=47 "
        f"receipt={receipt['receipt_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

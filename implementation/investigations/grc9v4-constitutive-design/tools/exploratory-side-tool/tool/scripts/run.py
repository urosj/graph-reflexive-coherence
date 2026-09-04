#!/usr/bin/env python3
"""Run admitted side-tool maintenance commands from any working directory."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
SIDE_TOOL_ROOT = Path(__file__).resolve().parents[2]
INVESTIGATION_ROOT = SIDE_TOOL_ROOT.parents[1]


def repository_root() -> Path:
    for candidate in SIDE_TOOL_ROOT.parents:
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "implementation/investigations/grc9v4-constitutive-design"
        ).is_dir():
            return candidate
    raise RuntimeError("cannot discover repository root")


COMMANDS = {
    "doctor": TOOL_ROOT / "scripts/doctor.py",
    "build-iteration0": TOOL_ROOT / "scripts/build_iteration0_contract.py",
    "audit-iteration0": TOOL_ROOT / "scripts/audit_iteration0_contract.py",
    "discover-sources": TOOL_ROOT / "scripts/discover_sources.py",
    "build-iteration1": TOOL_ROOT / "scripts/build_iteration1_bundle.py",
    "audit-iteration1": TOOL_ROOT / "scripts/audit_iteration1_bundle.py",
    "test-iteration1": TOOL_ROOT / "scripts/test_iteration1_adapters.py",
    "build-iteration2": TOOL_ROOT / "scripts/build_iteration2_graph.py",
    "audit-iteration2": TOOL_ROOT / "scripts/audit_iteration2_graph.py",
    "test-iteration2": TOOL_ROOT / "scripts/test_iteration2_kernel.py",
    "build-iteration3": TOOL_ROOT / "scripts/build_iteration3_forensics.py",
    "audit-iteration3": TOOL_ROOT / "scripts/audit_iteration3_forensics.py",
    "test-iteration3": TOOL_ROOT / "scripts/test_iteration3_forensics.py",
    "notebook-iteration3": TOOL_ROOT / "scripts/run_iteration3_notebook.py",
    "verify-iteration3": TOOL_ROOT / "scripts/verify_iteration3.py",
    "build-iteration4": TOOL_ROOT / "scripts/build_iteration4_counterfactuals.py",
    "audit-iteration4": TOOL_ROOT / "scripts/audit_iteration4_counterfactuals.py",
    "test-iteration4": TOOL_ROOT / "scripts/test_iteration4_counterfactuals.py",
    "verify-iteration4": TOOL_ROOT / "scripts/verify_iteration4.py",
    "build-iteration5": TOOL_ROOT / "scripts/build_iteration5_ripples.py",
    "audit-iteration5": TOOL_ROOT / "scripts/audit_iteration5_ripples.py",
    "test-iteration5": TOOL_ROOT / "scripts/test_iteration5_ripples.py",
    "verify-iteration5": TOOL_ROOT / "scripts/verify_iteration5.py",
    "build-iteration6": TOOL_ROOT / "scripts/build_iteration6_navigation.py",
    "audit-iteration6": TOOL_ROOT / "scripts/audit_iteration6_navigation.py",
    "test-iteration6": TOOL_ROOT / "scripts/test_iteration6_navigation.py",
    "install-browser-iteration6": TOOL_ROOT / "scripts/install_iteration6_browser.py",
    "browser-iteration6": TOOL_ROOT / "scripts/test_iteration6_browser.py",
    "verify-iteration6": TOOL_ROOT / "scripts/verify_iteration6.py",
    "serve-iteration6": TOOL_ROOT / "scripts/serve_iteration6.py",
    "build-iteration7": TOOL_ROOT / "scripts/build_iteration7_ceilings.py",
    "audit-iteration7": TOOL_ROOT / "scripts/audit_iteration7_ceilings.py",
    "test-iteration7": TOOL_ROOT / "scripts/test_iteration7_ceilings.py",
    "browser-iteration7": TOOL_ROOT / "scripts/test_iteration7_browser.py",
    "verify-iteration7": TOOL_ROOT / "scripts/verify_iteration7.py",
    "serve-iteration7": TOOL_ROOT / "scripts/serve_iteration7.py",
    "build-iteration8": TOOL_ROOT / "scripts/build_iteration8_lineage.py",
    "audit-iteration8": TOOL_ROOT / "scripts/audit_iteration8_lineage.py",
    "test-iteration8": TOOL_ROOT / "scripts/test_iteration8_lineage.py",
    "browser-iteration8": TOOL_ROOT / "scripts/test_iteration8_browser.py",
    "verify-iteration8": TOOL_ROOT / "scripts/verify_iteration8.py",
    "serve-iteration8": TOOL_ROOT / "scripts/serve_iteration8.py",
    "build-iteration9": TOOL_ROOT / "scripts/build_iteration9_closeout.py",
    "audit-iteration9": TOOL_ROOT / "scripts/audit_iteration9_closeout.py",
    "test-iteration9": TOOL_ROOT / "scripts/test_iteration9_closeout.py",
    "browser-iteration9": TOOL_ROOT / "scripts/test_iteration9_browser.py",
    "verify-iteration9": TOOL_ROOT / "scripts/verify_iteration9.py",
    "build-iteration10-d11": TOOL_ROOT / "scripts/build_iteration10_d11.py",
    "audit-iteration10-d11": TOOL_ROOT / "scripts/audit_iteration10_d11.py",
    "test-iteration10-d11": TOOL_ROOT / "scripts/test_iteration10_d11.py",
    "build-iteration11-d11-ux": TOOL_ROOT / "scripts/build_iteration11_d11_ux.py",
    "audit-iteration11-d11-ux": TOOL_ROOT / "scripts/audit_iteration11_d11_ux.py",
    "test-iteration11-d11-ux": TOOL_ROOT / "scripts/test_iteration11_d11_ux.py",
    "notebook-iteration11-d11": (TOOL_ROOT / "scripts/run_iteration11_d11_notebook.py"),
    "browser-iteration11-d11": (TOOL_ROOT / "scripts/test_iteration11_d11_browser.py"),
    "serve-iteration11-d11": TOOL_ROOT / "scripts/serve_iteration11_d11.py",
    "verify-post-d10-specifications": (
        INVESTIGATION_ROOT / "scripts/audit_grcv4_post_d10_specifications.py"
    ),
    "audit-d11-successor-opening": (
        INVESTIGATION_ROOT / "scripts/audit_grc9v4_d11_successor_opening.py"
    ),
    "audit-d11-c-resolution": (
        INVESTIGATION_ROOT / "scripts/audit_grc9v4_d11_c_resolution.py"
    ),
    "audit-d11-g9-resolution": (
        INVESTIGATION_ROOT / "scripts/audit_grc9v4_d11_g9_resolution.py"
    ),
    "audit-d11-paper-propagation": (
        INVESTIGATION_ROOT / "scripts/audit_grcv4_d11_paper_propagation.py"
    ),
}


def main() -> int:
    if Path(sys.prefix).resolve() != (repository_root() / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=sorted(COMMANDS))
    args = parser.parse_args()
    return subprocess.run(
        [sys.executable, str(COMMANDS[args.command])], check=False
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())

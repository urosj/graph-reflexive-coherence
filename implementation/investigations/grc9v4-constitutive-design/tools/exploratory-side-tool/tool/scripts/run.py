#!/usr/bin/env python3
"""Run admitted side-tool maintenance commands from any working directory."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
SIDE_TOOL_ROOT = Path(__file__).resolve().parents[2]


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

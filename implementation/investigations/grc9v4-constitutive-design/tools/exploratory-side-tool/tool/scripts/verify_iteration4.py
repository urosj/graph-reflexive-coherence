#!/usr/bin/env python3
"""Run the complete focused ET-C4 verification sequence."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]


def repository_root() -> Path:
    for candidate in SIDE_TOOL_ROOT.parents:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise RuntimeError("cannot discover repository root")


def run(path: Path) -> None:
    result = subprocess.run([sys.executable, str(path)], check=False)
    if result.returncode:
        raise RuntimeError(f"verification command failed: {path.name}")


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    scripts = TOOL_ROOT / "scripts"
    records = SIDE_TOOL_ROOT / "records"
    generated = (
        records / "ETC4CounterfactualScenarioReport.json",
        records / "ETC4CounterfactualScenarioReport.md",
        records / "ETC4BoundedCounterfactualKernel.json",
        records / "ETC4BoundedCounterfactualKernel.md",
    )
    run(scripts / "build_iteration4_counterfactuals.py")
    first = {path.name: path.read_bytes() for path in generated}
    run(scripts / "build_iteration4_counterfactuals.py")
    second = {path.name: path.read_bytes() for path in generated}
    if first != second:
        raise RuntimeError("ET-C4 double rebuild is not byte-identical")
    run(scripts / "audit_iteration4_counterfactuals.py")
    run(scripts / "test_iteration4_counterfactuals.py")
    run(scripts / "verify_iteration3.py")
    diff = subprocess.run(
        ["git", "diff", "--check"], cwd=repo_root, check=False
    )
    if diff.returncode:
        raise RuntimeError("git diff --check failed")
    print(
        "ET_C4_VERIFY_PASS deterministic_rebuild=2 "
        "scenario_count=13 predecessor_regression=ET_C3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

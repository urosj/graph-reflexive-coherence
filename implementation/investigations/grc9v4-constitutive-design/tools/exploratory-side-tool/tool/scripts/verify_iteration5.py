#!/usr/bin/env python3
"""Run the complete focused ET-C5 verification sequence."""

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


def generated_paths() -> tuple[Path, ...]:
    records = SIDE_TOOL_ROOT / "records"
    fixed = (
        records / "ETC5ScenarioBundle.json",
        records / "ETC5AllProfilesAggregate.json",
        records / "ETC5RippleShardIndex.json",
        records / "ETC5RippleAndScenarioContract.json",
        records / "ETC5RippleAndScenarioContract.md",
    )
    shards = tuple(sorted((records / "iteration5-ripple").glob("ETC5RippleShard-*.json")))
    return fixed + shards


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    scripts = TOOL_ROOT / "scripts"
    run(scripts / "build_iteration5_ripples.py")
    first_paths = generated_paths()
    first = {path.relative_to(SIDE_TOOL_ROOT).as_posix(): path.read_bytes() for path in first_paths}
    run(scripts / "build_iteration5_ripples.py")
    second_paths = generated_paths()
    second = {path.relative_to(SIDE_TOOL_ROOT).as_posix(): path.read_bytes() for path in second_paths}
    if first != second:
        raise RuntimeError("ET-C5 double rebuild is not byte-identical")
    if len(first) != 8:
        raise RuntimeError("ET-C5 generated file population changed")
    run(scripts / "audit_iteration5_ripples.py")
    run(scripts / "test_iteration5_ripples.py")
    run(scripts / "verify_iteration4.py")
    diff = subprocess.run(["git", "diff", "--check"], cwd=repo_root, check=False)
    if diff.returncode:
        raise RuntimeError("git diff --check failed")
    print(
        "ET_C5_VERIFY_PASS deterministic_rebuild=2 scenarios=25 rows=24 "
        "shards=3 predecessor_regression=ET_C4"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

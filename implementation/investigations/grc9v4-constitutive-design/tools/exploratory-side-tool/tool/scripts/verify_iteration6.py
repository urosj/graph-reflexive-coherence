#!/usr/bin/env python3
"""Run the complete focused ET-C6 verification sequence."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


def run_python(path: Path) -> None:
    result = subprocess.run([sys.executable, str(path)], check=False)
    if result.returncode:
        raise RuntimeError(f"verification command failed: {path.name}")


def generated_bytes() -> dict[str, bytes]:
    records = SIDE_TOOL_ROOT / "records"
    paths = (
        records / "ETC6StaticNavigationBundle.json",
        records / "ETC6CrossSurfaceParity.json",
        records / "ETC6WebBuildManifest.json",
        records / "ETC6StaticNavigationSurface.json",
        records / "ETC6StaticNavigationSurface.md",
    )
    dist = TOOL_ROOT / "web/dist"
    dist_paths = tuple(path for path in sorted(dist.rglob("*")) if path.is_file())
    all_paths = paths + dist_paths
    return {
        path.relative_to(SIDE_TOOL_ROOT).as_posix(): path.read_bytes()
        for path in all_paths
    }


def run_node_tests() -> None:
    tests = tuple(sorted((TOOL_ROOT / "web/tests").glob("*.test.mjs")))
    if not tests:
        raise RuntimeError("ET-C6 Node component tests are missing")
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
        raise RuntimeError("ET-C6 Node component tests failed")


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    scripts = TOOL_ROOT / "scripts"
    run_python(scripts / "build_iteration6_navigation.py")
    first = generated_bytes()
    run_python(scripts / "build_iteration6_navigation.py")
    second = generated_bytes()
    if first != second:
        raise RuntimeError("ET-C6 double rebuild is not byte-identical")
    run_python(scripts / "audit_iteration6_navigation.py")
    run_python(scripts / "test_iteration6_navigation.py")
    run_node_tests()
    run_python(scripts / "test_iteration6_browser.py")
    run_python(scripts / "verify_iteration5.py")
    diff = subprocess.run(["git", "diff", "--check"], cwd=repo_root, check=False)
    if diff.returncode:
        raise RuntimeError("git diff --check failed")
    print(
        "ET_C6_VERIFY_PASS deterministic_rebuild=2 audit_checks=44895 "
        "python_checks=47 node_tests=8 browser_projects=2 "
        "predecessor_regression=ET_C5"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

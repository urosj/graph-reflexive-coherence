#!/usr/bin/env python3
"""Exercise ET-C0 bootstrap from a clean, differently located repository copy."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]


def repository_root() -> Path:
    for candidate in SIDE_TOOL_ROOT.parents:
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "implementation/investigations/grc9v4-constitutive-design"
        ).is_dir():
            return candidate
    raise RuntimeError("cannot discover repository root")


REPO_ROOT = repository_root()
INVESTIGATION_RELATIVE = Path(
    "implementation/investigations/grc9v4-constitutive-design"
)


def require_repository_venv() -> None:
    if Path(sys.prefix).resolve() != (REPO_ROOT / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


def ignored(_directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in {".tooling", ".cache", "generated", "node_modules", "__pycache__"}
        or name.endswith(".pyc")
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    require_repository_venv()
    offline_cache = TOOL_ROOT / ".cache/downloads"
    if not offline_cache.is_dir():
        raise RuntimeError("run the primary bootstrap before the portability test")
    with tempfile.TemporaryDirectory(prefix="grcv4-explorer-portability-") as temp:
        target = Path(temp) / "relocated-graph-reflexive-coherence"
        target.mkdir()
        for name in ("pyproject.toml", "uv.lock", ".gitignore"):
            shutil.copy2(REPO_ROOT / name, target / name)
        destination = target / INVESTIGATION_RELATIVE
        destination.parent.mkdir(parents=True)
        shutil.copytree(
            REPO_ROOT / INVESTIGATION_RELATIVE,
            destination,
            ignore=ignored,
        )
        bootstrap = (
            destination / "tools/exploratory-side-tool/tool/scripts/bootstrap.py"
        )
        base_python = Path(getattr(sys, "_base_executable", sys.executable))
        command = [
            str(base_python),
            str(bootstrap),
            "--offline-cache",
            str(offline_cache),
        ]
        incomplete_venv = target / ".venv"
        incomplete_venv.mkdir()
        partial = subprocess.run(
            command,
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
        if partial.returncode == 0 or "environment is incomplete" not in (
            partial.stdout + partial.stderr
        ):
            raise RuntimeError("partial repository environment did not fail closed")
        shutil.rmtree(incomplete_venv)
        first = subprocess.run(
            command,
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
        if first.returncode != 0:
            raise RuntimeError(first.stdout + first.stderr)
        node = (
            destination
            / "tools/exploratory-side-tool/tool/.tooling/node/v22.23.2"
            / ("node.exe" if os.name == "nt" else "bin/node")
        )
        first_node_sha = file_sha256(node)
        second = subprocess.run(
            command,
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
        if second.returncode != 0:
            raise RuntimeError(second.stdout + second.stderr)
        if file_sha256(node) != first_node_sha:
            raise RuntimeError("idempotent bootstrap replaced the admitted Node binary")
        if "bootstrap_status=passed" not in first.stdout:
            raise RuntimeError("first relocated bootstrap did not report success")
        if "bootstrap_status=passed" not in second.stdout:
            raise RuntimeError("second relocated bootstrap did not report success")
    print("ET_C0_RELOCATED_BOOTSTRAP_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

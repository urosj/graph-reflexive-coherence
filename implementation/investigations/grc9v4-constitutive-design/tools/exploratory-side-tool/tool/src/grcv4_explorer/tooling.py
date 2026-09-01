"""Managed tool-local Node and frontend execution helpers."""

from __future__ import annotations

import os
import subprocess
import tomllib
from pathlib import Path
from typing import Sequence

from .paths import TOOL_ROOT


def managed_node_root() -> Path:
    toolchain = tomllib.loads((TOOL_ROOT / "toolchain.toml").read_text(encoding="utf-8"))
    return TOOL_ROOT / ".tooling/node" / f"v{toolchain['node']['managed_version']}"


def managed_node() -> Path:
    path = managed_node_root() / ("node.exe" if os.name == "nt" else "bin/node")
    if not path.is_file():
        raise RuntimeError("managed Node is unavailable; run the side-tool bootstrap")
    return path


def tool_environment() -> dict[str, str]:
    root = managed_node_root()
    cache = TOOL_ROOT / ".cache"
    environment = os.environ.copy()
    values = {
        "NPM_CONFIG_CACHE": cache / "npm",
        "NPM_CONFIG_USERCONFIG": TOOL_ROOT / ".tooling/npmrc",
        "COREPACK_HOME": TOOL_ROOT / ".tooling/corepack",
        "PLAYWRIGHT_BROWSERS_PATH": TOOL_ROOT / ".tooling/playwright",
    }
    for key, path in values.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        environment[key] = str(path)
    node_bin = root if os.name == "nt" else root / "bin"
    environment["PATH"] = os.pathsep.join((str(node_bin), environment.get("PATH", "")))
    return environment


def run_managed_node(script: Path, arguments: Sequence[str] = ()) -> None:
    completed = subprocess.run(
        [str(managed_node()), str(script), *arguments],
        cwd=TOOL_ROOT / "web",
        env=tool_environment(),
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"managed Node command failed: {script.name}")

#!/usr/bin/env python3
"""Serve the ET-C11 D11 UX candidate."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    audit = subprocess.run(
        [sys.executable, str(TOOL_ROOT / "scripts/audit_iteration11_d11_ux.py")],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if args.refresh or audit.returncode:
        result = subprocess.run(
            [sys.executable, str(TOOL_ROOT / "scripts/build_iteration11_d11_ux.py")],
            cwd=repo_root,
            check=False,
        )
        if result.returncode:
            return result.returncode
        audit = subprocess.run(
            [sys.executable, str(TOOL_ROOT / "scripts/audit_iteration11_d11_ux.py")],
            cwd=repo_root,
            check=False,
        )
        if audit.returncode:
            return audit.returncode
    vite = TOOL_ROOT / "web/node_modules/vite/bin/vite.js"
    print(f"ET_C11_D11_SERVE url=http://127.0.0.1:{args.port}", flush=True)
    return subprocess.run(
        [
            str(managed_node()),
            str(vite),
            "preview",
            "--host",
            "127.0.0.1",
            "--port",
            str(args.port),
            "--strictPort",
        ],
        cwd=TOOL_ROOT / "web",
        env=tool_environment(),
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())

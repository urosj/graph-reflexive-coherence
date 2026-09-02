#!/usr/bin/env python3
"""Run ET-C8 browser pressure with the tool-local Playwright runtime."""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.tooling import managed_node, tool_environment  # noqa: E402


def wait_for_server(url: str) -> None:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.15)
    raise RuntimeError(f"static preview did not start: {url}")


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    environment = tool_environment()
    vite = TOOL_ROOT / "web/node_modules/vite/bin/vite.js"
    server = subprocess.Popen(
        [
            str(managed_node()),
            str(vite),
            "preview",
            "--host",
            "127.0.0.1",
            "--port",
            "4173",
            "--strictPort",
        ],
        cwd=TOOL_ROOT / "web",
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_server("http://127.0.0.1:4173")
        cli = TOOL_ROOT / "web/node_modules/@playwright/test/cli.js"
        result = subprocess.run(
            [str(managed_node()), str(cli), "test"],
            cwd=TOOL_ROOT / "web",
            env=environment,
            check=False,
        )
        if result.returncode:
            raise RuntimeError("ET-C8 Playwright tests failed")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)
    print("ET_C8_BROWSER_TEST_PASS projects=desktop,mobile tests=8 screenshots=10")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

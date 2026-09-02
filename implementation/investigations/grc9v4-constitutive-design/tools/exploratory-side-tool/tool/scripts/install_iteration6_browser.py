#!/usr/bin/env python3
"""Install the pinned Chromium build into the tool-local Playwright root."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.tooling import run_managed_node  # noqa: E402


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    cli = TOOL_ROOT / "web/node_modules/@playwright/test/cli.js"
    run_managed_node(cli, ("install", "chromium"))
    print("ET_C6_BROWSER_INSTALL_PASS browser=chromium location=tool/.tooling/playwright")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

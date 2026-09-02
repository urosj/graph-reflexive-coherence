#!/usr/bin/env python3
"""Emit the non-authoritative source-evolution observation receipt."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes  # noqa: E402
from grcv4_explorer.discovery import discover_sources  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_et_c0_contract,
)


def require_repository_venv(repo_root: Path) -> None:
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


def main() -> int:
    repo_root = repository_root()
    require_repository_venv(repo_root)
    contract = load_et_c0_contract(
        SIDE_TOOL_ROOT / "records/ETC0SourceAndLayoutContract.json"
    )
    observation = discover_sources(repo_root, admitted_rows(contract))
    generated = TOOL_ROOT / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    (generated / "source-observation.json").write_bytes(
        canonical_bytes(observation) + b"\n"
    )
    print(f"source_observation_state={observation['state']}")
    print(f"source_observation_digest={observation['observation_digest']}")
    return 0 if observation["state"] == "current_bundle_exact" else 2


if __name__ == "__main__":
    raise SystemExit(main())

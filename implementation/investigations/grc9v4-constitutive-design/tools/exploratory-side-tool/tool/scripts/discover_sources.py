#!/usr/bin/env python3
"""Emit the non-authoritative source-evolution observation receipt."""

from __future__ import annotations

import sys
import argparse
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, load_json_object, record_digest  # noqa: E402
from grcv4_explorer.discovery import discover_sources  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_et_c0_contract,
    load_d11_source_contract,
)
from grcv4_explorer.receipt_parents import ADMISSION, ACCEPTED_ADMISSION_DIGEST  # noqa: E402
from grcv4_explorer.abundance import ADMISSION as ABUNDANCE_ADMISSION, ACCEPTED_ADMISSION_DIGEST as ABUNDANCE_DIGEST  # noqa: E402
from grcv4_explorer.a_initializer import ADMISSION as INITIALIZER_ADMISSION, ACCEPTED_ADMISSION_DIGEST as INITIALIZER_DIGEST  # noqa: E402


def require_repository_venv(repo_root: Path) -> None:
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


def main() -> int:
    repo_root = repository_root()
    require_repository_venv(repo_root)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("current", "d11", "et-c0"), default="current")
    args = parser.parse_args()
    contract = load_et_c0_contract(
        SIDE_TOOL_ROOT / "records/ETC0SourceAndLayoutContract.json"
    )
    rows = list(admitted_rows(contract))
    if args.scope != "et-c0":
        rows += admitted_rows(load_d11_source_contract(SIDE_TOOL_ROOT / "records/ETC10D11SourceContract.json"))
    if args.scope == "current":
        admission = load_json_object(SIDE_TOOL_ROOT / "records" / ADMISSION)
        if admission.get("record_digest") != record_digest(admission, "record_digest") or admission["record_digest"] != ACCEPTED_ADMISSION_DIGEST:
            raise ValueError("current discovery admission is not pinned")
        rows.append(admission["source"])
        abundance = load_json_object(SIDE_TOOL_ROOT / "records" / ABUNDANCE_ADMISSION)
        if abundance.get("record_digest") != record_digest(abundance, "record_digest") or abundance["record_digest"] != ABUNDANCE_DIGEST:
            raise ValueError("abundance discovery admission is not pinned")
        rows.append(abundance["source"])
        initializer = load_json_object(SIDE_TOOL_ROOT / "records" / INITIALIZER_ADMISSION)
        if initializer.get("record_digest") != record_digest(initializer, "record_digest") or initializer["record_digest"] != INITIALIZER_DIGEST:
            raise ValueError("initializer discovery admission is not pinned")
        rows.append(initializer["source"])
    observation = discover_sources(repo_root, rows)
    generated = TOOL_ROOT / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    (generated / "source-observation.json").write_bytes(
        canonical_bytes(observation) + b"\n"
    )
    print(f"source_observation_state={observation['state']}")
    print(f"source_observation_scope={args.scope}")
    print(f"source_observation_digest={observation['observation_digest']}")
    return 0 if observation["state"] == "current_bundle_exact" else 2


if __name__ == "__main__":
    raise SystemExit(main())

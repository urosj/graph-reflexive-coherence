#!/usr/bin/env python3
"""Compare a frozen blind replay with a physically separate recovery oracle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--replay", required=True)
    parser.add_argument("--replay-freeze", required=True)
    parser.add_argument("--oracle", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    replay_path = root / args.replay
    freeze_path = root / args.replay_freeze
    oracle_path = root / args.oracle
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    replay_freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    oracle = json.loads(oracle_path.read_text(encoding="utf-8"))

    errors: list[str] = []
    if replay_freeze.get("replay_sha256") != sha256_file(replay_path):
        errors.append("blind replay changed after it was frozen")
    if replay_freeze.get("replay_execution_digest") != replay.get(
        "execution_digest"
    ):
        errors.append("blind replay digest differs from replay freeze")
    for key, expected in oracle["expected_recovery"].items():
        actual = replay.get("recovery", {}).get(key)
        if actual != expected:
            errors.append(
                f"recovery mismatch for {key}: expected {expected!r}, got {actual!r}"
            )

    result = {
        "artifact": "Phase 8 GRC/LGRC I111 blind-recovery oracle validation",
        "schema_version": "phase8_grclgrc_i111_blind_validation_v1",
        "iteration": 111,
        "status": "passed" if not errors else "failed",
        "loaded_input_paths": [args.replay, args.replay_freeze, args.oracle],
        "blind_input_loaded": False,
        "guide_registry_or_matrix_loaded": False,
        "replay_frozen_before_oracle_comparison": True,
        "compared_fields": sorted(oracle["expected_recovery"]),
        "error_count": len(errors),
        "errors": errors,
        "runtime_behavior_changed": False,
    }
    result["validation_digest"] = canonical_digest(result)
    (root / args.output).write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

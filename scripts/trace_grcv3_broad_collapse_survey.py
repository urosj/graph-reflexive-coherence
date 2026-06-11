"""Survey the broader recorded collapse-capable GRCV3 lanes."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from pygrc.telemetry import build_grcv3_landscape_broad_collapse_survey


def main(argv: list[str] | None = None) -> int:
    del argv
    survey = build_grcv3_landscape_broad_collapse_survey()
    print(json.dumps(survey, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

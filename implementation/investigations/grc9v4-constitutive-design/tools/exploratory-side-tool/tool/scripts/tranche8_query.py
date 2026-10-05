#!/usr/bin/env python3
"""Side-tool entry to explicit Tranche 8 evidence inspection/check levels."""

from pathlib import Path
import sys

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer.paths import repository_root  # noqa: E402

sys.path.insert(0, str(repository_root() / "implementation/phase-9-grcv4/verification"))
from tranche8_evidence import main  # noqa: E402

if __name__ == "__main__":
    main()

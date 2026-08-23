"""Fresh-process replay worker for the GRV6 boundary-state diagnostic."""

from __future__ import annotations

from pathlib import Path
import sys

from artifact_io import canonical_json_bytes
from grv6_methods import fresh_step_replay_projection

from pygrc.models import GRC9V3


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(
            "usage: grv6_boundary_replay_worker.py SNAPSHOT ZERO_BAND TOLERANCE"
        )
    snapshot = Path(sys.argv[1])
    zero_band = float(sys.argv[2])
    tolerance = float(sys.argv[3])
    projection = fresh_step_replay_projection(
        GRC9V3.load(str(snapshot)),
        current_zero_band=zero_band,
        fixed_state_tolerance=tolerance,
    )
    sys.stdout.buffer.write(canonical_json_bytes(projection))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()

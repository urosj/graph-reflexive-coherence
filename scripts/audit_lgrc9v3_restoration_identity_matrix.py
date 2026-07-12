"""Audit the native restoration identity on the RCAE C02 source fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RCAE_ROOT = PROJECT_ROOT.parent / "reflexive-coherence-agentic-ecology"
RCAE_EXPERIMENT_RELATIVE = Path(
    "experiments/2026-07-AE01-post-n30-demand-composition-atlas"
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"expected JSON object: {path}")
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rcae-root",
        type=Path,
        default=DEFAULT_RCAE_ROOT,
        help="Path to the reflexive-coherence-agentic-ecology repository.",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    rcae_experiment = args.rcae_root.resolve() / RCAE_EXPERIMENT_RELATIVE
    if not rcae_experiment.is_dir():
        raise FileNotFoundError(f"RCAE P2-I1 experiment not found: {rcae_experiment}")

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    sys.path.insert(0, str(rcae_experiment / "scripts"))

    from pygrc import core, models
    from pygrc.core import digest_snapshot
    from pygrc.models import (
        digest_lgrc9v3_restoration_identity_v1,
        lgrc9v3_restoration_identity_v1,
    )
    from p2_i1_execution import (  # type: ignore[import-not-found]
        _contact_rows,
        _drain_queue,
        _reference_delta,
        restoration_projection,
    )
    from p2_i1_runtime import build_fixture  # type: ignore[import-not-found]

    fixture = _load_json(rcae_experiment / "configs/p2_i1_fixture.json")
    cells = _load_json(rcae_experiment / "configs/p2_i1_cells.json")
    model, _route = build_fixture(
        fixture,
        cells,
        {"core": core, "models": models},
        seed=211,
        cell_id="candidate-conditioning",
    )

    model.schedule_packet_departure(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=float(fixture["packets"]["writer_amount"]),
        departure_event_time_key=float(
            fixture["packets"]["writer_departure_event_time_key"]
        ),
        scheduler_event_index=1,
    )
    _drain_queue(model)
    if len(_contact_rows(model)) != 2:
        raise RuntimeError("expected writer departure and arrival contacts")
    cell = next(
        row for row in cells["cells"] if row["cell_id"] == "candidate-conditioning"
    )
    model.emit_feedback_eligibility_surface_row(
        front_node_ids=fixture["feedback"]["front_node_ids"],
        rear_node_ids=fixture["feedback"]["rear_node_ids"],
        reference_delta=_reference_delta(fixture, cell),
        feedback_threshold=float(fixture["feedback"]["feedback_threshold"]),
        expected_next_route_id=fixture["feedback"]["expected_next_route_id"],
        expected_next_channel_id=fixture["feedback"]["expected_next_channel_id"],
    )

    snapshots = [model.snapshot()]
    restored_models: list[Any] = []
    current = model
    with tempfile.TemporaryDirectory() as temp_dir:
        for cycle in range(3):
            path = Path(temp_dir) / f"cycle-{cycle}.json"
            current.save(str(path))
            current = models.LGRC9V3.load(str(path))
            restored_models.append(current)
            snapshots.append(current.snapshot())

    identity_artifacts = [
        lgrc9v3_restoration_identity_v1(snapshot) for snapshot in snapshots
    ]
    identity_digests = [
        digest_lgrc9v3_restoration_identity_v1(snapshot) for snapshot in snapshots
    ]
    raw_digests = [digest_snapshot(snapshot) for snapshot in snapshots]

    original_twin = model
    restored_twin = restored_models[0]
    for twin in (original_twin, restored_twin):
        state = twin.get_state()
        twin.schedule_packet_departure(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=float(fixture["packets"]["writer_amount"]),
            departure_event_time_key=float(state.event_time_key) + 1.0,
            scheduler_event_index=int(state.scheduler_event_index) + 1,
        )
        _drain_queue(twin)

    continuation_identity_equal = lgrc9v3_restoration_identity_v1(
        original_twin
    ) == lgrc9v3_restoration_identity_v1(restored_twin)
    continuation_runtime_equal = (
        original_twin.snapshot()["dynamics"]["lgrc9v3_runtime"]
        == restored_twin.snapshot()["dynamics"]["lgrc9v3_runtime"]
    )

    checks = {
        "identity_artifacts_equal_across_three_loads": all(
            artifact == identity_artifacts[0] for artifact in identity_artifacts
        ),
        "identity_digests_equal_across_three_loads": len(set(identity_digests)) == 1,
        "raw_snapshot_digests_remain_distinct": len(set(raw_digests)) > 1,
        "raw_digest_first_third_loaded_cycle_matches": raw_digests[1] == raw_digests[3],
        "raw_digest_first_second_loaded_cycle_differs": raw_digests[1]
        != raw_digests[2],
        "exact_runtime_artifact_after_first_load": snapshots[0]["dynamics"][
            "lgrc9v3_runtime"
        ]
        == snapshots[1]["dynamics"]["lgrc9v3_runtime"],
        "events_after_first_load": snapshots[0]["events"] == snapshots[1]["events"],
        "observables_after_first_load": snapshots[0]["observables"]
        == snapshots[1]["observables"],
        "rcae_c02_projection_after_first_load": restoration_projection(snapshots[0])
        == restoration_projection(snapshots[1]),
        "equal_input_continuation_identity": continuation_identity_equal,
        "equal_input_continuation_runtime": continuation_runtime_equal,
    }
    status = "passed" if all(checks.values()) else "failed"
    result = {
        "artifact_kind": "lgrc9v3_restoration_identity_i93_rcae_matrix",
        "artifact_schema_version": ("lgrc9v3_restoration_identity_i93_rcae_matrix_v1"),
        "status": status,
        "fixture": {
            "source": (
                "../reflexive-coherence-agentic-ecology/"
                "experiments/2026-07-AE01-post-n30-demand-composition-atlas"
            ),
            "seed": 211,
            "cell_id": "candidate-conditioning",
            "window": "post_writer_feedback_surface_branch_point",
        },
        "raw_snapshot_digests": raw_digests,
        "restoration_identity_digests": identity_digests,
        "checks": checks,
        "claim_boundary": {
            "restoration_identity_supported_pending_closeout": status == "passed",
            "raw_snapshot_byte_identity_required": False,
            "unrestricted_behavioral_equivalence": False,
            "rc_identity_supported": False,
            "selfhood_supported": False,
            "agency_supported": False,
            "native_shared_medium_supported": False,
        },
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

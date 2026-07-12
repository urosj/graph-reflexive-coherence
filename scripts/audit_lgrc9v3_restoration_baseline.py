"""Reproduce the Phase 8 LGRC9V3 restoration-identity baseline."""

from __future__ import annotations

import argparse
import json
import math
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


def _display(value: object, digest_canonical_data: Any) -> object:
    if isinstance(value, (dict, list)):
        return {
            "type": type(value).__name__,
            "canonical_digest": digest_canonical_data(value),
        }
    return {"type": type(value).__name__, "value": value}


def _differences(
    left: object,
    right: object,
    *,
    digest_canonical_data: Any,
    path: str = "",
) -> list[dict[str, Any]]:
    if isinstance(left, dict) and isinstance(right, dict):
        rows: list[dict[str, Any]] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}" if path else str(key)
            if key not in left:
                rows.append(
                    {
                        "path": child,
                        "before": "__absent__",
                        "after": _display(right[key], digest_canonical_data),
                    }
                )
            elif key not in right:
                rows.append(
                    {
                        "path": child,
                        "before": _display(left[key], digest_canonical_data),
                        "after": "__absent__",
                    }
                )
            else:
                rows.extend(
                    _differences(
                        left[key],
                        right[key],
                        digest_canonical_data=digest_canonical_data,
                        path=child,
                    )
                )
        return rows
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return [
                {
                    "path": path,
                    "before": _display(left, digest_canonical_data),
                    "after": _display(right, digest_canonical_data),
                }
            ]
        rows = []
        for index, (left_item, right_item) in enumerate(
            zip(left, right, strict=True)
        ):
            rows.extend(
                _differences(
                    left_item,
                    right_item,
                    digest_canonical_data=digest_canonical_data,
                    path=f"{path}.{index}",
                )
            )
        return rows
    signed_zero_differs = (
        isinstance(left, float)
        and isinstance(right, float)
        and left == 0.0
        and right == 0.0
        and math.copysign(1.0, left) != math.copysign(1.0, right)
    )
    if type(left) is not type(right) or left != right or signed_zero_differs:
        return [
            {
                "path": path,
                "before": _display(left, digest_canonical_data),
                "after": _display(right, digest_canonical_data),
            }
        ]
    return []


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rcae-root",
        type=Path,
        default=DEFAULT_RCAE_ROOT,
        help="Path to the reflexive-coherence-agentic-ecology repository.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path. The report is always printed.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    rcae_experiment = args.rcae_root.resolve() / RCAE_EXPERIMENT_RELATIVE
    if not rcae_experiment.is_dir():
        raise FileNotFoundError(f"RCAE P2-I1 experiment not found: {rcae_experiment}")

    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    sys.path.insert(0, str(rcae_experiment / "scripts"))

    from pygrc import core, models
    from pygrc.core import canonical_json_dumps, digest_canonical_data
    from p2_i1_execution import (
        _contact_rows,
        _drain_queue,
        _reference_delta,
        restoration_projection,
    )
    from p2_i1_runtime import build_fixture

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
        row
        for row in cells["cells"]
        if row["cell_id"] == "candidate-conditioning"
    )
    model.emit_feedback_eligibility_surface_row(
        front_node_ids=fixture["feedback"]["front_node_ids"],
        rear_node_ids=fixture["feedback"]["rear_node_ids"],
        reference_delta=_reference_delta(fixture, cell),
        feedback_threshold=float(fixture["feedback"]["feedback_threshold"]),
        expected_next_route_id=fixture["feedback"]["expected_next_route_id"],
        expected_next_channel_id=fixture["feedback"]["expected_next_channel_id"],
    )

    snapshot_0 = model.snapshot()
    with tempfile.TemporaryDirectory() as temp_dir:
        paths = [Path(temp_dir) / f"cycle-{index}.json" for index in range(3)]
        model.save(str(paths[0]))
        restored_1 = models.LGRC9V3.load(str(paths[0]))
        snapshot_1 = restored_1.snapshot()
        restored_1.save(str(paths[1]))
        restored_2 = models.LGRC9V3.load(str(paths[1]))
        snapshot_2 = restored_2.snapshot()
        restored_2.save(str(paths[2]))
        restored_3 = models.LGRC9V3.load(str(paths[2]))
        snapshot_3 = restored_3.snapshot()

    snapshots = [snapshot_0, snapshot_1, snapshot_2, snapshot_3]
    digests = [digest_canonical_data(snapshot) for snapshot in snapshots]
    result = {
        "artifact": "phase8_lgrc9_restoration_identity_baseline_diagnostic",
        "fixture": {
            "source": "RCAE P2-I1 fixture",
            "seed": 211,
            "cell_id": "candidate-conditioning",
            "window": "post_writer_feedback_surface_branch_point",
        },
        "snapshot_digests": {
            "before_save": digests[0],
            "after_first_load": digests[1],
            "after_second_load": digests[2],
            "after_third_load": digests[3],
        },
        "first_load_differences": _differences(
            snapshot_0,
            snapshot_1,
            digest_canonical_data=digest_canonical_data,
        ),
        "second_load_differences": _differences(
            snapshot_1,
            snapshot_2,
            digest_canonical_data=digest_canonical_data,
        ),
        "third_load_differences": _differences(
            snapshot_2,
            snapshot_3,
            digest_canonical_data=digest_canonical_data,
        ),
        "python_value_equality_after_first_and_second_load": (
            snapshot_1 == snapshot_2
        ),
        "canonical_digest_equality_after_first_and_second_load": (
            digests[1] == digests[2]
        ),
        "canonical_digest_cycle_first_to_third": digests[1] == digests[3],
        "outer_groups_equal_after_first_load": {
            key: snapshot_0.get(key) == snapshot_1.get(key)
            for key in (
                "metadata",
                "topology",
                "basin_attributes",
                "edge_labels",
                "dynamics",
                "observables",
                "events",
            )
        },
        "exact_lgrc_runtime_artifact_equal": (
            snapshot_0["dynamics"]["lgrc9v3_runtime"]
            == snapshot_1["dynamics"]["lgrc9v3_runtime"]
        ),
        "rcae_c02_projection_equal": (
            restoration_projection(snapshot_0)
            == restoration_projection(snapshot_1)
        ),
        "public_identity_surface_absent": not any(
            hasattr(target, "lgrc9v3_restoration_identity_v1")
            for target in (models, models.LGRC9V3)
        ),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")

    canonical_json_dumps(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

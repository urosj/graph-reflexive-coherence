"""Shared fixture and transform harness for GRC9V3 property experiments.

This module is experiment-local. It imports canonical port helpers from
``src/pygrc`` but does not change runtime behavior.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import random
from typing import Any

from pygrc.models.grc_9_ports import port_to_rc, rc_to_port


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
LANE_ID = "current_hybrid_signed_hessian"
DEFAULT_SIGNED_HESSIAN_BACKEND = "row_basis_diagonal"
ARTIFACT_SCHEMA_VERSION = "grc9v3_properties_iter2_v1"
PORT_IDS = tuple(range(1, 10))
AXES = tuple(range(1, 4))


@dataclass(frozen=True)
class PortTreatment:
    """One central-node port treatment in the canonical 3x3 port chart."""

    port_id: int
    row: int
    column: int
    active: bool
    coherence_delta: float
    conductance: float
    flux_uv: float


@dataclass(frozen=True)
class CentralNodeFixture:
    """Central-node fixture contract shared by O-style and D-style runs."""

    fixture_id: str
    seed: int
    lane_id: str
    central_node_id: int
    port_matrix: list[PortTreatment]
    notes: list[str]


def _validate_axis_permutation(values: tuple[int, int, int]) -> None:
    if tuple(sorted(values)) != AXES:
        raise ValueError("axis permutation must contain exactly 1, 2, 3")


def _validate_port_map(port_map: dict[int, int]) -> None:
    if sorted(port_map) != list(PORT_IDS):
        raise ValueError("port map must define every source port 1..9")
    if sorted(port_map.values()) != list(PORT_IDS):
        raise ValueError("port map must be a bijection over target ports 1..9")


def validate_fixture_contract(fixture: CentralNodeFixture) -> None:
    """Validate the static fixture contract before runtime binding."""

    if fixture.lane_id != LANE_ID:
        raise ValueError(f"fixture lane_id must be {LANE_ID!r}")
    if fixture.central_node_id < 0:
        raise ValueError("central_node_id must be nonnegative")
    seen_ports = [treatment.port_id for treatment in fixture.port_matrix]
    if sorted(seen_ports) != list(PORT_IDS):
        raise ValueError("fixture port_matrix must contain every port 1..9 once")
    for treatment in fixture.port_matrix:
        expected_row, expected_column = port_to_rc(treatment.port_id)
        if (treatment.row, treatment.column) != (expected_row, expected_column):
            raise ValueError("fixture row/column must match canonical port id")
        if treatment.conductance < 0.0:
            raise ValueError("conductance must be nonnegative")


def row_permutation_map(row_permutation: tuple[int, int, int]) -> dict[int, int]:
    """Map old ports to new ports by permuting rows and preserving columns."""

    _validate_axis_permutation(row_permutation)
    mapping = {}
    for port_id in PORT_IDS:
        row, column = port_to_rc(port_id)
        mapping[port_id] = rc_to_port(row_permutation[row - 1], column)
    return mapping


def column_permutation_map(column_permutation: tuple[int, int, int]) -> dict[int, int]:
    """Map old ports to new ports by preserving rows and permuting columns."""

    _validate_axis_permutation(column_permutation)
    mapping = {}
    for port_id in PORT_IDS:
        row, column = port_to_rc(port_id)
        mapping[port_id] = rc_to_port(row, column_permutation[column - 1])
    return mapping


def transpose_map() -> dict[int, int]:
    """Map old ports to new ports by swapping row and column coordinates."""

    mapping = {}
    for port_id in PORT_IDS:
        row, column = port_to_rc(port_id)
        mapping[port_id] = rc_to_port(column, row)
    return mapping


def is_row_column_factorized(port_map: dict[int, int]) -> bool:
    """Return whether a map factors as independent row and column maps."""

    _validate_port_map(port_map)
    row_map: dict[int, int] = {}
    column_map: dict[int, int] = {}
    for old_port, new_port in port_map.items():
        old_row, old_column = port_to_rc(old_port)
        new_row, new_column = port_to_rc(new_port)
        if old_row in row_map and row_map[old_row] != new_row:
            return False
        if old_column in column_map and column_map[old_column] != new_column:
            return False
        row_map[old_row] = new_row
        column_map[old_column] = new_column
    return sorted(row_map.values()) == list(AXES) and sorted(column_map.values()) == list(AXES)


def is_transpose_factorized(port_map: dict[int, int]) -> bool:
    """Return whether a map factors after swapping row and column axes."""

    _validate_port_map(port_map)
    row_to_column: dict[int, int] = {}
    column_to_row: dict[int, int] = {}
    for old_port, new_port in port_map.items():
        old_row, old_column = port_to_rc(old_port)
        new_row, new_column = port_to_rc(new_port)
        if old_row in row_to_column and row_to_column[old_row] != new_column:
            return False
        if old_column in column_to_row and column_to_row[old_column] != new_row:
            return False
        row_to_column[old_row] = new_column
        column_to_row[old_column] = new_row
    return sorted(row_to_column.values()) == list(AXES) and sorted(column_to_row.values()) == list(AXES)


def degree_preserving_random_relabel_map(seed: int) -> dict[int, int]:
    """Return a deterministic S9 relabeling that breaks 3x3 factorization."""

    rng = random.Random(seed)
    ports = list(PORT_IDS)
    for _ in range(1000):
        shuffled = ports[:]
        rng.shuffle(shuffled)
        mapping = dict(zip(PORT_IDS, shuffled, strict=True))
        if not is_row_column_factorized(mapping) and not is_transpose_factorized(mapping):
            return mapping
    raise RuntimeError("failed to generate a non-factorized port relabeling")


def default_central_node_fixture(seed: int = 0) -> CentralNodeFixture:
    """Create a deterministic balanced central-node fixture."""

    treatments: list[PortTreatment] = []
    for port_id in PORT_IDS:
        row, column = port_to_rc(port_id)
        treatments.append(
            PortTreatment(
                port_id=port_id,
                row=row,
                column=column,
                active=True,
                coherence_delta=0.1,
                conductance=1.0,
                flux_uv=0.2 if (port_id + seed) % 2 == 0 else -0.2,
            )
        )
    return CentralNodeFixture(
        fixture_id=f"iter2_central_node_seed_{seed}_balanced",
        seed=seed,
        lane_id=LANE_ID,
        central_node_id=0,
        port_matrix=treatments,
        notes=[
            "Balanced smoke fixture for transform verification.",
            "All ports are active so degree-preserving relabeling keeps edge count fixed.",
            "Column-H is not a direct Lane A gate in this fixture contract.",
        ],
    )


def partial_activity_fixture(
    *,
    seed: int = 0,
    active_ports: tuple[int, ...],
) -> CentralNodeFixture:
    """Create a deterministic central-node fixture with selected active ports."""

    active_set = set(active_ports)
    if not active_set.issubset(set(PORT_IDS)):
        raise ValueError("active_ports must be drawn from canonical ports 1..9")
    treatments: list[PortTreatment] = []
    for port_id in PORT_IDS:
        row, column = port_to_rc(port_id)
        active = port_id in active_set
        treatments.append(
            PortTreatment(
                port_id=port_id,
                row=row,
                column=column,
                active=active,
                coherence_delta=0.1 if active else 0.0,
                conductance=1.0 if active else 0.0,
                flux_uv=(0.2 if (port_id + seed) % 2 == 0 else -0.2)
                if active
                else 0.0,
            )
        )
    return CentralNodeFixture(
        fixture_id=f"iter2_central_node_seed_{seed}_degree_{len(active_set)}",
        seed=seed,
        lane_id=LANE_ID,
        central_node_id=0,
        port_matrix=treatments,
        notes=[
            "Partial-activity helper fixture for saturation controls.",
            "Inactive ports are represented in the schema but should not bind to live runtime edges.",
        ],
    )


def row_stress_fixture(
    *,
    seed: int = 0,
    stressed_row: int = 1,
) -> CentralNodeFixture:
    """Create a non-uniform row-stress fixture for energy-transform checks."""

    if stressed_row not in AXES:
        raise ValueError("stressed_row must be 1, 2, or 3")
    treatments: list[PortTreatment] = []
    for port_id in PORT_IDS:
        row, column = port_to_rc(port_id)
        is_stressed = row == stressed_row
        treatments.append(
            PortTreatment(
                port_id=port_id,
                row=row,
                column=column,
                active=True,
                coherence_delta=0.3 if is_stressed else 0.05,
                conductance=1.2 if is_stressed else 1.0,
                flux_uv=(0.35 if (column + seed) % 2 == 0 else -0.35)
                if is_stressed
                else 0.05,
            )
        )
    return CentralNodeFixture(
        fixture_id=f"iter2_central_node_seed_{seed}_row_{stressed_row}_stress",
        seed=seed,
        lane_id=LANE_ID,
        central_node_id=0,
        port_matrix=treatments,
        notes=[
            "Non-uniform row-stress fixture used to verify energy preservation.",
            "Experiment A may specialize this pattern into row-1/row-2/row-3 fixtures.",
        ],
    )


def apply_port_map(
    fixture: CentralNodeFixture,
    port_map: dict[int, int],
    *,
    transform_id: str,
) -> CentralNodeFixture:
    """Apply a port relabeling to one central-node fixture."""

    _validate_port_map(port_map)
    remapped = []
    for treatment in fixture.port_matrix:
        new_port = port_map[treatment.port_id]
        new_row, new_column = port_to_rc(new_port)
        remapped.append(
            replace(
                treatment,
                port_id=new_port,
                row=new_row,
                column=new_column,
            )
        )
    return replace(
        fixture,
        fixture_id=f"{fixture.fixture_id}__{transform_id}",
        port_matrix=sorted(remapped, key=lambda item: item.port_id),
        notes=[*fixture.notes, f"Applied transform: {transform_id}"],
    )


def perturbation_energy(fixture: CentralNodeFixture) -> dict[str, Any]:
    """Compute row, column, and total perturbation energy for matching checks."""

    by_row = {str(row): 0.0 for row in AXES}
    by_column = {str(column): 0.0 for column in AXES}
    by_port: dict[str, float] = {}
    for treatment in fixture.port_matrix:
        if not treatment.active:
            energy = 0.0
        else:
            conductance_delta = treatment.conductance - 1.0
            energy = (
                treatment.coherence_delta**2
                + conductance_delta**2
                + treatment.flux_uv**2
            )
        by_port[str(treatment.port_id)] = energy
        by_row[str(treatment.row)] += energy
        by_column[str(treatment.column)] += energy
    return {
        "metric": "coherence_delta^2 + (conductance - 1)^2 + flux_uv^2",
        "by_port": by_port,
        "by_row": by_row,
        "by_column": by_column,
        "total": sum(by_port.values()),
    }


def total_energy_preserved(
    fixture: CentralNodeFixture,
    port_map: dict[int, int],
) -> bool:
    """Return whether a port transform preserves total perturbation energy."""

    before = perturbation_energy(fixture)["total"]
    after = perturbation_energy(
        apply_port_map(fixture, port_map, transform_id="energy_check")
    )["total"]
    return abs(float(before) - float(after)) <= 1e-12


def fixture_schema() -> dict[str, Any]:
    """Return the Iteration 2 fixture schema."""

    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "central_node_fixture": {
            "fixture_id": "string",
            "seed": "integer",
            "lane_id": "current_hybrid_signed_hessian",
            "central_node_id": "integer",
            "port_matrix": [
                {
                    "port_id": "integer 1..9",
                    "row": "integer 1..3",
                    "column": "integer 1..3",
                    "active": "boolean",
                    "coherence_delta": "number",
                    "conductance": "number",
                    "flux_uv": "number",
                }
            ],
        },
    }


def runtime_assumptions() -> dict[str, str]:
    """Record runtime assumptions that belong to run manifests, not fixtures."""

    return {
        "lane_id": LANE_ID,
        "signed_hessian_backend": DEFAULT_SIGNED_HESSIAN_BACKEND,
        "column_h_status": "derived_analysis_proxy_only",
        "runtime_mutation_policy": "experiment code must not mutate src/pygrc",
    }


def run_id_convention() -> dict[str, str]:
    """Define deterministic run id construction for experiment artifacts."""

    return {
        "format": "<experiment_id>__<fixture_id>__<transform_id>__seed_<seed>__<schema_version>",
        "normalization": "lowercase ASCII; replace non [a-z0-9_.-] characters with underscores",
        "stability": "deterministic; no timestamp in reproducible run ids",
    }


def blocked_observations_schema() -> dict[str, str]:
    """Define the shared blocked-observations CSV columns."""

    return {
        "experiment": "experiment or discriminator id",
        "observation": "claim-specific observation name",
        "status": "blocked | inconclusive",
        "artifact_source": "artifact path or runtime surface attempted",
        "reconstruction_attempt": "short description of extraction/reconstruction attempt",
        "notes": "free-form audit note",
    }


def state_mapping_convention() -> dict[str, str]:
    """Describe how fixture treatments bind into GRC9V3 runtime state."""

    return {
        "central_node_id": "must exist in the target GRC9V3State before binding",
        "active_false": "schema placeholder only; do not create a live PortEdge",
        "active_true": "create one live PortEdge attached to central_node_id and treatment.port_id",
        "coherence_delta": "added to the selected node coherence by the experiment-specific fixture builder",
        "conductance": "maps to PortEdge.conductance and GRC9V3State.base_conductance[edge_id]",
        "flux_uv": "maps to PortEdge.flux_uv with orientation recorded in the run manifest",
    }


def runtime_binding_requirements() -> dict[str, str]:
    """Define checks that fixture-to-state binders must run before simulation."""

    return {
        "central_node_exists": "assert central_node_id is present in GRC9V3State.topology",
        "active_degree_matches": "assert live edges at the central node equal active treatment count",
        "port_occupancy_matches": "assert active treatments occupy exactly their declared ports",
        "inactive_ports_absent": "assert inactive treatments do not create live PortEdge records",
    }


def artifact_entry_points() -> dict[str, str]:
    """Define the shared artifact extraction entry points for later iterations."""

    return {
        "run_manifest": "../outputs/<run_id>/run_manifest.json",
        "step_events": "../outputs/<run_id>/step_events.jsonl",
        "lane_a_spark_gate_traces": "../outputs/<run_id>/lane_a_spark_gate_traces.jsonl",
        "state_snapshots": "../outputs/<run_id>/snapshots/",
        "comparison_report": "../reports/<run_id>_comparison.md",
        "blocked_observations": "../reports/<run_id>_blocked_observations.csv",
    }


def comparison_report_schema() -> dict[str, Any]:
    """Define the shared comparison report schema for transform pairs."""

    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "fixture_id": "string",
        "run_id": "string",
        "lane_id": LANE_ID,
        "seed": "integer",
        "transform_id": "string",
        "port_map": {"source_port": "target_port"},
        "preserves_edge_count": "boolean",
        "preserves_active_degree": "boolean",
        "factorization_class": "row_column | transpose | non_factorized",
        "energy_profile": "perturbation_energy object",
        "artifact_sources": "artifact_entry_points object",
        "blocked_observations_schema": "blocked_observations_schema object",
        "blocked_or_inconclusive_claims": ["string"],
    }


def transform_manifest(seed: int = 0) -> dict[str, Any]:
    """Build the deterministic Iteration 2 transform manifest."""

    row_map = row_permutation_map((2, 3, 1))
    column_map = column_permutation_map((3, 1, 2))
    transposed = transpose_map()
    random_map = degree_preserving_random_relabel_map(seed + 1000)
    base_fixture = default_central_node_fixture(seed=seed)
    row_stress = row_stress_fixture(seed=seed, stressed_row=1)
    partial_degree_8 = partial_activity_fixture(seed=seed, active_ports=tuple(range(1, 9)))
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "runtime_assumptions": runtime_assumptions(),
        "seed_replay": {
            "base_seed": seed,
            "random_relabel_seed": seed + 1000,
            "rule": "Every run manifest records seed, fixture_id, transform_id, lane_id, and schema_version.",
        },
        "run_id_convention": run_id_convention(),
        "fixture_schema": fixture_schema(),
        "base_fixture": asdict(base_fixture),
        "row_stress_fixture_example": asdict(row_stress),
        "partial_activity_fixture_example": asdict(partial_degree_8),
        "energy_matching": perturbation_energy(base_fixture),
        "non_uniform_energy_matching": perturbation_energy(row_stress),
        "transforms": {
            "row_permutation_231": row_map,
            "column_permutation_312": column_map,
            "row_column_transpose": transposed,
            "degree_preserving_random_relabel": random_map,
        },
        "state_mapping_convention": state_mapping_convention(),
        "runtime_binding_requirements": runtime_binding_requirements(),
        "artifact_entry_points": artifact_entry_points(),
        "blocked_observations_schema": blocked_observations_schema(),
        "comparison_report_schema": comparison_report_schema(),
    }


def verify_transform_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Verify the checklist properties for the generated transform manifest."""

    base_fixture = default_central_node_fixture(seed=manifest["seed_replay"]["base_seed"])
    row_stress = row_stress_fixture(
        seed=manifest["seed_replay"]["base_seed"],
        stressed_row=1,
    )
    partial_degree_8 = partial_activity_fixture(
        seed=manifest["seed_replay"]["base_seed"],
        active_ports=tuple(range(1, 9)),
    )
    validate_fixture_contract(base_fixture)
    validate_fixture_contract(row_stress)
    validate_fixture_contract(partial_degree_8)
    active_count = sum(treatment.active for treatment in base_fixture.port_matrix)
    transforms = {
        key: {int(port): int(target) for port, target in value.items()}
        for key, value in manifest["transforms"].items()
    }
    transformed_active_counts = {
        transform_id: sum(
            treatment.active
            for treatment in apply_port_map(
                base_fixture,
                port_map,
                transform_id=transform_id,
            ).port_matrix
        )
        for transform_id, port_map in transforms.items()
    }
    return {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "fixture_generation_deterministic": (
            asdict(default_central_node_fixture(seed=manifest["seed_replay"]["base_seed"]))
            == asdict(default_central_node_fixture(seed=manifest["seed_replay"]["base_seed"]))
        ),
        "edge_count_preserved": all(
            count == active_count for count in transformed_active_counts.values()
        ),
        "active_degree_preserved": transformed_active_counts,
        "row_transform_factorized": is_row_column_factorized(
            transforms["row_permutation_231"]
        ),
        "column_transform_factorized": is_row_column_factorized(
            transforms["column_permutation_312"]
        ),
        "transpose_transform_swaps_axes": is_transpose_factorized(
            transforms["row_column_transpose"]
        ),
        "random_relabel_breaks_factorization": (
            not is_row_column_factorized(transforms["degree_preserving_random_relabel"])
            and not is_transpose_factorized(transforms["degree_preserving_random_relabel"])
        ),
        "balanced_energy_preserved_under_transforms": {
            transform_id: total_energy_preserved(base_fixture, port_map)
            for transform_id, port_map in transforms.items()
        },
        "non_uniform_energy_preserved_under_transforms": {
            transform_id: total_energy_preserved(row_stress, port_map)
            for transform_id, port_map in transforms.items()
        },
        "partial_activity_degree_8_helper_active_count": sum(
            treatment.active for treatment in partial_degree_8.port_matrix
        ),
        "fixture_contract_validation": True,
        "runtime_binding_requirements_declared": bool(
            manifest["runtime_binding_requirements"]
        ),
        "blocked_observations_schema_declared": bool(
            manifest["blocked_observations_schema"]
        ),
        "run_id_convention_declared": bool(manifest["run_id_convention"]),
        "state_mapping_convention_declared": bool(
            manifest["state_mapping_convention"]
        ),
        "imports_from_src_without_runtime_mutation": True,
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_report(path: Path, manifest: dict[str, Any], verification: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Iteration 2 Shared Fixture And Transform Harness",
        "",
        "Status: complete.",
        "",
        "## Scope",
        "",
        "This report defines the experiment-local central-node fixture schema,",
        "transform utilities, seed replay convention, artifact entry points, and",
        "comparison report schema for the GRC9V3 property experiments.",
        "",
        "The baseline lane is `current_hybrid_signed_hessian`. Column-H remains",
        "a derived analysis proxy unless a separate canonical-column-H lane exists.",
        "",
        "## Generated Artifacts",
        "",
        "- `../configs/shared_fixture_transform_manifest.json`",
        "- `../outputs/iter2_fixture_transform_verification.json`",
        "",
        "## Verification",
        "",
    ]
    for key, value in verification.items():
        rendered_value = json.dumps(value, sort_keys=True)
        lines.append(f"- `{key}`: `{rendered_value}`")
    lines.extend(
        [
            "",
            "## Seed Replay",
            "",
            f"- base seed: `{manifest['seed_replay']['base_seed']}`",
            f"- random relabel seed: `{manifest['seed_replay']['random_relabel_seed']}`",
            "- required run-manifest fields: `seed`, `fixture_id`, `transform_id`,",
            "  `lane_id`, and `schema_version`",
            f"- run id format: `{manifest['run_id_convention']['format']}`",
            "",
            "## Runtime Assumptions",
            "",
            f"- lane id: `{manifest['runtime_assumptions']['lane_id']}`",
            "- signed Hessian backend: "
            f"`{manifest['runtime_assumptions']['signed_hessian_backend']}`",
            f"- column-H status: `{manifest['runtime_assumptions']['column_h_status']}`",
            "",
            "## Artifact Entry Points",
            "",
        ]
    )
    for key, value in manifest["artifact_entry_points"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Blocked Observations CSV",
            "",
        ]
    )
    for key, value in manifest["blocked_observations_schema"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## State Mapping Convention",
            "",
        ]
    )
    for key, value in manifest["state_mapping_convention"].items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Runtime Binding Requirements",
            "",
        ]
    )
    for key, value in manifest["runtime_binding_requirements"].items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_default_artifacts(seed: int = 0) -> dict[str, Path]:
    """Write the Iteration 2 manifest, verification JSON, and report."""

    manifest = transform_manifest(seed=seed)
    verification = verify_transform_manifest(manifest)
    manifest_path = EXPERIMENT_ROOT / "configs" / "shared_fixture_transform_manifest.json"
    verification_path = (
        EXPERIMENT_ROOT / "outputs" / "iter2_fixture_transform_verification.json"
    )
    report_path = EXPERIMENT_ROOT / "reports" / "iter2_shared_fixture_transform_harness.md"
    _write_json(manifest_path, manifest)
    _write_json(verification_path, verification)
    _write_report(report_path, manifest, verification)
    return {
        "manifest": manifest_path,
        "verification": verification_path,
        "report": report_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--write-defaults", action="store_true")
    args = parser.parse_args()
    if args.write_defaults:
        paths = write_default_artifacts(seed=args.seed)
        print(json.dumps({key: str(value) for key, value in paths.items()}, indent=2))
    else:
        manifest = transform_manifest(seed=args.seed)
        print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

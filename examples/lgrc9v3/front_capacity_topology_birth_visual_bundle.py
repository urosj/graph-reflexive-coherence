"""Capture a front-capacity-gated LGRC9V3 topology birth visual bundle.

What this example does:
    Lowers a GRCL9V3 front-growth source document into a GRC9V3 state, then
    runs LGRC9V3 boundary-birth scheduling with
    `causal_boundary_birth_parent_eligibility = grcl9v3_front_capacity`.
    The boundary-birth producer may schedule only through the lowered
    `grcl9v3_front_growth_eligible_ports` and
    `grcl9v3_growth_parent_capacity_sources` metadata. It then consumes the
    scheduled boundary-birth trial and saves graph checkpoints before and after
    the visible topology change.

What this example is not:
    It is not an MB5/MB6 closeout, not native support evidence, not semantic
    learning, not agency, and not Phase 8 completion. It is the corrected
    front-capacity visual companion to the diagnostic
    `topology_birth_refinement_visual_bundle.py` example.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
import json
from pathlib import Path

from pygrc.landscapes.extensions.grcl9v3 import (
    GRCL9V3GrowthLocus,
    GRCL9V3HybridSparkRegion,
    GRCL9V3SourceDocument,
)
from pygrc.models import (
    CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
    EDGE_DELAY_POLICY_CONSTANT_DELAY,
    LAPSE_POLICY_UNIT,
    LGRC_RUNTIME_LEVEL_LGRC3,
    LGRC9V3,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_PARENT_ELIGIBILITY_GRCL9V3_FRONT_CAPACITY,
    LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX,
    lower_grcl9v3_source_to_grc9v3_state,
)
from pygrc.models.lgrc_9_v3_contract import (
    LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL,
)
from pygrc.telemetry import (
    GraphCheckpointIndex,
    GraphCheckpointReference,
    RunTelemetryIdentity,
    TelemetryArtifactPack,
    build_lgrc9v3_graph_checkpoint,
    build_telemetry_artifact_layout,
    event_rows_from_events,
    lgrc9v3_event_family_extensions_for_events,
    lgrc9v3_run_summary_family_extensions,
    lgrc9v3_step_family_extensions,
    run_summary_from_step_results,
    save_telemetry_artifact_pack,
    step_row_from_step_result,
)
from pygrc.visualization import (
    build_graph_run_visualization_layout,
    render_graph_run_visual_bundle,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_OUTPUT_ROOT = REPO_ROOT / "outputs" / "examples" / "lgrc9v3"
RUN_ID = "lgrc9v3-front-capacity-topology-birth-visual-bundle"


def print_json(label: str, payload: object) -> None:
    """Print deterministic JSON for terminal inspection."""

    print(f"\n{label}:")
    print(json.dumps(jsonable(payload), indent=2, sort_keys=True))


def jsonable(payload: object) -> object:
    """Return a JSON-serializable copy of nested telemetry payloads."""

    if isinstance(payload, Mapping):
        return {str(key): jsonable(value) for key, value in payload.items()}
    if isinstance(payload, Sequence) and not isinstance(payload, str | bytes):
        return [jsonable(value) for value in payload]
    return payload


def display_path(path: Path) -> str:
    """Return a repo-relative path when the artifact lives in this checkout."""

    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def front_capacity_source_document() -> GRCL9V3SourceDocument:
    """Return the GRCL9V3 front-growth source used by the corrected example."""

    motif_id = "grc9v3-motif-s0006-hybrid-spark-gate-positive-control"
    return GRCL9V3SourceDocument(
        fixture_name="lgrc9v3_front_capacity_birth_visual_fixture",
        manifest_entry_id="composed_grcl9v3_hybrid_composition_v1",
        expected_selector_ids=("front_growth_provenance",),
        constructs=(
            GRCL9V3HybridSparkRegion(
                construct_id="spark_region",
                motif_id=motif_id,
                source_role="positive_control",
                ownership="grc9v3_hybrid",
                candidate_region_id="candidate",
                saturation_profile={"active_degree": 9},
                spark_threshold=0.05,
            ),
            GRCL9V3GrowthLocus(
                construct_id="front_growth",
                motif_id=motif_id,
                source_role="positive_control",
                ownership="grc9_mechanical",
                parent_region_id="growth_parent",
                inactive_parent_port=5,
                outward_pressure_profile={
                    "pressure": "front",
                    "support_flux": 1.0,
                    "support_coherence": 9.0,
                    "support_conductance": 1.5,
                },
                lambda_birth=1.0,
                growth_semantics="front_capacity",
                front_capacity_source="spark_expansion_front",
                front_source_construct_id="spark_region",
            ),
        ),
        compiled_source_provenance={"composed_source_ancestry": ("spark", "growth")},
    )


def front_capacity_topology_birth_params() -> dict[str, object]:
    """Return opt-in params for front-capacity-gated boundary birth."""

    return {
        "dt": 1.0,
        "evolution": {
            "lambda_birth": 1.0,
            "alpha_seed": 0.25,
            "w_bond": 1.5,
            "rng_seed": 1,
        },
        "causal_modes": {
            "causal_layer_mode": CAUSAL_LAYER_MODE_TOPOLOGY_CHANGING_CAUSAL_HISTORY,
            "lgrc_runtime_level": LGRC_RUNTIME_LEVEL_LGRC3,
            "lapse_policy": LAPSE_POLICY_UNIT,
            "edge_delay_policy": EDGE_DELAY_POLICY_CONSTANT_DELAY,
            "event_time_policy": "explicit_event_time_key",
            "proper_time_accumulation_policy": "local_event_frontier",
            "causal_boundary_birth_allowed": True,
            "causal_boundary_birth_policy": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_POLICY_GRC9V3_OUTWARD_FLUX
            ),
            "causal_boundary_birth_parent_eligibility": (
                LGRC9V3_CAUSAL_BOUNDARY_BIRTH_PARENT_ELIGIBILITY_GRCL9V3_FRONT_CAPACITY
            ),
        },
    }


def checkpoint_index(
    identity: RunTelemetryIdentity,
    checkpoints: tuple[object, ...],
) -> GraphCheckpointIndex:
    """Build a file-backed checkpoint index for saved telemetry artifacts."""

    return GraphCheckpointIndex(
        identity=identity,
        selection_policy="initial+after-front-capacity-boundary-birth",
        selection_params={
            "include_initial": True,
            "include_after_front_capacity_boundary_birth": True,
        },
        checkpoints=tuple(
            GraphCheckpointReference(
                checkpoint_id=checkpoint.checkpoint_id,
                step_index=checkpoint.step_index,
                time=checkpoint.time,
                checkpoint_label=checkpoint.checkpoint_label,
                checkpoint_reason=checkpoint.checkpoint_reason,
                path=f"{checkpoint.checkpoint_id}.json",
                event_step_range=checkpoint.event_step_range,
                event_count_window=checkpoint.event_count_window,
                event_counts_by_kind_window=checkpoint.event_counts_by_kind_window,
            )
            for checkpoint in checkpoints
        ),
    )


def run_front_capacity_topology_birth_visual_bundle(
    *,
    output_root: Path = EXAMPLE_OUTPUT_ROOT,
) -> dict[str, object]:
    """Run, save, and visualize the front-capacity topology-birth bundle."""

    source_document = front_capacity_source_document()
    lowering = lower_grcl9v3_source_to_grc9v3_state(source_document)
    model = LGRC9V3.from_state(
        lowering.state,
        front_capacity_topology_birth_params(),
    )
    identity = RunTelemetryIdentity(
        run_id=RUN_ID,
        model_family="LGRC9V3",
        params_identity=model.get_params().params_hash,
        seed_name="front-capacity-boundary-birth-fixture",
        seed_source_reference=(
            "examples/lgrc9v3/front_capacity_topology_birth_visual_bundle.py"
        ),
        seed_path="examples/lgrc9v3/front_capacity_topology_birth_visual_bundle.py",
        param_family="lgrc9v3_front_capacity_topology_birth_visual",
        requested_steps=1,
    )
    layout = build_telemetry_artifact_layout(RUN_ID, root_dir=output_root)
    initial_observables = dict(model.compute_observables())
    checkpoints = [
        build_lgrc9v3_graph_checkpoint(
            model,
            identity=identity,
            checkpoint_id="checkpoint-00000000",
            checkpoint_label="initial_front_capacity_source",
            checkpoint_reason="initial",
        )
    ]

    produced = model.produce_events(
        policy=LGRC9V3_AUTONOMOUS_PRODUCER_POLICY_BOUNDARY_BIRTH_TRIAL
    )
    step_result = model.step()
    step_event_counts = dict(Counter(event.kind for event in step_result.events))
    checkpoints.append(
        build_lgrc9v3_graph_checkpoint(
            model,
            identity=identity,
            checkpoint_id="checkpoint-00000001",
            checkpoint_label="after_front_capacity_boundary_birth",
            checkpoint_reason="after_queue_event",
            event_count_window=len(step_result.events),
            event_counts_by_kind_window=step_event_counts,
        )
    )

    step_results = (step_result,)
    all_events = tuple(event for result in step_results for event in result.events)
    event_counts = dict(Counter(event.kind for event in all_events))
    topology_event_kinds = tuple(
        event.kind for event in model.get_state().topology_event_log
    )
    checkpoint_node_counts = [checkpoint.node_count for checkpoint in checkpoints]
    checkpoint_edge_counts = [checkpoint.edge_count for checkpoint in checkpoints]
    production_record = produced.production_records[0].to_artifact()

    step_rows = (
        step_row_from_step_result(
            step_result,
            identity=identity,
            family_extensions=lgrc9v3_step_family_extensions(model),
        ),
    )
    event_rows = event_rows_from_events(
        all_events,
        identity=identity,
        family_extensions_by_event=lgrc9v3_event_family_extensions_for_events(
            all_events
        ),
    )
    run_summary = run_summary_from_step_results(
        step_results,
        identity=identity,
        initial_observables=initial_observables,
        final_observables=model.compute_observables(),
        resolved_params=model.get_params().resolved_config,
        raw_params=model.get_params().raw_config,
        parameter_overrides={
            "example": "lgrc9v3_front_capacity_topology_birth_visual_bundle"
        },
        family_extensions=lgrc9v3_run_summary_family_extensions(model),
    )
    graph_index = checkpoint_index(identity, tuple(checkpoints))
    save_telemetry_artifact_pack(
        layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=run_summary,
        graph_checkpoint_index=graph_index,
        graph_checkpoints=tuple(checkpoints),
    )
    pack = TelemetryArtifactPack(
        layout=layout,
        step_rows=step_rows,
        event_rows=event_rows,
        run_summary=run_summary,
        graph_checkpoint_index=graph_index,
        graph_checkpoints=tuple(checkpoints),
    )
    visual_layout = build_graph_run_visualization_layout(layout)
    render_graph_run_visual_bundle(pack, layout=visual_layout)

    source_state = lowering.state
    return {
        "run_dir": display_path(layout.run_dir),
        "telemetry_dir": display_path(layout.telemetry_dir),
        "graph_checkpoint_index_path": display_path(
            layout.graph_checkpoint_index_path
        ),
        "graph_sequence_figure": display_path(visual_layout.sequence_figure_path),
        "graph_html": display_path(visual_layout.final_html_path),
        "event_counts_by_kind": event_counts,
        "topology_event_kinds": topology_event_kinds,
        "checkpoint_node_counts": checkpoint_node_counts,
        "checkpoint_edge_counts": checkpoint_edge_counts,
        "initial_node_count": checkpoint_node_counts[0],
        "final_node_count": checkpoint_node_counts[-1],
        "initial_edge_count": checkpoint_edge_counts[0],
        "final_edge_count": checkpoint_edge_counts[-1],
        "visible_topology_growth": (
            checkpoint_node_counts[-1] > checkpoint_node_counts[0]
            or checkpoint_edge_counts[-1] > checkpoint_edge_counts[0]
        ),
        "front_capacity_surface": {
            "eligible_ports": source_state.cached_quantities[
                "grcl9v3_front_growth_eligible_ports"
            ],
            "capacity_sources": source_state.cached_quantities[
                "grcl9v3_growth_parent_capacity_sources"
            ],
        },
        "production_summary": {
            "scheduled_event_count": produced.scheduled_event_count,
            "reason_code": production_record["reason_code"],
            "parent_eligibility_mode": production_record["observed_evidence"][
                "parent_eligibility_mode"
            ],
            "front_capacity_source": production_record["observed_evidence"][
                "front_capacity_source"
            ],
            "parent_port_id": production_record["observed_evidence"][
                "parent_port_id"
            ],
        },
        "claim_boundary": {
            "mb5_or_mb6_claim": False,
            "native_support": False,
            "semantic_learning": False,
            "agency": False,
            "phase8_completion": False,
        },
    }


def main() -> None:
    """Run the example and print artifact paths plus claim boundary."""

    artifacts = run_front_capacity_topology_birth_visual_bundle()
    print("LGRC9V3 front-capacity topology birth visual bundle")
    print_json("artifacts", artifacts)
    print(
        "\nInterpretation: this bundle demonstrates visible LGRC9V3 topology "
        "growth through a corrected front-capacity-gated boundary-birth path. "
        "It is a visual and telemetry example, not an MB5/MB6 closeout, not "
        "native support, not semantic learning, not agency, and not Phase 8 "
        "completion."
    )


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest

from pygrc.landscapes import (
    BasinSeedPrimitive,
    LandscapeInferenceWindow,
    LandscapeSeed,
    SeedConstitutiveProfile,
    SeedDocumentMeta,
    SeedPotential,
    build_landscape_inference_evidence_substrate,
    build_minimal_landscape_inference_seed,
    classify_landscape_basin_candidates,
    infer_landscape_basin_seed,
    validate_landscape_inference_seed_extensions,
    validate_landscape_seed,
)
from pygrc.telemetry.schema import (
    GraphCheckpointArtifact,
    RunTelemetryIdentity,
    RunTelemetrySummary,
)


def _identity(family: str = "grc9v3") -> RunTelemetryIdentity:
    return RunTelemetryIdentity(
        run_id=f"{family}_basin_run",
        model_family=family,
        params_identity="params",
        requested_steps=3,
    )


def _summary(identity: RunTelemetryIdentity, family: str) -> RunTelemetrySummary:
    return RunTelemetrySummary(
        identity=identity,
        completed_steps=3,
        final_step_index=2,
        initial_time=0.0,
        final_time=0.2,
        total_event_count=0,
        event_counts_by_kind={},
        initial_observables={},
        final_observables={},
        resolved_params={"evolution": {"dt": 0.1}},
        family_extensions={family: {"contract_version": "test"}},
    )


def _checkpoint(
    *,
    checkpoint_id: str,
    step_index: int,
    family: str = "grc9v3",
    include_geometry: bool = True,
    include_mass: bool = True,
    include_basin: bool = True,
) -> GraphCheckpointArtifact:
    first_node: dict[str, object] = {
        "node_id": 1,
        "coherence": 2.0,
        "sink_flag": include_basin,
        **({"basin_id": "1"} if include_basin else {}),
        **({"basin_mass": 4.5} if include_mass else {}),
    }
    second_node: dict[str, object] = {
        "node_id": 2,
        "coherence": 1.25,
        **({"basin_id": "1"} if include_basin else {}),
        **({"basin_mass": 1.0} if include_mass else {}),
    }
    if include_geometry:
        first_node.update({"gradient_norm": 0.01, "min_signed_hessian": 0.4})
        second_node.update({"gradient_norm": 0.05, "min_signed_hessian": 0.25})
    return GraphCheckpointArtifact(
        identity=_identity(family),
        checkpoint_id=checkpoint_id,
        step_index=step_index,
        time=float(step_index) * 0.1,
        checkpoint_label=f"step_{step_index}",
        checkpoint_reason="basin_test",
        graph_kind="weighted_graph",
        node_count=2,
        edge_count=1,
        node_records=(first_node, second_node),
        edge_records=(
            {
                "edge_id": 1,
                "source_node_id": 1,
                "target_node_id": 2,
                "conductance": 1.0,
            },
        ),
        family_extensions={family: {"checkpoint_marker": True}},
    )


def _load_result(
    *,
    family: str = "grc9v3",
    checkpoints: tuple[GraphCheckpointArtifact, ...],
) -> SimpleNamespace:
    identity = _identity(family)
    pack = SimpleNamespace(
        run_summary=_summary(identity, family),
        step_rows=(),
        event_rows=(),
        graph_checkpoints=checkpoints,
        graph_checkpoint_index=None,
    )
    window = LandscapeInferenceWindow(start_step=0, end_step=2, policy="whole_run")
    inferred_seed = build_minimal_landscape_inference_seed(
        pack,
        artifact_root=Path("outputs") / family / "landscape_inference" / "sessions" / "S0001",
        source_runtime_family=family,
        inference_window=window,
    )
    return SimpleNamespace(
        artifact_root=Path("outputs") / family / "landscape_inference" / "sessions" / "S0001",
        telemetry_pack=pack,
        source_runtime_family=family,
        inference_window=window,
        inferred_seed=inferred_seed,
    )


def _substrate(
    *,
    family: str = "grc9v3",
    include_geometry: bool = True,
    include_mass: bool = True,
    include_basin: bool = True,
):
    load_result = _load_result(
        family=family,
        checkpoints=(
            _checkpoint(
                checkpoint_id="c0",
                step_index=0,
                family=family,
                include_geometry=include_geometry,
                include_mass=include_mass,
                include_basin=include_basin,
            ),
            _checkpoint(
                checkpoint_id="c1",
                step_index=1,
                family=family,
                include_geometry=include_geometry,
                include_mass=include_mass,
                include_basin=include_basin,
            ),
            _checkpoint(
                checkpoint_id="c2",
                step_index=2,
                family=family,
                include_geometry=include_geometry,
                include_mass=include_mass,
                include_basin=include_basin,
            ),
        ),
    )
    return build_landscape_inference_evidence_substrate(load_result), load_result


def _authored_seed() -> LandscapeSeed:
    return LandscapeSeed(
        seed_schema="pygrc.landscape_seed",
        seed_version="0.1",
        meta=SeedDocumentMeta(name="authored", source_kind="test"),
        constitutive_profile=SeedConstitutiveProfile(
            lambda_c=1.0,
            xi_c=1.0,
            zeta_c=0.0,
            kappa_c=0.0,
            dt=0.1,
            potential=SeedPotential(type="test", params={}),
        ),
        primitives=[
            BasinSeedPrimitive(id="observed_basin_1", role="identity_basin", depth_hint=0),
            BasinSeedPrimitive(id="authored_missing", role="identity_basin", depth_hint=0),
        ],
    )


class LandscapeInferenceBasinTest(unittest.TestCase):
    def test_grcv3_full_geometric_basin_uses_checkpoint_mass(self) -> None:
        substrate, _ = _substrate(family="grcv3", include_geometry=True, include_mass=True)

        candidates = classify_landscape_basin_candidates(substrate, runtime_family="grcv3")

        self.assertEqual(1, len(candidates))
        candidate = candidates[0]
        self.assertEqual("1", candidate.basin_id)
        self.assertEqual("full_geometric_basin", candidate.evidence_mode)
        self.assertEqual("full_geometric", candidate.capability_level)
        self.assertEqual("identity_basin", candidate.role)
        self.assertEqual(4.5, candidate.basin_mass)
        self.assertEqual("checkpoint_basin_mass", candidate.basin_mass_source)
        self.assertIn("graph_checkpoints.node_records.gradient_norm", candidate.evidence_fields)
        self.assertEqual(("c0", "c1", "c2"), candidate.checkpoint_ids)

    def test_grc9_topology_only_basin_does_not_overclaim_geometry(self) -> None:
        substrate, _ = _substrate(
            family="grc9",
            include_geometry=False,
            include_mass=False,
        )

        candidates = classify_landscape_basin_candidates(substrate, runtime_family="grc9")

        self.assertEqual(1, len(candidates))
        candidate = candidates[0]
        self.assertEqual("topology_mechanical_basin", candidate.evidence_mode)
        self.assertEqual("topology_mechanical", candidate.capability_level)
        self.assertNotIn("graph_checkpoints.node_records.gradient_norm", candidate.evidence_fields)
        self.assertEqual("coherence_mass_fallback", candidate.basin_mass_source)

    def test_grc9v3_geometric_basin_records_mass_proxy_when_basin_mass_missing(self) -> None:
        substrate, _ = _substrate(
            family="grc9v3",
            include_geometry=True,
            include_mass=False,
        )

        candidates = classify_landscape_basin_candidates(substrate, runtime_family="grc9v3")

        self.assertEqual(1, len(candidates))
        candidate = candidates[0]
        self.assertEqual("geometric_basin_mass_proxy", candidate.evidence_mode)
        self.assertEqual("geometric_mass_proxy", candidate.capability_level)
        self.assertEqual(3.25, candidate.basin_mass)
        self.assertEqual("coherence_mass_fallback", candidate.basin_mass_source)
        self.assertIn("graph_checkpoints.node_records.coherence", candidate.evidence_fields)

    def test_basin_seed_emission_validates_and_records_authored_relationships(self) -> None:
        substrate, load_result = _substrate(family="grc9v3")

        seed = infer_landscape_basin_seed(
            load_result,
            substrate=substrate,
            authored_seed=_authored_seed(),
        )

        validate_landscape_seed(seed)
        validate_landscape_inference_seed_extensions(seed)
        self.assertEqual(1, len(seed.primitives))
        primitive = seed.primitives[0]
        self.assertEqual("observed_basin_1", primitive.id)
        self.assertEqual("identity_basin", primitive.role)
        self.assertEqual("basin", primitive.type)
        self.assertEqual(4.5, primitive.coherence_prior)
        self.assertIn("landscape_inference", primitive.extensions)
        self.assertIn("landscape_inference_basin", primitive.extensions)
        inference = primitive.extensions["landscape_inference"]
        self.assertEqual("observed", inference["authority"])
        self.assertEqual("preserved", inference["relationship_to_authored"])
        self.assertEqual("observed_basin_1", inference["matched_authored_primitive_id"])

        summary = seed.extensions["landscape_inference_basin_summary"]
        self.assertEqual(["observed_basin_1"], summary["preserved_authored_basin_ids"])
        self.assertEqual([], summary["emerged_observed_basin_ids"])
        self.assertEqual(["authored_missing"], summary["dissolved_authored_basin_ids"])

    def test_basin_seed_emission_marks_unmatched_observations_as_emerged(self) -> None:
        substrate, load_result = _substrate(family="grc9v3")

        seed = infer_landscape_basin_seed(load_result, substrate=substrate)

        primitive = seed.primitives[0]
        self.assertEqual("emerged", primitive.extensions["landscape_inference"]["relationship_to_authored"])
        summary = seed.extensions["landscape_inference_basin_summary"]
        self.assertEqual(["observed_basin_1"], summary["emerged_observed_basin_ids"])
        self.assertEqual([], summary["dissolved_authored_basin_ids"])

    def test_no_basin_evidence_returns_no_candidates(self) -> None:
        substrate, load_result = _substrate(
            family="grc9v3",
            include_geometry=True,
            include_mass=False,
            include_basin=False,
        )

        candidates = classify_landscape_basin_candidates(substrate, runtime_family="grc9v3")
        seed = infer_landscape_basin_seed(load_result, substrate=substrate)

        self.assertEqual((), candidates)
        self.assertEqual([], seed.primitives)
        self.assertEqual(0, seed.extensions["landscape_inference_basin_summary"]["observed_basin_count"])


if __name__ == "__main__":
    unittest.main()

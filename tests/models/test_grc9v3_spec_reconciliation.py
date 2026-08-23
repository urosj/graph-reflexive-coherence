from __future__ import annotations

import hashlib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = REPO_ROOT / "specs/grc-9-v3-spec.md"
PROFILE_PATH = REPO_ROOT / "specs/grc-9-v3-evidence-profile.md"

FROZEN_INPUTS = {
    "src/pygrc/models/grc_9_v3.py": (
        "d297def1eddfaf79a7ad3d6b676caaeebb29e6d7235f4fac5c6729bd7e26ca9e"
    ),
    "src/pygrc/models/grc_9_v3_runtime.py": (
        "f6f12de4e9bf66cd97b4063854ea225ae00874fed7073d4e72775891db54f502"
    ),
    "src/pygrc/models/grc_9_v3_state.py": (
        "4ab5ffcb95d69a0767b24d6c95277ba3619a5d477c4865cc0d31735a2377918e"
    ),
    "src/pygrc/models/grc_9_v3_sparks.py": (
        "fa1db78355e1dba41245da44c9c515ac09820035ca451723873da779420ee820"
    ),
    "src/pygrc/models/grc_9_v3_choice.py": (
        "ab8be0391a37e71d4610022afe3f64dac6102b929ade4448a59e7f4e02167933"
    ),
    "implementation/Phase-7-ImplementationPlan.md": (
        "6d9d215757405e4be19f67cde844af3ac9297389ce730e8a44f9c7b6844067b3"
    ),
    "implementation/Phase-7-EquationMap.md": (
        "94461cdf43f9fb4bc7bb0996822ea4e6130f7256ac1a041594eea99656c3555c"
    ),
    "implementation/Phase-7-StepLoop.md": (
        "a5d52562e771317b9d669ef62cd337ac98bba8dfd21f7cd521e9ae7c04ad17fb"
    ),
    "implementation/Phase-7-ImplementationChecklist.md": (
        "a01305300a785e08feb32b33846454dcbd5709ab655d5fd5332dd409adc8d30a"
    ),
    "implementation/Phase-7-MidGate-Review.md": (
        "99e69b09c1538ff2c96a236460bf8e42faf238dcbd69dda7fbdbdd9dc33cf6b0"
    ),
    "implementation/Phase-7-RepresentativeRuntime.md": (
        "51aec1f3b3b512f47634b49f9608ee3a044a21d8c0996ad44dbe0103a915a9f0"
    ),
    "implementation/Phase-7-Closeout.md": (
        "677f4b4689fed54c6c0842481e3d4d61142a23db0148b2c5b3fe11d99cc59d5c"
    ),
    (
        "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
        "outputs/gates/grv8_closeout_acceptance_anchor.json"
    ): "239417d959f92bb3b32f2506b35fc279d8193722e46b8517001d3d29fa272da3",
    (
        "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
        "outputs/fixed_branch_registry.json"
    ): "56bd1857f892f187c6b99d6fcbd419ddd68ae0e17133b3a0bf7dda79b197e366",
    (
        "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
        "outputs/complete_step_jacobians.json"
    ): "e4de4b9351ef7258baa88e7b675e8ce82f39ffe9db3ce9df395713e4f610c5ec",
    (
        "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
        "outputs/conductance_retention_probe.json"
    ): "bba1472177a2f182359ad9bc1ade634cd388f55088428fd030e6e32e74ed5766",
    (
        "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
        "outputs/return_orbit_registry.json"
    ): "f9af1524153d31ee2528f2d275b8274d5f65ca4a0c438ce3d15540e9d1c68e9e",
    (
        "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
        "outputs/final_causal_role_classification.json"
    ): "18a881f6d2a13f28dc59246c47ad07c208faa56cf03ebe6134bd868253f2c3e0",
    (
        "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/"
        "outputs/final_claim_classification.json"
    ): "f85d474daef7db7597f99d0d4afea2e242b4ca66b08a95b830496ae802f57d38",
    (
        "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
        "outputs/gates/b2_closeout_acceptance_anchor.json"
    ): "2a4b6b3220eae0fe0b3e3e4a698d47ab893841a3be15bafea0bf3755cac1143c",
    (
        "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
        "outputs/b2_i8_empty_path_audit.json"
    ): "7caa0369b90f83d57495798fbbdff1d6051b45fe3588b13244c8b8101681dd74",
    (
        "experiments/2026-08-B2-GR-grc9v3-retention-mediation-constructibility/"
        "outputs/b2_i8_classification_and_handoff.json"
    ): "138ee93667181f0a73012636ad90ee2919f0999d1c47a75d0e800079035af370",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_reconciliation_inputs_match_frozen_source_identity() -> None:
    profile = PROFILE_PATH.read_text(encoding="utf-8")
    for relative_path, expected_sha256 in FROZEN_INPUTS.items():
        source_path = REPO_ROOT / relative_path
        assert source_path.is_file(), relative_path
        assert sha256_file(source_path) == expected_sha256, relative_path
        assert relative_path in profile
        assert expected_sha256 in profile


def test_normative_spec_separates_state_storage_from_causal_coordinates() -> None:
    spec = SPEC_PATH.read_text(encoding="utf-8")
    required_markers = (
        "## Complete-Step Causal-State Semantics",
        "## Historical Persistence, Retention, And Read-Back",
        "Serialization of a field does not by itself make that field an independent",
        "`coherence` (`C`) is the admitted independent complete-step",
        "Baseline `GRC9V3` specifies the first relation.",
        "constitutive retained-sector projector",
        "Analysis-only projectors or observer surfaces do not by themselves define",
        "It does not assert retained memory, adaptive learning, agentic",
        "must use a revision-distinct specification",
    )
    for marker in required_markers:
        assert marker in spec

    # Bounded experiment accounting belongs in the evidence profile, not the spec.
    for bounded_count in ("9,648", "1,705", "7,915", "26 of 48"):
        assert bounded_count not in spec


def test_native_step_order_matches_reconciled_profile() -> None:
    source = (REPO_ROOT / "src/pygrc/models/grc_9_v3.py").read_text(
        encoding="utf-8"
    )
    step_start = source.index("    def step(self) -> StepResult:")
    step_end = source.index("    def reset(self) -> None:", step_start)
    step_source = source[step_start:step_end]
    ordered_calls = (
        "self.rebuild_differential_state()",
        "self.rebuild_transport_state()",
        "self.rebuild_differential_state()",
        "self.rebuild_identity_state()",
        "self._apply_hybrid_spark_stages(trace)",
        "self.rebuild_choice_state()",
        "self.apply_growth()",
        "self.apply_boundary_behavior()",
        "self.apply_continuity()",
        "self.enforce_quadrature_budget()",
        "self.rebuild_differential_state()",
        "self.rebuild_transport_state()",
        "self.rebuild_differential_state()",
        "self.rebuild_identity_state()",
        "self.refresh_coarse_cache()",
        "self.compute_observables()",
    )
    cursor = 0
    for call in ordered_calls:
        next_cursor = step_source.find(call, cursor)
        assert next_cursor >= cursor, call
        cursor = next_cursor + len(call)


def test_current_write_is_sign_even_and_fresh_flux_is_potential_derived() -> None:
    runtime = (REPO_ROOT / "src/pygrc/models/grc_9_v3_runtime.py").read_text(
        encoding="utf-8"
    )
    assert "- gamma * (port_edge.flux_uv**2) / 2.0" in runtime
    assert "flux_uv = -eta * conductance * (potential_u - potential_v)" in runtime


def test_evidence_profile_keeps_bounded_claims_and_extension_open() -> None:
    profile = PROFILE_PATH.read_text(encoding="utf-8")
    required_boundaries = (
        "No resolved native carrier-formation signal was found in the accessible",
        "It is not a global nonexistence theorem.",
        "27 resolved clean no-driver baseline controls",
        "identifies 12 locally absent",
        "`GRR3`, `GRR4`, and `GRR5` were not testable",
        "that one particular GRC9V4 mechanism is selected",
        "a bounded environment exception for B2 closeout only",
    )
    for boundary in required_boundaries:
        assert boundary in profile


def test_spec_indexes_expose_the_evidence_profile() -> None:
    specs_index = (REPO_ROOT / "specs/README.md").read_text(encoding="utf-8")
    project_index = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "grc-9-v3-evidence-profile.md" in specs_index
    assert "specs/grc-9-v3-evidence-profile.md" in project_index

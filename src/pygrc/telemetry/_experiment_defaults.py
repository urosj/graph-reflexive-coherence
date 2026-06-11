"""Private default values for telemetry experiment helpers."""

from __future__ import annotations

from pathlib import Path

from pygrc.models import DEFAULT_GRCV3_LANDSCAPE_PROFILE


DEFAULT_CELL1_SEED = Path("configs/landscapes/seed/cell-1.seed.yaml")
DEFAULT_CELL4_SEED = Path("configs/landscapes/seed/cell-4.seed.yaml")
DEFAULT_REPRESENTATIVE_FAMILY = "balanced_baseline"
DEFAULT_REPRESENTATIVE_STEPS = 3
DEFAULT_REPRESENTATIVE_RNG_SEED = 7
DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH = Path("representative") / "grcv2"
DEFAULT_GRC9_REPRESENTATIVE_EXPERIMENT_PATH = Path("representative") / "grc9"
DEFAULT_GRC9_REPRESENTATIVE_LANE = "phase6_mechanical_baseline"
DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE = "phase_t_grc9_iter6_representative"
DEFAULT_GRC9_DIAGNOSTIC_PROBE_NAME = "phase_t_grc9_iter9_diagnostic_probe"
DEFAULT_GRC9_REPRESENTATIVE_STEPS = 4
DEFAULT_GRC9_REPRESENTATIVE_SOURCE_REFERENCE = (
    "implementation/Phase-6-StepLoop.md"
)
DEFAULT_GRC9_LANDSCAPE_EXPERIMENT_PATH = Path("representative") / "grc9_landscape"
DEFAULT_GRC9_LANDSCAPE_PROFILE = "phase6_seed_baseline"
DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE = "phase_t_grc9_iter7_seed"
DEFAULT_GRC9_LANDSCAPE_STEPS = 3
DEFAULT_GRC9_LANDSCAPE_SOURCE_REFERENCE = "implementation/Phase-6-Closeout.md"
DEFAULT_GRCV3_REPRESENTATIVE_EXPERIMENT_PATH = Path("representative") / "grcv3"
DEFAULT_GRCV3_REPRESENTATIVE_LANE = "phase5_reference"
DEFAULT_GRCV3_REPRESENTATIVE_STEPS = 3
DEFAULT_GRCV3_REPRESENTATIVE_SOURCE_REFERENCE = (
    "implementation/Phase-5-RepresentativeRuntime.md"
)
DEFAULT_GRCV3_LANDSCAPE_EXPERIMENT_PATH = Path("representative") / "grcv3_landscape"
DEFAULT_GRCV3_LANDSCAPE_STEPS = 3
DEFAULT_GRCV3_PATH_FAILURE_TRACE_BASELINE_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-transfer-mediation-probe.seed.yaml"
)
DEFAULT_GRCV3_PATH_FAILURE_TRACE_COMPARISON_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-single-intermediate-probe.seed.yaml"
)
DEFAULT_GRCV3_PATH_FAILURE_TRACE_STEPS = 6
DEFAULT_GRCV3_CANDIDATE_TRANSITION_BASELINE_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml"
)
DEFAULT_GRCV3_CANDIDATE_TRANSITION_COMPARISON_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-center-coupling-single-intermediate-probe.seed.yaml"
)
DEFAULT_GRCV3_CANDIDATE_TRANSITION_STEPS = 12
DEFAULT_GRCV3_SETTLEMENT_LOCUS_BASELINE_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-mediated-spill-branch-probe.seed.yaml"
)
DEFAULT_GRCV3_SETTLEMENT_LOCUS_COMPARISON_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-mediated-spill-branch-single-intermediate-probe.seed.yaml"
)
DEFAULT_GRCV3_SETTLEMENT_LOCUS_STEPS = 12
DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-path-node-split-child-inheriting-settlement-probe.seed.yaml"
)
DEFAULT_GRCV3_SETTLEMENT_REENTRY_COMPARISON_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-carrier-site-split-child-inheriting-settlement-probe.seed.yaml"
)
DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS = 12
DEFAULT_GRCV3_COLLAPSE_TRACE_DIRECT_SEED = DEFAULT_GRCV3_SETTLEMENT_LOCUS_BASELINE_SEED
DEFAULT_GRCV3_COLLAPSE_TRACE_PATH_SEED = DEFAULT_GRCV3_SETTLEMENT_LOCUS_COMPARISON_SEED
DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_PATH_SEED = DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED
DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_DIRECT_SEED = DEFAULT_GRCV3_SETTLEMENT_REENTRY_COMPARISON_SEED
DEFAULT_GRCV3_COLLAPSE_TRACE_STEPS = 24
DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE = 0.15
DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE = 0.14
DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_BASELINE_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-collapse-example.seed.yaml"
)
DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_COMPARISON_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-basin-boundary-channel-probe.seed.yaml"
)
DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BASELINE_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-transfer-mediation-probe.seed.yaml"
)
DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BLOCKED_CONTROL_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-center-coupling-probe.seed.yaml"
)
DEFAULT_GRCV3_POST_SPARK_COLLAPSE_REFINED_CONTROL_SEED = (
    Path("configs")
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml"
)
DEFAULT_GRCV3_POST_SPARK_COLLAPSE_STEPS = 120
DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_STEPS = 150
DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_START_STEP = 100
DEFAULT_GRCV3_BROAD_COLLAPSE_SURVEY_LANES = (
    {
        "lane_name": "collapse_example",
        "seed_path": Path("configs")
        / "landscapes"
        / "seed"
        / "grcv3-rich-collapse-example.seed.yaml",
        "profile_name": "hot_exploratory",
        "primitive_id": "decision_core",
        "num_steps": 10,
    },
    {
        "lane_name": "transfer_mediation_artifact_lane",
        "seed_path": Path("configs")
        / "landscapes"
        / "seed"
        / "grcv3-rich-v4-transfer-mediation-probe.seed.yaml",
        "profile_name": DEFAULT_GRCV3_LANDSCAPE_PROFILE,
        "primitive_id": "spindle_core",
        "num_steps": 160,
    },
    {
        "lane_name": "basin_boundary_channel_fulltest_lane",
        "seed_path": Path("configs")
        / "landscapes"
        / "seed"
        / "grcv3-rich-basin-boundary-channel-probe.seed.yaml",
        "profile_name": DEFAULT_GRCV3_LANDSCAPE_PROFILE,
        "primitive_id": "core_basin",
        "num_steps": 160,
    },
)


__all__ = [
    "DEFAULT_CELL1_SEED",
    "DEFAULT_CELL4_SEED",
    "DEFAULT_GRC9_REPRESENTATIVE_EXPERIMENT_PATH",
    "DEFAULT_GRC9_DIAGNOSTIC_PROBE_NAME",
    "DEFAULT_GRC9_PHASE_T_REPRESENTATIVE_LANE",
    "DEFAULT_GRC9_LANDSCAPE_EXPERIMENT_PATH",
    "DEFAULT_GRC9_LANDSCAPE_PROFILE",
    "DEFAULT_GRC9_PHASE_T_LANDSCAPE_PROFILE",
    "DEFAULT_GRC9_LANDSCAPE_SOURCE_REFERENCE",
    "DEFAULT_GRC9_LANDSCAPE_STEPS",
    "DEFAULT_GRC9_REPRESENTATIVE_LANE",
    "DEFAULT_GRC9_REPRESENTATIVE_SOURCE_REFERENCE",
    "DEFAULT_GRC9_REPRESENTATIVE_STEPS",
    "DEFAULT_REPRESENTATIVE_FAMILY",
    "DEFAULT_REPRESENTATIVE_STEPS",
    "DEFAULT_REPRESENTATIVE_RNG_SEED",
    "DEFAULT_REPRESENTATIVE_EXPERIMENT_PATH",
    "DEFAULT_GRCV3_REPRESENTATIVE_EXPERIMENT_PATH",
    "DEFAULT_GRCV3_REPRESENTATIVE_LANE",
    "DEFAULT_GRCV3_REPRESENTATIVE_STEPS",
    "DEFAULT_GRCV3_REPRESENTATIVE_SOURCE_REFERENCE",
    "DEFAULT_GRCV3_LANDSCAPE_EXPERIMENT_PATH",
    "DEFAULT_GRCV3_LANDSCAPE_STEPS",
    "DEFAULT_GRCV3_PATH_FAILURE_TRACE_BASELINE_SEED",
    "DEFAULT_GRCV3_PATH_FAILURE_TRACE_COMPARISON_SEED",
    "DEFAULT_GRCV3_PATH_FAILURE_TRACE_STEPS",
    "DEFAULT_GRCV3_CANDIDATE_TRANSITION_BASELINE_SEED",
    "DEFAULT_GRCV3_CANDIDATE_TRANSITION_COMPARISON_SEED",
    "DEFAULT_GRCV3_CANDIDATE_TRANSITION_STEPS",
    "DEFAULT_GRCV3_SETTLEMENT_LOCUS_BASELINE_SEED",
    "DEFAULT_GRCV3_SETTLEMENT_LOCUS_COMPARISON_SEED",
    "DEFAULT_GRCV3_SETTLEMENT_LOCUS_STEPS",
    "DEFAULT_GRCV3_SETTLEMENT_REENTRY_BASELINE_SEED",
    "DEFAULT_GRCV3_SETTLEMENT_REENTRY_COMPARISON_SEED",
    "DEFAULT_GRCV3_SETTLEMENT_REENTRY_STEPS",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_DIRECT_SEED",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_PATH_SEED",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_PATH_SEED",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_SPLIT_DIRECT_SEED",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_STEPS",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_CHOICE",
    "DEFAULT_GRCV3_COLLAPSE_TRACE_EPSILON_COLLAPSE",
    "DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_BASELINE_SEED",
    "DEFAULT_GRCV3_PRE_SPARK_COLLAPSE_COMPARISON_SEED",
    "DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BASELINE_SEED",
    "DEFAULT_GRCV3_POST_SPARK_COLLAPSE_BLOCKED_CONTROL_SEED",
    "DEFAULT_GRCV3_POST_SPARK_COLLAPSE_REFINED_CONTROL_SEED",
    "DEFAULT_GRCV3_POST_SPARK_COLLAPSE_STEPS",
    "DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_STEPS",
    "DEFAULT_GRCV3_POST_SPARK_LATE_WINDOW_START_STEP",
    "DEFAULT_GRCV3_BROAD_COLLAPSE_SURVEY_LANES",
]

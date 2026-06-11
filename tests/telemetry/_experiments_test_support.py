"""Shared script and seed support for telemetry experiment tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[2]
GRCV3_REPRESENTATIVE_SCRIPT = (
    REPO_ROOT / "scripts" / "run_grcv3_representative_telemetry.py"
)
GRCV3_LANDSCAPE_SCRIPT = REPO_ROOT / "scripts" / "run_grcv3_landscape_telemetry.py"
GRCV3_PATH_FAILURE_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_path_intermediacy_failure.py"
)
GRCV3_CANDIDATE_TRANSITION_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_candidate_transition_failure.py"
)
GRCV3_SETTLEMENT_LOCUS_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_settlement_locus_regimes.py"
)
GRCV3_SETTLEMENT_REENTRY_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_settlement_reentry_boundary.py"
)
GRCV3_SETTLEMENT_REENTRY_NEIGHBORHOOD_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_settlement_reentry_neighborhood_boundary.py"
)
GRCV3_SETTLEMENT_REENTRY_SUPPORT_ISOLATION_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_settlement_reentry_support_isolation.py"
)
GRCV3_SETTLEMENT_REENTRY_SECONDARY_SUPPORT_COUNTERFACTUAL_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_settlement_reentry_secondary_support_counterfactual.py"
)
GRCV3_SECONDARY_SUPPORT_AUTHORABILITY_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_secondary_support_authorability.py"
)
GRCV3_COLLAPSE_REGIME_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_collapse_regimes.py"
)
GRCV3_BROAD_COLLAPSE_SURVEY_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_broad_collapse_survey.py"
)
GRCV3_PRE_SPARK_COLLAPSE_DECOMPOSITION_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_pre_spark_collapse_decomposition.py"
)
GRCV3_POST_SPARK_COLLAPSE_BOUNDARY_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_post_spark_collapse_boundary.py"
)
GRCV3_POST_SPARK_LATE_WINDOW_STABILITY_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_post_spark_late_window_stability.py"
)
GRCV3_POST_SPARK_DELAY_AUTHORABILITY_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_post_spark_delay_authorability.py"
)
GRCV3_POST_COLLAPSE_GEOMETRY_EXCLUSION_TRACE_SCRIPT = (
    REPO_ROOT / "scripts" / "trace_grcv3_post_collapse_geometry_exclusion.py"
)
RICH_V3_WEAK_TO_STABLE_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v3-load-carrier-weak-to-stable-probe.seed.yaml"
)
RICH_V4_TRANSFER_MEDIATION_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-transfer-mediation-probe.seed.yaml"
)
RICH_V4_CENTER_COUPLING_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-center-coupling-probe.seed.yaml"
)
RICH_V4_SINGLE_INTERMEDIATE_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-single-intermediate-probe.seed.yaml"
)
RICH_V4_OPEN_CENTER_CONTROL_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-open-center-control-probe.seed.yaml"
)
RICH_V4_OPEN_CENTER_SINGLE_INTERMEDIATE_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-open-center-single-intermediate-probe.seed.yaml"
)
RICH_V4_ASYMMETRIC_CENTER_COUPLING_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-center-coupling-probe.seed.yaml"
)
RICH_V4_ASYMMETRIC_CENTER_COUPLING_SINGLE_INTERMEDIATE_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-center-coupling-single-intermediate-probe.seed.yaml"
)
RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-pair-mediation-probe.seed.yaml"
)
RICH_V4_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-asymmetric-pair-mediation-single-intermediate-probe.seed.yaml"
)
RICH_V4_MEDIATED_SPILL_BRANCH_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-mediated-spill-branch-probe.seed.yaml"
)
RICH_V4_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-mediated-spill-branch-single-intermediate-probe.seed.yaml"
)
RICH_V4_CARRIER_SITE_SETTLEMENT_REGIME_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-carrier-site-settlement-regime-probe.seed.yaml"
)
RICH_V4_CARRIER_SITE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-carrier-site-split-child-inheriting-settlement-probe.seed.yaml"
)
RICH_V4_PATH_NODE_SETTLEMENT_REGIME_SINGLE_INTERMEDIATE_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-path-node-settlement-regime-single-intermediate-probe.seed.yaml"
)
RICH_V4_PATH_NODE_SPLIT_CHILD_INHERITING_SETTLEMENT_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-path-node-split-child-inheriting-settlement-probe.seed.yaml"
)
RICH_V4_PATH_NODE_ANCHORED_SETTLEMENT_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-path-node-anchored-settlement-probe.seed.yaml"
)
RICH_V4_MEDIATED_SPILL_BRANCH_FAN_IN_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-mediated-spill-branch-fan-in-probe.seed.yaml"
)
RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-role-locked-asymmetric-pair-mediation-probe.seed.yaml"
)
RICH_V4_ROLE_LOCKED_ASYMMETRIC_PAIR_MEDIATION_SINGLE_INTERMEDIATE_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-role-locked-asymmetric-pair-mediation-single-intermediate-probe.seed.yaml"
)
RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-role-locked-mediated-spill-branch-probe.seed.yaml"
)
RICH_V4_ROLE_LOCKED_MEDIATED_SPILL_BRANCH_SINGLE_INTERMEDIATE_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-v4-role-locked-mediated-spill-branch-single-intermediate-probe.seed.yaml"
)
RICH_COLLAPSE_EXAMPLE_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-collapse-example.seed.yaml"
)
RICH_BASIN_BOUNDARY_CHANNEL_SEED = (
    REPO_ROOT
    / "configs"
    / "landscapes"
    / "seed"
    / "grcv3-rich-basin-boundary-channel-probe.seed.yaml"
)


def _load_script_module(module_name: str, script_path: Path, error_message: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(error_message)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_grcv3_representative_script_module() -> ModuleType:
    return _load_script_module(
        "run_grcv3_representative_telemetry_script",
        GRCV3_REPRESENTATIVE_SCRIPT,
        "failed to load GRCV3 representative telemetry script",
    )


def _load_grcv3_candidate_transition_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_candidate_transition_failure_script",
        GRCV3_CANDIDATE_TRANSITION_TRACE_SCRIPT,
        "failed to load GRCV3 candidate transition trace script",
    )


def _load_grcv3_collapse_regime_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_collapse_regimes_script",
        GRCV3_COLLAPSE_REGIME_TRACE_SCRIPT,
        "failed to load GRCV3 collapse regime trace script",
    )


def _load_grcv3_broad_collapse_survey_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_broad_collapse_survey_script",
        GRCV3_BROAD_COLLAPSE_SURVEY_SCRIPT,
        "failed to load GRCV3 broad collapse survey script",
    )


def _load_grcv3_pre_spark_collapse_decomposition_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_pre_spark_collapse_decomposition_script",
        GRCV3_PRE_SPARK_COLLAPSE_DECOMPOSITION_TRACE_SCRIPT,
        "failed to load GRCV3 pre-spark collapse decomposition trace script",
    )


def _load_grcv3_post_spark_collapse_boundary_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_post_spark_collapse_boundary_script",
        GRCV3_POST_SPARK_COLLAPSE_BOUNDARY_TRACE_SCRIPT,
        "failed to load GRCV3 post-spark collapse boundary trace script",
    )


def _load_grcv3_post_spark_late_window_stability_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_post_spark_late_window_stability_script",
        GRCV3_POST_SPARK_LATE_WINDOW_STABILITY_TRACE_SCRIPT,
        "failed to load GRCV3 post-spark late-window stability trace script",
    )


def _load_grcv3_post_spark_delay_authorability_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_post_spark_delay_authorability_script",
        GRCV3_POST_SPARK_DELAY_AUTHORABILITY_TRACE_SCRIPT,
        "failed to load GRCV3 post-spark delay authorability trace script",
    )


def _load_grcv3_post_collapse_geometry_exclusion_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_post_collapse_geometry_exclusion_script",
        GRCV3_POST_COLLAPSE_GEOMETRY_EXCLUSION_TRACE_SCRIPT,
        "failed to load GRCV3 post-collapse geometry exclusion trace script",
    )


def _load_grcv3_settlement_locus_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_settlement_locus_regimes_script",
        GRCV3_SETTLEMENT_LOCUS_TRACE_SCRIPT,
        "failed to load GRCV3 settlement locus trace script",
    )


def _load_grcv3_settlement_reentry_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_settlement_reentry_boundary_script",
        GRCV3_SETTLEMENT_REENTRY_TRACE_SCRIPT,
        "failed to load GRCV3 settlement reentry trace script",
    )


def _load_grcv3_settlement_reentry_neighborhood_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_settlement_reentry_neighborhood_boundary_script",
        GRCV3_SETTLEMENT_REENTRY_NEIGHBORHOOD_TRACE_SCRIPT,
        "failed to load GRCV3 settlement reentry neighborhood trace script",
    )


def _load_grcv3_settlement_reentry_support_isolation_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_settlement_reentry_support_isolation_script",
        GRCV3_SETTLEMENT_REENTRY_SUPPORT_ISOLATION_TRACE_SCRIPT,
        "failed to load GRCV3 settlement reentry support isolation trace script",
    )


def _load_grcv3_settlement_reentry_secondary_support_counterfactual_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_settlement_reentry_secondary_support_counterfactual_script",
        GRCV3_SETTLEMENT_REENTRY_SECONDARY_SUPPORT_COUNTERFACTUAL_TRACE_SCRIPT,
        "failed to load GRCV3 settlement reentry secondary-support counterfactual script",
    )


def _load_grcv3_secondary_support_authorability_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_secondary_support_authorability_script",
        GRCV3_SECONDARY_SUPPORT_AUTHORABILITY_TRACE_SCRIPT,
        "failed to load GRCV3 secondary support authorability trace script",
    )


def _load_grcv3_landscape_script_module() -> ModuleType:
    return _load_script_module(
        "run_grcv3_landscape_telemetry_script",
        GRCV3_LANDSCAPE_SCRIPT,
        "failed to load GRCV3 landscape telemetry script",
    )


def _load_grcv3_path_failure_trace_script_module() -> ModuleType:
    return _load_script_module(
        "trace_grcv3_path_intermediacy_failure_script",
        GRCV3_PATH_FAILURE_TRACE_SCRIPT,
        "failed to load GRCV3 path failure trace script",
    )

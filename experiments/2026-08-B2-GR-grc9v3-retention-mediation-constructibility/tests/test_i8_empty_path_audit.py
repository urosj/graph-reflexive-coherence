from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from b2_artifact_io import assert_envelope_digest, read_json  # noqa: E402
from build_i8_empty_path_audit import (  # noqa: E402
    CONFIG_PATH,
    OUTPUT_PATH,
    attribution_class,
)


def test_attribution_split_uses_frozen_i4_thresholds() -> None:
    policy = read_json(CONFIG_PATH)["attribution_split"]
    assert attribution_class(0.0, policy) == (
        "apparent_carrier_authored_within_numerical_uncertainty"
    )
    assert attribution_class(1e-12, policy) == (
        "apparent_carrier_authored_within_numerical_uncertainty"
    )
    assert attribution_class(1.0001e-12, policy) == (
        "runtime_residual_above_uncertainty_below_separation_floor"
    )
    assert attribution_class(1e-10, policy) == (
        "runtime_residual_above_uncertainty_below_separation_floor"
    )
    assert attribution_class(1.0001e-10, policy) == (
        "runtime_residual_above_separation_below_formation_floor"
    )
    assert attribution_class(1e-9, policy) == (
        "runtime_residual_above_separation_below_formation_floor"
    )


def test_attribution_split_rejects_a_positive_residual() -> None:
    policy = read_json(CONFIG_PATH)["attribution_split"]
    try:
        attribution_class(1.0001e-9, policy)
    except ValueError as error:
        assert "above the formation floor" in str(error)
    else:
        raise AssertionError("positive residual must not enter the merged negative split")


def test_audit_contract_cannot_reopen_i4_or_assign_a_rung() -> None:
    contract = read_json(CONFIG_PATH)
    assert contract["candidate_set_reopening_allowed"] is False
    assert contract["retention_or_mediation_adjudication_allowed"] is False
    assert contract["full_attempt_rows_retained"] is False
    assert contract["runtime_change_authorized"] is False


def test_generated_audit_is_bounded_when_present() -> None:
    if not OUTPUT_PATH.exists():
        return
    artifact = read_json(OUTPUT_PATH)
    assert_envelope_digest(artifact)
    payload = artifact["payload"]
    assert payload["reconstruction_equivalence"]["attempt_count"] == 9648
    assert payload["reconstruction_equivalence"][
        "classification_matrix_matches_accepted_I4"
    ] is True
    assert sum(
        row["attempt_count"] for row in payload["formation_attribution_split"]
    ) == 1706
    assert payload["scientific_boundary"]["I4_candidate_set_reopened"] is False
    assert payload["scientific_boundary"]["full_attempt_rows_retained"] is False

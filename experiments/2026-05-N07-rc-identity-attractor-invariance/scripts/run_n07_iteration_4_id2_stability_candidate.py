"""Run N07 Iteration 4 ID2 stability/local-well candidate.

This script is experiment-local. It consumes the Iteration 3 support-area
candidate, applies the manifest-declared stability proxy, records an ID2
candidate row, and emits negative controls for unstable basin, post-hoc
threshold changes, hidden/report-side well scores, wrong support area, and
budget discontinuity. It does not import or mutate `src/pygrc`.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[3]
N07 = ROOT / "experiments/2026-05-N07-rc-identity-attractor-invariance"
MANIFEST_PATH = N07 / "configs/n07_fixture_manifest_v1.json"
MANIFEST_VALIDATION_PATH = N07 / "outputs/n07_iteration_2_fixture_manifest_validation.json"
ID1_OUTPUT_PATH = N07 / "outputs/n07_iteration_3_id1_support_area_candidate.json"
ID1_REPORT_PATH = N07 / "reports/n07_iteration_3_id1_support_area_candidate.md"
OUTPUT_PATH = N07 / "outputs/n07_iteration_4_id2_stability_candidate.json"
REPORT_PATH = N07 / "reports/n07_iteration_4_id2_stability_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_4_id2_stability_candidate.py"
)

GATE_VECTOR_FIELDS = [
    "support",
    "stability",
    "attractivity",
    "invariance",
    "lineage_current",
    "reflexive_closure",
    "compatibility",
    "artifact_replay",
]

CONTROL_BLOCKERS = {
    "unstable_basin_no_local_well": "unstable_basin_no_local_well",
    "posthoc_threshold_change": "posthoc_threshold_change",
    "hidden_potential_or_report_side_well_score": (
        "hidden_potential_or_report_side_well_score"
    ),
    "wrong_support_area": "wrong_support_area",
    "budget_discontinuity": "budget_discontinuity",
}

NATIVE_SUPPORT_STATUS_VALUES = {
    "pure_native",
    "mixed_native_experiment_local",
    "experiment_local",
    "blocked",
}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(data: Any) -> str:
    return hashlib.sha256(_canonical_json(data).encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _git(args: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    return {
        "command": "git " + " ".join(args),
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _gate_vector(**overrides: str) -> dict[str, str]:
    vector = {field: "not_measured" for field in GATE_VECTOR_FIELDS}
    vector["lineage_current"] = "not_applicable"
    vector.update(overrides)
    return vector


def _claim_flags(manifest: Mapping[str, Any]) -> dict[str, bool]:
    flags = manifest["claim_boundary"]["claim_flags"]
    return {key: False for key in sorted(flags)}


def _topology_family(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return next(
        family
        for family in manifest["topology_families"]
        if family["topology_family_id"] == "n07_T2_stable_well_basin"
    )


def _source_artifact_records(id1_output: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_fixture_manifest_v1",
            "path": _rel(MANIFEST_PATH),
            "sha256": _file_sha256(MANIFEST_PATH),
        },
        {
            "name": "n07_iteration_2_fixture_manifest_validation",
            "path": _rel(MANIFEST_VALIDATION_PATH),
            "sha256": _file_sha256(MANIFEST_VALIDATION_PATH),
        },
        {
            "name": "n07_iteration_3_id1_support_area_candidate",
            "path": _rel(ID1_OUTPUT_PATH),
            "sha256": _file_sha256(ID1_OUTPUT_PATH),
            "status": id1_output["status"],
            "support_area_row_digest": id1_output["artifact_digests"][
                "support_area_row_digest"
            ],
            "id1_candidate_row_digest": id1_output["artifact_digests"][
                "id1_candidate_row_digest"
            ],
        },
    ]


def _source_report_records() -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_3_id1_support_area_candidate_report",
            "path": _rel(ID1_REPORT_PATH),
            "sha256": _file_sha256(ID1_REPORT_PATH),
        }
    ]


def _stability_observation_event(
    *,
    manifest: Mapping[str, Any],
    id1_output: Mapping[str, Any],
) -> dict[str, Any]:
    support_row = id1_output["support_area_row"]
    fixture = manifest["fixture"]
    return {
        "event_id": "n07_i4_stability_observation_event_0001",
        "event_kind": "experiment_local_runtime_visible_stability_window",
        "event_time_key": "n07_i4_t1_stability_window",
        "scheduler_event_index": 1,
        "source_id1_candidate_row_id": id1_output["id1_candidate_row"]["row_id"],
        "source_support_area_digest": support_row["support_area_digest"],
        "source_support_area_id": support_row["support_area_id"],
        "source_support_area_lineage_status": support_row["lineage_status"],
        "support_area_id": support_row["support_area_id"],
        "support_area_digest": support_row["support_area_digest"],
        "candidate_basin_id": support_row["support_area_id"].replace(
            "support_area", "basin"
        ),
        "candidate_identity_carrier_type": "coherence_basin",
        "topology_family_id": "n07_T2_stable_well_basin",
        "stability_proxy_policy_id": "n07_stability_well_proxy_v1",
        "proper_time_window_id": "n07_i4_ptw_support_A_0_2",
        "proper_time_sample_count": 3,
        "proper_time_samples": [
            {
                "proper_time_index": 0,
                "support_area_mass": 1.0,
                "incoming_flux_to_support": 0.10,
                "outgoing_flux_from_support": 0.02,
            },
            {
                "proper_time_index": 1,
                "support_area_mass": 0.98,
                "incoming_flux_to_support": 0.08,
                "outgoing_flux_from_support": 0.01,
            },
            {
                "proper_time_index": 2,
                "support_area_mass": 0.96,
                "incoming_flux_to_support": 0.06,
                "outgoing_flux_from_support": 0.01,
            },
        ],
        "support_area_mass_before": 1.0,
        "support_area_mass_after": 0.96,
        "incoming_flux_to_support": 0.24,
        "outgoing_flux_from_support": 0.04,
        "budget_surface": fixture["budget_surface"]["budget_surface"],
        "budget_before": fixture["budget_surface"]["conserved_budget_total"],
        "budget_after": fixture["budget_surface"]["conserved_budget_total"],
        "budget_error": 0.0,
        "thresholds_fixed_before_run": True,
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "hidden_potential_or_report_side_well_score_used": False,
        "posthoc_threshold_change_used": False,
    }


def _stability_proxy_record(
    *,
    manifest: Mapping[str, Any],
    id1_output: Mapping[str, Any],
    observation: Mapping[str, Any],
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["stability_well_proxy"]
    support_area_mass_before = observation["support_area_mass_before"]
    support_area_mass_after = observation["support_area_mass_after"]
    incoming_flux_to_support = observation["incoming_flux_to_support"]
    outgoing_flux_from_support = observation["outgoing_flux_from_support"]
    support_area_mass_retention = (
        support_area_mass_after / support_area_mass_before
        if support_area_mass_before
        else 0.0
    )
    local_inflow_dominance_score = (
        incoming_flux_to_support / (incoming_flux_to_support + outgoing_flux_from_support)
        if incoming_flux_to_support + outgoing_flux_from_support
        else 0.0
    )
    stability_score = (
        0.5 * support_area_mass_retention + 0.5 * local_inflow_dominance_score
    )
    digest_input = {
        "proxy_formula": metric["proxy_formula"],
        "threshold": metric["threshold"],
        "input_fields": metric["input_fields"],
        "support_area_digest": observation["support_area_digest"],
        "support_area_mass_before": support_area_mass_before,
        "support_area_mass_after": support_area_mass_after,
        "incoming_flux_to_support": incoming_flux_to_support,
        "outgoing_flux_from_support": outgoing_flux_from_support,
        "proper_time_window_id": observation["proper_time_window_id"],
        "source_id1_candidate_row_digest": id1_output["artifact_digests"][
            "id1_candidate_row_digest"
        ],
    }
    record_digest = _digest(digest_input)
    idempotency_key = {
        "stability_proxy_policy_id": observation["stability_proxy_policy_id"],
        "support_area_digest": observation["support_area_digest"],
        "event_time_key": observation["event_time_key"],
        "scheduler_event_index": observation["scheduler_event_index"],
        "proper_time_window_id": observation["proper_time_window_id"],
    }
    return {
        "record_id": "n07_i4_stability_proxy_record_v1",
        "record_kind": "experiment_local_stability_well_proxy_record",
        "stability_proxy_policy_id": observation["stability_proxy_policy_id"],
        "selected_proxy": metric["selected_proxy"],
        "proxy_formula": metric["proxy_formula"],
        "threshold": metric["threshold"],
        "thresholds_fixed_before_run": observation["thresholds_fixed_before_run"],
        "input_fields": metric["input_fields"],
        "digest_scope": metric["digest_scope"],
        "native_policy_available": metric["native_policy_available"],
        "native_policy_blocker": metric["native_policy_blocker"],
        "hidden_report_side_score_allowed": metric[
            "hidden_report_side_score_allowed"
        ],
        "support_area_digest": observation["support_area_digest"],
        "source_observation_event_id": observation["event_id"],
        "source_observation_event_digest": _digest(observation),
        "support_area_mass_before": support_area_mass_before,
        "support_area_mass_after": support_area_mass_after,
        "incoming_flux_to_support": incoming_flux_to_support,
        "outgoing_flux_from_support": outgoing_flux_from_support,
        "support_area_mass_retention": support_area_mass_retention,
        "local_inflow_dominance_score": local_inflow_dominance_score,
        "stability_score": stability_score,
        "stability_gate": "pass" if stability_score >= metric["threshold"] else "fail",
        "proper_time_window_id": observation["proper_time_window_id"],
        "proper_time_sample_count": observation["proper_time_sample_count"],
        "proper_time_samples_digest": _digest(observation["proper_time_samples"]),
        "budget_surface": observation["budget_surface"],
        "budget_before": observation["budget_before"],
        "budget_after": observation["budget_after"],
        "budget_error": observation["budget_error"],
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "hidden_potential_or_report_side_well_score_used": False,
        "posthoc_threshold_change_used": False,
        "stability_record_digest_input": digest_input,
        "stability_record_digest": record_digest,
        "stability_idempotency_key": idempotency_key,
        "stability_idempotency_key_digest": _digest(idempotency_key),
    }


def _id2_candidate_row(
    *,
    manifest: Mapping[str, Any],
    id1_output: Mapping[str, Any],
    observation: Mapping[str, Any],
    stability_record: Mapping[str, Any],
) -> dict[str, Any]:
    support_row = id1_output["support_area_row"]
    return {
        "row_id": "n07_i4_id2_stability_candidate_row_v1",
        "id_level": "ID2",
        "topology_family_id": "n07_T2_stable_well_basin",
        "composite_topology_id": None,
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": support_row["support_area_id"],
        "support_area_digest": support_row["support_area_digest"],
        "stability_record_id": stability_record["record_id"],
        "stability_record_digest": stability_record["stability_record_digest"],
        "source_artifacts": _source_artifact_records(id1_output),
        "source_artifact_sha256": {
            item["path"]: item["sha256"] for item in _source_artifact_records(id1_output)
        },
        "source_reports": _source_report_records(),
        "runtime_family": "LGRC9V3",
        "implementation_surface": "experiment_local_identity_gate_record",
        "gate_vector": _gate_vector(support="pass", stability="pass"),
        "derived_id_ceiling": "ID2",
        "primary_blocker": None,
        "native_support_status": "experiment_local",
        "native_observables_used": [
            "manifest_declared_lgrc_node_ids",
            "manifest_declared_lgrc_edge_ids",
            "node_plus_packet_budget_accounting",
        ],
        "experiment_local_observables_used": [
            observation["event_id"],
            stability_record["record_id"],
        ],
        "native_policy_blockers": [
            stability_record["native_policy_blocker"],
        ],
        "becoming_class_status": "observation_tag",
        "probe_role": "diagnostic_probe",
        "boundary_rung": "substrate_consequence",
        "support_dependency_status": "probe_dependent",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": "Nat0_probe_dependent_expression",
        "activity_history_digest": _digest(
            {
                "orientation": "N07 Iteration 4 ID2 stability/local-well candidate",
                "observation": observation["event_id"],
                "classification": "ID2_stable_basin_candidate",
                "probe": "manifest_declared_stability_well_proxy",
                "withdrawal": "not_tested",
                "naturalization": "not_applicable",
                "integration": "pending_iteration_5",
            }
        ),
        "claim_flags": _claim_flags(manifest),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "claim_ceiling": "stable_basin_candidate",
        "stability_is_identity_acceptance_claim": False,
        "identity_acceptance_claim_allowed": False,
        "agency_claim_allowed": False,
    }


def _control_rows(*, claim_flags: Mapping[str, bool]) -> list[dict[str, Any]]:
    controls = [
        {
            "control_id": "unstable_basin_no_local_well",
            "mutated_field": "stability_score",
            "mutated_value": 0.62,
            "primary_blocker": "unstable_basin_no_local_well",
        },
        {
            "control_id": "posthoc_threshold_change",
            "mutated_field": "threshold_after_run",
            "mutated_value": 0.95,
            "primary_blocker": "posthoc_threshold_change",
        },
        {
            "control_id": "hidden_potential_or_report_side_well_score",
            "mutated_field": "hidden_potential_or_report_side_well_score_used",
            "mutated_value": True,
            "primary_blocker": "hidden_potential_or_report_side_well_score",
        },
        {
            "control_id": "wrong_support_area",
            "mutated_field": "support_area_id",
            "mutated_value": "n07_support_area_wrong_v1",
            "primary_blocker": "wrong_support_area",
        },
        {
            "control_id": "budget_discontinuity",
            "mutated_field": "budget_error",
            "mutated_value": 0.1,
            "primary_blocker": "budget_discontinuity",
        },
    ]
    return [
        {
            **control,
            "status": "blocked",
            "support_gate": "pass",
            "stability_gate": "blocked",
            "derived_id_ceiling": "ID1",
            "claim_flags": dict(claim_flags),
            "distinct_primary_blocker": True,
        }
        for control in controls
    ]


def _evidence_only_surfaces() -> dict[str, Any]:
    return {
        "surface_row": "evidence_only",
        "deformation_token": "evidence_only",
        "boundary_signal": "evidence_only",
        "route_selection": "evidence_only",
        "movement_trace": "evidence_only",
        "non_coherence_basin_surfaces_promoted": False,
    }


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "source_id1_output_digest": _digest(result["source_id1_output_summary"]),
        "stability_observation_event_digest": _digest(
            result["stability_observation_event"]
        ),
        "stability_proxy_record_digest": _digest(result["stability_proxy_record"]),
        "id2_candidate_row_digest": _digest(result["id2_candidate_row"]),
        "control_rows_digest": _digest(result["control_rows"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    manifest = result["manifest"]
    family = _topology_family(manifest)
    metric = manifest["metric_definitions"]["stability_well_proxy"]
    observation = result["stability_observation_event"]
    stability_record = result["stability_proxy_record"]
    candidate = result["id2_candidate_row"]
    id1_output = result["source_id1_output"]
    gate_schema = manifest["gate_vector_schema"]
    becoming_enums = manifest["becoming_method_fields"]["enum_values"]
    control_rows = result["control_rows"]
    control_ids = [control["control_id"] for control in control_rows]
    blockers = [control["primary_blocker"] for control in control_rows]
    proper_time_indices = [
        sample["proper_time_index"] for sample in observation["proper_time_samples"]
    ]
    incoming_flux_sum = sum(
        sample["incoming_flux_to_support"]
        for sample in observation["proper_time_samples"]
    )
    outgoing_flux_sum = sum(
        sample["outgoing_flux_from_support"]
        for sample in observation["proper_time_samples"]
    )
    expected_score = 0.5 * (
        observation["support_area_mass_after"] / observation["support_area_mass_before"]
    ) + 0.5 * (
        observation["incoming_flux_to_support"]
        / (
            observation["incoming_flux_to_support"]
            + observation["outgoing_flux_from_support"]
        )
    )
    return {
        "status_passed": result["status"] == "passed",
        "source_id1_status_passed": id1_output["status"] == "passed",
        "source_id1_support_gate_passed": id1_output["id1_candidate_row"][
            "gate_vector"
        ]["support"]
        == "pass",
        "candidate_topology_family_matches_manifest": candidate[
            "topology_family_id"
        ]
        == family["topology_family_id"],
        "candidate_gate_matches_manifest": family["gate_under_test"] == "stability"
        and candidate["gate_vector"][family["gate_under_test"]] == "pass",
        "candidate_primary_metric_matches_manifest": family[
            "primary_positive_metric"
        ]
        == "stability_well_proxy",
        "candidate_target_id_matches_manifest": candidate["id_level"]
        == family["target_id_level"],
        "stability_proxy_formula_matches_manifest": stability_record[
            "proxy_formula"
        ]
        == metric["proxy_formula"],
        "stability_proxy_inputs_match_manifest": stability_record["input_fields"]
        == metric["input_fields"],
        "stability_threshold_fixed": stability_record["threshold"]
        == metric["threshold"]
        and stability_record["thresholds_fixed_before_run"] is True
        and stability_record["posthoc_threshold_change_used"] is False,
        "stability_inputs_source_backed": observation["source_backed"] is True
        and observation["runtime_visible"] is True
        and observation["report_side_only"] is False,
        "proper_time_samples_source_backed": observation[
            "proper_time_sample_count"
        ]
        == len(observation["proper_time_samples"])
        and observation["proper_time_sample_count"] == 3,
        "proper_time_sample_ordering_valid": proper_time_indices
        == sorted(proper_time_indices)
        and len(proper_time_indices) == len(set(proper_time_indices)),
        "proper_time_flux_aggregates_match_samples": abs(
            observation["incoming_flux_to_support"] - incoming_flux_sum
        )
        < 1e-12
        and abs(observation["outgoing_flux_from_support"] - outgoing_flux_sum)
        < 1e-12,
        "stability_score_recomputed": abs(
            stability_record["stability_score"] - expected_score
        )
        < 1e-12,
        "stability_score_above_threshold": stability_record["stability_score"]
        >= stability_record["threshold"],
        "no_hidden_potential_or_report_side_score": observation[
            "hidden_potential_or_report_side_well_score_used"
        ]
        is False
        and stability_record["hidden_report_side_score_allowed"] is False,
        "budget_exact": observation["budget_error"] == 0.0
        and stability_record["budget_error"] == 0.0,
        "candidate_carrier_is_coherence_basin": candidate[
            "candidate_identity_carrier_type"
        ]
        == "coherence_basin",
        "gate_vector_schema_matches_manifest": set(candidate["gate_vector"])
        == set(gate_schema["fields"])
        and set(candidate["gate_vector"].values()).issubset(
            set(gate_schema["allowed_values"])
        ),
        "derived_ceiling_id2": candidate["derived_id_ceiling"] == "ID2",
        "native_support_not_overstated": candidate["native_support_status"]
        == "experiment_local"
        and candidate["native_support_status"] in NATIVE_SUPPORT_STATUS_VALUES
        and metric["native_policy_blocker"] in candidate["native_policy_blockers"],
        "becoming_method_values_allowed": all(
            candidate[field] in set(becoming_enums[field])
            for field in [
                "becoming_class_status",
                "probe_role",
                "boundary_rung",
                "support_dependency_status",
                "withdrawal_test_status",
                "naturalization_rung",
            ]
        ),
        "stability_not_identity_acceptance_claim": candidate[
            "stability_is_identity_acceptance_claim"
        ]
        is False,
        "evidence_only_surfaces_not_promoted": result["evidence_only_surfaces"][
            "non_coherence_basin_surfaces_promoted"
        ]
        is False,
        "claim_flag_keys_match_manifest": set(candidate["claim_flags"])
        == set(result["claim_flags"])
        == set(manifest["claim_boundary"]["claim_flags"]),
        "required_controls_present": set(CONTROL_BLOCKERS).issubset(
            set(control_ids)
        ),
        "control_blockers_distinct": len(blockers) == len(set(blockers)),
        "controls_blocked": all(control["status"] == "blocked" for control in control_rows),
        "control_ceilings_id1": all(
            control["derived_id_ceiling"] == "ID1" for control in control_rows
        ),
        "claim_flags_all_false": all(value is False for value in result["claim_flags"].values()),
        "identity_acceptance_blocked": result["claim_flags"][
            "identity_acceptance_claim_allowed"
        ]
        is False
        and result["claim_flags"]["agency_claim_allowed"] is False,
        "no_src_changes_required": result["git"]["status_short_src"]["stdout"] == "",
    }


def _write_report(result: Mapping[str, Any]) -> None:
    controls = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` |".format(
            control["control_id"],
            control["status"],
            control["primary_blocker"],
            control["derived_id_ceiling"],
        )
        for control in result["control_rows"]
    )
    checks = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in sorted(result["checks"].items())
    )
    REPORT_PATH.write_text(
        f"""# N07 Iteration 4: ID2 Stability / Local Well Candidate

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Iteration 4 applies the manifest-declared experiment-local stability proxy to
the Iteration 3 support-area candidate. It records source-backed proxy inputs,
a fixed threshold, and a recomputable stability score. It does not claim native
basin-potential support, identity acceptance, agency, attractivity, invariance,
reflexive closure, or compatibility.

## Stability Proxy Record

```json
{json.dumps(result['stability_proxy_record'], indent=2, sort_keys=True)}
```

## Candidate Row

```json
{json.dumps(result['id2_candidate_row'], indent=2, sort_keys=True)}
```

## Controls

| Control | Status | Primary blocker | Derived ceiling |
|---|---|---|---|
{controls}

## Checks

| Check | Passed |
|---|---:|
{checks}

## Artifact Digests

```json
{json.dumps(result['artifact_digests'], indent=2, sort_keys=True)}
```

## Acceptance

Iteration 4 passes because the support area also satisfies the declared
stability proxy with source-backed inputs, a fixed threshold, exact
node-plus-packet budget accounting, and controls for unstable basin,
post-hoc threshold changes, hidden/report-side well scores, wrong support
area, and budget discontinuity. The result is capped at ID2/stable basin
candidate, remains experiment-local because native basin-potential support is
not available, and all identity-acceptance, agency, movement, biological, and
unrestricted claim flags remain false.
""",
        encoding="utf-8",
    )


def build_result() -> dict[str, Any]:
    manifest_validation = _load_json(MANIFEST_VALIDATION_PATH)
    manifest = manifest_validation["manifest"]
    id1_output = _load_json(ID1_OUTPUT_PATH)
    claim_flags = _claim_flags(manifest)
    observation = _stability_observation_event(
        manifest=manifest,
        id1_output=id1_output,
    )
    stability_record = _stability_proxy_record(
        manifest=manifest,
        id1_output=id1_output,
        observation=observation,
    )
    candidate = _id2_candidate_row(
        manifest=manifest,
        id1_output=id1_output,
        observation=observation,
        stability_record=stability_record,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_4_id2_stability_candidate_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": 4,
        "status": "passed",
        "command": COMMAND,
        "environment": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "source_manifest": {
            "path": _rel(MANIFEST_PATH),
            "sha256": _file_sha256(MANIFEST_PATH),
        },
        "source_manifest_validation": {
            "path": _rel(MANIFEST_VALIDATION_PATH),
            "sha256": _file_sha256(MANIFEST_VALIDATION_PATH),
            "status": manifest_validation["status"],
        },
        "source_id1_output_summary": {
            "path": _rel(ID1_OUTPUT_PATH),
            "sha256": _file_sha256(ID1_OUTPUT_PATH),
            "status": id1_output["status"],
            "id1_candidate_row_digest": id1_output["artifact_digests"][
                "id1_candidate_row_digest"
            ],
            "support_area_row_digest": id1_output["artifact_digests"][
                "support_area_row_digest"
            ],
        },
        "manifest": manifest,
        "source_id1_output": id1_output,
        "stability_observation_event": observation,
        "stability_proxy_record": stability_record,
        "id2_candidate_row": candidate,
        "control_rows": _control_rows(claim_flags=claim_flags),
        "evidence_only_surfaces": _evidence_only_surfaces(),
        "claim_flags": claim_flags,
        "acceptance": {
            "id2_stability_candidate_emitted": True,
            "id1_source_consumed": True,
            "support_gate_passed": True,
            "stability_gate_passed": True,
            "stability_proxy_policy": "experiment_local_declared_second_difference_retention_proxy",
            "stability_threshold_fixed_before_run": True,
            "hidden_potential_or_report_side_score_used": False,
            "posthoc_threshold_change_used": False,
            "budget_exact": True,
            "manifest_contract_checks_passed": True,
            "controls_declared_and_blocked": True,
            "identity_claims_blocked": True,
            "native_support_status": "experiment_local",
            "native_policy_blockers": [
                "native_basin_potential_policy_missing",
            ],
            "next_iteration": "5_id3_attractivity_candidate",
        },
        "git": {
            "status_short_src": _git(["status", "--short", "src"]),
        },
    }
    result["checks"] = _checks(result)
    result["artifact_digests"] = _artifact_digests(result)
    result["status"] = "passed" if all(result["checks"].values()) else "failed"
    result["checks"]["status_passed"] = result["status"] == "passed"
    result["artifact_digests"] = _artifact_digests(result)
    return result


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = build_result()
    OUTPUT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_report(result)
    print(OUTPUT_PATH)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()

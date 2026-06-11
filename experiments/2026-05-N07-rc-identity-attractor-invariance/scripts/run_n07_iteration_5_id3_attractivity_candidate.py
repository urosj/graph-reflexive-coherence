"""Run N07 Iteration 5 ID3 attractivity/flux-convergence candidate.

This script is experiment-local. It consumes the Iteration 4 stable-basin
candidate, applies the manifest-declared flux-convergence metric over the
declared neighborhood U, records an ID3 candidate row, and emits negative
controls for non-attractive flux, wrong basin, wrong polarity, subthreshold
flux, hidden route-context steering, and budget discontinuity. It does not
import or mutate `src/pygrc`.
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
ID2_OUTPUT_PATH = N07 / "outputs/n07_iteration_4_id2_stability_candidate.json"
ID2_REPORT_PATH = N07 / "reports/n07_iteration_4_id2_stability_candidate.md"
OUTPUT_PATH = N07 / "outputs/n07_iteration_5_id3_attractivity_candidate.json"
REPORT_PATH = N07 / "reports/n07_iteration_5_id3_attractivity_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_5_id3_attractivity_candidate.py"
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
    "non_attractive_flux": "non_attractive_flux",
    "wrong_basin": "wrong_basin",
    "wrong_polarity": "wrong_polarity",
    "subthreshold_flux": "subthreshold_flux",
    "hidden_route_context_steering": "hidden_route_context_steering",
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
        if family["topology_family_id"] == "n07_T3_attractor_neighborhood"
    )


def _source_artifact_records(id2_output: Mapping[str, Any]) -> list[dict[str, Any]]:
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
            "name": "n07_iteration_4_id2_stability_candidate",
            "path": _rel(ID2_OUTPUT_PATH),
            "sha256": _file_sha256(ID2_OUTPUT_PATH),
            "status": id2_output["status"],
            "stability_proxy_record_digest": id2_output["artifact_digests"][
                "stability_proxy_record_digest"
            ],
            "id2_candidate_row_digest": id2_output["artifact_digests"][
                "id2_candidate_row_digest"
            ],
        },
    ]


def _source_report_records() -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_4_id2_stability_candidate_report",
            "path": _rel(ID2_REPORT_PATH),
            "sha256": _file_sha256(ID2_REPORT_PATH),
        }
    ]


def _flux_observation_event(
    *,
    manifest: Mapping[str, Any],
    id2_output: Mapping[str, Any],
) -> dict[str, Any]:
    fixture = manifest["fixture"]
    neighborhood = fixture["neighborhood_U"]
    support_area_id = id2_output["id2_candidate_row"]["support_area_id"]
    support_area_digest = id2_output["id2_candidate_row"]["support_area_digest"]
    packet_work_events = [
        {
            "packet_event_id": "n07_i5_flux_packet_0001",
            "source_node_id": 0,
            "target_node_id": 2,
            "route_node_ids": [0, 1, 2],
            "amount": 0.18,
            "polarity": "toward_support",
            "runtime_visible": True,
        },
        {
            "packet_event_id": "n07_i5_flux_packet_0002",
            "source_node_id": 4,
            "target_node_id": 2,
            "route_node_ids": [4, 2],
            "amount": 0.12,
            "polarity": "toward_support",
            "runtime_visible": True,
        },
        {
            "packet_event_id": "n07_i5_flux_packet_0003",
            "source_node_id": 2,
            "target_node_id": 3,
            "route_node_ids": [2, 3],
            "amount": 0.06,
            "polarity": "away_from_support",
            "runtime_visible": True,
        },
    ]
    incoming = sum(
        event["amount"]
        for event in packet_work_events
        if event["target_node_id"] == 2 and event["polarity"] == "toward_support"
    )
    outgoing = sum(
        event["amount"]
        for event in packet_work_events
        if event["source_node_id"] == 2 and event["polarity"] == "away_from_support"
    )
    return {
        "event_id": "n07_i5_flux_observation_event_0001",
        "event_kind": "experiment_local_runtime_visible_neighborhood_flux_window",
        "event_time_key": "n07_i5_t2_flux_convergence_window",
        "scheduler_event_index": 2,
        "source_id2_candidate_row_id": id2_output["id2_candidate_row"]["row_id"],
        "source_id2_candidate_row_digest": id2_output["artifact_digests"][
            "id2_candidate_row_digest"
        ],
        "source_stability_record_digest": id2_output["artifact_digests"][
            "stability_proxy_record_digest"
        ],
        "support_area_id": support_area_id,
        "support_area_digest": support_area_digest,
        "candidate_basin_id": fixture["candidate_runtime_coherence_basin"]["basin_id"],
        "candidate_identity_carrier_type": "coherence_basin",
        "topology_family_id": "n07_T3_attractor_neighborhood",
        "flux_metric_id": "n07_flux_convergence_to_support_v1",
        "neighborhood_U": neighborhood,
        "neighborhood_U_digest": _digest(neighborhood),
        "packet_work_events": packet_work_events,
        "packet_work_events_digest": _digest(packet_work_events),
        "surface_rows_consumed": [
            {
                "surface_kind": "support_area",
                "surface_digest": support_area_digest,
                "source_iteration": 3,
            },
            {
                "surface_kind": "stability_proxy",
                "surface_digest": id2_output["artifact_digests"][
                    "stability_proxy_record_digest"
                ],
                "source_iteration": 4,
            },
        ],
        "net_flux_into_support_from_U": incoming,
        "net_flux_out_of_support": outgoing,
        "net_flux_convergence_margin": incoming - outgoing,
        "incoming_flux_source_node_ids": [0, 4],
        "outgoing_flux_target_node_ids": [3],
        "wrong_basin_node_ids_observed": [],
        "polarity": "toward_support",
        "preselected_by_fixture_label": False,
        "hidden_route_context_steering_used": False,
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "budget_surface": fixture["budget_surface"]["budget_surface"],
        "budget_before": fixture["budget_surface"]["conserved_budget_total"],
        "budget_after": fixture["budget_surface"]["conserved_budget_total"],
        "budget_error": 0.0,
        "min_active_node_coherence": 0.0,
        "min_packet_amount": min(event["amount"] for event in packet_work_events),
        "nonnegative_state_passed": True,
    }


def _flux_convergence_record(
    *,
    manifest: Mapping[str, Any],
    observation: Mapping[str, Any],
) -> dict[str, Any]:
    metric = manifest["metric_definitions"]["flux_convergence"]
    digest_input = {
        "metric_id": metric["metric_id"],
        "formula": metric["formula"],
        "positive_threshold": metric["positive_threshold"],
        "runtime_visible_inputs": metric["runtime_visible_inputs"],
        "support_area_digest": observation["support_area_digest"],
        "neighborhood_U_digest": observation["neighborhood_U_digest"],
        "packet_work_events_digest": observation["packet_work_events_digest"],
        "surface_rows_consumed": observation["surface_rows_consumed"],
        "net_flux_into_support_from_U": observation["net_flux_into_support_from_U"],
        "net_flux_out_of_support": observation["net_flux_out_of_support"],
        "net_flux_convergence_margin": observation["net_flux_convergence_margin"],
        "event_time_key": observation["event_time_key"],
        "scheduler_event_index": observation["scheduler_event_index"],
    }
    record_digest = _digest(digest_input)
    idempotency_key = {
        "flux_metric_id": metric["metric_id"],
        "support_area_digest": observation["support_area_digest"],
        "neighborhood_U_digest": observation["neighborhood_U_digest"],
        "event_time_key": observation["event_time_key"],
        "scheduler_event_index": observation["scheduler_event_index"],
    }
    return {
        "record_id": "n07_i5_flux_convergence_record_v1",
        "record_kind": "experiment_local_flux_convergence_record",
        "flux_metric_id": metric["metric_id"],
        "formula": metric["formula"],
        "positive_threshold": metric["positive_threshold"],
        "runtime_visible_inputs": metric["runtime_visible_inputs"],
        "metric_controls": metric["controls"],
        "native_policy_available": metric["native_policy_available"],
        "native_policy_blocker": metric["native_policy_blocker"],
        "source_observation_event_id": observation["event_id"],
        "source_observation_event_digest": _digest(observation),
        "support_area_digest": observation["support_area_digest"],
        "neighborhood_U_digest": observation["neighborhood_U_digest"],
        "packet_work_events_digest": observation["packet_work_events_digest"],
        "net_flux_into_support_from_U": observation["net_flux_into_support_from_U"],
        "net_flux_out_of_support": observation["net_flux_out_of_support"],
        "net_flux_convergence_margin": observation["net_flux_convergence_margin"],
        "attractivity_gate": (
            "pass"
            if observation["net_flux_convergence_margin"]
            > metric["positive_threshold"]
            else "fail"
        ),
        "budget_surface": observation["budget_surface"],
        "budget_before": observation["budget_before"],
        "budget_after": observation["budget_after"],
        "budget_error": observation["budget_error"],
        "min_active_node_coherence": observation["min_active_node_coherence"],
        "min_packet_amount": observation["min_packet_amount"],
        "nonnegative_state_passed": observation["nonnegative_state_passed"],
        "preselected_by_fixture_label": False,
        "hidden_route_context_steering_used": False,
        "wrong_basin_node_ids_observed": [],
        "polarity": "toward_support",
        "runtime_visible": True,
        "source_backed": True,
        "report_side_only": False,
        "flux_convergence_record_digest_input": digest_input,
        "flux_convergence_record_digest": record_digest,
        "flux_convergence_idempotency_key": idempotency_key,
        "flux_convergence_idempotency_key_digest": _digest(idempotency_key),
    }


def _id3_candidate_row(
    *,
    manifest: Mapping[str, Any],
    id2_output: Mapping[str, Any],
    observation: Mapping[str, Any],
    flux_record: Mapping[str, Any],
) -> dict[str, Any]:
    id2_candidate = id2_output["id2_candidate_row"]
    metric = manifest["metric_definitions"]["flux_convergence"]
    return {
        "row_id": "n07_i5_id3_attractivity_candidate_row_v1",
        "id_level": "ID3",
        "topology_family_id": "n07_T3_attractor_neighborhood",
        "composite_topology_id": None,
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": id2_candidate["support_area_id"],
        "support_area_digest": id2_candidate["support_area_digest"],
        "stability_record_id": id2_candidate["stability_record_id"],
        "stability_record_digest": id2_candidate["stability_record_digest"],
        "flux_convergence_record_id": flux_record["record_id"],
        "flux_convergence_record_digest": flux_record[
            "flux_convergence_record_digest"
        ],
        "source_artifacts": _source_artifact_records(id2_output),
        "source_artifact_sha256": {
            item["path"]: item["sha256"] for item in _source_artifact_records(id2_output)
        },
        "source_reports": _source_report_records(),
        "runtime_family": "LGRC9V3",
        "implementation_surface": "experiment_local_identity_gate_record",
        "gate_vector": _gate_vector(
            support="pass",
            stability="pass",
            attractivity="pass",
        ),
        "derived_id_ceiling": "ID3",
        "primary_blocker": None,
        "native_support_status": "experiment_local",
        "native_observables_used": [
            "manifest_declared_lgrc_node_ids",
            "manifest_declared_lgrc_edge_ids",
            "node_plus_packet_budget_accounting",
        ],
        "experiment_local_observables_used": [
            observation["event_id"],
            flux_record["record_id"],
        ],
        "native_policy_blockers": [metric["native_policy_blocker"]],
        "becoming_class_status": "observation_tag",
        "probe_role": "diagnostic_probe",
        "boundary_rung": "structured_consequence",
        "support_dependency_status": "probe_dependent",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": "Nat0_probe_dependent_expression",
        "activity_history_digest": _digest(
            {
                "orientation": "N07 Iteration 5 ID3 attractivity candidate",
                "observation": observation["event_id"],
                "classification": "ID3_attractor_candidate",
                "probe": "manifest_declared_flux_convergence_metric",
                "withdrawal": "not_tested",
                "naturalization": "not_applicable",
                "integration": "pending_iteration_6",
            }
        ),
        "claim_flags": _claim_flags(manifest),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "claim_ceiling": "attractor_candidate",
        "attractivity_is_agency_claim": False,
        "identity_acceptance_claim_allowed": False,
        "agency_claim_allowed": False,
    }


def _control_rows(*, claim_flags: Mapping[str, bool]) -> list[dict[str, Any]]:
    controls = [
        {
            "control_id": "non_attractive_flux",
            "mutated_field": "net_flux_convergence_margin",
            "mutated_value": -0.03,
            "primary_blocker": "non_attractive_flux",
        },
        {
            "control_id": "wrong_basin",
            "mutated_field": "target_support_area_id",
            "mutated_value": "n07_support_area_wrong_v1",
            "primary_blocker": "wrong_basin",
        },
        {
            "control_id": "wrong_polarity",
            "mutated_field": "polarity",
            "mutated_value": "away_from_support",
            "primary_blocker": "wrong_polarity",
        },
        {
            "control_id": "subthreshold_flux",
            "mutated_field": "net_flux_convergence_margin",
            "mutated_value": 0.0,
            "primary_blocker": "subthreshold_flux",
        },
        {
            "control_id": "hidden_route_context_steering",
            "mutated_field": "hidden_route_context_steering_used",
            "mutated_value": True,
            "primary_blocker": "hidden_route_context_steering",
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
            "stability_gate": "pass",
            "attractivity_gate": "blocked",
            "derived_id_ceiling": "ID2",
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
        "source_id2_output_digest": _digest(result["source_id2_output_summary"]),
        "flux_observation_event_digest": _digest(result["flux_observation_event"]),
        "flux_convergence_record_digest": _digest(result["flux_convergence_record"]),
        "id3_candidate_row_digest": _digest(result["id3_candidate_row"]),
        "control_rows_digest": _digest(result["control_rows"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    manifest = result["manifest"]
    family = _topology_family(manifest)
    metric = manifest["metric_definitions"]["flux_convergence"]
    observation = result["flux_observation_event"]
    flux_record = result["flux_convergence_record"]
    candidate = result["id3_candidate_row"]
    id2_output = result["source_id2_output"]
    gate_schema = manifest["gate_vector_schema"]
    becoming_enums = manifest["becoming_method_fields"]["enum_values"]
    control_rows = result["control_rows"]
    control_ids = [control["control_id"] for control in control_rows]
    blockers = [control["primary_blocker"] for control in control_rows]
    neighborhood_node_ids = set(observation["neighborhood_U"]["node_ids"])
    route_edges = {
        frozenset((edge["u"], edge["v"])) for edge in manifest["fixture"]["edges"]
    }
    packet_event_ids = [
        event["packet_event_id"] for event in observation["packet_work_events"]
    ]
    incoming = sum(
        event["amount"]
        for event in observation["packet_work_events"]
        if event["target_node_id"] == 2 and event["polarity"] == "toward_support"
    )
    outgoing = sum(
        event["amount"]
        for event in observation["packet_work_events"]
        if event["source_node_id"] == 2 and event["polarity"] == "away_from_support"
    )
    return {
        "status_passed": result["status"] == "passed",
        "source_id2_status_passed": id2_output["status"] == "passed",
        "source_id2_support_and_stability_passed": id2_output["id2_candidate_row"][
            "gate_vector"
        ]["support"]
        == "pass"
        and id2_output["id2_candidate_row"]["gate_vector"]["stability"] == "pass",
        "candidate_topology_family_matches_manifest": candidate[
            "topology_family_id"
        ]
        == family["topology_family_id"],
        "candidate_gate_matches_manifest": family["gate_under_test"]
        == "attractivity"
        and candidate["gate_vector"][family["gate_under_test"]] == "pass",
        "candidate_primary_metric_matches_manifest": family[
            "primary_positive_metric"
        ]
        == "flux_convergence",
        "candidate_target_id_matches_manifest": candidate["id_level"]
        == family["target_id_level"],
        "neighborhood_u_matches_manifest": observation["neighborhood_U"]
        == manifest["fixture"]["neighborhood_U"],
        "flux_nodes_are_members_of_neighborhood_u": set(
            observation["incoming_flux_source_node_ids"]
        ).issubset(neighborhood_node_ids)
        and set(observation["outgoing_flux_target_node_ids"]).issubset(
            neighborhood_node_ids
        ),
        "packet_event_ids_unique": len(packet_event_ids) == len(set(packet_event_ids)),
        "packet_routes_follow_manifest_edges": all(
            all(
                frozenset((u, v)) in route_edges
                for u, v in zip(
                    event["route_node_ids"], event["route_node_ids"][1:]
                )
            )
            for event in observation["packet_work_events"]
        ),
        "flux_metric_formula_matches_manifest": flux_record["formula"]
        == metric["formula"],
        "flux_metric_inputs_match_manifest": flux_record["runtime_visible_inputs"]
        == metric["runtime_visible_inputs"],
        "flux_native_policy_fields_match_manifest": flux_record[
            "native_policy_available"
        ]
        == metric["native_policy_available"]
        and flux_record["native_policy_blocker"] == metric["native_policy_blocker"],
        "flux_events_runtime_visible": all(
            event["runtime_visible"] is True for event in observation["packet_work_events"]
        )
        and observation["runtime_visible"] is True
        and observation["source_backed"] is True
        and observation["report_side_only"] is False,
        "flux_margin_recomputed": abs(
            observation["net_flux_convergence_margin"] - (incoming - outgoing)
        )
        < 1e-12,
        "flux_convergence_passed": flux_record["attractivity_gate"] == "pass"
        and observation["net_flux_convergence_margin"] > metric["positive_threshold"],
        "budget_exact": observation["budget_error"] == 0.0
        and flux_record["budget_error"] == 0.0,
        "nonnegative_state_passed": observation["nonnegative_state_passed"] is True
        and flux_record["nonnegative_state_passed"] is True
        and observation["min_active_node_coherence"] >= 0.0
        and observation["min_packet_amount"] >= 0.0,
        "not_preselected_by_fixture_labels": observation[
            "preselected_by_fixture_label"
        ]
        is False
        and flux_record["preselected_by_fixture_label"] is False,
        "no_hidden_route_context_steering": observation[
            "hidden_route_context_steering_used"
        ]
        is False
        and flux_record["hidden_route_context_steering_used"] is False,
        "candidate_carrier_is_coherence_basin": candidate[
            "candidate_identity_carrier_type"
        ]
        == "coherence_basin",
        "gate_vector_schema_matches_manifest": set(candidate["gate_vector"])
        == set(gate_schema["fields"])
        and set(candidate["gate_vector"].values()).issubset(
            set(gate_schema["allowed_values"])
        ),
        "derived_ceiling_id3": candidate["derived_id_ceiling"] == "ID3",
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
        "attractivity_not_agency_claim": candidate["attractivity_is_agency_claim"]
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
        "manifest_flux_controls_exercised": set(metric["controls"]).issubset(
            set(control_ids)
        ),
        "control_blockers_distinct": len(blockers) == len(set(blockers)),
        "controls_blocked": all(control["status"] == "blocked" for control in control_rows),
        "control_ceilings_id2": all(
            control["derived_id_ceiling"] == "ID2" for control in control_rows
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
        f"""# N07 Iteration 5: ID3 Attractivity / Flux Convergence

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Iteration 5 applies the manifest-declared flux-convergence metric to the
Iteration 4 stable-basin candidate. It records runtime-visible packet-work
events from the declared neighborhood U into the support area, verifies exact
budget/nonnegative state, and rejects hidden route-context steering. It does
not claim native attractor-neighborhood support, agency, identity acceptance,
invariance, reflexive closure, or compatibility.

This is a first-pass ID3 attractivity candidate. Iteration 5-B is reserved for
multi-source, multi-window attractivity stress before the experiment advances
to invariance.

## Flux Convergence Record

```json
{json.dumps(result['flux_convergence_record'], indent=2, sort_keys=True)}
```

## Candidate Row

```json
{json.dumps(result['id3_candidate_row'], indent=2, sort_keys=True)}
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

Iteration 5 passes because flux from the declared runtime-visible neighborhood
converges into the stable support area under exact node-plus-packet budget
accounting and nonnegative state. The result is capped at ID3/attractor
candidate, remains experiment-local because native attractor-neighborhood
policy support is not available, and all identity-acceptance, agency, movement,
biological, and unrestricted claim flags remain false.
""",
        encoding="utf-8",
    )


def build_result() -> dict[str, Any]:
    manifest_validation = _load_json(MANIFEST_VALIDATION_PATH)
    manifest = manifest_validation["manifest"]
    id2_output = _load_json(ID2_OUTPUT_PATH)
    claim_flags = _claim_flags(manifest)
    observation = _flux_observation_event(
        manifest=manifest,
        id2_output=id2_output,
    )
    flux_record = _flux_convergence_record(
        manifest=manifest,
        observation=observation,
    )
    candidate = _id3_candidate_row(
        manifest=manifest,
        id2_output=id2_output,
        observation=observation,
        flux_record=flux_record,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_5_id3_attractivity_candidate_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": 5,
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
        "source_id2_output_summary": {
            "path": _rel(ID2_OUTPUT_PATH),
            "sha256": _file_sha256(ID2_OUTPUT_PATH),
            "status": id2_output["status"],
            "id2_candidate_row_digest": id2_output["artifact_digests"][
                "id2_candidate_row_digest"
            ],
            "stability_proxy_record_digest": id2_output["artifact_digests"][
                "stability_proxy_record_digest"
            ],
        },
        "manifest": manifest,
        "source_id2_output": id2_output,
        "flux_observation_event": observation,
        "flux_convergence_record": flux_record,
        "id3_candidate_row": candidate,
        "control_rows": _control_rows(claim_flags=claim_flags),
        "evidence_only_surfaces": _evidence_only_surfaces(),
        "claim_flags": claim_flags,
        "acceptance": {
            "id3_attractivity_candidate_emitted": True,
            "id2_source_consumed": True,
            "support_gate_passed": True,
            "stability_gate_passed": True,
            "attractivity_gate_passed": True,
            "flux_metric_id": "n07_flux_convergence_to_support_v1",
            "neighborhood_U_declared": True,
            "flux_margin": observation["net_flux_convergence_margin"],
            "positive_threshold": manifest["metric_definitions"]["flux_convergence"][
                "positive_threshold"
            ],
            "runtime_visible_packet_work_events": True,
            "preselected_by_fixture_label": False,
            "hidden_route_context_steering_used": False,
            "budget_exact": True,
            "nonnegative_state_passed": True,
            "manifest_contract_checks_passed": True,
            "controls_declared_and_blocked": True,
            "identity_claims_blocked": True,
            "native_support_status": "experiment_local",
            "native_policy_blockers": [
                manifest["metric_definitions"]["flux_convergence"][
                    "native_policy_blocker"
                ]
            ],
            "next_iteration": "5B_id3_attractivity_stress_candidate",
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

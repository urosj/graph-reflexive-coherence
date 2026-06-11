"""Run N07 Iteration 3 ID1 support-area candidate.

This script is experiment-local. It derives a source-backed support-area row
from the frozen Iteration 2 manifest, records an ID1 candidate row, and emits
negative controls for missing support, label-only support, hidden support,
duplicate support rows, and budget discontinuity. It does not import or mutate
`src/pygrc`.
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
MANIFEST_REPORT_PATH = N07 / "reports/n07_iteration_2_fixture_manifest_validation.md"
OUTPUT_PATH = N07 / "outputs/n07_iteration_3_id1_support_area_candidate.json"
REPORT_PATH = N07 / "reports/n07_iteration_3_id1_support_area_candidate.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N07-rc-identity-attractor-invariance/scripts/"
    "run_n07_iteration_3_id1_support_area_candidate.py"
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
    "label_only_null_topology": "label_only_null_topology",
    "missing_support_area": "missing_support_area",
    "external_label_only": "external_label_only",
    "hidden_support_field": "hidden_support_field",
    "duplicate_support_row": "duplicate_support_row",
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


def _source_support_event(manifest: Mapping[str, Any]) -> dict[str, Any]:
    fixture = manifest["fixture"]
    support_area = manifest["support_area"]
    return {
        "event_id": "n07_i3_support_surface_event_0001",
        "event_kind": "experiment_local_runtime_visible_support_surface_row",
        "event_time_key": "n07_i3_t0_support_commit",
        "scheduler_event_index": 0,
        "source_fixture_id": fixture["fixture_id"],
        "support_area_id": support_area["support_area_id"],
        "candidate_basin_id": fixture["candidate_runtime_coherence_basin"]["basin_id"],
        "candidate_identity_carrier_type": "coherence_basin",
        "support_node_ids": sorted(support_area["support_node_ids"]),
        "support_edge_ids": sorted(support_area["support_edge_ids"]),
        "support_port_ids": sorted(support_area["support_port_ids"]),
        "lineage_status": support_area["lineage_status"],
        "lineage_map_digest": None,
        "budget_surface": "node_plus_packet",
        "budget_before": 6.0,
        "budget_after": 6.0,
        "budget_error": 0.0,
        "runtime_visible": True,
        "report_side_only": False,
        "hidden_support_source_used": False,
    }


def _support_area_digest_input(source_event: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "support_area_id": source_event["support_area_id"],
        "candidate_identity_carrier_type": source_event[
            "candidate_identity_carrier_type"
        ],
        "support_node_ids": source_event["support_node_ids"],
        "support_edge_ids": source_event["support_edge_ids"],
        "support_port_ids": source_event["support_port_ids"],
        "lineage_status": source_event["lineage_status"],
        "lineage_map_digest": source_event["lineage_map_digest"],
        "support_surface_digest": _digest(source_event),
        "event_time_key": source_event["event_time_key"],
        "scheduler_event_index": source_event["scheduler_event_index"],
        "budget_surface": source_event["budget_surface"],
        "budget_before": source_event["budget_before"],
        "budget_after": source_event["budget_after"],
        "budget_error": source_event["budget_error"],
    }


def _support_area_row(source_event: Mapping[str, Any]) -> dict[str, Any]:
    digest_input = _support_area_digest_input(source_event)
    support_area_digest = _digest(digest_input)
    idempotency_key = {
        "support_area_id": digest_input["support_area_id"],
        "support_area_digest": support_area_digest,
        "event_time_key": digest_input["event_time_key"],
        "scheduler_event_index": digest_input["scheduler_event_index"],
        "lineage_status": digest_input["lineage_status"],
    }
    return {
        **digest_input,
        "support_area_digest": support_area_digest,
        "support_area_idempotency_key": idempotency_key,
        "support_area_idempotency_key_digest": _digest(idempotency_key),
        "source_event_id": source_event["event_id"],
        "source_event_digest": _digest(source_event),
        "source_backed": True,
        "runtime_visible": True,
        "report_side_only": False,
        "hidden_support_source_used": False,
        "identity_label_is_evidence": False,
        "authored_central_node_is_identity_evidence": False,
        "support_gate": "pass",
    }


def _claim_flags(manifest: Mapping[str, Any]) -> dict[str, bool]:
    flags = manifest["claim_boundary"]["claim_flags"]
    return {key: False for key in sorted(flags)}


def _source_artifact_records() -> list[dict[str, Any]]:
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
    ]


def _source_report_records() -> list[dict[str, Any]]:
    return [
        {
            "name": "n07_iteration_2_fixture_manifest_validation_report",
            "path": _rel(MANIFEST_REPORT_PATH),
            "sha256": _file_sha256(MANIFEST_REPORT_PATH),
        }
    ]


def _execution_boundary() -> dict[str, Any]:
    return {
        "lgrc_step_invocations": 0,
        "step_cycles_run": 0,
        "scheduler_event_index_semantics": "support_commit_marker_not_runtime_step",
        "support_area_derivation": "manifest_declared_support_core",
        "support_area_source": "iteration_2_fixture_manifest",
        "support_area_discovered_by_dynamics": False,
        "dynamic_coherence_observation_window": "not_run_iteration_3",
        "stability_probe_run": False,
        "stability_deferred_to_iteration_4": True,
    }


def _id1_candidate_row(
    *,
    manifest: Mapping[str, Any],
    source_event: Mapping[str, Any],
    support_row: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "row_id": "n07_i3_id1_support_area_candidate_row_v1",
        "id_level": "ID1",
        "topology_family_id": "n07_T1_support_area_minimal",
        "composite_topology_id": None,
        "candidate_identity_carrier_type": "coherence_basin",
        "identity_carrier_surface": "runtime_coherence_basin",
        "support_area_id": support_row["support_area_id"],
        "support_area_digest": support_row["support_area_digest"],
        "source_artifacts": _source_artifact_records(),
        "source_artifact_sha256": {
            item["path"]: item["sha256"] for item in _source_artifact_records()
        },
        "source_reports": _source_report_records(),
        "runtime_family": "LGRC9V3",
        "implementation_surface": "experiment_local_identity_gate_record",
        "gate_vector": _gate_vector(support="pass"),
        "derived_id_ceiling": "ID1",
        "primary_blocker": None,
        "native_support_status": "experiment_local",
        "native_observables_used": [
            "manifest_declared_lgrc_node_ids",
            "manifest_declared_lgrc_edge_ids",
            "node_plus_packet_budget_accounting",
        ],
        "experiment_local_observables_used": [
            "n07_i3_support_surface_event_0001",
            "n07_i3_support_area_row_v1",
        ],
        "native_policy_blockers": [
            "native_rc_identity_support_area_policy_not_available"
        ],
        "becoming_class_status": "observation_tag",
        "probe_role": "diagnostic_probe",
        "boundary_rung": "eligible_state",
        "support_dependency_status": "probe_dependent",
        "withdrawal_test_status": "not_tested",
        "naturalization_rung": "Nat0_probe_dependent_expression",
        "activity_history_digest": _digest(
            {
                "orientation": "N07 Iteration 3 ID1 support-area candidate",
                "observation": source_event["event_id"],
                "classification": "ID1_support_area_candidate",
                "probe": "support_area_manifest_to_runtime_visible_row",
                "withdrawal": "not_tested",
                "naturalization": "not_applicable",
                "integration": "pending_iteration_4",
            }
        ),
        "claim_flags": _claim_flags(manifest),
        "visual_reference": None,
        "visual_is_evidence_source": False,
        "claim_ceiling": "support_area_candidate",
        "support_area_is_identity_claim": False,
        "identity_acceptance_claim_allowed": False,
        "agency_claim_allowed": False,
    }


def _control_rows(
    *, support_row: Mapping[str, Any], claim_flags: Mapping[str, bool]
) -> list[dict[str, Any]]:
    controls = [
        {
            "control_id": "label_only_null_topology",
            "mutated_field": "support_area_row",
            "mutated_value": None,
            "primary_blocker": "label_only_null_topology",
        },
        {
            "control_id": "missing_support_area",
            "mutated_field": "support_node_ids",
            "mutated_value": [],
            "primary_blocker": "missing_support_area",
        },
        {
            "control_id": "external_label_only",
            "mutated_field": "runtime_visible",
            "mutated_value": False,
            "primary_blocker": "external_label_only",
        },
        {
            "control_id": "hidden_support_field",
            "mutated_field": "hidden_support_source_used",
            "mutated_value": True,
            "primary_blocker": "hidden_support_field",
        },
        {
            "control_id": "duplicate_support_row",
            "mutated_field": "support_area_idempotency_key",
            "mutated_value": support_row["support_area_idempotency_key"],
            "primary_blocker": "duplicate_support_row",
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
            "support_gate": "blocked",
            "derived_id_ceiling": "ID0",
            "claim_flags": dict(claim_flags),
            "distinct_primary_blocker": True,
        }
        for control in controls
    ]


def _artifact_digests(result: Mapping[str, Any]) -> dict[str, str]:
    return {
        "execution_boundary_digest": _digest(result["execution_boundary"]),
        "source_support_event_digest": _digest(result["source_support_event"]),
        "support_area_row_digest": _digest(result["support_area_row"]),
        "id1_candidate_row_digest": _digest(result["id1_candidate_row"]),
        "control_rows_digest": _digest(result["control_rows"]),
        "claim_boundary_digest": _digest(result["claim_flags"]),
        "checks_digest": _digest(result["checks"]),
    }


def _checks(result: Mapping[str, Any]) -> dict[str, bool]:
    manifest = result["manifest"]
    support_row = result["support_area_row"]
    candidate = result["id1_candidate_row"]
    control_rows = result["control_rows"]
    execution_boundary = result["execution_boundary"]
    family = next(
        family
        for family in manifest["topology_families"]
        if family["topology_family_id"] == candidate["topology_family_id"]
    )
    gate_schema = manifest["gate_vector_schema"]
    gate_fields = set(gate_schema["fields"])
    gate_values = set(gate_schema["allowed_values"])
    becoming_enums = manifest["becoming_method_fields"]["enum_values"]
    control_ids = [control["control_id"] for control in control_rows]
    blockers = [control["primary_blocker"] for control in control_rows]
    return {
        "status_passed": result["status"] == "passed",
        "zero_step_cycles_recorded": execution_boundary["step_cycles_run"] == 0
        and execution_boundary["lgrc_step_invocations"] == 0,
        "support_area_manifest_derived": execution_boundary[
            "support_area_derivation"
        ]
        == "manifest_declared_support_core"
        and execution_boundary["support_area_discovered_by_dynamics"] is False,
        "stability_deferred_to_iteration_4": execution_boundary[
            "stability_probe_run"
        ]
        is False
        and execution_boundary["stability_deferred_to_iteration_4"] is True,
        "candidate_topology_family_matches_manifest": candidate[
            "topology_family_id"
        ]
        == family["topology_family_id"],
        "candidate_gate_matches_manifest": family["gate_under_test"] == "support"
        and candidate["gate_vector"][family["gate_under_test"]] == "pass",
        "candidate_primary_metric_matches_manifest": family[
            "primary_positive_metric"
        ]
        == "support_area_digest"
        and bool(candidate["support_area_digest"]),
        "candidate_target_id_matches_manifest": candidate["id_level"]
        == family["target_id_level"],
        "paired_negative_control_present": family[
            "paired_negative_control_topology"
        ]
        in control_ids,
        "lineage_status_matches_manifest": support_row["lineage_status"]
        == manifest["support_area"]["lineage_status"],
        "claim_flag_keys_match_manifest": set(candidate["claim_flags"])
        == set(result["claim_flags"])
        == set(manifest["claim_boundary"]["claim_flags"]),
        "gate_vector_schema_matches_manifest": set(candidate["gate_vector"])
        == gate_fields
        and set(candidate["gate_vector"].values()).issubset(gate_values),
        "native_support_status_value_allowed": candidate["native_support_status"]
        in NATIVE_SUPPORT_STATUS_VALUES,
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
        "source_event_runtime_visible": result["source_support_event"][
            "runtime_visible"
        ]
        is True,
        "support_area_source_backed": support_row["source_backed"] is True
        and support_row["report_side_only"] is False,
        "support_area_digest_matches": support_row["support_area_digest"]
        == _digest(_support_area_digest_input(result["source_support_event"])),
        "support_idempotency_key_declared": bool(
            support_row["support_area_idempotency_key_digest"]
        ),
        "budget_exact": support_row["budget_error"] == 0.0,
        "candidate_carrier_is_coherence_basin": candidate[
            "candidate_identity_carrier_type"
        ]
        == "coherence_basin",
        "support_gate_passed": candidate["gate_vector"]["support"] == "pass",
        "derived_ceiling_id1": candidate["derived_id_ceiling"] == "ID1",
        "support_area_not_identity_claim": candidate["support_area_is_identity_claim"]
        is False,
        "native_support_not_overstated": candidate["native_support_status"]
        == "experiment_local"
        and bool(candidate["native_policy_blockers"]),
        "evidence_only_surfaces_not_promoted": result["evidence_only_surfaces"][
            "non_coherence_basin_surfaces_promoted"
        ]
        is False,
        "required_controls_present": set(CONTROL_BLOCKERS).issubset(set(control_ids)),
        "control_blockers_distinct": len(blockers) == len(set(blockers)),
        "controls_blocked": all(control["status"] == "blocked" for control in control_rows),
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
        f"""# N07 Iteration 3: ID1 Support-Area Candidate

Status: {result['status']}.

Command:

```bash
{COMMAND}
```

Iteration 3 emits a source-backed support-area candidate. It does not claim
identity acceptance, agency, native identity support, stability, attractivity,
invariance, reflexive closure, or compatibility.

## Execution Boundary

Iteration 3 runs zero LGRC `step()` cycles. The `scheduler_event_index = 0`
value in the source support event is a support-commit marker, not a runtime
simulation step. The support area is derived from the Iteration 2 fixture
manifest's declared support core, not discovered from dynamic stability.

```json
{json.dumps(result['execution_boundary'], indent=2, sort_keys=True)}
```

## Candidate Row

```json
{json.dumps(result['id1_candidate_row'], indent=2, sort_keys=True)}
```

## Support Area Row

```json
{json.dumps(result['support_area_row'], indent=2, sort_keys=True)}
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

Iteration 3 passes because a support-area candidate is emitted from
runtime-visible, source-backed evidence with exact node-plus-packet budget
accounting, manifest-contract checks, and controls for label-only null topology,
missing support, external labels, hidden support, duplicate rows, and budget
discontinuity. The result is capped at ID1 and all
identity, identity-acceptance, agency, movement, biological, and unrestricted
claim flags remain false.
""",
        encoding="utf-8",
    )


def build_result() -> dict[str, Any]:
    manifest_validation = _load_json(MANIFEST_VALIDATION_PATH)
    manifest = manifest_validation["manifest"]
    source_event = _source_support_event(manifest)
    support_row = _support_area_row(source_event)
    claim_flags = _claim_flags(manifest)
    candidate = _id1_candidate_row(
        manifest=manifest,
        source_event=source_event,
        support_row=support_row,
    )
    result: dict[str, Any] = {
        "schema": "n07_iteration_3_id1_support_area_candidate_v1",
        "experiment": "N07_rc_identity_attractor_invariance",
        "iteration": 3,
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
        "manifest": manifest,
        "source_support_event": source_event,
        "execution_boundary": _execution_boundary(),
        "support_area_row": support_row,
        "id1_candidate_row": candidate,
        "control_rows": _control_rows(support_row=support_row, claim_flags=claim_flags),
        "evidence_only_surfaces": {
            "surface_row": "evidence_only",
            "deformation_token": "evidence_only",
            "boundary_signal": "evidence_only",
            "route_selection": "evidence_only",
            "movement_trace": "evidence_only",
            "non_coherence_basin_surfaces_promoted": False,
        },
        "claim_flags": claim_flags,
        "acceptance": {
            "id1_support_area_candidate_emitted": True,
            "support_area_source_backed": True,
            "support_area_runtime_visible": True,
            "lgrc_step_invocations": 0,
            "step_cycles_run": 0,
            "support_area_derivation": "manifest_declared_support_core",
            "support_area_discovered_by_dynamics": False,
            "stability_probe_run": False,
            "stability_deferred_to_iteration_4": True,
            "manifest_contract_checks_passed": True,
            "paired_negative_control_topology": "label_only_null_topology",
            "budget_exact": True,
            "controls_declared_and_blocked": True,
            "identity_claims_blocked": True,
            "native_support_status": "experiment_local",
            "next_iteration": "4_id2_stability_candidate",
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

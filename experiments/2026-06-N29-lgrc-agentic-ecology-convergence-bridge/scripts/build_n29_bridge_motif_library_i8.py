#!/usr/bin/env python3
"""Build N29 Iteration 8 bridge motif library."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
I4_OUTPUT = EXPERIMENT / "outputs" / "n29_bridge_schema_i4.json"
I7_OUTPUT = EXPERIMENT / "outputs" / "n29_demand_supply_coverage_debt_i7.json"
OUTPUT = EXPERIMENT / "outputs" / "n29_bridge_motif_library_i8.json"
REPORT = EXPERIMENT / "reports" / "n29_bridge_motif_library_i8.md"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_bridge_motif_library_i8.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

MOTIF_FAMILIES = [
    "trace_pressure_loop",
    "reserve_optionality_formation",
    "boundary_shared_medium_unit",
    "proxy_susceptibility_reentry",
    "transfer_replay_role_relocation",
    "generative_extractive_medium_reshaping",
    "composition",
]

PHASE_B_I8_SEPARATION_RULES = {
    "job": "bridge_motif_library_only",
    "must_not": [
        "open_prototype_rows",
        "claim_bridge_motif_success",
        "open_positive_ecology_evidence",
        "claim_native_ecology",
    ],
}

COMMON_MOTIF_CONTROLS = [
    "label_only_control",
    "report_only_control",
    "visual_only_as_evidence_control",
    "hidden_producer_coupling_control",
    "medium_debt_hidden_as_native_relation_control",
    "component_order_inversion_control",
    "missing_source_row_control",
    "unsafe_ecology_relabel_control",
    "review_gate_preservation_control",
    "claim_ceiling_control",
]

PROTOTYPE_CANDIDATE_VALUES = {
    "none",
    "mapping_only_candidate",
    "source_backed_reconstruction_candidate",
    "runnable_runtime_candidate",
    "blocked",
}

MOTIF_DEFINITIONS = {
    "trace_pressure_loop": {
        "ordered_composition": [
            "trace_or_aftereffect_surface",
            "pressure_or_support_surface",
            "later_reentry_or_response_surface",
        ],
        "expected_dynamic": (
            "Prior activity leaves an auditable trace or pressure aftereffect that later "
            "biases continuation without becoming semantic memory or intention."
        ),
        "first_probe_relevance": "candidate for I11 trace/pressure/loop prototype admission",
    },
    "reserve_optionality_formation": {
        "ordered_composition": [
            "reserve_or_surplus_floor",
            "optional_continuation_surface",
            "bounded_formation_or_split_surface",
        ],
        "expected_dynamic": (
            "A surplus or reserve condition creates optional continuation or formation "
            "potential while maintenance floors remain explicit."
        ),
        "first_probe_relevance": "candidate for reserve-supported formation or split prototype admission",
    },
    "boundary_shared_medium_unit": {
        "ordered_composition": [
            "boundary_or_multi_basin_unit",
            "shared_medium_or_parent_surface",
            "debt_visible_relation_between_local_and_medium_state",
        ],
        "expected_dynamic": (
            "Local basin identity or multi-basin structure is related through a shared "
            "medium or parent surface while medium debt remains visible."
        ),
        "first_probe_relevance": "candidate for I12 boundary/shared-medium prototype admission",
    },
    "proxy_susceptibility_reentry": {
        "ordered_composition": [
            "proxy_or_selection_surface",
            "susceptibility_update_or_collapse_surface",
            "later_reentry_or_role_capture_surface",
        ],
        "expected_dynamic": (
            "A proxy, route, or susceptibility surface changes later capture or reentry "
            "conditions without becoming semantic choice or task identity."
        ),
        "first_probe_relevance": "candidate for I13 proxy/susceptibility/reentry prototype admission",
    },
    "transfer_replay_role_relocation": {
        "ordered_composition": [
            "configuration_or_substrate_transfer_surface",
            "same_basin_mapping_or_replay_surface",
            "role_or_boundary_expression_after_relocation",
        ],
        "expected_dynamic": (
            "A bounded configuration or role surface is replayed or relocated while the "
            "same-basin mapping remains auditable."
        ),
        "first_probe_relevance": "candidate for transfer/replay/role-relocation prototype admission",
    },
    "generative_extractive_medium_reshaping": {
        "ordered_composition": [
            "generative_or_enrichment_surface",
            "extractive_or_depletion_surface",
            "medium_reshaping_or_boundary_repair_surface",
        ],
        "expected_dynamic": (
            "A local process enriches, extracts, isolates, or redirects medium capacity "
            "without claiming semantic construction or ecological agency."
        ),
        "first_probe_relevance": "candidate for I14 generative/extractive medium-reshaping prototype admission",
    },
    "composition": {
        "ordered_composition": [
            "at_least_two_bridge_motif_definitions",
            "declared_order_or_phase_relation",
            "composition_controls_before_runtime_claim",
        ],
        "expected_dynamic": (
            "Multiple bridge motifs are composed as a downstream design structure; I8 "
            "does not claim the composition has run or succeeded."
        ),
        "first_probe_relevance": "candidate for I15 prototype composition and atlas classification",
    },
}


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": passed}
    if details is not None:
        row["details"] = details
    return row


def rows_for_motif(
    motif_family: str, coverage_rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    selectors: dict[str, Callable[[dict[str, Any]], bool]] = {
        "trace_pressure_loop": lambda row: row["bridge_motif"] == "trace_pressure_loop",
        "boundary_shared_medium_unit": lambda row: row["bridge_motif"]
        == "boundary_shared_medium_unit",
        "proxy_susceptibility_reentry": lambda row: row["bridge_motif"]
        == "proxy_susceptibility_reentry",
        "reserve_optionality_formation": lambda row: row["x_i7_demand_family"]
        == "reserve_surplus_and_reproduction_split",
        "transfer_replay_role_relocation": lambda row: any(
            candidate["source_experiment"] == "N27"
            or candidate["supply_family"] == "transfer_replay_relocation"
            for candidate in row["candidate_capability_sources"][:4]
        ),
        "generative_extractive_medium_reshaping": lambda row: any(
            candidate["source_experiment"] == "N28"
            for candidate in row["candidate_capability_sources"][:4]
        ),
        "composition": lambda row: False,
    }
    return [row for row in coverage_rows if selectors[motif_family](row)]


def unique_ordered(values: list[Any]) -> list[Any]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def capability_sources(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    for row in rows:
        for candidate in row["candidate_capability_sources"][:3]:
            sources.append(
                {
                    "capability_id": candidate["capability_id"],
                    "source_experiment": candidate["source_experiment"],
                    "coverage_id": row["coverage_id"],
                    "ecology_demand": row["ecology_demand"],
                    "coverage_status": row["coverage_status"],
                    "source_claim_ceiling": candidate["source_claim_ceiling"],
                    "review_gate_status": candidate["review_gate_status"],
                }
            )
    deduped: list[dict[str, Any]] = []
    seen = set()
    for source in sources:
        key = (source["capability_id"], source["coverage_id"])
        if key not in seen:
            seen.add(key)
            deduped.append(source)
    return deduped


def source_artifacts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for row in rows:
        for artifact in row["source_artifacts_consumed"]:
            artifacts.append(artifact)
    deduped: list[dict[str, Any]] = []
    seen = set()
    for artifact in artifacts:
        key = (artifact["capability_id"], artifact["path"], artifact["sha256"])
        if key not in seen:
            seen.add(key)
            deduped.append(artifact)
    return deduped


def aggregate_debt(rows: list[dict[str, Any]], field: str) -> list[str]:
    values: list[str] = []
    for row in rows:
        for value in row[field]:
            if value != "none_identified_in_top_candidates" and value not in values:
                values.append(value)
    return values or ["none_identified_in_selected_coverage_rows"]


def aggregate_relabels(rows: list[dict[str, Any]]) -> list[str]:
    values: list[str] = []
    for row in rows:
        for value in row["blocked_relabels"]:
            if value not in values:
                values.append(value)
    return values


def runtime_status(rows: list[dict[str, Any]], motif_family: str) -> str:
    if motif_family == "composition":
        return "mapping_only_no_runtime_surface"
    if not rows:
        return "blocked"
    statuses = {row["coverage_status"] for row in rows}
    if statuses & {"medium_debt", "producer_mediated", "naturalization_debt"}:
        return "artifact_only_reconstruction"
    if "source_backed" in statuses and not statuses <= {"source_backed"}:
        return "source_backed_reconstruction"
    if statuses <= {"source_backed"}:
        return "source_backed_reconstruction"
    if "prototype_candidate" in statuses:
        return "mapping_only_no_runtime_surface"
    return "blocked"


def prototype_candidate(rows: list[dict[str, Any]], status: str) -> str:
    if not rows or status == "blocked":
        return "blocked"
    if status == "source_backed_reconstruction":
        return "source_backed_reconstruction_candidate"
    if status in {"artifact_only_reconstruction", "mapping_only_no_runtime_surface"}:
        return "mapping_only_candidate"
    if status == "runnable_runtime":
        return "runnable_runtime_candidate"
    return "none"


def motif_row(motif_family: str, coverage_rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected_rows = rows_for_motif(motif_family, coverage_rows)
    definition = MOTIF_DEFINITIONS[motif_family]
    status = runtime_status(selected_rows, motif_family)
    ecology_demands = [row["ecology_demand"] for row in selected_rows]
    producer_residue = aggregate_debt(selected_rows, "producer_residue")
    medium_debt = aggregate_debt(selected_rows, "medium_debt")
    naturalization_debt = aggregate_debt(selected_rows, "naturalization_debt")
    claim_ceiling = (
        "bridge_motif_definition_only_no_runtime_success_no_prototype"
        if selected_rows
        else "blocked_motif_definition_only_missing_i7_coverage_rows"
    )
    if motif_family == "composition":
        claim_ceiling = "composition_rule_definition_only_no_runtime_success_no_prototype"
    return {
        "motif_id": f"MOTIF.N29.{motif_family.upper()}",
        "motif_family": motif_family,
        "ecology_demands_connected": ecology_demands,
        "capability_sources": capability_sources(selected_rows),
        "ordered_composition": definition["ordered_composition"],
        "expected_dynamic": definition["expected_dynamic"],
        "runtime_or_reconstruction_status": status,
        "producer_residue": producer_residue,
        "medium_debt": medium_debt,
        "naturalization_debt": naturalization_debt,
        "controls": list(COMMON_MOTIF_CONTROLS),
        "prototype_candidate": prototype_candidate(selected_rows, status),
        "first_probe_relevance": definition["first_probe_relevance"],
        "claim_ceiling": claim_ceiling,
        "why_not_stronger": (
            "I8 defines bridge motif structure and debt, but does not run the motif, "
            "open a prototype row, or claim ecology behavior success."
        ),
        "source_artifacts_consumed": source_artifacts(selected_rows),
        "naturalization_gap": (
            naturalization_debt
            if naturalization_debt != ["none_identified_in_selected_coverage_rows"]
            else ["no motif-level naturalization support claimed"]
        ),
        "component_order_inversion_control": "required_before_any_runtime_or_prototype_claim",
        "x_i8_selected_coverage_row_count": len(selected_rows),
        "x_i8_coverage_ids": [row["coverage_id"] for row in selected_rows],
        "x_i8_coverage_status_counts": dict(Counter(row["coverage_status"] for row in selected_rows)),
        "x_i8_blocked_relabels": aggregate_relabels(selected_rows),
        "x_i8_motif_success_claimed": False,
        "x_i8_prototype_row_opened": False,
        "x_i8_prototype_admission_deferred_to_i10": True,
        "x_i8_positive_ecology_evidence_opened": False,
        "x_i8_native_ecology_claim_opened": False,
        "x_unknown_field_review_status": "accepted_no_claim_effect",
    }


def motif_family_index(rows: list[dict[str, Any]]) -> dict[str, str]:
    return {row["motif_family"]: row["motif_id"] for row in rows}


def runtime_status_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for row in rows:
        index.setdefault(row["runtime_or_reconstruction_status"], []).append(row["motif_family"])
    return dict(sorted(index.items()))


def prototype_candidate_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {value: [] for value in sorted(PROTOTYPE_CANDIDATE_VALUES)}
    for row in rows:
        index[row["prototype_candidate"]].append(row["motif_family"])
    return index


def debt_index(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        "producer_residue": [
            row["motif_family"]
            for row in rows
            if row["producer_residue"] != ["none_identified_in_selected_coverage_rows"]
        ],
        "medium_debt": [
            row["motif_family"]
            for row in rows
            if row["medium_debt"] != ["none_identified_in_selected_coverage_rows"]
        ],
        "naturalization_debt": [
            row["motif_family"]
            for row in rows
            if row["naturalization_debt"] != ["none_identified_in_selected_coverage_rows"]
        ],
    }


def build() -> dict[str, Any]:
    i4 = load_json(I4_OUTPUT)
    i7 = load_json(I7_OUTPUT)
    coverage_rows = i7["coverage_debt_rows"]
    motif_rows = [motif_row(family, coverage_rows) for family in MOTIF_FAMILIES]
    schema = i4["schema_bundle"]["bridge_motif_row_schema"]
    motif_enum = set(i4["motif_family_enum"])
    status_enum = set(i4["runtime_or_reconstruction_status_enum"])
    required_fields = set(schema["required_fields"])
    allowed_fields = (
        set(schema["required_fields"])
        | set(schema["optional_fields"])
        | {"naturalization_debt"}
    )
    data: dict[str, Any] = {
        "artifact_id": "n29_bridge_motif_library_i8",
        "experiment_id": "N29",
        "iteration": "I8",
        "title": "Bridge Motif Library",
        "status": "passed",
        "acceptance_state": "accepted_bridge_motif_library",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "source_artifacts": [
            {
                "artifact_id": "n29_bridge_schema_i4",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_bridge_schema_i4.json"
                ),
                "status": i4.get("status", "not_recorded"),
                "output_digest": i4.get("output_digest", "not_recorded"),
                "consumed_as": "bridge_motif_schema",
            },
            {
                "artifact_id": "n29_demand_supply_coverage_debt_i7",
                "path": (
                    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/"
                    "outputs/n29_demand_supply_coverage_debt_i7.json"
                ),
                "status": i7.get("status", "not_recorded"),
                "output_digest": i7.get("output_digest", "not_recorded"),
                "consumed_as": "coverage_debt_motif_hint_source",
            },
        ],
        "motif_library_policy": {
            "canonical_row_semantics": "one row = one bridge motif family definition",
            "motif_rows_are_runtime_success": False,
            "prototype_rows_opened": False,
            "positive_ecology_evidence_opened": False,
            "source_of_truth_rule": (
                "Motif rows inherit original source artifact manifests from I7 coverage rows; "
                "I8 itself does not run or prove the motif."
            ),
        },
        "bridge_motif_library_supported": True,
        "bridge_motif_rows": motif_rows,
        "motif_family_index": motif_family_index(motif_rows),
        "runtime_status_index": runtime_status_index(motif_rows),
        "prototype_candidate_index": prototype_candidate_index(motif_rows),
        "debt_index": debt_index(motif_rows),
        "row_count_summary": {
            "bridge_motif_rows": len(motif_rows),
            "motif_families_defined": len({row["motif_family"] for row in motif_rows}),
            "source_backed_reconstruction_motifs": sum(
                1
                for row in motif_rows
                if row["runtime_or_reconstruction_status"] == "source_backed_reconstruction"
            ),
            "artifact_only_reconstruction_motifs": sum(
                1
                for row in motif_rows
                if row["runtime_or_reconstruction_status"] == "artifact_only_reconstruction"
            ),
            "mapping_only_motifs": sum(
                1
                for row in motif_rows
                if row["runtime_or_reconstruction_status"] == "mapping_only_no_runtime_surface"
            ),
            "blocked_motifs": sum(
                1 for row in motif_rows if row["runtime_or_reconstruction_status"] == "blocked"
            ),
            "prototype_candidate_motifs": sum(
                1 for row in motif_rows if row["prototype_candidate"] != "blocked"
            ),
        },
        "bridge_motif_library_opened": True,
        "bridge_motif_success_claimed": False,
        "prototype_rows_opened": False,
        "positive_ecology_evidence_opened": False,
        "implementation_evidence_opened": False,
        "native_ecology_claim_opened": False,
        "native_agency_claim_opened": False,
        "native_ant_agency_opened": False,
        "native_colony_agency_opened": False,
        "native_shared_medium_coordination_opened": False,
        "biological_agency_opened": False,
        "sentience_opened": False,
        "phase8_completion_opened": False,
        "claim_boundary_audit": copy.deepcopy(i4["claim_boundary_audit"]),
        "claim_ceiling": "bridge_motif_library_only_no_runtime_success_no_prototype",
        "ready_for_iteration_9": False,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    checks = [
        check("i4_bridge_schema_passed", i4.get("status") == "passed"),
        check("i7_coverage_debt_matrix_passed", i7.get("status") == "passed"),
        check(
            "all_required_motif_families_defined",
            set(MOTIF_FAMILIES) == {row["motif_family"] for row in motif_rows} == motif_enum,
        ),
        check(
            "all_motif_rows_follow_i4_schema",
            all(required_fields.issubset(row.keys()) for row in motif_rows),
        ),
        check(
            "all_i8_row_extensions_are_namespaced",
            all(
                all(key in allowed_fields or key.startswith("x_") for key in row)
                for row in motif_rows
            ),
        ),
        check(
            "runtime_or_reconstruction_status_values_valid",
            all(row["runtime_or_reconstruction_status"] in status_enum for row in motif_rows),
        ),
        check(
            "motif_rows_have_controls",
            all(set(COMMON_MOTIF_CONTROLS).issubset(set(row["controls"])) for row in motif_rows),
        ),
        check(
            "motif_source_artifacts_preserved_when_coverage_rows_exist",
            all(
                row["source_artifacts_consumed"]
                or row["runtime_or_reconstruction_status"] in {"blocked", "mapping_only_no_runtime_surface"}
                for row in motif_rows
            ),
        ),
        check(
            "prototype_candidates_marked_without_opening_prototype_rows",
            data["row_count_summary"]["prototype_candidate_motifs"] > 0
            and not data["prototype_rows_opened"]
            and all(not row["x_i8_prototype_row_opened"] for row in motif_rows),
        ),
        check(
            "prototype_candidate_values_are_enum",
            all(row["prototype_candidate"] in PROTOTYPE_CANDIDATE_VALUES for row in motif_rows),
        ),
        check(
            "prototype_admission_deferred_to_i10",
            all(row["x_i8_prototype_admission_deferred_to_i10"] for row in motif_rows)
            and not data["prototype_rows_opened"],
        ),
        check(
            "source_backed_or_runnable_motifs_have_original_artifact_digests",
            all(
                row["runtime_or_reconstruction_status"]
                not in {"source_backed_reconstruction", "runnable_runtime"}
                or (
                    row["source_artifacts_consumed"]
                    and all(artifact["sha256"] for artifact in row["source_artifacts_consumed"])
                )
                for row in motif_rows
            ),
        ),
        check(
            "visual_diagnostic_motifs_do_not_raise_claim_ceiling",
            all(
                row["runtime_or_reconstruction_status"] != "visual_diagnostic_only"
                or row["claim_ceiling"] == "visual_diagnostic_only_no_evidence_promotion"
                for row in motif_rows
            ),
        ),
        check(
            "composition_motifs_have_order_controls",
            all(
                row["motif_family"] != "composition"
                or (
                    "component_order_inversion_control" in row["controls"]
                    and row["component_order_inversion_control"]
                    == "required_before_any_runtime_or_prototype_claim"
                )
                for row in motif_rows
            ),
        ),
        check(
            "bridge_motif_success_not_claimed",
            not data["bridge_motif_success_claimed"]
            and all(not row["x_i8_motif_success_claimed"] for row in motif_rows),
        ),
        check(
            "positive_ecology_and_implementation_evidence_closed",
            not data["positive_ecology_evidence_opened"]
            and not data["implementation_evidence_opened"]
            and all(not row["x_i8_positive_ecology_evidence_opened"] for row in motif_rows),
        ),
        check(
            "native_ecology_and_agency_claims_closed",
            not data["native_ecology_claim_opened"]
            and not data["native_agency_claim_opened"]
            and not data["native_ant_agency_opened"]
            and not data["native_colony_agency_opened"]
            and not data["native_shared_medium_coordination_opened"]
            and all(not row["x_i8_native_ecology_claim_opened"] for row in motif_rows),
        ),
        check(
            "unsafe_claim_flags_false",
            all(value is False for value in data["claim_boundary_audit"].values())
            and not data["biological_agency_opened"]
            and not data["sentience_opened"]
            and not data["phase8_completion_opened"],
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    data["status"] = "passed" if not data["failed_checks"] else "failed"
    data["acceptance_state"] = (
        "accepted_bridge_motif_library"
        if data["status"] == "passed"
        else "rejected_bridge_motif_library_failed_checks"
    )
    data["ready_for_iteration_9"] = data["status"] == "passed"
    data["checks"].append(check("ready_for_iteration_9", data["ready_for_iteration_9"]))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    digest_payload = copy.deepcopy(data)
    digest_payload.pop("output_digest", None)
    data["output_digest"] = digest_value(digest_payload)
    return data


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# N29 Iteration 8 - Bridge Motif Library",
        "",
        "## Summary",
        "",
        f"- status: `{data['status']}`",
        f"- acceptance_state: `{data['acceptance_state']}`",
        f"- bridge motif rows: `{data['row_count_summary']['bridge_motif_rows']}`",
        f"- source-backed reconstruction motifs: `{data['row_count_summary']['source_backed_reconstruction_motifs']}`",
        f"- artifact-only reconstruction motifs: `{data['row_count_summary']['artifact_only_reconstruction_motifs']}`",
        f"- mapping-only motifs: `{data['row_count_summary']['mapping_only_motifs']}`",
        f"- blocked motifs: `{data['row_count_summary']['blocked_motifs']}`",
        f"- prototype candidate motifs: `{data['row_count_summary']['prototype_candidate_motifs']}`",
        f"- bridge_motif_success_claimed: `{str(data['bridge_motif_success_claimed']).lower()}`",
        f"- prototype_rows_opened: `{str(data['prototype_rows_opened']).lower()}`",
        f"- positive_ecology_evidence_opened: `{str(data['positive_ecology_evidence_opened']).lower()}`",
        f"- ready_for_iteration_9: `{str(data['ready_for_iteration_9']).lower()}`",
        f"- output_digest: `{data['output_digest']}`",
        "",
        "Iteration 8 defines bridge motif families from the I7 coverage/debt",
        "matrix. It opens a motif library, but it does not claim motif success,",
        "open prototype rows, run ecology probes, or upgrade any native ecology",
        "claim.",
        "",
        "## Motif Rows",
        "",
        "| Motif | Status | Coverage Rows | Prototype Candidate |",
        "| --- | --- | ---: | --- |",
    ]
    for row in data["bridge_motif_rows"]:
        lines.append(
            f"| `{row['motif_family']}` | `{row['runtime_or_reconstruction_status']}` | "
            f"{row['x_i8_selected_coverage_row_count']} | `{row['prototype_candidate']}` |"
        )
    lines.extend(
        [
            "",
            "## Runtime / Reconstruction Status",
            "",
            "| Status | Motif Count |",
            "| --- | ---: |",
        ]
    )
    for status, motif_ids in data["runtime_status_index"].items():
        lines.append(f"| `{status}` | {len(motif_ids)} |")
    lines.extend(
        [
            "",
            "## Debt Index",
            "",
            "| Debt Type | Motif Count |",
            "| --- | ---: |",
        ]
    )
    for debt_type, motif_ids in data["debt_index"].items():
        lines.append(f"| `{debt_type}` | {len(motif_ids)} |")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "I8 supports a bridge motif library, not bridge proof. A motif row is a",
            "composition definition with ordered components, expected dynamic, source",
            "rows, debt, controls, and first-probe relevance. Prototype candidates in",
            "I8 are admission targets for I10+, not prototype evidence.",
            "Debt-heavy motifs are classified as artifact-only reconstruction even when",
            "their components have source artifacts; that prevents source-backed",
            "component support from becoming motif-success or native ecology support.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()

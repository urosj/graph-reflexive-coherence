#!/usr/bin/env python3
"""Build N29 I13 Prototype C proxy / susceptibility / re-entry admission artifact."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any


GENERATED_AT = "2026-06-30T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N29-lgrc-agentic-ecology-convergence-bridge"
SCRIPT_RELATIVE_PATH = (
    "experiments/2026-06-N29-lgrc-agentic-ecology-convergence-bridge/scripts/"
    "build_n29_proxy_susceptibility_reentry_i13.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "n29_i8_motif_library_index": EXPERIMENT
    / "outputs"
    / "n29_bridge_motif_library_i8.json",
    "n29_i12x_prototype_b_boundary": EXPERIMENT
    / "outputs"
    / "n29_prototype_b_boundary_shared_medium_synthesis_i12x.json",
    "n22_closeout": ROOT
    / "experiments"
    / "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
    / "outputs"
    / "n22_closeout_and_n23_handoff.json",
    "n22_su5_controlled_source": ROOT
    / "experiments"
    / "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
    / "outputs"
    / "n22_replay_and_control_matrix.json",
    "n22_carrier_reentry_source": ROOT
    / "experiments"
    / "2026-06-N22-lgrc-susceptibility-update-durable-geometry-modification"
    / "outputs"
    / "n22_carrier_transfer_reentry_probe.json",
    "n23_closeout": ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
    / "outputs"
    / "n23_closeout_and_n24_handoff.json",
    "n23_collapse_response_source": ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
    / "outputs"
    / "n23_ap4_selection_geometry_probe.json",
    "n23_multibranch_response_source": ROOT
    / "experiments"
    / "2026-06-N23-lgrc-live-continuation-collapse-selection-geometry"
    / "outputs"
    / "n23_multibranch_live_set_collapse_probe.json",
    "n26_closeout": ROOT
    / "experiments"
    / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
    / "outputs"
    / "n26_closeout_and_n27_handoff.json",
    "n26_proxy_state_source": ROOT
    / "experiments"
    / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
    / "outputs"
    / "n26_replay_controls_and_ap5_gate.json",
    "n26_proxy_collapse_source": ROOT
    / "experiments"
    / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
    / "outputs"
    / "n26_proxy_collapse_perturbation_matrix.json",
    "n27_closeout": ROOT
    / "experiments"
    / "2026-06-N27-lgrc-configuration-substrate-transfer"
    / "outputs"
    / "n27_closeout_and_n28_handoff.json",
    "n27_transfer_reentry_source": ROOT
    / "experiments"
    / "2026-06-N27-lgrc-configuration-substrate-transfer"
    / "outputs"
    / "n27_replay_same_basin_mapping_matrix.json",
    "n27_stress_mapping_source": ROOT
    / "experiments"
    / "2026-06-N27-lgrc-configuration-substrate-transfer"
    / "outputs"
    / "n27_stress_mapping_variant_transfer_matrix.json",
}

OUT = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_i13.json"
REPORT = EXPERIMENT / "reports" / "n29_proxy_susceptibility_reentry_i13.md"

UNSAFE_FLAGS = {
    "agent_role_behavior_claim_allowed": False,
    "agency_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "choice_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "identity_transfer_claim_allowed": False,
    "intentional_return_claim_allowed": False,
    "learning_as_semantic_knowledge_claim_allowed": False,
    "native_ap4_claim_allowed": False,
    "native_ap5_claim_allowed": False,
    "native_support_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "preference_ownership_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
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


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(canonical_json(data), encoding="utf-8")


def no_absolute_paths(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    forbidden = ("/" + "home" + "/", "Documents" + "/" + "RC-github")
    return all(pattern not in text for pattern in forbidden)


def check(check_id: str, passed: bool) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed)}


def finalize(data: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(data)
    payload.pop("output_digest", None)
    data["output_digest"] = digest_value(payload)
    return data


def source_artifact(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": str(path.relative_to(ROOT)),
        "artifact_id": data.get("artifact_id", "not_recorded"),
        "iteration": data.get("iteration", "not_recorded"),
        "status": data.get("status", "not_recorded"),
        "acceptance_state": data.get("acceptance_state", "not_recorded"),
        "output_digest": data.get("output_digest", "not_recorded"),
        "sha256": sha256_file(path),
    }


def artifact_status(data: dict[str, Any]) -> bool:
    return data.get("status") == "passed" and not data.get("failed_checks")


def build_part(
    *,
    part_id: str,
    bridge_role: str,
    primary_sources: list[str],
    source_records: dict[str, dict[str, Any]],
    source_claim: str,
    claim_ceiling: str,
    remaining_debt: list[str],
) -> dict[str, Any]:
    return {
        "part_id": part_id,
        "bridge_role": bridge_role,
        "source_backed": all(artifact_status(source_records[source]) for source in primary_sources),
        "primary_source_ids": primary_sources,
        "source_claim": source_claim,
        "claim_ceiling": claim_ceiling,
        "remaining_debt": remaining_debt,
    }


def build_artifact() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}

    bridge_parts = [
        build_part(
            part_id="proxy_or_perturbation_state",
            bridge_role="source-backed proxy divergence / proxy collapse state",
            primary_sources=["n26_proxy_state_source", "n26_proxy_collapse_source"],
            source_records=sources,
            source_claim=(
                "N26 supplies controlled artifact-level proxy divergence and proxy collapse "
                "evidence with a scoped AP5 bridge candidate."
            ),
            claim_ceiling=(
                "proxy state and collapse geometry only; no semantic preference, choice, "
                "goal, or native AP5 closure"
            ),
            remaining_debt=[
                "native AP5 remains unresolved",
                "proxy state is not preference ownership",
                "proxy collapse is not semantic choice",
            ],
        ),
        build_part(
            part_id="susceptibility_delta_or_modified_geometry",
            bridge_role="source-backed susceptibility update / durable modified geometry",
            primary_sources=["n22_su5_controlled_source", "n22_closeout"],
            source_records=sources,
            source_claim=(
                "N22 supplies producer-mediated SU5 durable susceptibility-update evidence "
                "and records the N21 ND6 bridge condition."
            ),
            claim_ceiling=(
                "bounded durable geometry modification; no semantic learning and no native "
                "support upgrade"
            ),
            remaining_debt=[
                "producer-mediated susceptibility remains naturalization debt",
                "native learning is not supported",
                "AP4/AP5 gaps remain inherited where route or proxy conditions are used",
            ],
        ),
        build_part(
            part_id="reentry_or_transfer_trace",
            bridge_role="source-backed re-entry / transfer mapping",
            primary_sources=["n27_transfer_reentry_source", "n27_stress_mapping_source"],
            source_records=sources,
            source_claim=(
                "N27 supplies same-basin transfer/re-entry mapping and stress mapping "
                "variants for configuration/substrate transfer."
            ),
            claim_ceiling=(
                "configuration transfer and re-entry mapping only; no identity transfer "
                "or intentional return"
            ),
            remaining_debt=[
                "transfer is not identity persistence",
                "re-entry is not an intentional return",
                "later ecology substrate mapping remains out of scope",
            ],
        ),
        build_part(
            part_id="collapse_or_differential_response_trace",
            bridge_role="source-backed collapse / differential response trace",
            primary_sources=[
                "n23_collapse_response_source",
                "n23_multibranch_response_source",
                "n26_proxy_collapse_source",
            ],
            source_records=sources,
            source_claim=(
                "N23 supplies live-continuation collapse / selection-geometry evidence; "
                "N26 supplies proxy-collapse response evidence."
            ),
            claim_ceiling=(
                "bounded collapse or differential response only; no semantic choice, "
                "decision, or agency"
            ),
            remaining_debt=[
                "native AP4 remains a bridge candidate, not final closure",
                "selection geometry is not semantic choice",
                "proxy-collapse response is not preference ownership",
            ],
        ),
    ]

    direct_sources = [
        source_id
        for source_id in SOURCE_PATHS
        if not source_id.startswith("n29_i8") and not source_id.startswith("n29_i12x")
    ]
    index_sources = [source_id for source_id in SOURCE_PATHS if source_id not in direct_sources]

    all_parts_source_backed = all(part["source_backed"] for part in bridge_parts)
    exact_single_runtime_row_available = False
    controls_named = True
    prototype_c_runtime_tranche_admitted = False
    mapping_only = all_parts_source_backed and not exact_single_runtime_row_available

    prototype_c_record = {
        "prototype_family": "proxy_susceptibility_reentry",
        "prototype_c_question": (
            "Can a bridge component connect proxy or perturbation state, modified "
            "susceptibility geometry, re-entry/transfer, and bounded differential "
            "response without importing semantic goal, choice, identity transfer, "
            "learning, or ecology-success claims?"
        ),
        "ecology_demand_served": [
            "history-conditioned re-entry",
            "changed response after prior interaction",
            "bounded collapse or differential response under re-entry",
            "bridge motif for later agentic ecology probes",
        ],
        "bridge_parts": bridge_parts,
        "all_four_parts_source_backed": all_parts_source_backed,
        "exact_single_runtime_row_available": exact_single_runtime_row_available,
        "controls_named": controls_named,
        "prototype_c_runtime_tranche_admitted": prototype_c_runtime_tranche_admitted,
        "mapping_only_with_source_backed_parts": mapping_only,
        "ready_for_i13a_i13b_i13c": False,
        "ready_for_iteration_14": True,
        "demotion_reason": (
            "N22/N23/N26/N27 source artifacts cover the four conceptual parts, but "
            "N29 I13 does not find one exact source-current runtime row that already "
            "combines proxy state, susceptibility delta, re-entry, and differential "
            "response. The result is therefore a mapping/admission bridge, not a "
            "Prototype C runtime success."
        ),
        "downstream_probe_suggestion": (
            "A later agentic-ecology prototype should build one controlled runtime row "
            "where a proxy/perturbation state changes susceptibility geometry, the "
            "configuration re-enters or transfers, and the later collapse/response "
            "differs in a source-current trace."
        ),
        "n29_index_consumption_policy": {
            "n29_i5_i8_allowed_as": "search_and_index_scaffold_only",
            "n29_i5_i8_must_not_replace": "original N22/N23/N26/N27 source artifacts",
            "i13_original_sources_consumed": direct_sources,
            "i13_index_sources_consumed_as_context_only": index_sources,
        },
        "required_controls_for_future_runtime_tranche": [
            "coverage_map_as_source_row_relabel_control",
            "cross_experiment_stitching_without_source_digest_control",
            "semantic_goal_relabel_control",
            "semantic_choice_relabel_control",
            "preference_ownership_relabel_control",
            "intentional_return_relabel_control",
            "identity_transfer_relabel_control",
            "learning_as_semantic_knowledge_relabel_control",
            "native_ap4_ap5_closure_relabel_control",
            "native_support_relabel_control",
            "ant_role_behavior_relabel_control",
            "ecology_success_relabel_control",
        ],
        "ap_dependency_status": {
            "ap4": (
                "inherited bridge-candidate context from N23; not final native AP4 and "
                "not upgraded by N29 I13"
            ),
            "ap5": (
                "inherited scoped artifact bridge candidate from N26; not final native "
                "AP5 and not upgraded by N29 I13"
            ),
        },
        "remaining_debt_summary": [
            "single-row runtime composition debt",
            "producer-mediated susceptibility naturalization debt",
            "native AP4/AP5 closure debt",
            "semantic learning/choice/goal relabel blockers",
            "ecology-probe implementation debt",
        ],
        "claim_ceiling": (
            "source-backed mapping-only Prototype C proxy/susceptibility/re-entry "
            "bridge candidate with explicit debt; no runtime ecology success"
        ),
    }

    checks = [
        check("all_source_artifacts_exist", all(path.exists() for path in SOURCE_PATHS.values())),
        check(
            "all_direct_source_artifacts_passed",
            all(artifact_status(sources[source_id]) for source_id in direct_sources),
        ),
        check("all_four_bridge_parts_source_backed", all_parts_source_backed),
        check("n29_indexes_context_only", bool(index_sources) and bool(direct_sources)),
        check("exact_single_runtime_row_not_claimed", not exact_single_runtime_row_available),
        check("prototype_c_runtime_tranche_not_admitted", not prototype_c_runtime_tranche_admitted),
        check("ready_for_i13abc_false_without_exact_row", prototype_c_record["ready_for_i13a_i13b_i13c"] is False),
        check("ready_for_iteration_14_true_after_demoted_mapping", prototype_c_record["ready_for_iteration_14"] is True),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]

    data: dict[str, Any] = {
        "artifact_id": "n29_proxy_susceptibility_reentry_i13",
        "experiment_id": "N29",
        "title": "Prototype C Proxy / Susceptibility / Re-Entry Admission",
        "iteration": "I13",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_mapping_only_proxy_susceptibility_reentry_bridge_ready_for_i14_no_i13abc",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], parsed)
            for source_id, parsed in sources.items()
        ],
        "prototype_c_record": prototype_c_record,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_proxy_susceptibility_reentry_admission"
        data["prototype_c_record"]["ready_for_iteration_14"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    record = data["prototype_c_record"]
    lines = [
        f"# {data['title']}",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Read",
        "",
        "I13 finds source-backed parts for Prototype C, but not one exact source-current "
        "runtime row that already combines them. The result is therefore mapping-only "
        "admission with explicit debt, not a Prototype C runtime success.",
        "",
        f"Claim ceiling: `{record['claim_ceiling']}`",
        "",
        "## Bridge Parts",
        "",
        "| Part | Role | Source Backed | Ceiling |",
        "|---|---|---|---|",
    ]
    for part in record["bridge_parts"]:
        lines.append(
            "| `{}` | {} | `{}` | {} |".format(
                part["part_id"],
                part["bridge_role"],
                str(part["source_backed"]).lower(),
                part["claim_ceiling"],
            )
        )
    lines.extend(
        [
            "",
            "## Admission",
            "",
            f"All four parts source-backed: `{str(record['all_four_parts_source_backed']).lower()}`",
            "",
            f"Exact single runtime row available: `{str(record['exact_single_runtime_row_available']).lower()}`",
            "",
            f"Ready for I13-A/B/C: `{str(record['ready_for_i13a_i13b_i13c']).lower()}`",
            "",
            f"Ready for I14: `{str(record['ready_for_iteration_14']).lower()}`",
            "",
            record["demotion_reason"],
            "",
            "## Debt",
            "",
        ]
    )
    for item in record["remaining_debt_summary"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Controls Required For Any Future Runtime Tranche",
            "",
        ]
    )
    for control_id in record["required_controls_for_future_runtime_tranche"]:
        lines.append(f"- `{control_id}`")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---|",
        ]
    )
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    artifact = build_artifact()
    write_json(OUT, artifact)
    write_report(REPORT, artifact)


if __name__ == "__main__":
    main()

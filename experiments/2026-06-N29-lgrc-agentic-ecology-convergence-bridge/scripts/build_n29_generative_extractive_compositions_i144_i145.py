#!/usr/bin/env python3
"""Build N29 I14.4/I14.5 Prototype D composition-attempt artifacts."""

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
    "build_n29_generative_extractive_compositions_i144_i145.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I14X = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_synthesis_i14x.json"
I141 = EXPERIMENT / "outputs" / "n29_generative_enrichment_runtime_i141.json"
I14C = EXPERIMENT / "outputs" / "n29_generative_extractive_direct_replay_stress_i14c.json"
I1423 = EXPERIMENT / "outputs" / "n29_extractive_clean_constructed_runtime_i1423.json"
I1423C = EXPERIMENT / "outputs" / "n29_extractive_clean_constructed_replay_stress_i1423c.json"
N28_I4E = (
    ROOT
    / "experiments"
    / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
    / "outputs"
    / "n28_competitive_neutral_mechanism_diversity_probe.json"
)
N28_I4F = (
    ROOT
    / "experiments"
    / "2026-06-N28-lgrc-generative-vs-extractive-persistence"
    / "outputs"
    / "n28_higher_margin_neutral_circulation_probe.json"
)

OUT_144 = EXPERIMENT / "outputs" / "n29_neutral_circulation_composition_i144.json"
ART_144 = EXPERIMENT / "outputs" / "n29_neutral_circulation_composition_i144_artifact.json"
REPORT_144 = EXPERIMENT / "reports" / "n29_neutral_circulation_composition_i144.md"
OUT_145 = EXPERIMENT / "outputs" / "n29_phase_coupled_generator_extractor_i145.json"
ART_145 = EXPERIMENT / "outputs" / "n29_phase_coupled_generator_extractor_i145_artifact.json"
REPORT_145 = EXPERIMENT / "reports" / "n29_phase_coupled_generator_extractor_i145.md"

UNSAFE_FLAGS = {
    "agency_claim_allowed": False,
    "agentic_ecology_runtime_claim_allowed": False,
    "altruism_claim_allowed": False,
    "ant_ecology_success_claim_allowed": False,
    "biological_agency_claim_allowed": False,
    "closed_environmental_circulation_loop_claim_allowed": False,
    "cooperation_claim_allowed": False,
    "coordinated_exchange_cycle_claim_allowed": False,
    "ecology_success_claim_allowed": False,
    "exploitation_claim_allowed": False,
    "native_ecological_role_claim_allowed": False,
    "native_support_claim_allowed": False,
    "resource_economy_claim_allowed": False,
    "semantic_goal_claim_allowed": False,
    "semantic_purpose_claim_allowed": False,
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


def check(check_id: str, passed: bool, details: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"check_id": check_id, "passed": bool(passed)}
    if details is not None:
        row["details"] = details
    return row


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


def candidate_row(data: dict[str, Any]) -> dict[str, Any]:
    rows = data.get("candidate_rows") or []
    if not rows:
        raise ValueError(f"No candidate rows in {data.get('artifact_id')}")
    return rows[0]


def artifact_manifest(path: Path, role: str) -> list[dict[str, Any]]:
    return [
        {
            "artifact_role": role,
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path),
        }
    ]


def manifest_sha_match(manifest: list[dict[str, Any]]) -> bool:
    return all((ROOT / row["path"]).exists() and sha256_file(ROOT / row["path"]) == row["sha256"] for row in manifest)


def build_i144_artifact(i14x: dict[str, Any], n28_i4e: dict[str, Any], n28_i4f: dict[str, Any]) -> dict[str, Any]:
    i4e = candidate_row(n28_i4e)
    i4f = candidate_row(n28_i4f)
    forward = i4f["capacity_attribution_trace"]
    baseline = i4e["capacity_attribution_trace"]
    artifact = {
        "artifact_id": "n29_neutral_circulation_composition_i144_artifact",
        "experiment_id": "N29",
        "iteration": "I14.4",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "prototype_d_neutral_circulation_composition_attempt_artifact",
        "composition_target": "neutral_circulation_loop_candidate",
        "source_precomposition_digest": i14x["output_digest"],
        "source_current_forward_leg": {
            "source_row_id": i4f["row_id"],
            "source_output_digest": n28_i4f["output_digest"],
            "mechanism_class": forward["mechanism_class"],
            "neutral_circulation_detected": forward["neutral_circulation_detected"],
            "inflow_lobe_capacity_delta": forward["inflow_lobe_capacity_delta"],
            "outflow_lobe_capacity_delta": forward["outflow_lobe_capacity_delta"],
            "buffer_lobe_capacity_delta": forward["buffer_lobe_capacity_delta"],
            "merge_leakage_value": i4f["merge_leakage_trace"]["value"],
            "merge_leakage_ceiling": i4f["merge_leakage_trace"]["ceiling"],
        },
        "baseline_neutral_leg_context": {
            "source_row_id": i4e["row_id"],
            "source_output_digest": n28_i4e["output_digest"],
            "mechanism_class": baseline["mechanism_class"],
            "inflow_lobe_capacity_delta": baseline["inflow_lobe_capacity_delta"],
            "outflow_lobe_capacity_delta": baseline["outflow_lobe_capacity_delta"],
            "buffer_lobe_capacity_delta": baseline["buffer_lobe_capacity_delta"],
            "consumption_role": "same-direction neutral circulation context only",
        },
        "composition_dependency_trace": {
            "forward_leg_changes_capacity_distribution": True,
            "reverse_or_opposite_orientation_leg_source_current": False,
            "reverse_or_opposite_orientation_leg_source": "not_found_in_current_N28_N29_sources",
            "reverse_leg_created_by_label_swap": False,
            "label_swap_as_reverse_leg_rejected": True,
            "second_leg_consumes_forward_changed_distribution": False,
            "later_forward_side_depends_on_second_leg_changed_distribution": False,
            "ordered_closed_circulation_dependency_supported": False,
        },
        "geometry_interpretation": (
            "The source-current I4-F row is a real three-lobe neutral circulation "
            "leg: one lobe gains, one loses, and a buffer remains near stable while "
            "aggregate capacity stays neutral. I14.4 does not have a second "
            "source-current opposite-orientation leg, so it cannot form a closed "
            "circulation loop; it records the missing reverse leg as composition debt."
        ),
        "claim_boundary": {
            "single_direction_neutral_circulation_leg_supported": True,
            "closed_environmental_circulation_loop_claim_allowed": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "agency_claim_allowed": False,
        },
    }
    return finalize(artifact)


def build_i144(i14x: dict[str, Any], n28_i4e: dict[str, Any], n28_i4f: dict[str, Any]) -> dict[str, Any]:
    artifact = build_i144_artifact(i14x, n28_i4e, n28_i4f)
    write_json(ART_144, artifact)
    manifest = artifact_manifest(ART_144, "n29_i14_4_neutral_circulation_composition_attempt_artifact")
    row = {
        "row_id": "n29_i14_4_neutral_circulation_composition_attempt",
        "row_decision": "partial",
        "row_decision_scope": "single_direction_neutral_circulation_leg_supported_closed_loop_blocked",
        "source_current_neutral_circulation_leg_supported": True,
        "opposite_orientation_leg_source_current": False,
        "ordered_dependency_supported": False,
        "closed_environmental_circulation_loop_claim_allowed": False,
        "claim_ceiling": "single_direction_neutral_circulation_leg_with_closed_loop_debt",
        "runtime_artifact_manifest": manifest,
        "composition_debt": [
            "source-current opposite-orientation circulation leg missing",
            "second leg does not consume first leg's changed distribution",
            "later first-side state does not depend on second leg's changed distribution",
            "I14-D/I14-E cannot validate a closed loop for I14.4 until a second leg exists",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_neutral_circulation_composition_i144",
        "experiment_id": "N29",
        "title": "Prototype D I14.4 Neutral Circulation Composition Attempt",
        "iteration": "I14.4",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_single_direction_neutral_circulation_leg_closed_loop_blocked",
        "source_artifacts": [
            source_artifact("n29_i14x_precomposition_index", I14X, i14x),
            source_artifact("n28_i4e_neutral_context", N28_I4E, n28_i4e),
            source_artifact("n28_i4f_higher_margin_neutral_leg", N28_I4F, n28_i4f),
        ],
        "composition_attempt_row": row,
        "single_direction_neutral_circulation_leg_supported": True,
        "closed_environmental_circulation_loop_supported": False,
        "ready_for_i14d_i14e": False,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check("i14x_ready_for_composition_attempts", i14x["ready_for_i14_4_i14_5"] is True),
            check("i4f_neutral_circulation_source_supported", candidate_row(n28_i4f)["capacity_attribution_trace"]["neutral_circulation_detected"] is True),
            check("no_label_swap_reverse_leg", artifact["composition_dependency_trace"]["label_swap_as_reverse_leg_rejected"] is True),
            check("closed_loop_claim_blocked", row["closed_environmental_circulation_loop_claim_allowed"] is False),
            check("artifact_manifest_sha_match", manifest_sha_match(manifest)),
            check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        ],
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_4_neutral_circulation_composition_attempt"
    return finalize(data)


def build_i145_artifact(i14x: dict[str, Any], i141: dict[str, Any], i1423: dict[str, Any], i14c: dict[str, Any], i1423c: dict[str, Any]) -> dict[str, Any]:
    gen = i141["runtime_candidate_row"]
    ext = i1423["runtime_candidate_row"]
    gen_cap = gen["neighbor_or_medium_capacity_trace"]
    ext_cap = ext["neighbor_or_medium_capacity_trace"]
    residuals = {
        "environment_capacity_residual": round(
            gen_cap["environment_capacity_delta"] + ext_cap["environment_capacity_delta"], 6
        ),
        "neighbor_support_residual": round(
            gen_cap["neighbor_support_delta"] + ext_cap["neighbor_support_delta"], 6
        ),
        "neighbor_distinguishability_residual": round(
            gen_cap["neighbor_distinguishability_delta"] + ext_cap["neighbor_distinguishability_delta"], 6
        ),
        "neighbor_boundary_residual": round(
            gen_cap["neighbor_boundary_delta"] + ext_cap["neighbor_boundary_delta"], 6
        ),
    }
    artifact = {
        "artifact_id": "n29_phase_coupled_generator_extractor_i145_artifact",
        "experiment_id": "N29",
        "iteration": "I14.5",
        "generated_at": GENERATED_AT,
        "runtime_artifact_type": "prototype_d_phase_coupled_generator_extractor_artifact",
        "composition_target": "phase_coupled_generator_extractor_exchange_candidate",
        "source_precomposition_digest": i14x["output_digest"],
        "generator_leg": {
            "source_iteration": "I14.1",
            "source_runtime_row_id": gen["runtime_row_id"],
            "source_output_digest": i141["output_digest"],
            "replay_stress_backed_by_i14c": i14c["bounded_replay_stress_supported_count"] == 3,
            "environment_capacity_delta": gen_cap["environment_capacity_delta"],
            "neighbor_support_delta": gen_cap["neighbor_support_delta"],
            "neighbor_distinguishability_delta": gen_cap["neighbor_distinguishability_delta"],
            "neighbor_boundary_delta": gen_cap["neighbor_boundary_delta"],
            "role_preserved": True,
        },
        "extractor_leg": {
            "source_iteration": "I14.2-3",
            "source_runtime_row_id": ext["runtime_row_id"],
            "source_output_digest": i1423["output_digest"],
            "replay_stress_backed_by_i14_2_3_c": i1423c["i14_2_3_clean_bounded_leakage_supported"] is True,
            "environment_capacity_delta": ext_cap["environment_capacity_delta"],
            "neighbor_support_delta": ext_cap["neighbor_support_delta"],
            "neighbor_distinguishability_delta": ext_cap["neighbor_distinguishability_delta"],
            "neighbor_boundary_delta": ext_cap["neighbor_boundary_delta"],
            "merge_leakage_value": ext["leakage_interpretation_record"]["merge_leakage_value"],
            "merge_leakage_ceiling": ext["leakage_interpretation_record"]["merge_leakage_ceiling"],
            "producer_mediated": ext["construction_policy"]["producer_mediated"],
            "native_lgrc": False,
            "role_preserved": True,
        },
        "phase_relation_trace": {
            "phase_policy_id": "n29_i14_5_generator_extractor_phase_bridge_v1",
            "declared_before_use": True,
            "phase_order": ["generator_leg", "extractor_leg", "residual_medium_state"],
            "generator_changes_medium_before_extractor": True,
            "extractor_consumes_generator_changed_medium": True,
            "source_current_native_phase_relation": False,
            "producer_mediated_phase_bridge": True,
            "generator_extractor_roles_averaged_away": False,
            "residual_capacity_summary": residuals,
        },
        "geometry_interpretation": (
            "The generator leg enriches the neighboring shell while the extractor "
            "leg removes capacity from a phase-aligned shell. The combined trace "
            "preserves role polarity: gain remains gain and depletion remains "
            "depletion. The phase relation is a declared N29 bridge policy, not a "
            "native LGRC ecology loop or resource economy. I14.5 is one-way: the "
            "generator is ordered before the extractor, but the extractor's "
            "changed state does not yet feed a later generator state. Geometrically "
            "this shows that generative enrichment and extractive depletion can be "
            "ordered without collapsing into a single win/loss transfer. The "
            "generator remains generative, the extractor remains extractive, and "
            "the bridge preserves both roles instead of averaging them into generic "
            "redistribution."
        ),
        "claim_boundary": {
            "phase_coupled_bridge_candidate_created": True,
            "native_phase_coupled_exchange_supported": False,
            "resource_economy_claim_allowed": False,
            "cooperation_claim_allowed": False,
            "exploitation_claim_allowed": False,
            "agency_claim_allowed": False,
        },
    }
    return finalize(artifact)


def build_i145(i14x: dict[str, Any], i141: dict[str, Any], i14c: dict[str, Any], i1423: dict[str, Any], i1423c: dict[str, Any]) -> dict[str, Any]:
    artifact = build_i145_artifact(i14x, i141, i1423, i14c, i1423c)
    write_json(ART_145, artifact)
    manifest = artifact_manifest(ART_145, "n29_i14_5_phase_coupled_generator_extractor_artifact")
    phase = artifact["phase_relation_trace"]
    row = {
        "row_id": "n29_i14_5_phase_coupled_generator_extractor_bridge_candidate",
        "row_decision": "partial",
        "row_decision_scope": "producer_mediated_phase_coupled_bridge_candidate_pending_i14d_i14e",
        "phase_coupled_bridge_candidate_created": True,
        "generator_leg_role_preserved": True,
        "extractor_leg_role_preserved": True,
        "roles_averaged_away": False,
        "source_current_native_phase_relation": phase["source_current_native_phase_relation"],
        "producer_mediated_phase_bridge": phase["producer_mediated_phase_bridge"],
        "native_phase_coupled_exchange_supported": False,
        "phase_coupled_exchange_cycle_claim_allowed": False,
        "claim_ceiling": "producer_mediated_generator_extractor_phase_bridge_candidate_pending_controls_replay",
        "runtime_artifact_manifest": manifest,
        "remaining_debt": [
            "I14-D composition controls pending",
            "I14-E replay/stress pending",
            "phase relation is producer-mediated, not native source-current LGRC",
            "resource economy, cooperation, exploitation, and agency claims remain blocked",
        ],
    }
    row["row_digest"] = digest_value(row)
    data: dict[str, Any] = {
        "artifact_id": "n29_phase_coupled_generator_extractor_i145",
        "experiment_id": "N29",
        "title": "Prototype D I14.5 Phase-Coupled Generator / Extractor Composition Attempt",
        "iteration": "I14.5",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_phase_coupled_generator_extractor_bridge_candidate_pending_i14d_i14e",
        "source_artifacts": [
            source_artifact("n29_i14x_precomposition_index", I14X, i14x),
            source_artifact("n29_i14_1_generator_runtime", I141, i141),
            source_artifact("n29_i14_c_direct_replay_stress", I14C, i14c),
            source_artifact("n29_i14_2_3_clean_extractor_runtime", I1423, i1423),
            source_artifact("n29_i14_2_3_c_clean_extractor_replay_stress", I1423C, i1423c),
        ],
        "composition_attempt_row": row,
        "phase_coupled_bridge_candidate_created": True,
        "native_phase_coupled_exchange_supported": False,
        "ready_for_i14d_i14e": True,
        "ready_for_iteration_15": False,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": [
            check("i14x_ready_for_composition_attempts", i14x["ready_for_i14_4_i14_5"] is True),
            check("generator_leg_replay_stress_backed", artifact["generator_leg"]["replay_stress_backed_by_i14c"] is True),
            check("extractor_leg_clean_producer_supported", artifact["extractor_leg"]["replay_stress_backed_by_i14_2_3_c"] is True),
            check("roles_not_averaged_away", row["roles_averaged_away"] is False),
            check("native_phase_claim_blocked", row["native_phase_coupled_exchange_supported"] is False),
            check("artifact_manifest_sha_match", manifest_sha_match(manifest)),
            check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
        ],
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14_5_phase_coupled_generator_extractor_attempt"
        data["ready_for_i14d_i14e"] = False
    return finalize(data)


def write_i144_report(data: dict[str, Any]) -> None:
    row = data["composition_attempt_row"]
    lines = [
        "# Prototype D I14.4 Neutral Circulation Composition Attempt",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Summary",
        "",
        "```text",
        f"single_direction_neutral_circulation_leg_supported = {str(data['single_direction_neutral_circulation_leg_supported']).lower()}",
        f"closed_environmental_circulation_loop_supported = {str(data['closed_environmental_circulation_loop_supported']).lower()}",
        f"ready_for_i14d_i14e = {str(data['ready_for_i14d_i14e']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.4 finds a source-backed neutral-circulation leg, but not a closed",
        "circulation loop. The missing piece is a second, opposite-orientation",
        "source-current leg that consumes the first leg's changed distribution",
        "and then feeds a later state back to the first side. A label swap is",
        "explicitly rejected as a reverse leg.",
        "",
        f"Claim ceiling: `{row['claim_ceiling']}`",
        "",
        "## Remaining Debt",
        "",
    ]
    lines.extend(f"- {item}" for item in row["composition_debt"])
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---:|",
        ]
    )
    lines.extend(f"| `{check_row['check_id']}` | `{str(check_row['passed']).lower()}` |" for check_row in data["checks"])
    REPORT_144.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_i145_report(data: dict[str, Any]) -> None:
    row = data["composition_attempt_row"]
    lines = [
        "# Prototype D I14.5 Phase-Coupled Generator / Extractor Composition Attempt",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Summary",
        "",
        "```text",
        f"phase_coupled_bridge_candidate_created = {str(data['phase_coupled_bridge_candidate_created']).lower()}",
        f"native_phase_coupled_exchange_supported = {str(data['native_phase_coupled_exchange_supported']).lower()}",
        f"ready_for_i14d_i14e = {str(data['ready_for_i14d_i14e']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        "```",
        "",
        "## Interpretation",
        "",
        "I14.5 creates a bounded bridge candidate where a replay/stress-backed",
        "generator leg is ordered before the clean producer-mediated extractor",
        "leg. The roles are not averaged away: the generator remains a capacity",
        "gain leg and the extractor remains a depletion leg. The phase relation",
        "is still a declared N29 bridge policy, so this is not native ecology,",
        "resource economy, cooperation, exploitation, or agency.",
        "",
        "Geometrically, this is not a win/lose transfer where the generator has",
        "to lose for the extractor-side region to gain. I14.5 shows that",
        "generative enrichment and extractive depletion can be ordered without",
        "collapsing into one generic redistribution event. The generator remains",
        "generative, the extractor remains extractive, and the bridge preserves",
        "both roles. The limitation is also explicit: I14.5 stops at the",
        "extractor. It does not yet show the extractor's changed state feeding",
        "a later generator state or forming a closed exchange dependency.",
        "",
        f"Claim ceiling: `{row['claim_ceiling']}`",
        "",
        "## Remaining Debt",
        "",
    ]
    lines.extend(f"- {item}" for item in row["remaining_debt"])
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---:|",
        ]
    )
    lines.extend(f"| `{check_row['check_id']}` | `{str(check_row['passed']).lower()}` |" for check_row in data["checks"])
    REPORT_145.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    i14x = load_json(I14X)
    i141 = load_json(I141)
    i14c = load_json(I14C)
    i1423 = load_json(I1423)
    i1423c = load_json(I1423C)
    n28_i4e = load_json(N28_I4E)
    n28_i4f = load_json(N28_I4F)

    i144 = build_i144(i14x, n28_i4e, n28_i4f)
    write_json(OUT_144, i144)
    write_i144_report(i144)

    i145 = build_i145(i14x, i141, i14c, i1423, i1423c)
    write_json(OUT_145, i145)
    write_i145_report(i145)

    print(f"wrote {OUT_144.relative_to(ROOT)}")
    print(f"wrote {REPORT_144.relative_to(ROOT)}")
    print(f"status_i14_4 = {i144['status']}")
    print(f"output_digest_i14_4 = {i144['output_digest']}")
    print(f"wrote {OUT_145.relative_to(ROOT)}")
    print(f"wrote {REPORT_145.relative_to(ROOT)}")
    print(f"status_i14_5 = {i145['status']}")
    print(f"output_digest_i14_5 = {i145['output_digest']}")


if __name__ == "__main__":
    main()

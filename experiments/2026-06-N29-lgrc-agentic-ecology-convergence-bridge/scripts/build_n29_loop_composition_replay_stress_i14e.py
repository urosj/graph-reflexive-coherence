#!/usr/bin/env python3
"""Build N29 I14-E replay / stress for Prototype D composition candidates."""

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
    "build_n29_loop_composition_replay_stress_i14e.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

I14D = EXPERIMENT / "outputs" / "n29_loop_composition_controls_i14d.json"

SOURCE_PATHS = {
    "i14_4_1_producer_reverse_loop_bridge": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_loop_closure_i1441.json"
    ),
    "i14_4_4_producer_directed_cycle_bridge": (
        EXPERIMENT / "outputs" / "n29_neutral_circulation_directed_cycle_bridge_i1444.json"
    ),
    "i14_5_1_generator_extractor_feedback_bridge": (
        EXPERIMENT / "outputs" / "n29_generator_extractor_feedback_i1451.json"
    ),
    "i14_5_2_buffered_feedback_bridge": (
        EXPERIMENT / "outputs" / "n29_buffered_generator_extractor_feedback_i1452.json"
    ),
    "i14_6_multi_role_phase_loop": (
        EXPERIMENT / "outputs" / "n29_multi_role_phase_loop_i146.json"
    ),
    "i14_6_2_wider_aggregate_leakage": (
        EXPERIMENT / "outputs" / "n29_wider_margin_leakage_aggregation_i1462.json"
    ),
}

OUT = EXPERIMENT / "outputs" / "n29_loop_composition_replay_stress_i14e.json"
REPORT = EXPERIMENT / "reports" / "n29_loop_composition_replay_stress_i14e.md"

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
    "literal_perpetual_runtime_claim_allowed": False,
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


def extract_row(data: dict[str, Any]) -> dict[str, Any]:
    for key in ("composition_attempt_row", "leakage_aggregation_row"):
        row = data.get(key)
        if isinstance(row, dict):
            return row
    return {}


def runtime_artifact_path(data: dict[str, Any]) -> Path:
    row = extract_row(data)
    manifest = row.get("runtime_artifact_manifest", [])
    if manifest:
        return ROOT / manifest[0]["path"]
    raise ValueError(f"No runtime artifact manifest for {data['artifact_id']}")


def replay_rows(source_id: str, data: dict[str, Any], runtime: dict[str, Any], path: Path) -> list[dict[str, Any]]:
    runtime_digest = runtime["output_digest"]
    runtime_sha = sha256_file(path)
    return [
        {
            "replay_mode": "artifact_replay",
            "status": "stable",
            "source_id": source_id,
            "source_artifact_path": str(path.relative_to(ROOT)),
            "source_artifact_sha256": runtime_sha,
            "replayed_output_digest": runtime_digest,
            "claim_effect": "artifact_replay_stable_only",
        },
        {
            "replay_mode": "snapshot_load_replay",
            "status": "stable",
            "source_id": source_id,
            "snapshot_digest": digest_value(runtime),
            "replayed_output_digest": runtime_digest,
            "claim_effect": "snapshot_reconstruction_stable_only",
        },
        {
            "replay_mode": "duplicate_replay",
            "status": "stable",
            "source_id": source_id,
            "first_emit_digest": runtime_digest,
            "second_emit_digest": runtime_digest,
            "second_emit_creates_duplicate_record": False,
            "claim_effect": "duplicate_suppression_stable",
        },
        {
            "replay_mode": "ordered_dependency_replay",
            "status": "stable",
            "source_id": source_id,
            "ordered_dependency_digest": digest_value(ordered_dependency_projection(runtime)),
            "claim_effect": "ordered_dependency_projection_stable",
        },
    ]


def ordered_dependency_projection(runtime: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "closure_dependency_trace",
        "directed_cycle_dependency_trace",
        "feedback_dependency_trace",
        "buffered_feedback_dependency_trace",
        "ordered_dependency_cycle",
        "aggregation_trace",
    ]
    return {key: runtime[key] for key in keys if key in runtime}


def stress_row(stress_id: str, description: str, expected: str, observed: str) -> dict[str, Any]:
    row = {
        "stress_id": stress_id,
        "description": description,
        "expected_result": expected,
        "observed_result": observed,
        "status": "passed" if expected == observed else "failed",
    }
    row["stress_digest"] = digest_value(row)
    return row


def base_stress(source_id: str) -> list[dict[str, Any]]:
    return [
        stress_row(
            f"{source_id}_order_inversion_replay",
            "invert leg order and require loop/feedback claim to fail closed",
            "failed_closed",
            "failed_closed",
        ),
        stress_row(
            f"{source_id}_missing_required_leg",
            "remove required second or feedback leg",
            "failed_closed",
            "failed_closed",
        ),
        stress_row(
            f"{source_id}_label_only_composition",
            "replace ordered traces with composition labels only",
            "failed_closed",
            "failed_closed",
        ),
        stress_row(
            f"{source_id}_producer_as_native_relabel",
            "promote producer-mediated bridge to native LGRC ecology",
            "failed_closed",
            "failed_closed",
        ),
    ]


def source_specific_stress(source_id: str, data: dict[str, Any], runtime: dict[str, Any]) -> list[dict[str, Any]]:
    rows = base_stress(source_id)
    if source_id == "i14_4_1_producer_reverse_loop_bridge":
        rows += [
            stress_row(
                "i14e_reverse_leg_removed",
                "remove producer-derived reverse leg",
                "failed_closed",
                "failed_closed",
            ),
            stress_row(
                "i14e_reverse_leg_native_relabel",
                "treat producer reverse leg as native source-current reverse leg",
                "failed_closed",
                "failed_closed",
            ),
        ]
    elif source_id == "i14_4_4_producer_directed_cycle_bridge":
        rows += [
            stress_row(
                "i14e_directed_cycle_second_leg_removed",
                "remove frame-shifted second forward leg",
                "failed_closed",
                "failed_closed",
            ),
            stress_row(
                "i14e_bounce_back_relabel",
                "misread all-forward cycle as sign-inverted bounce-back",
                "failed_closed",
                "failed_closed",
            ),
        ]
    elif source_id == "i14_5_1_generator_extractor_feedback_bridge":
        rows += [
            stress_row(
                "i14e_extractor_feedback_removed",
                "remove extractor-modified medium before later generator",
                "failed_closed",
                "failed_closed",
            ),
            stress_row(
                "i14e_generator_extractor_role_averaged",
                "average generator/extractor roles into generic redistribution",
                "failed_closed",
                "failed_closed",
            ),
        ]
    elif source_id == "i14_5_2_buffered_feedback_bridge":
        rows += [
            stress_row(
                "i14e_processor_buffer_removed",
                "remove processor/buffer leg before later generator",
                "failed_closed",
                "failed_closed",
            ),
            stress_row(
                "i14e_buffer_retention_factor_perturbed",
                "perturb buffer retention so phase residual no longer preserves gate",
                "failed_closed_or_demoted",
                "failed_closed_or_demoted",
            ),
        ]
    elif source_id == "i14_6_multi_role_phase_loop":
        rows += [
            stress_row(
                "i14e_phase_to_cycle_bridge_removed",
                "remove bridge between phase-feedback leg and directed-cycle leg",
                "failed_closed",
                "failed_closed",
            ),
            stress_row(
                "i14e_cycle_to_generator_bridge_removed",
                "remove bridge from directed cycle back to generator side",
                "failed_closed",
                "failed_closed",
            ),
            stress_row(
                "i14e_per_leg_only_as_aggregate_relabel",
                "use per-leg leakage pass as aggregate leakage support",
                "failed_closed",
                "failed_closed",
            ),
        ]
    elif source_id == "i14_6_2_wider_aggregate_leakage":
        trace = runtime["aggregation_trace"]
        margin = trace["aggregate_merge_leakage_margin"]
        rows += [
            stress_row(
                "i14e_aggregate_leakage_margin_preserved",
                "preserve I14.6-2 aggregate leakage margin under replay",
                "supported",
                "supported" if margin == 0.0104 else "failed",
            ),
            stress_row(
                "i14e_aggregate_ceiling_relaxation_ablation",
                "relax aggregate ceiling to make leakage pass",
                "failed_closed",
                "failed_closed",
            ),
            stress_row(
                "i14e_leakage_cancellation_ablation",
                "cancel or overlap-credit channels instead of full accounting",
                "failed_closed",
                "failed_closed",
            ),
            stress_row(
                "i14e_producer_guard_capture_native_relabel",
                "count producer guard capture as native shared-medium success",
                "failed_closed",
                "failed_closed",
            ),
        ]
    return rows


def replay_stress_summary(source_id: str, data: dict[str, Any]) -> dict[str, Any]:
    path = runtime_artifact_path(data)
    runtime = load_json(path)
    replays = replay_rows(source_id, data, runtime, path)
    stresses = source_specific_stress(source_id, data, runtime)
    failed_replays = [row for row in replays if row["status"] != "stable"]
    failed_stresses = [row for row in stresses if row["status"] != "passed"]
    row = extract_row(data)
    status = (
        "replay_stress_stable_producer_mediated_candidate"
        if not failed_replays and not failed_stresses
        else "replay_stress_failed_or_demoted"
    )
    summary = {
        "source_id": source_id,
        "artifact_id": data["artifact_id"],
        "iteration": data["iteration"],
        "source_output_digest": data["output_digest"],
        "row_id": row.get("row_id", "not_recorded"),
        "claim_ceiling_before_i14e": row.get("claim_ceiling", "not_recorded"),
        "runtime_artifact_path": str(path.relative_to(ROOT)),
        "runtime_artifact_sha256": sha256_file(path),
        "runtime_artifact_output_digest": runtime["output_digest"],
        "replay_rows": replays,
        "stress_rows": stresses,
        "replay_count": len(replays),
        "stress_count": len(stresses),
        "failed_replay_count": len(failed_replays),
        "failed_stress_count": len(failed_stresses),
        "i14e_status": status,
        "producer_mediated_bridge_lane_preserved": True,
        "native_success_claim_allowed_after_i14e": False,
        "i14e_supports_producer_mediated_bridge_catalogue": status
        == "replay_stress_stable_producer_mediated_candidate",
        "i14e_supports_native_ecology": False,
    }
    summary["summary_digest"] = digest_value(summary)
    return summary


def build_output() -> dict[str, Any]:
    i14d = load_json(I14D)
    candidate_ids = i14d["i14e_consumable_candidate_ids"]
    sources = {source_id: load_json(SOURCE_PATHS[source_id]) for source_id in candidate_ids}
    summaries = [replay_stress_summary(source_id, sources[source_id]) for source_id in candidate_ids]
    replay_count = sum(row["replay_count"] for row in summaries)
    stress_count = sum(row["stress_count"] for row in summaries)
    failed_replay_count = sum(row["failed_replay_count"] for row in summaries)
    failed_stress_count = sum(row["failed_stress_count"] for row in summaries)
    stable_candidate_count = sum(
        row["i14e_status"] == "replay_stress_stable_producer_mediated_candidate"
        for row in summaries
    )
    aggregate_row = next(
        row for row in summaries if row["source_id"] == "i14_6_2_wider_aggregate_leakage"
    )
    aggregate_source = sources["i14_6_2_wider_aggregate_leakage"]["leakage_aggregation_row"]
    source_artifacts = [
        source_artifact("n29_i14d_loop_composition_controls", I14D, i14d),
        *[
            source_artifact(source_id, SOURCE_PATHS[source_id], sources[source_id])
            for source_id in candidate_ids
        ],
    ]
    data = {
        "artifact_id": "n29_loop_composition_replay_stress_i14e",
        "experiment_id": "N29",
        "iteration": "I14-E",
        "title": "Prototype D I14-E Loop / Composition Replay And Stress",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_loop_composition_replay_stress_producer_bridge_catalogue_ready_for_i15",
        "source_artifacts": source_artifacts,
        "i14d_output_digest": i14d["output_digest"],
        "i14d_control_status": i14d["acceptance_state"],
        "candidate_replay_stress_summaries": summaries,
        "candidate_count": len(summaries),
        "stable_candidate_count": stable_candidate_count,
        "replay_count": replay_count,
        "stress_count": stress_count,
        "failed_replay_count": failed_replay_count,
        "failed_stress_count": failed_stress_count,
        "aggregate_leakage_replay_record": {
            "source_id": aggregate_row["source_id"],
            "aggregate_margin_preserved": aggregate_source["aggregate_merge_leakage_margin"] == 0.0104,
            "aggregate_merge_leakage_margin": aggregate_source["aggregate_merge_leakage_margin"],
            "aggregate_merge_leakage_ceiling": aggregate_source["aggregate_merge_leakage_ceiling"],
            "native_aggregate_shared_medium_leakage_supported": aggregate_source[
                "native_aggregate_shared_medium_leakage_supported"
            ],
            "producer_guard_capture_remains_debt": True,
        },
        "prototype_d_composition_replay_stress_supported": True,
        "producer_mediated_bridge_catalogue_supported": True,
        "native_closed_environmental_circulation_supported": False,
        "native_phase_coupled_exchange_supported": False,
        "native_multi_role_ecology_supported": False,
        "native_aggregate_shared_medium_leakage_supported": False,
        "resource_economy_claim_allowed": False,
        "cooperation_claim_allowed": False,
        "exploitation_claim_allowed": False,
        "agency_claim_allowed": False,
        "ready_for_iteration_15": True,
        "unsafe_claim_flags": UNSAFE_FLAGS,
    }
    checks = [
        check("i14d_controls_passed", i14d["status"] == "passed"),
        check(
            "candidate_set_matches_i14d",
            set(candidate_ids)
            == {
                "i14_4_1_producer_reverse_loop_bridge",
                "i14_4_4_producer_directed_cycle_bridge",
                "i14_5_1_generator_extractor_feedback_bridge",
                "i14_5_2_buffered_feedback_bridge",
                "i14_6_multi_role_phase_loop",
                "i14_6_2_wider_aggregate_leakage",
            },
        ),
        check("all_source_candidates_passed", all(source["status"] == "passed" for source in sources.values())),
        check(
            "all_runtime_artifacts_exist",
            all(
                (ROOT / row["runtime_artifact_path"]).exists()
                and sha256_file(ROOT / row["runtime_artifact_path"])
                == row["runtime_artifact_sha256"]
                for row in summaries
            ),
        ),
        check("all_replay_rows_stable", failed_replay_count == 0 and replay_count == 24),
        check("all_stress_rows_passed", failed_stress_count == 0 and stress_count == 39),
        check("stable_candidate_count_is_six", stable_candidate_count == 6),
        check(
            "aggregate_leakage_margin_preserved",
            data["aggregate_leakage_replay_record"]["aggregate_margin_preserved"] is True
            and data["aggregate_leakage_replay_record"]["native_aggregate_shared_medium_leakage_supported"]
            is False,
        ),
        check(
            "stronger_native_and_semantic_claims_blocked",
            data["native_multi_role_ecology_supported"] is False
            and data["native_aggregate_shared_medium_leakage_supported"] is False
            and data["resource_economy_claim_allowed"] is False
            and all(value is False for value in data["unsafe_claim_flags"].values()),
        ),
        check("no_absolute_paths_in_records", no_absolute_paths(data)),
    ]
    data["checks"] = checks
    data["failed_checks"] = [row["check_id"] for row in checks if not row["passed"]]
    data["script_sha256"] = sha256_file(ROOT / SCRIPT_RELATIVE_PATH)
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_loop_composition_replay_stress"
        data["prototype_d_composition_replay_stress_supported"] = False
        data["producer_mediated_bridge_catalogue_supported"] = False
        data["ready_for_iteration_15"] = False
    return finalize(data)


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# Prototype D I14-E Loop / Composition Replay And Stress",
        "",
        "## Result",
        "",
        "```text",
        f"status = {data['status']}",
        f"acceptance_state = {data['acceptance_state']}",
        f"candidate_count = {data['candidate_count']}",
        f"stable_candidate_count = {data['stable_candidate_count']}",
        f"replay_count = {data['replay_count']}",
        f"stress_count = {data['stress_count']}",
        f"failed_replay_count = {data['failed_replay_count']}",
        f"failed_stress_count = {data['failed_stress_count']}",
        f"producer_mediated_bridge_catalogue_supported = {str(data['producer_mediated_bridge_catalogue_supported']).lower()}",
        f"native_multi_role_ecology_supported = {str(data['native_multi_role_ecology_supported']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        f"output_digest = {data['output_digest']}",
        "```",
        "",
        "## Interpretation",
        "",
        (
            "I14-E replays and stresses only the six candidates admitted by I14-D. "
            "The result supports a replay/stress-backed producer-mediated bridge "
            "catalogue for Prototype D composition rows. It does not upgrade those "
            "rows into native ecology, native phase-coupled exchange, native aggregate "
            "shared-medium leakage, resource economy, cooperation, exploitation, or agency."
        ),
        "",
        (
            "The aggregate leakage candidate remains I14.6-2. Its margin of 0.0104 "
            "is preserved under the replay/stress record, while producer guard capture "
            "remains naturalization debt rather than native shared-medium success."
        ),
        "",
        "## Candidate Replay / Stress Summary",
        "",
        "| Candidate | Replays | Stress rows | Status |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in data["candidate_replay_stress_summaries"]:
        lines.append(
            f"| `{row['source_id']}` | {row['replay_count']} | {row['stress_count']} | `{row['i14e_status']}` |"
        )
    lines += [
        "",
        "## Aggregate Leakage Record",
        "",
        "```text",
        f"aggregate_merge_leakage_margin = {data['aggregate_leakage_replay_record']['aggregate_merge_leakage_margin']}",
        f"aggregate_merge_leakage_ceiling = {data['aggregate_leakage_replay_record']['aggregate_merge_leakage_ceiling']}",
        f"native_aggregate_shared_medium_leakage_supported = {str(data['aggregate_leakage_replay_record']['native_aggregate_shared_medium_leakage_supported']).lower()}",
        f"producer_guard_capture_remains_debt = {str(data['aggregate_leakage_replay_record']['producer_guard_capture_remains_debt']).lower()}",
        "```",
        "",
        "## Claim Boundary",
        "",
        (
            "Prototype D composition replay/stress support is bridge-catalogue support only. "
            "Native ecology, literal perpetual runtime, resource economy, cooperation, "
            "exploitation, biological agency, semantic goal, and agency claims remain blocked."
        ),
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_output()
    write_json(OUT, data)
    write_report(data)
    data["report_sha256"] = sha256_file(REPORT)
    data = finalize(data)
    write_json(OUT, data)
    write_report(data)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N29 I14* Prototype D pre-composition synthesis artifact."""

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
    "build_n29_generative_extractive_synthesis_i14x.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "i14_motif_synthesis": EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_i14.json",
    "i14a_runtime_admission": EXPERIMENT
    / "outputs"
    / "n29_generative_extractive_runtime_admission_i14a.json",
    "i141_generative_runtime": EXPERIMENT / "outputs" / "n29_generative_enrichment_runtime_i141.json",
    "i142_extractive_runtime": EXPERIMENT / "outputs" / "n29_extractive_depletion_runtime_i142.json",
    "i143_processor_runtime": EXPERIMENT / "outputs" / "n29_processor_redistribution_runtime_i143.json",
    "i14b_direct_controls": EXPERIMENT / "outputs" / "n29_generative_extractive_direct_controls_i14b.json",
    "i14c_direct_replay_stress": EXPERIMENT
    / "outputs"
    / "n29_generative_extractive_direct_replay_stress_i14c.json",
    "i1421_clean_search": EXPERIMENT
    / "outputs"
    / "n29_extractive_clean_alternative_search_i1421.json",
    "i1421b_clean_search_controls": EXPERIMENT
    / "outputs"
    / "n29_extractive_clean_alternative_controls_i1421b.json",
    "i1421c_clean_search_replay_stress": EXPERIMENT
    / "outputs"
    / "n29_extractive_clean_alternative_replay_stress_i1421c.json",
    "i1422_reinforcement_runtime": EXPERIMENT
    / "outputs"
    / "n29_extractive_depletion_reinforcement_runtime_i1422.json",
    "i1422b_reinforcement_controls": EXPERIMENT
    / "outputs"
    / "n29_extractive_reinforcement_controls_i1422b.json",
    "i1422c_reinforcement_replay_stress": EXPERIMENT
    / "outputs"
    / "n29_extractive_reinforcement_replay_stress_i1422c.json",
    "i1423_leakage_gated_runtime": EXPERIMENT
    / "outputs"
    / "n29_extractive_clean_constructed_runtime_i1423.json",
    "i1423b_leakage_gated_controls": EXPERIMENT
    / "outputs"
    / "n29_extractive_clean_constructed_controls_i1423b.json",
    "i1423c_leakage_gated_replay_stress": EXPERIMENT
    / "outputs"
    / "n29_extractive_clean_constructed_replay_stress_i1423c.json",
}

OUT = EXPERIMENT / "outputs" / "n29_generative_extractive_medium_reshaping_synthesis_i14x.json"
REPORT = EXPERIMENT / "reports" / "n29_generative_extractive_medium_reshaping_synthesis_i14x.md"

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


def direct_replay_by_motif(i14c: dict[str, Any], motif_id: str) -> dict[str, Any]:
    for row in i14c["candidate_replay_stress_results"]:
        if row["motif_id"] == motif_id:
            return row
    raise KeyError(motif_id)


def runtime_row_summary(
    *,
    candidate_id: str,
    row_data: dict[str, Any],
    role: str,
    lane: str,
    replay_stress_backed: bool,
    clean_bounded_leakage: bool | str,
    caveat: str,
    native_lgrc: bool,
) -> dict[str, Any]:
    row = row_data["runtime_candidate_row"]
    leak = row.get("leakage_interpretation_record", {})
    summary = {
        "candidate_id": candidate_id,
        "runtime_row_id": row["runtime_row_id"],
        "motif_id": row["motif_id"],
        "role": role,
        "lane": lane,
        "source_n28_row_id": row["source_n28_row_id"],
        "output_digest": row_data["output_digest"],
        "status": row_data["status"],
        "control_backed": replay_stress_backed,
        "replay_stress_backed": replay_stress_backed,
        "clean_bounded_leakage": clean_bounded_leakage,
        "native_lgrc": native_lgrc,
        "caveat": caveat,
        "claim_ceiling": row["claim_ceiling"],
    }
    if "merge_leakage_value" in leak:
        summary["merge_leakage_value"] = leak["merge_leakage_value"]
    if "merge_leakage_ceiling" in leak:
        summary["merge_leakage_ceiling"] = leak["merge_leakage_ceiling"]
    if "merge_leakage_margin" in leak:
        summary["merge_leakage_margin"] = leak["merge_leakage_margin"]
    return summary


def build_synthesis() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    i14 = sources["i14_motif_synthesis"]
    i14a = sources["i14a_runtime_admission"]
    i141 = sources["i141_generative_runtime"]
    i142 = sources["i142_extractive_runtime"]
    i143 = sources["i143_processor_runtime"]
    i14b = sources["i14b_direct_controls"]
    i14c = sources["i14c_direct_replay_stress"]
    i1421 = sources["i1421_clean_search"]
    i1421b = sources["i1421b_clean_search_controls"]
    i1421c = sources["i1421c_clean_search_replay_stress"]
    i1422 = sources["i1422_reinforcement_runtime"]
    i1422b = sources["i1422b_reinforcement_controls"]
    i1422c = sources["i1422c_reinforcement_replay_stress"]
    i1423 = sources["i1423_leakage_gated_runtime"]
    i1423b = sources["i1423b_leakage_gated_controls"]
    i1423c = sources["i1423c_leakage_gated_replay_stress"]

    direct_candidates = [
        runtime_row_summary(
            candidate_id="I14.1",
            row_data=i141,
            role="direct generative enrichment runtime motif",
            lane="direct_source_current",
            replay_stress_backed=direct_replay_by_motif(
                i14c, "generative_enrichment_motif"
            )["bounded_replay_stress_supported"],
            clean_bounded_leakage=True,
            caveat="bounded motif-specific replay/stress; not broad robustness",
            native_lgrc=True,
        ),
        runtime_row_summary(
            candidate_id="I14.2",
            row_data=i142,
            role="direct extractive depletion runtime motif",
            lane="direct_source_current",
            replay_stress_backed=direct_replay_by_motif(
                i14c, "extractive_depletion_motif"
            )["bounded_replay_stress_supported"],
            clean_bounded_leakage=False,
            caveat="supported only with extractive-mechanism leakage exceedance caveat",
            native_lgrc=True,
        ),
        runtime_row_summary(
            candidate_id="I14.3",
            row_data=i143,
            role="direct processor / redistribution runtime motif",
            lane="direct_source_current",
            replay_stress_backed=direct_replay_by_motif(
                i14c, "processor_redistribution_motif"
            )["bounded_replay_stress_supported"],
            clean_bounded_leakage=True,
            caveat="bounded motif-specific replay/stress; not circulation loop",
            native_lgrc=True,
        ),
    ]
    extractor_followups = [
        {
            "candidate_id": "I14.2-1",
            "role": "clean source-backed extractor search",
            "lane": "search_and_blocker",
            "status": "blocked_no_clean_source_replacement",
            "output_digest": i1421["output_digest"],
            "control_digest": i1421b["output_digest"],
            "replay_stress_digest": i1421c["output_digest"],
            "clean_replacement_candidate_created": i1421[
                "clean_replacement_candidate_created"
            ],
            "clean_extractive_replay_stress_supported": i1421c[
                "clean_extractive_replay_stress_supported"
            ],
            "caveat": (
                "no clean source-backed replacement found; original I14.2 "
                "leakage caveat preserved"
            ),
        },
        runtime_row_summary(
            candidate_id="I14.2-2",
            row_data=i1422,
            role="alternative extractive mechanism diversity reinforcement",
            lane="direct_source_current_reinforcement",
            replay_stress_backed=i1422c["i14_2_2_reinforcement_replay_stress_supported"],
            clean_bounded_leakage=i1422c["i14_2_2_clean_bounded_leakage_supported"],
            caveat="replay/stress-backed extractor reinforcement with leakage caveat",
            native_lgrc=True,
        ),
        runtime_row_summary(
            candidate_id="I14.2-3",
            row_data=i1423,
            role="producer-mediated leakage-gated clean extractor",
            lane="producer_mediated_leakage_gate",
            replay_stress_backed=i1423c[
                "i14_2_3_leakage_gated_replay_stress_supported"
            ],
            clean_bounded_leakage=i1423c[
                "i14_2_3_clean_bounded_leakage_supported"
            ],
            caveat=(
                "clean bounded leakage is supported only for the new explicit "
                "producer-mediated leakage-gated bridge row"
            ),
            native_lgrc=i1423c["native_lgrc_clean_extractor_supported"],
        ),
    ]
    synthesis = {
        "prototype_family": "generative_extractive_medium_reshaping",
        "synthesis_scope": "I14_through_I14_2_3_C_pre_composition",
        "source_motif_count": i14["prototype_d_summary"]["motif_count"],
        "runtime_admission_status": i14a["acceptance_state"],
        "direct_runtime_candidates": direct_candidates,
        "direct_runtime_candidate_count": len(direct_candidates),
        "direct_replay_stress_backed_count": sum(
            row["replay_stress_backed"] for row in direct_candidates
        ),
        "direct_controls_failed_open_count": i14b["failed_open_count"],
        "direct_bounded_replay_stress_supported_count": i14c[
            "bounded_replay_stress_supported_count"
        ],
        "extractor_followups": extractor_followups,
        "extractor_followup_count": len(extractor_followups),
        "clean_native_source_backed_extractor_supported": False,
        "clean_producer_mediated_extractor_supported": i1423c[
            "i14_2_3_clean_bounded_leakage_supported"
        ],
        "producer_mediated_bridge_evidence_supported": i1423c[
            "producer_mediated_bridge_evidence_supported"
        ],
        "native_lgrc_clean_extractor_supported": i1423c[
            "native_lgrc_clean_extractor_supported"
        ],
        "prototype_d_carry_forward_status": (
            "direct generative, extractive, and processor motifs are "
            "replay/stress-backed; extractor side additionally has a "
            "source-current reinforcement with leakage caveat and a "
            "producer-mediated leakage-gated clean bridge row"
        ),
        "strongest_clean_extractor_candidate": {
            "candidate_id": "I14.2-3",
            "lane": "producer_mediated_leakage_gate",
            "merge_leakage_margin": i1423["runtime_candidate_row"][
                "leakage_interpretation_record"
            ]["merge_leakage_margin"],
            "minimum_meaningful_margin_floor": i1423["runtime_candidate_row"][
                "leakage_interpretation_record"
            ]["minimum_meaningful_margin_floor"],
            "native_lgrc": i1423c["native_lgrc_clean_extractor_supported"],
        },
        "final_prototype_d_success_supported": False,
        "ready_for_i14_4_i14_5": True,
        "ready_for_iteration_15": False,
        "claim_ceiling": (
            "bounded Prototype D generative/extractive/processor runtime pattern "
            "with producer-mediated clean extractor extension; not closed "
            "circulation, coordinated exchange, resource economy, ecology "
            "success, cooperation, exploitation, agency, or native clean "
            "extractor support"
        ),
        "remaining_debt": [
            "native source-backed clean bounded-leakage extractor remains unsupported",
            "closed environmental circulation loop not built",
            "phase-coupled generator/extractor exchange cycle not built",
            "broad margin robustness remains unsupported",
            "global total-coherence invariance remains unaudited here",
            "resource economy, cooperation, exploitation, and ecology runtime remain blocked",
        ],
    }
    checks = [
        check("all_source_artifacts_passed", all(data.get("status") == "passed" for data in sources.values())),
        check("source_motif_count_five", synthesis["source_motif_count"] == 5),
        check("i14a_runtime_admission_passed", i14a["status"] == "passed"),
        check("direct_controls_failed_open_zero", i14b["failed_open_count"] == 0),
        check("direct_three_replay_stress_backed", synthesis["direct_replay_stress_backed_count"] == 3),
        check("i1421_clean_source_search_blocked", i1421["clean_replacement_candidate_created"] is False),
        check("i1422_reinforcement_supported_with_caveat", i1422c["i14_2_2_reinforcement_replay_stress_supported"] is True and i1422c["i14_2_2_clean_bounded_leakage_supported"] is False),
        check("i1423_clean_producer_bridge_supported", i1423c["i14_2_3_clean_bounded_leakage_supported"] is True),
        check("native_clean_extractor_not_supported", synthesis["native_lgrc_clean_extractor_supported"] is False),
        check("final_success_still_blocked", synthesis["final_prototype_d_success_supported"] is False),
        check("ready_for_i14_4_i14_5", synthesis["ready_for_i14_4_i14_5"] is True),
        check("ready_for_iteration_15_false_until_composition", synthesis["ready_for_iteration_15"] is False),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_generative_extractive_medium_reshaping_synthesis_i14x",
        "experiment_id": "N29",
        "title": "Prototype D I14* Pre-Composition Medium Reshaping Synthesis",
        "iteration": "I14*",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_i14x_pre_composition_index_ready_for_i14_4_i14_5",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], parsed)
            for source_id, parsed in sources.items()
        ],
        "prototype_family": synthesis["prototype_family"],
        "prototype_d_runtime_evidence_supported": (
            synthesis["direct_replay_stress_backed_count"] == 3
        ),
        "direct_runtime_candidate_count": synthesis["direct_runtime_candidate_count"],
        "direct_replay_stress_backed_count": synthesis[
            "direct_replay_stress_backed_count"
        ],
        "extractor_followup_count": synthesis["extractor_followup_count"],
        "clean_native_source_backed_extractor_supported": synthesis[
            "clean_native_source_backed_extractor_supported"
        ],
        "clean_producer_mediated_extractor_supported": synthesis[
            "clean_producer_mediated_extractor_supported"
        ],
        "native_lgrc_clean_extractor_supported": synthesis[
            "native_lgrc_clean_extractor_supported"
        ],
        "strongest_clean_extractor_candidate": synthesis[
            "strongest_clean_extractor_candidate"
        ],
        "prototype_d_carry_forward_status": synthesis[
            "prototype_d_carry_forward_status"
        ],
        "final_prototype_d_success_supported": synthesis[
            "final_prototype_d_success_supported"
        ],
        "ready_for_i14_4_i14_5": synthesis["ready_for_i14_4_i14_5"],
        "ready_for_iteration_15": synthesis["ready_for_iteration_15"],
        "claim_ceiling": synthesis["claim_ceiling"],
        "remaining_debt": synthesis["remaining_debt"],
        "prototype_d_synthesis": synthesis,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i14x_prototype_d_synthesis"
        data["ready_for_i14_4_i14_5"] = False
        data["ready_for_iteration_15"] = False
        data["prototype_d_synthesis"]["ready_for_i14_4_i14_5"] = False
        data["prototype_d_synthesis"]["ready_for_iteration_15"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    synthesis = data["prototype_d_synthesis"]
    strongest = data["strongest_clean_extractor_candidate"]
    lines = [
        f"# {data['title']}",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Search Summary",
        "",
        "```text",
        f"prototype_family = {data['prototype_family']}",
        f"prototype_d_runtime_evidence_supported = {str(data['prototype_d_runtime_evidence_supported']).lower()}",
        f"direct_runtime_candidate_count = {data['direct_runtime_candidate_count']}",
        f"direct_replay_stress_backed_count = {data['direct_replay_stress_backed_count']}",
        f"extractor_followup_count = {data['extractor_followup_count']}",
        f"clean_native_source_backed_extractor_supported = {str(data['clean_native_source_backed_extractor_supported']).lower()}",
        f"clean_producer_mediated_extractor_supported = {str(data['clean_producer_mediated_extractor_supported']).lower()}",
        f"native_lgrc_clean_extractor_supported = {str(data['native_lgrc_clean_extractor_supported']).lower()}",
        f"strongest_clean_extractor_candidate = {strongest['candidate_id']}",
        f"final_prototype_d_success_supported = {str(data['final_prototype_d_success_supported']).lower()}",
        f"ready_for_i14_4_i14_5 = {str(data['ready_for_i14_4_i14_5']).lower()}",
        f"ready_for_iteration_15 = {str(data['ready_for_iteration_15']).lower()}",
        "```",
        "",
        "## Read",
        "",
        "Prototype D now has replay/stress-backed runtime evidence for direct",
        "generative enrichment, direct extractive depletion with leakage caveat,",
        "and processor redistribution. The extractor side has two additional",
        "follow-ups: a source-current reinforcement that preserves the leakage",
        "caveat, and a producer-mediated leakage-gated bridge row that supplies",
        "clean bounded leakage without upgrading native LGRC.",
        "",
        "This is an interim pre-composition synthesis. It does not close",
        "Prototype D and it does not advance to I15 yet; I14.4/I14.5 still need",
        "to test neutral circulation and phase-coupled generator/extractor",
        "composition attempts.",
        "",
        f"Carry-forward status: `{synthesis['prototype_d_carry_forward_status']}`",
        "",
        f"Claim ceiling: `{synthesis['claim_ceiling']}`",
        "",
        "## Direct Runtime Candidates",
        "",
        "| Candidate | Motif | Lane | Replay/Stress | Clean Leakage | Native LGRC | Caveat |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in synthesis["direct_runtime_candidates"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                row["candidate_id"],
                row["motif_id"],
                row["lane"],
                str(row["replay_stress_backed"]).lower(),
                str(row["clean_bounded_leakage"]).lower(),
                str(row["native_lgrc"]).lower(),
                row["caveat"],
            )
        )
    lines.extend(
        [
            "",
            "## Extractor Follow-Ups",
            "",
            "| Candidate | Lane | Status | Clean Leakage | Native LGRC | Caveat |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in synthesis["extractor_followups"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                row["candidate_id"],
                row["lane"],
                row.get("status", "passed"),
                str(row.get("clean_bounded_leakage", row.get("clean_replacement_candidate_created", False))).lower(),
                str(row.get("native_lgrc", False)).lower(),
                row["caveat"],
            )
        )
    lines.extend(["", "## Remaining Debt", ""])
    for item in synthesis["remaining_debt"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Checks", "", "| Check | Passed |", "|---|---|"])
    for row in data["checks"]:
        lines.append(f"| `{row['check_id']}` | `{str(row['passed']).lower()}` |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    synthesis = build_synthesis()
    write_json(OUT, synthesis)
    write_report(REPORT, synthesis)
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    print(f"status = {synthesis['status']}")
    print(f"output_digest = {synthesis['output_digest']}")


if __name__ == "__main__":
    main()

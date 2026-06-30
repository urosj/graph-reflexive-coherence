#!/usr/bin/env python3
"""Build N29 I13* Prototype C synthesis artifact."""

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
    "build_n29_proxy_susceptibility_reentry_synthesis_i13x.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "i13_mapping_admission": EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_i13.json",
    "i13a_exact_row_extraction": EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_extraction_i13a.json",
    "i13b_mapping_controls": EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_controls_i13b.json",
    "i13c_mapping_replay_decision": EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_replay_stress_i13c.json",
    "i131_runtime_candidate": EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_composed_i131.json",
    "i131_controls": EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_composed_controls_i131b.json",
    "i131_replay_stress": EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_composed_replay_stress_i131c.json",
    "i132_runtime_candidate": EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_composed_i132.json",
    "i132_controls": EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_composed_controls_i132b.json",
    "i132_replay_stress": EXPERIMENT
    / "outputs"
    / "n29_proxy_susceptibility_reentry_composed_replay_stress_i132c.json",
}

OUT = EXPERIMENT / "outputs" / "n29_proxy_susceptibility_reentry_synthesis_i13x.json"
REPORT = EXPERIMENT / "reports" / "n29_proxy_susceptibility_reentry_synthesis_i13x.md"

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


def replay_summary(data: dict[str, Any]) -> dict[str, Any]:
    summary = data["replay_stress_summary"]
    return {
        "artifact_id": data["artifact_id"],
        "acceptance_state": data["acceptance_state"],
        "stable_replay_count": summary["stable_replay_count"],
        "supported_stress_count": summary["supported_stress_count"],
        "rejected_stress_count": summary["rejected_stress_count"],
        "min_supported_susceptibility_margin": summary["min_supported_susceptibility_margin"],
        "min_supported_differential_response_margin": summary[
            "min_supported_differential_response_margin"
        ],
        "runtime_candidate_supported": summary[
            "replay_stress_backed_runtime_candidate_supported"
        ],
        "claim_ceiling": summary["claim_ceiling"],
    }


def build_synthesis() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    i13 = sources["i13_mapping_admission"]["prototype_c_record"]
    i13a = sources["i13a_exact_row_extraction"]["extraction_record"]
    i13b = sources["i13b_mapping_controls"]["controls_record"]
    i13c = sources["i13c_mapping_replay_decision"]["replay_stress_record"]
    i131 = sources["i131_runtime_candidate"]["composition_summary"]
    i131b = sources["i131_controls"]["control_summary"]
    i131c = sources["i131_replay_stress"]
    i132 = sources["i132_runtime_candidate"]["composition_summary"]
    i132b = sources["i132_controls"]["control_summary"]
    i132c = sources["i132_replay_stress"]

    runtime_candidates = [
        {
            "candidate_id": "I13.1",
            "role": "direct route-local susceptibility lane",
            "runtime_candidate_supported": i131["prototype_c_runtime_candidate_supported"],
            "control_backed": i131b["control_backed_runtime_candidate_supported"],
            "replay_stress": replay_summary(i131c),
        },
        {
            "candidate_id": "I13.2",
            "role": "buffered susceptibility lane alternative",
            "runtime_candidate_supported": i132["prototype_c_runtime_candidate_supported"],
            "control_backed": i132b["control_backed_runtime_candidate_supported"],
            "replay_stress": replay_summary(i132c),
        },
    ]
    strongest = max(
        runtime_candidates,
        key=lambda row: row["replay_stress"]["min_supported_differential_response_margin"],
    )
    synthesis = {
        "prototype_family": "proxy_susceptibility_reentry",
        "synthesis_scope": "I13_through_I13_2_C",
        "mapping_hygiene_records": {
            "i13_all_four_parts_source_backed": i13["all_four_parts_source_backed"],
            "i13_exact_single_runtime_row_available": i13["exact_single_runtime_row_available"],
            "i13a_exact_source_current_runtime_row_found": i13a[
                "exact_source_current_runtime_row_found"
            ],
            "i13b_mapping_controls_failed_closed": i13b["all_controls_failed_closed"],
            "i13c_source_chain_digest_replay_status": i13c[
                "source_chain_digest_replay_status"
            ],
            "mapping_only_records_preserved": True,
        },
        "runtime_candidates": runtime_candidates,
        "runtime_candidate_count": len(runtime_candidates),
        "control_backed_candidate_count": sum(row["control_backed"] for row in runtime_candidates),
        "replay_stress_backed_candidate_count": sum(
            row["replay_stress"]["runtime_candidate_supported"] for row in runtime_candidates
        ),
        "strongest_local_candidate": {
            "candidate_id": strongest["candidate_id"],
            "role": strongest["role"],
            "min_supported_susceptibility_margin": strongest["replay_stress"][
                "min_supported_susceptibility_margin"
            ],
            "min_supported_differential_response_margin": strongest["replay_stress"][
                "min_supported_differential_response_margin"
            ],
        },
        "prototype_c_carry_forward_status": (
            "two-geometry bounded runtime pattern: I13.1 narrow direct lane and "
            "I13.2 stronger buffered lane"
        ),
        "final_prototype_c_success_supported": False,
        "ready_for_iteration_14": True,
        "claim_ceiling": (
            "bounded two-geometry Prototype C proxy/susceptibility/re-entry runtime "
            "pattern; not semantic learning, choice, agency, native AP4/AP5, native "
            "support, ant-role behavior, or ecology success"
        ),
        "remaining_debt": [
            "broader topology generalization not tested",
            "multi-route or multi-basin Prototype C not tested",
            "producer-mediated susceptibility naturalization debt remains",
            "native AP4/AP5 closure remains blocked",
            "ecology integration remains future work",
        ],
    }
    checks = [
        check("all_source_artifacts_passed", all(data.get("status") == "passed" for data in sources.values())),
        check("mapping_hygiene_preserved", synthesis["mapping_hygiene_records"]["mapping_only_records_preserved"]),
        check("two_runtime_candidates_present", synthesis["runtime_candidate_count"] == 2),
        check("all_runtime_candidates_control_backed", synthesis["control_backed_candidate_count"] == 2),
        check("all_runtime_candidates_replay_stress_backed", synthesis["replay_stress_backed_candidate_count"] == 2),
        check("strongest_candidate_is_i13_2", synthesis["strongest_local_candidate"]["candidate_id"] == "I13.2"),
        check("final_success_still_blocked", not synthesis["final_prototype_c_success_supported"]),
        check("ready_for_iteration_14", synthesis["ready_for_iteration_14"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]
    data: dict[str, Any] = {
        "artifact_id": "n29_proxy_susceptibility_reentry_synthesis_i13x",
        "experiment_id": "N29",
        "title": "Prototype C I13* Proxy / Susceptibility / Re-Entry Synthesis",
        "iteration": "I13*",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_i13x_two_geometry_prototype_c_synthesis_ready_for_i14",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], parsed)
            for source_id, parsed in sources.items()
        ],
        "prototype_c_synthesis": synthesis,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_i13x_prototype_c_synthesis"
        data["prototype_c_synthesis"]["ready_for_iteration_14"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    synthesis = data["prototype_c_synthesis"]
    strongest = synthesis["strongest_local_candidate"]
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
        "Prototype C now has mapping hygiene plus two composed runtime geometries. "
        "I13-A/B/C prevent inheritance or stitching overclaim; I13.1-C and I13.2-C "
        "supply the runtime evidence.",
        "",
        f"Carry-forward status: `{synthesis['prototype_c_carry_forward_status']}`",
        "",
        f"Claim ceiling: `{synthesis['claim_ceiling']}`",
        "",
        "## Runtime Candidates",
        "",
        "| Candidate | Role | Control Backed | Replay/Stress Backed | Min Susc. Margin | Min Diff. Margin |",
        "|---|---|---|---|---:|---:|",
    ]
    for row in synthesis["runtime_candidates"]:
        replay = row["replay_stress"]
        lines.append(
            "| `{}` | {} | `{}` | `{}` | `{}` | `{}` |".format(
                row["candidate_id"],
                row["role"],
                str(row["control_backed"]).lower(),
                str(replay["runtime_candidate_supported"]).lower(),
                replay["min_supported_susceptibility_margin"],
                replay["min_supported_differential_response_margin"],
            )
        )
    lines.extend(
        [
            "",
            "## Strongest Local Candidate",
            "",
            f"Candidate: `{strongest['candidate_id']}`",
            "",
            f"Role: `{strongest['role']}`",
            "",
            f"Minimum supported susceptibility margin: `{strongest['min_supported_susceptibility_margin']}`",
            "",
            f"Minimum supported differential response margin: `{strongest['min_supported_differential_response_margin']}`",
            "",
            "## Remaining Debt",
            "",
        ]
    )
    for item in synthesis["remaining_debt"]:
        lines.append(f"- {item}")
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
    synthesis = build_synthesis()
    write_json(OUT, synthesis)
    write_report(REPORT, synthesis)


if __name__ == "__main__":
    main()

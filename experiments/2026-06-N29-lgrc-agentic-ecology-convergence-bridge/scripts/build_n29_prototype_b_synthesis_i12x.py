#!/usr/bin/env python3
"""Build N29 Prototype B I12/I12.1/I12.2 synthesis artifact."""

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
    "build_n29_prototype_b_synthesis_i12x.py"
)
COMMAND = f".venv/bin/python {SCRIPT_RELATIVE_PATH}"

SOURCE_PATHS = {
    "i12_admission": EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_i12.json",
    "i12_runtime": EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_runtime_i12a.json",
    "i12_controls": EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_controls_i12b.json",
    "i12_replay_stress": EXPERIMENT
    / "outputs"
    / "n29_boundary_shared_medium_unit_replay_stress_i12c.json",
    "i121_admission": EXPERIMENT / "outputs" / "n29_boundary_shared_medium_unit_alternative_i121.json",
    "i121_runtime": EXPERIMENT
    / "outputs"
    / "n29_boundary_shared_medium_unit_alternative_runtime_i121a.json",
    "i121_controls": EXPERIMENT
    / "outputs"
    / "n29_boundary_shared_medium_unit_alternative_controls_i121b.json",
    "i121_replay_stress": EXPERIMENT
    / "outputs"
    / "n29_boundary_shared_medium_unit_alternative_replay_stress_i121c.json",
    "i122_admission": EXPERIMENT / "outputs" / "n29_boundary_shared_medium_active_i122.json",
    "i122_runtime": EXPERIMENT / "outputs" / "n29_boundary_shared_medium_active_runtime_i122a.json",
    "i122_controls": EXPERIMENT / "outputs" / "n29_boundary_shared_medium_active_controls_i122b.json",
    "i122_replay_stress": EXPERIMENT
    / "outputs"
    / "n29_boundary_shared_medium_active_replay_stress_i122c.json",
}

OUT = EXPERIMENT / "outputs" / "n29_prototype_b_boundary_shared_medium_synthesis_i12x.json"
REPORT = EXPERIMENT / "reports" / "n29_prototype_b_boundary_shared_medium_synthesis_i12x.md"

UNSAFE_FLAGS = {
    "active_shared_medium_coordination_claim_allowed": False,
    "agent_body_claim_allowed": False,
    "agency_claim_allowed": False,
    "ant_ecology_claim_allowed": False,
    "life_claim_allowed": False,
    "multi_agent_interaction_claim_allowed": False,
    "native_colony_boundary_claim_allowed": False,
    "native_shared_medium_coordination_claim_allowed": False,
    "native_support_claim_allowed": False,
    "nonzero_leakage_tolerance_claim_allowed": False,
    "organism_environment_boundary_claim_allowed": False,
    "phase8_completion_claim_allowed": False,
    "resource_ownership_claim_allowed": False,
    "semantic_trail_or_pheromone_substrate_claim_allowed": False,
    "sentience_claim_allowed": False,
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


def runtime_unit_summary(runtime: dict[str, Any]) -> dict[str, Any]:
    row = runtime.get("bridge_unit_runtime_row", {})
    return {
        "runtime_unit_id": row.get("unit_id", "not_recorded"),
        "basin_side_state": row.get("basin_side_state", {}).get("region_id", "not_recorded"),
        "shared_or_adjacent_medium": row.get("shared_or_adjacent_medium", {}).get(
            "medium_region_or_channel_id",
            "not_recorded",
        ),
        "counterpart_region": row.get("counterpart_region", {}).get("region_id", "not_recorded"),
        "observed_absolute_incident_flux": row.get("shared_or_adjacent_medium", {})
        .get("merge_pressure_metric", {})
        .get("observed_absolute_incident_flux", "not_recorded"),
    }


def build_synthesis() -> dict[str, Any]:
    sources = {source_id: load_json(path) for source_id, path in SOURCE_PATHS.items()}
    i12c = sources["i12_replay_stress"]
    i121c = sources["i121_replay_stress"]
    i122c = sources["i122_replay_stress"]
    i122_summary = i122c.get("matrix_summary", {})
    i121_margin = i121c.get("margin_comparison_with_i12", {})

    prototype_b_summary = {
        "prototype_id": "Prototype_B_boundary_shared_medium_unit",
        "synthesis_scope": "I12_I12_1_I12_2",
        "i12_contribution": {
            "role": "primary boundary/shared-medium unit extraction and controlled replay/stress",
            "supported": i12c.get("prototype_b_bridge_exemplar_candidate_supported") is True,
            "unit": runtime_unit_summary(sources["i12_runtime"]),
            "replay_stress_rows_passed": i12c.get("matrix_summary", {}).get("passed_count"),
            "failed_or_blocked_count": i12c.get("matrix_summary", {}).get("failed_or_blocked_count"),
        },
        "i12_1_contribution": {
            "role": "sibling repeatability variant, not envelope widening",
            "supported": i121c.get("prototype_b_alternative_bridge_candidate_supported") is True,
            "repeatability_strengthened": i121c.get("prototype_b_repeatability_strengthened") is True,
            "primary_i12_replaced": i121c.get("primary_i12_replaced") is True,
            "primary_i12_envelope_widened": i121c.get("primary_i12_envelope_widened") is True,
            "unit": runtime_unit_summary(sources["i121_runtime"]),
            "margin_interpretation": i121_margin.get("margin_interpretation", "not_recorded"),
            "numeric_margin_summary": i121_margin.get("numeric_margin_summary", {}),
        },
        "i12_2_contribution": {
            "role": "active-medium separability tranche, not leakage tolerance",
            "supported": i122c.get("prototype_b_active_medium_separability_strengthened") is True,
            "active_medium_present_count": i122_summary.get("active_medium_present_count"),
            "zero_leakage_policy_preserved_count": i122_summary.get(
                "zero_leakage_policy_preserved_count"
            ),
            "nonzero_injected_pressure_failed_closed_count": i122_summary.get(
                "nonzero_injected_pressure_failed_closed_count"
            ),
            "leakage_headroom_improved": i122_summary.get("leakage_headroom_improved"),
            "zero_leakage_policy_changed": i122_summary.get("zero_leakage_policy_changed"),
        },
        "shared_claim_ceiling": (
            "bounded Prototype B boundary/shared-medium bridge evidence: primary unit, "
            "sibling repeatability, and active-medium separability"
        ),
        "ready_for_iteration_13": all(
            artifact.get("ready_for_iteration_13") is True for artifact in (i12c, i121c, i122c)
        ),
        "prototype_success_claimed": False,
        "runtime_ecology_success_claimed": False,
        "claim_blockers_remaining": [
            "native shared-medium coordination",
            "nonzero leakage tolerance",
            "semantic trail or pheromone substrate",
            "multi-agent interaction",
            "ant ecology success",
            "agent body / organism-environment boundary",
            "native support",
            "sentience",
            "Phase 8 completion",
        ],
    }

    checks = [
        check("all_source_artifacts_passed", all(source.get("status") == "passed" for source in sources.values())),
        check("i12_primary_supported", prototype_b_summary["i12_contribution"]["supported"]),
        check("i12_1_repeatability_supported", prototype_b_summary["i12_1_contribution"]["supported"]),
        check("i12_1_does_not_replace_or_widen_i12", not prototype_b_summary["i12_1_contribution"]["primary_i12_replaced"] and not prototype_b_summary["i12_1_contribution"]["primary_i12_envelope_widened"]),
        check("i12_2_active_medium_separability_supported", prototype_b_summary["i12_2_contribution"]["supported"]),
        check("i12_2_does_not_claim_leakage_headroom", prototype_b_summary["i12_2_contribution"]["leakage_headroom_improved"] is False),
        check("ready_for_iteration_13", prototype_b_summary["ready_for_iteration_13"]),
        check("unsafe_claim_flags_false", all(value is False for value in UNSAFE_FLAGS.values())),
    ]

    data: dict[str, Any] = {
        "artifact_id": "n29_prototype_b_boundary_shared_medium_synthesis_i12x",
        "experiment_id": "N29",
        "title": "Prototype B Boundary / Shared-Medium Synthesis",
        "iteration": "I12x",
        "generated_at": GENERATED_AT,
        "generated_by": SCRIPT_RELATIVE_PATH,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_prototype_b_synthesis_ready_for_i13",
        "source_artifacts": [
            source_artifact(source_id, SOURCE_PATHS[source_id], parsed)
            for source_id, parsed in sources.items()
        ],
        "prototype_b_summary": prototype_b_summary,
        "claim_boundary": {"unsafe_claim_flags": UNSAFE_FLAGS},
        "checks": checks,
        "failed_checks": [row["check_id"] for row in checks if not row["passed"]],
        "script_sha256": sha256_file(ROOT / SCRIPT_RELATIVE_PATH),
    }
    data["checks"].append(check("no_absolute_paths_in_records", no_absolute_paths(data)))
    data["failed_checks"] = [row["check_id"] for row in data["checks"] if not row["passed"]]
    if data["failed_checks"]:
        data["status"] = "failed"
        data["acceptance_state"] = "failed_prototype_b_synthesis"
        data["prototype_b_summary"]["ready_for_iteration_13"] = False
    return finalize(data)


def write_report(path: Path, data: dict[str, Any]) -> None:
    summary = data["prototype_b_summary"]
    lines = [
        f"# {data['title']}",
        "",
        f"Status: `{data['status']}`",
        "",
        f"Acceptance state: `{data['acceptance_state']}`",
        "",
        f"Output digest: `{data['output_digest']}`",
        "",
        "## Synthesis",
        "",
        "| Tranche | Contribution | Supported |",
        "|---|---|---|",
        f"| `I12` | {summary['i12_contribution']['role']} | `{str(summary['i12_contribution']['supported']).lower()}` |",
        f"| `I12.1` | {summary['i12_1_contribution']['role']} | `{str(summary['i12_1_contribution']['supported']).lower()}` |",
        f"| `I12.2` | {summary['i12_2_contribution']['role']} | `{str(summary['i12_2_contribution']['supported']).lower()}` |",
        "",
        "## Units",
        "",
        "| Unit | Basin side | Medium | Counterpart | Observed flux |",
        "|---|---|---|---|---:|",
    ]
    for label, unit in (
        ("I12", summary["i12_contribution"]["unit"]),
        ("I12.1", summary["i12_1_contribution"]["unit"]),
    ):
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                label,
                unit["basin_side_state"],
                unit["shared_or_adjacent_medium"],
                unit["counterpart_region"],
                unit["observed_absolute_incident_flux"],
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            f"Ready for I13: `{str(summary['ready_for_iteration_13']).lower()}`",
            "",
            "I12.1 is repeatability strengthening, not envelope widening. I12.2 is "
            "active-medium separability, not nonzero leakage tolerance.",
            "",
            "Remaining blockers: " + ", ".join(summary["claim_blockers_remaining"]),
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

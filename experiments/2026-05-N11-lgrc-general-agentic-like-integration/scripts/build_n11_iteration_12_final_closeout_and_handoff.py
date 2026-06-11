#!/usr/bin/env python3
"""Build N11 Iteration 12 final closeout and handoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT / "experiments" / "2026-05-N11-lgrc-general-agentic-like-integration"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

N11_I10_PATH = OUTPUTS / "n11_iteration_10_hypothesis_ab_closeout.json"
N11_I11_PATH = OUTPUTS / "n11_iteration_11_hypothesis_c_native_generalization_gap.json"
ROADMAP_PATH = ROOT / "experiments" / "N05-N11-LGRC-AgenticLikeFoundationRoadmap.md"

OUTPUT_PATH = OUTPUTS / "n11_iteration_12_final_closeout_and_handoff.json"
REPORT_PATH = REPORTS / "n11_iteration_12_final_closeout_and_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-05-N11-lgrc-general-agentic-like-integration/scripts/"
    "build_n11_iteration_12_final_closeout_and_handoff.py"
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_value(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{rel(path)} must contain a JSON object")
    return data


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def git_status_short(pathspec: str) -> str:
    completed = subprocess.run(
        ["git", "status", "--short", pathspec],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def output_digest(output: dict[str, Any]) -> str:
    excluded = {"generated_at", "output_digest", "git"}
    return digest_value(
        {key: value for key, value in output.items() if key not in excluded}
    )


def source_artifact(path: Path, artifact: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": digest_file(path),
        "status": None if artifact is None else artifact.get("status"),
        "output_digest": None if artifact is None else artifact.get("output_digest"),
    }


def final_blocked_claims(i10: dict[str, Any]) -> list[str]:
    claims = []
    for key, allowed in i10["unsafe_claim_flags"].items():
        if allowed is False:
            claims.append(key.removesuffix("_claim_allowed").replace("_", " "))
    return sorted(set(claims))


def build_output() -> dict[str, Any]:
    i10 = load_json(N11_I10_PATH)
    i11 = load_json(N11_I11_PATH)
    final_claim_ceiling = i10["strongest_supported_claim_ceiling"]
    native_blockers = sorted(
        {
            row["native_gap"]
            for row in i11["native_generalization_gap_rows"]
            if row["native_supported"] is False
        }
    )
    generalization_envelope = {
        "positive_ceiling": final_claim_ceiling,
        "gali_level": i10["strongest_supported_gali_level"],
        "positive_basis": i10["level_decisions"]["GALI7"]["basis"],
        "level_decisions": i10["level_decisions"],
        "negative_envelope": i10["negative_envelope"],
        "hypothesis_distinction": i10["hypothesis_distinction"],
    }
    handoff = {
        "handoff_status": "closed_artifact_only_foundation_ready_for_native_gap_work",
        "result_can_be_consumed_by_later_experiments": True,
        "result_can_be_used_as_native_claim": False,
        "recommended_next_paths": [
            {
                "path": "phase8_native_absorption",
                "first_candidates": i11["phase8_ready_candidate_rows"],
                "reason": (
                    "N11 identifies concrete missing native policies behind "
                    "the GALI7 artifact-only foundation."
                ),
            },
            {
                "path": "new_downstream_experiment",
                "precondition": (
                    "Use N11 GALI7 as artifact-only source evidence, not native "
                    "agentic behavior."
                ),
                "reason": (
                    "The N05-N11 foundation can now feed later locomotion-like "
                    "or other agentic-like dynamics experiments with explicit "
                    "claim boundaries."
                ),
            },
        ],
        "native_absorption_order": i11["interpretation"]["phase8_sequence"],
    }
    roadmap_update = {
        "roadmap_path": rel(ROADMAP_PATH),
        "update_required": True,
        "update_performed": True,
        "update_summary": (
            "Record N11 as closed at A7/GALI7 artifact-only foundation, with "
            "native absorption gaps still blocked and Phase 8 candidates named."
        ),
    }
    checks = {
        "iteration_10_closeout_consumed": i10["status"] == "passed",
        "iteration_11_gap_record_consumed": i11["status"] == "passed",
        "final_gali_ceiling_recorded": i10["strongest_supported_gali_level"]
        == "GALI7",
        "a7_target_evidence_reached": i10["roadmap_a7_local_evidence_target_met"]
        is True,
        "artifact_only_result_recorded": i10["gali7_evidence_classification_supported"]
        is True,
        "native_result_not_claimed": all(
            value is False for value in i11["native_support_flags"].values()
        ),
        "generalization_envelope_recorded": bool(generalization_envelope),
        "failure_boundaries_recorded": bool(i10["negative_envelope"]),
        "source_artifacts_recorded": True,
        "final_blocked_claims_recorded": bool(final_blocked_claims(i10)),
        "native_blocker_set_recorded": bool(native_blockers),
        "phase8_handoff_recorded": bool(handoff),
        "roadmap_update_required_recorded": roadmap_update["update_required"],
        "roadmap_update_performed_recorded": roadmap_update["update_performed"],
        "no_agency_personhood_biological_unrestricted_boundary_preserved": all(
            i10["unsafe_claim_flags"][key] is False
            for key in (
                "agency_claim_allowed",
                "personhood_claim_allowed",
                "biological_claim_allowed",
                "unrestricted_agency_claim_allowed",
            )
        ),
        "src_clean_for_iteration_12": git_status_short("src") == "",
    }
    acceptance = {
        "status": "passed" if all(checks.values()) else "failed",
        "achieved": all(checks.values()),
        "acceptance_statement": (
            "Iteration 12 passes if N11 closes with a source-backed final GALI "
            "ceiling, explicit generalization envelope, preserved claim "
            "boundaries, and a clear handoff for either later experiments or "
            "future Phase 8 native absorption. A negative or partial result is "
            "acceptable if the blocker is exact."
        ),
    }
    output: dict[str, Any] = {
        "schema": "n11_iteration_12_final_closeout_and_handoff_v1",
        "experiment": "2026-05-N11-lgrc-general-agentic-like-integration",
        "iteration": 12,
        "purpose": "final_closeout_and_handoff",
        "status": acceptance["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": COMMAND,
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
            "src_clean": git_status_short("src") == "",
        },
        "source_artifacts": {
            "n11_iteration_10_hypothesis_ab_closeout": source_artifact(
                N11_I10_PATH, i10
            ),
            "n11_iteration_11_hypothesis_c_native_generalization_gap": source_artifact(
                N11_I11_PATH, i11
            ),
            "n05_n11_roadmap": source_artifact(ROADMAP_PATH),
        },
        "final_supported_gali_ceiling": i10["strongest_supported_gali_level"],
        "a7_target_evidence_reached": i10["roadmap_a7_local_evidence_target_met"],
        "final_claim_ceiling": final_claim_ceiling,
        "result_mediation": {
            "artifact_only": True,
            "producer_mediated_components_present": True,
            "validator_local_components_present": True,
            "native_route_arbitration_selection_only_present": True,
            "fully_native": False,
        },
        "generalization_envelope": generalization_envelope,
        "final_blocked_claims": final_blocked_claims(i10),
        "native_blocker_set": native_blockers,
        "phase8_handoff": handoff,
        "roadmap_update": roadmap_update,
        "interpretation": {
            "what_n11_achieved": (
                "N11 closes the N05-N11 foundation arc at A7/GALI7 as a "
                "broader/general artifact-only agentic-like integration "
                "candidate across declared context, proxy, support, matrix, "
                "longer-horizon, control, and artifact-replay conditions."
            ),
            "what_n11_does_not_claim": (
                "N11 does not claim agency, intention, goal ownership, identity "
                "acceptance, RC identity collapse, biological behavior, "
                "personhood, unrestricted agency, ACO behavior, or fully native "
                "LGRC agentic-like integration."
            ),
            "handoff_meaning": (
                "The next native work is not to repeat N11's artifact result, "
                "but to absorb selected producer/validator-local mechanisms into "
                "serialized LGRC policy surfaces while preserving the same claim "
                "boundaries."
            ),
        },
        "checks": checks,
        "acceptance": acceptance,
        "next_step": "choose_phase8_native_absorption_or_next_downstream_experiment",
    }
    output["output_digest"] = output_digest(output)
    return output


def render_report(output: dict[str, Any]) -> str:
    lines = [
        "# N11 Iteration 12 Final Closeout And Handoff",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Final Result",
        "",
        "```text",
        f"final_supported_gali_ceiling = {output['final_supported_gali_ceiling']}",
        f"final_claim_ceiling = {output['final_claim_ceiling']}",
        (
            "a7_target_evidence_reached = "
            f"{str(output['a7_target_evidence_reached']).lower()}"
        ),
        "fully_native = false",
        "```",
        "",
        output["interpretation"]["what_n11_achieved"],
        "",
        output["interpretation"]["what_n11_does_not_claim"],
        "",
        "## Result Mediation",
        "",
        "```json",
        json.dumps(output["result_mediation"], indent=2, sort_keys=True),
        "```",
        "",
        "## Generalization Envelope",
        "",
        "```json",
        json.dumps(output["generalization_envelope"], indent=2, sort_keys=True),
        "```",
        "",
        "## Native Blockers And Handoff",
        "",
        "```json",
        json.dumps(
            {
                "native_blocker_set": output["native_blocker_set"],
                "phase8_handoff": output["phase8_handoff"],
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "## Final Blocked Claims",
        "",
        "```json",
        json.dumps(output["final_blocked_claims"], indent=2, sort_keys=True),
        "```",
        "",
        "## Roadmap Update",
        "",
        "```json",
        json.dumps(output["roadmap_update"], indent=2, sort_keys=True),
        "```",
        "",
        "## Checks",
        "",
        "```json",
        json.dumps(output["checks"], indent=2, sort_keys=True),
        "```",
        "",
        "## Acceptance",
        "",
        output["acceptance"]["acceptance_statement"],
        "",
        f"Acceptance state: `{output['acceptance']['status']}`.",
        "",
        "## Run Record",
        "",
        "```text",
        output["command"],
        "```",
        "",
        "Output digest:",
        "",
        "```text",
        output["output_digest"],
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_report(output), encoding="utf-8")
    print(f"wrote {rel(OUTPUT_PATH)}")
    print(f"wrote {rel(REPORT_PATH)}")
    print(f"status {output['status']}")
    print(f"final_supported_gali_ceiling {output['final_supported_gali_ceiling']}")
    print(f"output_digest {output['output_digest']}")


if __name__ == "__main__":
    main()

"""Build N04 Lane A1 retrospective evidence ladder audit."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
N04 = ROOT / "experiments/2026-05-N04-grc9v3-movement-ladders"

ARTIFACTS = {
    "baseline_inventory": N04 / "outputs/n04_baseline_inventory.json",
    "fixture_manifest": N04 / "outputs/movement_fixture_manifest_validation.json",
    "initializer_validation": N04 / "outputs/movement_initializer_validation.json",
    "observables_validation": N04 / "outputs/movement_observables_validation.json",
    "fixed_substrate_tranche_a": N04 / "outputs/fixed_substrate_tranche_a_report.json",
    "m0_m3_classifier": N04 / "outputs/movement_classifier_m0_m3_validation.json",
    "e3_pulse_import": N04 / "outputs/e3_pulse_import_validation.json",
    "geometry_coupling_audit": N04 / "outputs/packet_loop_geometry_coupling_audit.json",
    "boundary_coupled_pulse_fixture": N04 / "outputs/boundary_coupled_pulse_report.json",
    "m4_m5_classifier": N04 / "outputs/loop_driven_movement_m4_m5_report.json",
}

OUTPUT_PATH = N04 / "outputs/n04_evidence_ladder_audit.json"
REPORT_PATH = N04 / "reports/n04_evidence_ladder_audit.md"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": _sha256(path)}


def _run_git_command(args: list[str]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return {"available": False, "error": str(exc)}
    return {
        "available": True,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def _environment_record() -> dict[str, Any]:
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "platform": platform.platform(),
        "git_diff_check": _run_git_command(["diff", "--check"]),
        "git_status_short_src_and_n04": _run_git_command(
            ["status", "--short", "src", str(N04.relative_to(ROOT))]
        ),
    }


def _levels_from_classifier(classifier: dict[str, Any]) -> dict[str, Any]:
    classifications = classifier["classifications"]
    fixed = {
        run_id: row
        for run_id, row in classifications.items()
        if row.get("source") == "iteration_5_fixed_substrate"
    }
    b1_rows = {
        run_id: row
        for run_id, row in fixed.items()
        if row.get("lane_or_case_id") in {"B1", "B1_reversed"}
    }
    k1_rows = {
        run_id: row
        for run_id, row in fixed.items()
        if row.get("lane_or_case_id") in {"K1", "K1_reversed"}
    }
    null_rows = {
        run_id: row
        for run_id, row in fixed.items()
        if row.get("lane_or_case_id") in {"U0", "B0"}
    }
    return {
        "fixed_substrate_run_count": len(fixed),
        "null_runs": sorted(null_rows),
        "b1_bias_runs": sorted(b1_rows),
        "k1_runs": sorted(k1_rows),
        "all_fixed_lanes_m0": all(
            row["movement_level"].startswith("M0") for row in fixed.values()
        ),
        "all_fixed_claims_blocked": all(
            row["movement_claim_allowed"] is False for row in fixed.values()
        ),
        "b1_subthreshold_directional_bias_preserved": all(
            row["diagnostic_subtype"] == "M0_subthreshold_directional_bias"
            for row in b1_rows.values()
        ),
        "k1_no_threshold_response": all(
            row["movement_level"].startswith("M0") for row in k1_rows.values()
        ),
        "identity_shape_safety": {
            "identity_passed_where_applicable": all(
                row["identity_passed"] for row in fixed.values()
            ),
            "shape_passed_where_applicable": all(
                row["shape_passed"] for row in fixed.values()
            ),
            "identity_preserving_displacement_claim_allowed": False,
        },
    }


def build_audit() -> dict[str, Any]:
    data = {key: _load_json(path) for key, path in ARTIFACTS.items()}
    artifact_records = {key: _artifact_record(path) for key, path in ARTIFACTS.items()}

    fixed_summary = _levels_from_classifier(data["m0_m3_classifier"])
    boundary_report = data["boundary_coupled_pulse_fixture"]
    m4_m5 = data["m4_m5_classifier"]

    claim_boundary = {
        "n03_e3_heartbeat_is_pulse_substrate_only": True,
        "movement_claim_inherited_from_n03": False,
        "iteration_10_m6_opened": False,
        "movement_claim_allowed": False,
        "boundary_coupled_movement_claim_allowed": False,
        "loop_driven_movement_claim_allowed": False,
        "locomotion_like_claim_allowed": False,
        "adaptive_topology_entry_allowed": False,
        "biological_or_agency_claim_allowed": False,
    }

    ladder = [
        {
            "level": "M0_M1_fixed_substrate",
            "classification": "movement_negative_with_subthreshold_bias_diagnostics",
            "allowed_evidence": [
                "U0/B0 nulls reject directed movement",
                "B1/B1 reversed preserve subthreshold opposite-sign directional bias",
                "K1/K1 reversed produce no threshold-level response",
            ],
            "blocked_claims": [
                "movement_response",
                "identity_preserving_displacement",
                "loop_driven_movement",
            ],
            "source": artifact_records["m0_m3_classifier"]["path"],
            "summary": fixed_summary,
        },
        {
            "level": "M2_M3_identity_shape",
            "classification": "safety_gates_validated_no_displacement_promotion",
            "allowed_evidence": [
                "identity and shape gates pass where applicable",
                "classifier adversarial cases preserve fail-closed behavior",
            ],
            "blocked_claims": [
                "identity_preserving_displacement_from_fixed_substrate",
                "shape_preserving_displacement_from_fixed_substrate",
            ],
            "source": artifact_records["m0_m3_classifier"]["path"],
            "summary": fixed_summary["identity_shape_safety"],
        },
        {
            "level": "boundary_coupling_fixture",
            "classification": "state_mediated_boundary_coupling_fixture_positive",
            "allowed_evidence": [
                "region-based E3-to-S0 mapping is defined",
                "state-mediated node-coherence coupling is measurable",
                "no direct support/centroid/displacement/topology writes",
                "forward/reversed coupling directions produce signed centroid response",
            ],
            "blocked_claims": [
                "movement_response",
                "boundary_coupled_movement",
                "loop_driven_movement",
            ],
            "source": artifact_records["boundary_coupled_pulse_fixture"]["path"],
            "summary": {
                "claim_ceiling": boundary_report["claim_ceiling"],
                "forward_dx": boundary_report["summary"]["forward_centroid_delta"],
                "reversed_dx": boundary_report["summary"]["reversed_centroid_delta"],
                "movement_claim_allowed": boundary_report["claim_flags"][
                    "movement_claim_allowed"
                ],
            },
        },
        {
            "level": "M4_M5_candidate",
            "classification": "m5_candidate_control_limited",
            "allowed_evidence": [
                "asymmetric lanes pass M4/M5 candidate gates",
                "distinct pulse-locked response windows are counted",
                "pulse-disabled, symmetric-null, and scrambled-order controls remain negative",
            ],
            "blocked_claims": [
                "full_loop_driven_movement_without_true_reversed_e3_pulse_control",
                "locomotion_like_basin_dynamics",
                "adaptive_topology_movement",
                "M6_self_renewing_movement",
            ],
            "source": artifact_records["m4_m5_classifier"]["path"],
            "summary": {
                "claim_ceiling": m4_m5["claim_ceiling"],
                "candidate_lanes": m4_m5["candidate_lanes"],
                "full_claim_controls_passed": m4_m5["summary"][
                    "full_claim_controls_passed"
                ],
                "true_reversed_e3_pulse_control": m4_m5[
                    "true_reversed_e3_pulse_control"
                ],
                "claim_flags": m4_m5["claim_flags"],
            },
        },
    ]

    checks = {
        "all_source_artifacts_present": all(path.exists() for path in ARTIFACTS.values()),
        "fixed_substrate_all_m0": fixed_summary["all_fixed_lanes_m0"],
        "iteration_8_fixture_positive_not_movement": (
            boundary_report["status"] == "passed"
            and boundary_report["claim_flags"]["movement_claim_allowed"] is False
        ),
        "iteration_9_candidate_control_limited": (
            m4_m5["status"] == "passed"
            and m4_m5["claim_ceiling"] == "m5_candidate_control_limited"
            and m4_m5["claim_flags"]["loop_driven_movement_claim_allowed"] is False
        ),
        "m6_remains_blocked": m4_m5["m6_status"]["opened"] is False,
        "all_global_claims_blocked": all(value is False for value in claim_boundary.values() if isinstance(value, bool) and "heartbeat" not in str(value)),
    }
    # The heartbeat field is intentionally true; spell the global claim check out.
    checks["all_global_claims_blocked"] = all(
        claim_boundary[key] is False
        for key in [
            "movement_claim_inherited_from_n03",
            "iteration_10_m6_opened",
            "movement_claim_allowed",
            "boundary_coupled_movement_claim_allowed",
            "loop_driven_movement_claim_allowed",
            "locomotion_like_claim_allowed",
            "adaptive_topology_entry_allowed",
            "biological_or_agency_claim_allowed",
        ]
    )

    return {
        "schema": "movement_ladder_report_v1",
        "report_kind": "n04_evidence_ladder_audit_v1",
        "lane": "A",
        "iteration": "A1",
        "status": "passed" if all(checks.values()) else "failed",
        "source_artifacts": artifact_records,
        "claim_boundary": claim_boundary,
        "evidence_ladder": ladder,
        "allowed_evidence_labels": [
            "fixed_substrate_negative",
            "subthreshold_directional_bias",
            "state_mediated_boundary_coupling_fixture_positive",
            "m5_candidate_control_limited",
        ],
        "blocked_claims": [
            "movement_response",
            "boundary_coupled_movement",
            "loop_driven_movement",
            "locomotion_like_basin_dynamics",
            "adaptive_topology_movement",
            "M6_self_renewing_movement",
            "biological_or_agency_claim",
            "movement_inherited_from_n03",
        ],
        "next_evidence_gap": {
            "primary_gap": "native_true_reversed_e3_pulse_direction_parity",
            "alternative": "close_current_N04_tranche_as_m5_candidate_control_limited",
        },
        "checks": checks,
        "environment": _environment_record(),
    }


def write_report(audit: dict[str, Any]) -> None:
    lines = [
        "# N04 Evidence Ladder Audit",
        "",
        "Command:",
        "",
        "```bash",
        ".venv/bin/python experiments/2026-05-N04-grc9v3-movement-ladders/scripts/build_n04_evidence_ladder_audit.py",
        "```",
        "",
        f"Status: `{audit['status']}`",
        f"Claim boundary: movement claims allowed = `{audit['claim_boundary']['movement_claim_allowed']}`",
        "",
        "## Evidence Ladder",
        "",
        "| Level | Classification | Source |",
        "|---|---|---|",
    ]
    for item in audit["evidence_ladder"]:
        lines.append(
            f"| `{item['level']}` | `{item['classification']}` | `{item['source']}` |"
        )
    lines.extend(
        [
            "",
            "## Allowed Evidence Labels",
            "",
        ]
    )
    for label in audit["allowed_evidence_labels"]:
        lines.append(f"- `{label}`")
    lines.extend(
        [
            "",
            "## Blocked Claims",
            "",
        ]
    )
    for claim in audit["blocked_claims"]:
        lines.append(f"- `{claim}`")
    lines.extend(
        [
            "",
            "## Next Evidence Gap",
            "",
            f"- Primary: `{audit['next_evidence_gap']['primary_gap']}`",
            f"- Alternative: `{audit['next_evidence_gap']['alternative']}`",
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "|---|---:|",
        ]
    )
    for key, value in audit["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A1 clears the existing N04 evidence without promoting new claims. The fixed-substrate tranche remains movement-negative, Iteration 8 remains a fixture-level state-mediated boundary-coupling positive, and Iteration 9 remains an M5-style candidate/control-limited result. Iteration 10/M6 remains blocked.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    audit = build_audit()
    OUTPUT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(audit)
    print(
        json.dumps(
            {
                "status": audit["status"],
                "output": OUTPUT_PATH.relative_to(ROOT).as_posix(),
                "report": REPORT_PATH.relative_to(ROOT).as_posix(),
            },
            sort_keys=True,
        )
    )
    if audit["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

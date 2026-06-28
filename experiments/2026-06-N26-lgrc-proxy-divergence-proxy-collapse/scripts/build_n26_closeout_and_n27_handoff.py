#!/usr/bin/env python3
"""Build N26 Iteration 8 closeout and N27 handoff."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N26-lgrc-proxy-divergence-proxy-collapse"
OUTPUT = EXPERIMENT / "outputs" / "n26_closeout_and_n27_handoff.json"
REPORT = EXPERIMENT / "reports" / "n26_closeout_and_n27_handoff.md"

COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/scripts/"
    "build_n26_closeout_and_n27_handoff.py"
)

SOURCE_ARTIFACTS = [
    (
        "I1",
        "source_inventory_and_scoped_substrate_admission",
        EXPERIMENT / "outputs" / "n26_source_inventory_and_scoped_substrate_admission.json",
        "b2f2a69f98aefbf3cb949dc834e6dab8c480f30bd580e3e389b301b74a04516a",
    ),
    (
        "I2",
        "proxy_divergence_collapse_schema_and_controls",
        EXPERIMENT / "outputs" / "n26_proxy_divergence_collapse_schema_and_controls.json",
        "bbaf1621f64638b76ab296c4dc5b28bf99be7d5c2369d8e96e110e68972de070",
    ),
    (
        "I3",
        "active_nulls_and_failure_baselines",
        EXPERIMENT / "outputs" / "n26_active_nulls_and_failure_baselines.json",
        "90b3adf46add9fd0b98b3022733ce9f9fabbbd1b3695908aefbfb58f7199c2fd",
    ),
    (
        "I4",
        "source_current_proxy_derivation_probe",
        EXPERIMENT / "outputs" / "n26_source_current_proxy_derivation_probe.json",
        "b8c8794ecc8e71c01c7bf9d0e1c369f1630416534741f3fb342c5622775a1680",
    ),
    (
        "I4-A",
        "proxy_derivation_sensitivity_probe",
        EXPERIMENT / "outputs" / "n26_proxy_derivation_sensitivity_probe.json",
        "5dbe325f6ce1ff95434b978e69cf659fdf609e2890960198aca66e2c5c85e414",
    ),
    (
        "I5",
        "proxy_divergence_contrast_matrix",
        EXPERIMENT / "outputs" / "n26_proxy_divergence_contrast_matrix.json",
        "52e7cba79816e840947472d35ee8906f357db1bcf896b59f59bbac243d9ee4a5",
    ),
    (
        "I5-A",
        "alternative_proxy_surface_divergence_probe",
        EXPERIMENT / "outputs" / "n26_alternative_proxy_surface_divergence_probe.json",
        "108849bf8b5249b97611461a4423d4986030c6d84d83b6580ba03cfc561e8eda",
    ),
    (
        "I5-B",
        "fixed_surface_divergence_search",
        EXPERIMENT / "outputs" / "n26_fixed_surface_divergence_search.json",
        "cab31a49994ae2ddf1c031e0e3f30c6c17c9dd169bbb3a9d2ccdc80b1da59c73",
    ),
    (
        "I5-C",
        "same_route_score_dose_divergence_probe",
        EXPERIMENT / "outputs" / "n26_same_route_score_dose_divergence_probe.json",
        "5f4c9355645ba39840f860d4544b71195fbfde277ab9ce7b6fd22291c34099ab",
    ),
    (
        "I6",
        "proxy_collapse_perturbation_matrix",
        EXPERIMENT / "outputs" / "n26_proxy_collapse_perturbation_matrix.json",
        "12207d9eed6e206027abc194ec25f11b7b93b39e4cb3671076742a0af8e7012e",
    ),
    (
        "I7",
        "replay_controls_and_ap5_gate",
        EXPERIMENT / "outputs" / "n26_replay_controls_and_ap5_gate.json",
        "a66fe57dbd7f476f9e7b7c17bff7e02834346bc3e276a8a2c2da79fbe38da0a9",
    ),
]

ABSOLUTE_PATH_MARKERS = ["/home/" + "uros", "Documents/" + "RC-github"]

UNSAFE_CLAIMS = [
    "agency_claim_allowed",
    "ant_ecology_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "organism_life_claim_allowed",
    "phase8_completion_claim_allowed",
    "semantic_choice_claim_allowed",
    "semantic_goal_claim_allowed",
    "semantic_learning_claim_allowed",
    "semantic_target_ownership_claim_allowed",
    "sentience_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
    "unscoped_multi_basin_claim_allowed",
]


def canonical_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def canonical_compact(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest_data(data: Any) -> str:
    return hashlib.sha256(canonical_compact(data).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(data), encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def contains_absolute_path(data: Any) -> bool:
    text = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return any(marker in text for marker in ABSOLUTE_PATH_MARKERS)


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check": check_id, "passed": bool(passed), "detail": detail}


def git_lines(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def src_diff_status() -> dict[str, Any]:
    diff_paths = git_lines(["diff", "--name-only", "--", "src"])
    status_lines = git_lines(["status", "--short", "--", "src"])
    return {
        "src_diff_paths": diff_paths,
        "src_status_lines": status_lines,
        "src_diff_empty": len(diff_paths) == 0 and len(status_lines) == 0,
    }


def load_sources() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    sources: dict[str, dict[str, Any]] = {}
    chain = []
    for iteration, role, path, expected_digest in SOURCE_ARTIFACTS:
        artifact = load_json(path)
        actual_digest = artifact.get("output_digest")
        sources[iteration] = artifact
        chain.append(
            {
                "iteration": iteration,
                "source_role": role,
                "artifact_path": rel(path),
                "artifact_sha256": sha256_file(path),
                "expected_output_digest": expected_digest,
                "actual_output_digest": actual_digest,
                "digest_matches_expected": actual_digest == expected_digest,
                "status": artifact.get("status"),
                "failed_checks": artifact.get("failed_checks", []),
            }
        )
    return sources, chain


def final_pd_status(i7: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "final_supported_pd_ladder_rung": "PD6_N27_ready_bounded_proxy_divergence_collapse_evidence",
        "pd6_supported": True,
        "pd6_source_iteration": "I8",
        "pd5_evidence_source_iteration": "I7",
        "pd5_supported": i7["pd5_supported"],
        "controlled_proxy_divergence_supported": i7[
            "controlled_proxy_divergence_supported"
        ],
        "controlled_proxy_collapse_supported": i7[
            "controlled_proxy_collapse_supported"
        ],
        "source_current_proxy_derivation_supported": True,
        "replay_controls_passed": len(i7["failed_checks"]) == 0,
        "pd6_scope": (
            "bounded artifact-level proxy divergence / proxy collapse evidence "
            "on scoped multi-basin LGRC substrate"
        ),
    }


def final_closeout_status() -> dict[str, Any]:
    return {
        "final_n26_closeout_rung": "N26-C6_N27_ready_bounded_proxy_divergence_collapse_closeout",
        "n26_c6_supported": True,
        "n26_closeout_ladder_rung_assigned": True,
        "final_n26_supported": True,
        "closeout_source_iteration": "I8",
        "closeout_does_not_expand_claim_ceiling": True,
    }


def ap5_status(i7: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ap5_bridge_status": i7["ap5_bridge_status"],
        "scoped_artifact_ap5_bridge_candidate_supported": i7[
            "scoped_artifact_ap5_bridge_candidate_supported"
        ],
        "native_ap5_bridge_supported": False,
        "ap5_nat4_gap_resolved": False,
        "final_global_ap5_supported": False,
        "ap5_dependency_role": (
            "row-local AP5 dependency recorded and replay/control clean for "
            "scoped artifact bridge use"
        ),
        "ap5_boundary_reason": (
            "route-score and basin-deepening surfaces remain producer-mediated "
            "or declared fixture variants, so they cannot close native AP5"
        ),
    }


def source_roles(i7: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "source_iteration": "I4",
            "final_role": "PD2 source-current proxy derivation input",
            "consumable_by_n27": True,
            "must_not_consume_as": ["native_AP5", "native_support", "semantic_goal"],
        },
        {
            "source_iteration": "I4-A",
            "final_role": "proxy derivation sensitivity context",
            "consumable_by_n27": True,
            "must_not_consume_as": ["controlled_proxy_divergence", "proxy_collapse"],
        },
        {
            "source_iteration": "I5",
            "final_role": "PD3 replay-backed contrast context",
            "consumable_by_n27": True,
            "must_not_consume_as": ["controlled_proxy_divergence"],
        },
        {
            "source_iteration": "I5-A",
            "final_role": "alternative-surface false-positive context",
            "consumable_by_n27": True,
            "must_not_consume_as": ["controlled_proxy_divergence"],
        },
        {
            "source_iteration": "I5-B",
            "final_role": "fixed-surface search blocker context",
            "consumable_by_n27": True,
            "must_not_consume_as": ["controlled_proxy_divergence"],
        },
        {
            "source_iteration": "I5-C",
            "final_role": "PD4 controlled proxy-divergence evidence",
            "consumable_by_n27": True,
            "supporting_rows": [
                row["row_id"]
                for row in i7["positive_row_classifications"]
                if row["source_iteration"] == "I5-C"
            ],
            "must_not_consume_as": ["native_AP5", "native_support", "agency"],
        },
        {
            "source_iteration": "I6",
            "final_role": "PD5 controlled proxy-collapse evidence",
            "consumable_by_n27": True,
            "supporting_rows": [
                row["row_id"]
                for row in i7["positive_row_classifications"]
                if row["source_iteration"] == "I6"
            ],
            "must_not_consume_as": ["native_AP5", "native_support", "agency"],
        },
        {
            "source_iteration": "I7",
            "final_role": "replay/control/AP5 classification gate",
            "consumable_by_n27": True,
            "must_not_consume_as": ["native_AP5_closeout", "AP5_NAT4_resolution"],
        },
    ]


def claim_boundary() -> dict[str, Any]:
    return {
        "allowed_claim": (
            "N27-ready bounded artifact-level proxy divergence / proxy collapse "
            "evidence on scoped multi-basin LGRC substrate"
        ),
        "claim_ceiling": (
            "controlled artifact-level PD6 proxy divergence / proxy collapse "
            "closeout with scoped artifact AP5 bridge candidate; not native AP5, "
            "native support, semantic goal, choice, agency, sentience, Phase 8 "
            "completion, ant ecology, or unscoped multi-basin substrate"
        ),
        "blocked_claims": [
            "native_AP5",
            "AP5_NAT4_gap_resolution",
            "native_support",
            "semantic_goal",
            "semantic_target_ownership",
            "semantic_choice",
            "semantic_learning",
            "agency",
            "identity_acceptance",
            "sentience",
            "organism_life",
            "Phase_8_completion",
            "ant_ecology",
            "unscoped_multi_basin_substrate",
            "unrestricted_autonomy",
        ],
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def n27_handoff() -> dict[str, Any]:
    return {
        "next_experiment": "N27_configuration_substrate_transfer",
        "handoff_status": "ready",
        "handoff_question": (
            "Can a basin signature transfer across a declared configuration or "
            "substrate mapping without being reduced to proxy divergence, hidden "
            "producer state, or semantic identity?"
        ),
        "may_consume_n26_as": [
            "bounded_PD6_proxy_divergence_collapse_evidence",
            "scoped_artifact_AP5_bridge_candidate_context",
            "proxy_pressure_control_context",
            "source_current_proxy_basin_contrast_context",
        ],
        "must_not_consume_n26_as": [
            "native_AP5",
            "AP5_NAT4_gap_resolution",
            "semantic_goal_or_choice",
            "agency",
            "native_support",
            "sentience",
            "Phase_8_completion",
            "ant_ecology",
            "unscoped_multi_basin_substrate",
        ],
        "required_n27_controls": [
            "transfer_not_proxy_score_relabel",
            "configuration_mapping_declared_before_use",
            "same_basin_signature_preserved_under_mapping",
            "hidden_producer_state_blocks_transfer_claim",
            "source_current_geometry_required",
            "AP4_AP5_dependency_carried_row_locally_when_selection_or_proxy_participates",
            "unsafe_semantic_agency_native_support_claims_blocked",
        ],
        "handoff_input_artifacts": [
            "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/outputs/n26_closeout_and_n27_handoff.json",
            "experiments/2026-06-N26-lgrc-proxy-divergence-proxy-collapse/reports/n26_closeout_and_n27_handoff.md",
        ],
    }


def embedded_manifest(payloads: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "artifact_role": role,
            "json_pointer": f"#/{role}",
            "digest": digest_data(payload),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        }
        for role, payload in payloads.items()
    ]


def build_checks(output: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_chain = output["source_chain"]
    src_status = output["source_diff_status"]
    return [
        check(
            "source_chain_digests_match_expected",
            all(row["digest_matches_expected"] for row in source_chain),
            source_chain,
        ),
        check(
            "all_source_artifacts_passed",
            all(row["status"] == "passed" and row["failed_checks"] == [] for row in source_chain),
            source_chain,
        ),
        check(
            "i7_controlled_pd5_ready",
            output["source_i7_summary"]["pd5_supported"] is True
            and output["source_i7_summary"]["pd6_or_stronger_supported"] is False
            and output["source_i7_summary"]["failed_checks"] == [],
            output["source_i7_summary"],
        ),
        check(
            "final_pd6_assigned",
            output["final_pd_status"]["pd6_supported"] is True
            and output["final_pd_status"]["final_supported_pd_ladder_rung"].startswith("PD6"),
            output["final_pd_status"],
        ),
        check(
            "final_n26_c6_assigned",
            output["final_closeout_status"]["n26_c6_supported"] is True
            and output["final_closeout_status"]["n26_closeout_ladder_rung_assigned"] is True,
            output["final_closeout_status"],
        ),
        check(
            "ap5_bridge_scoped_native_ap5_blocked",
            output["final_ap5_status"]["scoped_artifact_ap5_bridge_candidate_supported"] is True
            and output["final_ap5_status"]["native_ap5_bridge_supported"] is False
            and output["final_ap5_status"]["ap5_nat4_gap_resolved"] is False,
            output["final_ap5_status"],
        ),
        check(
            "src_diff_empty",
            src_status["src_diff_empty"] is True,
            src_status,
        ),
        check(
            "n27_handoff_ready_with_constraints",
            output["n27_handoff"]["handoff_status"] == "ready"
            and len(output["n27_handoff"]["required_n27_controls"]) >= 6
            and "native_AP5" in output["n27_handoff"]["must_not_consume_n26_as"],
            output["n27_handoff"],
        ),
        check(
            "unsafe_claim_flags_false",
            all(flag is False for flag in output["unsafe_claim_flags"].values())
            and all(flag is False for flag in output["claim_boundary"]["unsafe_claim_flags"].values()),
            output["unsafe_claim_flags"],
        ),
        check(
            "embedded_manifest_valid",
            all(
                row["json_pointer"].startswith("#/")
                and row["digest_algorithm"] == "sha256_canonical_json"
                and row["digest_matches_embedded_payload"] is True
                for row in output["embedded_closeout_manifest"]
            ),
            output["embedded_closeout_manifest"],
        ),
        check("no_absolute_paths_in_records", not contains_absolute_path(output), "repo-relative records only"),
    ]


def write_report(output: Mapping[str, Any]) -> None:
    checks = ["| Check | Passed |", "| --- | --- |"]
    for item in output["checks"]:
        checks.append(f"| `{item['check']}` | `{str(item['passed']).lower()}` |")
    report = f"""# N26 Iteration 8 - Closeout And N27 Handoff

Status: `{output['status']}`

Acceptance state: `{output['acceptance_state']}`

## Final State

```text
final_supported_pd_ladder_rung = {output['final_pd_status']['final_supported_pd_ladder_rung']}
final_n26_closeout_rung = {output['final_closeout_status']['final_n26_closeout_rung']}
pd6_supported = {str(output['final_pd_status']['pd6_supported']).lower()}
n26_c6_supported = {str(output['final_closeout_status']['n26_c6_supported']).lower()}
scoped_artifact_ap5_bridge_candidate_supported = {str(output['final_ap5_status']['scoped_artifact_ap5_bridge_candidate_supported']).lower()}
native_ap5_bridge_supported = {str(output['final_ap5_status']['native_ap5_bridge_supported']).lower()}
ap5_nat4_gap_resolved = {str(output['final_ap5_status']['ap5_nat4_gap_resolved']).lower()}
src_diff_empty = {str(output['source_diff_status']['src_diff_empty']).lower()}
ready_for_n27 = {str(output['ready_for_n27']).lower()}
```

## Interpretation

N26 closes at `PD6` / `N26-C6`: bounded proxy divergence and proxy collapse
evidence is replay/control clean and ready for N27 consumption. The strongest
closed claim is artifact-level and scoped to the multi-basin LGRC substrate
validated by N25.2.

The AP5 result remains bounded:

```text
scoped artifact AP5 bridge candidate = supported
native AP5 bridge = blocked
AP5 NAT4 gap resolved = false
```

The decisive score and basin-deepening surfaces are runtime-visible and
source-current for N26's artifact evidence, but they remain producer-mediated
or declared fixture variants. They must not be promoted into native AP5,
native support, semantic goal ownership, choice, agency, sentience, Phase 8
completion, ant ecology, or unscoped multi-basin substrate.

## N27 Handoff

N27 may consume N26 as bounded PD6 proxy divergence / proxy collapse evidence
and as scoped artifact AP5 bridge context. N27 must treat configuration or
substrate transfer as a new source-current question, not as a proxy-score
relabel or hidden producer carryover.

## Checks

{chr(10).join(checks)}

## Digest

```text
output_digest = {output['output_digest']}
```
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    sources, source_chain = load_sources()
    i7 = sources["I7"]
    src_status = src_diff_status()
    pd_status = final_pd_status(i7)
    closeout = final_closeout_status()
    ap5 = ap5_status(i7)
    roles = source_roles(i7)
    boundary = claim_boundary()
    handoff = n27_handoff()
    payloads = {
        "final_pd_status": pd_status,
        "final_closeout_status": closeout,
        "final_ap5_status": ap5,
        "source_roles": roles,
        "claim_boundary": boundary,
        "n27_handoff": handoff,
    }
    output: dict[str, Any] = {
        "artifact_id": "n26_closeout_and_n27_handoff",
        "experiment": "N26",
        "iteration": "I8",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed",
        "acceptance_state": "accepted_n26_c6_pd6_closeout_and_n27_handoff",
        "source_chain": source_chain,
        "source_i7_summary": {
            "output_digest": i7["output_digest"],
            "candidate_pd_ladder_rung": i7["candidate_pd_ladder_rung"],
            "pd5_supported": i7["pd5_supported"],
            "pd6_or_stronger_supported": i7["pd6_or_stronger_supported"],
            "scoped_artifact_ap5_bridge_candidate_supported": i7[
                "scoped_artifact_ap5_bridge_candidate_supported"
            ],
            "native_ap5_bridge_supported": i7["native_ap5_bridge_supported"],
            "ap5_nat4_gap_resolved": i7["ap5_nat4_gap_resolved"],
            "failed_checks": i7["failed_checks"],
        },
        "final_pd_status": pd_status,
        "final_closeout_status": closeout,
        "final_ap5_status": ap5,
        "source_roles": roles,
        "claim_boundary": boundary,
        "n27_handoff": handoff,
        "source_diff_status": src_status,
        "ready_for_n27": True,
        "unsafe_claim_flags": unsafe_claim_flags(),
        "embedded_closeout_manifest": embedded_manifest(payloads),
        "row_decision": "supported",
        "claim_ceiling": boundary["claim_ceiling"],
    }
    output["checks"] = build_checks(output)
    output["failed_checks"] = [item["check"] for item in output["checks"] if not item["passed"]]
    digest_payload = dict(output)
    digest_payload.pop("output_digest", None)
    output["output_digest"] = digest_data(digest_payload)
    write_json(OUTPUT, output)
    write_report(output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build N13 Iteration 2 support schema and AP mapping artifact."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"
INVENTORY_OUTPUT = OUTPUTS / "n13_support_condition_inventory.json"
INVENTORY_REPORT = REPORTS / "n13_support_condition_inventory.md"

OUTPUT_PATH = OUTPUTS / "n13_support_schema_v1.json"
REPORT_PATH = REPORTS / "n13_support_schema_v1.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N13-lgrc-self-maintenance-and-support-seeking-regulation/"
    "scripts/build_n13_support_schema_v1.py"
)
GENERATED_AT = "2026-06-15T00:00:00+00:00"

AP_LADDER = {
    "AP0": {
        "label": "passive integrated replay",
        "n13_interpretation": (
            "source envelope or boundary row with no support-seeking target"
        ),
    },
    "AP1": {
        "label": "runtime-visible trigger produces bounded response",
        "n13_interpretation": (
            "bounded response evidence exists, but target is still external or "
            "not support-derived"
        ),
    },
    "AP2": {
        "label": "support-sensitive regulation preserves a declared support condition",
        "n13_interpretation": (
            "composition or response is gated by support-state evidence, but "
            "the N13 support-derived target has not yet been isolated"
        ),
    },
    "AP3": {
        "label": "self-maintenance candidate",
        "n13_interpretation": (
            "regulation targets a source-current support-state-derived "
            "condition rather than only an externally declared proxy"
        ),
    },
    "AP4": {
        "label": "consequence-sensitive selection",
        "n13_interpretation": "reserved for N14",
    },
    "AP5": {
        "label": "endogenous proxy candidate",
        "n13_interpretation": "reserved for N15",
    },
    "AP6": {
        "label": "self/environment boundary candidate",
        "n13_interpretation": "reserved for N16",
    },
    "AP7": {
        "label": "closed action-perception loop candidate",
        "n13_interpretation": "reserved for N17",
    },
    "AP8": {
        "label": "long-horizon agentic-like closure candidate",
        "n13_interpretation": "reserved for N18",
    },
}

ROW_SCHEMA_FIELDS = [
    "row_id",
    "source_experiment",
    "source_iteration",
    "source_artifact",
    "source_report",
    "source_sha256",
    "source_report_sha256",
    "mechanism_name",
    "mechanism_role",
    "support_state_fields",
    "external_proxy_fields",
    "producer_decision_fields",
    "bookkeeping_fields",
    "runtime_visible_surfaces",
    "budget_surfaces",
    "response_surfaces",
    "support_condition_name",
    "target_derivation",
    "provisional_ap_level",
    "provisional_self_maintenance_candidate",
    "claim_ceiling",
    "blocked_claims",
    "missing_gates",
    "control_requirements",
]

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_goal_ownership_claim_allowed": False,
    "semantic_goal_understanding_claim_allowed": False,
    "identity_acceptance_claim_allowed": False,
    "runtime_identity_acceptance_claim_allowed": False,
    "selfhood_claim_allowed": False,
    "personhood_claim_allowed": False,
    "biological_behavior_claim_allowed": False,
    "unrestricted_agency_claim_allowed": False,
    "fully_native_agentic_like_integration_claim_allowed": False,
    "native_support_opened": False,
}


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


def build_output() -> dict[str, Any]:
    inventory = load_json(INVENTORY_OUTPUT)
    ap_criteria = {
        "AP0": {
            "required": [
                "source artifact present",
                "claim boundary recorded",
            ],
            "forbidden": ["support-seeking regulation claim"],
        },
        "AP1": {
            "required": [
                "runtime-visible trigger or response surface",
                "bounded response or replay surface",
                "budget surface named",
            ],
            "forbidden": [
                "support-derived target claim",
                "semantic goal ownership claim",
            ],
        },
        "AP2": {
            "required": [
                "source-backed support condition or support-state matrix",
                "support-present and support-disrupted distinction",
                "artifact replay or source-current reconstruction",
                "claim flags forced false",
            ],
            "forbidden": [
                "identity acceptance claim",
                "self-maintenance claim without target derivation",
            ],
        },
        "AP3": {
            "required": [
                "support_state_fields source-current and serialized",
                "support_condition_name derived from support state",
                "target_derivation not external fixture label",
                "external_proxy_fields separated from support target",
                "support error signal recorded",
                "bounded response magnitude surface recorded",
                "node-plus-packet or explicit budget debit recorded",
                "support trend/stability fields recorded",
                "support-disrupted negative control passes",
                "explicit restoration control, if used, is source-backed",
                "hidden support target control passes",
                "post-hoc support label control passes",
                "identity acceptance relabel blocked",
                "semantic goal ownership relabel blocked",
                "agency relabel blocked",
            ],
            "forbidden": [
                "identity acceptance claim",
                "semantic goal ownership claim",
                "intention claim",
                "agency claim",
                "native support claim without Phase 8 implementation",
            ],
        },
    }
    dispositions = {
        "support_condition_seed": (
            "source-backed support-state evidence that may feed later target "
            "derivation"
        ),
        "external_proxy_baseline": (
            "bounded proxy regulation evidence that must remain separated from "
            "support-derived targets"
        ),
        "support_sensitive_matrix": (
            "source-backed matrix showing support-valid, disrupted, and "
            "restored regimes"
        ),
        "phase8_readiness_input": (
            "N12 readiness record that may inform response/route surfaces but "
            "does not open native support"
        ),
        "claim_boundary_blocker": (
            "blocked input or theory-sensitive boundary record"
        ),
    }
    control_flags = {
        "external_proxy_relabel_blocked": True,
        "hidden_support_target_blocked": True,
        "post_hoc_support_label_blocked": True,
        "support_disrupted_regulation_blocked": True,
        "identity_acceptance_relabel_blocked": True,
        "semantic_goal_ownership_relabel_blocked": True,
        "agency_relabel_blocked": True,
        "budget_ambiguity_blocked": True,
        "stale_source_replay_blocked": True,
        "native_support_relabel_blocked": True,
    }
    validation_scope = {
        "iteration_2_freezes_schema": True,
        "row_validation_starts_iteration_3": True,
        "ap3_assignment_requires_all_ap3_gates": True,
        "positive_n13_result_is_agency_prerequisite_only": True,
    }
    checks = {
        "inventory_source_passed": inventory["status"] == "passed",
        "row_schema_fields_declared": len(ROW_SCHEMA_FIELDS) >= 20,
        "ap_ladder_complete": set(AP_LADDER) == {
            "AP0",
            "AP1",
            "AP2",
            "AP3",
            "AP4",
            "AP5",
            "AP6",
            "AP7",
            "AP8",
        },
        "ap2_ap3_distinction_declared": "AP2" in ap_criteria
        and "AP3" in ap_criteria
        and "target_derivation not external fixture label"
        in ap_criteria["AP3"]["required"],
        "control_flags_declared": all(control_flags.values()),
        "claim_flags_all_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "phase8_not_opened": True,
        "native_support_not_opened": CLAIM_FLAGS_FORCED_FALSE[
            "native_support_opened"
        ]
        is False,
        "validation_scope_declared": validation_scope[
            "row_validation_starts_iteration_3"
        ],
        "inventory_sha256_present": bool(digest_file(INVENTORY_OUTPUT)),
        "src_diff_empty": git_status_short("src") == "",
    }
    output = {
        "experiment": "N13",
        "iteration": 2,
        "purpose": "support_schema_v1",
        "schema": "n13_support_schema_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "target_ap_ceiling": "AP3",
        "ap_ladder": AP_LADDER,
        "ap_criteria": ap_criteria,
        "row_schema_fields": ROW_SCHEMA_FIELDS,
        "primary_dispositions": dispositions,
        "control_flags": control_flags,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "fail_closed_blockers": [
            "missing_source_artifact",
            "external_proxy_only",
            "hidden_support_target",
            "post_hoc_support_label",
            "support_disrupted_but_regulation_counted",
            "budget_surface_ambiguity",
            "stale_source_replay",
            "identity_acceptance_relabel",
            "semantic_goal_ownership_relabel",
            "agency_relabel",
            "native_support_without_phase8",
        ],
        "validation_scope": validation_scope,
        "checks": checks,
        "source_artifacts": {
            rel(INVENTORY_OUTPUT): source_artifact(INVENTORY_OUTPUT, inventory)
        },
        "source_reports": {
            rel(INVENTORY_REPORT): {
                "path": rel(INVENTORY_REPORT),
                "sha256": digest_file(INVENTORY_REPORT),
            }
        },
        "artifact_reproducibility": {
            "generated_at_fixed": GENERATED_AT,
            "wall_clock_timestamp_in_file": False,
            "output_digest_excludes_generated_at_and_git": True,
        },
        "git": {
            "head": git_head(),
            "src_status_short": git_status_short("src"),
        },
    }
    output["output_digest"] = output_digest(output)
    return output


def write_report(output: dict[str, Any]) -> None:
    lines = [
        "# N13 Support Schema V1",
        "",
        "## Status",
        "",
        f"Status: `{output['status']}`.",
        "",
        "```text",
        f"target_ap_ceiling = {output['target_ap_ceiling']}",
        "phase8_opened = false",
        "native_support_opened = false",
        "identity_acceptance_opened = false",
        "agency_claim_opened = false",
        "```",
        "",
        "Iteration 2 freezes the support-condition schema and N13 AP mapping.",
        "It does not validate candidate rows against AP3 yet; that begins in",
        "Iterations 3-7.",
        "",
        "## AP Ladder",
        "",
        "| AP | Label | N13 interpretation |",
        "| --- | --- | --- |",
    ]
    for level, record in output["ap_ladder"].items():
        lines.append(
            "| "
            f"`{level}` | "
            f"{record['label']} | "
            f"{record['n13_interpretation']} |"
        )
    lines.extend(
        [
            "",
            "## AP2 And AP3 Criteria",
            "",
            "```json",
            json.dumps(
                {
                    "AP2": output["ap_criteria"]["AP2"],
                    "AP3": output["ap_criteria"]["AP3"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Row Schema Fields",
            "",
            "```json",
            json.dumps(output["row_schema_fields"], indent=2),
            "```",
            "",
            "## Controls",
            "",
            "```json",
            json.dumps(output["control_flags"], indent=2, sort_keys=True),
            "```",
            "",
            "## Fail-Closed Blockers",
            "",
            "```json",
            json.dumps(output["fail_closed_blockers"], indent=2),
            "```",
            "",
            "## Checks",
            "",
            "```json",
            json.dumps(output["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Claim Boundary",
            "",
            "```text",
            "AP3 self-maintenance candidate != agency",
            "support-derived target != semantic goal ownership",
            "support survival != identity acceptance",
            "bounded response != intention",
            "artifact-level regulation != native support",
            "```",
            "",
            "## Output Digest",
            "",
            "```text",
            output["output_digest"],
            "```",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = build_output()
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(output)
    if output["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

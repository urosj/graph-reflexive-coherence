#!/usr/bin/env python3
"""Build N14 Iteration 5 adversarial consequence control matrix."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = (
    ROOT
    / "experiments"
    / "2026-06-N14-lgrc-consequence-sensitive-route-selection"
)
OUTPUTS = EXPERIMENT / "outputs"
REPORTS = EXPERIMENT / "reports"

SELECTION_OUTPUT = OUTPUTS / "n14_consequence_sensitive_selection_candidate.json"
SELECTION_REPORT = REPORTS / "n14_consequence_sensitive_selection_candidate.md"
ROUTE_RECORDS_OUTPUT = OUTPUTS / "n14_route_consequence_records.json"
ROUTE_RECORDS_REPORT = REPORTS / "n14_route_consequence_records.md"

OUTPUT_PATH = OUTPUTS / "n14_consequence_control_matrix.json"
REPORT_PATH = REPORTS / "n14_consequence_control_matrix.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N14-lgrc-consequence-sensitive-route-selection/"
    "scripts/build_n14_consequence_control_matrix.py"
)
GENERATED_AT = "2026-06-16T00:00:00+00:00"

CLAIM_FLAGS_FORCED_FALSE = {
    "agency_claim_allowed": False,
    "intention_claim_allowed": False,
    "semantic_choice_claim_allowed": False,
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

VALID_BUDGET_SURFACE = "source_budget_surfaces_present_for_selection_candidate"
VALID_RANK_SOURCE = "derived_from_serialized_consequence_score_components"
SELECTION_CONTRACT_ENFORCEMENT = {
    "contract_id": "n14_i5_selection_contract_hardening_v1",
    "source_selection_rule_id": "lowest_derived_consequence_rank_budget_valid_v1",
    "enforced_order": [
        "reject hidden outcome, post-hoc, stale, relabel, and fixture-label metadata",
        "reject candidate-set cherry-picking",
        "reject missing consequence records",
        "reject candidates without budget-valid source surfaces before ranking",
        "require consequence_rank_source derived from serialized score components",
        "sort by consequence_rank, immediate_affordance_rank, and route_candidate_id",
        "apply explicit tie-policy removal control only when removal is explicit",
    ],
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


def source_report(path: Path) -> dict[str, str]:
    return {"path": rel(path), "sha256": digest_file(path)}


def make_variant(
    control_id: str,
    control_name: str,
    base_records: list[dict[str, Any]],
    baseline_eligible_routes: list[str],
    expected_outcome: str,
    expected_blocker_code: str | None,
    mutation_summary: str,
    *,
    records: list[dict[str, Any]] | None = None,
    eligible_routes: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    variant_records = copy.deepcopy(records if records is not None else base_records)
    return {
        "control_id": control_id,
        "control_name": control_name,
        "mutation_summary": mutation_summary,
        "baseline_eligible_routes": baseline_eligible_routes,
        "eligible_routes": eligible_routes
        if eligible_routes is not None
        else list(baseline_eligible_routes),
        "records": variant_records,
        "metadata": metadata or {},
        "expected_outcome": expected_outcome,
        "expected_blocker_code": expected_blocker_code,
        "variant_digest": digest_value(
            {
                "control_id": control_id,
                "eligible_routes": eligible_routes
                if eligible_routes is not None
                else list(baseline_eligible_routes),
                "records": variant_records,
                "metadata": metadata or {},
            }
        ),
    }


def has_top_tie(records: list[dict[str, Any]]) -> bool:
    if len(records) < 2:
        return False
    ranks = [record["consequence_rank"] for record in records]
    return ranks.count(min(ranks)) > 1


def route_ids(records: list[dict[str, Any]]) -> set[str]:
    return {record["route_candidate_id"] for record in records}


def execute_variant(variant: dict[str, Any]) -> dict[str, Any]:
    records = variant["records"]
    metadata = variant["metadata"]
    baseline_routes = set(variant["baseline_eligible_routes"])
    eligible_routes = set(variant["eligible_routes"])
    actual_routes = route_ids(records)
    if metadata.get("hidden_outcome_table") is not None:
        return blocked("hidden_outcome_table_blocked")
    if metadata.get("post_hoc_consequence_score") is not None:
        return blocked("post_hoc_consequence_scoring_blocked")
    if metadata.get("stale_source_window") is True:
        return blocked("stale_consequence_record_blocked")
    if metadata.get("claim_relabel") is not None:
        return blocked(f"{metadata['claim_relabel']}_relabel_blocked")
    if metadata.get("selection_rule_override") == "immediate_affordance_only":
        return blocked("immediate_affordance_only_relabel_blocked")
    if metadata.get("fixture_label_preference") is not None:
        return blocked("fixture_label_preference_blocked")
    if eligible_routes != baseline_routes:
        return blocked("candidate_set_cherry_picking_blocked")
    if actual_routes != eligible_routes:
        return blocked("missing_consequence_record_blocked")
    budget_invalid_routes = [
        record["route_candidate_id"]
        for record in records
        if record["budget_validity"] != VALID_BUDGET_SURFACE
    ]
    if budget_invalid_routes:
        return blocked("budget_invalid_route_blocked")
    invalid_rank_source_routes = [
        record["route_candidate_id"]
        for record in records
        if record.get("consequence_rank_source") != VALID_RANK_SOURCE
    ]
    if invalid_rank_source_routes:
        return blocked("invalid_consequence_rank_source_blocked")
    tie_policy_explicitly_removed = (
        "tie_policy" in metadata and metadata["tie_policy"] in {None, ""}
    )
    if tie_policy_explicitly_removed and has_top_tie(records):
        return blocked("tie_policy_ambiguity_blocked")
    ranked = sorted(
        records,
        key=lambda record: (
            record["consequence_rank"],
            record["immediate_affordance_rank"],
            record["route_candidate_id"],
        ),
    )
    selected = ranked[0]
    return {
        "observed_outcome": "selected",
        "selected_route": selected["route_candidate_id"],
        "blocker_code": None,
        "blocked": False,
    }


def blocked(blocker_code: str) -> dict[str, Any]:
    return {
        "observed_outcome": "blocked",
        "selected_route": None,
        "blocker_code": blocker_code,
        "blocked": True,
    }


def control_passed(variant: dict[str, Any], observed: dict[str, Any]) -> bool:
    if variant["expected_outcome"] == "selected_route_b":
        return (
            observed["observed_outcome"] == "selected"
            and observed["selected_route"] == "route_b"
            and observed["blocker_code"] is None
        )
    return (
        observed["observed_outcome"] == "blocked"
        and observed["blocker_code"] == variant["expected_blocker_code"]
    )


def build_variants(selection: dict[str, Any]) -> list[dict[str, Any]]:
    base_records = selection["selection_records"]
    baseline_eligible_routes = selection["selection_decision_record"][
        "eligible_routes"
    ]
    variants = []
    variants.append(
        make_variant(
            "hidden_outcome_table_control",
            "Hidden outcome table",
            base_records,
            baseline_eligible_routes,
            "blocked",
            "hidden_outcome_table_blocked",
            "Injects future outcome labels outside the serialized consequence records.",
            metadata={"hidden_outcome_table": {"route_b": "future_good"}},
        )
    )
    variants.append(
        make_variant(
            "post_hoc_consequence_scoring_control",
            "Post-hoc consequence scoring",
            base_records,
            baseline_eligible_routes,
            "blocked",
            "post_hoc_consequence_scoring_blocked",
            "Adds a score after selected_route is known.",
            metadata={"post_hoc_consequence_score": {"route_b": 999.0}},
        )
    )
    invalid_rank_source_records = copy.deepcopy(base_records)
    for record in invalid_rank_source_records:
        if record["route_candidate_id"] == "route_b":
            record["consequence_rank_source"] = "fabricated_post_hoc_rank_source"
            record["consequence_rank"] = 1
    variants.append(
        make_variant(
            "fabricated_consequence_rank_source_control",
            "Fabricated consequence-rank source",
            base_records,
            baseline_eligible_routes,
            "blocked",
            "invalid_consequence_rank_source_blocked",
            "Fabricates a consequence rank source instead of deriving rank from serialized score components.",
            records=invalid_rank_source_records,
        )
    )
    variants.append(
        make_variant(
            "stale_consequence_record_control",
            "Stale consequence record",
            base_records,
            baseline_eligible_routes,
            "blocked",
            "stale_consequence_record_blocked",
            "Marks the source window stale before selection.",
            metadata={"stale_source_window": True},
        )
    )
    invalid_budget_records = copy.deepcopy(base_records)
    for record in invalid_budget_records:
        if record["route_candidate_id"] == "route_b":
            record["budget_validity"] = "budget_invalid_source_surface"
            record["budget_cost_surface"]["invalid_budget_marker"] = (
                "forced_budget_debit_exceeds_bound"
            )
    variants.append(
        make_variant(
            "budget_invalid_route_control",
            "Budget-invalid route",
            base_records,
            baseline_eligible_routes,
            "blocked",
            "budget_invalid_route_blocked",
            "Makes the highest consequence-ranked route budget-invalid.",
            records=invalid_budget_records,
        )
    )
    missing_records = [
        copy.deepcopy(record)
        for record in base_records
        if record["route_candidate_id"] != "route_b"
    ]
    variants.append(
        make_variant(
            "missing_consequence_record_control",
            "Missing consequence record",
            base_records,
            baseline_eligible_routes,
            "blocked",
            "missing_consequence_record_blocked",
            "Removes the route_b consequence record while route_b remains eligible.",
            records=missing_records,
        )
    )
    cherry_records = [
        copy.deepcopy(record)
        for record in base_records
        if record["route_candidate_id"] == "route_b"
    ]
    variants.append(
        make_variant(
            "candidate_set_cherry_picking_control",
            "Candidate-set cherry-picking",
            base_records,
            baseline_eligible_routes,
            "blocked",
            "candidate_set_cherry_picking_blocked",
            "Drops route_a from the eligible set before selection.",
            records=cherry_records,
            eligible_routes=["route_b"],
        )
    )
    tie_records = copy.deepcopy(base_records)
    for record in tie_records:
        record["consequence_rank"] = 1
        record["consequence_score_components"]["consequence_score"] = 0.12
    variants.append(
        make_variant(
            "tie_policy_ambiguity_control",
            "Tie-policy ambiguity",
            base_records,
            baseline_eligible_routes,
            "blocked",
            "tie_policy_ambiguity_blocked",
            "Forces a consequence-rank tie and removes the tie policy.",
            records=tie_records,
            metadata={"tie_policy": None},
        )
    )
    variants.append(
        make_variant(
            "immediate_affordance_only_relabel_control",
            "Immediate-affordance-only relabel",
            base_records,
            baseline_eligible_routes,
            "blocked",
            "immediate_affordance_only_relabel_blocked",
            "Attempts to replace the consequence rule with immediate affordance.",
            metadata={"selection_rule_override": "immediate_affordance_only"},
        )
    )
    variants.append(
        make_variant(
            "matched_affordance_conflict_control",
            "Matched affordance conflict",
            base_records,
            baseline_eligible_routes,
            "selected_route_b",
            None,
            "Runs the unmodified conflict case: route_a has immediate rank 1 and route_b has consequence rank 1.",
        )
    )
    variants.append(
        make_variant(
            "fixture_label_preference_control",
            "Fixture-label preference",
            base_records,
            baseline_eligible_routes,
            "blocked",
            "fixture_label_preference_blocked",
            "Attempts to select from a fixture label instead of consequence records.",
            metadata={"fixture_label_preference": {"preferred_route": "route_a"}},
        )
    )
    claim_controls = [
        ("semantic_intention_relabel_control", "semantic_intention"),
        ("agency_relabel_control", "agency"),
        ("native_support_relabel_control", "native_support"),
        ("identity_acceptance_relabel_control", "identity_acceptance"),
        ("selfhood_relabel_control", "selfhood"),
        ("personhood_relabel_control", "personhood"),
        ("biological_behavior_relabel_control", "biological_behavior"),
        ("semantic_choice_relabel_control", "semantic_choice"),
        ("semantic_goal_ownership_relabel_control", "semantic_goal_ownership"),
        ("unrestricted_agency_relabel_control", "unrestricted_agency"),
    ]
    for control_id, claim in claim_controls:
        variants.append(
            make_variant(
                control_id,
                claim.replace("_", " ").title(),
                base_records,
                baseline_eligible_routes,
                "blocked",
                f"{claim}_relabel_blocked",
                f"Attempts to promote the AP4 candidate into {claim}.",
                metadata={"claim_relabel": claim},
            )
        )
    return variants


def build_control_records(selection: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for variant in build_variants(selection):
        observed = execute_variant(variant)
        record = {
            "control_id": variant["control_id"],
            "control_name": variant["control_name"],
            "mutation_summary": variant["mutation_summary"],
            "variant_digest": variant["variant_digest"],
            "expected_outcome": variant["expected_outcome"],
            "expected_blocker_code": variant["expected_blocker_code"],
            "observed_outcome": observed["observed_outcome"],
            "observed_selected_route": observed["selected_route"],
            "observed_blocker_code": observed["blocker_code"],
            "blocked": observed["blocked"],
            "passed": control_passed(variant, observed),
            "runtime_state_used": False,
            "phase8_opened": False,
            "native_support_opened": False,
            "final_ap4_supported": False,
        }
        records.append(record)
    return records


def build_output() -> dict[str, Any]:
    selection = load_json(SELECTION_OUTPUT)
    route_records = load_json(ROUTE_RECORDS_OUTPUT)
    control_records = build_control_records(selection)
    lookup = {record["control_id"]: record for record in control_records}
    negative_records = [
        record for record in control_records if record["expected_outcome"] == "blocked"
    ]
    blocker_codes = [
        record["observed_blocker_code"]
        for record in negative_records
        if record["observed_blocker_code"]
    ]
    checks = {
        "selection_source_passed": selection["status"] == "passed",
        "route_records_source_passed": route_records["status"] == "passed",
        "all_controls_executed": all(
            record["observed_outcome"] in {"blocked", "selected"}
            for record in control_records
        ),
        "all_controls_passed": all(record["passed"] for record in control_records),
        "negative_controls_blocked": all(
            record["blocked"] and record["passed"] for record in negative_records
        ),
        "distinct_negative_blockers_present": len(set(blocker_codes))
        == len(blocker_codes),
        "hidden_outcome_table_blocked": lookup[
            "hidden_outcome_table_control"
        ]["passed"],
        "post_hoc_consequence_scoring_blocked": lookup[
            "post_hoc_consequence_scoring_control"
        ]["passed"],
        "invalid_consequence_rank_source_blocked": lookup[
            "fabricated_consequence_rank_source_control"
        ]["passed"],
        "stale_consequence_record_blocked": lookup[
            "stale_consequence_record_control"
        ]["passed"],
        "budget_invalid_route_blocked": lookup[
            "budget_invalid_route_control"
        ]["passed"],
        "missing_consequence_record_blocked": lookup[
            "missing_consequence_record_control"
        ]["passed"],
        "candidate_set_cherry_picking_blocked": lookup[
            "candidate_set_cherry_picking_control"
        ]["passed"],
        "tie_policy_ambiguity_blocked": lookup[
            "tie_policy_ambiguity_control"
        ]["passed"],
        "budget_validity_checked_before_ranking": lookup[
            "budget_invalid_route_control"
        ]["observed_blocker_code"]
        == "budget_invalid_route_blocked",
        "consequence_rank_source_validated_before_ranking": lookup[
            "fabricated_consequence_rank_source_control"
        ]["observed_blocker_code"]
        == "invalid_consequence_rank_source_blocked",
        "tie_policy_removal_requires_explicit_metadata": lookup[
            "tie_policy_ambiguity_control"
        ]["observed_blocker_code"]
        == "tie_policy_ambiguity_blocked",
        "immediate_affordance_only_relabel_blocked": lookup[
            "immediate_affordance_only_relabel_control"
        ]["passed"],
        "matched_affordance_conflict_resolved_by_consequence": (
            lookup["matched_affordance_conflict_control"]["observed_selected_route"]
            == "route_b"
            and lookup["matched_affordance_conflict_control"]["passed"]
        ),
        "fixture_label_preference_blocked": lookup[
            "fixture_label_preference_control"
        ]["passed"],
        "semantic_intention_relabel_blocked": lookup[
            "semantic_intention_relabel_control"
        ]["passed"],
        "agency_relabel_blocked": lookup["agency_relabel_control"]["passed"],
        "native_support_relabel_blocked": lookup[
            "native_support_relabel_control"
        ]["passed"],
        "identity_acceptance_relabel_blocked": lookup[
            "identity_acceptance_relabel_control"
        ]["passed"],
        "selfhood_relabel_blocked": lookup["selfhood_relabel_control"]["passed"],
        "personhood_relabel_blocked": lookup["personhood_relabel_control"]["passed"],
        "biological_behavior_relabel_blocked": lookup[
            "biological_behavior_relabel_control"
        ]["passed"],
        "semantic_choice_relabel_blocked": lookup[
            "semantic_choice_relabel_control"
        ]["passed"],
        "semantic_goal_ownership_relabel_blocked": lookup[
            "semantic_goal_ownership_relabel_control"
        ]["passed"],
        "unrestricted_agency_relabel_blocked": lookup[
            "unrestricted_agency_relabel_control"
        ]["passed"],
        "claim_flags_forced_false": all(
            value is False for value in CLAIM_FLAGS_FORCED_FALSE.values()
        ),
        "runtime_state_used_false": all(
            record["runtime_state_used"] is False for record in control_records
        ),
        "final_ap4_not_supported": all(
            record["final_ap4_supported"] is False for record in control_records
        ),
        "phase8_opened_false": all(
            record["phase8_opened"] is False for record in control_records
        ),
        "native_support_opened_false": all(
            record["native_support_opened"] is False for record in control_records
        ),
        "src_diff_empty": git_status_short("src") == "",
    }
    acceptance_state = (
        "accepted_adversarial_control_matrix_pending_replay"
        if all(checks.values())
        else "rejected_adversarial_control_matrix"
    )
    interpretation_record = {
        "record_id": "n14_i5_interpretation_control_matrix_v1",
        "acceptance_state": acceptance_state,
        "supported_interpretation": (
            "N14 Iteration 5 executes adversarial controls for the provisional "
            "memory-dominant AP4 candidate. Hidden outcomes, post-hoc scores, "
            "stale records, budget-invalid routes, missing records, cherry-picked "
            "candidate sets, ambiguous ties, fixture labels, immediate-affordance "
            "relabels, and unsafe claim relabels fail closed."
        ),
        "unsupported_interpretations": [
            "final AP4 support",
            "support-specific route consequence support",
            "regulation-specific route consequence support",
            "intention",
            "agency",
            "semantic choice",
            "semantic goal ownership",
            "identity acceptance",
            "selfhood",
            "personhood",
            "biological behavior",
            "native support",
            "fully native integration",
        ],
        "plain_language_interpretation": (
            "The Iteration 4 candidate is no longer relying only on declared "
            "control policies: Iteration 5 constructs corrupted variants and "
            "confirms each fails with a distinct blocker. The clean conflict case "
            "still selects route_b by consequence evidence. Final AP4 remains "
            "pending because replay and perturbation controls are not run until "
            "Iteration 6 and claim classification is not frozen until Iteration 7."
        ),
        "next_required_step": (
            "Run Iteration 6 consequence perturbation and replay matrix to test "
            "source-sensitive rank changes and replay stability."
        ),
    }
    output = {
        "experiment": "N14",
        "iteration": 5,
        "purpose": "adversarial_consequence_control_matrix",
        "schema": "n14_consequence_control_matrix_v1",
        "generated_at": GENERATED_AT,
        "command": COMMAND,
        "status": "passed" if all(checks.values()) else "failed",
        "acceptance_state": acceptance_state,
        "target_ap_ceiling": "AP4",
        "iteration_result": {
            "acceptance_state": acceptance_state,
            "controls_passed": all(checks.values()),
            "control_record_count": len(control_records),
            "negative_control_count": len(negative_records),
            "negative_controls_blocked": checks["negative_controls_blocked"],
            "matched_affordance_conflict_selected_route": lookup[
                "matched_affordance_conflict_control"
            ]["observed_selected_route"],
            "provisional_ap_level": "AP4_candidate",
            "final_ap4_supported": False,
            "phase8_opened": False,
            "native_support_opened": False,
        },
        "selection_contract_enforcement": SELECTION_CONTRACT_ENFORCEMENT,
        "control_records": control_records,
        "interpretation_record": interpretation_record,
        "claim_flags_forced_false": CLAIM_FLAGS_FORCED_FALSE,
        "checks": checks,
        "source_artifacts": {
            rel(SELECTION_OUTPUT): source_artifact(SELECTION_OUTPUT, selection),
            rel(ROUTE_RECORDS_OUTPUT): source_artifact(
                ROUTE_RECORDS_OUTPUT, route_records
            ),
        },
        "source_reports": {
            rel(SELECTION_REPORT): source_report(SELECTION_REPORT),
            rel(ROUTE_RECORDS_REPORT): source_report(ROUTE_RECORDS_REPORT),
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
        "# N14 Consequence Control Matrix",
        "",
        f"Status: `{output['status']}`.",
        "",
        "## Acceptance State",
        "",
        "```text",
        output["acceptance_state"],
        "```",
        "",
        "## Interpretation",
        "",
        "```json",
        json.dumps(output["interpretation_record"], indent=2, sort_keys=True),
        "```",
        "",
        "## Selection Contract Enforcement",
        "",
        "```json",
        json.dumps(
            output["selection_contract_enforcement"], indent=2, sort_keys=True
        ),
        "```",
        "",
        "## Control Records",
        "",
        "| Control | Expected | Observed | Blocker | Passed |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in output["control_records"]:
        observed = record["observed_outcome"]
        if record["observed_selected_route"]:
            observed = f"{observed}:{record['observed_selected_route']}"
        blocker = record["observed_blocker_code"] or "none"
        lines.append(
            "| "
            f"`{record['control_id']}` | "
            f"`{record['expected_outcome']}` | "
            f"`{observed}` | "
            f"`{blocker}` | "
            f"`{str(record['passed']).lower()}` |"
        )
    lines.extend(
        [
            "",
            "Iteration 5 executes adversarial controls against the Iteration 4",
            "selection candidate. It does not run perturbation/replay regimes",
            "and does not close final `AP4`.",
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
            "control matrix passed != final AP4 support",
            "memory-dominant AP4 candidate != support-specific route consequence support",
            "memory-dominant AP4 candidate != regulation-specific route consequence support",
            "consequence control pass != intention",
            "consequence control pass != agency",
            "artifact-level controls != native support",
            "N14 Iteration 5 != semantic choice or goal ownership",
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

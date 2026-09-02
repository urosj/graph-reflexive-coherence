#!/usr/bin/env python3
"""Focused ET-C4 mutation, support, frontier, and adversarial checks."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Callable


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, digest  # noqa: E402
from grcv4_explorer.counterfactual import (  # noqa: E402
    MUTATION_TARGETS,
    RESULT_STATUSES,
    TARGET_KINDS,
    evaluate_mutation,
    evaluate_support_predicate,
    load_counterfactual_context,
    make_mutation,
    mutation_falsifies_closing_precondition,
    mutation_satisfies_activation_condition,
    validate_mutation,
)
from grcv4_explorer.errors import MutationValidationError  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402


A_CANDIDATE = "V4-A-temporalized-W"
C_CANDIDATE = "V4-C-constitutive-C-sector"
A_CONTRACTION = "D10.2-EC-CI-A-CONTRACTION"
D10_2 = "GRC9V4-CD-D10.2-v1"


def expect_error(
    label: str, error_type: type[BaseException], call: Callable[[], Any]
) -> None:
    try:
        call()
    except error_type:
        return
    raise RuntimeError(f"ET-C4 fixture did not fail closed: {label}")


def refresh(mutation: dict[str, Any]) -> dict[str, Any]:
    mutation["mutation_id"] = f"ET-C4-MUT-{digest({k: v for k, v in mutation.items() if k != 'mutation_id'})}"
    return mutation


def edge(edge_id: str, semantic: str) -> dict[str, Any]:
    return {"edge_id": edge_id, "support_semantic": semantic}


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    context = load_counterfactual_context(repo_root, SIDE_TOOL_ROOT)
    checks = 0

    expected_mutations = {
        "remove_term",
        "replace_operator",
        "change_authority",
        "change_stage",
        "change_normalization",
        "change_profile_parameterization",
        "add_derivation",
        "remove_derivation",
        "change_candidate_disposition",
    }
    if set(MUTATION_TARGETS) != expected_mutations:
        raise RuntimeError("typed mutation population changed")
    checks += 1
    if set(TARGET_KINDS) != {
        "equation_contract",
        "normative_object",
        "gate_record",
        "candidate",
    }:
        raise RuntimeError("typed target population changed")
    checks += 1
    if len(RESULT_STATUSES) != 9:
        raise RuntimeError("result status population changed")
    checks += 1

    if evaluate_support_predicate([edge("r", "required")], {"r"}) != (
        "exact_invalidation"
    ):
        raise RuntimeError("required support did not invalidate")
    checks += 1
    one_of = [edge("a", "one_of"), edge("b", "one_of")]
    if evaluate_support_predicate(one_of, {"a"}) != "supported":
        raise RuntimeError("one-of support ignored independent support")
    checks += 1
    if evaluate_support_predicate(one_of, {"a", "b"}) != "exact_invalidation":
        raise RuntimeError("exhausted one-of support did not invalidate")
    checks += 1
    if evaluate_support_predicate([edge("c", "conditional")], {"c"}) != (
        "requires_reexecution_from_gate"
    ):
        raise RuntimeError("conditional support overclaimed exactness")
    checks += 1
    if evaluate_support_predicate([edge("n", "negative_boundary")], {"n"}) != (
        "requires_reexecution_from_gate"
    ):
        raise RuntimeError("negative boundary overclaimed activation")
    checks += 1
    if evaluate_support_predicate(
        [edge("i", "indeterminate_requires_review")], {"i"}
    ) != "indeterminate_requires_review":
        raise RuntimeError("indeterminate support did not fail closed")
    checks += 1
    if evaluate_support_predicate([edge("r", "required")], set()) != "supported":
        raise RuntimeError("unmodified support did not remain known")
    checks += 1

    mutation = make_mutation(
        context,
        target_id=A_CONTRACTION,
        target_kind="equation_contract",
        mutation_type="remove_term",
        baseline_record_id=D10_2,
        profile_scope=["A_CI"],
        candidate_scope=[A_CANDIDATE],
        realization_scope=["comparison:A-CI"],
        declared_payload={"term_id": "bounded_contraction_condition"},
    )
    validate_mutation(context, mutation)
    checks += 1
    condition = {
        "target_id": A_CONTRACTION,
        "mutation_type": "remove_term",
        "required_payload": {"term_id": "retained_term"},
    }
    if not mutation_falsifies_closing_precondition(mutation, condition):
        raise RuntimeError("typed closing precondition was not falsified")
    checks += 1
    if mutation_falsifies_closing_precondition(mutation, "non_structured_condition"):
        raise RuntimeError("untyped closing precondition became exact")
    checks += 1
    activation = {
        "target_id": A_CONTRACTION,
        "mutation_type": "remove_term",
        "required_payload": {"term_id": "bounded_contraction_condition"},
    }
    if not mutation_satisfies_activation_condition(mutation, activation):
        raise RuntimeError("typed activation condition did not match")
    checks += 1
    if mutation_satisfies_activation_condition(mutation, "always"):
        raise RuntimeError("source prose activation became exact mutation logic")
    checks += 1
    first = evaluate_mutation(context, mutation)
    second = evaluate_mutation(context, mutation)
    if canonical_bytes(first) != canonical_bytes(second):
        raise RuntimeError("counterfactual evaluation is nondeterministic")
    checks += 1
    if first["claim_boundary"] != {
        "creates_scientific_evidence": False,
        "numeric_effect_prediction": False,
        "positive_claim_beyond_frontier": False,
        "predicts_reexecuted_gate_outcome": False,
    }:
        raise RuntimeError("counterfactual claim boundary is open")
    checks += 1
    if first["structural_result"]["profiles_affected"] != ["A_CI"]:
        raise RuntimeError("A profile scope changed")
    checks += 1

    stale = refresh(copy.deepcopy(mutation))
    stale["baseline_record_digest"] = "0" * 64
    refresh(stale)
    if evaluate_mutation(context, stale)["structural_result"]["invalid_reason"] != (
        "baseline_record_identity_is_stale"
    ):
        raise RuntimeError("stale baseline did not fail closed")
    checks += 1

    unknown_type = copy.deepcopy(mutation)
    unknown_type["mutation_type"] = "weaken"
    refresh(unknown_type)
    if evaluate_mutation(context, unknown_type)["structural_result"]["invalid_reason"] != (
        "mutation_type_not_admitted"
    ):
        raise RuntimeError("unknown mutation type did not fail closed")
    checks += 1

    unknown_target = copy.deepcopy(mutation)
    unknown_target["target_id"] = "missing-contract"
    refresh(unknown_target)
    if evaluate_mutation(context, unknown_target)["structural_result"]["invalid_reason"] != (
        "target_is_not_an_admitted_graph_node"
    ):
        raise RuntimeError("unknown target did not fail closed")
    checks += 1

    profile_leak = copy.deepcopy(mutation)
    profile_leak["profile_scope"] = ["C_CI"]
    profile_leak["realization_scope"] = []
    refresh(profile_leak)
    if evaluate_mutation(context, profile_leak)["structural_result"]["invalid_reason"] != (
        "profile_scope_exceeds_source_scope"
    ):
        raise RuntimeError("profile leak did not fail closed")
    checks += 1

    candidate_leak = copy.deepcopy(mutation)
    candidate_leak["candidate_scope"] = [C_CANDIDATE]
    candidate_leak["realization_scope"] = []
    refresh(candidate_leak)
    if evaluate_mutation(context, candidate_leak)["structural_result"]["invalid_reason"] != (
        "candidate_scope_exceeds_source_scope"
    ):
        raise RuntimeError("candidate leak did not fail closed")
    checks += 1

    realization_leak = copy.deepcopy(mutation)
    realization_leak["realization_scope"] = ["comparison:C-CI"]
    refresh(realization_leak)
    if evaluate_mutation(context, realization_leak)["structural_result"]["invalid_reason"] != (
        "realization_scope_exceeds_candidate_scope"
    ):
        raise RuntimeError("realization leak did not fail closed")
    checks += 1

    missing_candidate = copy.deepcopy(mutation)
    missing_candidate["candidate_scope"] = []
    missing_candidate["realization_scope"] = []
    refresh(missing_candidate)
    if evaluate_mutation(context, missing_candidate)["structural_result"]["invalid_reason"] != (
        "candidate_scope_is_required_for_profile"
    ):
        raise RuntimeError("missing profile candidate did not fail closed")
    checks += 1

    malformed_payload = copy.deepcopy(mutation)
    malformed_payload["declared_payload"] = {"term_id": "x", "effect": "positive"}
    refresh(malformed_payload)
    if evaluate_mutation(context, malformed_payload)["structural_result"]["invalid_reason"] != (
        "declared_payload_fields_not_admitted"
    ):
        raise RuntimeError("arbitrary payload field did not fail closed")
    checks += 1

    numeric = copy.deepcopy(mutation)
    numeric["declared_payload"] = {"term_id": 1.0}
    refresh(numeric)
    if evaluate_mutation(context, numeric)["structural_result"]["invalid_reason"] != (
        "numeric_effect_injection_forbidden"
    ):
        raise RuntimeError("numeric prediction did not fail closed")
    checks += 1

    bad_id = copy.deepcopy(mutation)
    bad_id["mutation_id"] = "ET-C4-MUT-bad"
    expect_error(
        "mutation digest",
        MutationValidationError,
        lambda: validate_mutation(context, bad_id),
    )
    checks += 1

    report = json.loads(
        (SIDE_TOOL_ROOT / "records/ETC4CounterfactualScenarioReport.json").read_text()
    )
    scenarios = {row["scenario_id"]: row for row in report["scenarios"]}
    if report["scenario_count"] != 13:
        raise RuntimeError("scenario report population is malformed")
    checks += 1
    c1 = scenarios["C1"]["result"]
    if c1["structural_result"]["earliest_gates_to_reopen"] != [
        "GRC9V4-CD-D7V2-v1"
    ]:
        raise RuntimeError("Candidate B did not reopen at D7-v2")
    checks += 1
    if c1["structural_result"]["debts_reactivated"]:
        raise RuntimeError("Candidate B route was falsely reactivated exactly")
    checks += 1
    if not c1["structural_result"]["unknown_beyond_evidence_frontier"]:
        raise RuntimeError("Candidate B frontier is empty")
    checks += 1
    if any(
        row["result"]["claim_boundary"]["positive_claim_beyond_frontier"]
        for row in report["scenarios"]
    ):
        raise RuntimeError("scenario crossed the evidence frontier")
    checks += 1
    if "requires_reexecution_from_gate" not in scenarios["C5"]["result"][
        "result_statuses"
    ]:
        raise RuntimeError("bounded-contraction removal skipped reexecution")
    checks += 1
    if any(
        row["result"]["structural_result"].get("fabricated_successor_claims", [])
        for row in report["scenarios"]
    ):
        raise RuntimeError("scenario fabricated a successor claim")
    checks += 1
    if report["exact_debt_reactivation_count"] != 0:
        raise RuntimeError("source-free exact reactivation was emitted")
    checks += 1
    if report["exact_negative_activation_count"] != 0:
        raise RuntimeError("source-free exact negative activation was emitted")
    checks += 1
    if (SIDE_TOOL_ROOT / "records/ETC4CounterfactualScenarioReport.json").stat().st_size > (
        2 * 1024 * 1024
    ):
        raise RuntimeError("counterfactual report copied an excessive artifact surface")
    checks += 1

    print(f"ET_C4_TEST_PASS checks={checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

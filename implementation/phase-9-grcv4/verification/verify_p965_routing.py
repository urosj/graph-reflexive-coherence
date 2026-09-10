#!/usr/bin/env python3
"""Check Tranche 6 routing, reusing accepted numerical verification owners."""

from __future__ import annotations

import argparse
from copy import deepcopy
import importlib
import json
import subprocess
import sys

import phase9_implementation_policy as p
import verify_p964c_rg2b_graph as prior

RECORD = p.PHASE + "tranche-6/P9-6.5-RealizationRouting.json"
REGISTER = p.PHASE + "tranche-1/P9-1.4-SupportAndDependencies.json"
DEBTS = p.PHASE + "tranche-1/P9-1.2-DebtInventory.json"
ROUTING = p.PHASE + "tranche-1/P9-1.3-VerificationRouting.json"
COMP = p.INV + "decisions/GeometryTemporalRealizationComparativeSynthesis.json"
D9 = p.INV + "decisions/D9ResidualDebtLedger.json"
BASE = "739c123"
RECIPES = {
    "CI": (1, "ci", "fixture", ["CI_children", "CI_shared"]),
    "PC": (2, "pc", "fixture", ["PC"]),
    "CI_PC": (3, "cipc", "fixture", ["CI_PC"]),
    "RG2b": (4, "rg2b_graph", "graph_fixture", ["RG2b"]),
}
ACCEPTANCES = {
    "CI_children": "P9-6.1ab-AuditFollowup.json",
    "CI_shared": "P9-6.1c-ExecutionRecord.json",
    "PC": "P9-6.2abc-AuditFollowup.json",
    "CI_PC": "P9-6.3abc-AuditFollowup.json",
    "RG2b": "P9-6.4d-AuditFollowup.json",
}
PC_DISPOSITIONS = [
    (COMP, "/immediate_predecessor_debt_disposition/38", "GTRS-PC-DEBT-COMPARATIVE-SYNTHESIS"),
    (COMP, "/immediate_predecessor_debt_disposition/39", "GTRS-PC-DEBT-CARRIER-DOMAIN-WRITER-AND-PARAMETERS"),
    (D9, "/predecessor_dispositions/37", "GTRS-PC-DEBT-TOPOLOGY-EVENT-INTERSPACE"),
    (D9, "/predecessor_dispositions/40", "GTRS-COMP-DEBT-PC-PARAMETRIC-ENVELOPE-AND-WRITER"),
]


def pc_dispositions():
    result = []
    for path, pointer, debt_id in PC_DISPOSITIONS:
        field, index = pointer.strip("/").split("/")
        row = p.read(p.ROOT / path)[field][int(index)]
        p.require(row["debt_id"] == debt_id, "changed PC disposition identity")
        result.append(dict(path=path, json_pointer=pointer, debt_id=debt_id,
                           status=row["status"],
                           successor=row.get("superseded_by", row.get("successor_verification_obligation_id"))))
    return result


def seeds():
    result = {}
    for realization, (_, module, function, _) in RECIPES.items():
        module = "tests.models.test_grc_v4_" + module
        factory = getattr(importlib.import_module(module), function)
        for candidate in ("A", "C"):
            inputs, _ = factory(candidate=candidate)
            result[candidate + "_" + realization] = dict(
                module=module, function=function, kwargs={"candidate": candidate},
                complete_profile_id=inputs.geometry.reference.profile.complete_profile_id,
            )
    return result


def validate(value, concrete, support):
    require = p.require
    require(value["record_digest"] == p.digest_record(value), "routing digest")
    require(value["iteration_id"] == "P9-6.5"
            and value["status"] == "reviewed_verified_pending_user_acceptance"
            and value["scientific_verdict"] == "PASS_bounded_reconciliation"
            and value["user_accepted"] is False, "routing acceptance boundary")
    require(value["scientific_debts_closed"] == value["public_support_added"]
            == value["new_runtime_iterations_authorized"] == []
            and value["G3_accepted"] is False, "routing promotion")
    expected_refs = {key: p.PHASE + "tranche-6/" + name
                     for key, name in ACCEPTANCES.items()}
    require(set(value["accepted_records"]) == set(expected_refs), "acceptance roster")
    paths = set(expected_refs.values()) | {REGISTER, DEBTS, ROUTING, COMP, D9, p.G2_ACCEPTANCE,
                p.PHASE + "tranche-5/P9-5.4-AuditFollowup.json"}
    require(set(value["source_bindings"]) == paths, "source roster")
    for path in paths:
        raw = p.git(p.ROOT, "show", BASE + ":" + path)
        require((p.ROOT / path).read_bytes() == raw
                and value["source_bindings"][path] == p.sha(raw), "accepted source drift")
    accepted = {}
    for key, path in expected_refs.items():
        require(value["accepted_records"][key] == dict(
            path=path, sha256=value["source_bindings"][path], acceptance_pointer="/acceptance"
        ), "acceptance reference")
        accepted[key] = p.read(p.ROOT / path)["acceptance"]
        require(accepted[key]["status"] == "accepted_by_user"
                and accepted[key]["open_leaf_blockers"] == [], "unaccepted prerequisite")
    require(value["source_git_commit"] == p.git(p.ROOT, "rev-parse", BASE).decode().strip(),
            "routing source commit")
    register = p.read(p.ROOT / REGISTER)["profiles"]
    rows = value["profiles"]
    require(len(rows) == 8 and {r["profile_family"] for r in rows} == set(concrete),
            "missing or duplicate candidate realization")
    for row in rows:
        family = row["profile_family"]
        candidate, realization = family.split("_", 1)
        number, _, _, evidence = RECIPES[realization]
        children = [f"P9-6.{number}" + ("b" if candidate == "A" else "a")]
        children += ["P9-6.4c", "P9-6.4d"] if number == 4 else [f"P9-6.{number}c"]
        require(row["candidate"] == candidate and row["seed"] == concrete[family],
                "wrong concrete candidate seed")
        require(row["numerical_status"] == "accepted_bounded_provisional"
                and row["evidence_refs"] == evidence
                and row["accepted_children"] == children
                and set(children) <= {leaf for key in evidence
                                     for leaf in accepted[key]["accepted_iterations"]},
                "candidate or shared-audit evidence mismatch")
        require(row["authority"] == ["C"] + (["W_A"] if candidate == "A" else [])
                + (["Z4"] if realization in ("PC", "CI_PC") else []), "history ownership")
        index = next(i for i, r in enumerate(register) if r["profile_family"] == family)
        require(row["required_catalog_ref"] == dict(path=REGISTER,
                json_pointer=f"/profiles/{index}/required_catalog_case_ids"), "fixture product")
        require(row["lifecycle_children"] == [f"P9-7.{leaf}-{family}"
                for leaf in ("1", "2a", "2b", "3", "4", "5", "6")]
                and row["lifecycle_status"] == "pending_exact_scope_binding_and_execution"
                and row["conformance_child"] == "P9-7.7-" + family
                and row["G2_gate"] == "P9-G2[" + family + "]"
                and row["G2_status"] == "pending_full_applicable_product"
                and row["accepted_generic_profile_ids"] == []
                and row["depends_on_unrelated_siblings"] is False, "lifecycle/support route")
    require(value["prior_OS_scope"]["C_OS"] == dict(G2_acceptance=p.G2_ACCEPTANCE,
            accepted_generic_profile_ids=sorted(support)) and len(support) == 1,
            "changed exact public support")
    require(value["prior_OS_scope"]["A_OS"] == dict(
        acceptance=p.PHASE + "tranche-5/P9-5.4-AuditFollowup.json",
        numerical_status="accepted_provisional", lifecycle_status="pending", G2_status="pending"
    ), "A_OS scope")
    require(value["migration_classes_ref"] == dict(path=REGISTER, json_pointer="/migration_classes")
            and value["retained_deferred_gates_ref"] == dict(path=DEBTS, json_pointer="/deferred_gates"),
            "lost migration or scientific obligations")
    expected = []
    for key, rows in p.read(p.ROOT / ROUTING).items():
        if isinstance(rows, list):
            for index, row in enumerate(rows):
                if isinstance(row, dict) and "P9-6.5" in row.get("phase9_route", {}).get("phase9_iterations", []):
                    oid = row["obligation_id"]
                    expected.append(dict(obligation_id=oid, source_ref=dict(path=ROUTING,
                        json_pointer=f"/{key}/{index}"),
                        disposition="scoped_evidence_reconciled_full_obligation_pending",
                        next_owners=["P9-7.2a", "P9-7.2b", "P9-7.7"] if oid.startswith("D11")
                        else ["P9-EVID-ENVELOPES"]))
    require(value["forward_obligations"] == expected and len(expected) == 2,
            "forward scientific obligation scope")
    require(value["historical_PC_debt_dispositions"] == pc_dispositions(),
            "resolved PC design debt was reopened or misrouted")
    require(value["RG2b_scope"] == dict(
        numerical_variant="generalized_finite_graph_after_scalar_foundation",
        shared_audit="P9-6.4d", regularity="completion_relative_Lipschitz_only",
        indefinite_entry_chart_invariance=False,
        optional_32_vertex_full_campaign="not_established_not_required_without_explicit_request"
    ), "RG2b graph/regularity/optional scope")
    require(value["verification"]["numerical_tests_rerun"] == 0
            and value["verification"]["optional_32_vertex_campaign_run"] is False,
            "invented numerical execution")
    acceptance = value.get("acceptance")
    if acceptance is not None:
        require(acceptance["status"] == "accepted_by_user"
                and acceptance["accepted_iterations"] == ["P9-6.5"]
                and acceptance["profiles_reviewed"] == sorted(concrete)
                and acceptance["scientific_verdict"] == "PASS"
                and acceptance["open_leaf_blockers"] == []
                and acceptance["tranche_6_status"] == "accepted_closed"
                and acceptance["tranche_iterations"] == sorted(
                    {leaf for record in accepted.values()
                     for leaf in record["accepted_iterations"]} | {"P9-6.5"})
                and acceptance["next_work"] == "P9-7.1-A_OS"
                and acceptance["new_runtime_iterations_authorized"] == []
                and acceptance["public_support_added"] == []
                and acceptance["G3_accepted"] is False
                and acceptance["reviewed_record_digest"] == p.digest_record(
                    {key: item for key, item in value.items() if key != "acceptance"}),
                "invalid Tranche 6 acceptance")


def pressure(value, concrete, support):
    # Recompute digests so these challenges reach semantic routing checks.
    mutations = {
        "missing_candidate": lambda v: v["profiles"].pop(),
        "duplicate_candidate": lambda v: v["profiles"].append(deepcopy(v["profiles"][0])),
        "other_candidate_seed": lambda v: v["profiles"][0].update(seed=v["profiles"][1]["seed"]),
        "missing_shared_audit": lambda v: v["profiles"][0].update(evidence_refs=["CI_children"]),
        "wrong_candidate_child": lambda v: v["profiles"][0].update(accepted_children=["P9-6.1a", "P9-6.1c"]),
        "conflated_history": lambda v: v["profiles"][2].update(authority=["C", "Z4"]),
        "unsupported_G2": lambda v: v["profiles"][0].update(G2_status="accepted"),
        "sibling_hold": lambda v: v["profiles"][0].update(depends_on_unrelated_siblings=True),
        "dropped_debt": lambda v: v["forward_obligations"].pop(),
        "reopen_resolved_PC_debt": lambda v: v["historical_PC_debt_dispositions"][0].update(status="pending"),
        "optional_skip_as_pass": lambda v: v["RG2b_scope"].update(optional_32_vertex_full_campaign="passed"),
        "C1_promotion": lambda v: v["RG2b_scope"].update(regularity="C1"),
        "partial_fixture_product": lambda v: v["profiles"][0]["required_catalog_ref"].update(json_pointer="/profiles/0/ordinary"),
    }
    for name, mutate in mutations.items():
        changed = deepcopy(value)
        mutate(changed)
        changed["record_digest"] = p.digest_record(changed)
        try:
            validate(changed, concrete, support)
        except ValueError:
            continue
        raise AssertionError("routing pressure did not reject " + name)
    return sorted(mutations)


def check():
    from pygrc.models.grc_v4_profile import list_supported_profiles

    value, concrete, support = p.read(p.ROOT / RECORD), seeds(), list_supported_profiles()
    validate(value, concrete, support)
    for name in value["covariance_examples"]:
        module, cls, method = name.rsplit(".", 2)
        p.require(callable(getattr(getattr(importlib.import_module(module), cls), method)),
                  "missing existing covariance witness")
    challenges = pressure(value, concrete, support)
    inherited = prior.check()  # Includes historical subjects and live side-tool contract checks once.
    p.require(inherited["status"] == "passed" and inherited["user_accepted"],
              "unverified numerical predecessor")
    sys.path.insert(0, str(p.ROOT / p.SIDE / "tool/src"))
    from grcv4_explorer.phase9_verification import verification_status
    from grcv4_explorer.tooling import managed_node, tool_environment

    tool = p.ROOT / p.SIDE / "tool"
    status = verification_status(p.ROOT)
    p.require(status["current_boundary"] == "passed"
              and "P9-6.5" in status["dependency_ready_leaves"]
              and "P9-7.1-A_OS" not in status["dependency_ready_leaves"]
              and len(status["implementation_scope"]) == 52
              and len(status["permitted_runtime_paths"]) == 40,
              "coordination expanded runtime scope")
    # Feed real API output through the existing browser validator, not another copy.
    subprocess.run([str(managed_node()), "--input-type=module", "-e",
        "import {checkedStatus} from './verification.js'; "
        "let s=''; for await (const x of process.stdin) s+=x; checkedStatus(JSON.parse(s));"],
        input=json.dumps(status), text=True, check=True, cwd=tool / "phase9-web",
        env=tool_environment(), capture_output=True)
    browser = subprocess.run([str(managed_node()), "verification.test.mjs"],
        text=True, check=True, cwd=tool / "phase9-web", env=tool_environment(), capture_output=True)
    print(browser.stdout, file=sys.stderr, end="")
    return dict(status="passed", profile_seeds_reconstructed=len(concrete),
                routing_mutations_rejected=challenges, numerical_tests_rerun=0,
                optional_32_vertex_campaign_run=False, accepted_generic_support=sorted(support),
                P9_6_5_user_accepted=bool(value.get("acceptance")),
                tranche_6_status=value.get("acceptance", {}).get("tranche_6_status", "pending_acceptance"),
                side_tool_API_browser="passed",
                browser_validator="passed", prior=inherited)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(check(), indent=2))

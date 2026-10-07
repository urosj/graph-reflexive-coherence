"""Freeze boundary probes and budgets without running an allocator or solver."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
for directory in (ROOT / "src", ROOT / SIDE / "tool/src"):
    sys.path.insert(0, str(directory))

from pygrc.models.grc_v4_codec import canonical_json_bytes  # noqa: E402

BASE = "implementation/phase-9-grcv4/tranche-8/"
HERE = "implementation/phase-9-grcv4/verification/"
OUTPUT = BASE + "P9-8.4c-BoundaryContract.json"
REVIEW = BASE + "P9-8.4c-BoundaryReview.md"
SELF = HERE + "prepare_p984c_boundaries.py"
TEST = HERE + "test_p984c_boundaries.py"
DEGREES = (36, 37, 38, 43, 44, 45)
ROLES = ("current", "reset")
# These are subjects and ceiling proposals, not imported execution adapters.
FAMILIES = {
    "C_OS": ("COS", "p984b_cos_successor.py", 120),
    "A_OS": ("AOS", "p984b_aos_runtime.py", 120),
    "C_CI": ("CCICompletion", "p984b_cci_runtime.py", 480),
    "A_CI": ("ACI", "p984b_aci_runtime.py", 600),
    "C_PC": ("CPC", "p984b_cpc_runtime.py", 480),
    "A_PC": ("APC", "p984b_apc_runtime.py", 600),
    "C_CI_PC": ("CCIPC", "p984b_ccipc_runtime.py", 900),
    "A_CI_PC": ("ACIPC", "p984b_acipc_runtime.py", 900),
    "C_RG2b": ("CRG2b", "p984b_crg2b_runtime.py", 900),
    "A_RG2b": ("ARG2b", "p984b_arg2b_runtime.py", 1800),
}
CONTRACTS = ("N-CAPACITY-FLOOR", "TREE-AND-CAPACITY", "GROWTH-PHASE", "LIFECYCLE-READMISSION")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def seal(value):
    return {**value, "record_digest": digest({k: v for k, v in value.items() if k != "record_digest"})}


def geometry(degree, chirality, phase):
    """Integer formula from spec; no production count/allocator helper."""
    require(type(degree) is int and degree >= 9, "degree outside contract")
    require(type(chirality) is int and chirality in (-1, 1), "chirality outside contract")
    n = max(4, (degree - 2 + 6) // 7)
    q, rho = divmod(n - 4, 3)
    require(phase is None if rho == 0 else type(phase) is int and phase in (1, 2, 3), "phase outside contract")
    extras = [q] * 3
    for offset in range(rho):
        extras[(phase - 1 + chirality * offset) % 3] += 1
    return dict(module_nodes=n, internal_edges=n - 1, capacity=7 * n + 2,
                unused_capacity=7 * n + 2 - degree, quotient=q, remainder=rho,
                branch_extras=extras, target_vertices=9 + n, target_edges=8 + n)


def layouts():
    rows = []
    for degree in DEGREES:
        n = max(4, (degree + 4) // 7)
        for chirality in (-1, 1):
            for phase in ((1, 2, 3) if (n - 4) % 3 else (None,)):
                rows.append(dict(id=f"P984C-D{degree}-E{chirality}-P{phase or 0}",
                    degree=degree, chirality=chirality, phase=phase,
                    expected=geometry(degree, chirality, phase),
                    structural_admissibility="valid_under_bound_saturated_source_and_request",
                    numerical_admissibility="not_established_for_new_subject"))
    return rows


def failure_cases():
    """One-fault recipes; null and missing wire keys have different owners."""
    rows = []
    for degree in DEGREES:
        active = degree != 45
        for chirality in (-1, 1):
            for phase in ((None,) if active else (1, 2, 3)):
                rows.append(dict(id=f"semantic-D{degree}-E{chirality}-P{phase or 0}",
                    base_layout=f"P984C-D{degree}-E{chirality}-P{1 if active else 0}",
                    operation="replace", field="growth_phase", value=phase,
                    expected_stage="typed_request_admission", expected_code=(
                        "module_growth_phase_required" if active else "reject_noncanonical_inactive_growth_phase")))
    rows.append(dict(id="null-chirality", base_layout="P984C-D37-E1-P1", operation="replace",
        field="module_chirality", value=None, expected_stage="typed_request_admission",
        expected_code="module_chirality_required"))
    wire = [("remove", "growth_phase", None), ("remove", "module_chirality", None),
            ("replace", "growth_phase", True), ("replace", "growth_phase", 0),
            ("replace", "growth_phase", 4), ("replace", "growth_phase", "1"),
            ("replace", "module_chirality", True), ("replace", "module_chirality", 0),
            ("replace", "target_effective_degree", True), ("replace", "target_effective_degree", 8),
            ("replace", "target_effective_degree", 37.5), ("replace", "target_effective_degree", "37"),
            ("replace_raw_json_token", "target_effective_degree", "9007199254740992"),
            ("insert", "extra_phase", 1)]
    for i, (operation, field, value) in enumerate(wire):
        rows.append(dict(id=f"wire-{i:02d}", base_layout="P984C-D37-E1-P1", operation=operation,
            field=field, value=value, expected_stage="wire_decode", expected_code=None))
    return rows


class Sources:
    def __init__(self, root):
        self.root, self.bindings = Path(root), {}

    def bind(self, name):
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "relative source required")
        raw = (self.root / name).read_bytes()
        self.bindings[name] = dict(path=name, sha256=hashlib.sha256(raw).hexdigest())
        return self.bindings[name]

    def read(self, name):
        self.bind(name)
        return json.loads((self.root / name).read_bytes())

    def ref(self, name, pointer, value):
        return dict(path=name, pointer=pointer, payload_digest=digest(value))


def build(root=ROOT):
    from grcv4_explorer.successor import load_successor_forensic_context
    from grcv4_explorer.forensic import contract_provenance

    sources = Sources(root)
    coverage = sources.read(BASE + "P9-8.4a-Coverage.json")
    owner = next(r for r in coverage["additional_work_register"] if r["owner"] == "P9-8.4c")
    require(set(owner["families"]) == set(FAMILIES) and owner["roles"] == list(ROLES), "coverage owner drift")
    context = load_successor_forensic_context(Path(root), Path(root) / SIDE)
    traces = [contract_provenance(context, "D11-G9-EC-" + name) for name in CONTRACTS]
    for trace in traces:
        for row in trace["rows"]:
            sources.bind(row["source_ref"]["path"])
    for path in (SELF, TEST, "specs/grc-9-v4-spec.md", "specs/grc-v4-spec.md",
                 "specs/grc-v4-contract-schema.json", "docs/reference/EvidenceStorage.md",
                 "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md"):
        sources.bind(path)
    matrix, families, cases, cells = layouts(), [], [], []
    for family, (tag, checker, seconds) in FAMILIES.items():
        name = BASE + f"P9-8.4b-{tag}Cases.json"
        previous = sources.read(name)
        template_name = BASE + "P9-8.4b-AOSOracleInputs.json" if family == "A_OS" else name
        template = sources.read(template_name)
        inputs = previous["initial_inputs"]
        require(inputs["current"] != inputs["reset"], "roles must be distinct")
        sources.bind(HERE + checker)
        comparison = template["cases"][0]["comparison"]
        families.append(dict(family=family,
            initial_inputs=sources.ref(name, "/initial_inputs", inputs),
            inherited_numerical_parameters=sources.ref(name, "/initial_inputs/reference", inputs["reference"]),
            comparison=comparison, comparison_source=sources.ref(template_name, "/cases/0/comparison", comparison),
            budget_status="frozen_required_ceiling_not_new_target_certificate",
            execution_budget_seconds=seconds, budget_kind="operational_not_scientific",
            retained_operand_consumer=HERE + checker,
            readiness="pending_exact_target_oracle_domain_and_runtime_binding",
            new_A_oracle_review_required=family.startswith("A_"),
            raw_completed_result_budget_bytes=64_000_000,
            current_reset_shared_source=True))
        for layout in matrix:
            degree = 45 if layout["phase"] is None else 31
            index, case = next((i, c) for i, c in enumerate(template["cases"])
                if (c["request"]["target_effective_degree"], c["request"]["module_chirality"], c["request"]["growth_phase"])
                == (degree, layout["chirality"], layout["phase"]))
            request = case["request"]
            request_ref = sources.ref(template_name, f"/cases/{index}/request", request)
            # No nominal source identity is asserted to be a fresh native source.
            recipe = dict(template=request_ref, resource_distribution=request["resource_distribution"],
                overrides=dict(target_effective_degree=layout["degree"], module_chirality=layout["chirality"],
                               growth_phase=layout["phase"]),
                fresh_fields=["operation_id", "source_state_digest", "source_graph_digest",
                              "history_policy", "expected_event_id", "expected_target_graph_digest"],
                identity_rule="bind_actual_postbeat_source_then_independently_construct_expected_target",
                new_two_remainder_target_requires_preflight=layout["expected"]["remainder"] == 2)
            case_id = f"{layout['id']}::{family}"
            cases.append(dict(id=case_id, layout=layout["id"], family=family, request_recipe=recipe,
                disposition="pending_exact_reuse_check" if layout["degree"] == 45 else "pending_new_target_prerequisites",
                reuse_case_id=case["case_id"] if layout["degree"] == 45 else None))
            for role in ROLES:
                cells.append(dict(id=f"{layout['id']}::{family}::{role}", layout=layout["id"],
                    family=family, role=role, case_id=case_id,
                    disposition="pending_exact_reuse_check" if layout["degree"] == 45 else "pending_new_target_prerequisites",
                    reuse_case_id=case["case_id"] if layout["degree"] == 45 else None,
                    runtime_executed=False, user_accepted=False))
    value = dict(schema="p984c-boundary-contract-v1", date="2026-10-07", planning_commit="26714bd4",
        work_id="P9-8.4c", disposition="preregistered_contract_pending_review",
        selected_capacity_transitions=[37, 44], selection_reason="required_endpoints_and_their_immediate_integer_neighbors",
        families=families, layouts=matrix, cases=cases, cells=cells, negative_recipes=failure_cases(),
        common_pressure=dict(numerical_credit=False, failure_recipes_shared=True,
            family_dispatch_required=list(FAMILIES), control_degrees=[8, 9, 29, 30, 31],
            integer_valued_float_control=37.0, float_control_expected="existing_JSON_integer_normalization_not_malformed"),
        schedule=dict(source_current_beats=1, source_reset_beats=0, target_beats_per_role=10,
                      dt=1/4096, final_read=True, source_per_family="shared_once_or_exact_bound_reuse"),
        counts=dict(layouts=len(matrix), families=len(families), cases=len(cases), history_cells=len(cells),
            new_history_cells=sum(c["reuse_case_id"] is None for c in cells),
            reuse_candidates=sum(c["reuse_case_id"] is not None for c in cells),
            negative_recipes=len(failure_cases()), accepted_cells=0, executed_cells=0),
        retention=dict(primary=["short_review", "frozen_contract", "focused_tests", "completed_coverage", "worst_bounds"],
            format="shared_context_once_and_only_operands_consumed_by_named_checker",
            max_contract_bytes=2_000_000, max_git_file_bytes=10_000_000,
            large_operand_storage="byte_exact_XZ_via_scripts/evidence_storage.py",
            operational_or_incomplete_runs_retained=False,
            budget_overrun="stop_and_review_retention_design_not_drop_required_operands"),
        prerequisites=["independent_exact_target_graph_and_reference_construction", "both_role_resource_history_maps",
            "target_domain_and_error_bounds", "review_new_A_oracle_scope", "bind_actual_runtime_sources_and_requests"],
        scope_limits=["no_new_native_event_or_step", "no_new_numerical_certificate", "no_parameter_tube_or_trajectory_error_bound",
            "structural_admissibility_is_not_runtime_success", "expected_negative_is_not_positive_coverage",
            "no_8_4b_reopening", "full_atomicity_replay_campaign_owned_by_P9_8_5"],
        authority_traces=traces, source_bindings=sorted(sources.bindings.values(), key=lambda x:x["path"]),
        native_runtime_executed=False, user_accepted=False, aggregate_closed=False)
    return seal(value)


def validate(value, root=ROOT):
    require(canonical_json_bytes(value) == canonical_json_bytes(build(root)), "boundary contract differs from source-bound reconstruction")
    require(value["record_digest"] == seal(value)["record_digest"], "contract digest drift")
    return dict(contract_integrity="passed", **value["counts"], native_runtime_executed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the preregistration, never execute native work")
    args = parser.parse_args()
    if args.emit:
        print(json.dumps(build(), indent=2, ensure_ascii=False, allow_nan=False))
    else:
        value = json.loads((ROOT / OUTPUT).read_bytes())
        print(json.dumps(validate(value), indent=2))


if __name__ == "__main__":
    main()

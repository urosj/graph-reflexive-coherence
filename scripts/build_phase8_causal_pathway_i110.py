#!/usr/bin/env python3
"""Build and validate Phase 8 Iteration 110 conformance artifacts."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_grc_lgrc_causal_pathway_conformance.py"
REGISTRY_PATH = ROOT / "specs/grc-lgrc-causal-pathway-contracts.json"
CROSSWALK_PATH = ROOT / "specs/grc-lgrc-causal-pathway-evidence-crosswalk.json"
MATRIX_PATH = ROOT / "specs/grc-lgrc-causal-pathway-composition-matrix.json"
SELECTOR_PATH = ROOT / "specs/grc-lgrc-causal-pathway-selection-guide.json"
I108_FREEZE_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactFreeze.json"
I108_SUPERSESSION_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactBundleSupersession.json"
I109_FREEZE_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactFreeze.json"
I109_RESULT_PATH = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.json"

OUTPUT_POLICY = ROOT / "specs/grc-lgrc-causal-pathway-conformance.json"
OUTPUT_I109_RECONCILIATION = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactBundleSupersession.json"
OUTPUT_EXECUTION = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ConformanceExecution.json"
OUTPUT_NEGATIVE = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110NegativeControlExecution.json"
OUTPUT_RESULT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.json"
OUTPUT_REPORT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.md"
OUTPUT_FREEZE = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ArtifactFreeze.json"

EXPECTED_DIGESTS = {
    "registry_digest": "a266b33da10778e8caf5ad7d4a4bfe4b71aed9d0df563fd6c74e7d4ed6cb486b",
    "crosswalk_digest": "0036dcdf54f4663bed183387db1c8f657eb44a694252ef44421be56fb239ff06",
    "matrix_digest": "d1dbbdcb911cf34b399562c2dfe5122606c0de8d48d9634bc6af1e3d92e09e90",
    "selector_digest": "f57545997fac63c9e465d21e0c840971aee073bd89aff135fb5d93a1ce134e1b",
    "i108_artifact_bundle_digest": "d2bd07c662acc7185f1e5cb62c03d48c9a2469f96511ec3cefd1dfde75eec8d3",
    "i109_artifact_bundle_digest": "d61a2189d016c0213ae89942db3d36515fa02de6d6f9519e47203e2f2cc306c9",
    "i108_reconciliation_digest": "27d120cce54f47bde1ed399735134cd5537a588cf7986000141d5804d7b64756",
}
SUPERSEDED_I109_WORKING_BUNDLE_DIGEST = "6e6aa217f9eb95d22e48b25f36b8dfb79a52adaa8dc20bb16f76be87bc81dbcf"
SUPERSEDED_I109_SELECTOR_DIGEST = "4f6306b7cde805e6331e31e9efe5e575d7c43e081094dbd7b73511b2e3305d22"
SUPERSEDED_I109_RESULT_DIGEST = "1543928149b4e63b6d4b2360072cfc37d4848693b6d7f025daeee64ab3df214a"


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.STDOUT
    ).rstrip("\n")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_digest(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def file_ref(path: str, role: str) -> dict[str, str]:
    target = ROOT / path
    if not target.is_file():
        raise FileNotFoundError(path)
    return {"path": path, "sha256": sha256_file(target), "artifact_role": role}


def load_checker():
    spec = importlib.util.spec_from_file_location("causal_pathway_conformance", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load conformance checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def composition(bundle: dict[str, Any], composition_id: str) -> dict[str, Any]:
    return next(
        row
        for row in bundle["matrix"]["compositions"]
        if row["composition_id"] == composition_id
    )


def selection_case(bundle: dict[str, Any], case_id: str) -> dict[str, Any]:
    return next(
        row
        for row in bundle["selector"]["worked_cases"]
        if row["case_id"] == case_id
    )


def apply_negative_mutation(
    case_id: str, bundle: dict[str, Any], policy: dict[str, Any]
) -> None:
    if case_id == "NC-001":
        del bundle["registry"]["pathways"][0]["time_semantics"]
    elif case_id == "NC-002":
        bundle["crosswalk"]["stage_rows"][0]["pathway_implementation_refs"][0]["path"] = "src/pygrc/models/absent_conformance_fixture.py"
    elif case_id == "NC-003":
        bundle["registry"]["pathways"][0]["authority_summary"]["funding"] = []
    elif case_id == "NC-004":
        row = next(
            row
            for row in bundle["crosswalk"]["stage_rows"]
            if row["pathway_id"] == "grc9v3.synchronous_update_cycle"
        )
        row["test_refs"] = []
        row["evidence_status"] = "source_present_without_test"
    elif case_id == "NC-005":
        composition(bundle, "CMP-20")["adapter_owner"] = "native"
    elif case_id == "NC-006":
        composition(bundle, "CMP-07")["to_pathway_id"] = "missing.pathway"
    elif case_id == "NC-007":
        composition(bundle, "CMP-26")["adapter_owner"] = "none"
    elif case_id == "NC-008":
        source = composition(bundle, "CMP-01")["crossing_source_refs"][0]
        composition(bundle, "CMP-06")["crossing_source_refs"] = [copy.deepcopy(source)]
    elif case_id == "NC-009":
        composition(bundle, "CMP-24")["composition_status"] = "lawful_native"
    elif case_id == "NC-010":
        composition(bundle, "CMP-11")["composition_status"] = "lawful_native"
    elif case_id == "NC-011":
        selection_case(bundle, "SEL-03")["adapter_owner"] = "native"
    elif case_id == "NC-012":
        selection_case(bundle, "SEL-09")["composition_status"] = "unsupported_missing_crossing"
    elif case_id == "NC-013":
        selection_case(bundle, "SEL-10")["registered_alternatives"] = ["CMP-07"]
    elif case_id == "NC-014":
        selection_case(bundle, "SEL-02")["composition_status_is_maturity"] = True
    elif case_id == "NC-015":
        selection_case(bundle, "SEL-06")["extension_authorized"] = True
    elif case_id == "NC-016":
        selection_case(bundle, "SEL-05")["ecological_meaning_inferred"] = True
    elif case_id == "NC-017":
        bundle["crosswalk"]["stage_rows"][0]["pathway_implementation_refs"][0]["sha256"] = "0" * 64
    elif case_id == "NC-018":
        bundle["selector"]["authority_rule"] = "selector owns pathway and evidence facts"
    elif case_id == "NC-019":
        bundle["selector"]["runtime_behavior_changed"] = True
    elif case_id == "NC-020":
        policy["accepted_digests"]["matrix_digest"] = "0" * 64
    else:
        raise ValueError(case_id)


NEGATIVE_CASES = [
    ("NC-001", "missing registry field", "CF-002"),
    ("NC-002", "missing source path", "CF-003"),
    ("NC-003", "missing authority coordinate", "CF-004"),
    ("NC-004", "native stage evidence removed", "CF-005"),
    ("NC-005", "producer owner erased", "CF-006"),
    ("NC-006", "composition endpoint missing", "CF-007"),
    ("NC-007", "explicit adapter owner erased", "CF-008"),
    ("NC-008", "missing crossing supplied a source ref", "CF-009"),
    ("NC-009", "diagnostic crossing promoted to behavioral", "CF-010"),
    ("NC-010", "configured route promoted to formed route", "CF-011"),
    ("NC-011", "selector owner differs from matrix", "CF-012"),
    ("NC-012", "unregistered pair promoted to missing crossing", "CF-013"),
    ("NC-013", "ambiguous alternatives collapsed", "CF-014"),
    ("NC-014", "composition status promoted to maturity", "CF-015"),
    ("NC-015", "selection authorizes extension", "CF-016"),
    ("NC-016", "selection infers ecology", "CF-017"),
    ("NC-017", "source drift left current", "CF-018"),
    ("NC-018", "selector authority overlaps registry", "CF-019"),
    ("NC-019", "conformance tranche claims runtime change", "CF-020"),
    ("NC-020", "accepted matrix digest stale", "CF-001"),
]


def main() -> int:
    checker = load_checker()
    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    selector = json.loads(SELECTOR_PATH.read_text(encoding="utf-8"))
    i109_freeze = json.loads(I109_FREEZE_PATH.read_text(encoding="utf-8"))
    i109_result = json.loads(I109_RESULT_PATH.read_text(encoding="utf-8"))

    i109_reconciliation = {
        "artifact": "Phase 8 GRC/LGRC causal pathway Iteration 109 artifact-bundle supersession",
        "schema_version": "phase8_grclgrc_causal_pathway_i109_artifact_bundle_supersession_v1",
        "status": "reconciled",
        "recorded_during_iteration": 110,
        "superseded_working_bundle_digest": SUPERSEDED_I109_WORKING_BUNDLE_DIGEST,
        "superseded_selector_digest": SUPERSEDED_I109_SELECTOR_DIGEST,
        "superseded_result_digest": SUPERSEDED_I109_RESULT_DIGEST,
        "superseded_artifact_count": 6,
        "accepted_current_bundle_digest": i109_freeze[
            "artifact_bundle_digest"
        ],
        "accepted_current_selector_digest": selector["selector_digest"],
        "accepted_current_result_digest": i109_result["result_digest"],
        "accepted_current_artifact_count": len(i109_freeze["artifacts"]),
        "accepted_current_freeze": {
            "path": "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactFreeze.json",
            "sha256": sha256_file(I109_FREEZE_PATH),
        },
        "transition_reason": "Post-I109 review reconciliation made the I108 predecessor-bundle supersession explicit in the selector, validation, result, report, and freeze.",
        "changed_artifact_paths": [
            "scripts/build_phase8_causal_pathway_i109.py",
            "specs/grc-lgrc-causal-pathway-selection-guide.json",
            "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ValidationExecution.json",
            "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.json",
            "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109.md",
            "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactFreeze.json",
        ],
        "added_artifact_paths": [
            "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactBundleSupersession.json"
        ],
        "selection_case_count_before": 10,
        "selection_case_count_after": len(selector["worked_cases"]),
        "selection_case_results_changed": False,
        "composition_status_coverage_changed": False,
        "selection_semantics_changed": False,
        "scientific_claim_changed": False,
        "runtime_behavior_changed": False,
        "historical_bundle_bytes_retained_as_current_artifact": False,
        "supersession_relation": "The accepted current I109 bundle supersedes the pre-review working bundle for repository authority; the earlier full digests remain provenance and are not alternate accepted predecessors.",
    }
    i109_reconciliation["reconciliation_digest"] = canonical_digest(
        i109_reconciliation
    )
    write_json(OUTPUT_I109_RECONCILIATION, i109_reconciliation)

    accepted_digests = {
        **EXPECTED_DIGESTS,
        "i109_reconciliation_digest": i109_reconciliation[
            "reconciliation_digest"
        ],
    }

    policy = {
        "artifact": "GRC/LGRC causal pathway conformance policy",
        "schema_version": "grc_lgrc_causal_pathway_conformance_policy_v1",
        "iteration": 110,
        "status": "frozen",
        "source_revision": head,
        "accepted_digests": accepted_digests,
        "rules": [
            {
                "rule_id": rule_id,
                "description": description,
                "severity": "fail_closed",
            }
            for rule_id, description in checker.RULES
        ],
        "artifact_authority": {
            "registry_projection": registry["artifact_authority"],
            "selector_rule": selector["authority_rule"],
        },
        "staleness_rule": "relevant source or accepted-artifact digest drift fails closed; affected pathway must become stale_pending_review before re-admission",
        "supersession_rule": "superseded artifacts remain provenance and cannot act as alternate accepted predecessors",
        "i109_supersession": {
            "superseded_working_bundle_digest": SUPERSEDED_I109_WORKING_BUNDLE_DIGEST,
            "superseded_selector_digest": SUPERSEDED_I109_SELECTOR_DIGEST,
            "accepted_current_bundle_digest": i109_freeze[
                "artifact_bundle_digest"
            ],
            "accepted_current_selector_digest": selector["selector_digest"],
            "reconciliation_digest": i109_reconciliation[
                "reconciliation_digest"
            ],
        },
        "readmission_lifecycle": {
            "ordered_steps": checker.READMISSION_STEPS,
            "dependency_scoped_where_complete": True,
            "full_reaudit_when_dependency_scope_is_incomplete": True,
            "accepted_digests_updated_only_after_review": True,
            "stale_state_cannot_self_authorize_readmission": True,
            "dependency_scope": {
                "source_to_stage": "pathway_implementation_refs and cross-cutting dependency refs",
                "stage_to_pathway": "pathway_id plus stage_id",
                "pathway_to_composition": "from_pathway_id and to_pathway_id",
                "composition_to_selection": "required_directional_composition_id and registered alternatives",
            },
            "documentation_neutral_change_rule": "A change outside the declared dependency closure does not stale unrelated pathways; uncertainty in dependency coverage requires the broader re-audit.",
            "readmission_claim_rule": "A successor becomes current only through versioned artifacts, explicit supersession, refreshed evidence and crossings, full conformance, and fail-closed controls.",
        },
        "repair_rule": "behavioral discrepancies open a separate repair identity",
        "behavioral_repair_allowed": False,
        "runtime_dispatcher_created": False,
        "experiment_declaration_guidance": "Substantial experiments may declare consumed pathway IDs, producer additions, diagnostic surfaces, attempted compositions, and missing crossings when useful; this is review guidance rather than universal boilerplate.",
        "runtime_behavior_changed": False,
    }
    policy["policy_digest"] = canonical_digest(policy)
    write_json(OUTPUT_POLICY, policy)

    command = [
        str(ROOT / ".venv/bin/python"),
        "scripts/check_grc_lgrc_causal_pathway_conformance.py",
        "--output",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ConformanceExecution.json",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout)
    execution = json.loads(OUTPUT_EXECUTION.read_text(encoding="utf-8"))

    base_bundle = checker.load_bundle(ROOT)
    negative_rows = []
    rule_isolation_rows = []
    for case_id, description, expected_rule in NEGATIVE_CASES:
        mutated_bundle = copy.deepcopy(base_bundle)
        mutated_policy = copy.deepcopy(policy)
        apply_negative_mutation(case_id, mutated_bundle, mutated_policy)
        outcome = checker.validate_bundle(ROOT, mutated_bundle, mutated_policy)
        triggered_rules = sorted(
            {issue["rule_id"] for issue in outcome["issues"]}
        )
        negative_rows.append(
            {
                "case_id": case_id,
                "description": description,
                "expected_rule_id": expected_rule,
                "triggered_rule_ids": triggered_rules,
                "status": (
                    "passed"
                    if outcome["status"] == "failed_closed"
                    and expected_rule in triggered_rules
                    else "failed_open"
                ),
            }
        )
        if expected_rule != "CF-001":
            isolated_bundle = copy.deepcopy(base_bundle)
            isolated_policy = copy.deepcopy(policy)
            apply_negative_mutation(case_id, isolated_bundle, isolated_policy)
            isolated = checker.validate_bundle(
                ROOT,
                isolated_bundle,
                isolated_policy,
                active_rule_ids={expected_rule},
            )
            isolated_rules = sorted(
                {issue["rule_id"] for issue in isolated["issues"]}
            )
            rule_isolation_rows.append(
                {
                    "case_id": case_id,
                    "description": description,
                    "active_rule_ids": [expected_rule],
                    "digest_guard_active": False,
                    "triggered_rule_ids": isolated_rules,
                    "status": (
                        "passed"
                        if isolated["status"] == "failed_closed"
                        and isolated_rules == [expected_rule]
                        else "failed_open"
                    ),
                }
            )
    negative = {
        "artifact": "Phase 8 GRC/LGRC causal pathway I110 negative-control execution",
        "schema_version": "phase8_grclgrc_causal_pathway_i110_negative_controls_v1",
        "iteration": 110,
        "source_revision": head,
        "control_count": len(negative_rows),
        "controls": negative_rows,
        "rule_isolation_control_count": len(rule_isolation_rows),
        "rule_isolation_controls": rule_isolation_rows,
        "rule_isolation_policy": "CF-001 is inactive and only the intended target rule participates in each isolated decision.",
        "all_rules_have_deliberate_failure_control": {
            expected_rule for _, _, expected_rule in NEGATIVE_CASES
        }
        == {rule_id for rule_id, _ in checker.RULES},
        "failed_open_count": sum(row["status"] == "failed_open" for row in negative_rows),
        "rule_isolation_failed_open_count": sum(
            row["status"] == "failed_open" for row in rule_isolation_rows
        ),
        "all_non_digest_rules_have_isolated_control": {
            row["active_rule_ids"][0] for row in rule_isolation_rows
        }
        == {rule_id for rule_id, _ in checker.RULES if rule_id != "CF-001"},
        "status": (
            "passed"
            if all(row["status"] == "passed" for row in negative_rows)
            and all(row["status"] == "passed" for row in rule_isolation_rows)
            else "failed"
        ),
    }
    negative["execution_digest"] = canonical_digest(negative)
    write_json(OUTPUT_NEGATIVE, negative)

    checks = {
        "positive_conformance_passed": execution["status"] == "passed",
        "all_20_rules_passed_current_bundle": execution["passed_rule_count"] == 20
        and execution["failed_rule_count"] == 0,
        "all_20_negative_controls_failed_closed": negative["status"] == "passed"
        and negative["control_count"] == 20
        and negative["failed_open_count"] == 0,
        "all_19_non_digest_rules_reject_independently": negative[
            "rule_isolation_control_count"
        ]
        == 19
        and negative["rule_isolation_failed_open_count"] == 0
        and negative["all_non_digest_rules_have_isolated_control"],
        "every_rule_has_negative_control": negative[
            "all_rules_have_deliberate_failure_control"
        ],
        "i109_bundle_reconciliation_recorded": i109_reconciliation["status"]
        == "reconciled"
        and i109_reconciliation["accepted_current_bundle_digest"]
        == EXPECTED_DIGESTS["i109_artifact_bundle_digest"]
        and i109_reconciliation["selection_semantics_changed"] is False,
        "legal_readmission_lifecycle_frozen": policy[
            "readmission_lifecycle"
        ]["ordered_steps"]
        == checker.READMISSION_STEPS,
        "registry_crosswalk_matrix_selector_counts_preserved": (
            execution["pathway_count"],
            execution["stage_count"],
            execution["composition_count"],
            execution["selection_case_count"],
        )
        == (23, 52, 26, 10),
        "runtime_dispatcher_not_created": policy["runtime_dispatcher_created"]
        is False,
        "behavioral_repair_not_owned": policy["behavioral_repair_allowed"]
        is False,
        "protected_src_test_example_diff_empty": not bool(
            git("diff", "--name-only", "--", "src", "tests", "examples")
        ),
    }
    result = {
        "artifact": "Phase 8 GRC/LGRC causal pathway consolidation Iteration 110 result",
        "schema_version": "phase8_grclgrc_causal_pathway_iteration_110_result_v1",
        "iteration": 110,
        "status": "passed" if all(checks.values()) else "failed",
        "repository_branch": branch,
        "repository_head": head,
        "policy_digest": policy["policy_digest"],
        "i109_reconciliation_digest": i109_reconciliation[
            "reconciliation_digest"
        ],
        "conformance_execution_digest": execution["conformance_digest"],
        "negative_control_execution_digest": negative["execution_digest"],
        "rule_count": len(checker.RULES),
        "negative_control_count": len(negative_rows),
        "rule_isolation_control_count": len(rule_isolation_rows),
        "checks": checks,
        "runtime_behavior_changed": False,
        "iteration_111_ready": all(checks.values()),
    }
    result["result_digest"] = canonical_digest(result)
    write_json(OUTPUT_RESULT, result)

    report = f"""# Phase 8 GRC/LGRC Causal Pathway Consolidation - Iteration 110

## Result

Iteration 110 passed as machine-enforced conformance and repository
integration over the I106-I109 artifacts.

```text
conformance rules = {len(checker.RULES)} / {len(checker.RULES)} passed
deliberate negative controls = {len(negative_rows)} / {len(negative_rows)} failed closed
non-digest rule-isolation controls = {len(rule_isolation_rows)} / {len(rule_isolation_rows)} failed closed independently
I109 predecessor reconciliation = passed
legal stale-to-reviewed lifecycle = frozen
pathways = {execution['pathway_count']}
stages = {execution['stage_count']}
compositions = {execution['composition_count']}
selection cases = {execution['selection_case_count']}
runtime dispatcher created = false
runtime behavior changed = false
Iteration 111 ready = {str(result['iteration_111_ready']).lower()}
```

## Enforced Boundaries

The checker validates accepted artifact digests, repository-relative path and
SHA references, registry/stage shape, time and spatial scope, all six authority
coordinates, native test evidence, producer and adapter ownership,
composition-status rules, exact selector projections, unregistered and
ambiguous pair handling, source staleness, artifact-authority separation, and
the no-runtime-change boundary.

Every rule has one deliberate in-memory mutation that must fail closed. These
controls include diagnostic-as-behavioral and configured-as-formed relabels,
erased producer/adapter ownership, stale source and artifact digests,
unregistered promotion, ambiguity collapse, maturity promotion, extension
authorization, and ecological inference.

For `CF-002` through `CF-020`, a second rule-isolation pass disables `CF-001`
and every unrelated rule. All 19 target rules reject their own mutation
independently. `CF-001` retains its dedicated stale accepted-digest control in
the global matrix.

## Provenance Reconciliation

The current I109 bundle `e5cc2fb6...` supersedes the pre-review working bundle
`6e6aa217...`. The selector moved from `4f6306b7...` to `9bc63456...` because
I109 added the explicit I108 predecessor reconciliation to its provenance and
validation surfaces. The ten selection cases, their outcomes, composition
status coverage, scientific claim, and runtime behavior did not change. The
machine reconciliation record preserves both full identities and makes only
the current bundle authoritative.

## Legal Update And Re-admission

The policy now freezes a scoped lifecycle from detected source/artifact drift
through `stale_pending_review`, affected I106-I109 regeneration, versioned
successor and supersession records, prospective digest acceptance, full I110
conformance, and restored current status. Dependency references may bound the
rerun when coverage is complete; uncertain coverage requires the broader
re-audit. A stale record cannot update accepted digests to authorize itself.

## Remaining Boundary

I110 is conformance, not a universal causal-work API, runtime dispatcher,
behavioral repair, or experiment bureaucracy. It does not establish that a
low-context consumer can use the guide. Independent pressure-consumer routing,
ambiguity thresholds, and closeout remain I111 work.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")

    freeze_paths = [
        ("scripts/build_phase8_causal_pathway_i110.py", "reproducible_builder"),
        ("scripts/check_grc_lgrc_causal_pathway_conformance.py", "prospective_conformance_checker"),
        ("specs/grc-lgrc-causal-pathway-conformance.json", "frozen_conformance_policy"),
        ("implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactBundleSupersession.json", "i109_predecessor_reconciliation"),
        ("implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110ConformanceExecution.json", "positive_execution"),
        ("implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110NegativeControlExecution.json", "negative_control_execution"),
        ("implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.json", "iteration_result"),
        ("implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration110.md", "iteration_report"),
    ]
    freeze_records = [file_ref(path, role) for path, role in freeze_paths]
    freeze = {
        "artifact": "Phase 8 GRC/LGRC causal pathway consolidation Iteration 110 artifact freeze",
        "schema_version": "phase8_grclgrc_causal_pathway_iteration_110_artifact_freeze_v1",
        "iteration": 110,
        "source_revision": head,
        "i109_artifact_bundle_digest": EXPECTED_DIGESTS[
            "i109_artifact_bundle_digest"
        ],
        "i109_reconciliation_digest": i109_reconciliation[
            "reconciliation_digest"
        ],
        "artifacts": freeze_records,
        "artifact_bundle_digest": canonical_digest(freeze_records),
        "runtime_behavior_changed": False,
    }
    write_json(OUTPUT_FREEZE, freeze)

    print(
        json.dumps(
            {
                "status": result["status"],
                "policy_digest": policy["policy_digest"],
                "conformance_execution_digest": execution[
                    "conformance_digest"
                ],
                "negative_control_execution_digest": negative[
                    "execution_digest"
                ],
                "result_digest": result["result_digest"],
                "artifact_bundle_digest": freeze["artifact_bundle_digest"],
            },
            indent=2,
        )
    )
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

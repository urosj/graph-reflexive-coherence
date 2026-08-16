#!/usr/bin/env python3
"""Validate the frozen GRC/LGRC causal-pathway contract bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


RULES = [
    ("CF-001", "Accepted artifact and predecessor digests must match."),
    ("CF-002", "Registry entries and stages must satisfy the frozen schema and version fields."),
    ("CF-003", "Referenced repository paths and SHA-256 values must resolve."),
    ("CF-004", "Every pathway and stage must expose complete time, space, and authority coordinates."),
    ("CF-005", "Native and native-with-configured-semantics stages must retain current test evidence."),
    ("CF-006", "Producer pathways and compositions must retain explicit producer ownership."),
    ("CF-007", "Composition endpoints, statuses, and crossing evidence must satisfy matrix rules."),
    ("CF-008", "Explicit-adapter compositions must retain adapter identity and non-native ownership."),
    ("CF-009", "Registered missing crossings must remain explicit absences rather than endpoint inference."),
    ("CF-010", "Diagnostic-only crossings must not be promoted to behavioral crossings."),
    ("CF-011", "Configured routes and candidates must not be promoted to formed routes or candidates."),
    ("CF-012", "Selection results must resolve to current pathway and composition identities."),
    ("CF-013", "Unregistered pairs must remain unclassified until a source audit registers them."),
    ("CF-014", "Ambiguous registered crossings must retain all alternatives until semantics disambiguate them."),
    ("CF-015", "Composition status must not be used as a maturity score."),
    ("CF-016", "Selection must not authorize an extension."),
    ("CF-017", "Substrate selection must not infer ecological or agentic meaning."),
    ("CF-018", "Relevant source drift must fail closed as stale_pending_review."),
    ("CF-019", "Registry, crosswalk, matrix, and selector authority must remain non-overlapping."),
    ("CF-020", "The consolidation bundle must not claim runtime behavior changes or behavioral repair."),
]

AUTHORITY_KEYS = {
    "direction",
    "funding",
    "eligibility",
    "scheduling",
    "commit",
    "reception",
}
STAGE_AUTHORITY_FIELDS = {
    "direction_authority",
    "funding_authority",
    "eligibility_authority",
    "scheduling_authority",
    "commit_authority",
    "reception_authority",
}
COMPOSITION_STATUSES = {
    "lawful_native",
    "lawful_with_explicit_adapter",
    "diagnostic_only",
    "producer_mediated",
    "unsupported_missing_crossing",
    "invalid_relabel",
}
READMISSION_STEPS = [
    "detect relevant source or authority-artifact drift",
    "mark affected pathways stale_pending_review and block dependent selection",
    "derive affected stages pathways compositions and selection cases from current dependency references",
    "rerun affected I106 classification and source digests",
    "rerun affected I107 source test evidence and claim ceilings",
    "rerun affected I108 directional crossings and controls",
    "rerun affected I109 selections and ambiguity handling",
    "issue versioned successor artifacts and explicit supersession records",
    "update accepted digests prospectively after review",
    "run full I110 conformance global negatives and rule isolation",
    "restore current status only after every affected dependency passes",
]


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


def digest_without(document: dict[str, Any], field: str) -> str:
    return canonical_digest({key: value for key, value in document.items() if key != field})


def walk_records(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_records(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_records(child)


def load_bundle(root: Path) -> dict[str, Any]:
    paths = {
        "registry": "specs/grc-lgrc-causal-pathway-contracts.json",
        "crosswalk": "specs/grc-lgrc-causal-pathway-evidence-crosswalk.json",
        "matrix": "specs/grc-lgrc-causal-pathway-composition-matrix.json",
        "selector": "specs/grc-lgrc-causal-pathway-selection-guide.json",
        "i108_freeze": "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactFreeze.json",
        "i108_supersession": "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration108ArtifactBundleSupersession.json",
        "i109_freeze": "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactFreeze.json",
        "i109_reconciliation": "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration109ArtifactBundleSupersession.json",
    }
    return {
        key: json.loads((root / path).read_text(encoding="utf-8"))
        for key, path in paths.items()
    }


def add_issue(
    issues: list[dict[str, str]], rule_id: str, location: str, message: str
) -> None:
    issues.append({"rule_id": rule_id, "location": location, "message": message})


def validate_bundle(
    root: Path,
    bundle: dict[str, Any],
    policy: dict[str, Any],
    active_rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    registry = bundle["registry"]
    crosswalk = bundle["crosswalk"]
    matrix = bundle["matrix"]
    selector = bundle["selector"]
    i108_freeze = bundle["i108_freeze"]
    i108_supersession = bundle["i108_supersession"]
    i109_freeze = bundle["i109_freeze"]
    i109_reconciliation = bundle["i109_reconciliation"]

    actual_digests = {
        "registry_digest": digest_without(registry, "registry_digest"),
        "crosswalk_digest": digest_without(crosswalk, "crosswalk_digest"),
        "matrix_digest": digest_without(matrix, "matrix_digest"),
        "selector_digest": digest_without(selector, "selector_digest"),
        "i108_artifact_bundle_digest": canonical_digest(i108_freeze.get("artifacts", [])),
        "i109_artifact_bundle_digest": canonical_digest(i109_freeze.get("artifacts", [])),
        "i108_reconciliation_digest": digest_without(i108_supersession, "reconciliation_digest"),
        "i109_reconciliation_digest": digest_without(i109_reconciliation, "reconciliation_digest"),
    }
    declared_digests = {
        "registry_digest": registry.get("registry_digest"),
        "crosswalk_digest": crosswalk.get("crosswalk_digest"),
        "matrix_digest": matrix.get("matrix_digest"),
        "selector_digest": selector.get("selector_digest"),
        "i108_artifact_bundle_digest": i108_freeze.get("artifact_bundle_digest"),
        "i109_artifact_bundle_digest": i109_freeze.get("artifact_bundle_digest"),
        "i108_reconciliation_digest": i108_supersession.get("reconciliation_digest"),
        "i109_reconciliation_digest": i109_reconciliation.get("reconciliation_digest"),
    }
    for name, expected in policy["accepted_digests"].items():
        actual = actual_digests.get(name)
        if actual != expected or declared_digests.get(name) != expected:
            add_issue(issues, "CF-001", name, f"accepted digest mismatch: expected {expected}, got {actual}")
    if digest_without(policy, "policy_digest") != policy.get("policy_digest"):
        add_issue(issues, "CF-001", "policy.policy_digest", "conformance policy digest does not match its content")

    expected_policy_rules = [
        {
            "rule_id": rule_id,
            "description": description,
            "severity": "fail_closed",
        }
        for rule_id, description in RULES
    ]
    if (
        policy.get("schema_version")
        != "grc_lgrc_causal_pathway_conformance_policy_v1"
        or policy.get("status") != "frozen"
        or policy.get("rules") != expected_policy_rules
    ):
        add_issue(issues, "CF-002", "policy", "policy schema, status, or fail-closed rule table changed")

    if selector.get("registry_digest") != registry.get("registry_digest"):
        add_issue(issues, "CF-001", "selector.registry_digest", "selector does not consume current registry digest")
    if selector.get("crosswalk_digest") != crosswalk.get("crosswalk_digest"):
        add_issue(issues, "CF-001", "selector.crosswalk_digest", "selector does not consume current crosswalk digest")
    if selector.get("matrix_digest") != matrix.get("matrix_digest"):
        add_issue(issues, "CF-001", "selector.matrix_digest", "selector does not consume current matrix digest")
    reconciliation = selector.get("i108_predecessor_reconciliation", {})
    if reconciliation.get("reconciliation_digest") != i108_supersession.get("reconciliation_digest"):
        add_issue(issues, "CF-001", "selector.i108_predecessor_reconciliation", "selector predecessor reconciliation is stale")
    if i108_supersession.get("accepted_current_bundle_digest") != i108_freeze.get("artifact_bundle_digest"):
        add_issue(issues, "CF-001", "i108_supersession", "accepted I108 bundle does not match current freeze")
    if (
        i109_reconciliation.get("accepted_current_bundle_digest")
        != i109_freeze.get("artifact_bundle_digest")
        or i109_reconciliation.get("accepted_current_selector_digest")
        != selector.get("selector_digest")
        or i109_reconciliation.get("superseded_working_bundle_digest")
        != policy.get("i109_supersession", {}).get(
            "superseded_working_bundle_digest"
        )
        or i109_reconciliation.get("superseded_selector_digest")
        != policy.get("i109_supersession", {}).get("superseded_selector_digest")
    ):
        add_issue(
            issues,
            "CF-001",
            "i109_reconciliation",
            "I109 accepted/superseded identities do not match policy and current artifacts",
        )

    required_entry_fields = set(registry.get("required_entry_fields", []))
    required_stage_fields = set(registry.get("required_stage_fields", []))
    pathway_ids: list[str] = []
    stage_keys: list[tuple[str, str]] = []
    for pathway in registry.get("pathways", []):
        pathway_id = pathway.get("pathway_id", "<missing>")
        pathway_ids.append(pathway_id)
        missing = sorted(required_entry_fields - set(pathway))
        if missing or not isinstance(pathway.get("entry_version"), int) or pathway.get("entry_version", 0) < 1:
            add_issue(issues, "CF-002", pathway_id, f"invalid entry schema/version; missing={missing}")
        if pathway.get("mechanism_ownership") not in registry.get("mechanism_ownership_values", []):
            add_issue(issues, "CF-002", pathway_id, "invalid mechanism ownership")
        if pathway.get("availability") not in registry.get("availability_values", []):
            add_issue(issues, "CF-002", pathway_id, "invalid availability")
        if pathway.get("activation") not in registry.get("activation_values", []):
            add_issue(issues, "CF-002", pathway_id, "invalid activation")
        if pathway.get("staleness_state") not in registry.get("staleness_values", []):
            add_issue(issues, "CF-002", pathway_id, "invalid staleness state")
        for field in ("source_commit", "last_verified_commit"):
            value = pathway.get(field, "")
            if len(value) != 40 or any(char not in "0123456789abcdef" for char in value):
                add_issue(issues, "CF-002", f"{pathway_id}.{field}", "revision must be a 40-character lowercase hex digest")
        value = pathway.get("source_digest", "")
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
            add_issue(issues, "CF-002", f"{pathway_id}.source_digest", "source digest must be SHA-256")
        if not isinstance(pathway.get("supersedes"), list) or not isinstance(pathway.get("superseded_by"), list):
            add_issue(issues, "CF-002", pathway_id, "supersession fields must be lists")

        if not pathway.get("time_semantics") or not pathway.get("spatial_scope"):
            add_issue(issues, "CF-004", pathway_id, "time and spatial scope are required")
        authority = pathway.get("authority_summary", {})
        if set(authority) != AUTHORITY_KEYS or any(not authority.get(key) for key in AUTHORITY_KEYS):
            add_issue(issues, "CF-004", pathway_id, "pathway authority summary is incomplete")
        for stage in pathway.get("stage_sequence", []):
            stage_id = stage.get("stage_id", "<missing>")
            stage_keys.append((pathway_id, stage_id))
            missing_stage = sorted(required_stage_fields - set(stage))
            if missing_stage:
                add_issue(issues, "CF-002", f"{pathway_id}:{stage_id}", f"missing stage fields {missing_stage}")
            if not stage.get("time_semantics") or not stage.get("spatial_scope") or any(not stage.get(field) for field in STAGE_AUTHORITY_FIELDS):
                add_issue(issues, "CF-004", f"{pathway_id}:{stage_id}", "stage authority/time/space is incomplete")

    if len(pathway_ids) != len(set(pathway_ids)) or len(stage_keys) != len(set(stage_keys)):
        add_issue(issues, "CF-002", "registry", "pathway or stage IDs are not unique")
    if registry.get("pathway_count") != len(pathway_ids):
        add_issue(issues, "CF-002", "registry.pathway_count", "declared count does not match entries")

    pathway_index = {row["pathway_id"]: row for row in registry.get("pathways", []) if "pathway_id" in row}
    for pathway in registry.get("pathways", []):
        pathway_id = pathway.get("pathway_id", "<missing>")
        for field in ("supersedes", "superseded_by"):
            unresolved = [
                ref
                for ref in pathway.get(field, [])
                if ref not in pathway_index or ref == pathway_id
            ]
            if unresolved:
                add_issue(
                    issues,
                    "CF-002",
                    f"{pathway_id}.{field}",
                    f"supersession references do not resolve cleanly: {unresolved}",
                )
    crosswalk_index = {
        (row.get("pathway_id"), row.get("stage_id")): row
        for row in crosswalk.get("stage_rows", [])
    }
    if set(stage_keys) != set(crosswalk_index):
        add_issue(issues, "CF-002", "crosswalk.stage_rows", "crosswalk stages do not exactly match registry stages")

    ref_records = [
        record
        for document in (
            crosswalk,
            matrix,
            i108_freeze,
            i109_freeze,
            i109_reconciliation,
        )
        for record in walk_records(document)
        if isinstance(record.get("path"), str) and isinstance(record.get("sha256"), str)
    ]
    for record in ref_records:
        relative = record["path"]
        target = root / relative
        if Path(relative).is_absolute() or not target.is_file():
            add_issue(issues, "CF-003", relative, "referenced path is absent or not repository-relative")
        elif sha256_file(target) != record["sha256"]:
            add_issue(issues, "CF-003", relative, "referenced SHA-256 does not match current file")

    changed_pathways: set[str] = set()
    for row in crosswalk.get("stage_rows", []):
        for ref in row.get("pathway_implementation_refs", []):
            target = root / ref.get("path", "")
            if not target.is_file() or sha256_file(target) != ref.get("sha256"):
                changed_pathways.add(row.get("pathway_id", "<missing>"))
    for pathway_id in changed_pathways:
        pathway = pathway_index.get(pathway_id, {})
        if pathway.get("staleness_state") != "stale_pending_review":
            add_issue(issues, "CF-018", pathway_id, "relevant source drift is not marked stale_pending_review")
    for pathway in registry.get("pathways", []):
        if pathway.get("staleness_state") == "stale_pending_review":
            add_issue(
                issues,
                "CF-018",
                pathway.get("pathway_id", "<missing>"),
                "stale pathway remains blocked pending review and re-admission",
            )
    readmission = policy.get("readmission_lifecycle", {})
    if (
        readmission.get("ordered_steps") != READMISSION_STEPS
        or readmission.get("dependency_scoped_where_complete") is not True
        or readmission.get("full_reaudit_when_dependency_scope_is_incomplete")
        is not True
        or readmission.get("accepted_digests_updated_only_after_review") is not True
        or readmission.get("stale_state_cannot_self_authorize_readmission")
        is not True
    ):
        add_issue(
            issues,
            "CF-018",
            "policy.readmission_lifecycle",
            "legal stale-to-reviewed readmission lifecycle is incomplete",
        )

    for pathway in registry.get("pathways", []):
        if pathway.get("mechanism_ownership") not in {"native", "native_with_configured_semantics"}:
            continue
        for stage in pathway.get("stage_sequence", []):
            row = crosswalk_index.get((pathway["pathway_id"], stage["stage_id"]), {})
            if row.get("evidence_status") != "current_source_passed" or not row.get("test_refs"):
                add_issue(issues, "CF-005", f"{pathway['pathway_id']}:{stage['stage_id']}", "native stage lacks current test evidence")

    for pathway in registry.get("pathways", []):
        if pathway.get("mechanism_ownership") == "producer" and not pathway.get("producer_residue"):
            add_issue(issues, "CF-006", pathway["pathway_id"], "producer pathway erased producer residue")

    matrix_rows = matrix.get("compositions", [])
    matrix_index = {row.get("composition_id"): row for row in matrix_rows}
    if len(matrix_index) != len(matrix_rows):
        add_issue(issues, "CF-007", "matrix", "composition IDs are not unique")
    pair_index: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in matrix_rows:
        composition_id = row.get("composition_id", "<missing>")
        from_id = row.get("from_pathway_id")
        to_id = row.get("to_pathway_id")
        pair_index.setdefault((from_id, to_id), []).append(row)
        status = row.get("composition_status")
        if from_id not in pathway_index or to_id not in pathway_index or status not in COMPOSITION_STATUSES:
            add_issue(issues, "CF-007", composition_id, "composition endpoint or status is invalid")
        if row.get("endpoint_coverage_used_as_crossing_evidence") is not False:
            add_issue(issues, "CF-007", composition_id, "endpoint evidence was promoted to crossing evidence")
        if status == "lawful_native" and (not row.get("crossing_source_refs") or not row.get("crossing_evidence_refs")):
            add_issue(issues, "CF-007", composition_id, "lawful native crossing lacks source/current evidence")
        if status == "producer_mediated" and (not row.get("adapter_id") or row.get("adapter_owner") in {None, "none", "native"}):
            add_issue(issues, "CF-006", composition_id, "producer-mediated crossing erased producer ownership")
        if status == "lawful_with_explicit_adapter" and (not row.get("adapter_id") or row.get("adapter_owner") in {None, "none", "native"}):
            add_issue(issues, "CF-008", composition_id, "explicit adapter identity/owner is absent")
        if status == "unsupported_missing_crossing":
            mapping_status = row.get("state_identity_mapping", {}).get("status")
            if (
                row.get("crossing_source_refs")
                or row.get("crossing_evidence_refs")
                or row.get("evidence_status") != "source_audit_missing_crossing"
                or mapping_status
                not in {"missing", "retained_not_consumed", "persisted_not_consumed"}
            ):
                add_issue(issues, "CF-009", composition_id, "missing crossing does not fail closed as an explicit absence")

    for guard_id, expected_status, rule_id in (
        ("CMP-04", "diagnostic_only", "CF-010"),
        ("CMP-05", "invalid_relabel", "CF-010"),
        ("CMP-08", "invalid_relabel", "CF-011"),
        ("CMP-11", "invalid_relabel", "CF-011"),
        ("CMP-24", "diagnostic_only", "CF-010"),
    ):
        if matrix_index.get(guard_id, {}).get("composition_status") != expected_status:
            add_issue(issues, rule_id, guard_id, f"guard composition must remain {expected_status}")

    for case in selector.get("worked_cases", []):
        case_id = case.get("case_id", "<missing>")
        selected_ids = case.get("selected_pathway_ids", [])
        if not selected_ids or any(pathway_id not in pathway_index for pathway_id in selected_ids):
            add_issue(issues, "CF-012", case_id, "selection pathway IDs do not resolve")
        composition_id = case.get("required_directional_composition_id")
        if composition_id:
            row = matrix_index.get(composition_id)
            if row is None or row.get("composition_status") != case.get("composition_status") or row.get("adapter_owner") != case.get("adapter_owner"):
                add_issue(issues, "CF-012", case_id, "selection does not project current matrix identity/status/owner")
        if case.get("resolution_kind") == "unregistered_not_classified":
            candidates = pair_index.get((case.get("from_pathway_id"), case.get("to_pathway_id")), [])
            if candidates or case.get("composition_status") != "unregistered_not_classified":
                add_issue(issues, "CF-013", case_id, "unregistered pair was promoted or has a registered row")
        if case.get("resolution_kind") == "ambiguous_registered_crossing":
            candidates = pair_index.get((case.get("from_pathway_id"), case.get("to_pathway_id")), [])
            expected = {row["composition_id"] for row in candidates}
            if len(expected) < 2 or set(case.get("registered_alternatives", [])) != expected:
                add_issue(issues, "CF-014", case_id, "ambiguous crossing alternatives were collapsed")
        if case.get("composition_status_is_maturity") is not False:
            add_issue(issues, "CF-015", case_id, "composition status was used as maturity")
        if case.get("extension_authorized") is not False:
            add_issue(issues, "CF-016", case_id, "selection authorized an extension")
        if case.get("ecological_meaning_inferred") is not False:
            add_issue(issues, "CF-017", case_id, "selection inferred ecological meaning")

    authority = registry.get("artifact_authority", {})
    expected_authority = policy["artifact_authority"]
    if authority != expected_authority["registry_projection"] or selector.get("authority_rule") != expected_authority["selector_rule"]:
        add_issue(issues, "CF-019", "artifact_authority", "artifact authority boundaries changed or overlap")
    if registry.get("registry_is_evidence_source") is not False or registry.get("registry_is_runtime_dispatcher") is not False:
        add_issue(issues, "CF-019", "registry", "registry was promoted to evidence source or dispatcher")

    for name, document in bundle.items():
        if isinstance(document, dict) and document.get("runtime_behavior_changed") is True:
            add_issue(issues, "CF-020", name, "documentation/conformance tranche claims runtime behavior change")
    for field in (
        "behavioral_repair_allowed",
        "runtime_dispatcher_created",
        "runtime_behavior_changed",
    ):
        if policy.get(field) is not False:
            add_issue(issues, "CF-020", f"policy.{field}", f"I110 policy requires {field}=false")

    known_rule_ids = {rule_id for rule_id, _ in RULES}
    active_rules = known_rule_ids if active_rule_ids is None else active_rule_ids
    if not active_rules or not active_rules <= known_rule_ids:
        raise ValueError("active_rule_ids must be a non-empty subset of known rules")
    issues = [issue for issue in issues if issue["rule_id"] in active_rules]
    rule_results = []
    for rule_id, description in RULES:
        if rule_id not in active_rules:
            continue
        matching = [issue for issue in issues if issue["rule_id"] == rule_id]
        rule_results.append(
            {
                "rule_id": rule_id,
                "description": description,
                "status": "passed" if not matching else "failed_closed",
                "issue_count": len(matching),
            }
        )
    return {
        "status": "passed" if not issues else "failed_closed",
        "validation_scope": (
            "full_conformance"
            if active_rule_ids is None
            else "isolated_rules"
        ),
        "active_rule_ids": sorted(active_rules),
        "rule_count": len(active_rules),
        "passed_rule_count": sum(row["status"] == "passed" for row in rule_results),
        "failed_rule_count": sum(row["status"] != "passed" for row in rule_results),
        "issue_count": len(issues),
        "rule_results": rule_results,
        "issues": issues,
        "actual_digests": actual_digests,
        "pathway_count": len(pathway_ids),
        "stage_count": len(stage_keys),
        "composition_count": len(matrix_rows),
        "selection_case_count": len(selector.get("worked_cases", [])),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("specs/grc-lgrc-causal-pathway-conformance.json"),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--active-rule",
        action="append",
        choices=[rule_id for rule_id, _ in RULES],
        help="Run only the named rule; repeat for a bounded diagnostic subset.",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    policy_path = args.policy if args.policy.is_absolute() else root / args.policy
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    result = validate_bundle(
        root,
        load_bundle(root),
        policy,
        active_rule_ids=set(args.active_rule) if args.active_rule else None,
    )
    result["policy_digest"] = policy["policy_digest"]
    result["conformance_digest"] = canonical_digest(result)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else root / args.output
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build and pressure Phase 8 causal-pathway binding conformance."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any

from pygrc.causal_pathways import CausalPathwayAuthority, PathwayBindingSession
from pygrc.core import PortGraphBackend
from pygrc.models import LGRC9V3, GRC9V3NodeState, GRC9V3State, PortEdge

ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts/check_grc_lgrc_causal_pathway_binding_conformance.py"
POLICY_PATH = ROOT / "specs/grc-lgrc-causal-pathway-binding-conformance.json"
EVIDENCE_DIR = ROOT / "implementation/evidence/causal-pathway-binding"
LOCK_PATH = EVIDENCE_DIR / "i115-native-pathway.lock.json"
RECEIPT_PATH = EVIDENCE_DIR / "i115-native-pathway.receipt.json"
EXECUTION_PATH = EVIDENCE_DIR / "i115-conformance-execution.json"
NEGATIVE_PATH = EVIDENCE_DIR / "i115-negative-control-execution.json"


NEGATIVE_CASES = [
    ("BNC-001", "unknown pathway passed as an admitted binding", "BCF-001"),
    ("BNC-002", "unknown composition passed as a registered binding", "BCF-002"),
    ("BNC-003", "unregistered relation bound without candidate declaration", "BCF-003"),
    ("BNC-004", "candidate described as native and promoted", "BCF-004"),
    ("BNC-005", "CMP-20-style producer identity erased", "BCF-005"),
    ("BNC-006", "explicit adapter identity erased", "BCF-006"),
    ("BNC-007", "diagnostic relation claimed behavioral", "BCF-007"),
    ("BNC-008", "configured route claimed formed", "BCF-008"),
    ("BNC-009", "native arbitration claimed candidate formation", "BCF-009"),
    ("BNC-010", "unsupported crossing treated as existing", "BCF-010"),
    ("BNC-011", "invalid relabel reused as a candidate identity", "BCF-011"),
    ("BNC-012", "stale registry digest accepted", "BCF-012"),
    ("BNC-013", "stale matrix digest accepted", "BCF-013"),
    ("BNC-014", "stale binding-map source-symbol digest accepted", "BCF-014"),
    ("BNC-015", "receipt invokes an undeclared symbol", "BCF-015"),
    ("BNC-016", "wrapper invocation changes locked pathway identity", "BCF-016"),
    ("BNC-017", "runtime records an undeclared alternative path", "BCF-017"),
    ("BNC-018", "binder automatically resolves an ambiguous crossing", "BCF-018"),
    ("BNC-019", "chained compositions synthesize an unregistered claim", "BCF-019"),
    ("BNC-020", "unbound execution presents claim-qualified evidence", "BCF-020"),
]


def load_checker() -> Any:
    spec = importlib.util.spec_from_file_location(
        "causal_pathway_binding_conformance",
        CHECKER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load causal-pathway binding conformance checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_acceptance_anchor(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("binding-acceptance anchor must contain a JSON object")
    return value


def load_accepted_authority(
    acceptance_anchor: dict[str, Any],
    trusted_anchor_digest: str,
) -> CausalPathwayAuthority:
    return CausalPathwayAuthority.load(
        ROOT,
        acceptance_anchor=acceptance_anchor,
        trusted_anchor_digest=trusted_anchor_digest,
    )


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stderr=subprocess.STDOUT,
    ).rstrip("\n")


def _two_node_runtime() -> LGRC9V3:
    graph = PortGraphBackend()
    source = graph.add_node({"label": "source"})
    target = graph.add_node({"label": "target"})
    edge = graph.connect_ports(source, 0, target, 0, {"kind": "route"})
    state = GRC9V3State(
        topology=graph,
        nodes={
            source: GRC9V3NodeState(coherence=1.0),
            target: GRC9V3NodeState(coherence=1.0),
        },
        port_edges={
            edge: PortEdge(
                source,
                1,
                target,
                1,
                conductance=1.0,
                flux_uv=0.0,
            )
        },
        base_conductance={edge: 1.0},
        geometric_length={edge: 1.0},
        temporal_delay={edge: 1.0},
        flux_coupling={edge: 0.0},
    )
    return LGRC9V3.from_state(state, {"dt": 1.0})


def build_positive_fixture(
    acceptance_anchor: dict[str, Any],
    trusted_anchor_digest: str,
) -> None:
    model = _two_node_runtime()
    session = PathwayBindingSession(
        load_accepted_authority(acceptance_anchor, trusted_anchor_digest)
    )
    packet = session.bind_pathway(
        "lgrc9v3.explicit_packet_transport",
        stage_ids=("packet_schedule",),
    )
    schedule = packet.symbol("packet_schedule", instance=model)
    lock = session.freeze_lock()
    schedule(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
    )
    receipt = session.build_receipt()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    lock.write(LOCK_PATH)
    receipt.write(RECEIPT_PATH)


def build_policy(
    checker: Any,
    acceptance_anchor: dict[str, Any],
    trusted_anchor_digest: str,
) -> dict[str, Any]:
    authority = load_accepted_authority(
        acceptance_anchor,
        trusted_anchor_digest,
    )
    accepted = dict(authority.artifact_identities())
    policy = {
        "artifact": "GRC/LGRC causal pathway binding conformance policy",
        "schema_version": "grc_lgrc_causal_pathway_binding_conformance_policy_v1",
        "iteration": 115,
        "status": "frozen",
        "source_revision": git("rev-parse", "HEAD"),
        "accepted_digests": {
            "registry_digest": accepted["registry_digest"],
            "crosswalk_digest": accepted["crosswalk_digest"],
            "matrix_digest": accepted["matrix_digest"],
            "selector_digest": accepted["selector_digest"],
            "consolidation_policy_digest": accepted["conformance_policy_digest"],
            "binding_map_digest": accepted["binding_map_digest"],
        },
        "rules": [
            {
                "rule_id": rule_id,
                "description": description,
                "severity": "fail_closed",
            }
            for rule_id, description in checker.RULES
        ],
        "staleness_rule": (
            "A missing or mismatched independent acceptance anchor, binding-map "
            "drift, symbol drift, or source drift becomes stale_pending_review "
            "and blocks claim-qualified artifacts until reviewed re-admission"
        ),
        "candidate_promotion_automated": False,
        "runtime_dispatcher_created": False,
        "semantic_selection_performed_by_binder": False,
        "unbound_execution_claim_qualified": False,
        "runtime_behavior_changed": False,
    }
    policy["policy_digest"] = checker.canonical_digest(policy)
    return policy


def _composition_record(bundle: dict[str, Any], composition_id: str) -> dict[str, Any]:
    row = next(
        item
        for item in bundle["matrix"]["compositions"]
        if item["composition_id"] == composition_id
    )
    fields = (
        "composition_id",
        "from_pathway_id",
        "from_stage_ids",
        "to_pathway_id",
        "to_stage_ids",
        "composition_status",
        "adapter_id",
        "adapter_owner",
        "authority_retained",
        "authority_transferred",
        "information_lost_or_compressed",
        "claim_ceiling",
        "blocked_relabels",
    )
    return {
        "binding_id": f"composition:{composition_id}",
        **{field: copy.deepcopy(row[field]) for field in fields},
    }


def _candidate_record(
    *,
    candidate_id: str,
    claim_ceiling: str = "experimental_unregistered",
    promotion_status: str = "none",
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "candidate_kind": "composition",
        "purpose": "I115 bounded negative-control fixture",
        "owner": "i115_fixture",
        "consumed_admitted_pathway_ids": [
            "lgrc9v3.explicit_packet_transport",
            "pygrc.restoration_replay_identity",
        ],
        "consumed_admitted_composition_ids": [],
        "proposed_source_pathway_id": "lgrc9v3.explicit_packet_transport",
        "proposed_target_pathway_id": "pygrc.restoration_replay_identity",
        "proposed_relation": "distinct I115 fixture relation",
        "authority": {
            "direction": "unresolved",
            "funding": "unresolved",
            "eligibility": "unresolved",
            "scheduling": "unresolved",
            "commit": "unresolved",
            "reception": "unresolved",
        },
        "producer_residue": [],
        "adapter_residue": [],
        "configured_residue": [],
        "evidence_owner": "i115_fixture",
        "claim_ceiling": claim_ceiling,
        "blocked_claims": [
            "candidate relation is admitted",
            "candidate relation is native",
            "candidate declaration is promotion",
        ],
        "promotion_status": promotion_status,
    }


def apply_negative_mutation(case_id: str, bundle: dict[str, Any]) -> None:
    lock = bundle["lock"]
    receipt = bundle["receipt"]
    lock_binding = lock["declared_pathway_bindings"][0]
    lock_claim = lock["pre_execution_claim_envelope"][
        "constituent_pathway_claim_ceilings"
    ][0]
    if case_id == "BNC-001":
        lock_binding["pathway_id"] = "experiment.not_admitted"
    elif case_id == "BNC-002":
        lock["declared_composition_bindings"].append(
            {
                "binding_id": "composition:CMP-NOT-REGISTERED",
                "composition_id": "CMP-NOT-REGISTERED",
            }
        )
    elif case_id == "BNC-003":
        receipt["pathway_use_graph"]["edges"].append(
            {
                "edge_id": "silent-unregistered-edge",
                "edge_kind": "unregistered_relation",
            }
        )
    elif case_id == "BNC-004":
        lock["candidate_declarations"].append(
            _candidate_record(
                candidate_id="experiment.native_candidate",
                claim_ceiling="lawful_native",
                promotion_status="promoted",
            )
        )
    elif case_id == "BNC-005":
        lock["declared_composition_bindings"].append(
            _composition_record(bundle, "CMP-20")
        )
    elif case_id == "BNC-006":
        lock["declared_composition_bindings"].append(
            _composition_record(bundle, "CMP-26")
        )
    elif case_id == "BNC-007":
        lock["declared_composition_bindings"].append(
            _composition_record(bundle, "CMP-24")
        )
    elif case_id == "BNC-008":
        lock_claim["required_qualifiers"]["configured_residue"] = []
        lock["pre_execution_claim_envelope"]["required_qualifiers"][
            "configured_semantics"
        ] = []
    elif case_id == "BNC-009":
        lock_binding["pathway_id"] = "lgrc9v3.native_route_arbitration"
        lock_claim["pathway_id"] = "lgrc9v3.native_route_arbitration"
        lock_claim["required_qualifiers"]["producer_residue"] = []
    elif case_id == "BNC-010":
        lock["declared_composition_bindings"].append(
            _composition_record(bundle, "CMP-06")
        )
    elif case_id == "BNC-011":
        lock["candidate_declarations"].append(_candidate_record(candidate_id="CMP-05"))
    elif case_id == "BNC-012":
        lock["registry_digest"] = "0" * 64
    elif case_id == "BNC-013":
        lock["matrix_digest"] = "0" * 64
    elif case_id == "BNC-014":
        bundle["bindings"]["stage_bindings"][0]["symbols"][0]["source_sha256"] = (
            "0" * 64
        )
    elif case_id == "BNC-015":
        receipt["actual_stage_symbol_invocations"][0]["symbol_id"] = (
            "experiment:undeclared:symbol"
        )
    elif case_id == "BNC-016":
        receipt["actual_stage_symbol_invocations"][0]["pathway_id"] = (
            "pygrc.restoration_replay_identity"
        )
    elif case_id == "BNC-017":
        lock["allowed_pathway_alternatives"] = [
            {
                "alternative_set_id": "i115.dynamic",
                "pathway_ids": [
                    "lgrc9v3.explicit_packet_transport",
                    "pygrc.restoration_replay_identity",
                ],
                "selection_authority": "fixture_boolean",
            }
        ]
        receipt["allowed_pathway_alternatives_actual_use"] = [
            {
                "alternative_set_id": "i115.dynamic",
                "selection_authority": "fixture_boolean",
                "allowed_pathway_ids": [
                    "lgrc9v3.explicit_packet_transport",
                    "pygrc.restoration_replay_identity",
                ],
                "actual_pathway_ids_used": ["experiment.undeclared_alternative"],
            }
        ]
    elif case_id == "BNC-018":
        lock["semantic_selection_performed_by_binder"] = True
    elif case_id == "BNC-019":
        receipt["claim_envelope"]["synthesized_chain_claim"] = True
        receipt["pathway_use_graph"]["larger_chain_claim_synthesized"] = True
    elif case_id == "BNC-020":
        receipt["unbound_execution_accepted_as_evidence"] = True
    else:
        raise ValueError(case_id)


def apply_independent_anchor_mutation(
    case_id: str,
    bundle: dict[str, Any],
    policy: dict[str, Any],
    checker: Any,
) -> None:
    """Keep candidate artifacts self-consistent while violating external review."""

    if case_id == "BNC-014-COORDINATED-P1-P2":
        stage = next(
            item
            for item in bundle["bindings"]["stage_bindings"]
            if item["pathway_id"] == "lgrc9v3.explicit_packet_transport"
            and item["stage_id"] == "packet_schedule"
        )
        stage["symbols"][0]["qualified_symbol"] = "LGRC9V3.step"
    elif case_id == "BNC-014-FALSE-REVISION":
        bundle["bindings"]["source_revision"] = "0" * 40
        bundle["lock"]["source_revision"] = "0" * 40
        bundle["receipt"]["source_revision"] = "0" * 40
    else:
        raise ValueError(case_id)
    map_digest = checker.digest_without(
        bundle["bindings"],
        "binding_map_digest",
    )
    bundle["bindings"]["binding_map_digest"] = map_digest
    bundle["lock"]["binding_map_digest"] = map_digest
    bundle["receipt"]["binding_map_digest"] = map_digest
    policy["accepted_digests"]["binding_map_digest"] = map_digest
    policy["policy_digest"] = checker.digest_without(policy, "policy_digest")


def main(
    *,
    acceptance_anchor_path: Path,
    trusted_anchor_digest: str,
) -> int:
    checker = load_checker()
    acceptance_anchor = load_acceptance_anchor(acceptance_anchor_path)
    policy = build_policy(checker, acceptance_anchor, trusted_anchor_digest)
    write_json(POLICY_PATH, policy)
    build_positive_fixture(acceptance_anchor, trusted_anchor_digest)
    base_bundle = checker.load_bundle(
        ROOT,
        lock_path=LOCK_PATH,
        receipt_path=RECEIPT_PATH,
    )
    execution = checker.validate_bundle(
        ROOT,
        copy.deepcopy(base_bundle),
        policy,
        acceptance_anchor=acceptance_anchor,
        trusted_anchor_digest=trusted_anchor_digest,
    )
    execution["policy_digest"] = policy["policy_digest"]
    execution["conformance_digest"] = checker.canonical_digest(execution)
    write_json(EXECUTION_PATH, execution)
    if execution["status"] != "passed":
        raise RuntimeError(json.dumps(execution["issues"], indent=2))

    control_rows = []
    isolation_rows = []
    for case_id, description, expected_rule in NEGATIVE_CASES:
        mutated = copy.deepcopy(base_bundle)
        apply_negative_mutation(case_id, mutated)
        outcome = checker.validate_bundle(
            ROOT,
            mutated,
            policy,
            acceptance_anchor=acceptance_anchor,
            trusted_anchor_digest=trusted_anchor_digest,
        )
        triggered = sorted({issue["rule_id"] for issue in outcome["issues"]})
        control_rows.append(
            {
                "case_id": case_id,
                "description": description,
                "expected_rule_id": expected_rule,
                "triggered_rule_ids": triggered,
                "status": (
                    "passed"
                    if outcome["status"] == "failed_closed"
                    and expected_rule in triggered
                    else "failed_open"
                ),
            }
        )
        isolated = checker.validate_bundle(
            ROOT,
            mutated,
            policy,
            active_rule_ids={expected_rule},
            acceptance_anchor=acceptance_anchor,
            trusted_anchor_digest=trusted_anchor_digest,
        )
        isolated_triggered = sorted({issue["rule_id"] for issue in isolated["issues"]})
        isolation_rows.append(
            {
                "case_id": case_id,
                "description": description,
                "active_rule_ids": [expected_rule],
                "general_artifact_digest_guard_active": False,
                "triggered_rule_ids": isolated_triggered,
                "status": (
                    "passed"
                    if isolated["status"] == "failed_closed"
                    and isolated_triggered == [expected_rule]
                    else "failed_open"
                ),
            }
        )

    drift_bundle = copy.deepcopy(base_bundle)
    apply_negative_mutation("BNC-014", drift_bundle)
    drift_outcome = checker.validate_bundle(
        ROOT,
        drift_bundle,
        policy,
        acceptance_anchor=acceptance_anchor,
        trusted_anchor_digest=trusted_anchor_digest,
    )
    anchor_control_rows = []
    for case_id, description in (
        (
            "BNC-014-COORDINATED-P1-P2",
            "coordinated packet-schedule to step map and policy re-admission",
        ),
        (
            "BNC-014-FALSE-REVISION",
            "coordinated false source-revision and policy re-admission",
        ),
    ):
        mutated = copy.deepcopy(base_bundle)
        mutated_policy = copy.deepcopy(policy)
        apply_independent_anchor_mutation(
            case_id,
            mutated,
            mutated_policy,
            checker,
        )
        outcome = checker.validate_bundle(
            ROOT,
            mutated,
            mutated_policy,
            active_rule_ids={"BCF-014"},
            acceptance_anchor=acceptance_anchor,
            trusted_anchor_digest=trusted_anchor_digest,
        )
        triggered = sorted({issue["rule_id"] for issue in outcome["issues"]})
        anchor_control_rows.append(
            {
                "case_id": case_id,
                "description": description,
                "candidate_map_and_policy_self_consistent": True,
                "triggered_rule_ids": triggered,
                "binding_staleness_state": outcome["binding_staleness_state"],
                "status": (
                    "passed"
                    if outcome["status"] == "failed_closed"
                    and triggered == ["BCF-014"]
                    and outcome["binding_staleness_state"]
                    == "stale_pending_review"
                    else "failed_open"
                ),
            }
        )
    negative = {
        "artifact": "Phase 8 GRC/LGRC causal pathway binding I115 negative-control execution",
        "schema_version": "phase8_grclgrc_causal_pathway_binding_i115_negative_controls_v1",
        "iteration": 115,
        "source_revision": git("rev-parse", "HEAD"),
        "control_count": len(control_rows),
        "controls": control_rows,
        "rule_isolation_control_count": len(isolation_rows),
        "rule_isolation_controls": isolation_rows,
        "rule_isolation_policy": (
            "Only the target semantic rule participates; lock, receipt, and "
            "authority digest findings owned by unrelated rules are inactive."
        ),
        "failed_open_count": sum(
            row["status"] == "failed_open" for row in control_rows
        ),
        "rule_isolation_failed_open_count": sum(
            row["status"] == "failed_open" for row in isolation_rows
        ),
        "binding_drift_control_becomes_stale_pending_review": (
            drift_outcome["binding_staleness_state"] == "stale_pending_review"
        ),
        "independent_anchor_control_count": len(anchor_control_rows),
        "independent_anchor_controls": anchor_control_rows,
        "independent_anchor_failed_open_count": sum(
            row["status"] == "failed_open" for row in anchor_control_rows
        ),
    }
    negative["status"] = (
        "passed"
        if negative["failed_open_count"] == 0
        and negative["rule_isolation_failed_open_count"] == 0
        and negative["independent_anchor_failed_open_count"] == 0
        and negative["binding_drift_control_becomes_stale_pending_review"]
        else "failed"
    )
    negative["execution_digest"] = checker.canonical_digest(negative)
    write_json(NEGATIVE_PATH, negative)
    if negative["status"] != "passed":
        raise RuntimeError(json.dumps(negative, indent=2))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--acceptance-anchor", type=Path, required=True)
    parser.add_argument("--trusted-anchor-digest", required=True)
    arguments = parser.parse_args()
    raise SystemExit(
        main(
            acceptance_anchor_path=arguments.acceptance_anchor,
            trusted_anchor_digest=arguments.trusted_anchor_digest,
        )
    )

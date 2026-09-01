#!/usr/bin/env python3
"""Focused ET-C7 compiler and authority tests."""

from __future__ import annotations

import copy
import sys
from collections import Counter
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, load_json_object, record_digest  # noqa: E402
from grcv4_explorer.ceilings import build_claim_ceiling_layer  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    checks = 0

    def require(condition: bool, label: str) -> None:
        nonlocal checks
        if not condition:
            raise RuntimeError(f"ET-C7 focused test failed: {label}")
        checks += 1

    records = SIDE_TOOL_ROOT / "records"
    layer = load_json_object(records / "ETC7ClaimCeilingAlternativeLayer.json")
    rebuilt = build_claim_ceiling_layer(repo_root, SIDE_TOOL_ROOT)
    gate = load_json_object(records / "ETC7ClaimCeilingAlternativeNavigation.json")
    require(canonical_bytes(layer) == canonical_bytes(rebuilt), "compiler_parity")
    require(layer["layer_digest"] == record_digest(layer, "layer_digest"), "layer_digest")
    require(gate["record_digest"] == record_digest(gate, "record_digest"), "gate_digest")
    require(layer["status"] == "accepted", "accepted_status")
    require(gate["authority"]["iteration_8_authorized"] is True, "I8_authorized")

    locks = {row["lock_id"]: row for row in layer["locks"]}
    require(len(locks) == 90, "lock_count")
    require(len({row["lock_id"] for row in layer["locks"]}) == 90, "lock_unique")
    require(sum(row["lock_class"] == "accepted_negative_claim" for row in locks.values()) == 6, "negative_count")
    require(sum(row["lock_class"] == "targeted_provenance_hardening" for row in locks.values()) == 8, "hardening_count")
    for key in (
        "core_K_vs_graph_K4",
        "M4_ontology",
        "Candidate_A_profile_scope",
        "Candidate_A_future_curvature_rule",
        "migration_split",
        "reference_Hodge_embedding",
        "differential_backend_scope",
        "destination_semantics",
    ):
        lock = locks[f"hardening:{key}"]
        require(lock["hardening"]["key"] == key, f"hardening:{key}")
        require(lock["promotion_allowed"] is False, f"hardening_locked:{key}")
    require(
        locks["hardening:Candidate_A_future_curvature_rule"]["hardening"]["machine_value"]
        == "curvature_conditioning_requires_a_new_profile_identity_and_provenance_reopening",
        "future_curvature_distinct",
    )

    alternative_counts = Counter(row["alternative_class"] for row in layer["alternatives"])
    require(alternative_counts["routed_candidate"] == 1, "routed_candidate")
    require(alternative_counts["conditional_claim"] == 12, "conditional_claims")
    require(alternative_counts["historical_claim"] == 29, "historical_claims")
    require(alternative_counts["rejected_candidate"] == 1, "rejected_candidate")
    require(alternative_counts["blocked_relabel"] == 96, "blocked_relabels")
    for row in layer["alternatives"]:
        require(row["promotion_allowed"] is False, f"promotion:{row['alternative_id']}")
        require(row["visibility_threshold"] in {20, 40, 60, 80, 100}, f"threshold:{row['alternative_id']}")
        require(row["presentation_order_semantic"] == "staged_disclosure_not_rank_priority_or_evidence_strength", f"no_rank:{row['alternative_id']}")

    b = layer["candidate_B_readmission"]
    require(b["current_status"] == "routed_not_rejected", "B_status")
    require(b["earliest_counterfactual_reexecution_gate_ids"] == ["GRC9V4-CD-D7V2-v1"], "B_gate")
    require("U_B" in b["accepted_route_boundary"], "B_writer")
    require(b["outcome_status"] == "open_work_not_promised_success", "B_no_promise")
    require(
        any(
            row["classification"] == "D7G_eligible_complete_candidate_transition"
            for row in layer["candidate_careers"]["V4-C-constitutive-C-sector"]["rows"]
        ),
        "C_career",
    )
    require(
        any(
            row["classification"] == "current_tranche_closed_missing_constitutive_derivation"
            for row in layer["candidate_careers"]["V4-B-independent-derived-carrier"]["rows"]
        ),
        "B_career",
    )
    require(layer["authority_populations"]["current_debt_transformations"] == 29, "current_transformations")
    require(layer["authority_populations"]["verification_obligations"] == 11, "verification_obligations")
    require(layer["authority_populations"]["historical_claims"] == 29, "history_population")

    tampered = copy.deepcopy(layer)
    tampered["locks"][0]["promotion_allowed"] = True
    require(tampered["layer_digest"] != record_digest(tampered, "layer_digest"), "tamper_lock")
    tampered = copy.deepcopy(layer)
    tampered["alternatives"][0]["immutable_status"] = "accepted"
    require(tampered["layer_digest"] != record_digest(tampered, "layer_digest"), "tamper_alternative")
    require(layer["authority"]["browser_propagation"] is False, "no_browser_propagation")
    require(layer["authority"]["browser_scenario_serialization"] is False, "no_browser_serialization")
    require(layer["authority"]["hidden_score_or_ranking"] is False, "no_hidden_rank")

    print(f"ET_C7_TEST_PASS checks={checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

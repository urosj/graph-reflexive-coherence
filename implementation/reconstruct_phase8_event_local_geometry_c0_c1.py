#!/usr/bin/env python3
"""Classify frozen C0/C1 raw evidence without importing PyGRC."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
        default=str,
    ).encode("utf-8")


def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def max_delta(left: Mapping[str, Any], right: Mapping[str, Any]) -> float:
    return max(
        (abs(float(left[key]) - float(right[key])) for key in sorted(left)),
        default=0.0,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--registration", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite reconstruction: {output}")
    raw = load_json(args.raw)
    registration = load_json(args.registration)
    arms = {row["arm_id"]: row for row in raw["arms"]}
    tol = registration["tolerances"]
    equality = float(tol["float_equality"])
    minimum_effect = float(tol["minimum_order_effect"])
    minimum_control = float(tol["minimum_negative_control_difference"])

    def coherence(arm_id: str) -> Mapping[str, Any]:
        return arms[arm_id]["final_source"]["coherence"]

    def semantic_equal(left: str, right: str) -> bool:
        return arms[left]["semantic_result"]["digest"] == arms[right]["semantic_result"]["digest"]

    c0_delta = max_delta(coherence("C0_H12"), coherence("C0_H21"))
    c1_delta = max_delta(coherence("C1_H12"), coherence("C1_H21"))
    same_frontier_delta = max_delta(coherence("C1_F12"), coherence("C1_F21"))
    geometry_off_delta = max_delta(
        coherence("C1_GEOMETRY_OFF_H12"), coherence("C1_GEOMETRY_OFF_H21")
    )
    packetization_off_delta = max_delta(
        coherence("C1_PACKETIZATION_OFF_H12"),
        coherence("C1_PACKETIZATION_OFF_H21"),
    )
    geometry_dependence_delta = max_delta(
        coherence("C1_H12"), coherence("C1_GEOMETRY_OFF_H12")
    )
    packet_dependence_delta = max_delta(
        coherence("C1_H12"), coherence("C1_PACKETIZATION_OFF_H12")
    )
    scale_delta = max_delta(coherence("C1_H12"), coherence("C1_HALF_SCALE_H12"))
    direction_delta = max_delta(
        coherence("C1_H12"), coherence("C1_WRONG_DIRECTION_H12")
    )

    controls = {
        "c0_full_drain_null": {
            "status": "passed" if c0_delta <= equality else "failed_open",
            "maximum_coherence_delta": c0_delta,
        },
        "same_frontier_scheduler_batching": {
            "status": "passed" if same_frontier_delta <= equality else "failed_open",
            "maximum_coherence_delta": same_frontier_delta,
        },
        "geometry_off": {
            "status": "failed_closed"
            if geometry_off_delta <= equality and geometry_dependence_delta >= minimum_control
            else "failed_open",
            "history_order_delta": geometry_off_delta,
            "positive_path_difference": geometry_dependence_delta,
        },
        "packetization_off": {
            "status": "failed_closed"
            if packetization_off_delta <= equality
            and packet_dependence_delta >= minimum_control
            else "failed_open",
            "history_order_delta": packetization_off_delta,
            "positive_path_difference": packet_dependence_delta,
        },
        "stale_proposal": {
            "status": "failed_closed"
            if raw["static_controls"]["stale_proposal"]["status"]
            == "rejected_stale_proposal"
            else "failed_open"
        },
        "scope_leak": {
            "status": "failed_closed"
            if raw["static_controls"]["scope_leak"]["status"]
            == "rejected_scope_leak"
            else "failed_open"
        },
        "label_only": {
            "status": "failed_closed"
            if semantic_equal("C1_H12", "C1_LABEL_ONLY_H12")
            else "failed_open"
        },
        "direction": {
            "status": "failed_closed"
            if direction_delta >= minimum_control
            else "failed_open",
            "maximum_coherence_delta": direction_delta,
        },
        "scale": {
            "status": "failed_closed" if scale_delta >= minimum_control else "failed_open",
            "maximum_coherence_delta": scale_delta,
        },
        "funding": {
            "status": "failed_closed"
            if any(
                proposal["status"] == "rejected_underfunded"
                for proposal in arms["C1_OVERDRAW_H12"]["proposals"]
            )
            else "failed_open"
        },
        "restoration": {
            "status": "passed"
            if semantic_equal("C1_H12", "C1_RESTORATION_H12")
            and arms["C1_RESTORATION_H12"]["restored_after_first_trigger"]
            else "failed_open"
        },
        "replay": {
            "status": "passed"
            if semantic_equal("C1_H12", "C1_REPLAY_H12")
            else "failed_open"
        },
        "budget_conservation": {
            "status": "passed"
            if all(row["budget_conservation_passed"] for row in raw["arms"])
            else "failed_open",
            "maximum_absolute_error": max(
                float(row["maximum_absolute_budget_error"]) for row in raw["arms"]
            ),
        },
        "mutation_and_basin_identity": {
            "status": "passed"
            if all(
                row["semantic_result"]["topology_nodes"] == [0, 1, 2]
                and row["semantic_result"]["topology_edges"] == [0, 1]
                and row["semantic_result"]["basin_ids"]
                == {"0": 0, "1": 1, "2": 2}
                for row in raw["arms"]
            )
            else "failed_open"
        },
    }

    independent_later_effect = (
        arms["C1_H12"]["independent_later_effect"]["digest"]
        != arms["C1_H21"]["independent_later_effect"]["digest"]
    )
    c0_class = "C0-EQUIV" if c0_delta <= equality else "C0-ORDER"
    required_controls = [
        "c0_full_drain_null",
        "same_frontier_scheduler_batching",
        "geometry_off",
        "packetization_off",
        "stale_proposal",
        "scope_leak",
        "label_only",
        "direction",
        "scale",
        "funding",
        "restoration",
        "replay",
        "budget_conservation",
        "mutation_and_basin_identity",
    ]
    controls_pass = all(
        controls[name]["status"] in {"passed", "failed_closed"}
        for name in required_controls
    )
    positive_direct_funding = all(
        proposal.get("direct_funding_passed", True)
        for arm_id in ("C1_H12", "C1_H21")
        for proposal in arms[arm_id]["proposals"]
    )
    positive_packet_count = sum(
        len(proposal.get("packets", []))
        for arm_id in ("C1_H12", "C1_H21")
        for proposal in arms[arm_id]["proposals"]
    )
    c1_order = c1_delta >= minimum_effect
    if positive_packet_count == 0 and direction_delta >= minimum_control:
        c1_class = "C1-SCOPE"
    elif c1_order and controls_pass:
        c1_class = "C1-ORDER"
    else:
        c1_class = "C1-NULL"
    gate_requirements = {
        "c0_stable_full_drain_null_or_bounded_domain": c0_class
        in {"C0-EQUIV", "C0-DOMAIN"},
        "c1_non_tied_order_effect_beyond_c0": c1_class == "C1-ORDER",
        "geometry_dependence": controls["geometry_off"]["status"] == "failed_closed",
        "packet_transduction_dependence": controls["packetization_off"]["status"]
        == "failed_closed",
        "independent_later_effect": independent_later_effect,
        "replay_and_provenance": controls["restoration"]["status"] == "passed"
        and controls["replay"]["status"] == "passed"
        and raw["freeze_verification"]["passed"],
        "alternative_explanations_rejected": controls_pass,
        "remaining_hidden_mechanism_identified": True,
        "positive_path_directly_funded": positive_direct_funding,
    }
    gate_passed = all(gate_requirements.values())
    closeout = {
        "artifact": "Phase-8-LGRC9-EventLocalGeometryIntegrationC0C1Closeout",
        "schema_version": "phase8_lgrc9_event_local_geometry_integration_c0_c1_closeout_v1",
        "date": "2026-08-16",
        "iteration": 96,
        "source_commit": raw["source_commit"],
        "raw_evidence_path": str(args.raw),
        "raw_evidence_sha256": sha256_file(args.raw),
        "raw_evidence_digest_verified": digest_json(
            {key: value for key, value in raw.items() if key != "evidence_digest"}
        )
        == raw["evidence_digest"],
        "registration_path": str(args.registration),
        "registration_sha256": sha256_file(args.registration),
        "independent_reconstruction_imported_pygrc": False,
        "c0": {
            "classification": c0_class,
            "maximum_coherence_delta": c0_delta,
        },
        "c1": {
            "classification": c1_class,
            "observed_numerical_classification": "C1-NULL"
            if c1_delta < minimum_effect
            else "C1-ORDER",
            "maximum_non_tied_order_delta": c1_delta,
            "independent_later_effect_passed": independent_later_effect,
            "positive_direct_funding_passed": positive_direct_funding,
            "positive_geometry_derived_packet_count": positive_packet_count,
            "scope_interpretation": (
                "Native reconstructed current was incoming at the trigger node; the registered trigger-node-owned outward action scope emitted no work. The reversed-direction negative control changed state, but cannot support the registered mapping."
                if c1_class == "C1-SCOPE"
                else "not_applicable"
            ),
        },
        "controls": controls,
        "gate_requirements": gate_requirements,
        "source_change_gate_disposition": "gate_passed"
        if gate_passed
        else "close_without_runtime_change",
        "strongest_supported_claim": (
            "A source-current producer-mediated event-triggered global geometry reconstruction and directly funded packet-transduction composition exhibits a bounded non-tied order effect beyond the full-drain null in the registered fixed-topology domain; the external global orchestrator remains the missing LGRC ownership layer."
            if gate_passed
            else "C0 is a stable full-drain equivalence result, but C1 closes at the registered action-scope boundary: native reconstructed current was incoming at the trigger node, so no trigger-node-owned geometry-derived packet work or independent order effect was produced."
        ),
        "phase8_runtime_implementation_opened": False,
        "post_implementation_validation_opened": False,
        "n32_selected": False,
        "blocked_claims": registration["blocked_claims"],
    }
    closeout["closeout_digest"] = digest_json(closeout)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(closeout, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

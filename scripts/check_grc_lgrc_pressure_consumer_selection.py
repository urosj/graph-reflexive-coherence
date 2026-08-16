#!/usr/bin/env python3
"""Run one low-context causal-pathway selection replay.

The replay is intentionally restricted to the frozen machine selection guide,
registry, composition matrix, and one answer-free consumer input. It does not
inspect implementation source, tests, the evidence crosswalk, earlier
iteration reports, or an expected-recovery oracle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DEFAULT_REGISTRY = "specs/grc-lgrc-causal-pathway-contracts.json"
DEFAULT_MATRIX = "specs/grc-lgrc-causal-pathway-composition-matrix.json"
DEFAULT_GUIDE = "specs/grc-lgrc-causal-pathway-selection-guide.json"


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def load_json(root: Path, relative_path: str) -> dict[str, Any]:
    return json.loads((root / relative_path).read_text(encoding="utf-8"))


FORBIDDEN_BLIND_INPUT_FIELDS = {
    "expected_recovery",
    "recovery",
    "selected_guide_case_id",
    "selected_pathway_ids",
    "required_directional_composition_id",
    "composition_id",
    "composition_ids",
    "composition_status",
    "adapter_id",
    "adapter_owner",
    "guide_case_id",
    "resolution_kind",
    "configured_residue",
    "producer_residue",
    "authority_transferred",
    "native_or_bounded_claim",
    "claim_ceiling",
    "blocked_claims",
    "blocked_nearby_interpretation",
    "missing_crossing",
    "missing_relation",
    "nearby_alternatives_rejected",
    "extension_authorized",
}


def all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value).union(*(all_keys(child) for child in value.values()))
    if isinstance(value, list):
        return set().union(*(all_keys(child) for child in value))
    return set()


def signature(value: dict[str, Any]) -> tuple[tuple[str, ...], str, str]:
    if "declared_constraints" in value:
        constraints = value["declared_constraints"]
        return (
            tuple(sorted(constraints["temporal_semantics"])),
            constraints["route_relation"],
            constraints["retained_relation"],
        )
    return (
        tuple(sorted(value["required_temporal_semantics"])),
        value["route_relation"],
        value["retained_relation"],
    )


def nearby_alternatives(
    selected: dict[str, Any], candidates: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    fields = (
        "required_temporal_semantics",
        "route_relation",
        "retained_relation",
    )
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate["case_id"] == selected["case_id"]:
            continue
        matching = []
        mismatches = []
        for field in fields:
            left = selected[field]
            right = candidate[field]
            if field == "required_temporal_semantics":
                left = sorted(left)
                right = sorted(right)
            if left == right:
                matching.append(field)
            else:
                mismatches.append(
                    {
                        "field": field,
                        "required": left,
                        "alternative": right,
                    }
                )
        rows.append(
            {
                "case_id": candidate["case_id"],
                "matching_signature_field_count": len(matching),
                "matching_signature_fields": matching,
                "why_wrong": mismatches,
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -row["matching_signature_field_count"],
            row["case_id"],
        ),
    )[:3]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--consumer", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = args.root.resolve()

    input_paths = {
        "selection_guide": DEFAULT_GUIDE,
        "registry": DEFAULT_REGISTRY,
        "composition_matrix": DEFAULT_MATRIX,
        "blind_consumer_input": args.consumer,
    }
    guide = load_json(root, input_paths["selection_guide"])
    registry = load_json(root, input_paths["registry"])
    matrix = load_json(root, input_paths["composition_matrix"])
    consumer = load_json(root, input_paths["blind_consumer_input"])

    errors: list[str] = []
    forbidden_fields_present = sorted(
        all_keys(consumer).intersection(FORBIDDEN_BLIND_INPUT_FIELDS)
    )
    if forbidden_fields_present:
        errors.append(
            "blind input contains answer-bearing fields: "
            + ", ".join(forbidden_fields_present)
        )
    actual = {
        "registry_digest": registry.get("registry_digest"),
        "matrix_digest": matrix.get("matrix_digest"),
        "selector_digest": guide.get("selector_digest"),
    }
    if guide.get("registry_digest") != registry.get("registry_digest"):
        errors.append("guide registry digest is stale")
    if guide.get("matrix_digest") != matrix.get("matrix_digest"):
        errors.append("guide matrix digest is stale")

    demand_signature = signature(consumer)
    matches = [
        row
        for row in guide.get("worked_cases", [])
        if signature(row) == demand_signature
    ]
    if len(matches) != 1:
        errors.append(
            f"normalized demand resolved to {len(matches)} guide cases; expected one"
        )
        selected: dict[str, Any] = {}
    else:
        selected = matches[0]

    pathways_by_id = {
        row["pathway_id"]: row for row in registry.get("pathways", [])
    }
    compositions_by_id = {
        row["composition_id"]: row for row in matrix.get("compositions", [])
    }
    selected_ids = selected.get("selected_pathway_ids", [])
    if any(pathway_id not in pathways_by_id for pathway_id in selected_ids):
        errors.append("selected pathway does not resolve in current registry")

    composition_id = selected.get("required_directional_composition_id")
    composition = compositions_by_id.get(composition_id) if composition_id else None
    if composition_id and composition is None:
        errors.append("selected composition does not resolve in current matrix")
    if composition and (
        composition.get("composition_status") != selected.get("composition_status")
        or composition.get("adapter_owner") != selected.get("adapter_owner")
    ):
        errors.append("guide projection differs from current matrix ownership/status")

    recovery = {
        "selected_guide_case_id": selected.get("case_id"),
        "selected_pathway_ids": selected_ids,
        "required_directional_composition_id": composition_id,
        "composition_status": selected.get("composition_status"),
        "adapter_id": selected.get("adapter_id"),
        "adapter_owner": selected.get("adapter_owner"),
        "configured_residue": selected.get("configured_residue", []),
        "producer_residue": selected.get("producer_residue", []),
        "authority_transferred": (
            composition.get("authority_transferred", []) if composition else []
        ),
        "native_or_bounded_claim": selected.get("claim_ceiling"),
        "blocked_claims": selected.get("blocked_nearby_interpretation", []),
        "missing_crossing": selected.get("missing_relation"),
        "nearby_alternatives_rejected": (
            nearby_alternatives(selected, guide.get("worked_cases", []))
            if selected
            else []
        ),
    }
    execution = {
        "artifact": "Phase 8 GRC/LGRC low-context pressure-consumer replay",
        "schema_version": "phase8_grclgrc_i111_independent_replay_v1",
        "iteration": 111,
        "status": "passed" if not errors else "failed",
        "loaded_input_paths": list(input_paths.values()),
        "loaded_input_roles": list(input_paths),
        "loaded_artifact_digests": actual,
        "source_or_test_files_read": [],
        "evidence_crosswalk_read": False,
        "earlier_iteration_report_read": False,
        "semantic_match_rule": "exact normalized time/route/retained-relation signature",
        "blind_input_answer_fields_present": forbidden_fields_present,
        "match_count": len(matches),
        "recovery": recovery,
        "error_count": len(errors),
        "errors": errors,
        "runtime_behavior_changed": False,
        "ecological_meaning_inferred": False,
        "extension_authorized": False,
    }
    execution["execution_digest"] = canonical_digest(execution)
    output = root / args.output
    output.write_text(
        json.dumps(execution, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0 if execution["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

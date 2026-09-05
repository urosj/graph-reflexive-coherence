"""Source-exact review projections, never an upgrade of forensic support."""

from copy import deepcopy
import phase9_policy as p


def source_projection(root):
    paths = [
        p.PHASE + "tranche-1/P9-1.1-SourceCrosswalk.json",
        p.PHASE + "tranche-1/P9-1.3-VerificationRouting.json",
        p.PHASE + "tranche-1/P9-1.4-SupportAndDependencies.json",
    ]
    for name in paths:
        p.prior.git_exact(root, p.prior.CHECKPOINT, name)
    cross, routing, support = [p.read(root / name) for name in paths]
    name = "specs/grc-v4-conformance-fixtures.json"
    p.prior.git_exact(root, p.prior.CHECKPOINT, name)
    paths.append(name)
    compatibility = p.read(root / name)["disabled_compatibility"]
    return {
        "specification_authority": "accepted_frozen",
        "claims": [
            {"claim_id": r["claim_id"], "source_claim": r["source_claim"]}
            for r in cross["claims"]
        ],
        "contracts": [
            {
                k: deepcopy(r[k])
                for k in [
                    "contract_id",
                    "source_contract",
                    "support_disposition",
                    "planning_scope",
                    "accepted_claim_support_semantics",
                ]
            }
            for r in cross["contracts"]
        ],
        "profiles": deepcopy(support["profiles"]),
        "evidence_aliases": deepcopy(support["child_iterations"]),
        "obligations": deepcopy(routing["obligations"]),
        "deferred": deepcopy(support["deliberately_deferred"]),
        "compatibility_cells": [
            {
                "profile": r["profile"],
                "surface": surface,
                "contract_id": r[surface],
                "evidence_kind": compatibility["concrete_vector_status"],
            }
            for r in compatibility["matrix"]
            for surface in compatibility["surfaces"]
        ],
        "provenance_only_locator": deepcopy(cross["provenance_only_locator"]),
        "source_bindings": [
            {"path": name, "sha256": p.sha((root / name).read_bytes())}
            for name in paths
        ],
    }


def validate_projection(candidate, expected):
    # This comparison is deliberately after source admission. Controlled
    # projection edits exercise semantic fidelity, not just file SHA rejection.
    for field in [
        "specification_authority",
        "claims",
        "contracts",
        "profiles",
        "evidence_aliases",
        "obligations",
        "deferred",
        "compatibility_cells",
        "provenance_only_locator",
        "source_bindings",
    ]:
        p.require(
            candidate[field] == expected[field], "semantic projection drift: " + field
        )
    return candidate


def source_meaning(root):
    value = source_projection(root)
    rows = [
        r
        for r in value["contracts"]
        if "indeterminate_requires_review" in r["accepted_claim_support_semantics"]
    ]
    return {
        "specification_authority": value["specification_authority"],
        "forensic_support_disposition": "indeterminate_requires_review",
        "association_count": len(rows),
        "association_denominator": len(value["contracts"]),
        "pending_source_obligations": 15,
        "evidence_kind": "source_bound_planning_crosswalk_not_runtime_evidence",
        "source_bindings": value["source_bindings"],
        "claim_ceiling": "Accepted specification authority does not promote indeterminate forensic associations; those associations do not revoke the accepted specification.",
    }

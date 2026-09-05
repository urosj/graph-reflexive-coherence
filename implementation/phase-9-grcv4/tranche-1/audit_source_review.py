"""Reconstruct the P9-1.1--P9-1.3 review data without changing source authority.

Default: read-only verification. --emit prints a generated artifact (or a
bounded character slice) so callers can materialize it with apply_patch.
No runtime, investigation record, specification, or forensic graph is written.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
INV = "implementation/investigations/grc9v4-constitutive-design/"
SIDE = ROOT / INV / "tools/exploratory-side-tool"
sys.path.insert(0, str(SIDE / "tool/src"))

from grcv4_explorer.forensic import (  # noqa: E402
    contract_provenance,
    debt_lifecycle,
    reconstruction_path,
)
from grcv4_explorer.successor import load_successor_forensic_context  # noqa: E402

SPEC = "specs/grc-v4-spec.md"
API = "specs/grc-common-interface-v4-ext.md"
G9 = "specs/grc-9-v4-spec.md"
PAPER = INV + "drafts/2026-09-GRC-V4.md"
DEBTS = INV + "decisions/D10DebtClaimTransformationLedger.json"
D102 = INV + "decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json"
ACCEPT = INV + "specification/GRCV4SpecificationReleaseAcceptanceGate.json"
PROPAGATION = (
    INV + "specification/D11PaperPropagationAndSpecificationExtractionGate.json"
)
BASE = "7c772d36bd4cf12b4a444b7b954b74612de2926f"
RELEASE_ID = "grcv4-spec-release-sha256:9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f"


def group(spec_sections, paper_sections, module, iterations, oracle, schema_defs=()):
    return {
        "spec_sections": spec_sections,
        "paper_section_prefixes": paper_sections,
        "proposed_module": f"src/pygrc/models/{module}.py",
        "proposed_test_module": f"tests/models/test_{module}.py",
        "ownership_status": "proposed_crosswalk_only_P9-1.5_review_pending",
        "implementation_iterations": iterations.split(),
        "independent_oracle_requirement": oracle,
        "machine_schema_definitions": list(schema_defs),
    }


GROUPS = {
    "identity": group(
        [
            (SPEC, "Complete profile identity"),
            (SPEC, "Parameters"),
            (API, "Construction and parameter resolution"),
            (API, "Canonical identity and deep immutability"),
        ],
        ["7.", "12.1"],
        "grc_v4_profile",
        "P9-2.2 P9-2.6",
        "Canonical preimage vectors, semantic/schema negative separation, unsupported complete identities.",
        ["resolved_params", "profile_identity_payload"],
    ),
    "state": group(
        [
            (SPEC, "State and authority"),
            (API, "Concrete class relationships"),
            (API, "State and authority extension"),
        ],
        ["3.", "11.1", "12.1"],
        "grc_v4_state",
        "P9-2.1 P9-2.6 P9-4.6",
        "State authority matrix; independently attempted nested mutations and duplicate aliasing.",
        [
            "authoritative_state",
            "scientific_state_payload",
            "lifecycle_envelope_payload",
        ],
    ),
    "api": group(
        [
            (SPEC, "Class"),
            (SPEC, "Capabilities"),
            (SPEC, "Observables"),
            (API, "V4 input-bearing operations"),
            (API, "Capability and profile discovery"),
            (API, "Interoperability and non-retroactivity"),
        ],
        ["11.1", "12.3"],
        "grc_v4",
        "P9-2.3 P9-2.6 P9-10.4",
        "Common-interface projections and typed operation requests; no unsupported capability advertisement.",
        ["step_request_input", "step_request", "migration_request"],
    ),
    "differential": group(
        [
            (SPEC, "Graph and differential backend"),
            (API, "Graph and differential backend extension"),
            (API, "Edge-label compatibility"),
        ],
        ["3.", "4."],
        "grc_v4_differential",
        "P9-3.1 P9-3.4",
        "Explicit incidence matrices, stable signed-edge permutations, pairing and boundary examples.",
        ["serialized_graph_payload"],
    ),
    "transport": group(
        [
            (SPEC, "Common resource and transport contract"),
            (SPEC, "Structural geometry and current typing"),
        ],
        ["4.", "6."],
        "grc_v4_transport",
        "P9-3.1 P9-3.3",
        "Independent scalar potential-flow reference; exactly one continuity write, no inferred Hodge-to-mobility authority.",
    ),
    "charge": group(
        [(SPEC, "Charge contract"), (API, "Step results, receipts, and observables")],
        ["4."],
        "grc_v4_charge",
        "P9-3.3 P9-3.4 P9-10.2",
        "Balanced binary64 sum, signed residual and tolerance edges; nonidentity repair rejects; geometry derivative of charge is zero.",
        ["charge_policy", "charge_receipt_identity_payload"],
    ),
    "geometry": group(
        [
            (SPEC, "Structural geometry and current typing"),
            (SPEC, "Graph and differential backend"),
        ],
        ["6."],
        "grc_v4_geometry",
        "P9-3.1 P9-3.2 P9-3.4",
        "Nonidentity SPD matrices, star partition/assembly, flat/sharp similarity conditioning, signed covariance; fixed-space covariance is not event transport.",
        ["geometry_params", "k4_identity_payload", "reference_hodge_identity_payload"],
    ),
    "candidate_A": group(
        [
            (SPEC, "Candidate A contract"),
            (SPEC, "Lifecycle, migration, and topology events"),
        ],
        ["8.", "12.6"],
        "grc_v4_candidate_a",
        "P9-5.1 P9-5.2 P9-5.3",
        "Independent positive initializer/log-writer values and old/new state stage probes; formation remains unproved.",
        ["candidate_a_params"],
    ),
    "candidate_C": group(
        [(SPEC, "Candidate C contract")],
        ["9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "9.7", "9.8", "9.9", "9.10"],
        "grc_v4_candidate_c",
        "P9-4.1 P9-4.2 P9-4.3",
        "Exact C algebra vectors, strict-gap selector rejection, one chi gate, physical/retained conditioning distinction.",
        ["candidate_c_params"],
    ),
    "C_baseline": group(
        [
            (SPEC, "Candidate C contract"),
            (SPEC, "Accepted Candidate C baseline transport — D11-C-T3a"),
        ],
        ["9."],
        "grc_v4_candidate_c_transport",
        "P9-4.1 P9-4.2 P9-4.3 P9-7.4",
        "Independent W_C,tr/E_H/E_M, unnormalized retained stiffness and J0; kappa-M/chi/zeta/tau controls, complete derivative, event reference-map readmission.",
        ["candidate_c_params", "wctr_identity_payload"],
    ),
    "OS": group(
        [(SPEC, "Operator Split (`OS`)")],
        ["10.3"],
        "grc_v4_os",
        "P9-4.4 P9-4.5 P9-5.3",
        "One predictor/geometry/corrector; independently recompute corrected C baseline and residual; forbid second pass.",
        ["os_params"],
    ),
    "CI": group(
        [(SPEC, "Coupled Implicit (`CI`)")],
        ["10.2"],
        "grc_v4_ci",
        "P9-6.1a P9-6.1b P9-6.1c",
        "Selected bounded roots, absence/multiplicity/conditioning failures and independent A/C residuals.",
        ["ci_params"],
    ),
    "PC": group(
        [(SPEC, "Persistent Carrier (`PC`)")],
        ["10.5"],
        "grc_v4_pc",
        "P9-6.2a P9-6.2b P9-6.2c",
        "Analytic scalar-ZOH writer, old carrier reads, matched forcing/release, source envelope.",
        ["pc_params"],
    ),
    "CI_PC": group(
        [(SPEC, "Coupled Implicit plus Persistent Carrier (`CI+PC`)")],
        ["10.6"],
        "grc_v4_ci_pc",
        "P9-6.3a P9-6.3b P9-6.3c",
        "Same root/source and exact unit-plus-unit gain two, independent candidate controls.",
        ["cipc_params"],
    ),
    "RG2b": group(
        [(SPEC, "Reconstructed Geometry (`RG2b`)")],
        ["10.4"],
        "grc_v4_rg2b",
        "P9-6.4a P9-6.4b P9-6.4c",
        "Finite admitted evaluator, error/containment certificates, deterministic Lipschitz section; no classical derivative claim.",
        ["rg2b_params"],
    ),
    "step": group(
        [
            (SPEC, "Complete-step transaction"),
            (SPEC, "Errors and atomicity"),
            (API, "Error and atomicity extension"),
        ],
        ["11.", "E.3", "E.4", "E.12"],
        "grc_v4_step",
        "P9-2.3 P9-3.5 P9-4.5 P9-4.7a",
        "Twelve-stage transaction, valid zero-duration identity, no fallback after invalid root, exact prestate rollback.",
        ["step_result", "failure_receipt", "solver_policy"],
    ),
    "lifecycle": group(
        [
            (SPEC, "Lifecycle, migration, and topology events"),
            (SPEC, "Serialization"),
            (API, "Lifecycle and event extension"),
            (API, "Serialization and restoration"),
            (API, "Step results, receipts, and observables"),
        ],
        ["12.1", "12.2", "12.3", "E.5", "E.11"],
        "grc_v4_lifecycle",
        "P9-4.6 P9-4.7a P9-7.1 P9-7.6",
        "Roundtrip/restore/replay and transformed reset; receipt delta/ledger split and independent duplication.",
        ["reset_payload", "commit_payload", "successful_receipt_envelope"],
    ),
    "events": group(
        [
            (SPEC, "Lifecycle, migration, and topology events"),
            (API, "V4 input-bearing operations"),
        ],
        ["12.", "E.7", "E.9", "E.10"],
        "grc_v4_events",
        "P9-4.7b P9-7.2a P9-7.2b P9-7.3 P9-7.4 P9-7.5",
        "Nonzero affine event increment, live/reset/charge map, separate history channels, target reconstruction and admission; endpoint support does not prove crossing support.",
        [
            "resource_event_transform",
            "mapped_topology_event_request",
            "history_bundle_policy",
        ],
    ),
    "claim_boundary": group(
        [
            (SPEC, "Conformance language"),
            (SPEC, "Claim conformance matrix"),
            (SPEC, "Explicit nonclaims"),
            (API, "Claim boundary"),
        ],
        ["15."],
        "grc_v4_profile",
        "P9-2.6 P9-10.5",
        "Unsupported B/successor rejection and exact implemented support subset; no claim upgrades from API availability.",
    ),
    "analysis": group(
        [(SPEC, "Analysis interfaces"), (SPEC, "Explicit nonclaims")],
        ["13.", "Appendix F."],
        "grc_v4_analysis",
        "P9-10.5",
        "Read-only formed-branch typed operators; numeric spectra/stability/metric claims require separately admitted evidence.",
    ),
    "G9_ports": group(
        [(G9, "Port graph"), (G9, "Fixed $3\\times3$ chart")],
        ["A.2", "A.3"],
        "grc_9_v4_ports",
        "P9-8.1a",
        "Unique endpoint occupancy, chart/port identities and forbidden self-loop cases.",
        ["port_graph_payload", "specialization_identity_payload"],
    ),
    "G9_differential": group(
        [
            (G9, "Fixed row-basis differential backend"),
            (G9, "V4 row-weight bridge and stage"),
        ],
        ["A.4"],
        "grc_9_v4_differential",
        "P9-8.1b",
        "Exact row basis/weights/sign and stage; V4-only adaptation.",
        ["row_weight_policy"],
    ),
    "G9_expansion": group(
        [
            (G9, "Mechanical expansion"),
            (G9, "Accepted D11-G9 chiral same-port expansion"),
        ],
        ["A.6"],
        "grc_9_v4_expansion",
        "P9-8.2 P9-8.3C-OS P9-8.3C-PC P9-8.4 P9-8.5 P9-8.6",
        "All applicable D30/D31/D45/D52, extra D37/D44 probes, dihedral/edge covariance, reference/history/readmission; no caller-built target or A evidence inferred.",
        [
            "expansion_policy",
            "expansion_event_request",
            "expansion_event_identity_payload",
        ],
    ),
    "G9_completion": group(
        [
            (G9, "Saturation and hybrid spark semantics"),
            (G9, "Child-basin completion"),
            (G9, "Step and event ordering"),
        ],
        ["A.5", "A.7"],
        "grc_9_v4_sparks",
        "P9-8.1c P9-9.1",
        "Mechanical candidate versus completed spark, child stabilization and hierarchy require independent runtime evidence.",
        ["spark_policy", "child_stabilization_policy"],
    ),
    "G9_coarse": group(
        [(G9, "Column coarse-graining and Split")],
        ["A.8"],
        "grc_9_v4_coarse",
        "P9-8.1d",
        "Column aggregation and exact supported-field Split roundtrip.",
        ["coarse_policy"],
    ),
    "G9_A_initializer": group(
        [
            (G9, "Exact Candidate-A initializer binding"),
            (G9, "Whole-lifecycle completion and legacy boundary"),
        ],
        ["A.9"],
        "grc_9_v4_candidate_a",
        "P9-8.3A",
        "Exact legacy-row reference initializer and new concrete A target vector before advertised expansion.",
        ["candidate_a_profile_template_payload"],
    ),
    "G9_disabled": group(
        [
            (G9, "Exact disabled GRC9V3 compatibility"),
            (G9, "Whole-lifecycle completion and legacy boundary"),
        ],
        ["A.10"],
        "grc_9_v4_compatibility",
        "P9-9.2 P9-9.4 P9-9.5 P9-9.6",
        "Forty independent delegate cells; both migration directions; legacy undefined port-5 expansion fails atomically in V4.",
        [
            "legacy_compatibility_policy",
            "legacy_compatibility_receipt_identity_payload",
        ],
    ),
}

# These are planning routes, not scientific admissions or accepted new gates.
DEFERRED = {
    "P9-SCI-SINGULAR": "Named source-backed singular-continuation successor; current profiles fail closed.",
    "P9-SCI-PHYSICAL": "Declared baseline-model nonabsorbability/physical attribution investigation.",
    "P9-SCI-UNITS": "Units/gauge/normalization and cross-profile comparability bridge.",
    "P9-SCI-B": "Source-backed Candidate B writer/read successor.",
    "P9-SCI-RG-REGULARITY": "Separately admitted RG2b regularization/derivative proof.",
    "P9-EVID-ENVELOPES": "Preregistered numeric envelopes; finite implementation parameter tests are not full-family bounds.",
    "P9-EVID-ENDPOINT": "Complete-chain committed nonannihilation/endpoint witnesses per exact profile.",
    "P9-EVID-ANALYSIS": "Formed branches, complete operators, numeric spectra/stability and declared metrics.",
    "P9-EVID-A-METRIC": "A complete-state analysis metric before absolute/cross-architecture nonnormality.",
    "P9-EVID-COMPARISON": "Matched formed-profile discrimination before ranking/preference.",
    "P9-EVID-FORMATION": "Runtime reachability, formation/retention/release evidence beyond conformance.",
}


def route(
    iterations="",
    gate=None,
    disposition="pending_runtime_execution",
    limit="Scoped implementation evidence does not discharge the complete scientific obligation.",
):
    return {
        "phase9_iterations": iterations.split(),
        "deferred_gate": gate,
        "downstream_disposition": disposition,
        "closure_limit": limit,
    }


OBLIGATION_ROUTES = {
    "D9-VERIFY-QUANTITATIVE-PARAMETER-ENVELOPES": route(
        "P9-4.3 P9-6.5", "P9-EVID-ENVELOPES", "pending_numeric_evidence"
    ),
    "D9-VERIFY-LIFECYCLE-RUNTIME-CONFORMANCE": route(
        "P9-4.6 P9-4.7a P9-4.7b P9-7.1 P9-7.5 P9-7.6"
    ),
    "D9-VERIFY-MIGRATION-AND-EVENT-CONFORMANCE": route(
        "P9-4.7b P9-7.2a P9-7.2b P9-7.3 P9-7.4"
    ),
    "D9-VERIFY-CHARGE-AND-EVENT-RECEIPTS": route("P9-3.3 P9-3.4 P9-7.3 P9-10.2"),
    "D10-VERIFY-COMPLETE-CHAIN-WITNESSES": route(
        "P9-10.5", "P9-EVID-ENDPOINT", "pending_scientific_evidence"
    ),
    "D10-VERIFY-FORMED-BRANCH-STRUCTURAL-TEMPORAL": route(
        "P9-10.5", "P9-EVID-ANALYSIS", "pending_scientific_evidence"
    ),
    "D10-VERIFY-A-ANALYSIS-METRIC": route(
        "P9-10.5", "P9-EVID-A-METRIC", "pending_scientific_evidence"
    ),
    "D10-VERIFY-EXECUTABLE-COVARIANCE-HODGE": route("P9-3.4 P9-4.3 P9-8.4"),
    "D10-VERIFY-MATCHED-PROFILE-DISCRIMINATION": route(
        "P9-10.5", "P9-EVID-COMPARISON", "pending_scientific_evidence"
    ),
    "D10-VERIFY-RUNTIME-FORMATION-RETENTION-RELEASE": route(
        "P9-10.5", "P9-EVID-FORMATION", "pending_scientific_evidence"
    ),
    "D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT": route(
        disposition="satisfied_bounded_by_D10_2",
        limit="Current initial population only; materially distinct successor profiles reopen provenance.",
    ),
    "D11-C-VERIFY-PAPER-AND-SPECIFICATION-PROPAGATION": route(
        disposition="satisfied_by_downstream_paper_and_specification_acceptance",
        limit="Accepted propagated bytes only, not runtime conformance.",
    ),
    "D11-C-VERIFY-REFERENCE-FIELD-SERIALIZATION-AND-EVENT-READMISSION": route(
        "P9-4.1 P9-4.6 P9-4.7b P9-7.4 P9-8.3C-OS P9-8.3C-PC"
    ),
    "D11-C-VERIFY-IMPLEMENTATION-COVARIANCE-AND-SOLVER-CONFORMANCE": route(
        "P9-3.4 P9-4.2 P9-4.3 P9-6.5"
    ),
    "D11-G9-VERIFY-PAPER-THEN-SPECIFICATION-PROPAGATION": route(
        disposition="satisfied_by_downstream_paper_and_specification_acceptance",
        limit="Accepted propagated bytes only, not runtime conformance.",
    ),
    "D11-G9-VERIFY-PORT-PLAN-ID-PHASE-AND-REPLAY-CONFORMANCE": route(
        "P9-8.2 P9-8.3C-OS P9-8.4 P9-8.6"
    ),
    "D11-G9-VERIFY-RESOURCE-HISTORY-TARGET-READMISSION-AND-ATOMICITY": route(
        "P9-8.3C-OS P9-8.3C-PC P9-8.3A P9-8.5 P9-9.1"
    ),
    "D11-G9-VERIFY-DISABLED-LEGACY-DEFINED-DOMAIN-FAIL-CLOSED": route(
        "P9-9.2 P9-9.4 P9-9.5"
    ),
}

DEBT_WITHOUT_OBLIGATION = {
    "D5V2-DEBT-CURRENT-SINGULAR-SUCCESSOR": route("P9-3.5", "P9-SCI-SINGULAR"),
    "D6V2-DEBT-C-MATHEMATICAL-ABSORBABILITY": route(
        "P9-10.5", "P9-SCI-PHYSICAL", "retained_scientific_boundary"
    ),
    "D7-DEBT-A-ABSORBABILITY": route(
        "P9-10.5", "P9-SCI-PHYSICAL", "retained_scientific_boundary"
    ),
    "D7-DEBT-A-CORE-STATUS": route(
        "P9-2.6 P9-10.5",
        disposition="retain_resolved_negative",
        limit="Present A remains optional, revision-specific and nonunique; no new core derivation.",
    ),
    "D7-DEBT-A-UNITS-AND-GAUGE": route(
        "P9-2.2", "P9-SCI-UNITS", "retained_scientific_boundary"
    ),
    "D7-DEBT-PHYSICAL-CHANNEL-ATTRIBUTION": route(
        "P9-10.5", "P9-SCI-PHYSICAL", "retained_scientific_boundary"
    ),
    "D7G-DEBT-STAR-PAIR-NORMALIZATION-ALTERNATIVES": route(
        "P9-3.1", "P9-SCI-UNITS", "retained_scientific_boundary"
    ),
    "D7GV2-DEBT-H4-CAPACITY-AND-PROFILE-COMPARABILITY": route(
        "P9-10.5", "P9-SCI-UNITS", "retained_scientific_boundary"
    ),
    "D7V2-DEBT-B-FUTURE-SOURCE-BACKED-WRITER": route(
        "P9-2.6", "P9-SCI-B", "reserved_successor"
    ),
    "D8A-DEBT-HODGE-CORRECTION-NORMATIVE-ENCODING": route(
        "P9-3.1 P9-3.4",
        disposition="retain_confirmed_normative_encoding",
        limit="Accepted specification encodes types; runtime covariance remains separately pending.",
    ),
    "GTRS-CI-PC-DEBT-COMPOSITION-PROFILE-STATUS": route(
        "P9-6.3a P9-6.3b P9-6.3c",
        disposition="retain_narrowed_optional_composition",
        limit="Gain-two composition is optional; no uniqueness, core or amplitude-equivalence claim.",
    ),
    "GTRS-RG-DEBT-C1-SECTION-REGULARITY": route(
        "P9-6.4a P9-6.4b P9-6.4c",
        "P9-SCI-RG-REGULARITY",
        "retain_lipschitz_only_boundary",
    ),
}


def read(path):
    return json.loads((ROOT / path).read_text())


def binding(path):
    return {
        "path": path,
        "sha256": hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
    }


def section(path, title, prefix=False):
    matches = []
    for number, line in enumerate((ROOT / path).read_text().splitlines(), 1):
        match = re.match(r"^#{2,4} (.+)$", line)
        if match and (
            match[1].startswith(title + " ") if prefix else match[1] == title
        ):
            matches.append({"path": path, "heading": match[1], "line": number})
    if len(matches) != 1:
        raise ValueError(f"section is missing or ambiguous: {path}: {title}: {matches}")
    return matches[0]


def contract_group(key):
    if key.startswith("D10.2-EC-DISABLED-") or key == "D11-G9-EC-LEGACY-DEFINED-DOMAIN":
        return "G9_disabled"
    if key.startswith("D11-C-"):
        return "C_baseline"
    if key.startswith("D11-G9-"):
        return "G9_expansion"
    stem = key.removeprefix("D10.2-EC-")
    for prefix, name in [
        ("CI-PC-", "CI_PC"),
        ("CI-", "CI"),
        ("OS-", "OS"),
        ("PC-", "PC"),
        ("RG-", "RG2b"),
        ("C-", "candidate_C"),
        ("CHARGE-", "charge"),
        ("EVENT-", "events"),
        ("GEOM-", "geometry"),
    ]:
        if stem.startswith(prefix):
            return name
    parent = stem.removeprefix("PARENT-")
    for prefix, name in [
        ("A-", "candidate_A"),
        ("C-", "candidate_C"),
        ("GEOM-", "geometry"),
        ("BASE-DISABLED-", "G9_disabled"),
    ]:
        if parent.startswith(prefix):
            return name
    exact = {
        "BASE-GRC-DIFFERENTIAL": "differential",
        "BASE-GRC9-ROW-BASIS-DIFFERENTIAL": "G9_differential",
        "BASE-POTENTIAL": "transport",
        "BASE-POTENTIAL-FLOW": "transport",
        "BASE-SCALAR-MOBILITY": "transport",
        "CORE-C-AUTHORITY": "state",
        "CORE-INCIDENCE-CONTINUITY": "transport",
        "CORE-K-STRUCTURAL-ROLE": "analysis",
        "GRC9-ORDERED-PORTS": "G9_ports",
        "GRC9-ROW-COLUMN-CHART": "G9_ports",
        "GRC9-SATURATION": "G9_completion",
        "GRC9-HYBRID-SPARK": "G9_completion",
        "GRC9-CHILD-BASIN-STABILIZATION": "G9_completion",
        "GRC9-MECHANICAL-EXPANSION": "G9_expansion",
        "GRC9-COLUMN-COARSE-GRAINING": "G9_coarse",
        "L-A-INITIALIZER-GRC": "candidate_A",
        "L-A-INITIALIZER-GRC9V3": "G9_A_initializer",
        "L-ATOMICITY": "step",
        "L-AUTHORITATIVE-CURRENT": "step",
        "L-CONTINUITY-WRITE": "step",
        "L-POSTCONTINUITY-REFRESH": "step",
        "L-SINGULAR-FAIL-CLOSED": "step",
        "L-PROFILE-GRAMMAR": "identity",
        "L-ORDERED-RECEIPTS": "lifecycle",
        "L-SNAPSHOT-RESET": "lifecycle",
        "L-PROFILE-MIGRATION": "events",
        "L-TOPOLOGY-EVENT": "events",
        "REAL-CI": "CI",
        "REAL-OS": "OS",
        "REAL-PC": "PC",
        "REAL-RG2B": "RG2b",
        "REAL-CI-PC": "CI_PC",
        "SPEC-COMPOSITION-PROFILE-IDENTITY": "identity",
        "SPEC-NORMALIZATION-UNITS-GAUGE-DOMAIN-SOLVER": "identity",
        "SPEC-PROFILE-GRAMMAR": "identity",
    }
    if parent in exact:
        return exact[parent]
    if parent in {
        "CORE-CHARGE-TANGENT",
        "CORE-EXTERNAL-EVENT-CHARGE",
        "CORE-GENERAL-CHARGE",
        "CORE-STRUCTURAL-CHARGE-PROJECTOR",
        "CORE-UNIT-MEASURE",
    }:
        return "charge"
    if parent in {
        "SPEC-B-SLOT",
        "SPEC-CLAIM-CEILINGS",
        "SPEC-FUTURE-ADMISSION",
        "SPEC-VERIFICATION-REGISTRY",
    }:
        return "claim_boundary"
    raise ValueError(f"unmapped contract: {key}")


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


def evidence(trace):
    """Compact exact references; full traces are regenerated and digest-bound.

    Direct API witnesses retain every edge locator. Backward reconstruction
    additionally traverses unrelated predecessor branches: retain the edges
    incident to the queried claim and explicitly hash/count the full set.
    """
    rows = []
    for row in trace["rows"]:
        edges = row["edge_refs"]
        selected = edges
        projection = "all_edge_locators"
        if row["classification"] == "accepted_backward_reconstruction":
            node = "current_claim:" + trace["query"]["claim_id"]
            selected = [e for e in edges if node in (e["source"], e["target"])]
            projection = "queried_claim_incident_edges_only_full_trace_regenerated"
        rows.append(
            {
                "classification": row["classification"],
                "source_ref": row["source_ref"],
                "edge_ref_ids": [e["edge_id"] for e in selected],
                "edge_projection": projection,
                "full_edge_ref_count": len(edges),
                "full_edge_refs_sha256": digest(edges),
            }
        )
    return {
        "operation": trace["operation"],
        "query": trace["query"],
        "trace_digest": trace["trace_digest"],
        "rows": rows,
    }


def build():
    context = load_successor_forensic_context(ROOT, SIDE)

    def ids(kind):
        return sorted(
            n["identifier"] for n in context.nodes.values() if n["kind"] == kind
        )

    assert tuple(
        len(ids(k))
        for k in [
            "current_claim",
            "historical_claim",
            "equation_contract",
            "debt_transformation",
            "verification_obligation",
        ]
    ) == (41, 29, 183, 31, 18)
    release = read("specs/grc-v4-specification-release.json")
    assert release["release_id"] == RELEASE_ID
    for member in release["release_identity_payload"]["artifact_bindings"]:
        assert binding(member["path"])["sha256"] == member["sha256"], member["path"]
    assert read(ACCEPT)["status"] == "accepted_frozen"
    assert (
        read(D102)["claim_topology_effect"]["D10_preclosure_obligation"]
        == "resolved_by_accepted_D10_2"
    )
    assert read(PROPAGATION)["paper_source"]["paper_propagation_status"] == "propagated"
    schema = read("specs/grc-v4-contract-schema.json")["$defs"]
    checklist = (
        ROOT / "implementation/Phase-9-GRCV4-ImplementationChecklist.md"
    ).read_text()
    for item in list(OBLIGATION_ROUTES.values()) + list(
        DEBT_WITHOUT_OBLIGATION.values()
    ):
        assert (
            item["phase9_iterations"]
            or item["deferred_gate"]
            or item["downstream_disposition"].startswith("satisfied")
        )
        for step in item["phase9_iterations"]:
            assert step in checklist, step
        assert item["deferred_gate"] is None or item["deferred_gate"] in DEFERRED
    groups = {}
    for key, value in GROUPS.items():
        entry = dict(value)
        entry["spec_sections"] = [section(*s) for s in value["spec_sections"]]
        entry["paper_sections"] = [
            section(PAPER, p, prefix=True) for p in value["paper_section_prefixes"]
        ]
        for definition in entry["machine_schema_definitions"]:
            assert definition in schema, definition
        for step in entry["implementation_iterations"]:
            assert step in checklist, step
        groups[key] = entry
    source_paths = [
        SPEC,
        API,
        G9,
        PAPER,
        INV + "drafts/GRCV4-proposal.md",
        DEBTS,
        D102,
        ACCEPT,
        PROPAGATION,
        "specs/grc-v4-contract-schema.json",
        "specs/grc-v4-conformance-fixtures.json",
        "specs/grc-v4-conformance-vectors.json",
        "specs/grc-v4-specification-release.json",
        "implementation/Phase-9-GRCV4-PhaseOpening.json",
    ]
    base = {
        "schema": "phase9_source_review_v1",
        "preparation_status": "prepared_for_review",
        "baseline_commit": BASE,
        "release_id": RELEASE_ID,
        "forensic_context": {
            "source_bundle_digest": context.source_bundle_digest,
            "graph_digest": context.graph_digest,
            "authority_extension_digest": context.authority_extension_digest,
        },
        "source_bindings": [binding(p) for p in source_paths],
        "authority_boundary": "planning_crosswalk_and_inventory_not_scientific_reclassification_runtime_evidence_or_P9_G1_acceptance",
        "evidence_reference_policy": "Typed API trace digest and exact source_ref/edge_ref_ids; backward-reconstruction edge projection is explicitly labeled and the full witness set is hash/count-bound. Nested predecessor lineage is separately hash-bound, not recopied; full traces are regenerated by this auditor. Literal registry fallback is explicitly labeled.",
    }
    claims = []
    for key in ids("current_claim"):
        trace = reconstruction_path(context, key)
        nodes = trace["rows"][0]["payload"]["nodes"]
        matches = [
            n for n in nodes if n["kind"] == "current_claim" and n["identifier"] == key
        ]
        assert len(matches) == 1, key
        claims.append(
            {
                "claim_id": key,
                "source_claim": matches[0]["attributes"],
                "forensic_evidence": evidence(trace),
            }
        )
    contracts = []
    for key in ids("equation_contract"):
        trace = contract_provenance(context, key)
        payload = trace["rows"][0]["payload"]
        attrs = payload["contract"]["attributes"]
        name = contract_group(key)
        profiles = attrs.get("profile_ids", [])
        scope = "later_profile_or_analysis_inventory"
        if (
            name.startswith("G9_")
            and name != "G9_A_initializer"
            and (not profiles or "C_OS" in profiles)
        ):
            scope = "gated_GRC9V4_C_OS_follow_on"
        elif (
            name not in {"candidate_A", "CI", "PC", "CI_PC", "RG2b", "analysis"}
            and not name.startswith("G9_")
            and (not profiles or "C_OS" in profiles)
        ):
            scope = "proposed_C_OS_generic_first_slice"
        contracts.append(
            {
                "contract_id": key,
                "crosswalk_group": name,
                "planning_scope": scope,
                "source_contract": attrs,
                "support_disposition": payload["support_disposition"],
                "accepted_claim_support_semantics": payload[
                    "accepted_claim_support_semantics"
                ],
                "forensic_evidence": evidence(trace),
            }
        )
    for claim in claims:
        linked = [
            c
            for c in contracts
            if claim["claim_id"] in c["source_contract"].get("accepted_claim_ids", [])
        ]
        claim["source_linked_contract_ids"] = [c["contract_id"] for c in linked]
        claim["crosswalk_groups"] = sorted(
            {"claim_boundary"} | {c["crosswalk_group"] for c in linked}
        )
        claim["mapping_boundary"] = (
            "planning_consumers_not_new_support_edges_or_claim_upgrades"
        )
    debt_rows, forward = [], {}
    for key in ids("debt_transformation"):
        trace = debt_lifecycle(context, key)
        payloads = []
        for row in trace["rows"]:
            payload = dict(row["payload"])
            projection = {"classification": row["classification"], "payload": payload}
            if "predecessor_lineage" in payload:
                lineage = payload.pop("predecessor_lineage")
                projection["predecessor_lineage_reference"] = {
                    "sha256": digest(lineage),
                    "source_ref": row["source_ref"],
                    "payload_field": "predecessor_lineage",
                    "policy": "complete_nested_lineage_retained_in_source_and_regenerated_trace_not_copied",
                }
            payloads.append(projection)
        for index, r in enumerate(trace["rows"]):
            if r["classification"] == "forward_verification_routing":
                forward.setdefault(r["payload"]["obligation_id"], []).append(
                    {
                        "debt_id": key,
                        "trace_digest": trace["trace_digest"],
                        "row_index": index,
                    }
                )
        first = trace["rows"][0]["payload"]
        if key.startswith("D11-"):
            routing = route(
                disposition="retain_bounded_design_resolution",
                limit="Only local missing design authority is resolved; original D10 debt and all runtime obligations retain their scope.",
            )
            routing["forward_obligation_ids"] = [
                r["payload"]["obligation_id"]
                for r in trace["rows"]
                if r["classification"] == "forward_verification_routing"
            ]
            routing["bounded_resolution_claim_id"] = (
                "D11-C-CL-O-001" if key.startswith("D11-C-") else "D11-G9-CL-N-001"
            )
            assert routing["bounded_resolution_claim_id"] in ids("current_claim")
        else:
            obligation = first.get("verification_obligation")
            routing = (
                OBLIGATION_ROUTES[obligation]
                if obligation
                else DEBT_WITHOUT_OBLIGATION[key]
            )
        debt_rows.append(
            {
                "debt_id": key,
                "historical_rows": payloads,
                "phase9_route": routing,
                "forensic_evidence": evidence(trace),
            }
        )
    literal_obligations = read(DEBTS)["verification_obligations"]
    obligation_rows = []
    for key in ids("verification_obligation"):
        n = context.nodes[f"verification_obligation:{key}"]  # locator discovery only
        if key.startswith("D11-"):
            debt = next(
                d
                for d in debt_rows
                if key in d["phase9_route"].get("forward_obligation_ids", [])
            )
            index = next(
                i
                for i, r in enumerate(debt["historical_rows"])
                if r["payload"].get("obligation_id") == key
            )
            source_ref = debt["forensic_evidence"]["rows"][index]["source_ref"]
            payload = debt["historical_rows"][index]["payload"]
        else:
            index = next(
                i
                for i, p in enumerate(literal_obligations)
                if p["obligation_id"] == key
            )
            payload = literal_obligations[index]
            source_ref = {
                **binding(DEBTS),
                "record_id": n["source_record_id"],
                "source_json_pointer": f"/verification_obligations/{index}",
            }
        for witness in forward.get(key, []):
            owner = next(d for d in debt_rows if d["debt_id"] == witness["debt_id"])
            observed = owner["historical_rows"][witness["row_index"]]["payload"]
            assert observed == payload, f"literal/API obligation mismatch: {key}"
        result = {
            "obligation_id": key,
            "source_payload": payload,
            "source_ref": source_ref,
            "access_method": (
                "typed_debt_lifecycle_forward_row"
                if key.startswith("D11-")
                else "literal_registry_with_typed_debt_lifecycle_forward_crosscheck"
                if key in forward
                else "literal_verification_registry_no_dedicated_public_query"
            ),
            "typed_forward_witnesses": forward.get(key, []),
            "phase9_route": OBLIGATION_ROUTES[key],
        }
        if key == "D10-PRECLOSE-SUBSTRATE-PROVENANCE-AUDIT":
            result["downstream_evidence"] = [
                {
                    **binding(D102),
                    "source_json_pointer": "/claim_topology_effect/D10_preclosure_obligation",
                }
            ]
        elif "PROPAGATION" in key:
            result["downstream_evidence"] = [
                binding(PROPAGATION),
                binding(ACCEPT),
                binding("specs/grc-v4-specification-release.json"),
            ]
        obligation_rows.append(result)
    assert set(OBLIGATION_ROUTES) == set(ids("verification_obligation"))
    unresolved_locator = "D10_2_CL_N_001"
    try:
        reconstruction_path(context, unresolved_locator)
    except KeyError:
        locator = {
            "text": unresolved_locator,
            "api_disposition": "unknown_claim",
            "literal_source": {
                **binding(D102),
                "source_json_pointer": "/claim_topology_effect/D10_2_CL_N_001",
            },
            "source_text": read(D102)["claim_topology_effect"][unresolved_locator],
        }
    else:
        raise AssertionError("provenance-only locator was silently admitted")
    return {
        "P9-1.1-SourceCrosswalk.json": {
            **base,
            "iteration_id": "P9-1.1",
            "groups": groups,
            "claims": claims,
            "contracts": contracts,
            "provenance_only_locator": locator,
            "summary": {
                "current_claims": len(claims),
                "equation_contracts": len(contracts),
                "support_dispositions": dict(
                    Counter(
                        json.dumps(c["support_disposition"], sort_keys=True)
                        for c in contracts
                    )
                ),
            },
        },
        "P9-1.2-DebtInventory.json": {
            **base,
            "iteration_id": "P9-1.2",
            "historical_claim_ids": ids("historical_claim"),
            "debts": debt_rows,
            "deferred_gates": DEFERRED,
            "summary": {
                "D10_debts": 29,
                "D11_local_debts": 2,
                "source_status_changes": 0,
                "new_debt_discharges": 0,
            },
        },
        "P9-1.3-VerificationRouting.json": {
            **base,
            "iteration_id": "P9-1.3",
            "obligations": obligation_rows,
            "deferred_gates": DEFERRED,
            "summary": {
                "source_obligations": 18,
                "satisfied_bounded_preclose": 1,
                "satisfied_downstream_propagation": 2,
                "pending_runtime_or_scientific_evidence": 15,
                "discharged_by_this_batch": 0,
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--emit",
        choices=[
            "P9-1.1-SourceCrosswalk.json",
            "P9-1.2-DebtInventory.json",
            "P9-1.3-VerificationRouting.json",
            "sizes",
        ],
    )
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    artifacts = build()
    rendered = {
        name: json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        for name, value in artifacts.items()
    }
    if args.emit == "sizes":
        print(json.dumps({name: len(value) for name, value in rendered.items()}))
    elif args.emit:
        end = None if args.limit is None else args.offset + args.limit
        print(rendered[args.emit][args.offset : end], end="")
    else:
        for name, value in artifacts.items():
            assert json.loads((OUT / name).read_text()) == value, (
                f"review artifact drift: {name}"
            )
        record = json.loads((OUT / "P9-1.1-1.3-ExecutionRecord.json").read_text())
        assert record["baseline_commit"] == BASE
        assert record["release_id"] == RELEASE_ID
        assert record["status"] == "prepared_for_review"
        assert record["runtime_authorized"] is False
        assert (
            record["gate_effect"] == "none_P9_G1_and_all_runtime_gates_remain_pending"
        )
        expected_bound = set(artifacts) | {
            "audit_source_review.py",
            "P9-1.1-1.3-Review.md",
        }
        assert {
            Path(b["path"]).name for b in record["artifact_bindings"]
        } == expected_bound
        assert len(record["artifact_bindings"]) == len(expected_bound)
        for member in record["artifact_bindings"]:
            assert member["path"] == str(
                (OUT / Path(member["path"]).name).relative_to(ROOT)
            )
            assert binding(member["path"]) == member, member["path"]
        assert [r["iteration_id"] for r in record["iteration_results"]] == [
            "P9-1.1",
            "P9-1.2",
            "P9-1.3",
        ]
        for row in record["iteration_results"]:
            assert row["reviewer_decision"] == "pending_user_review"
            assert row["result"] == "artifact_prepared_and_source_validation_passed"
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", BASE, "HEAD"], cwd=ROOT, check=True
        )
        print(
            "PHASE9_SOURCE_REVIEW_AUDIT_PASS iterations=P9-1.1,P9-1.2,P9-1.3 claims=41 contracts=183 debts=31 obligations=18 pending_evidence=15 runtime_authorized=false"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

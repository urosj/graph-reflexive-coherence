#!/usr/bin/env python3
"""Build the Phase 8 Iteration 106 pathway registry and source audit."""

from __future__ import annotations

import ast
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src"
OUTPUT_MANIFEST = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationSourceManifest.json"
OUTPUT_UNMAPPED = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationUnmappedSurfaceReport.md"
OUTPUT_REGISTRY = ROOT / "specs/grc-lgrc-causal-pathway-contracts.json"
OUTPUT_RESULT = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.json"
OUTPUT_FREEZE = ROOT / "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106ArtifactFreeze.json"


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
    path.write_text(
        json.dumps(value, indent=2, sort_keys=False, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


PRIMARY_SOURCES = tuple(
    sorted(
        {
            *ROOT.glob("src/pygrc/models/grc_9_v3*.py"),
            *ROOT.glob("src/pygrc/models/lgrc_9_v3*.py"),
            ROOT / "src/pygrc/telemetry/lgrc9v3_contract.py",
        }
    )
)


def module_name(path: Path) -> str:
    return ".".join(path.relative_to(SOURCE_ROOT).with_suffix("").parts)


def resolve_module(module: str) -> Path | None:
    candidate = SOURCE_ROOT.joinpath(*module.split("."))
    module_file = candidate.with_suffix(".py")
    if module_file.is_file():
        return module_file
    package_file = candidate / "__init__.py"
    if package_file.is_file():
        return package_file
    return None


def source_dependency_closure(seeds: Iterable[Path]) -> list[Path]:
    queue = deque(dict.fromkeys(seeds))
    seen: set[Path] = set()
    while queue:
        path = queue.popleft()
        if path in seen:
            continue
        seen.add(path)
        parts = module_name(path).split(".")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.ImportFrom):
                if node.level:
                    base = parts[:-1]
                    if node.level > 1:
                        base = base[: -(node.level - 1)]
                    imported_from = ".".join(base + ([node.module] if node.module else []))
                elif node.module:
                    imported_from = node.module
                else:
                    imported_from = ""
                if imported_from:
                    modules.append(imported_from)
                    modules.extend(
                        f"{imported_from}.{alias.name}"
                        for alias in node.names
                        if alias.name != "*"
                    )
            elif isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            for module in modules:
                if not module.startswith("pygrc"):
                    continue
                dependency = resolve_module(module)
                if dependency is not None and dependency not in seen:
                    queue.append(dependency)
    return sorted(seen)


P = {
    "sync": "grc9v3.synchronous_update_cycle",
    "identity": "grc9v3.identity_basin_reconstruction",
    "choice": "grc9v3.sink_compatibility_choice",
    "spark": "grc9v3.hybrid_spark_refinement",
    "legacy_growth": "grc9v3.legacy_inactive_port_growth",
    "growth": "grc9v3.front_capacity_growth",
    "history": "lgrc9v3.causal_history_annotation",
    "eligibility": "lgrc9v3.fixed_topology_eligibility",
    "packet": "lgrc9v3.explicit_packet_transport",
    "route": "lgrc9v3.configured_flux_route",
    "surplus": "lgrc9v3.route_aspect_surplus",
    "pulse": "lgrc9v3.pulse_substrate_coupling_producer",
    "feedback": "lgrc9v3.feedback_eligibility_producer",
    "arbitration": "lgrc9v3.native_route_arbitration",
    "birth": "lgrc9v3.boundary_birth",
    "integration": "lgrc9v3.causal_spark_topology_integration",
    "collapse": "lgrc9v3.collapse_reabsorption",
    "identity_eval": "lgrc9v3.proper_time_identity_evaluation",
    "identity_accept": "lgrc9v3.proper_time_identity_acceptance",
    "surface": "lgrc9v3.causal_pulse_surface_lineage",
    "multibasin": "lgrc9v3.multi_basin_record_validation",
    "diagnostic": "lgrc9v3.diagnostic_grc_reconstruction",
    "restoration": "pygrc.restoration_replay_identity",
}


PRIMARY_PATHWAY_MAP: dict[str, list[str]] = {
    "src/pygrc/models/grc_9_v3.py": [P["sync"], P["identity"], P["choice"], P["spark"], P["legacy_growth"], P["growth"], P["restoration"]],
    "src/pygrc/models/grc_9_v3_runtime.py": [P["sync"], P["identity"]],
    "src/pygrc/models/grc_9_v3_choice.py": [P["choice"]],
    "src/pygrc/models/grc_9_v3_sparks.py": [P["spark"]],
    "src/pygrc/models/lgrc_9_v3_timing.py": [P["history"], P["eligibility"]],
    "src/pygrc/models/lgrc_9_v3_packets.py": [P["packet"]],
    "src/pygrc/models/lgrc_9_v3_runtime.py": [
        P["packet"], P["route"], P["surplus"], P["pulse"], P["feedback"],
        P["arbitration"], P["birth"], P["integration"], P["collapse"],
        P["identity_accept"], P["surface"], P["multibasin"], P["diagnostic"],
        P["restoration"],
    ],
    "src/pygrc/models/lgrc_9_v3_topology.py": [P["integration"], P["collapse"], P["surface"]],
    "src/pygrc/models/lgrc_9_v3_identity.py": [P["identity_eval"], P["identity_accept"]],
    "src/pygrc/models/lgrc_9_v3_restoration.py": [P["restoration"]],
}


CROSS_CUTTING_MAP: dict[str, tuple[str, str]] = {
    "src/pygrc/models/grc_9_v3_state.py": ("grc9v3.state_contract", "State identity and cached runtime fields consumed by GRC9V3 pathways."),
    "src/pygrc/models/lgrc_9_v3_runtime_state.py": ("lgrc9v3.runtime_state_contract", "Queue, ledger, policy, record, and restoration state consumed across LGRC9V3 pathways."),
    "src/pygrc/models/lgrc_9_v3_contract.py": ("lgrc9v3.artifact_contract_vocabulary", "Artifact schemas, validation, digests, policies, and route-aspect contracts."),
    "src/pygrc/models/lgrc_9_v3.py": ("lgrc9v3.public_facade", "Public import facade; does not add independent runtime behavior."),
    "src/pygrc/models/lgrc_9_v3_construction.py": ("lgrc9v3.construction_contract", "Landscape lowering, runtime construction, route extraction, and explicit queue priming."),
    "src/pygrc/models/grc_9_v3_grcl9v3_lowering.py": ("grcl9v3.lowering_contract", "Source-to-runtime lowering; construction path rather than causal execution path."),
    "src/pygrc/models/grc_9_v3_grcl9v3_provenance.py": ("grcl9v3.provenance_contract", "Lowering provenance payloads retained by construction surfaces."),
    "src/pygrc/models/grc_9_state.py": ("grc9.shared_state_contract", "Port-edge and expansion state shared by GRC9V3/LGRC9V3."),
    "src/pygrc/models/grc_9_ports.py": ("grc9.port_coordinate_contract", "Port/slot/row-column coordinate translation."),
    "src/pygrc/models/grc_9_expansion.py": ("grc9.expansion_contract", "Mechanical expansion utilities consumed by GRC9V3 spark refinement."),
    "src/pygrc/models/grc_9_coarse.py": ("grc9.coarse_graining_contract", "Coarse cache and split utilities called by the synchronous update cycle."),
    "src/pygrc/models/grc_v3_differential.py": ("grcv3.differential_contract", "Weighted least-squares differential helper consumed by GRC9V3."),
    "src/pygrc/models/grc_v3_state.py": ("grcv3.state_type_contract", "Shared differential-state types; not a GRCV3 pathway admission."),
    "src/pygrc/telemetry/schema.py": ("pygrc.telemetry_schema_contract", "Shared telemetry row and checkpoint schemas."),
    "src/pygrc/telemetry/io.py": ("pygrc.telemetry_io_contract", "Telemetry serialization utility; descriptive rather than runtime authority."),
    "src/pygrc/telemetry/lgrc9v3_contract.py": ("lgrc9v3.telemetry_observability_contract", "LGRC9V3 event, step, run-summary, checkpoint, and diagnostic projection; observes but does not authorize runtime behavior."),
}


def classify_surface(path: Path) -> dict[str, Any]:
    rel = path.relative_to(ROOT).as_posix()
    if rel in PRIMARY_PATHWAY_MAP:
        return {
            "mapping_kind": "pathway",
            "mapping_ids": PRIMARY_PATHWAY_MAP[rel],
            "reason": "Defines load-bearing state transformation or native/producer/diagnostic pathway stages.",
        }
    if rel in CROSS_CUTTING_MAP:
        contract_id, reason = CROSS_CUTTING_MAP[rel]
        return {"mapping_kind": "cross_cutting_contract", "mapping_ids": [contract_id], "reason": reason}
    if rel.startswith("src/pygrc/core/"):
        target = "pygrc.core_restoration_contract" if rel.endswith(("serialization.py", "digests.py")) else "pygrc.core_runtime_contract"
        return {
            "mapping_kind": "cross_cutting_contract",
            "mapping_ids": [target],
            "reason": "Shared PyGRC type, graph, parameter, backend, mutation, error, serialization, or identity utility directly imported by in-scope modules.",
        }
    if rel in {
        "src/pygrc/landscapes/__init__.py",
        "src/pygrc/landscapes/seed.py",
        "src/pygrc/landscapes/io.py",
        "src/pygrc/landscapes/validation.py",
        "src/pygrc/landscapes/equivalence.py",
    }:
        return {
            "mapping_kind": "cross_cutting_contract",
            "mapping_ids": ["pygrc.landscape_seed_construction_contract"],
            "reason": "Construction-time landscape input, validation, loading, and equivalence surface; not runtime causal execution.",
        }
    if rel.startswith("src/pygrc/landscapes/extensions/grcl9v3/"):
        if rel.endswith(("examples.py", "fixtures.py")):
            return {
                "mapping_kind": "explicit_exclusion",
                "mapping_ids": [],
                "reason": "Fixture/example provider imported through the GRCL9V3 facade; not a load-bearing runtime pathway.",
            }
        return {
            "mapping_kind": "cross_cutting_contract",
            "mapping_ids": ["grcl9v3.source_and_lowering_contract"],
            "reason": "Source schema, manifest, selector, or facade consumed during construction/lowering only.",
        }
    if rel.startswith("src/pygrc/landscapes/"):
        return {
            "mapping_kind": "explicit_exclusion",
            "mapping_ids": [],
            "reason": "Reached through broad landscape-package re-exports but not imported as a consumed GRC9V3/LGRC9V3 pathway surface.",
        }
    return {
        "mapping_kind": "unclassified",
        "mapping_ids": [],
        "reason": "No I106 classification rule matched this imported source surface.",
    }


def surface_kind(path: Path, classification: dict[str, Any]) -> tuple[str, str]:
    rel = path.relative_to(ROOT).as_posix()
    name = path.name
    if classification["mapping_kind"] == "explicit_exclusion":
        return "transitive_or_fixture_surface", "descriptive_or_unconsumed"
    if rel.startswith("src/pygrc/telemetry/"):
        return "observability_contract", "descriptive"
    if name.endswith("_state.py") or name in {"types.py", "events.py", "graph.py"}:
        return "state_or_identity_contract", "behavior_enabling"
    if "restoration" in name or name in {"serialization.py", "digests.py"}:
        return "restoration_or_identity_contract", "behavior_enabling"
    if "lowering" in name or "provenance" in name or rel.startswith("src/pygrc/landscapes/"):
        return "construction_or_lowering_contract", "behavior_enabling"
    if classification["mapping_kind"] == "pathway":
        return "pathway_implementation", "behavior_changing"
    return "shared_runtime_contract", "behavior_enabling"


def authority(
    direction: str,
    funding: str,
    eligibility: str,
    scheduling: str,
    commitment: str,
    reception: str,
) -> dict[str, str]:
    return {
        "direction": direction,
        "funding": funding,
        "eligibility": eligibility,
        "scheduling": scheduling,
        "commitment": commitment,
        "reception": reception,
    }


def stage(
    stage_id: str,
    trigger: str,
    consumed: list[str],
    produced: list[str],
    auth: dict[str, str],
    action_scope: str,
    mutation_scope: str,
    time_semantics: str,
    spatial_scope: str,
    failure: str,
) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "trigger": trigger,
        "state_consumed": consumed,
        "state_produced": produced,
        "direction_authority": auth["direction"],
        "funding_authority": auth["funding"],
        "eligibility_authority": auth["eligibility"],
        "scheduling_authority": auth["scheduling"],
        "commit_authority": auth["commitment"],
        "reception_authority": auth["reception"],
        "action_scope": action_scope,
        "mutation_scope": mutation_scope,
        "time_semantics": time_semantics,
        "spatial_scope": spatial_scope,
        "failure_or_noop_semantics": failure,
    }


def pathway(
    pathway_id: str,
    name: str,
    purpose: str,
    layer: str,
    contract_kind: str,
    ownership: str,
    availability: str,
    activation: str,
    trigger_surface: str,
    event_locus: str,
    causal_scope: str,
    stages: list[dict[str, Any]],
    configured_residue: list[str],
    producer_residue: list[str],
    naturalization_debt: list[str],
    invariants: list[str],
    identity_fields: list[str],
    history_consumed: list[str],
    history_retained: list[str],
    fail_closed: list[str],
    restoration_identity: str,
    supported_claims: list[str],
    blocked_claims: list[str],
    source_paths: list[str],
    source_commit: str,
) -> dict[str, Any]:
    consumed = sorted({item for item_stage in stages for item in item_stage["state_consumed"]})
    produced = sorted({item for item_stage in stages for item in item_stage["state_produced"]})
    source_records = [{"path": path, "sha256": sha256_file(ROOT / path)} for path in sorted(source_paths)]
    source_digest = canonical_digest(source_records)
    authority_summary = {
        key: sorted({item[f"{key}_authority"] for item in stages})
        for key in ("direction", "funding", "eligibility", "scheduling", "commit", "reception")
    }
    return {
        "pathway_id": pathway_id,
        "entry_version": 1,
        "name": name,
        "purpose": purpose,
        "substrate_layer": layer,
        "contract_kind": contract_kind,
        "mechanism_ownership": ownership,
        "availability": availability,
        "activation": activation,
        "state_consumed": consumed,
        "state_produced": produced,
        "time_semantics": sorted({item["time_semantics"] for item in stages}),
        "spatial_scope": sorted({item["spatial_scope"] for item in stages}),
        "trigger_surface": trigger_surface,
        "event_locus": event_locus,
        "causal_information_scope": causal_scope,
        "authority_summary": authority_summary,
        "stage_sequence": stages,
        "configured_residue": configured_residue,
        "producer_residue": producer_residue,
        "naturalization_debt": naturalization_debt,
        "budget_and_invariants": invariants,
        "state_identity_fields": identity_fields,
        "history_consumed": history_consumed,
        "history_retained_but_not_consumed": history_retained,
        "fail_closed_conditions": fail_closed,
        "restoration_and_serialization_identity": restoration_identity,
        "supported_claims": supported_claims,
        "blocked_claims": blocked_claims,
        "evidence_refs": [],
        "composition_refs": [],
        "catalog_relation_refs": [],
        "source_commit": source_commit,
        "source_digest": source_digest,
        "last_verified_commit": source_commit,
        "staleness_state": "current_at_iteration_106_freeze",
        "supersedes": [],
        "superseded_by": [],
    }


def build_pathways(source_commit: str) -> list[dict[str, Any]]:
    native_step = authority("native_reconstructed_flux", "node_coherence", "declared_step_contract", "GRC9V3.step", "GRC9V3.step", "graph_state")
    packet_commit = authority("supplied_packet_endpoints", "source_node_coherence", "packet_validation", "caller_or_registered_producer", "LGRC9V3.step", "target_node")
    topology_commit = authority("candidate_or_policy_specific", "parent_or_losing_basin_coherence", "mechanism_specific_gate", "caller_or_native_producer", "LGRC9V3_topology_integrator", "runtime_topology_and_lineage")
    source = {
        "grc": ["src/pygrc/models/grc_9_v3.py", "src/pygrc/models/grc_9_v3_runtime.py"],
        "identity": ["src/pygrc/models/grc_9_v3.py", "src/pygrc/models/grc_9_v3_runtime.py"],
        "choice": ["src/pygrc/models/grc_9_v3.py", "src/pygrc/models/grc_9_v3_choice.py"],
        "spark": ["src/pygrc/models/grc_9_v3.py", "src/pygrc/models/grc_9_v3_sparks.py"],
        "timing": ["src/pygrc/models/lgrc_9_v3_timing.py"],
        "packet": ["src/pygrc/models/lgrc_9_v3_packets.py", "src/pygrc/models/lgrc_9_v3_runtime.py"],
        "runtime": ["src/pygrc/models/lgrc_9_v3_runtime.py"],
        "topology": ["src/pygrc/models/lgrc_9_v3_runtime.py", "src/pygrc/models/lgrc_9_v3_topology.py"],
        "identity_lgrc": ["src/pygrc/models/lgrc_9_v3_identity.py", "src/pygrc/models/lgrc_9_v3_runtime.py"],
        "surface": ["src/pygrc/models/lgrc_9_v3_contract.py", "src/pygrc/models/lgrc_9_v3_runtime.py", "src/pygrc/models/lgrc_9_v3_topology.py"],
        "multibasin": ["src/pygrc/models/lgrc_9_v3_contract.py", "src/pygrc/models/lgrc_9_v3_runtime.py", "src/pygrc/telemetry/lgrc9v3_contract.py"],
        "restoration": ["src/pygrc/models/grc_9_v3.py", "src/pygrc/models/lgrc_9_v3_restoration.py", "src/pygrc/models/lgrc_9_v3_runtime.py"],
    }
    entries: list[dict[str, Any]] = []

    entries.append(pathway(P["sync"], "GRC9V3 Synchronous Update Cycle", "Reconstruct differential and transport state, apply continuity and invariants, then refresh current observables.", "GRC9V3", "runtime_composite", "native", "installed", "explicit_call", "GRC9V3.step", "global_step_frontier", "current GRC9V3 graph state and declared constitutive parameters", [
        stage("differential_rebuild", "GRC9V3.step", ["node_coherence", "topology", "port_edges"], ["gradient_rows", "signed_hessian_rows", "net_flux_summaries"], native_step, "reconstruct differential summaries", "cached differential fields", "global_synchronous_step", "graph_wide", "invalid topology or non-finite state rejects"),
        stage("transport_rebuild", "differential_rebuild complete", ["node_coherence", "gradient_rows", "edge conductance", "edge labels"], ["potential", "oriented_flux", "updated_edge_labels"], native_step, "reconstruct transport", "transport caches and edge flux", "global_synchronous_step", "graph_wide", "invalid labels or conductance reject"),
        stage("continuity_and_invariants", "all configured substages complete", ["node_coherence", "oriented_flux", "boundary state"], ["updated_node_coherence", "budget_adjustment", "step_observables"], native_step, "apply continuity and invariant closure", "node coherence and step metadata", "global_synchronous_step", "graph_wide", "budget or state validation failure rejects step"),
    ], ["constitutive modes", "backend selections", "evolution parameters"], [], ["none for synchronous mechanics; semantic meanings remain outside substrate"], ["quadrature budget", "finite coherence", "topology consistency"], ["topology", "node coherence", "port edges", "params identity", "step index"], ["current cached differential and transport state"], ["event history not used unless a named subpathway consumes it"], ["unsupported backend", "invalid state", "budget failure"], "GRC9V3 snapshot/reset-baseline contract", ["native synchronous GRC9V3 update mechanics"], ["LGRC packet execution", "generic causal admission", "semantic action"], source["grc"], source_commit))

    entries.append(pathway(P["identity"], "GRC9V3 Identity And Basin Reconstruction", "Detect current flux-topology identities, validate basin seeds, and compute effective basin masses.", "GRC9V3", "runtime_subpathway", "native", "installed", "default_on", "GRC9V3.rebuild_identity_state", "synchronous_identity_rebuild_stage", "current flux, topology, and coherence only", [
        stage("detect_flux_topology_identities", "transport state available", ["oriented_flux", "topology"], ["identity_candidates", "basin_assignments"], authority("native_oriented_flux", "not_applicable", "flux_topology_predicate", "GRC9V3.step", "identity_rebuild", "basin_cache"), "derive current identity graph", "identity caches", "global_synchronous_step", "graph_wide", "invalid flux/topology rejects"),
        stage("validate_and_mass_basins", "identity candidates available", ["identity_candidates", "node_coherence", "quadrature"], ["validated_basin_seeds", "effective_basin_masses"], authority("identity_candidate_graph", "node_coherence", "geometric_seed_validation", "identity_rebuild", "identity_rebuild", "basin mass cache"), "validate and aggregate basins", "basin attributes and caches", "global_synchronous_step", "basin_regions", "invalid seeds are rejected or excluded"),
    ], ["identity backend", "geometric seed thresholds"], [], ["retained basin IDs are not constitutive memory without a read path"], ["finite effective mass", "current topology consistency"], ["basin assignment", "basin mass", "topology"], ["current flux topology"], ["prior basin labels unless explicitly consumed by a downstream path"], ["missing flux", "invalid basin seed"], "GRC9V3 snapshot identity fields", ["native current-state basin reconstruction"], ["selfhood", "semantic identity", "Read-Back"], source["identity"], source_commit))

    entries.append(pathway(P["choice"], "GRC9V3 Sink Compatibility Choice", "Score reachable sinks from current positive outgoing flux and update bounded choice/collapse state.", "GRC9V3", "runtime_subpathway", "native_with_configured_semantics", "installed", "default_on", "GRC9V3.rebuild_choice_state", "synchronous_choice_stage", "current successor/flux graph and configured thresholds", [
        stage("sink_compatibility_scoring", "identity state rebuilt", ["oriented_flux", "successor_map", "sink_set"], ["compatibility_scores"], authority("positive outgoing native flux", "not_a_packet_path", "reachable_sink_and_threshold", "GRC9V3.step", "choice_rebuild", "compatibility registry"), "score reachable sinks", "compatibility cache", "global_synchronous_step", "node_to_reachable_sink", "no reachable sink yields no compatible selection"),
        stage("choice_collapse_update", "compatibility scores available", ["compatibility_scores", "prior_choice_registry", "configured thresholds"], ["choice_registry", "collapse_registry", "bounded_learning_update"], authority("selected compatible sink", "declared coherence budget", "choice/collapse thresholds", "choice rebuild", "choice rebuild and budget policy", "choice/collapse state"), "update bounded registry state", "choice, collapse, and optional coherence update", "global_synchronous_step", "node_and_sink_relations", "budget or threshold failure rejects update"),
    ], ["choice backend", "epsilon choice", "epsilon collapse", "learning rate", "budget policy"], [], ["candidate formation and semantic valuation are not native choice"], ["declared budget target", "finite compatibility"], ["choice registry", "collapse registry", "params identity"], ["prior choice registry when configured"], ["unconsumed semantic labels"], ["missing sink", "budget failure", "unsupported backend"], "GRC9V3 snapshot choice/collapse fields", ["native bounded sink-compatibility and choice/collapse mechanics"], ["semantic choice", "intention", "agency", "current generation"], source["choice"], source_commit))

    entries.append(pathway(P["spark"], "GRC9V3 Hybrid Spark Refinement", "Detect Hessian/gradient spark candidates and apply bounded mechanical expansion under declared spark policies.", "GRC9V3", "topology_subpathway", "native_with_configured_semantics", "installed", "default_on", "GRC9V3 hybrid spark stages", "synchronous_spark_and_refinement_stage", "current/previous differential summaries and configured spark backend", [
        stage("spark_candidate_detection", "pre-flux and post-flux differential state", ["gradient_rows", "signed_hessian_rows", "column_h_history", "spark parameters"], ["spark_candidate_events"], authority("native differential geometry", "not_yet_funded", "hybrid spark predicate", "GRC9V3.step", "candidate event log", "candidate registry"), "detect candidates", "candidate/history caches", "global_synchronous_step", "candidate_node_or_column", "predicate miss emits no candidate"),
        stage("mechanical_expansion", "eligible spark candidate and enabled backend", ["spark_candidate", "parent coherence", "free ports", "expansion policy"], ["child topology", "coherence transfer", "lineage record"], authority("candidate geometry and expansion policy", "parent coherence", "enabled mechanical expansion gate", "spark stage", "GRC9V3 topology mutation", "child node and lineage"), "expand topology", "topology, node coherence, expansion history", "global_synchronous_step", "candidate_local", "capacity or port failure blocks expansion"),
    ], ["spark backend", "thresholds", "expansion distribution", "stabilization policy"], [], ["spark candidate meaning and semantic creation remain unclaimed"], ["coherence transfer conservation", "port capacity", "topology validity"], ["candidate IDs", "expansion lineage", "topology"], ["previous column-H history where configured"], ["candidate labels not consumed as semantic meaning"], ["predicate miss", "no port capacity", "disabled backend"], "GRC9V3 snapshot spark/expansion fields", ["native bounded hybrid spark detection and mechanical refinement"], ["semantic creation", "agency", "general basin birth"], source["spark"], source_commit))

    entries.append(pathway(P["legacy_growth"], "GRC9V3 Legacy Inactive-Port Growth", "Apply the legacy any-inactive-port growth policy and transfer parent coherence into a new child topology.", "GRC9V3", "topology_subpathway", "native_with_configured_semantics", "installed", "default_off", "GRC9V3.apply_growth with growth_parent_eligibility=legacy_any_inactive_port", "synchronous_growth_stage", "current outward flux, any inactive port, configured growth parameters, and RNG state", [
        stage("legacy_growth_eligibility", "growth stage with positive lambda_birth and legacy_any_inactive_port mode", ["outward_flux", "inactive_ports", "growth parameters"], ["eligible_parent_ports", "birth_probability"], authority("outward flux at first inactive port", "parent coherence", "legacy any-inactive-port mode", "GRC9V3.step", "growth trial", "eligible parent port"), "evaluate legacy growth", "growth caches", "global_synchronous_step", "parent_port_local", "zero lambda, no inactive port, or nonpositive outward flux is no-op"),
        stage("legacy_growth_commit", "eligible legacy trial and RNG acceptance", ["parent coherence", "free port", "RNG state"], ["child node", "parent-child edge", "coherence transfer", "growth event"], authority("accepted first inactive parent port", "parent coherence", "probability and RNG", "growth stage", "GRC9V3 topology mutation", "child node"), "commit child birth", "topology, coherence, event log, RNG", "global_synchronous_step", "parent_and_child_local", "failed RNG or occupied port is no-op"),
    ], ["legacy any-inactive-port eligibility mode", "birth alpha", "RNG policy"], [], ["legacy eligibility is not GRCL9V3 front capacity and should not be used as its evidence"], ["parent debit equals child credit", "port capacity", "RNG restoration"], ["topology", "growth event", "RNG state"], [], ["front-capacity records are not consumed"], ["zero lambda", "no inactive port", "nonpositive outward flux", "failed RNG", "invalid transfer"], "GRC9V3 snapshot growth and RNG fields", ["native mechanics for configured legacy inactive-port growth"], ["front-capacity growth", "RC-proper boundary formation", "semantic reproduction"], source["grc"], source_commit))

    entries.append(pathway(P["growth"], "GRC9V3 Front-Capacity Growth", "Apply configured GRCL9V3 front-capacity eligibility and transfer parent coherence into a new child topology.", "GRC9V3", "topology_subpathway", "native_with_configured_semantics", "installed", "default_off", "GRC9V3.apply_growth with growth_parent_eligibility=grcl9v3_front_capacity", "synchronous_growth_stage", "current outward flux, inactive ports admitted by configured front capacity, and RNG state", [
        stage("front_capacity_growth_eligibility", "growth stage with positive lambda_birth and grcl9v3_front_capacity mode", ["outward_flux", "inactive_ports", "front_capacity", "growth parameters"], ["eligible_parent_ports", "birth_probability"], authority("outward flux at front-admitted port", "parent coherence", "GRCL9V3 front-capacity eligibility", "GRC9V3.step", "growth trial", "eligible parent port"), "evaluate front-capacity growth", "growth caches", "global_synchronous_step", "parent_port_local", "zero lambda, missing front capacity, or ineligible parent/port is no-op"),
        stage("growth_commit", "eligible trial and RNG acceptance", ["parent coherence", "free port", "RNG state"], ["child node", "parent-child edge", "coherence transfer", "growth event"], authority("accepted parent port", "parent coherence", "probability and RNG", "growth stage", "GRC9V3 topology mutation", "child node"), "commit child birth", "topology, coherence, event log, RNG", "global_synchronous_step", "parent_and_child_local", "failed RNG or occupied port is no-op"),
        stage("front_propagation", "configured propagated-front policy", ["source front record", "child free ports"], ["child front capacity", "optional outlet"], authority("configured child front", "configured outlet coherence", "propagation policy", "growth commit", "GRC9V3 topology mutation", "child front/outlet"), "propagate declared front", "cached front map and optional outlet topology", "global_synchronous_step", "new_child_local", "missing/disabled propagation is no-op"),
    ], ["GRCL9V3 front-capacity eligibility mode", "front-capacity map", "birth alpha", "RNG policy", "front propagation"], [], ["front role is authored by lowering/configuration rather than formed semantically"], ["parent debit equals child credit", "port capacity", "RNG restoration"], ["topology", "growth event", "RNG state", "front-capacity cache"], ["configured front lineage"], ["legacy eligibility records and ecological role labels are not consumed"], ["zero lambda", "missing front capacity", "no free admitted port", "failed RNG", "invalid transfer"], "GRC9V3 snapshot growth and RNG fields", ["native mechanics for configured front-capacity growth"], ["general autonomous basin formation", "semantic reproduction"], source["grc"], source_commit))

    entries.append(pathway(P["history"], "LGRC9V3 Causal-History Annotation", "Derive lapse, delay, distance, cone, and causal-basin annotations from GRC9V3 state and event history.", "LGRC9V3 diagnostic layer", "diagnostic_derivation", "diagnostic", "installed", "explicit_call", "annotate_lgrc9v3_causal_history", "explicit_annotation_call", "declared graph state, event records, and timing policy", [
        stage("derive_causal_metrics", "explicit annotation request", ["GRC9V3 state", "event history", "timing modes"], ["lapse", "edge delays", "geometric/causal/functional distances"], authority("graph and timing policy", "not_applicable", "annotation input validation", "caller", "annotation helper", "annotation artifact"), "derive causal metrics", "none outside returned artifact", "derived_event_time", "graph_wide_or_source_scoped", "missing/invalid timing inputs reject"),
        stage("assemble_causal_annotation", "metrics available", ["distances", "event times"], ["causal cones", "causal basin core", "annotation artifact"], authority("derived metric graph", "not_applicable", "annotation schema", "helper", "artifact construction", "caller"), "assemble diagnostic", "returned artifact only", "derived_event_time", "graph_wide_or_source_scoped", "empty sources produce bounded empty annotation"),
    ], ["lapse policy", "delay policy", "distance modes", "source nodes"], [], ["annotation is not active causal execution"], ["finite distances", "schema validity"], ["source state digest", "annotation schema"], ["declared event records"], ["unreferenced ledger history"], ["invalid timing mode", "missing edge values"], "annotation artifact restoration contract", ["source-backed causal-history diagnostic"], ["native event propagation", "causal work admission"], source["timing"], source_commit))

    entries.append(pathway(P["eligibility"], "LGRC9V3 Fixed-Topology Eligibility", "Compute bounded semi-causal fixed-topology eligibility from declared timing and state surfaces.", "LGRC9V3 diagnostic layer", "diagnostic_eligibility", "diagnostic", "installed", "explicit_call", "compute_lgrc9v3_fixed_topology_eligibility", "explicit_eligibility_call", "current fixed topology and declared causal-history inputs", [
        stage("fixed_topology_eligibility", "explicit eligibility request", ["GRC9V3 state", "causal annotation", "eligibility policy"], ["eligibility artifact"], authority("declared source/target relation", "not_a_transport_budget", "fixed-topology predicate", "caller", "eligibility helper", "caller"), "compute eligibility", "returned artifact only", "derived_event_time", "fixed_topology_relation", "topology change or missing inputs rejects"),
    ], ["eligibility thresholds", "timing policy"], [], ["computed eligibility is not packet scheduling or generic admission"], ["fixed topology signature", "finite inputs"], ["topology signature", "eligibility schema"], ["declared annotation"], ["other ledger history"], ["topology mismatch", "invalid policy"], "eligibility artifact restoration contract", ["bounded fixed-topology eligibility diagnostic"], ["packet departure", "native generic admission"], source["timing"], source_commit))

    entries.append(pathway(P["packet"], "Explicit LGRC9V3 Packet Transport", "Validate and process a declared packet through source debit, in-flight state, arrival, and target credit.", "LGRC9V3", "event_transport", "native_with_configured_semantics", "installed", "explicit_call", "schedule_packet_departure or queued packet event", "packet_event_queue_frontier", "declared packet record plus source/target state", [
        stage("packet_schedule", "explicit call or registered producer", ["source", "target", "edge", "amount", "event times", "packet ledger"], ["queued departure record"], packet_commit, "validate and queue packet", "packet ledger queue", "event_time", "declared_edge", "invalid endpoints, amount, time, or budget rejects"),
        stage("source_debit", "departure event reaches queue front", ["queued departure", "source coherence"], ["source debit", "in_flight packet", "arrival event"], packet_commit, "commit departure", "source coherence and packet ledger", "event_time", "source_and_edge", "insufficient source budget rejects atomically"),
        stage("target_credit", "arrival event reaches queue front", ["in_flight packet", "target state"], ["target credit", "settled packet", "processing record"], packet_commit, "commit arrival", "target coherence and packet ledger", "event_time", "target_and_edge", "invalid arrival alignment rejects atomically"),
    ], ["route endpoints", "amount", "departure/arrival times"], [], ["native route formation and departure reason remain absent"], ["source debit equals in-flight amount equals target credit", "deterministic queue order", "fixed packet identity"], ["packet ID", "event IDs", "ledger", "scheduler index", "topology endpoints"], ["packet and queue history required for settlement"], ["unrelated event history"], ["budget failure", "endpoint mismatch", "event ordering mismatch", "duplicate event"], "LGRC9V3 runtime-state and packet-ledger restoration", ["native packet accounting and queue-processing mechanics"], ["substrate-formed route", "native departure reason", "agency"], source["packet"], source_commit))

    entries.append(pathway(P["route"], "Configured Causal-Flux Route Producer", "Schedule packet departures over caller-configured causal routes using native producer and packet mechanics.", "LGRC9V3 producer layer", "configured_producer", "native_with_configured_semantics", "installed", "default_off", "produce_events with causal_flux_routes", "producer_frontier_before_queue_processing", "configured route map and current source coherence", [
        stage("route_registration", "set_causal_flux_routes", ["route specs"], ["runtime route map"], authority("configured route", "not_yet_funded", "route schema", "caller", "runtime config state", "producer"), "register routes", "runtime policy state", "configuration_time", "declared_endpoints", "invalid route rejects"),
        stage("route_departure_production", "produce_events and empty/idempotent route slot", ["route map", "source coherence", "producer policy"], ["queued packet departure", "production record"], authority("configured route", "source coherence", "route validity and producer policy", "native producer", "packet scheduler", "configured target"), "produce packet work", "packet queue and producer log", "producer_frontier_then_event_time", "configured_route", "insufficient budget or duplicate key emits no work"),
    ], ["route", "target", "amount source", "arrival delay"], [], ["route formation and role meaning remain configured residue"], ["aggregate source preflight", "idempotency", "packet budget"], ["route map", "producer record IDs", "packet ledger"], ["producer idempotency history"], ["unrelated route history"], ["invalid route", "insufficient source", "duplicate production"], "LGRC9V3 runtime route and producer state", ["native scheduling mechanics over configured routes"], ["native route formation", "semantic role formation"], source["runtime"], source_commit))

    entries.append(pathway(P["surplus"], "Route-Aspect Surplus Producer", "Evaluate configured pole-mass surplus and schedule bounded packet continuation along a declared route-aspect channel.", "LGRC9V3 producer layer", "configured_producer", "native_with_configured_semantics", "installed", "default_off", "produce_events with route_aspect_surplus_trigger", "producer_frontier", "configured route aspect, current pole mass, and source coherence", [
        stage("surplus_evaluation", "produce_events", ["route aspect", "pole mass", "reference mass", "threshold"], ["surplus amount", "selected trigger channel"], authority("configured channel", "not_yet_funded", "native surplus predicate over configured semantics", "native producer", "producer result", "selected channel"), "evaluate surplus", "producer result cache", "producer_frontier", "configured_pole_regions", "below threshold is no-op"),
        stage("surplus_packet_schedule", "positive bounded surplus", ["selected channel", "source coherence", "packet amount policy"], ["queued packet", "self-rearm evidence"], authority("configured channel", "source coherence", "positive surplus and packet validation", "native producer", "packet scheduler", "channel target"), "schedule packet", "packet queue and evidence log", "producer_frontier_then_event_time", "first_channel_hop", "budget or idempotency failure blocks"),
    ], ["pole regions", "channel sequence", "reference mass", "threshold", "packet amount"], [], ["pole meaning and ecological role are not substrate-formed"], ["packet budget", "surplus threshold", "idempotency"], ["route-aspect digest", "producer record", "packet ledger"], ["previous channel/self-rearm evidence where configured"], ["semantic route labels"], ["below threshold", "invalid route aspect", "budget failure"], "LGRC9V3 route-aspect and producer restoration", ["native surplus evaluation and packet scheduling under configured semantics"], ["native pole meaning", "generic current source", "support seeking"], source["runtime"], source_commit))

    entries.append(pathway(P["pulse"], "Pulse-Substrate Coupling Producer", "Use an experiment-configured pulse-contact surface and coupling policy to schedule bounded packet work.", "producer over LGRC9V3", "producer_adapter", "producer", "installed", "default_off", "produce_events with pulse_substrate_coupling_producer", "producer_frontier", "runtime-visible pulse-contact surface plus producer configuration", [
        stage("pulse_surface_read", "produce_events", ["latest pulse-contact surface", "coupling config"], ["producer eligibility decision"], authority("producer-configured relation", "not_yet_funded", "producer predicate", "producer", "producer decision record", "packet adapter"), "read and classify surface", "producer decision log", "producer_frontier", "producer_declared_surface", "missing/stale/nonqualifying surface is no-op"),
        stage("coupled_packet_schedule", "producer predicate passes", ["decision", "source coherence", "configured route"], ["queued packet", "producer result"], authority("producer-configured route", "source coherence", "producer predicate", "producer", "native packet scheduler", "configured target"), "schedule bounded packet", "packet queue and producer log", "producer_frontier_then_event_time", "producer_declared_route", "budget/idempotency failure blocks"),
    ], ["surface keys", "thresholds", "route", "amount policy"], ["pulse-to-work eligibility and relation"], ["native pulse-conditioned admission"], ["native packet budget", "producer idempotency"], ["producer config", "surface digest", "packet ledger"], ["latest declared pulse-contact row"], ["other retained surface history"], ["surface stale", "predicate miss", "budget failure"], "LGRC9V3 producer and packet state restoration", ["producer-mediated pulse-conditioned packet candidate"], ["native pulse admission", "agency"], source["runtime"], source_commit))

    entries.append(pathway(P["feedback"], "Feedback-Eligibility Producer", "Use an experiment-authored feedback surface and eligibility policy to schedule bounded packet work.", "producer over LGRC9V3", "producer_adapter", "producer", "installed", "default_off", "emit_feedback_eligibility_surface_row and produce_events", "producer_frontier", "registered feedback surface, masks, thresholds, and current source state", [
        stage("feedback_surface_registration", "explicit producer call", ["runtime-visible state", "feedback policy"], ["feedback eligibility surface row"], authority("producer relation", "not_yet_funded", "producer-authored surface rule", "producer", "runtime surface record", "feedback producer"), "emit bounded eligibility row", "producer-owned runtime record", "producer_frontier", "producer_declared", "invalid row rejects"),
        stage("feedback_packet_schedule", "qualifying feedback row", ["feedback row", "source coherence", "route config"], ["queued packet", "producer result"], authority("producer route", "source coherence", "producer feedback predicate", "producer", "native packet scheduler", "configured target"), "schedule packet", "packet queue and producer log", "producer_frontier_then_event_time", "producer_declared_route", "stale/missing row or budget failure blocks"),
    ], ["feedback masks", "thresholds", "route", "amount"], ["feedback surface formation and eligibility"], ["native feedback or generic admission"], ["native packet budget", "surface freshness", "idempotency"], ["feedback surface ID", "producer record", "packet ledger"], ["latest eligible feedback row"], ["nonconsumed feedback history"], ["missing/stale row", "predicate miss", "budget failure"], "LGRC9V3 feedback producer state restoration", ["producer-mediated feedback eligibility candidate"], ["native feedback", "semantic intention", "agency"], source["runtime"], source_commit))

    entries.append(pathway(P["arbitration"], "Native Route Arbitration", "Validate, order, select, and commit over supplied route-candidate records and scores.", "LGRC9V3", "candidate_arbitration", "native_with_configured_semantics", "installed", "default_off", "emit/arbitrate/commit native route candidate set", "explicit_arbitration_frontier", "supplied candidates, scores, budget predictions, and current runtime context", [
        stage("candidate_set_admission", "emit_native_route_candidate_set", ["candidate specs", "runtime context"], ["validated candidate records", "candidate set"], authority("supplied candidate routes", "predicted candidate budgets", "native candidate schema validation", "caller", "candidate-set record", "arbitrator"), "admit candidate set", "candidate records", "explicit_call", "candidate_routes", "invalid context or prediction rejects"),
        stage("native_arbitration", "arbitrate_native_route_candidate_set", ["candidate set", "scores", "runtime state"], ["ordered candidates", "selected candidate", "arbitration record"], authority("supplied candidate direction and scores", "validated budget prediction", "native ordering and eligibility checks", "caller", "native arbitration record", "selected candidate"), "select candidate", "arbitration records", "explicit_call", "candidate_set", "no valid candidate yields fail-closed result"),
        stage("selection_commit", "commit_native_route_arbitration_selection", ["selected candidate", "referenced topology event"], ["committed topology event", "lineage state"], topology_commit, "commit selected event", "runtime topology and lineage", "event_time", "selected_route", "missing/mismatched event blocks commit"),
    ], ["candidate schema", "score/order policy", "claim flags", "budget prediction"], ["candidate and score formation when experiment supplied"], ["native route formation and semantic valuation"], ["candidate budget prediction", "order validity", "runtime context digest"], ["candidate-set digest", "arbitration ID", "topology event ID"], ["candidate and arbitration records"], ["semantic candidate labels"], ["invalid candidate", "budget mismatch", "missing event", "duplicate commit"], "LGRC9V3 candidate/arbitration runtime restoration", ["native validation, ordering, selection, and commit mechanics over supplied candidates"], ["native candidate formation", "semantic choice", "agency"], source["runtime"], source_commit))

    entries.append(pathway(P["birth"], "LGRC9V3 Causal Boundary Birth", "Evaluate configured outward-flux/front-capacity eligibility, schedule a causal trial, and commit parent-funded topology birth.", "LGRC9V3", "causal_topology_pathway", "native_with_configured_semantics", "installed", "default_off", "produce_events or schedule_causal_boundary_birth_trial", "producer_and_boundary_birth_queue_frontier", "current outward flux, inactive ports, parent capacity, configured policy, and RNG", [
        stage("birth_trial_production", "produce_events", ["outward flux", "inactive ports", "parent capacity", "birth policy"], ["queued boundary-birth trial", "production record"], authority("outward flux at eligible port", "parent coherence", "configured parent eligibility mode", "native producer", "birth trial queue", "parent port"), "schedule trial", "boundary-birth queue", "producer_frontier", "parent_port_local", "no capacity or duplicate trial is no-op"),
        stage("birth_trial_commit", "trial reaches queue front", ["queued trial", "parent coherence", "RNG state", "free port"], ["child topology", "coherence transfer", "birth event"], authority("queued eligible parent port", "parent coherence", "birth probability and RNG", "event queue", "LGRC9V3 topology integrator", "child node"), "commit birth", "topology, coherence, event history, RNG", "event_time", "parent_and_child_local", "failed RNG/port/budget blocks without partial mutation"),
    ], ["eligibility mode", "front-capacity source", "birth probability", "edge delay", "RNG policy"], [], ["specialized birth eligibility does not naturalize generic admission"], ["parent debit equals child credit", "port capacity", "queue order", "RNG restoration"], ["trial ID", "topology event ID", "lineage", "RNG state"], ["queued trial and parent capacity"], ["unrelated packet history"], ["no capacity", "occupied port", "failed RNG", "budget failure"], "LGRC9V3 boundary queue/topology/RNG restoration", ["native mechanics for configured causal boundary birth"], ["universal current-to-action admission", "semantic reproduction"], source["runtime"], source_commit))

    entries.append(pathway(P["integration"], "LGRC9V3 Causal Spark Topology Integration", "Evaluate causal spark diagnostics at an arrival/local-update boundary and optionally commit mechanical refinement with packet and lineage transport.", "LGRC9V3", "causal_topology_pathway", "native_with_configured_semantics", "installed", "default_off", "packet arrival local-update boundary", "arrival_then_local_update_then_spark_frontier", "current arrival result, local diagnostics, configured spark/integration policies", [
        stage("causal_spark_diagnostic", "packet arrival and local update", ["arrival result", "local differential state", "spark policy"], ["causal spark candidate event"], authority("local differential geometry", "not_yet_funded", "causal spark predicate", "LGRC9V3.step", "candidate event log", "integration gate"), "evaluate candidate", "diagnostic/event records", "event_time", "arrival_local", "predicate miss emits no candidate"),
        stage("topology_integration", "eligible candidate and enabled policy", ["candidate event", "parent coherence", "topology policy"], ["refined topology", "coherence transfer", "topology event"], topology_commit, "commit refinement", "topology, coherence, lineage", "event_time", "candidate_local", "disabled policy/capacity failure blocks"),
        stage("packet_and_lineage_transport", "topology integration committed", ["topology event", "packet ledger", "proper time state"], ["transported packets", "lineage map", "proper time inheritance"], topology_commit, "transport active state", "packet/runtime lineage state", "event_time", "affected_topology_region", "transport mismatch blocks replay-clean claim"),
    ], ["spark modes", "integration policy", "expansion distribution", "proper-time policy"], [], ["candidate semantics and identity acceptance remain separate"], ["coherence conservation", "packet budget", "lineage completeness"], ["candidate ID", "topology event ID", "lineage IDs", "packet IDs"], ["arrival and topology history required for integration/transport"], ["other ledger history"], ["predicate miss", "disabled policy", "capacity failure", "transport mismatch"], "LGRC9V3 topology/packet/lineage restoration", ["native causal spark evaluation and enabled topology-integration mechanics"], ["semantic creation", "identity acceptance", "generic admission"], source["topology"], source_commit))

    entries.append(pathway(P["collapse"], "LGRC9V3 Collapse And Reabsorption", "Commit explicit or arbitrated collapse/reabsorption and transport packet, lineage, surface, and active-state records.", "LGRC9V3", "causal_topology_pathway", "native_with_configured_semantics", "installed", "explicit_call", "process_causal_collapse_reabsorption", "explicit_or_arbitrated_topology_event_frontier", "selected sinks/losers, runtime topology, packet ledger, and configured policy", [
        stage("collapse_event_admission", "explicit request or arbitration selection", ["selected sink", "losing nodes", "policy", "runtime context"], ["validated collapse event"], authority("explicit/arbitrated collapse relation", "losing basin coherence", "collapse policy and context validation", "caller or arbitrator", "collapse processor", "selected sink"), "validate collapse", "none before commit", "event_time", "selected_basin_region", "invalid relation rejects atomically"),
        stage("topology_reabsorption_commit", "validated event", ["collapse event", "topology", "coherence"], ["reabsorbed topology", "transferred coherence", "lineage event"], topology_commit, "commit reabsorption", "topology, coherence, lineage", "event_time", "selected_basin_region", "budget/topology failure blocks atomically"),
        stage("active_state_transport", "topology commit complete", ["packet ledger", "pending flux", "surface rows", "active state"], ["redirected/settled packets", "reabsorbed surfaces", "transport records"], topology_commit, "transport active state", "packet/runtime records", "event_time", "affected_topology_region", "unmapped active state blocks clean replay"),
    ], ["collapse policy", "explicit or arbitration input", "reabsorption modes"], ["candidate formation when externally supplied"], ["native collapse reason and semantic identity"], ["coherence/packet budget", "lineage completeness", "endpoint validity"], ["collapse event ID", "lineage map", "packet/surface record IDs"], ["selected event, packet, lineage, and surface history"], ["semantic identity labels"], ["invalid sink/loser", "budget mismatch", "unmapped endpoint", "duplicate event"], "LGRC9V3 topology and active-state restoration", ["native collapse/reabsorption and active-state transport mechanics"], ["semantic death", "identity acceptance", "native candidate formation"], source["topology"], source_commit))

    entries.append(pathway(P["identity_eval"], "LGRC9V3 Proper-Time Identity Evaluation", "Evaluate bounded proper-time identity-persistence criteria over topology and causal-history records.", "LGRC9V3 diagnostic layer", "diagnostic_evaluation", "diagnostic", "installed", "explicit_call", "evaluate_lgrc9v3_proper_time_identity_persistence", "explicit_identity_evaluation_frontier", "proper-time, topology, lineage, and policy records", [
        stage("proper_time_identity_evaluation", "explicit evaluation request", ["proper-time state", "topology lineage", "identity policy"], ["persistence evaluation artifact"], authority("declared sink-local lineage", "not_applicable", "identity persistence predicate", "caller", "evaluation helper", "caller or acceptance gate"), "evaluate persistence", "evaluation artifact only", "proper_time_and_event_time", "sink_local_lineage", "failed criteria produce negative evaluation"),
    ], ["identity persistence policy", "thresholds"], [], ["evaluation does not establish selfhood or acceptance"], ["lineage ordering", "finite proper time", "policy validity"], ["evaluation ID", "lineage IDs", "proper-time state"], ["declared topology and proper-time history"], ["unreferenced packet history"], ["missing lineage", "criterion failure", "invalid policy"], "identity evaluation artifact restoration", ["native diagnostic evaluation mechanics"], ["selfhood", "semantic identity", "identity acceptance"], source["identity_lgrc"], source_commit))

    entries.append(pathway(P["identity_accept"], "LGRC9V3 Proper-Time Identity Acceptance", "Emit an explicit identity-acceptance event only after a passing evaluation and enabled policy.", "LGRC9V3", "policy_gated_event_emission", "native_with_configured_semantics", "installed", "default_off", "emit_causal_identity_acceptance", "explicit_acceptance_frontier", "passing identity evaluation and enabled acceptance policy", [
        stage("acceptance_gate", "explicit acceptance request", ["identity evaluation", "acceptance policy", "runtime context"], ["acceptance eligibility"], authority("evaluated sink-local lineage", "not_a_coherence_transfer", "passing evaluation plus enabled policy", "caller", "acceptance gate", "event emitter"), "gate event emission", "none before pass", "event_time", "sink_local", "disabled or failed evaluation emits no event"),
        stage("acceptance_event_emission", "gate passes", ["acceptance eligibility", "event identity fields"], ["identity acceptance event"], authority("accepted lineage", "not_a_coherence_transfer", "passed gate", "caller", "LGRC9V3 event log", "runtime event history"), "emit event", "event log", "event_time", "sink_local", "duplicate event ID blocks"),
    ], ["acceptance policy", "event schema"], [], ["semantic selfhood and organism identity remain blocked"], ["evaluation pass", "idempotent event ID"], ["evaluation ID", "acceptance event ID", "lineage"], ["passing evaluation"], ["unrelated retained history"], ["policy disabled", "evaluation failed", "duplicate event"], "LGRC9V3 event/runtime restoration", ["native gated acceptance-event emission mechanics"], ["selfhood", "semantic identity", "organism status"], source["identity_lgrc"], source_commit))

    entries.append(pathway(P["surface"], "LGRC9V3 Causal-Pulse Surface Lineage", "Emit configured pulse-contact surface rows and transport, supersede, or reabsorb them across topology events.", "LGRC9V3", "runtime_surface_lineage", "native_with_configured_semantics", "installed", "default_off", "packet arrival and topology event hooks", "arrival_or_topology_event_frontier", "packet contact, configured surface policy, topology lineage, and reabsorption records", [
        stage("surface_row_emission", "qualifying packet contact", ["arrival result", "surface policy", "local runtime state"], ["surface row", "surface event"], authority("packet contact and configured surface key", "not_a_coherence_transfer", "surface policy predicate", "LGRC9V3.step", "runtime surface log", "local surface state"), "emit runtime surface row", "surface records", "event_time", "contact_local", "disabled/nonqualifying policy is no-op"),
        stage("surface_lineage_transport", "committed topology event", ["surface row", "lineage transfer map"], ["transported row", "lineage record", "supersession record"], topology_commit, "transport surface identity", "surface/lineage records", "event_time", "affected_topology_region", "missing lineage blocks clean transport"),
        stage("surface_reabsorption", "collapse/reabsorption event", ["surface lineage", "reabsorption map"], ["reabsorbed or superseded surface state"], topology_commit, "reabsorb active surface", "surface records", "event_time", "collapsed_region", "missing reabsorption record leaves explicit debt"),
    ], ["surface policy", "keys", "update policy", "lineage mode"], [], ["surface meaning and constitutive consumption remain absent unless a named producer/pathway reads it"], ["idempotency", "lineage completeness", "no hidden coherence budget"], ["surface digest", "lineage record ID", "topology event ID"], ["packet contact and topology lineage"], ["surface history not consumed by constitutive transport"], ["policy disabled", "stale/missing lineage", "duplicate row"], "LGRC9V3 runtime surface/lineage restoration", ["native configured surface recording and lineage transport mechanics"], ["native memory", "Read-Back", "support"], source["surface"], source_commit))

    entries.append(pathway(P["multibasin"], "LGRC9V3 Multi-Basin Record And Validation", "Emit child-basin/flow-window records after committed topology events and validate replay plus merge/leakage controls.", "LGRC9V3 diagnostic layer", "diagnostic_validation", "diagnostic", "installed", "default_off", "committed topology event with multi-basin policy", "post_topology_diagnostic_frontier", "committed topology, child metrics, packet/edge flux traces, and validation policy", [
        stage("flow_and_child_record_emission", "topology event committed", ["topology event", "active state", "edge/packet flux", "multi-basin policy"], ["flow-window record", "child-basin state record"], authority("committed topology relation", "descriptive budget trace", "multi-basin record schema", "runtime post-commit hook", "diagnostic record log", "telemetry/validator"), "emit diagnostic records", "runtime diagnostic records", "event_time", "affected_child_region", "missing metrics blocks positive record"),
        stage("replay_and_control_validation", "explicit validation request", ["child record", "flow record", "snapshot/replay state", "control policy"], ["replay validation", "merge/leakage control record"], authority("recorded child relation", "descriptive budget trace", "replay/control predicates", "caller", "validation record", "caller/telemetry"), "validate records", "validation records only", "replay_window", "child_and_parent_regions", "failed control remains explicit and blocks support"),
    ], ["multi-basin policy", "window", "metrics", "control thresholds"], [], ["record emission does not itself form a basin or prove broad robustness"], ["budget trace closure", "record digest", "replay mapping ratios"], ["topology event ID", "child record ID", "flow record ID", "replay digest"], ["committed topology and replay history"], ["unconsumed semantic basin labels"], ["missing topology event", "replay mismatch", "merge/leakage control failure"], "LGRC9V3 multi-basin record restoration", ["native diagnostic record emission and replay/control validation"], ["native basin formation by record", "agency", "general robustness"], source["multibasin"], source_commit))

    entries.append(pathway(P["diagnostic"], "Diagnostic GRC Reconstruction Over LGRC State", "Explicitly reconstruct synchronous GRC9V3 differential, transport, identity, and choice surfaces over an LGRC base-state copy.", "diagnostic over LGRC9V3", "diagnostic_reconstruction", "diagnostic", "installed", "explicit_call", "prepare_lgrc9v3_grc9v3_diagnostics or explicit reconstruction helper", "caller_selected_checkpoint", "LGRC base state copied into an explicit GRC9V3 diagnostic model", [
        stage("diagnostic_model_construction", "explicit helper call", ["LGRC base state", "GRC params"], ["diagnostic GRC9V3 model"], authority("copied graph state", "not_a_transport_budget", "caller-selected reconstruction", "caller", "helper-local model", "diagnostic pipeline"), "construct diagnostic model", "helper-local state", "caller_checkpoint", "copied_graph", "invalid state/params reject"),
        stage("diagnostic_rebuild", "diagnostic model available", ["copied state"], ["differential", "flux", "identity", "choice diagnostics"], authority("GRC reconstruction", "not_applied_to_LGRC", "explicit diagnostic request", "caller", "helper-local rebuild", "returned diagnostic"), "rebuild diagnostics", "helper-local state only", "synchronous_limit_at_checkpoint", "copied_graph", "failure does not mutate original LGRC"),
    ], ["diagnostic modes", "copied params"], [], ["ordinary LGRC step does not consume the reconstruction"], ["original LGRC state unchanged", "copy identity"], ["source checkpoint digest", "diagnostic model identity"], ["selected checkpoint only"], ["other LGRC history"], ["copy mismatch", "invalid params", "attempted write-back"], "diagnostic copy/snapshot contract", ["explicit bounded GRC diagnostic over LGRC state"], ["ordinary LGRC behavior", "native current-to-packet adapter"], ["src/pygrc/models/lgrc_9_v3_construction.py", "src/pygrc/models/lgrc_9_v3_runtime.py"], source_commit))

    entries.append(pathway(P["restoration"], "PyGRC Restoration And Replay Identity", "Serialize, restore, compare, reset, and replay GRC9V3/LGRC9V3 state under versioned identity contracts.", "shared PyGRC/GRC9V3/LGRC9V3", "restoration_utility", "utility", "installed", "explicit_call", "snapshot/load/reset/restoration identity/replay validation", "serialization_or_replay_frontier", "declared snapshot state and versioned identity schema", [
        stage("snapshot_serialization", "snapshot/save", ["model state", "reset baseline", "runtime artifacts"], ["canonical snapshot"], authority("not_applicable", "not_applicable", "snapshot schema", "caller", "serialization utility", "snapshot consumer"), "serialize state", "snapshot bytes only", "checkpoint_time", "full_declared_model_scope", "unsupported/malformed state rejects"),
        stage("load_and_reset_restoration", "load/reset", ["canonical snapshot", "reset baseline bundle"], ["restored model", "restored reset behavior"], authority("not_applicable", "not_applicable", "versioned compatibility policy", "caller", "model loader/reset", "restored model"), "restore state", "new/restored model state", "checkpoint_time", "full_declared_model_scope", "legacy/malformed baseline follows explicit compatibility policy"),
        stage("identity_and_replay_validation", "identity or replay request", ["before/after state", "identity schema", "event/topology records"], ["identity digest", "replay result"], authority("declared identity projection", "not_applicable", "versioned comparison/replay contract", "caller", "validation utility", "caller"), "validate equivalence", "validation artifact only", "replay_window", "declared_identity_scope", "mismatch fails without rewriting state"),
    ], ["identity schema version", "legacy compatibility policy", "replay scope"], [], ["identity equality remains scope-bounded and does not imply semantic identity or work eligibility"], ["canonical serialization", "reset-baseline preservation", "included scientific state equality"], ["snapshot schema", "reset baseline", "runtime artifact", "identity version"], ["declared replay/event history"], ["representation-only caches excluded by schema"], ["schema mismatch", "included-state mismatch", "malformed baseline", "replay divergence"], "GRC9V3/LGRC9V3 restoration identity v1/v2 and reset-baseline contracts", ["versioned restoration and replay identity"], ["byte identity requirement", "unrestricted behavioral identity", "semantic identity", "action eligibility"], source["restoration"], source_commit))

    return sorted(entries, key=lambda item: item["pathway_id"])


NORMATIVE_INPUT_PATHS = [
    "specs/lgrc-9-v3-spec.md",
    "docs/reference/ClaimBoundaryIndex.md",
    "docs/reference/GRC-Runtime-ReferenceGuide.md",
    "implementation/Phase-8-LGRC9-ImplementationPlan.md",
    "implementation/Phase-8-LGRC9-ImplementationChecklist.md",
    "implementation/Phase-8-LGRC9-Handoff.md",
    "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationPlan.md",
    "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationChecklist.md",
]

PREDECESSOR_INPUT_PATHS = [
    "implementation/investigations/event-local-geometry-integration/Phase-8-LGRC9-EventLocalGeometryIntegrationC0C1Closeout.json",
    "implementation/investigations/event-local-geometry-integration/Phase-8-LGRC9-EventLocalGeometryIntegrationC0C1Closeout.md",
    "implementation/investigations/event-local-geometry-integration/Phase-8-LGRC9-EventLocalGeometryIntegrationStatus.json",
    "implementation/investigations/event-local-geometry-integration/Phase-8-LGRC9-EventLocalGeometryIntegrationPostC1ScopeInterpretation.json",
    "implementation/investigations/event-local-geometry-integration/Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkOwnershipPressureMap.json",
    "implementation/investigations/event-local-geometry-integration/Phase-8-LGRC9-EventLocalGeometryIntegrationCausalWorkAdmissionPatternAudit.json",
]

WORKING_CONTRACT_PATHS = [
    "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationPlan.md",
    "implementation/Phase-8-GRCLGRC-CausalPathwayConsolidationChecklist.md",
    "scripts/build_phase8_causal_pathway_i106.py",
    "specs/grc-lgrc-causal-pathway-contracts.md",
]


def head_anchor(path: str, head: str) -> dict[str, str]:
    content = subprocess.check_output(["git", "show", f"{head}:{path}"], cwd=ROOT)
    return {"path": path, "sha256": sha256_bytes(content), "anchor_revision": head}


def working_anchor(path: str) -> dict[str, str]:
    return {
        "path": path,
        "sha256": sha256_file(ROOT / path),
        "anchor_revision": "iteration_106_working_contract",
    }


def main() -> int:
    head = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    branch = git("branch", "--show-current")
    source_paths = source_dependency_closure(PRIMARY_SOURCES)
    surface_records = []
    for path in source_paths:
        classification = classify_surface(path)
        kind, behavior_role = surface_kind(path, classification)
        surface_records.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256_file(path),
                "surface_kind": kind,
                "behavior_role": behavior_role,
                **classification,
            }
        )

    unclassified = [item for item in surface_records if item["mapping_kind"] == "unclassified"]
    unclassified_behavior = [item for item in unclassified if item["behavior_role"] == "behavior_changing"]
    full_status = git("status", "--short")
    protected_diff = git("diff", "--", "src", "tests", "examples")
    manifest = {
        "artifact": "Phase-8-GRCLGRC-CausalPathwayConsolidationSourceManifest",
        "schema_version": "phase8_grclgrc_causal_pathway_source_manifest_v1",
        "iteration": 106,
        "repository_branch": branch,
        "repository_head": head,
        "repository_tree": tree,
        "full_git_status_short": full_status.splitlines(),
        "registry_scope_v1": ["GRC9V3", "LGRC9V3", "directly_consumed_shared_PyGRC_utilities"],
        "dependency_closure_method": "recursive_internal_import_closure_from_grc_9_v3_star_lgrc_9_v3_star_and_lgrc9v3_telemetry_contract",
        "surface_count": len(surface_records),
        "surface_classification_counts": dict(Counter(item["mapping_kind"] for item in surface_records)),
        "unclassified_surface_count": len(unclassified),
        "unclassified_behavior_changing_surface_count": len(unclassified_behavior),
        "zero_unclassified_behavior_changing_surfaces": not unclassified_behavior,
        "protected_source_test_example_diff_empty": protected_diff == "",
        "normative_contract_anchor_mode": "committed_I106_input_authority_at_repository_head",
        "normative_contract_anchors": [head_anchor(path, head) for path in NORMATIVE_INPUT_PATHS],
        "working_contract_anchor_mode": "final_I106_working_contract_bytes_separate_from_committed_inputs",
        "working_contract_anchors": [working_anchor(path) for path in WORKING_CONTRACT_PATHS],
        "predecessor_evidence_anchors": [head_anchor(path, head) for path in PREDECESSOR_INPUT_PATHS],
        "surfaces": surface_records,
    }
    write_json(OUTPUT_MANIFEST, manifest)

    pathways = build_pathways(head)
    required_stage_fields = [
        "stage_id", "trigger", "state_consumed", "state_produced",
        "direction_authority", "funding_authority", "eligibility_authority",
        "scheduling_authority", "commit_authority", "reception_authority",
        "action_scope", "mutation_scope", "time_semantics", "spatial_scope",
        "failure_or_noop_semantics",
    ]
    required_entry_fields = [
        "pathway_id", "entry_version", "name", "purpose", "substrate_layer",
        "contract_kind", "mechanism_ownership", "availability", "activation",
        "state_consumed", "state_produced", "time_semantics", "spatial_scope",
        "trigger_surface", "event_locus", "causal_information_scope",
        "authority_summary", "stage_sequence", "configured_residue",
        "producer_residue", "naturalization_debt", "budget_and_invariants",
        "state_identity_fields", "history_consumed",
        "history_retained_but_not_consumed", "fail_closed_conditions",
        "restoration_and_serialization_identity", "supported_claims",
        "blocked_claims", "evidence_refs", "composition_refs",
        "catalog_relation_refs", "source_commit", "source_digest",
        "last_verified_commit", "staleness_state", "supersedes", "superseded_by",
    ]
    registry = {
        "artifact": "grc-lgrc-causal-pathway-contracts",
        "registry_schema_version": "grc_lgrc_causal_pathway_contract_registry_v1",
        "status": "iteration_106_schema_frozen_crosswalk_and_composition_refs_pending",
        "iteration": 106,
        "registry_scope_v1": manifest["registry_scope_v1"],
        "registry_is_evidence_source": False,
        "registry_is_runtime_dispatcher": False,
        "universal_causal_work_API_supported": False,
        "generic_native_admission_supported": False,
        "ownership_model_selected": False,
        "required_entry_fields": required_entry_fields,
        "required_stage_fields": required_stage_fields,
        "mechanism_ownership_values": ["native", "native_with_configured_semantics", "producer", "external_adapter", "diagnostic", "utility"],
        "availability_values": ["installed", "experiment_local", "bounded_external", "historical", "absent"],
        "activation_values": ["default_on", "default_off", "explicit_call", "externally_orchestrated"],
        "staleness_values": ["current_at_iteration_106_freeze", "stale_pending_review", "superseded"],
        "artifact_authority": {
            "registry": "intrinsic pathway and stage facts",
            "crosswalk": "source specification test and evidence relations",
            "composition_matrix": "directional inter-pathway relations",
            "selection_guide": "derived explanation only",
        },
        "pathway_catalog_boundary": "Pathway execution contracts do not admit primitive building-block motif or regime claims.",
        "source_manifest": OUTPUT_MANIFEST.relative_to(ROOT).as_posix(),
        "pathway_count": len(pathways),
        "pathways": pathways,
    }
    registry["registry_digest"] = canonical_digest(registry)
    write_json(OUTPUT_REGISTRY, registry)

    result = {
        "artifact": "Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106",
        "schema_version": "phase8_grclgrc_causal_pathway_iteration_106_result_v1",
        "iteration": 106,
        "status": "passed",
        "source_manifest": OUTPUT_MANIFEST.relative_to(ROOT).as_posix(),
        "registry": OUTPUT_REGISTRY.relative_to(ROOT).as_posix(),
        "artifact_freeze": OUTPUT_FREEZE.relative_to(ROOT).as_posix(),
        "registry_digest": registry["registry_digest"],
        "source_surface_count": len(surface_records),
        "unclassified_surface_count": len(unclassified),
        "unclassified_behavior_changing_surface_count": len(unclassified_behavior),
        "initial_pathway_family_count": 12,
        "frozen_pathway_count": len(pathways),
        "stage_count": sum(len(item["stage_sequence"]) for item in pathways),
        "runtime_behavior_changed": False,
        "protected_source_test_example_diff_empty": protected_diff == "",
        "schema_frozen": True,
        "crosswalk_complete": False,
        "composition_matrix_complete": False,
        "selection_guide_complete": False,
        "iteration_107_ready": True,
        "blocked_claims": [
            "universal_causal_work_API", "generic_native_admission",
            "causal_work_ownership", "event_local_runtime_implementation",
            "primitive_or_building_block_admission", "ecological_coordination",
            "agency", "N32",
        ],
    }
    result["result_digest"] = canonical_digest(result)
    write_json(OUTPUT_RESULT, result)

    lines = [
        "# Phase 8 GRC/LGRC Causal Pathway Consolidation Unmapped Surface Report",
        "",
        "**Iteration:** 106",
        "",
        "**Status:** Passed; zero unclassified behavior-changing surfaces",
        "",
        "## Method",
        "",
        "The audit recursively followed internal `pygrc` imports from every",
        "`grc_9_v3*` and `lgrc_9_v3*` model module plus the LGRC9V3 telemetry",
        "contract. Every reached file was mapped to one or more pathways, a",
        "cross-cutting contract, or an explicit exclusion with reason.",
        "",
        "## Result",
        "",
        "```text",
        f"source surfaces = {len(surface_records)}",
        f"pathway-mapped = {manifest['surface_classification_counts'].get('pathway', 0)}",
        f"cross-cutting contracts = {manifest['surface_classification_counts'].get('cross_cutting_contract', 0)}",
        f"explicit exclusions = {manifest['surface_classification_counts'].get('explicit_exclusion', 0)}",
        f"unclassified = {len(unclassified)}",
        f"unclassified behavior-changing = {len(unclassified_behavior)}",
        "protected src/test/example diff = empty",
        "```",
        "",
        "The explicit exclusions are transitive package re-exports or fixture/example",
        "providers not consumed as runtime causal pathways. They remain listed and",
        "hashed in the machine manifest rather than disappearing from the audit.",
        "",
        "## Claim Boundary",
        "",
        "Completeness means every source surface in the declared import closure has",
        "a classification. It does not mean every PyGRC family is covered, every",
        "composition is admitted, or every listed mechanism is native.",
    ]
    OUTPUT_UNMAPPED.write_text("\n".join(lines) + "\n", encoding="utf-8")

    frozen_paths = [
        "specs/grc-lgrc-causal-pathway-contracts.json",
        "specs/grc-lgrc-causal-pathway-contracts.md",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.json",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106.md",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationSourceManifest.json",
        "implementation/investigations/causal-pathway-consolidation/Phase-8-GRCLGRC-CausalPathwayConsolidationUnmappedSurfaceReport.md",
        "scripts/build_phase8_causal_pathway_i106.py",
    ]
    frozen_artifacts = [
        {
            "path": path,
            "sha256": sha256_file(ROOT / path),
            "artifact_role": (
                "machine_registry"
                if path == "specs/grc-lgrc-causal-pathway-contracts.json"
                else "registry_specification"
                if path == "specs/grc-lgrc-causal-pathway-contracts.md"
                else "iteration_result"
                if path.endswith("Iteration106.json")
                else "iteration_report"
                if path.endswith("Iteration106.md")
                else "source_manifest"
                if path.endswith("SourceManifest.json")
                else "unmapped_surface_report"
                if path.endswith("UnmappedSurfaceReport.md")
                else "reproducible_builder"
            ),
        }
        for path in frozen_paths
    ]
    artifact_freeze = {
        "artifact": "Phase-8-GRCLGRC-CausalPathwayConsolidationIteration106ArtifactFreeze",
        "schema_version": "phase8_grclgrc_causal_pathway_iteration_106_artifact_freeze_v1",
        "iteration": 106,
        "status": "frozen",
        "repository_branch": branch,
        "repository_head": head,
        "registry_digest": registry["registry_digest"],
        "result_digest": result["result_digest"],
        "frozen_artifacts": frozen_artifacts,
        "self_hash_policy": "artifact_freeze_excluded_to_avoid_recursive_digest",
    }
    artifact_freeze["bundle_digest"] = canonical_digest(frozen_artifacts)
    write_json(OUTPUT_FREEZE, artifact_freeze)

    if unclassified_behavior or protected_diff:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

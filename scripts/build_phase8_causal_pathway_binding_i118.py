#!/usr/bin/env python3
"""Build and verify the I118 pre-refactor compatibility freeze."""

from __future__ import annotations

import argparse
import ast
import dataclasses
import hashlib
import importlib.util
import inspect
import json
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any

import pygrc.causal_pathways as public_api
import pygrc.causal_pathways.binding as binding_api
from pygrc.causal_pathways import (
    CausalPathwayAuthority,
    PathwayBindingSession,
    canonical_digest,
    sha256_file,
    unbound_execution_classification,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "implementation/evidence/causal-pathway-binding/i118"
CORPUS_DIR = EVIDENCE_DIR / "corpus"
PUBLIC_API_FREEZE_PATH = EVIDENCE_DIR / "I118PublicAPICompatibilityFreeze.json"
ARTIFACT_RUNTIME_FREEZE_PATH = EVIDENCE_DIR / "I118ArtifactRuntimeFreeze.json"
CHECKER_FREEZE_PATH = EVIDENCE_DIR / "I118CheckerIndependenceFreeze.json"
BASELINE_EXECUTION_PATH = EVIDENCE_DIR / "I118BaselineExecution.json"
I116_BUILDER_PATH = ROOT / "scripts/build_phase8_causal_pathway_binding_i116.py"
CHECKER_PATH = ROOT / "scripts/check_grc_lgrc_causal_pathway_binding_conformance.py"
ACCEPTANCE_ANCHOR_PATH = (
    ROOT / "implementation/evidence/causal-pathway-binding/"
    "binding-acceptance-anchor.json"
)
TRUSTED_ACCEPTANCE_ANCHOR_DIGEST = (
    "127382ebd0b8f70a5990971190bec5de614f39f03b47c7ffaffe4f53e5970ae2"
)
CMP05_EVIDENCE_PATH = Path(
    "tests/fixtures/causal_pathway_candidate_cmp05_distinct_mechanism_evidence.json"
)

I116_CASES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "01-simple-native-pathway",
        "_simple_native",
        ("native_pathway",),
    ),
    (
        "02-producer-mediated-cmp20",
        "_cmp20",
        ("producer_composition",),
    ),
    (
        "03-explicit-adapter-cmp26",
        "_cmp26",
        ("adapter_composition",),
    ),
    (
        "04-diagnostic-only-cmp04",
        "_diagnostic",
        ("diagnostic_composition", "non_qualifying_returned_effect"),
    ),
    (
        "05-ambiguous-crossing-not-selected",
        "_ambiguous",
        ("unused_declaration", "ambiguous_crossing"),
    ),
    (
        "08-unregistered-candidate",
        "_candidate",
        ("candidate_composition",),
    ),
    (
        "09-dynamic-a-b-choice",
        "_dynamic",
        ("dynamic_choice", "unused_declaration"),
    ),
    (
        "10-multi-edge-use-graph",
        "_multi_edge",
        ("multi_edge_graph",),
    ),
)

ADDITIONAL_CASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "11-reviewed-invalid-pair-candidate",
        ("reviewed_invalid_pair_candidate", "candidate_composition"),
    ),
    (
        "12-unused-candidate-pathway",
        ("candidate_pathway", "unused_declaration"),
    ),
    (
        "13-non-qualifying-returned-effect",
        ("non_qualifying_returned_effect",),
    ),
    (
        "14-raised-effect",
        ("raised_effect",),
    ),
)

SPECIAL_METHODS = {"__call__", "__enter__", "__exit__", "__init__"}


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _record_digest(value: Mapping[str, Any], *, excluding: str) -> str:
    payload = {key: item for key, item in value.items() if key != excluding}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return _sha256_bytes(encoded)


def _git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments],
        cwd=ROOT,
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()


def _load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def _accepted_authority() -> CausalPathwayAuthority:
    return CausalPathwayAuthority.load(
        ROOT,
        acceptance_anchor=_load_json(ACCEPTANCE_ANCHOR_PATH),
        trusted_anchor_digest=TRUSTED_ACCEPTANCE_ANCHOR_DIGEST,
    )


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Mapping):
        return {
            str(key): _json_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, tuple):
        return {"python_type": "tuple", "items": [_json_value(item) for item in value]}
    if isinstance(value, frozenset):
        return {
            "python_type": "frozenset",
            "items": sorted((_json_value(item) for item in value), key=repr),
        }
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    raise TypeError(f"unsupported public constant type: {type(value).__name__}")


def _signature(value: Callable[..., Any] | type[Any]) -> str | None:
    try:
        return str(inspect.signature(value))
    except (TypeError, ValueError):
        return None


def _class_members(value: type[Any]) -> list[dict[str, Any]]:
    members: list[dict[str, Any]] = []
    for name, descriptor in sorted(value.__dict__.items()):
        if name.startswith("_") and name not in SPECIAL_METHODS:
            continue
        if isinstance(descriptor, classmethod):
            members.append(
                {
                    "name": name,
                    "kind": "classmethod",
                    "signature": _signature(descriptor.__func__),
                }
            )
        elif isinstance(descriptor, staticmethod):
            members.append(
                {
                    "name": name,
                    "kind": "staticmethod",
                    "signature": _signature(descriptor.__func__),
                }
            )
        elif isinstance(descriptor, property):
            members.append(
                {
                    "name": name,
                    "kind": "property",
                    "signature": (
                        _signature(descriptor.fget)
                        if descriptor.fget is not None
                        else None
                    ),
                }
            )
        elif inspect.isfunction(descriptor):
            members.append(
                {
                    "name": name,
                    "kind": "method",
                    "signature": _signature(descriptor),
                }
            )
    return members


def public_api_contract() -> dict[str, Any]:
    """Return the current public import and behavioral-signature contract."""

    exported_names = list(public_api.__all__)
    exports: list[dict[str, Any]] = []
    for name in sorted(exported_names):
        root_value = getattr(public_api, name)
        binding_value = getattr(binding_api, name)
        row: dict[str, Any] = {
            "name": name,
            "root_and_binding_identity_equal": root_value is binding_value,
        }
        if inspect.isclass(root_value):
            row.update(
                {
                    "kind": "class",
                    "signature": _signature(root_value),
                    "members": _class_members(root_value),
                    "dataclass_fields": (
                        [field.name for field in dataclasses.fields(root_value)]
                        if dataclasses.is_dataclass(root_value)
                        else []
                    ),
                    "public_exception_bases": [
                        base.__name__
                        for base in root_value.__mro__[1:]
                        if issubclass(base, BaseException)
                    ],
                }
            )
        elif inspect.isfunction(root_value):
            row.update(
                {
                    "kind": "function",
                    "signature": _signature(root_value),
                }
            )
        else:
            row.update(
                {
                    "kind": "constant",
                    "python_type": type(root_value).__name__,
                    "value": _json_value(root_value),
                }
            )
        exports.append(row)
    return {
        "root_import_path": "pygrc.causal_pathways",
        "binding_import_path": "pygrc.causal_pathways.binding",
        "root_all_order": exported_names,
        "binding_has_every_root_export": all(
            hasattr(binding_api, name) for name in exported_names
        ),
        "exports": exports,
    }


def _capture_exception(
    condition_id: str,
    operation: Callable[[], object],
) -> dict[str, Any]:
    try:
        operation()
    except Exception as exc:  # noqa: BLE001 - the type is the frozen outcome
        return {
            "condition_id": condition_id,
            "exception_type": type(exc).__name__,
            "message": str(exc),
        }
    raise RuntimeError(f"{condition_id} did not raise")


def exception_contracts() -> list[dict[str, Any]]:
    """Exercise important public fail-closed conditions."""

    authority = _accepted_authority()

    def authority_drift() -> object:
        return CausalPathwayAuthority.load(
            ROOT,
            acceptance_anchor=_load_json(ACCEPTANCE_ANCHOR_PATH),
            trusted_anchor_digest="0" * 64,
        )

    def unknown_pathway() -> object:
        return PathwayBindingSession(authority).bind_pathway("missing.pathway")

    def unknown_composition() -> object:
        return PathwayBindingSession(authority).bind_composition("CMP-999")

    def unsupported_composition() -> object:
        return PathwayBindingSession(authority).bind_composition("CMP-06")

    def invalid_candidate_kind() -> object:
        return PathwayBindingSession(authority).declare_candidate(
            candidate_id="experiment.i118.invalid-kind",
            candidate_kind="invalid",
            purpose="Freeze the invalid candidate-kind condition.",
            owner="i118_fixture",
            evidence_owner="i118_fixture",
        )

    def declaration_after_lock() -> object:
        session = PathwayBindingSession(authority)
        session.bind_pathway("lgrc9v3.explicit_packet_transport")
        session.freeze_lock()
        return session.bind_pathway("pygrc.restoration_replay_identity")

    def missing_symbol() -> object:
        symbol = authority.symbols(
            "lgrc9v3.explicit_packet_transport",
            "packet_schedule",
        )[0]
        return replace(symbol, qualified_symbol="missing_symbol").resolve(ROOT)

    operations = (
        ("untrusted_acceptance_anchor_digest", authority_drift),
        ("unknown_pathway_identity", unknown_pathway),
        ("unknown_composition_identity", unknown_composition),
        ("unsupported_composition", unsupported_composition),
        ("invalid_candidate_kind", invalid_candidate_kind),
        ("declaration_after_lock", declaration_after_lock),
        ("missing_source_symbol", missing_symbol),
    )
    return [
        _capture_exception(condition_id, operation)
        for condition_id, operation in operations
    ]


def runtime_contracts() -> dict[str, Any]:
    """Exercise return types and context-manager behavior at the public API."""

    i116 = _load_module("causal_pathway_binding_i116_runtime", I116_BUILDER_PATH)
    authority = _accepted_authority()
    model = i116._two_node_runtime()
    session = PathwayBindingSession(authority)
    pathway = session.bind_pathway(
        "lgrc9v3.explicit_packet_transport",
        stage_ids=("packet_schedule",),
    )
    verified = pathway.symbol("packet_schedule", instance=model)
    lock = session.freeze_lock()
    call_result = verified(
        source_node_id=0,
        target_node_id=1,
        edge_id=0,
        amount=0.25,
    )
    receipt = session.build_receipt()

    context_managers: list[dict[str, Any]] = []

    composition_session = PathwayBindingSession(authority)
    composition = composition_session.bind_composition("CMP-20")
    composition_session.freeze_lock()
    composition_scope = composition.evidence_scope()
    composition_entered = composition_scope.__enter__()
    composition_exit = composition_scope.__exit__(None, None, None)
    context_managers.append(
        {
            "factory": "BoundComposition.evidence_scope",
            "scope_type": type(composition_scope).__name__,
            "enter_returns_self": composition_entered is composition_scope,
            "exit_return": composition_exit,
            "session_phase_after_exit": composition_session.phase,
        }
    )

    alternative_session = PathwayBindingSession(authority)
    first = alternative_session.bind_pathway(
        "lgrc9v3.explicit_packet_transport",
        stage_ids=("packet_schedule",),
    )
    second = alternative_session.bind_pathway(
        "pygrc.restoration_replay_identity",
        stage_ids=("snapshot_serialization",),
    )
    alternatives = alternative_session.declare_alternatives(
        alternative_set_id="i118.runtime-contract",
        pathway_ids=(first.pathway_id, second.pathway_id),
        selection_authority="i118_fixture",
    )
    alternative_session.freeze_lock()
    alternative_scope = alternatives.selection_scope()
    alternative_entered = alternative_scope.__enter__()
    alternative_exit = alternative_scope.__exit__(None, None, None)
    context_managers.append(
        {
            "factory": "AllowedPathwayAlternatives.selection_scope",
            "scope_type": type(alternative_scope).__name__,
            "enter_returns_self": alternative_entered is alternative_scope,
            "exit_return": alternative_exit,
            "session_phase_after_exit": alternative_session.phase,
        }
    )

    candidate_session = PathwayBindingSession(authority)
    candidate = candidate_session.declare_candidate(
        candidate_id="experiment.i118.runtime-contract",
        candidate_kind="pathway",
        purpose="Freeze candidate context-manager behavior.",
        owner="i118_fixture",
        evidence_owner="i118_fixture",
    )
    candidate_session.freeze_lock()
    candidate_scope = candidate.evidence_scope()
    candidate_entered = candidate_scope.__enter__()
    candidate_exit = candidate_scope.__exit__(None, None, None)
    context_managers.append(
        {
            "factory": "CandidateDeclaration.evidence_scope",
            "scope_type": type(candidate_scope).__name__,
            "enter_returns_self": candidate_entered is candidate_scope,
            "exit_return": candidate_exit,
            "session_phase_after_exit": candidate_session.phase,
        }
    )

    return {
        "return_object_types": {
            "CausalPathwayAuthority.load": type(authority).__name__,
            "PathwayBindingSession": type(session).__name__,
            "PathwayBindingSession.bind_pathway": type(pathway).__name__,
            "BoundPathway.symbol": type(verified).__name__,
            "PathwayBindingSession.freeze_lock": type(lock).__name__,
            "VerifiedCallable.__call__": type(call_result).__name__,
            "PathwayBindingSession.build_receipt": type(receipt).__name__,
            "BindingLock.to_record": type(lock.to_record()).__name__,
            "BindingReceipt.to_record": type(receipt.to_record()).__name__,
            "unbound_execution_classification": type(
                unbound_execution_classification()
            ).__name__,
        },
        "context_managers": context_managers,
        "unbound_execution_classification": dict(unbound_execution_classification()),
    }


def _relation_review(
    *,
    candidate_id: str,
    proposed_relation: str,
    mechanism_evidence: Mapping[str, str],
) -> tuple[dict[str, Any], str]:
    review: dict[str, Any] = {
        "artifact": "causal-pathway-candidate-relation-review",
        "schema_version": "causal_pathway_candidate_relation_review_v2",
        "review_id": f"fixture-review:{candidate_id}",
        "reviewer": "independent-fixture-reviewer",
        "review_status": "accepted_structural_distinction",
        "candidate_id": candidate_id,
        "candidate_kind": "composition",
        "proposed_source_pathway_id": "lgrc9v3.diagnostic_grc_reconstruction",
        "proposed_target_pathway_id": "lgrc9v3.explicit_packet_transport",
        "proposed_relation": proposed_relation,
        "invalid_relabel_conflict_ids": ["CMP-05"],
        "invalid_relabel_blocked_claims": [
            "diagnostic_as_behavior",
            "native packet admission",
        ],
        "mechanism_evidence": {
            "mechanism_id": mechanism_evidence["mechanism_id"],
            "path": mechanism_evidence["path"],
            "sha256": mechanism_evidence["sha256"],
        },
        "source_result_parameter": "diagnostic_result",
        "structural_distinction": {
            "distinction_kind": "reviewed_external_adapter",
            "source_binding": "candidate_callable_consumes_source_result",
            "mechanism_effect": "distinct_nonempty_mapping_result",
            "target_binding": "candidate_result_supplies_follow_on_request",
        },
    }
    review_digest = canonical_digest(review, excluding="review_digest")
    review["review_digest"] = review_digest
    return review, review_digest


def _write_case(
    output_dir: Path,
    *,
    case_id: str,
    lock: Any,
    receipt: Any,
    observations: Mapping[str, Any],
) -> dict[str, Any]:
    lock_path = output_dir / f"{case_id}.lock.json"
    receipt_path = output_dir / f"{case_id}.receipt.json"
    lock.write(lock_path)
    receipt.write(receipt_path)
    return {
        "case_id": case_id,
        "observations": dict(observations),
    }


def _reviewed_invalid_pair_case(
    output_dir: Path,
    authority: CausalPathwayAuthority,
    i116: Any,
) -> dict[str, Any]:
    model = i116._two_node_runtime()
    session = PathwayBindingSession(authority)
    candidate_id = "experiment.i118.reviewed-cmp05-mechanism"
    proposed_relation = "new externally owned diagnostic packet adapter"
    mechanism_evidence = {
        "evidence_kind": "executable_candidate_mechanism",
        "mechanism_id": "fixture.distinct_diagnostic_packet_adapter",
        "path": CMP05_EVIDENCE_PATH.as_posix(),
        "sha256": sha256_file(ROOT / CMP05_EVIDENCE_PATH),
    }
    relation_review, trusted_review_digest = _relation_review(
        candidate_id=candidate_id,
        proposed_relation=proposed_relation,
        mechanism_evidence=mechanism_evidence,
    )
    diagnostic = session.bind_pathway(
        "lgrc9v3.diagnostic_grc_reconstruction",
        stage_ids=("diagnostic_model_construction",),
    )
    packet = session.bind_pathway(
        "lgrc9v3.explicit_packet_transport",
        stage_ids=("packet_schedule",),
    )
    prepare = diagnostic.symbol("diagnostic_model_construction")
    schedule = packet.symbol("packet_schedule", instance=model)
    candidate = session.declare_candidate(
        candidate_id=candidate_id,
        candidate_kind="composition",
        purpose="Freeze a distinct reviewed mechanism over CMP-05 endpoints.",
        owner="i118_fixture",
        consumed_pathway_ids=(diagnostic.pathway_id, packet.pathway_id),
        proposed_source_pathway_id=diagnostic.pathway_id,
        proposed_target_pathway_id=packet.pathway_id,
        proposed_relation=proposed_relation,
        evidence_owner="i118_fixture",
        mechanism_evidence=mechanism_evidence,
        invalid_relabel_relation_review=relation_review,
        trusted_relation_review_digest=trusted_review_digest,
    )
    crossing = candidate.mechanism()
    lock = session.freeze_lock()
    with candidate.evidence_scope():
        diagnostic_result = prepare(model)
        request = crossing(diagnostic_result)
        schedule(**request["packet_schedule_arguments"])
    session.record_candidate_use(candidate.candidate_id)
    receipt = session.build_receipt()
    record = receipt.to_record()
    used = record["candidate_relations_exercised"][0]
    witness = used["candidate_execution_witness"]["candidate_dataflow_witness"]
    return _write_case(
        output_dir,
        case_id="11-reviewed-invalid-pair-candidate",
        lock=lock,
        receipt=receipt,
        observations={
            "invalid_relabel_conflict_ids": used["invalid_relabel_conflict_ids"],
            "blocked_claims": used["invalid_relabel_blocked_claims"],
            "source_result_parameter": used["invalid_relabel_relation_review"][
                "source_result_parameter"
            ],
            "request_dependency_proof_kind": record["actual_stage_symbol_invocations"][
                -1
            ]["candidate_request_flow"]["source_dependency_proof"]["proof_kind"],
            "witness_kind": witness["witness_kind"],
            "claim_status": record["claim_envelope"]["overall_claim_status"],
        },
    )


def _unused_candidate_pathway_case(
    output_dir: Path,
    authority: CausalPathwayAuthority,
) -> dict[str, Any]:
    session = PathwayBindingSession(authority)
    candidate = session.declare_candidate(
        candidate_id="experiment.i118.unused-candidate-pathway",
        candidate_kind="pathway",
        purpose="Freeze declared-but-unused candidate-pathway behavior.",
        owner="i118_fixture",
        evidence_owner="i118_fixture",
    )
    lock = session.freeze_lock()
    receipt = session.build_receipt()
    record = receipt.to_record()
    return _write_case(
        output_dir,
        case_id="12-unused-candidate-pathway",
        lock=lock,
        receipt=receipt,
        observations={
            "candidate_id": candidate.candidate_id,
            "declared_but_unused_candidate_ids": record["declared_but_unused"][
                "candidate_ids"
            ],
            "candidate_relations_exercised": record["candidate_relations_exercised"],
            "claim_qualified": record["claim_qualified"],
        },
    )


def _non_qualifying_effect_case(
    output_dir: Path,
    authority: CausalPathwayAuthority,
    i116: Any,
) -> dict[str, Any]:
    model = i116._two_node_runtime()
    session = PathwayBindingSession(authority)
    birth = session.bind_pathway(
        "lgrc9v3.boundary_birth",
        stage_ids=("birth_trial_commit",),
    )
    commit = birth.symbol("birth_trial_commit", instance=model)
    lock = session.freeze_lock()
    result = commit(
        parent_node_id=0,
        parent_port_id=2,
        outward_flux_pressure=1.0,
        rng_sample=0.0,
    )
    receipt = session.build_receipt()
    record = receipt.to_record()
    invocation = record["actual_stage_symbol_invocations"][0]
    return _write_case(
        output_dir,
        case_id="13-non-qualifying-returned-effect",
        lock=lock,
        receipt=receipt,
        observations={
            "result_type": type(result).__name__,
            "return_category": invocation["return_category"],
            "effect_outcome": invocation["effect_outcome"],
            "claim_qualifying_effect": invocation["claim_qualifying_effect"],
            "claim_qualified": record["claim_qualified"],
        },
    )


def _raised_effect_case(
    output_dir: Path,
    authority: CausalPathwayAuthority,
    i116: Any,
) -> dict[str, Any]:
    model = i116._two_node_runtime()
    session = PathwayBindingSession(authority)
    packet = session.bind_pathway(
        "lgrc9v3.explicit_packet_transport",
        stage_ids=("packet_schedule",),
    )
    schedule = packet.symbol("packet_schedule", instance=model)
    lock = session.freeze_lock()
    raised_type = ""
    try:
        schedule(
            source_node_id=0,
            target_node_id=1,
            edge_id=0,
            amount=-0.25,
        )
    except ValueError as exc:
        raised_type = type(exc).__name__
    else:
        raise RuntimeError("negative packet amount did not raise")
    receipt = session.build_receipt()
    record = receipt.to_record()
    invocation = record["actual_stage_symbol_invocations"][0]
    return _write_case(
        output_dir,
        case_id="14-raised-effect",
        lock=lock,
        receipt=receipt,
        observations={
            "raised_type": raised_type,
            "outcome": invocation["outcome"],
            "error_type": invocation["error_type"],
            "claim_qualified": record["claim_qualified"],
            "actual_bound_pathways_used": record["actual_bound_pathways_used"],
        },
    )


def generate_corpus(output_dir: Path) -> list[dict[str, Any]]:
    """Generate the complete practical binder corpus into ``output_dir``."""

    output_dir.mkdir(parents=True, exist_ok=True)
    i116 = _load_module("causal_pathway_binding_i116_corpus", I116_BUILDER_PATH)
    i116.EVIDENCE_DIR = output_dir
    authority = _accepted_authority()
    generated: list[dict[str, Any]] = []
    for case_id, function_name, semantic_families in I116_CASES:
        result = getattr(i116, function_name)(authority)
        generated.append(
            {
                "case_id": case_id,
                "semantic_families": list(semantic_families),
                "observations": result["assertions"],
            }
        )
    additional = (
        _reviewed_invalid_pair_case(output_dir, authority, i116),
        _unused_candidate_pathway_case(output_dir, authority),
        _non_qualifying_effect_case(output_dir, authority, i116),
        _raised_effect_case(output_dir, authority, i116),
    )
    family_by_case = dict(ADDITIONAL_CASES)
    for result in additional:
        generated.append(
            {
                **result,
                "semantic_families": list(family_by_case[result["case_id"]]),
            }
        )
    return generated


def _artifact_row(path: Path, *, digest_field: str) -> dict[str, Any]:
    record = _load_json(path)
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "byte_length": path.stat().st_size,
        "sha256": sha256_file(path),
        "digest_field": digest_field,
        "artifact_digest": record[digest_field],
    }


def _canonical_case_paths(case_id: str) -> tuple[Path, Path]:
    if any(case_id == row[0] for row in I116_CASES):
        directory = ROOT / "implementation/evidence/causal-pathway-binding/i116"
    else:
        directory = CORPUS_DIR
    return (
        directory / f"{case_id}.lock.json",
        directory / f"{case_id}.receipt.json",
    )


def _canonical_fixture_paths() -> list[Path]:
    base = ROOT / "implementation/evidence/causal-pathway-binding"
    paths = [
        base / "i115-native-pathway.lock.json",
        base / "i115-native-pathway.receipt.json",
        base / "i115-conformance-execution.json",
        base / "i115-negative-control-execution.json",
        base / "i116-low-context-consumer-specification.json",
    ]
    paths.extend(sorted((base / "i116").glob("*.json")))
    return paths


def checker_independence_contract() -> dict[str, Any]:
    """Describe direct and dynamic imports used by the independent checker."""

    source = CHECKER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(CHECKER_PATH))
    imports: list[dict[str, Any]] = []
    dynamic_imports: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    {"kind": "import", "module": alias.name, "line": node.lineno}
                )
        elif isinstance(node, ast.ImportFrom):
            imports.append(
                {
                    "kind": "from",
                    "module": node.module or "",
                    "line": node.lineno,
                }
            )
        elif isinstance(node, ast.Call):
            function_name = ""
            if isinstance(node.func, ast.Name):
                function_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                function_name = node.func.attr
            if function_name not in {"__import__", "import_module"} or not node.args:
                continue
            argument = node.args[0]
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                dynamic_imports.append(
                    {
                        "function": function_name,
                        "module": argument.value,
                        "line": node.lineno,
                    }
                )
    imports.sort(key=lambda row: (row["line"], row["kind"], row["module"]))
    dynamic_imports.sort(key=lambda row: (row["line"], row["module"]))
    forbidden = [
        row
        for row in [*imports, *dynamic_imports]
        if str(row["module"]) == "pygrc.causal_pathways"
        or str(row["module"]).startswith("pygrc.causal_pathways.")
    ]
    return {
        "checker_path": CHECKER_PATH.relative_to(ROOT).as_posix(),
        "checker_sha256": sha256_file(CHECKER_PATH),
        "imports": imports,
        "dynamic_imports": dynamic_imports,
        "forbidden_binding_imports": forbidden,
        "load_bearing_derivations_remain_independent": not forbidden,
    }


def _freeze_record(
    *,
    artifact: str,
    schema_version: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    record = {
        "artifact": artifact,
        "schema_version": schema_version,
        "iteration": 118,
        "date": "2026-08-20",
        "status": "frozen",
        "source_commit": _git("rev-parse", "HEAD"),
        "source_tree": _git("rev-parse", "HEAD^{tree}"),
        "binder_source_path": "src/pygrc/causal_pathways/binding.py",
        "binder_source_sha256": sha256_file(
            ROOT / "src/pygrc/causal_pathways/binding.py"
        ),
        "runtime_behavior_changed": False,
        **payload,
    }
    record["freeze_digest"] = _record_digest(record, excluding="freeze_digest")
    return record


def write_freezes() -> None:
    """Write canonical I118 freezes from the unmodified binder."""

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".i118-corpus-", dir=ROOT) as raw:
        generated_dir = Path(raw)
        generated = generate_corpus(generated_dir)
        for case in generated:
            case_id = str(case["case_id"])
            canonical_lock, canonical_receipt = _canonical_case_paths(case_id)
            generated_lock = generated_dir / f"{case_id}.lock.json"
            generated_receipt = generated_dir / f"{case_id}.receipt.json"
            if any(case_id == row[0] for row in I116_CASES):
                if generated_lock.read_bytes() != canonical_lock.read_bytes():
                    raise RuntimeError(f"{case_id} lock differs from I116 evidence")
                if generated_receipt.read_bytes() != canonical_receipt.read_bytes():
                    raise RuntimeError(f"{case_id} receipt differs from I116 evidence")
            else:
                shutil.copyfile(generated_lock, canonical_lock)
                shutil.copyfile(generated_receipt, canonical_receipt)

        corpus_cases: list[dict[str, Any]] = []
        for case in generated:
            case_id = str(case["case_id"])
            lock_path, receipt_path = _canonical_case_paths(case_id)
            corpus_cases.append(
                {
                    **case,
                    "artifacts": [
                        _artifact_row(lock_path, digest_field="lock_digest"),
                        _artifact_row(receipt_path, digest_field="receipt_digest"),
                    ],
                }
            )

    canonical_manifest = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "byte_length": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in _canonical_fixture_paths()
    ]
    public_freeze = _freeze_record(
        artifact="I118 public API compatibility freeze",
        schema_version="i118_public_api_compatibility_freeze_v1",
        payload={"public_api_contract": public_api_contract()},
    )
    artifact_freeze = _freeze_record(
        artifact="I118 artifact and runtime compatibility freeze",
        schema_version="i118_artifact_runtime_compatibility_freeze_v1",
        payload={
            "canonical_i115_i116_fixture_manifest": canonical_manifest,
            "regenerated_corpus_cases": corpus_cases,
            "runtime_contracts": runtime_contracts(),
            "exception_contracts": exception_contracts(),
        },
    )
    checker_freeze = _freeze_record(
        artifact="I118 checker independence freeze",
        schema_version="i118_checker_independence_freeze_v1",
        payload={"checker_independence_contract": checker_independence_contract()},
    )
    _write_json(PUBLIC_API_FREEZE_PATH, public_freeze)
    _write_json(ARTIFACT_RUNTIME_FREEZE_PATH, artifact_freeze)
    _write_json(CHECKER_FREEZE_PATH, checker_freeze)


def _assert_freeze_digest(path: Path, record: Mapping[str, Any]) -> None:
    expected = _record_digest(record, excluding="freeze_digest")
    if record.get("freeze_digest") != expected:
        raise AssertionError(f"{path.name} freeze digest is invalid")


def verify_public_api_freeze() -> None:
    freeze = _load_json(PUBLIC_API_FREEZE_PATH)
    _assert_freeze_digest(PUBLIC_API_FREEZE_PATH, freeze)
    if freeze["public_api_contract"] != public_api_contract():
        raise AssertionError("public causal-pathway API differs from I118 freeze")


def verify_checker_independence_freeze() -> None:
    freeze = _load_json(CHECKER_FREEZE_PATH)
    _assert_freeze_digest(CHECKER_FREEZE_PATH, freeze)
    current = checker_independence_contract()
    if current["forbidden_binding_imports"]:
        raise AssertionError("independent checker imports binder implementation")
    if freeze["checker_independence_contract"] != current:
        raise AssertionError("independent checker differs from I118 freeze")


def verify_artifact_runtime_freeze() -> None:
    freeze = _load_json(ARTIFACT_RUNTIME_FREEZE_PATH)
    _assert_freeze_digest(ARTIFACT_RUNTIME_FREEZE_PATH, freeze)
    for frozen in freeze["canonical_i115_i116_fixture_manifest"]:
        path = ROOT / frozen["path"]
        if path.stat().st_size != frozen["byte_length"]:
            raise AssertionError(f"canonical fixture size drift: {frozen['path']}")
        if sha256_file(path) != frozen["sha256"]:
            raise AssertionError(f"canonical fixture byte drift: {frozen['path']}")

    with tempfile.TemporaryDirectory(prefix=".i118-verify-", dir=ROOT) as raw:
        generated_dir = Path(raw)
        generated = generate_corpus(generated_dir)
        generated_by_id = {row["case_id"]: row for row in generated}
        for frozen_case in freeze["regenerated_corpus_cases"]:
            case_id = frozen_case["case_id"]
            current_case = generated_by_id[case_id]
            if current_case != {
                key: value for key, value in frozen_case.items() if key != "artifacts"
            }:
                raise AssertionError(f"runtime observation drift: {case_id}")
            for artifact in frozen_case["artifacts"]:
                kind = (
                    "lock" if artifact["digest_field"] == "lock_digest" else "receipt"
                )
                generated_path = generated_dir / f"{case_id}.{kind}.json"
                canonical_path = ROOT / artifact["path"]
                if generated_path.read_bytes() != canonical_path.read_bytes():
                    raise AssertionError(f"golden-byte drift: {case_id} {kind}")
                if sha256_file(generated_path) != artifact["sha256"]:
                    raise AssertionError(f"golden digest drift: {case_id} {kind}")

    if freeze["runtime_contracts"] != runtime_contracts():
        raise AssertionError("public return/context-manager behavior drift")
    if freeze["exception_contracts"] != exception_contracts():
        raise AssertionError("public exception behavior drift")


def verify_baseline_execution_record() -> None:
    record = _load_json(BASELINE_EXECUTION_PATH)
    expected = _record_digest(record, excluding="execution_digest")
    if record.get("execution_digest") != expected:
        raise AssertionError("I118 baseline execution digest is invalid")
    if record.get("status") != "passed":
        raise AssertionError("I118 baseline execution is not passed")


def verify_all_freezes() -> None:
    verify_public_api_freeze()
    verify_checker_independence_freeze()
    verify_artifact_runtime_freeze()
    verify_baseline_execution_record()


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    if arguments.write:
        write_freezes()
    else:
        verify_all_freezes()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

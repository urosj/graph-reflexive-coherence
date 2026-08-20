"""Candidate declarations, executable evidence, and provenance proofs.

This provider owns the fail-closed boundary for explicitly unregistered
pathways and compositions.  It depends on the permanent authority and identity
providers and communicates with runtime orchestration through a narrow
structural host protocol.
"""

from __future__ import annotations

import ast
import importlib.util
import inspect
import json
import re
import textwrap
from collections.abc import Callable, Collection, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType, TracebackType
from typing import Any, Final, Protocol, Self, cast

from .authority import (
    CausalPathwayAuthority,
    UnknownCompositionError,
    UnknownPathwayError,
)
from .identity import (
    AuthorityDriftError,
    CausalPathwayBindingError,
    SourceSymbolBinding,
    SymbolBindingError,
    _callable_definition,
    _CallableIdentityGuard,
    _canonical_value_digest,
    canonical_digest,
    sha256_file,
)

AUTHORITY_COORDINATES: Final[tuple[str, ...]] = (
    "direction",
    "funding",
    "eligibility",
    "scheduling",
    "commit",
    "reception",
)

INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT: Final[str] = (
    "externally_supplied_digest_for_invalid_relabel_candidate_review"
)

_REVIEWED_STRUCTURAL_DISTINCTION: Final[Mapping[str, str]] = MappingProxyType(
    {
        "distinction_kind": "reviewed_external_adapter",
        "source_binding": "candidate_callable_consumes_source_result",
        "mechanism_effect": "distinct_nonempty_mapping_result",
        "target_binding": "candidate_result_supplies_follow_on_request",
    }
)


class InvalidCandidateError(CausalPathwayBindingError):
    """Raised when an unregistered candidate hides identity or authority debt."""


class _CandidateRequestError(ValueError):
    """Internal failure to expose a canonical candidate request."""


@dataclass(frozen=True)
class _CandidateMechanismEvent:
    """Candidate-owned event handed to the runtime recorder boundary."""

    candidate_id: str
    mechanism_id: str
    symbol_id: str
    outcome: str
    result_type: str | None
    error_type: str | None
    callable_identity: Mapping[str, Any]
    relation_review_digest: str | None
    structural_result_observed: bool | None
    runtime_object_flow: Mapping[str, Any]


class _CandidateExecutionScope(Protocol):
    """Minimum runtime-scope surface visible to a candidate declaration."""

    scope_id: str

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool: ...


CandidateExecutionScope = _CandidateExecutionScope


class _CandidateRuntime(Protocol):
    """Execution collaborator required by a verified candidate mechanism."""

    def authorize_candidate_mechanism(
        self,
        *,
        candidate_id: str,
        symbol_id: str,
    ) -> CandidateExecutionScope: ...

    def observe_object_flow(
        self,
        *,
        target: Callable[..., Any],
        arguments: Mapping[str, object],
        result: object | None,
    ) -> dict[str, Any]: ...

    def record_candidate_mechanism_event(
        self,
        scope: CandidateExecutionScope,
        event: _CandidateMechanismEvent,
        *,
        result: object | None,
    ) -> None: ...


class PathwayBindingSession(Protocol):
    """Narrow candidate factory and recorder host supplied by the runtime."""

    authority: CausalPathwayAuthority

    def _callable_identity_guard(
        self,
        symbol: SourceSymbolBinding,
        target: Callable[..., Any],
    ) -> _CallableIdentityGuard: ...

    def _candidate_evidence_scope(
        self,
        candidate: CandidateDeclaration,
    ) -> CandidateExecutionScope: ...

    def _candidate_mechanism(
        self,
        candidate_id: str,
    ) -> VerifiedCandidateMechanism: ...

    def _candidate_runtime(self) -> _CandidateRuntime: ...


def _source_default_payload(value: Any) -> dict[str, Any]:
    """Return a type-preserving record for one admitted Python default."""

    value_type = type(value)
    if value is None:
        return {"python_type": "none"}
    if value_type is bool:
        return {"python_type": "bool", "value": value}
    if value_type is int:
        return {"python_type": "int", "value": value}
    if value_type is float:
        return {"python_type": "float", "value": value}
    if value_type is str:
        return {"python_type": "str", "value": value}
    if value_type is list:
        return {
            "python_type": "list",
            "items": [_source_default_payload(item) for item in value],
        }
    if value_type is tuple:
        return {
            "python_type": "tuple",
            "items": [_source_default_payload(item) for item in value],
        }
    if value_type is dict:
        if not all(type(key) is str for key in value):
            raise ValueError("reviewed source defaults require string mapping keys")
        return {
            "python_type": "dict",
            "items": {
                key: _source_default_payload(item)
                for key, item in value.items()
            },
        }
    raise ValueError("unsupported reviewed source-parameter default")


def _source_default_digest(value: Any) -> str:
    """Digest an admitted default without erasing Python container types."""

    return _canonical_value_digest(_source_default_payload(value))


_SOURCE_PRESENT: Final[object] = object()


def _safe_source_expression(
    node: ast.expr,
    *,
    source_result_parameter: str,
    source_value: object,
) -> Any:
    """Evaluate the small pure expression language admitted for source flow."""

    def evaluate(child: ast.expr) -> Any:
        return _safe_source_expression(
            child,
            source_result_parameter=source_result_parameter,
            source_value=source_value,
        )

    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id == source_result_parameter:
        return source_value
    if isinstance(node, ast.Dict):
        if any(key is None for key in node.keys):
            raise ValueError("mapping unpacking is not a reviewed source expression")
        keys = [evaluate(key) for key in node.keys if key is not None]
        if not all(isinstance(key, str) for key in keys) or len(set(keys)) != len(keys):
            raise ValueError("reviewed request mappings require unique string keys")
        return {
            key: evaluate(value)
            for key, value in zip(keys, node.values, strict=True)
        }
    if isinstance(node, ast.List):
        return [evaluate(item) for item in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(evaluate(item) for item in node.elts)
    if isinstance(node, ast.IfExp):
        return evaluate(node.body if bool(evaluate(node.test)) else node.orelse)
    if isinstance(node, ast.Compare) and len(node.ops) == len(node.comparators) == 1:
        left = evaluate(node.left)
        right = evaluate(node.comparators[0])
        operator = node.ops[0]
        if isinstance(operator, ast.Is):
            return left is right
        if isinstance(operator, ast.IsNot):
            return left is not right
        if isinstance(operator, ast.Eq):
            return left == right
        if isinstance(operator, ast.NotEq):
            return left != right
    if isinstance(node, ast.UnaryOp):
        operand = evaluate(node.operand)
        if isinstance(node.op, ast.Not):
            return not operand
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
    if isinstance(node, ast.BoolOp):
        result = evaluate(node.values[0])
        if isinstance(node.op, ast.And):
            for item in node.values[1:]:
                if not bool(result):
                    return result
                result = evaluate(item)
            return result
        if isinstance(node.op, ast.Or):
            for item in node.values[1:]:
                if bool(result):
                    return result
                result = evaluate(item)
            return result
    if isinstance(node, ast.BinOp):
        left = evaluate(node.left)
        right = evaluate(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
        if isinstance(node.op, ast.Mod):
            return left % right
    raise ValueError("unsupported reviewed source-dependency expression")


def _safe_source_parameter_default(
    arguments: ast.arguments,
    *,
    source_result_parameter: str,
) -> Any:
    """Return the frozen safe default used when the source argument is omitted."""

    positional = [*arguments.posonlyargs, *arguments.args]
    default_offset = len(positional) - len(arguments.defaults)
    for index, argument in enumerate(positional):
        if argument.arg != source_result_parameter:
            continue
        if index < default_offset:
            raise ValueError("reviewed source parameter has no omission default")
        return _safe_source_expression(
            arguments.defaults[index - default_offset],
            source_result_parameter="",
            source_value=None,
        )
    for argument, default in zip(
        arguments.kwonlyargs,
        arguments.kw_defaults,
        strict=True,
    ):
        if argument.arg != source_result_parameter:
            continue
        if default is None:
            raise ValueError("reviewed source parameter has no omission default")
        return _safe_source_expression(
            default,
            source_result_parameter="",
            source_value=None,
        )
    raise ValueError("reviewed source parameter is not a fixed named parameter")


def _source_parameter_default_contract(
    definition: Callable[..., Any],
    *,
    source_result_parameter: str,
) -> tuple[Any, str] | None:
    """Match one safe source default to the loaded callable signature."""

    try:
        tree = ast.parse(textwrap.dedent(inspect.getsource(definition)))
    except (OSError, TypeError, SyntaxError):
        return None
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    if len(definitions) != 1 or definitions[0].decorator_list:
        return None
    try:
        source_default = _safe_source_parameter_default(
            definitions[0].args,
            source_result_parameter=source_result_parameter,
        )
        runtime_parameter = inspect.signature(definition).parameters.get(
            source_result_parameter
        )
        if (
            runtime_parameter is None
            or runtime_parameter.kind
            not in {
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }
            or runtime_parameter.default is inspect.Parameter.empty
        ):
            return None
        source_default_digest = _source_default_digest(source_default)
        if source_default_digest != _source_default_digest(
            runtime_parameter.default
        ):
            return None
    except (ArithmeticError, TypeError, ValueError):
        return None
    return source_default, source_default_digest


def _source_dependent_request_proof(
    definition: Callable[..., Any],
    *,
    source_result_parameter: str,
    request_path: Sequence[str],
) -> dict[str, Any] | None:
    """Prove that one exact returned request changes with source presence."""

    try:
        tree = ast.parse(textwrap.dedent(inspect.getsource(definition)))
    except (OSError, TypeError, SyntaxError):
        return None
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    if len(definitions) != 1:
        return None
    parsed_definition = definitions[0]
    body = list(parsed_definition.body)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        return None
    request_expression = body[0].value
    if request_expression is None:
        return None
    for segment in request_path:
        if not isinstance(request_expression, ast.Dict):
            return None
        matches = [
            value
            for key, value in zip(
                request_expression.keys,
                request_expression.values,
                strict=True,
            )
            if isinstance(key, ast.Constant) and key.value == segment
        ]
        if len(matches) != 1:
            return None
        request_expression = matches[0]
    try:
        default_contract = _source_parameter_default_contract(
            definition,
            source_result_parameter=source_result_parameter,
        )
        if default_contract is None:
            return None
        source_default, source_default_digest = default_contract
        present = _safe_source_expression(
            request_expression,
            source_result_parameter=source_result_parameter,
            source_value=_SOURCE_PRESENT,
        )
        omitted = _safe_source_expression(
            request_expression,
            source_result_parameter=source_result_parameter,
            source_value=source_default,
        )
        present_payload = _candidate_request_payload(present)
        omitted_payload = _candidate_request_payload(omitted)
    except (ArithmeticError, TypeError, ValueError):
        return None
    if (
        not isinstance(present_payload, dict)
        or not present_payload
        or not isinstance(omitted_payload, dict)
        or not omitted_payload
    ):
        return None
    present_digest = _canonical_value_digest(present_payload)
    omitted_digest = _canonical_value_digest(omitted_payload)
    if present_digest == omitted_digest:
        return None
    return {
        "schema_version": "reviewed_candidate_source_dependency_v2",
        "proof_kind": "source_presence_changes_exact_target_request",
        "source_result_parameter": source_result_parameter,
        "candidate_result_request_path": list(request_path),
        "source_parameter_default_digest": source_default_digest,
        "source_present_request_digest": present_digest,
        "source_omitted_request_digest": omitted_digest,
    }


def _normalized_claim_text(value: str) -> str:
    """Normalize claim labels so punctuation cannot hide a blocked relabel."""

    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _claim_semantic_tokens(value: str) -> set[str]:
    """Return load-bearing tokens for order-independent relabel comparison."""

    stopwords = {"a", "an", "and", "as", "from", "is", "of", "or", "the", "to"}
    return set(_normalized_claim_text(value).split()) - stopwords


def _restates_blocked_relabel(relation: str, blocked_relabel: str) -> bool:
    """Reject literal or order-independent restatements of a blocked label."""

    normalized_relation = _normalized_claim_text(relation)
    normalized_blocked = _normalized_claim_text(blocked_relabel)
    blocked_tokens = _claim_semantic_tokens(blocked_relabel)
    return normalized_blocked in normalized_relation or (
        bool(blocked_tokens) and blocked_tokens <= _claim_semantic_tokens(relation)
    )


def _load_candidate_evidence_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AuthorityDriftError(f"authority {path} must contain a JSON object")
    return value


def _resolve_candidate_symbol(
    symbol: SourceSymbolBinding,
    repository_root: Path,
    *,
    verify_source: bool = True,
) -> Callable[..., Any]:
    """Load an unregistered candidate callable from its pinned repository file."""

    root = repository_root.resolve()
    source = (root / symbol.source_path).resolve()
    try:
        source.relative_to(root)
    except ValueError as exc:
        raise InvalidCandidateError(
            "candidate executable source path escapes the repository"
        ) from exc
    spec = importlib.util.spec_from_file_location(symbol.module, source)
    if spec is None or spec.loader is None:
        raise InvalidCandidateError(
            f"candidate executable module {symbol.module!r} cannot be loaded"
        )
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        target: Any = module
        for part in symbol.qualified_symbol.split("."):
            target = getattr(target, part)
    except (AttributeError, ImportError, OSError) as exc:
        raise InvalidCandidateError(
            f"candidate executable {symbol.qualified_symbol!r} cannot be loaded"
        ) from exc
    if not callable(target):
        raise InvalidCandidateError(
            f"candidate executable {symbol.qualified_symbol!r} is not callable"
        )
    resolved = cast(Callable[..., Any], target)
    if verify_source:
        try:
            symbol.callable_identity(resolved, repository_root)
        except SymbolBindingError as exc:
            raise InvalidCandidateError(
                "candidate executable symbol is absent, stale, or inconsistent"
            ) from exc
    return resolved


@dataclass(frozen=True)
class CandidateDeclaration:
    """An explicit unregistered pathway or composition candidate."""

    _session: PathwayBindingSession = field(repr=False, compare=False)
    candidate_id: str
    candidate_kind: str
    purpose: str
    owner: str
    consumed_pathway_ids: tuple[str, ...]
    consumed_composition_ids: tuple[str, ...]
    proposed_source_pathway_id: str | None
    proposed_target_pathway_id: str | None
    proposed_relation: str | None
    authority: Mapping[str, str]
    producer_residue: tuple[str, ...]
    adapter_residue: tuple[str, ...]
    configured_residue: tuple[str, ...]
    evidence_owner: str
    blocked_claims: tuple[str, ...]
    mechanism_evidence: CandidateMechanismEvidence | None
    mechanism_link: Mapping[str, Any] | None
    invalid_relabel_conflict_ids: tuple[str, ...]
    invalid_relabel_blocked_claims: tuple[str, ...]
    invalid_relabel_relation_review: CandidateRelationReview | None
    claim_ceiling: str = "experimental_unregistered"
    promotion_status: str = "none"

    def to_record(self) -> dict[str, Any]:
        """Return a serializable candidate record."""

        return {
            "candidate_id": self.candidate_id,
            "candidate_kind": self.candidate_kind,
            "purpose": self.purpose,
            "owner": self.owner,
            "consumed_admitted_pathway_ids": list(self.consumed_pathway_ids),
            "consumed_admitted_composition_ids": list(self.consumed_composition_ids),
            "proposed_source_pathway_id": self.proposed_source_pathway_id,
            "proposed_target_pathway_id": self.proposed_target_pathway_id,
            "proposed_relation": self.proposed_relation,
            "authority": dict(self.authority),
            "producer_residue": list(self.producer_residue),
            "adapter_residue": list(self.adapter_residue),
            "configured_residue": list(self.configured_residue),
            "evidence_owner": self.evidence_owner,
            "mechanism_evidence": (
                self.mechanism_evidence.to_record()
                if self.mechanism_evidence is not None
                else None
            ),
            "candidate_mechanism_link": (
                dict(self.mechanism_link)
                if self.mechanism_link is not None
                else None
            ),
            "invalid_relabel_conflict_ids": list(self.invalid_relabel_conflict_ids),
            "invalid_relabel_blocked_claims": list(
                self.invalid_relabel_blocked_claims
            ),
            "invalid_relabel_relation_review": (
                self.invalid_relabel_relation_review.to_record()
                if self.invalid_relabel_relation_review is not None
                else None
            ),
            "invalid_relabel_relation_review_trust_requirement": (
                INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT
                if self.invalid_relabel_relation_review is not None
                else None
            ),
            "proposed_relation_claim_status": (
                "descriptive_unreviewed_not_claim_qualified"
                if self.proposed_relation is not None
                else None
            ),
            "claim_ceiling": self.claim_ceiling,
            "blocked_claims": list(self.blocked_claims),
            "promotion_status": self.promotion_status,
        }

    def evidence_scope(self) -> CandidateExecutionScope:
        """Return an explicit observed-use scope for this candidate."""

        return self._session._candidate_evidence_scope(self)

    def mechanism(self) -> VerifiedCandidateMechanism:
        """Return the exact candidate-specific executable linked before lock."""

        return self._session._candidate_mechanism(self.candidate_id)


@dataclass(frozen=True)
class CandidateMechanismEvidence:
    """Pre-lock content address for candidate-specific executable evidence."""

    evidence_kind: str
    mechanism_id: str
    path: str
    sha256: str

    @classmethod
    def from_record(
        cls,
        record: Mapping[str, Any],
    ) -> CandidateMechanismEvidence:
        """Parse the intentionally small candidate-evidence contract."""

        evidence = cls(
            evidence_kind=str(record.get("evidence_kind", "")),
            mechanism_id=str(record.get("mechanism_id", "")),
            path=str(record.get("path", "")),
            sha256=str(record.get("sha256", "")),
        )
        if evidence.evidence_kind != "executable_candidate_mechanism":
            raise InvalidCandidateError(
                "candidate mechanism evidence must be executable_candidate_mechanism"
            )
        if not evidence.mechanism_id:
            raise InvalidCandidateError(
                "candidate mechanism evidence requires a mechanism_id"
            )
        if not evidence.path:
            raise InvalidCandidateError("candidate mechanism evidence requires a path")
        if not re.fullmatch(r"[0-9a-f]{64}", evidence.sha256):
            raise InvalidCandidateError(
                "candidate mechanism evidence requires a lowercase SHA-256"
            )
        return evidence

    def to_record(self) -> dict[str, str]:
        """Return the exact evidence identity frozen into lock and receipt."""

        return {
            "evidence_kind": self.evidence_kind,
            "mechanism_id": self.mechanism_id,
            "path": self.path,
            "sha256": self.sha256,
        }

    def assert_current(
        self,
        repository_root: Path,
        *,
        candidate_kind: str,
        proposed_source_pathway_id: str | None,
        proposed_target_pathway_id: str | None,
        proposed_relation: str | None,
    ) -> SourceSymbolBinding:
        """Validate and return the artifact's exact executable symbol."""

        relative = Path(self.path)
        if relative.is_absolute() or ".." in relative.parts:
            raise InvalidCandidateError(
                "candidate mechanism evidence path must stay repository-relative"
            )
        root = repository_root.resolve()
        target = (root / relative).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise InvalidCandidateError(
                "candidate mechanism evidence path escapes the repository"
            ) from exc
        if not target.is_file() or target.stat().st_size == 0:
            raise InvalidCandidateError(
                f"candidate mechanism evidence {self.path!r} is missing or empty"
            )
        if sha256_file(target) != self.sha256:
            raise InvalidCandidateError(
                f"candidate mechanism evidence {self.path!r} content is stale"
            )
        try:
            artifact = _load_candidate_evidence_json(target)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise InvalidCandidateError(
                "candidate mechanism evidence must be a JSON artifact"
            ) from exc
        expected = {
            "artifact": "causal-pathway-candidate-mechanism-evidence",
            "schema_version": "causal_pathway_candidate_mechanism_evidence_v2",
            "mechanism_id": self.mechanism_id,
            "candidate_kind": candidate_kind,
            "proposed_source_pathway_id": proposed_source_pathway_id,
            "proposed_target_pathway_id": proposed_target_pathway_id,
            "supported_relation": proposed_relation,
        }
        mismatched = [
            field for field, value in expected.items() if artifact.get(field) != value
        ]
        if mismatched:
            raise InvalidCandidateError(
                "candidate mechanism evidence does not match its declaration: "
                f"{mismatched}"
            )
        if set(artifact) != {*expected, "executable_symbol"}:
            raise InvalidCandidateError(
                "candidate mechanism artifact fields are incomplete or widened"
            )
        executable = artifact.get("executable_symbol")
        expected_symbol_fields = {
            "symbol_id",
            "module",
            "qualified_symbol",
            "binding_role",
            "call_kind",
            "source_path",
            "source_sha256",
        }
        if not isinstance(executable, Mapping) or set(executable) != (
            expected_symbol_fields
        ):
            raise InvalidCandidateError(
                "candidate mechanism evidence requires one exact executable symbol"
            )
        if (
            executable.get("symbol_id")
            != f"candidate-mechanism:{self.mechanism_id}"
            or executable.get("binding_role") != "candidate_mechanism_entrypoint"
            or executable.get("call_kind") != "module_function"
        ):
            raise InvalidCandidateError(
                "candidate executable identity or binding role is invalid"
            )
        module = str(executable.get("module", ""))
        qualified_symbol = str(executable.get("qualified_symbol", ""))
        if (
            re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*",
                module,
            )
            is None
            or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", qualified_symbol) is None
        ):
            raise InvalidCandidateError(
                "candidate executable module or qualified symbol is invalid"
            )
        source_relative = Path(str(executable.get("source_path", "")))
        if source_relative.is_absolute() or ".." in source_relative.parts:
            raise InvalidCandidateError(
                "candidate executable source path must stay repository-relative"
            )
        resolved_root = repository_root.resolve()
        try:
            (resolved_root / source_relative).resolve().relative_to(resolved_root)
        except ValueError as exc:
            raise InvalidCandidateError(
                "candidate executable source path escapes the repository"
            ) from exc
        symbol = SourceSymbolBinding.from_record(executable)
        _resolve_candidate_symbol(symbol, repository_root)
        return symbol


@dataclass(frozen=True)
class CandidateRelationReview:
    """Separately trusted structural distinction for one invalid-pair candidate."""

    review_id: str
    reviewer: str
    candidate_id: str
    candidate_kind: str
    proposed_source_pathway_id: str
    proposed_target_pathway_id: str
    proposed_relation: str
    invalid_relabel_conflict_ids: tuple[str, ...]
    invalid_relabel_blocked_claims: tuple[str, ...]
    mechanism_evidence: Mapping[str, str]
    source_result_parameter: str
    structural_distinction: Mapping[str, str]
    review_digest: str

    @classmethod
    def from_record(
        cls,
        record: Mapping[str, Any],
        *,
        trusted_digest: str | None,
    ) -> CandidateRelationReview:
        """Parse one review only when its digest comes from caller trust input."""

        expected_fields = {
            "artifact",
            "schema_version",
            "review_id",
            "reviewer",
            "review_status",
            "candidate_id",
            "candidate_kind",
            "proposed_source_pathway_id",
            "proposed_target_pathway_id",
            "proposed_relation",
            "invalid_relabel_conflict_ids",
            "invalid_relabel_blocked_claims",
            "mechanism_evidence",
            "source_result_parameter",
            "structural_distinction",
            "review_digest",
        }
        review_digest = str(record.get("review_digest", ""))
        if (
            set(record) != expected_fields
            or record.get("artifact") != "causal-pathway-candidate-relation-review"
            or record.get("schema_version")
            != "causal_pathway_candidate_relation_review_v2"
            or record.get("review_status") != "accepted_structural_distinction"
            or not str(record.get("review_id", ""))
            or not str(record.get("reviewer", ""))
            or re.fullmatch(r"[0-9a-f]{64}", review_digest) is None
            or canonical_digest(record, excluding="review_digest") != review_digest
        ):
            raise InvalidCandidateError(
                "invalid-relabel candidate review is malformed or self-inconsistent"
            )
        if trusted_digest != review_digest:
            raise InvalidCandidateError(
                "invalid-relabel candidate requires an independently trusted "
                "structural-distinction review digest"
            )
        conflicts = record.get("invalid_relabel_conflict_ids")
        blocks = record.get("invalid_relabel_blocked_claims")
        mechanism_evidence = record.get("mechanism_evidence")
        source_result_parameter = str(record.get("source_result_parameter", ""))
        distinction = record.get("structural_distinction")
        if (
            not isinstance(conflicts, list)
            or not conflicts
            or not all(isinstance(item, str) and item for item in conflicts)
            or not isinstance(blocks, list)
            or not blocks
            or not all(isinstance(item, str) and item for item in blocks)
            or not isinstance(mechanism_evidence, Mapping)
            or set(mechanism_evidence) != {"mechanism_id", "path", "sha256"}
            or re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*",
                source_result_parameter,
            )
            is None
            or not isinstance(distinction, Mapping)
            or dict(distinction) != dict(_REVIEWED_STRUCTURAL_DISTINCTION)
        ):
            raise InvalidCandidateError(
                "invalid-relabel candidate review lacks its structural contract"
            )
        return cls(
            review_id=str(record["review_id"]),
            reviewer=str(record["reviewer"]),
            candidate_id=str(record["candidate_id"]),
            candidate_kind=str(record["candidate_kind"]),
            proposed_source_pathway_id=str(record["proposed_source_pathway_id"]),
            proposed_target_pathway_id=str(record["proposed_target_pathway_id"]),
            proposed_relation=str(record["proposed_relation"]),
            invalid_relabel_conflict_ids=tuple(conflicts),
            invalid_relabel_blocked_claims=tuple(blocks),
            mechanism_evidence=MappingProxyType(
                {str(key): str(value) for key, value in mechanism_evidence.items()}
            ),
            source_result_parameter=source_result_parameter,
            structural_distinction=MappingProxyType(
                {str(key): str(value) for key, value in distinction.items()}
            ),
            review_digest=review_digest,
        )

    def assert_matches(
        self,
        *,
        candidate_id: str,
        candidate_kind: str,
        proposed_source_pathway_id: str,
        proposed_target_pathway_id: str,
        proposed_relation: str,
        invalid_relabel_conflict_ids: Sequence[str],
        invalid_relabel_blocked_claims: Sequence[str],
        mechanism_evidence: CandidateMechanismEvidence,
    ) -> None:
        """Require the trusted review to bind every load-bearing candidate fact."""

        expected_mechanism = {
            "mechanism_id": mechanism_evidence.mechanism_id,
            "path": mechanism_evidence.path,
            "sha256": mechanism_evidence.sha256,
        }
        if (
            self.candidate_id != candidate_id
            or self.candidate_kind != candidate_kind
            or self.proposed_source_pathway_id != proposed_source_pathway_id
            or self.proposed_target_pathway_id != proposed_target_pathway_id
            or self.proposed_relation != proposed_relation
            or self.invalid_relabel_conflict_ids
            != tuple(invalid_relabel_conflict_ids)
            or self.invalid_relabel_blocked_claims
            != tuple(invalid_relabel_blocked_claims)
            or dict(self.mechanism_evidence) != expected_mechanism
        ):
            raise InvalidCandidateError(
                "trusted structural-distinction review does not match candidate"
            )

    def to_record(self) -> dict[str, Any]:
        """Return the exact independently trusted review frozen into artifacts."""

        return {
            "artifact": "causal-pathway-candidate-relation-review",
            "schema_version": "causal_pathway_candidate_relation_review_v2",
            "review_id": self.review_id,
            "reviewer": self.reviewer,
            "review_status": "accepted_structural_distinction",
            "candidate_id": self.candidate_id,
            "candidate_kind": self.candidate_kind,
            "proposed_source_pathway_id": self.proposed_source_pathway_id,
            "proposed_target_pathway_id": self.proposed_target_pathway_id,
            "proposed_relation": self.proposed_relation,
            "invalid_relabel_conflict_ids": list(
                self.invalid_relabel_conflict_ids
            ),
            "invalid_relabel_blocked_claims": list(
                self.invalid_relabel_blocked_claims
            ),
            "mechanism_evidence": dict(self.mechanism_evidence),
            "source_result_parameter": self.source_result_parameter,
            "structural_distinction": dict(self.structural_distinction),
            "review_digest": self.review_digest,
        }


class _CandidateRequestInt(int):
    """Integer preserving one candidate-request value identity."""


class _CandidateRequestFloat(float):
    """Float preserving one candidate-request value identity."""


class _CandidateRequestStr(str):
    """String preserving one candidate-request value identity."""


def _candidate_request_payload(value: Any) -> Any:
    """Freeze one reviewed candidate mapping as a canonical JSON value."""

    if isinstance(value, Mapping):
        if any(not isinstance(key, str) or not key for key in value):
            raise _CandidateRequestError(
                "reviewed candidate request mappings require nonempty string keys"
            )
        return {
            key: _candidate_request_payload(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_candidate_request_payload(item) for item in value]
    if value is None or isinstance(value, (bool, int, float, str)):
        _canonical_value_digest(value)
        return value
    raise _CandidateRequestError(
        "reviewed candidate requests must contain only canonical JSON values"
    )


class _CandidateRequestMapping(Mapping[str, Any]):
    """Read-only mapping whose expanded values retain candidate provenance."""

    def __init__(
        self,
        value: Mapping[str, Any],
        *,
        root: _CandidateRequestMapping | None = None,
        path: tuple[str, ...] = (),
        normalized: bool = False,
    ) -> None:
        payload = dict(value) if normalized else _candidate_request_payload(value)
        self._payload = cast(dict[str, Any], payload)
        self._root = self if root is None else root
        self._path = path
        self._cache: dict[str, Any] = {}

    @property
    def root(self) -> _CandidateRequestMapping:
        return self._root

    def __len__(self) -> int:
        return len(self._payload)

    def __iter__(self) -> Iterator[str]:
        return iter(self._payload)

    def __getitem__(self, key: str) -> Any:
        if key in self._cache:
            return self._cache[key]
        value = self._payload[key]
        if isinstance(value, dict):
            exposed: Any = _CandidateRequestMapping(
                value,
                root=self._root,
                path=(*self._path, key),
                normalized=True,
            )
        elif type(value) is int:
            exposed = _CandidateRequestInt(value)
        elif type(value) is float:
            exposed = _CandidateRequestFloat(value)
        elif type(value) is str:
            exposed = _CandidateRequestStr(value)
        else:
            exposed = value
        self._cache[key] = exposed
        return exposed

    def _matching_request(
        self,
        keyword_arguments: Mapping[str, Any],
    ) -> tuple[tuple[str, ...], Mapping[str, Any]] | None:
        """Return the exact candidate submapping expanded into target kwargs."""

        if set(keyword_arguments) == set(self._payload) and all(
            type(self._payload[name]) not in {bool, type(None)}
            and keyword_arguments[name] is self[name]
            for name in self._payload
        ):
            return self._path, self._payload
        for name, value in self._payload.items():
            if not isinstance(value, dict):
                continue
            child = self[name]
            assert isinstance(child, _CandidateRequestMapping)
            if (match := child._matching_request(keyword_arguments)) is not None:
                return match
        return None


class VerifiedCandidateMechanism:
    """Exact executable link for one explicitly unregistered candidate."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        candidate_id: str,
        mechanism_id: str,
        symbol: SourceSymbolBinding,
        relation_review: CandidateRelationReview | None,
    ) -> None:
        if symbol.call_kind != "module_function":
            raise InvalidCandidateError(
                "candidate mechanisms must expose one module-function entrypoint"
            )
        target = _resolve_candidate_symbol(
            symbol,
            session.authority.repository_root,
            verify_source=False,
        )
        definition = _callable_definition(target)
        if (
            inspect.iscoroutinefunction(definition)
            or inspect.isasyncgenfunction(definition)
            or inspect.isgeneratorfunction(definition)
        ):
            raise InvalidCandidateError(
                "candidate mechanisms must execute as synchronous functions"
            )
        if (
            relation_review is not None
            and relation_review.source_result_parameter
            not in inspect.signature(target).parameters
        ):
            raise InvalidCandidateError(
                "reviewed candidate executable lacks its frozen source-result "
                "parameter"
            )
        if (
            relation_review is not None
            and _source_parameter_default_contract(
                definition,
                source_result_parameter=(
                    relation_review.source_result_parameter
                ),
            )
            is None
        ):
            raise InvalidCandidateError(
                "reviewed candidate source-result parameter requires one safe "
                "frozen omission default"
            )
        self._runtime = session._candidate_runtime()
        self._candidate_id = candidate_id
        self._mechanism_id = mechanism_id
        self._symbol = symbol
        self._relation_review = relation_review
        self._target = target
        self._expected_definition = definition
        try:
            self._identity_guard = session._callable_identity_guard(
                symbol,
                target,
            )
        except SymbolBindingError as exc:
            raise InvalidCandidateError(
                "candidate executable symbol is absent, stale, or inconsistent"
            ) from exc
        self._callable_identity = self._identity_guard.identity
        self.__name__ = getattr(target, "__name__", symbol.qualified_symbol)
        self.__doc__ = getattr(target, "__doc__", None)
        self.__signature__ = inspect.signature(target)

    @property
    def symbol_id(self) -> str:
        return self._symbol.symbol_id

    def source_dependency_proof(
        self,
        request_path: Sequence[str],
    ) -> dict[str, Any] | None:
        """Prove source-sensitive construction of one exact target request."""

        if self._relation_review is None:
            return None
        return _source_dependent_request_proof(
            self._expected_definition,
            source_result_parameter=(
                self._relation_review.source_result_parameter
            ),
            request_path=request_path,
        )

    @property
    def link_record(self) -> Mapping[str, Any]:
        """Return the executable identity frozen into the candidate declaration."""

        return MappingProxyType(
            {
                "mechanism_id": self._mechanism_id,
                "symbol_id": self._symbol.symbol_id,
                "module": self._symbol.module,
                "qualified_symbol": self._symbol.qualified_symbol,
                "binding_role": self._symbol.binding_role,
                "call_kind": self._symbol.call_kind,
                "source_path": self._symbol.source_path,
                "source_sha256": self._symbol.source_sha256,
                "callable_identity": self._callable_identity.to_record(),
            }
        )

    def _assert_current_callable(self) -> tuple[Callable[..., Any], Mapping[str, Any]]:
        if _callable_definition(self._target) is not self._expected_definition:
            raise SymbolBindingError(
                f"candidate mechanism {self.symbol_id!r} callable identity changed"
            )
        current_identity = self._identity_guard.assert_current(self._target)
        return self._target, current_identity

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        scope = self._runtime.authorize_candidate_mechanism(
            candidate_id=self._candidate_id,
            symbol_id=self.symbol_id,
        )
        target, callable_identity = self._assert_current_callable()
        try:
            bound_arguments = dict(
                inspect.signature(target).bind(*args, **kwargs).arguments
            )
        except TypeError:
            bound_arguments = {}
        try:
            result = target(*args, **kwargs)
        except Exception as exc:
            runtime_object_flow = self._runtime.observe_object_flow(
                target=target,
                arguments=bound_arguments,
                result=None,
            )
            self._runtime.record_candidate_mechanism_event(
                scope,
                _CandidateMechanismEvent(
                    candidate_id=self._candidate_id,
                    mechanism_id=self._mechanism_id,
                    symbol_id=self.symbol_id,
                    outcome="raised",
                    result_type=None,
                    error_type=type(exc).__name__,
                    callable_identity=callable_identity,
                    relation_review_digest=(
                        self._relation_review.review_digest
                        if self._relation_review is not None
                        else None
                    ),
                    structural_result_observed=(
                        False if self._relation_review is not None else None
                    ),
                    runtime_object_flow=runtime_object_flow,
                ),
                result=None,
            )
            raise
        structurally_distinct_mapping = (
            isinstance(result, Mapping)
            and bool(result)
            and all(result is not argument for argument in (*args, *kwargs.values()))
            if self._relation_review is not None
            else False
        )
        exposed_result = result
        structural_result_observed: bool | None = None
        if self._relation_review is not None:
            if structurally_distinct_mapping:
                try:
                    exposed_result = _CandidateRequestMapping(result)
                except _CandidateRequestError:
                    exposed_result = result
            structural_result_observed = isinstance(
                exposed_result,
                _CandidateRequestMapping,
            )
        runtime_object_flow = self._runtime.observe_object_flow(
            target=target,
            arguments=bound_arguments,
            result=exposed_result,
        )
        self._runtime.record_candidate_mechanism_event(
            scope,
            _CandidateMechanismEvent(
                candidate_id=self._candidate_id,
                mechanism_id=self._mechanism_id,
                symbol_id=self.symbol_id,
                outcome="returned",
                result_type=type(exposed_result).__name__,
                error_type=None,
                callable_identity=callable_identity,
                relation_review_digest=(
                    self._relation_review.review_digest
                    if self._relation_review is not None
                    else None
                ),
                structural_result_observed=structural_result_observed,
                runtime_object_flow=runtime_object_flow,
            ),
            result=exposed_result,
        )
        return exposed_result


def _candidate_target_request_flow(
    *,
    candidate: CandidateDeclaration,
    scope_id: str,
    mechanism_events: Sequence[Mapping[str, Any]],
    mechanism: VerifiedCandidateMechanism,
    binding_id: str,
    pathway_id: str,
    symbol_id: str,
    positional_arguments: Sequence[Any],
    keyword_arguments: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Attest one exact reviewed-candidate mapping expansion."""

    if (
        candidate.invalid_relabel_relation_review is None
        or candidate.candidate_kind != "composition"
        or pathway_id != candidate.proposed_target_pathway_id
        or positional_arguments
    ):
        return None
    returned = [
        event
        for event in mechanism_events
        if event["record"].outcome == "returned"
    ]
    if len(returned) != 1:
        return None
    mechanism_event = returned[0]
    result = mechanism_event["result"]
    if not isinstance(result, _CandidateRequestMapping):
        return None
    match = result._matching_request(keyword_arguments)
    if match is None:
        return None
    request_path, request_payload = match
    request_digest = _canonical_value_digest(request_payload)
    if request_digest != _canonical_value_digest(dict(keyword_arguments)):
        return None
    dependency_proof = mechanism.source_dependency_proof(request_path)
    if (
        dependency_proof is None
        or dependency_proof["source_present_request_digest"] != request_digest
    ):
        return None
    result_descriptor = mechanism_event["record"].runtime_object_flow.get("result")
    if not isinstance(result_descriptor, Mapping):
        return None
    return {
        "schema_version": "reviewed_candidate_target_request_flow_v1",
        "binding_rule": (
            "candidate_result_mapping_supplies_complete_target_keyword_request"
        ),
        "candidate_scope_id": scope_id,
        "candidate_id": candidate.candidate_id,
        "candidate_mechanism_invocation_index": mechanism_event["record_index"],
        "candidate_result": dict(result_descriptor),
        "candidate_result_request_path": list(request_path),
        "candidate_result_request_digest": request_digest,
        "target_bound_arguments_digest": request_digest,
        "source_dependency_proof": dependency_proof,
        "target_binding_id": binding_id,
        "target_pathway_id": pathway_id,
        "target_symbol_id": symbol_id,
    }


def _reviewed_candidate_dataflow_witness(
    *,
    source_events: Sequence[Mapping[str, Any]],
    target_events: Sequence[Mapping[str, Any]],
    mechanism_event: Mapping[str, Any],
    source_result_parameter: str,
) -> dict[str, Any] | None:
    """Reconstruct source-result to candidate-result to target-request flow."""

    mechanism_record = mechanism_event["record"]
    mechanism_flow = mechanism_record.runtime_object_flow
    candidate_arguments = mechanism_flow.get("arguments")
    candidate_result = mechanism_flow.get("result")
    if not isinstance(candidate_arguments, Mapping) or not isinstance(
        candidate_result,
        Mapping,
    ):
        return None
    for source_event in source_events:
        source_result = source_event["record"].runtime_object_flow.get("result")
        if not isinstance(source_result, Mapping):
            continue
        if candidate_arguments.get(source_result_parameter) != source_result:
            continue
        for target_event in target_events:
            request_flow = target_event["record"].candidate_request_flow
            if not isinstance(request_flow, Mapping):
                continue
            if not (
                request_flow.get("candidate_scope_id")
                == mechanism_record.candidate_scope_id
                and request_flow.get("candidate_id")
                == mechanism_record.candidate_id
                and request_flow.get("candidate_mechanism_invocation_index")
                == mechanism_event["record_index"]
                and request_flow.get("candidate_result") == candidate_result
                and request_flow.get("target_bound_arguments_digest")
                == request_flow.get("candidate_result_request_digest")
            ):
                continue
            return {
                "witness_kind": "externally_attested_candidate_request_flow",
                "source_invocation_index": source_event["record_index"],
                "source_result": dict(source_result),
                "candidate_argument_name": source_result_parameter,
                "candidate_mechanism_invocation_index": mechanism_event[
                    "record_index"
                ],
                "candidate_result": dict(candidate_result),
                "candidate_result_request_path": list(
                    request_flow["candidate_result_request_path"]
                ),
                "target_invocation_index": target_event["record_index"],
                "target_request_digest": request_flow["target_bound_arguments_digest"],
            }
    return None


def _candidate_exercise_witness(
    *,
    candidate: CandidateDeclaration,
    scope_id: str,
    completed: bool,
    events: Sequence[Mapping[str, Any]],
    mechanism_events: Sequence[Mapping[str, Any]],
) -> dict[str, Any] | None:
    """Return evidence only for completed, returned constituent execution."""

    if not completed:
        return None
    qualifying = [
        event for event in events if event["record"].claim_qualifying_effect
    ]
    returned_mechanism_events = [
        event
        for event in mechanism_events
        if event["record"].outcome == "returned"
    ]
    if len(returned_mechanism_events) != 1:
        return None
    mechanism_event = returned_mechanism_events[0]
    mechanism_record = mechanism_event["record"]
    relation_review = candidate.invalid_relabel_relation_review
    if relation_review is not None and (
        mechanism_record.relation_review_digest != relation_review.review_digest
        or mechanism_record.structural_result_observed is not True
    ):
        return None
    if candidate.candidate_kind == "pathway":
        if candidate.consumed_pathway_ids and not qualifying:
            return None
        return {
            "candidate_scope_id": scope_id,
            "candidate_id": candidate.candidate_id,
            "witness_kind": "identity_verified_candidate_mechanism_execution",
            "candidate_mechanism_invocation_index": mechanism_event["record_index"],
            "candidate_mechanism_symbol_id": mechanism_record.symbol_id,
            "constituent_invocation_indices": [
                event["record_index"] for event in qualifying
            ],
        }

    source_id = candidate.proposed_source_pathway_id
    target_id = candidate.proposed_target_pathway_id
    source_events = [
        event for event in qualifying if event["record"].pathway_id == source_id
    ]
    target_events = [
        event for event in qualifying if event["record"].pathway_id == target_id
    ]
    if source_id == target_id:
        if len(source_events) < 2:
            return None
        target_events = source_events[1:]
        source_events = source_events[:1]
    if not source_events or not target_events:
        return None
    if max(event["event_order"] for event in source_events) >= min(
        event["event_order"] for event in target_events
    ):
        return None
    if not (
        max(event["event_order"] for event in source_events)
        < mechanism_event["event_order"]
        < min(event["event_order"] for event in target_events)
    ):
        return None
    candidate_dataflow_witness = None
    if relation_review is not None:
        candidate_dataflow_witness = _reviewed_candidate_dataflow_witness(
            source_events=source_events,
            target_events=target_events,
            mechanism_event=mechanism_event,
            source_result_parameter=relation_review.source_result_parameter,
        )
        if candidate_dataflow_witness is None:
            return None
    return {
        "candidate_scope_id": scope_id,
        "candidate_id": candidate.candidate_id,
        "witness_kind": "identity_verified_candidate_crossing_execution",
        "candidate_mechanism_invocation_index": mechanism_event["record_index"],
        "candidate_mechanism_symbol_id": mechanism_record.symbol_id,
        "source_pathway_id": source_id,
        "source_binding_id": source_events[0]["record"].binding_id,
        "source_invocation_indices": [
            event["record_index"] for event in source_events
        ],
        "target_pathway_id": target_id,
        "target_binding_id": target_events[0]["record"].binding_id,
        "target_invocation_indices": [
            event["record_index"] for event in target_events
        ],
        "ordering_rule": (
            "all_source_invocations_before_candidate_mechanism_before_"
            "all_target_invocations"
        ),
        **(
            {"candidate_dataflow_witness": candidate_dataflow_witness}
            if candidate_dataflow_witness is not None
            else {}
        ),
    }


@dataclass(frozen=True)
class CandidateUseRecord:
    """Explicit evidence that a declared candidate relation was exercised."""

    candidate_id: str
    mechanism_evidence: Mapping[str, str]
    execution_witness: Mapping[str, Any]


def _build_candidate_declaration(
    *,
    session: PathwayBindingSession,
    authority_provider: CausalPathwayAuthority,
    existing_candidate_ids: Collection[str],
    executable_composition_statuses: Collection[str],
    candidate_id: str,
    candidate_kind: str,
    purpose: str,
    owner: str,
    consumed_pathway_ids: Sequence[str],
    consumed_composition_ids: Sequence[str],
    proposed_source_pathway_id: str | None,
    proposed_target_pathway_id: str | None,
    proposed_relation: str | None,
    authority: Mapping[str, str] | None,
    producer_residue: Sequence[str],
    adapter_residue: Sequence[str],
    configured_residue: Sequence[str],
    evidence_owner: str,
    mechanism_evidence: Mapping[str, Any] | None,
    invalid_relabel_relation_review: Mapping[str, Any] | None,
    trusted_relation_review_digest: str | None,
    blocked_claims: Sequence[str],
) -> tuple[CandidateDeclaration, VerifiedCandidateMechanism | None]:
    """Validate and build one declaration plus its optional executable handle."""

    if not candidate_id or candidate_id in existing_candidate_ids:
        raise InvalidCandidateError("candidate_id must be non-empty and unique")
    try:
        authority_provider.pathway(candidate_id)
    except UnknownPathwayError:
        pass
    else:
        raise InvalidCandidateError("candidate ID collides with an admitted pathway")
    try:
        authority_provider.composition(candidate_id)
    except UnknownCompositionError:
        pass
    else:
        raise InvalidCandidateError(
            "candidate ID collides with a registered composition"
        )
    if candidate_kind not in {"pathway", "composition"}:
        raise InvalidCandidateError("candidate_kind must be pathway or composition")
    if not purpose or not owner or not evidence_owner:
        raise InvalidCandidateError(
            "purpose, owner, and evidence_owner are required"
        )
    consumed_pathways = tuple(dict.fromkeys(consumed_pathway_ids))
    consumed_compositions = tuple(dict.fromkeys(consumed_composition_ids))
    for pathway_id in consumed_pathways:
        authority_provider.pathway(pathway_id)
    for composition_id in consumed_compositions:
        composition = authority_provider.composition(composition_id)
        if composition["composition_status"] not in executable_composition_statuses:
            raise InvalidCandidateError(
                f"candidate cannot consume non-executable composition {composition_id}"
            )
    parsed_evidence = (
        CandidateMechanismEvidence.from_record(mechanism_evidence)
        if mechanism_evidence is not None
        else None
    )
    mechanism_handle: VerifiedCandidateMechanism | None = None
    parsed_relation_review: CandidateRelationReview | None = None
    invalid_relabel_conflicts: tuple[Mapping[str, Any], ...] = ()
    if candidate_kind == "composition":
        if not proposed_source_pathway_id or not proposed_target_pathway_id:
            raise InvalidCandidateError(
                "composition candidates require explicit source and target pathways"
            )
        authority_provider.pathway(proposed_source_pathway_id)
        authority_provider.pathway(proposed_target_pathway_id)
        if not proposed_relation:
            raise InvalidCandidateError(
                "composition candidate requires a genuinely new relation description"
            )
        if (
            proposed_source_pathway_id not in consumed_pathways
            or proposed_target_pathway_id not in consumed_pathways
        ):
            raise InvalidCandidateError(
                "composition candidate endpoints must be explicit consumed "
                "admitted pathways"
            )
        invalid_relabel_conflicts = authority_provider.invalid_relabels_for_endpoints(
            proposed_source_pathway_id,
            proposed_target_pathway_id,
        )
        blocked_relabels = {
            str(relabel)
            for composition in invalid_relabel_conflicts
            for relabel in composition["blocked_relabels"]
        }
        restated = sorted(
            relabel
            for relabel in blocked_relabels
            if _restates_blocked_relabel(proposed_relation, relabel)
        )
        if restated:
            raise InvalidCandidateError(
                "candidate relation restates registered invalid relabels: "
                f"{restated}"
            )
        if invalid_relabel_conflicts and parsed_evidence is None:
            missing_mechanism_conflict_ids = sorted(
                str(item["composition_id"]) for item in invalid_relabel_conflicts
            )
            raise InvalidCandidateError(
                "candidate endpoint pair conflicts with invalid relabel rows "
                f"{missing_mechanism_conflict_ids}; distinct executable candidate mechanism "
                "evidence is required"
            )
        if invalid_relabel_conflicts and invalid_relabel_relation_review is None:
            raise InvalidCandidateError(
                "candidate endpoint pair conflicts with invalid relabel rows; "
                "an independently trusted structural-distinction review is required"
            )
        if not invalid_relabel_conflicts and invalid_relabel_relation_review is not None:
            raise InvalidCandidateError(
                "invalid-relabel relation reviews are only valid for conflicting "
                "endpoint pairs"
            )
        if invalid_relabel_conflicts and parsed_evidence is not None:
            reserved_ids = {
                str(item["composition_id"]) for item in invalid_relabel_conflicts
            }
            if parsed_evidence.mechanism_id in reserved_ids:
                raise InvalidCandidateError(
                    "candidate mechanism identity must be distinct from the "
                    "conflicting invalid composition"
                )
    if parsed_evidence is not None:
        executable_symbol = parsed_evidence.assert_current(
            authority_provider.repository_root,
            candidate_kind=candidate_kind,
            proposed_source_pathway_id=proposed_source_pathway_id,
            proposed_target_pathway_id=proposed_target_pathway_id,
            proposed_relation=proposed_relation,
        )
        if authority_provider.callable_is_registered(executable_symbol):
            raise InvalidCandidateError(
                "candidate executable must be distinct from every admitted "
                "stage and registered crossing callable"
            )
        if invalid_relabel_conflicts:
            assert invalid_relabel_relation_review is not None
            parsed_relation_review = CandidateRelationReview.from_record(
                invalid_relabel_relation_review,
                trusted_digest=trusted_relation_review_digest,
            )
            conflict_ids = tuple(
                str(item["composition_id"])
                for item in invalid_relabel_conflicts
            )
            invalid_blocks = tuple(
                dict.fromkeys(
                    str(relabel)
                    for composition in invalid_relabel_conflicts
                    for relabel in composition["blocked_relabels"]
                )
            )
            parsed_relation_review.assert_matches(
                candidate_id=candidate_id,
                candidate_kind=candidate_kind,
                proposed_source_pathway_id=str(proposed_source_pathway_id),
                proposed_target_pathway_id=str(proposed_target_pathway_id),
                proposed_relation=str(proposed_relation),
                invalid_relabel_conflict_ids=conflict_ids,
                invalid_relabel_blocked_claims=invalid_blocks,
                mechanism_evidence=parsed_evidence,
            )
        mechanism_handle = VerifiedCandidateMechanism(
            session=session,
            candidate_id=candidate_id,
            mechanism_id=parsed_evidence.mechanism_id,
            symbol=executable_symbol,
            relation_review=parsed_relation_review,
        )
    raw_authority = dict(authority or {})
    unknown_coordinates = sorted(set(raw_authority) - set(AUTHORITY_COORDINATES))
    if unknown_coordinates:
        raise InvalidCandidateError(
            f"unknown authority coordinates: {unknown_coordinates}"
        )
    resolved_authority = {
        coordinate: str(raw_authority.get(coordinate) or "unresolved")
        for coordinate in AUTHORITY_COORDINATES
    }
    blocked = tuple(
        dict.fromkeys(
            (
                *blocked_claims,
                *(
                    str(relabel)
                    for composition in invalid_relabel_conflicts
                    for relabel in composition["blocked_relabels"]
                ),
                "candidate relation is admitted",
                "candidate relation is native",
                "candidate declaration is promotion",
            )
        )
    )
    declaration = CandidateDeclaration(
        _session=session,
        candidate_id=candidate_id,
        candidate_kind=candidate_kind,
        purpose=purpose,
        owner=owner,
        consumed_pathway_ids=consumed_pathways,
        consumed_composition_ids=consumed_compositions,
        proposed_source_pathway_id=proposed_source_pathway_id,
        proposed_target_pathway_id=proposed_target_pathway_id,
        proposed_relation=proposed_relation,
        authority=MappingProxyType(resolved_authority),
        producer_residue=tuple(producer_residue),
        adapter_residue=tuple(adapter_residue),
        configured_residue=tuple(configured_residue),
        evidence_owner=evidence_owner,
        blocked_claims=blocked,
        mechanism_evidence=parsed_evidence,
        mechanism_link=(
            mechanism_handle.link_record if mechanism_handle is not None else None
        ),
        invalid_relabel_conflict_ids=tuple(
            str(item["composition_id"]) for item in invalid_relabel_conflicts
        ),
        invalid_relabel_blocked_claims=tuple(
            dict.fromkeys(
                str(relabel)
                for composition in invalid_relabel_conflicts
                for relabel in composition["blocked_relabels"]
            )
        ),
        invalid_relabel_relation_review=parsed_relation_review,
    )
    return declaration, mechanism_handle


__all__ = [
    "AUTHORITY_COORDINATES",
    "INVALID_RELABEL_CANDIDATE_REVIEW_TRUST_REQUIREMENT",
    "CandidateDeclaration",
    "CandidateMechanismEvidence",
    "CandidateRelationReview",
    "CandidateUseRecord",
    "InvalidCandidateError",
]

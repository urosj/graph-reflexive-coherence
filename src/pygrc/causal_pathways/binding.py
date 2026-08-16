"""Exact causal-pathway linkage for evidence-bearing consumers.

This module links declared knowledge-plane identities to current Python
callables.  It deliberately does not select pathways or dispatch causal work.
"""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, field, replace
from pathlib import Path
from types import MappingProxyType, TracebackType
from typing import Any, Final, Literal, Self, cast

AUTHORITY_PATHS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "registry": "specs/grc-lgrc-causal-pathway-contracts.json",
        "crosswalk": "specs/grc-lgrc-causal-pathway-evidence-crosswalk.json",
        "matrix": "specs/grc-lgrc-causal-pathway-composition-matrix.json",
        "selector": "specs/grc-lgrc-causal-pathway-selection-guide.json",
        "policy": "specs/grc-lgrc-causal-pathway-conformance.json",
        "bindings": "specs/grc-lgrc-causal-pathway-bindings.json",
    }
)

EXECUTABLE_COMPOSITION_STATUSES: Final[frozenset[str]] = frozenset(
    {
        "lawful_native",
        "lawful_with_explicit_adapter",
        "diagnostic_only",
        "producer_mediated",
    }
)

AUTHORITY_COORDINATES: Final[tuple[str, ...]] = (
    "direction",
    "funding",
    "eligibility",
    "scheduling",
    "commit",
    "reception",
)

CLAIM_SCOPE_BOUND_INVOCATIONS: Final[str] = "bound_invocations_only"
UNTRACKED_EXECUTION_STATUS: Final[str] = "not_observable_by_binding_plane"


class CausalPathwayBindingError(ValueError):
    """Base error for fail-closed binding operations."""


class AuthorityDriftError(CausalPathwayBindingError):
    """Raised when a knowledge or source-link authority no longer matches."""


class UnknownPathwayError(CausalPathwayBindingError):
    """Raised when a pathway is absent from the admitted registry."""


class UnknownCompositionError(CausalPathwayBindingError):
    """Raised when a composition is absent from the admitted matrix."""


class UnbindableCompositionError(CausalPathwayBindingError):
    """Raised when a registered row is missing or an invalid relabel."""


class InvalidCandidateError(CausalPathwayBindingError):
    """Raised when an unregistered candidate hides identity or authority debt."""


class SymbolBindingError(CausalPathwayBindingError):
    """Raised when an exact stage symbol cannot be linked safely."""


class BindingStateError(CausalPathwayBindingError):
    """Raised when declaration, locking, use, and sealing order is violated."""


def canonical_digest(value: Mapping[str, Any], *, excluding: str) -> str:
    """Return the repository's canonical SHA-256 digest for one JSON object."""

    payload = {key: item for key, item in value.items() if key != excluding}
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized_claim_text(value: str) -> str:
    """Normalize claim labels so punctuation cannot hide a blocked relabel."""

    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AuthorityDriftError(f"authority {path} must contain a JSON object")
    return value


def _index_unique(
    records: Iterable[Mapping[str, Any]],
    *,
    key: str,
    authority_name: str,
) -> dict[str, Mapping[str, Any]]:
    index: dict[str, Mapping[str, Any]] = {}
    for record in records:
        identity = str(record.get(key, ""))
        if not identity or identity in index:
            raise AuthorityDriftError(
                f"{authority_name} has a missing or duplicate {key}: {identity!r}"
            )
        index[identity] = record
    return index


def _callable_definition(target: Callable[..., Any]) -> Callable[..., Any]:
    """Return the underlying Python definition for a callable or bound method."""

    definition = getattr(target, "__func__", target)
    return cast(Callable[..., Any], inspect.unwrap(definition))


def _callable_bound_owner(target: Callable[..., Any]) -> object | None:
    """Return the instance/class owner carried by a bound method."""

    return getattr(target, "__self__", None)


@dataclass(frozen=True)
class CallableIdentity:
    """Content-addressed identity for one resolved mechanism callable."""

    module: str
    qualified_symbol: str
    source_path: str
    source_sha256: str
    definition_first_line: int
    definition_source_sha256: str

    def to_record(self) -> dict[str, Any]:
        """Return the canonical identity record frozen into locks and receipts."""

        record: dict[str, Any] = {
            "module": self.module,
            "qualified_symbol": self.qualified_symbol,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "definition_first_line": self.definition_first_line,
            "definition_source_sha256": self.definition_source_sha256,
            "callable_identity_digest": "",
        }
        record["callable_identity_digest"] = canonical_digest(
            record,
            excluding="callable_identity_digest",
        )
        return record


@dataclass(frozen=True)
class SourceSymbolBinding:
    """One exact stage-to-source link from the machine binding map."""

    symbol_id: str
    module: str
    qualified_symbol: str
    binding_role: str
    call_kind: str
    source_path: str
    source_sha256: str
    required_keyword_arguments: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> SourceSymbolBinding:
        required = record.get("required_keyword_arguments", {})
        if not isinstance(required, Mapping):
            raise AuthorityDriftError("required_keyword_arguments must be a mapping")
        return cls(
            symbol_id=str(record["symbol_id"]),
            module=str(record["module"]),
            qualified_symbol=str(record["qualified_symbol"]),
            binding_role=str(record["binding_role"]),
            call_kind=str(record["call_kind"]),
            source_path=str(record["source_path"]),
            source_sha256=str(record["source_sha256"]),
            required_keyword_arguments=MappingProxyType(dict(required)),
        )

    def callable_identity(
        self,
        target: Callable[..., Any],
        repository_root: Path,
    ) -> CallableIdentity:
        """Validate and describe a resolved callable against its source link."""

        definition = _callable_definition(target)
        module = str(getattr(definition, "__module__", ""))
        qualified_symbol = str(getattr(definition, "__qualname__", ""))
        if module != self.module or qualified_symbol != self.qualified_symbol:
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} resolved as "
                f"{module}.{qualified_symbol}, expected "
                f"{self.module}.{self.qualified_symbol}"
            )

        source_file = inspect.getsourcefile(definition)
        if source_file is None:
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} has no inspectable source file"
            )
        expected_source = (repository_root / self.source_path).resolve()
        actual_source = Path(source_file).resolve()
        if actual_source != expected_source:
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} resolved from {actual_source}, "
                f"expected {expected_source}"
            )
        if sha256_file(actual_source) != self.source_sha256:
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} source content is stale"
            )
        try:
            source_lines, first_line = inspect.getsourcelines(definition)
        except (OSError, TypeError) as exc:
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} definition is not inspectable"
            ) from exc
        definition_source = "".join(source_lines).encode("utf-8")
        return CallableIdentity(
            module=module,
            qualified_symbol=qualified_symbol,
            source_path=self.source_path,
            source_sha256=self.source_sha256,
            definition_first_line=first_line,
            definition_source_sha256=hashlib.sha256(definition_source).hexdigest(),
        )

    def resolve(self, repository_root: Path | None = None) -> Callable[..., Any]:
        """Import and identity-check the exact callable recorded by this link."""

        target: Any = importlib.import_module(self.module)
        try:
            for part in self.qualified_symbol.split("."):
                target = getattr(target, part)
        except AttributeError as exc:
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} no longer resolves"
            ) from exc
        if not callable(target):
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} is no longer callable"
            )
        resolved = cast(Callable[..., Any], target)
        definition = _callable_definition(resolved)
        actual_identity = (
            str(getattr(definition, "__module__", "")),
            str(getattr(definition, "__qualname__", "")),
        )
        if actual_identity != (self.module, self.qualified_symbol):
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} resolved as "
                f"{actual_identity[0]}.{actual_identity[1]}, expected "
                f"{self.module}.{self.qualified_symbol}"
            )
        if repository_root is not None:
            self.callable_identity(resolved, repository_root)
        return resolved


@dataclass(frozen=True)
class CompositionCrossingBinding:
    """Concrete crossing callable for a registered explicit-adapter row."""

    composition_id: str
    crossing_kind: str
    source_pathway_id: str
    source_argument_name: str
    target_pathway_id: str
    symbol: SourceSymbolBinding

    @classmethod
    def from_record(
        cls,
        record: Mapping[str, Any],
    ) -> CompositionCrossingBinding:
        return cls(
            composition_id=str(record["composition_id"]),
            crossing_kind=str(record["crossing_kind"]),
            source_pathway_id=str(record["source_pathway_id"]),
            source_argument_name=str(record["source_argument_name"]),
            target_pathway_id=str(record["target_pathway_id"]),
            symbol=SourceSymbolBinding.from_record(record["symbol"]),
        )


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
    invalid_relabel_conflict_ids: tuple[str, ...]
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
            "invalid_relabel_conflict_ids": list(self.invalid_relabel_conflict_ids),
            "claim_ceiling": self.claim_ceiling,
            "blocked_claims": list(self.blocked_claims),
            "promotion_status": self.promotion_status,
        }

    def evidence_scope(self) -> CandidateExecutionScope:
        """Return an explicit observed-use scope for this candidate."""

        return CandidateExecutionScope(session=self._session, candidate=self)


@dataclass(frozen=True)
class CandidateMechanismEvidence:
    """Pre-lock content address for a candidate-specific mechanism artifact."""

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
        if evidence.evidence_kind != "content_addressed_artifact":
            raise InvalidCandidateError(
                "candidate mechanism evidence must be content_addressed_artifact"
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
    ) -> None:
        """Validate the address and candidate semantics of the evidence artifact."""

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
            artifact = _load_json(target)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise InvalidCandidateError(
                "candidate mechanism evidence must be a JSON artifact"
            ) from exc
        expected = {
            "artifact": "causal-pathway-candidate-mechanism-evidence",
            "schema_version": "causal_pathway_candidate_mechanism_evidence_v1",
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


@dataclass(frozen=True)
class AllowedPathwayAlternatives:
    """Declared dynamic alternatives; it contains no selection operation."""

    alternative_set_id: str
    pathway_ids: tuple[str, ...]
    selection_authority: str


class CausalPathwayAuthority:
    """Validated immutable view over accepted knowledge and binding artifacts."""

    def __init__(
        self,
        *,
        repository_root: Path,
        documents: Mapping[str, Mapping[str, Any]],
        pathways: Mapping[str, Mapping[str, Any]],
        compositions: Mapping[str, Mapping[str, Any]],
        stage_symbols: Mapping[tuple[str, str], tuple[SourceSymbolBinding, ...]],
        composition_crossings: Mapping[str, CompositionCrossingBinding],
    ) -> None:
        self._repository_root = repository_root
        self._documents = MappingProxyType(dict(documents))
        self._pathways = MappingProxyType(dict(pathways))
        self._compositions = MappingProxyType(dict(compositions))
        self._stage_symbols = MappingProxyType(dict(stage_symbols))
        self._composition_crossings = MappingProxyType(dict(composition_crossings))

    @property
    def repository_root(self) -> Path:
        return self._repository_root

    @property
    def registry_digest(self) -> str:
        return str(self._documents["registry"]["registry_digest"])

    @property
    def crosswalk_digest(self) -> str:
        return str(self._documents["crosswalk"]["crosswalk_digest"])

    @property
    def matrix_digest(self) -> str:
        return str(self._documents["matrix"]["matrix_digest"])

    @property
    def selector_digest(self) -> str:
        return str(self._documents["selector"]["selector_digest"])

    @property
    def policy_digest(self) -> str:
        return str(self._documents["policy"]["policy_digest"])

    @property
    def binding_map_digest(self) -> str:
        return str(self._documents["bindings"]["binding_map_digest"])

    @property
    def source_revision(self) -> str:
        return str(self._documents["bindings"]["source_revision"])

    def artifact_identities(self) -> Mapping[str, str]:
        """Return the accepted digests consumed by one binding lock."""

        return MappingProxyType(
            {
                "source_revision": self.source_revision,
                "registry_digest": self.registry_digest,
                "crosswalk_digest": self.crosswalk_digest,
                "matrix_digest": self.matrix_digest,
                "selector_digest": self.selector_digest,
                "binding_map_digest": self.binding_map_digest,
                "conformance_policy_digest": self.policy_digest,
            }
        )

    def assert_current(self) -> None:
        """Fail closed if any consumed authority or source link has drifted."""

        current = type(self).load(self.repository_root)
        if dict(current.artifact_identities()) != dict(self.artifact_identities()):
            raise AuthorityDriftError(
                "loaded causal-pathway authority is no longer current"
            )

    def pathway(self, pathway_id: str) -> Mapping[str, Any]:
        try:
            return deepcopy(self._pathways[pathway_id])
        except KeyError as exc:
            raise UnknownPathwayError(
                f"pathway {pathway_id!r} is not admitted; declare a candidate instead"
            ) from exc

    def composition(self, composition_id: str) -> Mapping[str, Any]:
        try:
            return deepcopy(self._compositions[composition_id])
        except KeyError as exc:
            raise UnknownCompositionError(
                f"composition {composition_id!r} is not registered; "
                "declare a candidate instead"
            ) from exc

    def invalid_relabels_for_endpoints(
        self,
        source_pathway_id: str,
        target_pathway_id: str,
    ) -> tuple[Mapping[str, Any], ...]:
        """Return every registered invalid relabel for an exact endpoint pair."""

        return tuple(
            deepcopy(composition)
            for composition in self._compositions.values()
            if composition["composition_status"] == "invalid_relabel"
            and composition["from_pathway_id"] == source_pathway_id
            and composition["to_pathway_id"] == target_pathway_id
        )

    def stage_ids(self, pathway_id: str) -> tuple[str, ...]:
        pathway = self.pathway(pathway_id)
        return tuple(str(stage["stage_id"]) for stage in pathway["stage_sequence"])

    def symbols(
        self,
        pathway_id: str,
        stage_id: str,
    ) -> tuple[SourceSymbolBinding, ...]:
        self.pathway(pathway_id)
        try:
            return self._stage_symbols[(pathway_id, stage_id)]
        except KeyError as exc:
            raise SymbolBindingError(
                f"stage {pathway_id}:{stage_id} has no current binding"
            ) from exc

    def composition_crossing(
        self,
        composition_id: str,
    ) -> CompositionCrossingBinding:
        """Return the registered concrete crossing for an adapter composition."""

        self.composition(composition_id)
        try:
            return self._composition_crossings[composition_id]
        except KeyError as exc:
            raise SymbolBindingError(
                f"composition {composition_id!r} has no explicit crossing callable"
            ) from exc

    @classmethod
    def load(cls, repository_root: str | Path) -> CausalPathwayAuthority:
        """Load and validate all accepted knowledge and linkage artifacts."""

        root = Path(repository_root).resolve()
        documents = {
            name: _load_json(root / relative)
            for name, relative in AUTHORITY_PATHS.items()
        }
        digest_fields = {
            "registry": "registry_digest",
            "crosswalk": "crosswalk_digest",
            "matrix": "matrix_digest",
            "selector": "selector_digest",
            "policy": "policy_digest",
            "bindings": "binding_map_digest",
        }
        for name, digest_field in digest_fields.items():
            actual = canonical_digest(documents[name], excluding=digest_field)
            expected = str(documents[name].get(digest_field, ""))
            if actual != expected:
                raise AuthorityDriftError(
                    f"{name} digest mismatch: expected {expected}, got {actual}"
                )

        bindings = documents["bindings"]
        consumed_digests = {
            "registry_digest": documents["registry"]["registry_digest"],
            "crosswalk_digest": documents["crosswalk"]["crosswalk_digest"],
            "matrix_digest": documents["matrix"]["matrix_digest"],
            "selector_digest": documents["selector"]["selector_digest"],
            "policy_digest": documents["policy"]["policy_digest"],
        }
        for field_name, actual in consumed_digests.items():
            if bindings.get(field_name) != actual:
                raise AuthorityDriftError(f"binding map consumes stale {field_name}")

        pathways = _index_unique(
            documents["registry"]["pathways"],
            key="pathway_id",
            authority_name="registry",
        )
        compositions = _index_unique(
            documents["matrix"]["compositions"],
            key="composition_id",
            authority_name="matrix",
        )
        expected_stages = {
            (pathway_id, str(stage["stage_id"]))
            for pathway_id, pathway in pathways.items()
            for stage in pathway["stage_sequence"]
        }
        stage_symbols: dict[tuple[str, str], tuple[SourceSymbolBinding, ...]] = {}
        symbol_ids: set[str] = set()
        for stage_record in bindings["stage_bindings"]:
            key = (
                str(stage_record["pathway_id"]),
                str(stage_record["stage_id"]),
            )
            if key in stage_symbols:
                raise AuthorityDriftError(f"duplicate binding stage {key}")
            symbols = tuple(
                SourceSymbolBinding.from_record(record)
                for record in stage_record["symbols"]
            )
            if not symbols:
                raise AuthorityDriftError(f"binding stage {key} has no symbols")
            for symbol in symbols:
                if symbol.symbol_id in symbol_ids:
                    raise AuthorityDriftError(
                        f"duplicate binding symbol {symbol.symbol_id!r}"
                    )
                symbol_ids.add(symbol.symbol_id)
                source_path = root / symbol.source_path
                if not source_path.is_file():
                    raise AuthorityDriftError(
                        f"binding source is absent: {symbol.source_path}"
                    )
                if sha256_file(source_path) != symbol.source_sha256:
                    raise AuthorityDriftError(
                        f"binding source is stale: {symbol.source_path}"
                    )
                symbol.resolve(root)
            stage_symbols[key] = symbols
        if set(stage_symbols) != expected_stages:
            missing = sorted(expected_stages - set(stage_symbols))
            extra = sorted(set(stage_symbols) - expected_stages)
            raise AuthorityDriftError(
                f"binding map stage closure mismatch; missing={missing}, extra={extra}"
            )
        if int(bindings["pathway_count"]) != len(pathways):
            raise AuthorityDriftError("binding-map pathway count is stale")
        if int(bindings["stage_binding_count"]) != len(stage_symbols):
            raise AuthorityDriftError("binding-map stage count is stale")

        composition_crossings: dict[str, CompositionCrossingBinding] = {}
        for crossing_record in bindings.get("composition_crossing_bindings", []):
            crossing = CompositionCrossingBinding.from_record(crossing_record)
            if crossing.composition_id in composition_crossings:
                raise AuthorityDriftError(
                    f"duplicate composition crossing {crossing.composition_id!r}"
                )
            try:
                composition = compositions[crossing.composition_id]
            except KeyError as exc:
                raise AuthorityDriftError(
                    f"crossing references unknown composition {crossing.composition_id!r}"
                ) from exc
            if (
                crossing.crossing_kind != "explicit_adapter_callable"
                or composition["composition_status"] != "lawful_with_explicit_adapter"
                or crossing.source_pathway_id != composition["from_pathway_id"]
                or crossing.target_pathway_id != composition["to_pathway_id"]
                or crossing.symbol.qualified_symbol != composition["adapter_id"]
                or crossing.symbol.call_kind != "module_function"
            ):
                raise AuthorityDriftError(
                    f"composition crossing {crossing.composition_id!r} "
                    "does not match its matrix row"
                )
            if crossing.symbol.symbol_id in symbol_ids:
                raise AuthorityDriftError(
                    f"duplicate binding symbol {crossing.symbol.symbol_id!r}"
                )
            symbol_ids.add(crossing.symbol.symbol_id)
            source_path = root / crossing.symbol.source_path
            if (
                not source_path.is_file()
                or sha256_file(source_path) != crossing.symbol.source_sha256
            ):
                raise AuthorityDriftError(
                    f"composition crossing source is stale: "
                    f"{crossing.symbol.source_path}"
                )
            crossing.symbol.resolve(root)
            composition_crossings[crossing.composition_id] = crossing

        required_crossings = {
            composition_id
            for composition_id, composition in compositions.items()
            if composition["composition_status"] == "lawful_with_explicit_adapter"
        }
        if set(composition_crossings) != required_crossings:
            raise AuthorityDriftError(
                "explicit-adapter crossing closure mismatch; "
                f"required={sorted(required_crossings)}, "
                f"actual={sorted(composition_crossings)}"
            )
        if int(bindings.get("composition_crossing_binding_count", -1)) != len(
            composition_crossings
        ):
            raise AuthorityDriftError("composition-crossing binding count is stale")
        return cls(
            repository_root=root,
            documents=documents,
            pathways=pathways,
            compositions=compositions,
            stage_symbols=stage_symbols,
            composition_crossings=composition_crossings,
        )


@dataclass(frozen=True)
class InvocationRecord:
    """One in-memory I113 use record around real-callable delegation."""

    binding_id: str
    pathway_id: str
    stage_id: str
    symbol_id: str
    composition_ids: tuple[str, ...]
    outcome: str
    result_type: str | None
    error_type: str | None
    callable_identity: Mapping[str, Any]
    execution_event_order: int = -1
    crossing_scope_id: str | None = None
    candidate_scope_id: str | None = None


@dataclass(frozen=True)
class CrossingInvocationRecord:
    """One invocation of a registered composition crossing callable."""

    crossing_scope_id: str
    binding_id: str
    composition_id: str
    symbol_id: str
    source_binding_id: str
    target_binding_id: str
    outcome: str
    result_type: str | None
    error_type: str | None
    callable_identity: Mapping[str, Any]
    execution_event_order: int = -1


_UNRESOLVED_CROSSING_RESULT: Final[object] = object()


class CrossingResultReference:
    """Deferred instance reference to a real crossing callable's result."""

    def __init__(self, *, composition_id: str, target_pathway_id: str) -> None:
        self.composition_id = composition_id
        self.target_pathway_id = target_pathway_id
        self._value: object = _UNRESOLVED_CROSSING_RESULT

    def _set(self, value: object) -> None:
        if self._value is not _UNRESOLVED_CROSSING_RESULT:
            raise BindingStateError(
                f"composition {self.composition_id!r} crossing already returned"
            )
        self._value = value

    def resolve(self) -> object:
        """Return the adapter result or fail before target-stage delegation."""

        if self._value is _UNRESOLVED_CROSSING_RESULT:
            raise BindingStateError(
                f"composition {self.composition_id!r} crossing has not returned"
            )
        return self._value


class VerifiedCallable:
    """Callable link that preserves the linked mechanism's arguments and result."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        composition_ids: tuple[str, ...],
        symbol: SourceSymbolBinding,
        instance: object | CrossingResultReference | None,
    ) -> None:
        repository_root = session.authority.repository_root
        target = symbol.resolve(repository_root)
        instance_reference = (
            instance if isinstance(instance, CrossingResultReference) else None
        )
        if instance_reference is not None:
            if symbol.call_kind != "instance_method":
                raise SymbolBindingError(
                    f"{symbol.symbol_id!r} cannot use a deferred instance"
                )
        elif instance is not None:
            if symbol.call_kind != "instance_method":
                raise SymbolBindingError(
                    f"{symbol.symbol_id!r} is not an instance method"
                )
            target = target.__get__(instance, type(instance))
        identity = symbol.callable_identity(target, repository_root)
        self._session = session
        self._binding_id = binding_id
        self._pathway_id = pathway_id
        self._stage_id = stage_id
        self._composition_ids = composition_ids
        self._symbol = symbol
        self._target = target
        self._instance_reference = instance_reference
        self._expected_definition = _callable_definition(target)
        self._expected_bound_owner = _callable_bound_owner(target)
        self._callable_identity = identity
        self.__name__ = getattr(target, "__name__", symbol.qualified_symbol)
        self.__doc__ = getattr(target, "__doc__", None)
        signature = inspect.signature(target)
        if instance_reference is not None:
            parameters = tuple(signature.parameters.values())
            if parameters and parameters[0].name in {"self", "cls"}:
                signature = signature.replace(parameters=parameters[1:])
        self.__signature__ = signature

    @property
    def symbol_id(self) -> str:
        return self._symbol.symbol_id

    @property
    def linked_callable(self) -> Callable[..., Any]:
        if self._instance_reference is None:
            return self._target
        target, _ = self._assert_current_callable()
        return target

    @property
    def callable_identity(self) -> Mapping[str, Any]:
        """Return the callable identity frozen for this handle."""

        return MappingProxyType(self._callable_identity.to_record())

    def _assert_current_callable(
        self,
    ) -> tuple[Callable[..., Any], Mapping[str, Any]]:
        """Fail before delegation if the resolved or stored target has changed."""

        repository_root = self._session.authority.repository_root
        current = self._symbol.resolve(repository_root)
        if self._symbol.call_kind == "instance_method":
            if self._instance_reference is not None:
                owner = self._instance_reference.resolve()
            else:
                owner = self._expected_bound_owner
            if owner is None:
                raise SymbolBindingError(
                    f"binding {self._symbol.symbol_id!r} lost its instance owner"
                )
            current = current.__get__(owner, type(owner))
        current_identity = self._symbol.callable_identity(current, repository_root)
        if current_identity.to_record() != self._callable_identity.to_record():
            raise SymbolBindingError(
                f"binding {self._symbol.symbol_id!r} callable fingerprint drifted"
            )
        identity_changed = (
            _callable_definition(current) is not self._expected_definition
            or _callable_definition(self._target) is not self._expected_definition
        )
        if self._instance_reference is None:
            identity_changed = identity_changed or (
                _callable_bound_owner(current) is not self._expected_bound_owner
                or _callable_bound_owner(self._target) is not self._expected_bound_owner
            )
        if identity_changed:
            raise SymbolBindingError(
                f"binding {self._symbol.symbol_id!r} callable identity changed"
            )
        return current, MappingProxyType(current_identity.to_record())

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self._session._assert_invocation_allowed(
            binding_id=self._binding_id,
            pathway_id=self._pathway_id,
            stage_id=self._stage_id,
            symbol_id=self._symbol.symbol_id,
            composition_ids=self._composition_ids,
        )
        target, callable_identity = self._assert_current_callable()
        for name, expected in self._symbol.required_keyword_arguments.items():
            if kwargs.get(name) != expected:
                raise SymbolBindingError(
                    f"binding {self._symbol.symbol_id!r} requires {name}={expected!r}"
                )
        try:
            result = target(*args, **kwargs)
        except Exception as exc:
            self._session._record_invocation(
                InvocationRecord(
                    binding_id=self._binding_id,
                    pathway_id=self._pathway_id,
                    stage_id=self._stage_id,
                    symbol_id=self._symbol.symbol_id,
                    composition_ids=self._composition_ids,
                    outcome="raised",
                    result_type=None,
                    error_type=type(exc).__name__,
                    callable_identity=callable_identity,
                )
            )
            raise
        self._session._record_invocation(
            InvocationRecord(
                binding_id=self._binding_id,
                pathway_id=self._pathway_id,
                stage_id=self._stage_id,
                symbol_id=self._symbol.symbol_id,
                composition_ids=self._composition_ids,
                outcome="returned",
                result_type=type(result).__name__,
                error_type=None,
                callable_identity=callable_identity,
            )
        )
        return result


class VerifiedCompositionCrossing:
    """Verified mechanism-specific callable for a registered adapter crossing."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        composition: BoundComposition,
        crossing: CompositionCrossingBinding,
        source_instance: object,
    ) -> None:
        target = crossing.symbol.resolve(session.authority.repository_root)
        self._session = session
        self._composition = composition
        self._crossing = crossing
        self._source_instance = source_instance
        self._target = target
        self._expected_definition = _callable_definition(target)
        self._callable_identity = crossing.symbol.callable_identity(
            target,
            session.authority.repository_root,
        )
        self._result_reference = CrossingResultReference(
            composition_id=composition.composition_id,
            target_pathway_id=crossing.target_pathway_id,
        )
        self.__name__ = getattr(
            target,
            "__name__",
            crossing.symbol.qualified_symbol,
        )
        self.__doc__ = getattr(target, "__doc__", None)
        self.__signature__ = inspect.signature(target)

    @property
    def symbol_id(self) -> str:
        return self._crossing.symbol.symbol_id

    @property
    def result_reference(self) -> CrossingResultReference:
        """Return the deferred target-instance reference for endpoint links."""

        return self._result_reference

    @property
    def callable_identity(self) -> Mapping[str, Any]:
        return MappingProxyType(self._callable_identity.to_record())

    def _assert_current_callable(self) -> tuple[Callable[..., Any], Mapping[str, Any]]:
        symbol = self._crossing.symbol
        repository_root = self._session.authority.repository_root
        current = symbol.resolve(repository_root)
        current_identity = symbol.callable_identity(current, repository_root)
        if (
            current_identity.to_record() != self._callable_identity.to_record()
            or _callable_definition(current) is not self._expected_definition
            or _callable_definition(self._target) is not self._expected_definition
        ):
            raise SymbolBindingError(
                f"composition crossing {symbol.symbol_id!r} callable identity changed"
            )
        return current, MappingProxyType(current_identity.to_record())

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        scope = self._session._assert_crossing_invocation_allowed(
            composition=self._composition,
            symbol_id=self.symbol_id,
        )
        target, callable_identity = self._assert_current_callable()
        try:
            arguments = inspect.signature(target).bind(*args, **kwargs).arguments
        except TypeError as exc:
            raise SymbolBindingError(
                f"composition crossing {self.symbol_id!r} arguments are invalid"
            ) from exc
        source_argument = self._crossing.source_argument_name
        if arguments.get(source_argument) is not self._source_instance:
            raise SymbolBindingError(
                f"composition crossing {self.symbol_id!r} must consume the "
                "declared source instance"
            )
        try:
            result = target(*args, **kwargs)
        except Exception as exc:
            self._session._record_crossing_invocation(
                scope,
                CrossingInvocationRecord(
                    crossing_scope_id=scope.scope_id,
                    binding_id=self._composition.binding_id,
                    composition_id=self._composition.composition_id,
                    symbol_id=self.symbol_id,
                    source_binding_id=self._composition.source_binding.binding_id,
                    target_binding_id=self._composition.target_binding.binding_id,
                    outcome="raised",
                    result_type=None,
                    error_type=type(exc).__name__,
                    callable_identity=callable_identity,
                ),
            )
            raise
        self._result_reference._set(result)
        self._session._record_crossing_invocation(
            scope,
            CrossingInvocationRecord(
                crossing_scope_id=scope.scope_id,
                binding_id=self._composition.binding_id,
                composition_id=self._composition.composition_id,
                symbol_id=self.symbol_id,
                source_binding_id=self._composition.source_binding.binding_id,
                target_binding_id=self._composition.target_binding.binding_id,
                outcome="returned",
                result_type=type(result).__name__,
                error_type=None,
                callable_identity=callable_identity,
            ),
        )
        return result


class BoundPathway:
    """An exact admitted pathway declaration and its stage links."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        binding_id: str,
        pathway_id: str,
        stage_ids: Sequence[str],
        composition_ids: Sequence[str] = (),
    ) -> None:
        self._session = session
        self.binding_id = binding_id
        self.pathway_id = pathway_id
        self.stage_ids = tuple(stage_ids)
        self.composition_ids = tuple(composition_ids)

    @property
    def contract(self) -> Mapping[str, Any]:
        return self._session.authority.pathway(self.pathway_id)

    def symbol(
        self,
        stage_id: str,
        *,
        symbol_id: str | None = None,
        instance: object | CrossingResultReference | None = None,
    ) -> VerifiedCallable:
        """Link one declared stage to an exact real source callable."""

        if (
            isinstance(instance, CrossingResultReference)
            and instance.target_pathway_id != self.pathway_id
        ):
            raise SymbolBindingError(
                f"crossing {instance.composition_id!r} returns "
                f"{instance.target_pathway_id!r}, not {self.pathway_id!r}"
            )
        if stage_id not in self.stage_ids:
            raise SymbolBindingError(
                f"stage {stage_id!r} was not declared for binding {self.binding_id!r}"
            )
        symbols = self._session.authority.symbols(self.pathway_id, stage_id)
        if symbol_id is None:
            if len(symbols) != 1:
                choices = [symbol.symbol_id for symbol in symbols]
                raise SymbolBindingError(
                    f"stage {self.pathway_id}:{stage_id} requires an exact "
                    f"symbol_id choice from {choices}"
                )
            selected = symbols[0]
        else:
            matches = [symbol for symbol in symbols if symbol.symbol_id == symbol_id]
            if len(matches) != 1:
                raise SymbolBindingError(
                    f"symbol {symbol_id!r} is not registered for "
                    f"{self.pathway_id}:{stage_id}"
                )
            selected = matches[0]
        linked = VerifiedCallable(
            session=self._session,
            binding_id=self.binding_id,
            pathway_id=self.pathway_id,
            stage_id=stage_id,
            composition_ids=self.composition_ids,
            symbol=selected,
            instance=instance,
        )
        self._session._register_link(
            binding_id=self.binding_id,
            pathway_id=self.pathway_id,
            stage_id=stage_id,
            composition_ids=self.composition_ids,
            symbol=selected,
            instance=instance,
            callable_identity=linked.callable_identity,
        )
        return linked


class BoundComposition:
    """One exact executable matrix row and its endpoint pathway handles."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        binding_id: str,
        composition: Mapping[str, Any],
        endpoints: Mapping[str, BoundPathway],
    ) -> None:
        self._session = session
        self.binding_id = binding_id
        self.composition_id = str(composition["composition_id"])
        self._composition = deepcopy(composition)
        self._endpoints = dict(endpoints)
        self._crossing_handle: VerifiedCompositionCrossing | None = None

    @property
    def contract(self) -> Mapping[str, Any]:
        return deepcopy(self._composition)

    @property
    def composition_status(self) -> str:
        return str(self._composition["composition_status"])

    @property
    def adapter_id(self) -> str:
        return str(self._composition["adapter_id"])

    @property
    def adapter_owner(self) -> str:
        return str(self._composition["adapter_owner"])

    @property
    def endpoint_bindings(self) -> tuple[BoundPathway, ...]:
        return tuple(self._endpoints.values())

    @property
    def source_binding(self) -> BoundPathway:
        return self.pathway(str(self._composition["from_pathway_id"]))

    @property
    def target_binding(self) -> BoundPathway:
        return self.pathway(str(self._composition["to_pathway_id"]))

    def pathway(self, pathway_id: str) -> BoundPathway:
        try:
            return self._endpoints[pathway_id]
        except KeyError as exc:
            raise UnknownPathwayError(
                f"{pathway_id!r} is not an endpoint of {self.composition_id}"
            ) from exc

    def crossing(
        self,
        *,
        source_instance: object,
    ) -> VerifiedCompositionCrossing:
        """Link the exact registered adapter callable for this composition."""

        self._session._require_declaration_phase()
        if self._crossing_handle is not None:
            raise CausalPathwayBindingError(
                f"composition {self.composition_id!r} crossing is already linked"
            )
        crossing = self._session.authority.composition_crossing(self.composition_id)
        handle = VerifiedCompositionCrossing(
            session=self._session,
            composition=self,
            crossing=crossing,
            source_instance=source_instance,
        )
        self._session._register_crossing_link(
            composition=self,
            crossing=crossing,
            source_instance=source_instance,
            result_reference=handle.result_reference,
            callable_identity=handle.callable_identity,
        )
        self._crossing_handle = handle
        return handle

    def evidence_scope(self) -> CompositionExecutionScope:
        """Return an explicit provenance-only scope for one crossing use."""

        return CompositionExecutionScope(session=self._session, composition=self)


class CompositionExecutionScope:
    """Ordered observed-use scope; it does not dispatch composition mechanics."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        composition: BoundComposition,
    ) -> None:
        self._session = session
        self.composition = composition
        self.scope_id = ""
        self._events: list[dict[str, Any]] = []
        self._completed = False

    def __enter__(self) -> Self:
        self.scope_id = self._session._open_composition_scope(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        self._completed = exc_type is None
        self._session._close_composition_scope(self)
        return False

    def _record_endpoint(
        self,
        *,
        event_order: int,
        invocation_index: int,
        record: InvocationRecord,
    ) -> None:
        self._events.append(
            {
                "event_order": event_order,
                "event_kind": "endpoint_stage",
                "record_index": invocation_index,
                "record": record,
            }
        )

    def _record_crossing(
        self,
        *,
        event_order: int,
        invocation_index: int,
        record: CrossingInvocationRecord,
    ) -> None:
        self._events.append(
            {
                "event_order": event_order,
                "event_kind": "crossing_callable",
                "record_index": invocation_index,
                "record": record,
            }
        )

    def exercise_witness(self) -> dict[str, Any] | None:
        """Return a witness only for complete ordered observed crossing use."""

        if not self._completed:
            return None
        contract = self.composition.contract
        source_binding = self.composition.source_binding
        target_binding = self.composition.target_binding
        source_events: list[dict[str, Any]] = []
        target_events: list[dict[str, Any]] = []
        for stage_id in contract["from_stage_ids"]:
            matches = [
                event
                for event in self._events
                if event["event_kind"] == "endpoint_stage"
                and event["record"].outcome == "returned"
                and event["record"].binding_id == source_binding.binding_id
                and event["record"].stage_id == stage_id
            ]
            if not matches:
                return None
            source_events.append(matches[0])
        for stage_id in contract["to_stage_ids"]:
            matches = [
                event
                for event in self._events
                if event["event_kind"] == "endpoint_stage"
                and event["record"].outcome == "returned"
                and event["record"].binding_id == target_binding.binding_id
                and event["record"].stage_id == stage_id
            ]
            if not matches:
                return None
            target_events.append(matches[0])
        if max(event["event_order"] for event in source_events) >= min(
            event["event_order"] for event in target_events
        ):
            return None

        crossing_events = [
            event
            for event in self._events
            if event["event_kind"] == "crossing_callable"
            and event["record"].outcome == "returned"
            and event["record"].binding_id == self.composition.binding_id
        ]
        adapter_required = (
            contract["composition_status"] == "lawful_with_explicit_adapter"
        )
        if adapter_required:
            if len(crossing_events) != 1:
                return None
            crossing_order = crossing_events[0]["event_order"]
            if not (
                max(event["event_order"] for event in source_events)
                < crossing_order
                < min(event["event_order"] for event in target_events)
            ):
                return None
        elif crossing_events:
            return None

        return {
            "crossing_scope_id": self.scope_id,
            "binding_id": self.composition.binding_id,
            "composition_id": self.composition.composition_id,
            "ordering_rule": "all_from_stages_before_crossing_before_all_to_stages"
            if adapter_required
            else "all_from_stages_before_all_to_stages",
            "from_invocation_indices": [
                event["record_index"] for event in source_events
            ],
            "crossing_invocation_indices": [
                event["record_index"] for event in crossing_events
            ],
            "to_invocation_indices": [event["record_index"] for event in target_events],
            "explicit_adapter_required": adapter_required,
            "explicit_adapter_observed": bool(crossing_events),
        }


class CandidateExecutionScope:
    """Observed constituent-use scope for one unregistered candidate."""

    def __init__(
        self,
        *,
        session: PathwayBindingSession,
        candidate: CandidateDeclaration,
    ) -> None:
        self._session = session
        self.candidate = candidate
        self.scope_id = ""
        self._events: list[dict[str, Any]] = []
        self._completed = False

    def __enter__(self) -> Self:
        self.scope_id = self._session._open_candidate_scope(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        self._completed = exc_type is None
        self._session._close_candidate_scope(self)
        return False

    def _record_constituent(
        self,
        *,
        event_order: int,
        invocation_index: int,
        record: InvocationRecord,
    ) -> None:
        self._events.append(
            {
                "event_order": event_order,
                "record_index": invocation_index,
                "record": record,
            }
        )

    def exercise_witness(self) -> dict[str, Any] | None:
        """Return evidence only for completed, returned constituent execution."""

        if not self._completed:
            return None
        returned = [
            event for event in self._events if event["record"].outcome == "returned"
        ]
        if self.candidate.candidate_kind == "pathway":
            if not returned:
                return None
            return {
                "candidate_scope_id": self.scope_id,
                "candidate_id": self.candidate.candidate_id,
                "witness_kind": "content_addressed_constituent_execution",
                "constituent_invocation_indices": [
                    event["record_index"] for event in returned
                ],
            }

        source_id = self.candidate.proposed_source_pathway_id
        target_id = self.candidate.proposed_target_pathway_id
        source_events = [
            event for event in returned if event["record"].pathway_id == source_id
        ]
        target_events = [
            event for event in returned if event["record"].pathway_id == target_id
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
        return {
            "candidate_scope_id": self.scope_id,
            "candidate_id": self.candidate.candidate_id,
            "witness_kind": "content_addressed_source_before_target",
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
            "ordering_rule": "all_source_invocations_before_all_target_invocations",
        }


@dataclass(frozen=True)
class CandidateUseRecord:
    """Explicit evidence that a declared candidate relation was exercised."""

    candidate_id: str
    mechanism_evidence: Mapping[str, str]
    execution_witness: Mapping[str, Any]


class BindingArtifact:
    """Immutable canonical JSON artifact with a content digest."""

    def __init__(self, record: Mapping[str, Any], *, digest_field: str) -> None:
        self._record = deepcopy(dict(record))
        self._digest_field = digest_field

    @property
    def digest(self) -> str:
        return str(self._record[self._digest_field])

    def to_record(self) -> dict[str, Any]:
        return deepcopy(self._record)

    def write(self, path: str | Path) -> None:
        target = Path(path)
        target.write_text(
            json.dumps(self._record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


class BindingLock(BindingArtifact):
    """Exact pre-execution pathway declaration and claim envelope."""

    def __init__(self, record: Mapping[str, Any]) -> None:
        super().__init__(record, digest_field="lock_digest")

    def contains_link(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        symbol_id: str,
        composition_ids: Sequence[str],
    ) -> bool:
        """Return whether this lock freezes one exact callable link."""

        record = self.to_record()
        for binding in record["declared_pathway_bindings"]:
            if (
                binding["binding_id"] != binding_id
                or binding["pathway_id"] != pathway_id
                or binding["composition_ids"] != list(composition_ids)
            ):
                continue
            return any(
                link["stage_id"] == stage_id and link["symbol_id"] == symbol_id
                for link in binding["expected_concrete_symbols"]
            )
        return False

    def contains_crossing_link(
        self,
        *,
        binding_id: str,
        composition_id: str,
        symbol_id: str,
    ) -> bool:
        """Return whether the lock freezes one explicit crossing callable."""

        for binding in self.to_record()["declared_composition_bindings"]:
            crossing = binding.get("expected_crossing_callable")
            if (
                binding.get("binding_id") == binding_id
                and binding.get("composition_id") == composition_id
                and isinstance(crossing, dict)
                and crossing.get("symbol_id") == symbol_id
            ):
                return True
        return False


class BindingReceipt(BindingArtifact):
    """Exact post-use receipt linked to one binding lock."""

    def __init__(self, record: Mapping[str, Any]) -> None:
        super().__init__(record, digest_field="receipt_digest")


class PathwayBindingSession:
    """Explicit declaration and linkage session; it never selects semantics."""

    def __init__(self, authority: CausalPathwayAuthority) -> None:
        self.authority = authority
        self._phase = "declaration"
        self._pathway_bindings: dict[str, BoundPathway] = {}
        self._composition_bindings: dict[str, BoundComposition] = {}
        self._candidates: dict[str, CandidateDeclaration] = {}
        self._alternatives: dict[str, AllowedPathwayAlternatives] = {}
        self._linked_symbols: dict[tuple[str, str], dict[str, Any]] = {}
        self._linked_instances: dict[tuple[str, str], object | None] = {}
        self._crossing_links: dict[str, dict[str, Any]] = {}
        self._crossing_runtime_links: dict[
            str,
            tuple[object, CrossingResultReference],
        ] = {}
        self._invocations: list[InvocationRecord] = []
        self._crossing_invocations: list[CrossingInvocationRecord] = []
        self._composition_scopes: list[CompositionExecutionScope] = []
        self._active_composition_scope: CompositionExecutionScope | None = None
        self._candidate_scopes: list[CandidateExecutionScope] = []
        self._active_candidate_scope: CandidateExecutionScope | None = None
        self._execution_event_count = 0
        self._candidate_uses: list[CandidateUseRecord] = []
        self._lock: BindingLock | None = None

    @property
    def phase(self) -> str:
        return self._phase

    @property
    def invocation_records(self) -> tuple[InvocationRecord, ...]:
        return tuple(self._invocations)

    @property
    def crossing_invocation_records(self) -> tuple[CrossingInvocationRecord, ...]:
        return tuple(self._crossing_invocations)

    @property
    def candidates(self) -> tuple[CandidateDeclaration, ...]:
        return tuple(self._candidates.values())

    @property
    def alternatives(self) -> tuple[AllowedPathwayAlternatives, ...]:
        return tuple(self._alternatives.values())

    @property
    def binding_lock(self) -> BindingLock | None:
        return self._lock

    def _require_declaration_phase(self) -> None:
        if self._phase != "declaration":
            raise BindingStateError(
                f"binding declarations are closed in session phase {self._phase!r}"
            )

    def _register_link(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        composition_ids: tuple[str, ...],
        symbol: SourceSymbolBinding,
        instance: object | CrossingResultReference | None,
        callable_identity: Mapping[str, Any],
    ) -> None:
        self._require_declaration_phase()
        key = (binding_id, symbol.symbol_id)
        self._linked_symbols[key] = {
            "binding_id": binding_id,
            "pathway_id": pathway_id,
            "stage_id": stage_id,
            "composition_ids": list(composition_ids),
            "symbol_id": symbol.symbol_id,
            "module": symbol.module,
            "qualified_symbol": symbol.qualified_symbol,
            "binding_role": symbol.binding_role,
            "call_kind": symbol.call_kind,
            "source_path": symbol.source_path,
            "source_sha256": symbol.source_sha256,
            "required_keyword_arguments": dict(symbol.required_keyword_arguments),
            "callable_identity": dict(callable_identity),
        }
        self._linked_instances[key] = instance

    def _register_crossing_link(
        self,
        *,
        composition: BoundComposition,
        crossing: CompositionCrossingBinding,
        source_instance: object,
        result_reference: CrossingResultReference,
        callable_identity: Mapping[str, Any],
    ) -> None:
        self._require_declaration_phase()
        if composition.binding_id in self._crossing_links:
            raise CausalPathwayBindingError(
                f"composition binding {composition.binding_id!r} already has a crossing"
            )
        symbol = crossing.symbol
        self._crossing_links[composition.binding_id] = {
            "binding_id": composition.binding_id,
            "composition_id": composition.composition_id,
            "crossing_kind": crossing.crossing_kind,
            "source_binding_id": composition.source_binding.binding_id,
            "source_pathway_id": crossing.source_pathway_id,
            "source_argument_name": crossing.source_argument_name,
            "target_binding_id": composition.target_binding.binding_id,
            "target_pathway_id": crossing.target_pathway_id,
            "symbol_id": symbol.symbol_id,
            "module": symbol.module,
            "qualified_symbol": symbol.qualified_symbol,
            "binding_role": symbol.binding_role,
            "call_kind": symbol.call_kind,
            "source_path": symbol.source_path,
            "source_sha256": symbol.source_sha256,
            "callable_identity": dict(callable_identity),
        }
        self._crossing_runtime_links[composition.binding_id] = (
            source_instance,
            result_reference,
        )

    def _assert_invocation_allowed(
        self,
        *,
        binding_id: str,
        pathway_id: str,
        stage_id: str,
        symbol_id: str,
        composition_ids: tuple[str, ...],
    ) -> None:
        if self._phase != "locked" or self._lock is None:
            raise BindingStateError(
                "claim-bearing bound calls require a frozen pre-execution lock"
            )
        if not self._lock.contains_link(
            binding_id=binding_id,
            pathway_id=pathway_id,
            stage_id=stage_id,
            symbol_id=symbol_id,
            composition_ids=composition_ids,
        ):
            raise BindingStateError(
                f"symbol {symbol_id!r} is absent from binding lock {self._lock.digest}"
            )

    def _record_invocation(self, record: InvocationRecord) -> None:
        invocation_index = len(self._invocations)
        scope = self._active_composition_scope
        scoped_to_composition = (
            scope is not None
            and scope.composition.composition_id in record.composition_ids
        )
        record = replace(
            record,
            execution_event_order=self._execution_event_count,
            crossing_scope_id=(
                scope.scope_id if scope is not None and scoped_to_composition else None
            ),
            candidate_scope_id=(
                self._active_candidate_scope.scope_id
                if self._active_candidate_scope is not None
                and record.pathway_id
                in self._active_candidate_scope.candidate.consumed_pathway_ids
                else None
            ),
        )
        self._invocations.append(record)
        if scope is not None and scoped_to_composition:
            scope._record_endpoint(
                event_order=self._execution_event_count,
                invocation_index=invocation_index,
                record=record,
            )
        candidate_scope = self._active_candidate_scope
        if (
            candidate_scope is not None
            and record.pathway_id in candidate_scope.candidate.consumed_pathway_ids
        ):
            candidate_scope._record_constituent(
                event_order=self._execution_event_count,
                invocation_index=invocation_index,
                record=record,
            )
        self._execution_event_count += 1

    def _record_crossing_invocation(
        self,
        scope: CompositionExecutionScope,
        record: CrossingInvocationRecord,
    ) -> None:
        invocation_index = len(self._crossing_invocations)
        record = replace(
            record,
            execution_event_order=self._execution_event_count,
        )
        self._crossing_invocations.append(record)
        scope._record_crossing(
            event_order=self._execution_event_count,
            invocation_index=invocation_index,
            record=record,
        )
        self._execution_event_count += 1

    def _open_composition_scope(self, scope: CompositionExecutionScope) -> str:
        if self._phase != "locked" or self._lock is None:
            raise BindingStateError(
                "composition evidence scopes require a frozen binding lock"
            )
        if (
            self._active_composition_scope is not None
            or self._active_candidate_scope is not None
        ):
            raise BindingStateError("execution evidence scopes cannot overlap")
        if scope.composition.binding_id not in self._composition_bindings:
            raise BindingStateError("composition scope is not declared in this session")
        scope_id = (
            f"{scope.composition.binding_id}:crossing-scope:"
            f"{len(self._composition_scopes)}"
        )
        self._active_composition_scope = scope
        self._composition_scopes.append(scope)
        return scope_id

    def _close_composition_scope(self, scope: CompositionExecutionScope) -> None:
        if self._active_composition_scope is not scope:
            raise BindingStateError("composition evidence scope is not active")
        self._active_composition_scope = None

    def _open_candidate_scope(self, scope: CandidateExecutionScope) -> str:
        if self._phase != "locked" or self._lock is None:
            raise BindingStateError(
                "candidate evidence scopes require a frozen binding lock"
            )
        if (
            self._active_composition_scope is not None
            or self._active_candidate_scope is not None
        ):
            raise BindingStateError("execution evidence scopes cannot overlap")
        candidate = self._candidates.get(scope.candidate.candidate_id)
        if candidate is not scope.candidate:
            raise BindingStateError("candidate scope is not declared in this session")
        scope_id = (
            f"candidate:{scope.candidate.candidate_id}:evidence-scope:"
            f"{len(self._candidate_scopes)}"
        )
        self._active_candidate_scope = scope
        self._candidate_scopes.append(scope)
        return scope_id

    def _close_candidate_scope(self, scope: CandidateExecutionScope) -> None:
        if self._active_candidate_scope is not scope:
            raise BindingStateError("candidate evidence scope is not active")
        self._active_candidate_scope = None

    def _assert_crossing_invocation_allowed(
        self,
        *,
        composition: BoundComposition,
        symbol_id: str,
    ) -> CompositionExecutionScope:
        if self._phase != "locked" or self._lock is None:
            raise BindingStateError(
                "composition crossing calls require a frozen binding lock"
            )
        scope = self._active_composition_scope
        if scope is None or scope.composition is not composition:
            raise BindingStateError(
                "composition crossing calls require their explicit evidence scope"
            )
        if not self._lock.contains_crossing_link(
            binding_id=composition.binding_id,
            composition_id=composition.composition_id,
            symbol_id=symbol_id,
        ):
            raise BindingStateError(
                f"crossing symbol {symbol_id!r} is absent from the binding lock"
            )
        if any(
            item.binding_id == composition.binding_id
            for item in self._crossing_invocations
        ):
            raise BindingStateError(
                f"composition {composition.composition_id!r} crossing was already "
                "invoked"
            )
        return scope

    def _all_pathway_bindings(self) -> tuple[BoundPathway, ...]:
        endpoints = (
            endpoint
            for composition in self._composition_bindings.values()
            for endpoint in composition.endpoint_bindings
        )
        return (*self._pathway_bindings.values(), *endpoints)

    def _binding_record(self, binding: BoundPathway) -> dict[str, Any]:
        contract = self.authority.pathway(binding.pathway_id)
        expected_symbols = sorted(
            (
                deepcopy(link)
                for (binding_id, _), link in self._linked_symbols.items()
                if binding_id == binding.binding_id
            ),
            key=lambda item: str(item["symbol_id"]),
        )
        return {
            "binding_id": binding.binding_id,
            "pathway_id": binding.pathway_id,
            "declared_stage_ids": list(binding.stage_ids),
            "composition_ids": list(binding.composition_ids),
            "mechanism_ownership": contract["mechanism_ownership"],
            "availability": contract["availability"],
            "activation": contract["activation"],
            "configured_residue": list(contract["configured_residue"]),
            "producer_residue": list(contract["producer_residue"]),
            "expected_concrete_symbols": expected_symbols,
        }

    def _composition_record(self, binding: BoundComposition) -> dict[str, Any]:
        contract = binding.contract
        return {
            "binding_id": binding.binding_id,
            "composition_id": binding.composition_id,
            "from_pathway_id": contract["from_pathway_id"],
            "from_stage_ids": list(contract["from_stage_ids"]),
            "to_pathway_id": contract["to_pathway_id"],
            "to_stage_ids": list(contract["to_stage_ids"]),
            "composition_status": contract["composition_status"],
            "adapter_id": contract["adapter_id"],
            "adapter_owner": contract["adapter_owner"],
            "authority_retained": list(contract["authority_retained"]),
            "authority_transferred": list(contract["authority_transferred"]),
            "information_lost_or_compressed": contract[
                "information_lost_or_compressed"
            ],
            "claim_ceiling": contract["claim_ceiling"],
            "blocked_relabels": list(contract["blocked_relabels"]),
            "expected_crossing_callable": deepcopy(
                self._crossing_links.get(binding.binding_id)
            ),
        }

    def _derive_claim_envelope(
        self,
        *,
        pathway_bindings: Sequence[BoundPathway],
        composition_bindings: Sequence[BoundComposition],
        candidates: Sequence[CandidateDeclaration],
    ) -> dict[str, Any]:
        pathway_claims: list[dict[str, Any]] = []
        composition_claims: list[dict[str, Any]] = []
        producer_cuts: list[dict[str, Any]] = []
        adapter_cuts: list[dict[str, Any]] = []
        diagnostic_relations: list[dict[str, str]] = []
        configured_semantics: list[dict[str, Any]] = []
        blocked_claims: list[str] = []

        for pathway_binding in sorted(
            pathway_bindings, key=lambda item: item.binding_id
        ):
            contract = self.authority.pathway(pathway_binding.pathway_id)
            pathway_claims.append(
                {
                    "binding_id": pathway_binding.binding_id,
                    "pathway_id": pathway_binding.pathway_id,
                    "constituent_claim_ceiling": list(contract["supported_claims"]),
                    "mechanism_ownership": contract["mechanism_ownership"],
                    "required_qualifiers": {
                        "configured_residue": list(contract["configured_residue"]),
                        "producer_residue": list(contract["producer_residue"]),
                        "naturalization_debt": list(contract["naturalization_debt"]),
                    },
                    "blocked_claims": list(contract["blocked_claims"]),
                }
            )
            if contract["configured_residue"]:
                configured_semantics.append(
                    {
                        "pathway_id": pathway_binding.pathway_id,
                        "residue": list(contract["configured_residue"]),
                    }
                )
            if (
                contract["producer_residue"]
                or contract["mechanism_ownership"] == "producer"
            ):
                producer_cuts.append(
                    {
                        "pathway_id": pathway_binding.pathway_id,
                        "producer_identity": contract["trigger_surface"],
                        "producer_owned_authorities": list(
                            contract["producer_residue"]
                        ),
                    }
                )
            if contract["mechanism_ownership"] == "diagnostic":
                diagnostic_relations.append(
                    {
                        "kind": "pathway",
                        "identity": pathway_binding.pathway_id,
                    }
                )
            blocked_claims.extend(str(item) for item in contract["blocked_claims"])

        for composition_binding in sorted(
            composition_bindings, key=lambda item: item.composition_id
        ):
            contract = composition_binding.contract
            status = str(contract["composition_status"])
            composition_claims.append(
                {
                    "binding_id": composition_binding.binding_id,
                    "composition_id": composition_binding.composition_id,
                    "composition_status": status,
                    "constituent_claim_ceiling": contract["claim_ceiling"],
                    "adapter_id": contract["adapter_id"],
                    "adapter_owner": contract["adapter_owner"],
                    "authority_retained": list(contract["authority_retained"]),
                    "authority_transferred": list(contract["authority_transferred"]),
                    "blocked_claims": list(contract["blocked_relabels"]),
                }
            )
            if status == "producer_mediated":
                producer_cuts.append(
                    {
                        "composition_id": composition_binding.composition_id,
                        "producer_identity": contract["adapter_id"],
                        "producer_owner": contract["adapter_owner"],
                        "producer_owned_authorities": list(
                            contract["authority_transferred"]
                        ),
                    }
                )
            if status == "lawful_with_explicit_adapter":
                adapter_cuts.append(
                    {
                        "composition_id": composition_binding.composition_id,
                        "adapter_id": contract["adapter_id"],
                        "adapter_owner": contract["adapter_owner"],
                    }
                )
            if status == "diagnostic_only":
                diagnostic_relations.append(
                    {
                        "kind": "composition",
                        "identity": composition_binding.composition_id,
                    }
                )
            blocked_claims.extend(str(item) for item in contract["blocked_relabels"])

        candidate_records = [candidate.to_record() for candidate in candidates]
        for candidate in candidates:
            blocked_claims.extend(candidate.blocked_claims)
        if candidates:
            overall_status = "experimental_unregistered"
        elif diagnostic_relations:
            overall_status = "bounded_with_diagnostic_cut"
        elif producer_cuts or adapter_cuts:
            overall_status = "bounded_with_explicit_ownership_cuts"
        else:
            overall_status = "admitted_bounded"
        return {
            "constituent_pathway_claim_ceilings": pathway_claims,
            "constituent_composition_claim_ceilings": composition_claims,
            "required_qualifiers": {
                "configured_semantics": configured_semantics,
                "producer_cuts": producer_cuts,
                "adapter_cuts": adapter_cuts,
                "diagnostic_only_relations": diagnostic_relations,
                "candidate_relations": candidate_records,
            },
            "contains_producer_cut": bool(producer_cuts),
            "contains_adapter_cut": bool(adapter_cuts),
            "contains_diagnostic_only_relation": bool(diagnostic_relations),
            "experimental_unregistered": bool(candidates),
            "blocked_claims": list(dict.fromkeys(blocked_claims)),
            "overall_claim_status": overall_status,
            "composition_status_is_maturity_score": False,
            "synthesized_chain_claim": False,
        }

    def _validate_explicit_crossing_dataflow(self) -> None:
        """Bind explicit-adapter endpoints to the adapter's exact object flow."""

        for composition in self._composition_bindings.values():
            if composition.composition_status != "lawful_with_explicit_adapter":
                continue
            try:
                source_instance, result_reference = self._crossing_runtime_links[
                    composition.binding_id
                ]
            except KeyError as exc:
                raise BindingStateError(
                    f"explicit-adapter composition {composition.composition_id!r} "
                    "lacks a crossing runtime link"
                ) from exc
            endpoint_roles = (
                (
                    composition.source_binding,
                    source_instance,
                    "declared_adapter_source_instance",
                ),
                (
                    composition.target_binding,
                    result_reference,
                    "adapter_result_reference",
                ),
            )
            for endpoint, expected_instance, role in endpoint_roles:
                for key, link in self._linked_symbols.items():
                    if key[0] != endpoint.binding_id:
                        continue
                    if link["call_kind"] != "instance_method":
                        raise BindingStateError(
                            f"explicit-adapter endpoint {endpoint.pathway_id!r} "
                            "requires instance-bound stage symbols"
                        )
                    if self._linked_instances.get(key) is not expected_instance:
                        raise BindingStateError(
                            f"explicit-adapter endpoint {endpoint.pathway_id!r} "
                            f"must use its {role.replace('_', ' ')}"
                        )
                    link["composition_crossing_instance_role"] = role
            crossing_link = self._crossing_links[composition.binding_id]
            crossing_link["source_instance_binding"] = (
                "exact_declared_adapter_source_instance"
            )
            crossing_link["target_instance_binding"] = "exact_adapter_result_reference"

    def freeze_lock(self) -> BindingLock:
        """Close declarations and freeze exact symbols before execution."""

        self._require_declaration_phase()
        self.authority.assert_current()
        bindings = self._all_pathway_bindings()
        missing_crossings = sorted(
            binding.composition_id
            for binding in self._composition_bindings.values()
            if binding.composition_status == "lawful_with_explicit_adapter"
            and binding.binding_id not in self._crossing_links
        )
        if missing_crossings:
            raise BindingStateError(
                "explicit-adapter compositions require their exact crossing "
                f"callable before lock: {missing_crossings}"
            )
        self._validate_explicit_crossing_dataflow()
        for candidate in self._candidates.values():
            if candidate.mechanism_evidence is not None:
                candidate.mechanism_evidence.assert_current(
                    self.authority.repository_root,
                    candidate_kind=candidate.candidate_kind,
                    proposed_source_pathway_id=(candidate.proposed_source_pathway_id),
                    proposed_target_pathway_id=(candidate.proposed_target_pathway_id),
                    proposed_relation=candidate.proposed_relation,
                )
        declared_pathway_ids = {binding.pathway_id for binding in bindings}
        for alternatives in self._alternatives.values():
            missing = sorted(set(alternatives.pathway_ids) - declared_pathway_ids)
            if missing:
                raise BindingStateError(
                    f"alternative set {alternatives.alternative_set_id!r} lacks "
                    f"declared pathway bindings for {missing}"
                )
        claim_envelope = self._derive_claim_envelope(
            pathway_bindings=bindings,
            composition_bindings=tuple(self._composition_bindings.values()),
            candidates=tuple(self._candidates.values()),
        )
        record: dict[str, Any] = {
            "artifact": "causal-pathways-binding-lock",
            "schema_version": "causal_pathways_binding_lock_v1",
            **dict(self.authority.artifact_identities()),
            "declared_pathway_bindings": [
                self._binding_record(binding)
                for binding in sorted(bindings, key=lambda item: item.binding_id)
            ],
            "declared_composition_bindings": [
                self._composition_record(binding)
                for binding in sorted(
                    self._composition_bindings.values(),
                    key=lambda item: item.composition_id,
                )
            ],
            "allowed_pathway_alternatives": [
                {
                    "alternative_set_id": item.alternative_set_id,
                    "pathway_ids": list(item.pathway_ids),
                    "selection_authority": item.selection_authority,
                }
                for item in sorted(
                    self._alternatives.values(),
                    key=lambda item: item.alternative_set_id,
                )
            ],
            "candidate_declarations": [
                item.to_record()
                for item in sorted(
                    self._candidates.values(), key=lambda item: item.candidate_id
                )
            ],
            "explicit_producers": deepcopy(
                claim_envelope["required_qualifiers"]["producer_cuts"]
            ),
            "explicit_adapters": deepcopy(
                claim_envelope["required_qualifiers"]["adapter_cuts"]
            ),
            "pre_execution_claim_envelope": claim_envelope,
            "blocked_claims": list(claim_envelope["blocked_claims"]),
            "claim_scope": CLAIM_SCOPE_BOUND_INVOCATIONS,
            "whole_run_causal_closure_claimed": False,
            "untracked_execution_observable_by_binding_plane": False,
            "semantic_selection_performed_by_binder": False,
            "unregistered_relation_bound_without_candidate": False,
            "lock_digest": "",
        }
        record["lock_digest"] = canonical_digest(record, excluding="lock_digest")
        self._lock = BindingLock(record)
        self._phase = "locked"
        return self._lock

    def record_candidate_use(
        self,
        candidate_id: str,
    ) -> CandidateUseRecord:
        """Record one scoped candidate use against its frozen content address."""

        if self._phase != "locked":
            raise BindingStateError("candidate use requires a frozen binding lock")
        if candidate_id not in self._candidates:
            raise InvalidCandidateError(
                f"candidate {candidate_id!r} was not declared before lock"
            )
        if any(item.candidate_id == candidate_id for item in self._candidate_uses):
            raise InvalidCandidateError(
                f"candidate {candidate_id!r} already has a use record"
            )
        candidate = self._candidates[candidate_id]
        evidence = candidate.mechanism_evidence
        if evidence is None:
            raise InvalidCandidateError(
                "candidate use requires content-addressed mechanism evidence "
                "declared before lock"
            )
        evidence.assert_current(
            self.authority.repository_root,
            candidate_kind=candidate.candidate_kind,
            proposed_source_pathway_id=candidate.proposed_source_pathway_id,
            proposed_target_pathway_id=candidate.proposed_target_pathway_id,
            proposed_relation=candidate.proposed_relation,
        )
        witnesses = [
            witness
            for scope in self._candidate_scopes
            if scope.candidate is candidate
            if (witness := scope.exercise_witness()) is not None
        ]
        if len(witnesses) != 1:
            raise InvalidCandidateError(
                "candidate use requires exactly one completed evidence scope with "
                "returned constituent execution"
            )
        use = CandidateUseRecord(
            candidate_id=candidate_id,
            mechanism_evidence=MappingProxyType(evidence.to_record()),
            execution_witness=MappingProxyType(deepcopy(witnesses[0])),
        )
        self._candidate_uses.append(use)
        return use

    def _composition_witnesses(self) -> tuple[dict[str, Any], ...]:
        witnesses: list[dict[str, Any]] = []
        witnessed_binding_ids: set[str] = set()
        for scope in self._composition_scopes:
            witness = scope.exercise_witness()
            if witness is None:
                continue
            binding_id = str(witness["binding_id"])
            if binding_id in witnessed_binding_ids:
                raise BindingStateError(
                    f"composition binding {binding_id!r} has multiple complete "
                    "execution scopes"
                )
            witnessed_binding_ids.add(binding_id)
            witnesses.append(witness)
        return tuple(witnesses)

    def _exercised_compositions(
        self,
        witnesses: Sequence[Mapping[str, Any]],
    ) -> tuple[BoundComposition, ...]:
        witnessed_binding_ids = {str(witness["binding_id"]) for witness in witnesses}
        return tuple(
            binding
            for binding in self._composition_bindings.values()
            if binding.binding_id in witnessed_binding_ids
        )

    def _actual_pathway_bindings(self) -> tuple[BoundPathway, ...]:
        successful_binding_ids = {
            record.binding_id
            for record in self._invocations
            if record.outcome == "returned"
        }
        return tuple(
            binding
            for binding in self._all_pathway_bindings()
            if binding.binding_id in successful_binding_ids
        )

    def _use_graph(
        self,
        *,
        actual_bindings: Sequence[BoundPathway],
        exercised_compositions: Sequence[BoundComposition],
    ) -> dict[str, Any]:
        successful = [
            record for record in self._invocations if record.outcome == "returned"
        ]
        nodes: list[dict[str, Any]] = []
        for pathway_binding in sorted(
            actual_bindings, key=lambda item: item.binding_id
        ):
            contract = self.authority.pathway(pathway_binding.pathway_id)
            uses = [
                record
                for record in successful
                if record.binding_id == pathway_binding.binding_id
            ]
            nodes.append(
                {
                    "node_id": pathway_binding.binding_id,
                    "node_kind": "admitted_pathway",
                    "pathway_id": pathway_binding.pathway_id,
                    "pathway_status": {
                        "availability": contract["availability"],
                        "activation": contract["activation"],
                        "staleness_state": contract["staleness_state"],
                        "mechanism_ownership": contract["mechanism_ownership"],
                    },
                    "stage_ids_used": list(
                        dict.fromkeys(record.stage_id for record in uses)
                    ),
                    "mechanism_ownership": contract["mechanism_ownership"],
                    "configured_residue": list(contract["configured_residue"]),
                    "producer_residue": list(contract["producer_residue"]),
                    "source_bindings_used": list(
                        dict.fromkeys(record.symbol_id for record in uses)
                    ),
                }
            )
        edges: list[dict[str, Any]] = []
        for composition_binding in sorted(
            exercised_compositions, key=lambda item: item.composition_id
        ):
            contract = composition_binding.contract
            endpoint_ids = {
                endpoint.pathway_id: endpoint.binding_id
                for endpoint in composition_binding.endpoint_bindings
            }
            edges.append(
                {
                    "edge_id": composition_binding.binding_id,
                    "edge_kind": "registered_composition",
                    "composition_id": composition_binding.composition_id,
                    "source_node_id": endpoint_ids[str(contract["from_pathway_id"])],
                    "target_node_id": endpoint_ids[str(contract["to_pathway_id"])],
                    "composition_status": contract["composition_status"],
                    "adapter_id": contract["adapter_id"],
                    "adapter_owner": contract["adapter_owner"],
                    "producer_owner": (
                        contract["adapter_owner"]
                        if contract["composition_status"] == "producer_mediated"
                        else None
                    ),
                    "authority_retained": list(contract["authority_retained"]),
                    "authority_transferred": list(contract["authority_transferred"]),
                    "information_lost_or_compressed": contract[
                        "information_lost_or_compressed"
                    ],
                    "claim_ceiling": contract["claim_ceiling"],
                    "blocked_claims": list(contract["blocked_relabels"]),
                }
            )
        actual_by_pathway: dict[str, str] = {}
        for binding in actual_bindings:
            actual_by_pathway.setdefault(binding.pathway_id, binding.binding_id)
        for use in self._candidate_uses:
            candidate = self._candidates[use.candidate_id]
            if candidate.candidate_kind == "pathway":
                nodes.append(
                    {
                        "node_id": f"candidate:{candidate.candidate_id}",
                        "node_kind": "experimental_unregistered_candidate",
                        "candidate_id": candidate.candidate_id,
                        "claim_ceiling": candidate.claim_ceiling,
                        "promotion_status": candidate.promotion_status,
                        "mechanism_evidence": dict(use.mechanism_evidence),
                        "candidate_execution_witness": dict(use.execution_witness),
                        "authority": dict(candidate.authority),
                        "producer_residue": list(candidate.producer_residue),
                        "adapter_residue": list(candidate.adapter_residue),
                        "configured_residue": list(candidate.configured_residue),
                        "blocked_claims": list(candidate.blocked_claims),
                    }
                )
                continue
            assert candidate.proposed_source_pathway_id is not None
            assert candidate.proposed_target_pathway_id is not None
            source_binding_id = str(use.execution_witness.get("source_binding_id", ""))
            target_binding_id = str(use.execution_witness.get("target_binding_id", ""))
            if (
                candidate.proposed_source_pathway_id not in actual_by_pathway
                or candidate.proposed_target_pathway_id not in actual_by_pathway
                or source_binding_id
                not in {binding.binding_id for binding in actual_bindings}
                or target_binding_id
                not in {binding.binding_id for binding in actual_bindings}
            ):
                raise BindingStateError(
                    f"used candidate {candidate.candidate_id!r} lacks actual bound "
                    "source or target pathway use"
                )
            edges.append(
                {
                    "edge_id": f"candidate:{candidate.candidate_id}",
                    "edge_kind": "experimental_unregistered_candidate",
                    "candidate_id": candidate.candidate_id,
                    "source_node_id": source_binding_id,
                    "target_node_id": target_binding_id,
                    "proposed_relation": candidate.proposed_relation,
                    "claim_ceiling": candidate.claim_ceiling,
                    "promotion_status": candidate.promotion_status,
                    "mechanism_evidence": dict(use.mechanism_evidence),
                    "candidate_execution_witness": dict(use.execution_witness),
                    "authority": dict(candidate.authority),
                    "producer_residue": list(candidate.producer_residue),
                    "adapter_residue": list(candidate.adapter_residue),
                    "configured_residue": list(candidate.configured_residue),
                    "blocked_claims": list(candidate.blocked_claims),
                }
            )
        return {
            "nodes": nodes,
            "edges": edges,
            "unregistered_edge_synthesized_from_endpoint_co_use": False,
            "larger_chain_claim_synthesized": False,
        }

    def build_receipt(self) -> BindingReceipt:
        """Seal actual use against the exact frozen binding lock."""

        if self._phase != "locked" or self._lock is None:
            raise BindingStateError("a receipt requires one active binding lock")
        if self._active_composition_scope is not None:
            raise BindingStateError(
                "a receipt cannot be sealed inside a composition evidence scope"
            )
        if self._active_candidate_scope is not None:
            raise BindingStateError(
                "a receipt cannot be sealed inside a candidate evidence scope"
            )
        self.authority.assert_current()
        actual_bindings = self._actual_pathway_bindings()
        composition_witnesses = self._composition_witnesses()
        exercised_compositions = self._exercised_compositions(composition_witnesses)
        used_candidate_ids = {item.candidate_id for item in self._candidate_uses}
        used_candidates = tuple(
            self._candidates[candidate_id]
            for candidate_id in sorted(used_candidate_ids)
        )
        for candidate in used_candidates:
            assert candidate.mechanism_evidence is not None
            candidate.mechanism_evidence.assert_current(
                self.authority.repository_root,
                candidate_kind=candidate.candidate_kind,
                proposed_source_pathway_id=candidate.proposed_source_pathway_id,
                proposed_target_pathway_id=candidate.proposed_target_pathway_id,
                proposed_relation=candidate.proposed_relation,
            )
        graph = self._use_graph(
            actual_bindings=actual_bindings,
            exercised_compositions=exercised_compositions,
        )
        claim_envelope = self._derive_claim_envelope(
            pathway_bindings=actual_bindings,
            composition_bindings=exercised_compositions,
            candidates=used_candidates,
        )
        successful_binding_ids = {binding.binding_id for binding in actual_bindings}
        all_bindings = self._all_pathway_bindings()
        declared_but_unused = {
            "pathway_binding_ids": sorted(
                binding.binding_id
                for binding in all_bindings
                if binding.binding_id not in successful_binding_ids
            ),
            "composition_binding_ids": sorted(
                binding.binding_id
                for binding in self._composition_bindings.values()
                if binding not in exercised_compositions
            ),
            "candidate_ids": sorted(set(self._candidates) - used_candidate_ids),
        }
        actual_uses = [
            {
                "invocation_index": index,
                "binding_id": item.binding_id,
                "pathway_id": item.pathway_id,
                "stage_id": item.stage_id,
                "symbol_id": item.symbol_id,
                "composition_ids": list(item.composition_ids),
                "outcome": item.outcome,
                "result_type": item.result_type,
                "error_type": item.error_type,
                "callable_identity": dict(item.callable_identity),
                "execution_event_order": item.execution_event_order,
                "crossing_scope_id": item.crossing_scope_id,
                "candidate_scope_id": item.candidate_scope_id,
            }
            for index, item in enumerate(self._invocations)
        ]
        crossing_uses = [
            {
                "crossing_invocation_index": index,
                "crossing_scope_id": item.crossing_scope_id,
                "binding_id": item.binding_id,
                "composition_id": item.composition_id,
                "symbol_id": item.symbol_id,
                "source_binding_id": item.source_binding_id,
                "target_binding_id": item.target_binding_id,
                "outcome": item.outcome,
                "result_type": item.result_type,
                "error_type": item.error_type,
                "callable_identity": dict(item.callable_identity),
                "execution_event_order": item.execution_event_order,
            }
            for index, item in enumerate(self._crossing_invocations)
        ]
        alternative_uses = [
            {
                "alternative_set_id": alternatives.alternative_set_id,
                "selection_authority": alternatives.selection_authority,
                "allowed_pathway_ids": list(alternatives.pathway_ids),
                "actual_pathway_ids_used": [
                    pathway_id
                    for pathway_id in alternatives.pathway_ids
                    if any(
                        binding.pathway_id == pathway_id for binding in actual_bindings
                    )
                ],
            }
            for alternatives in sorted(
                self._alternatives.values(),
                key=lambda item: item.alternative_set_id,
            )
        ]
        record: dict[str, Any] = {
            "artifact": "causal-pathways-binding-receipt",
            "schema_version": "causal_pathways_binding_receipt_v1",
            "binding_lock_digest": self._lock.digest,
            **dict(self.authority.artifact_identities()),
            "actual_bound_pathways_used": [
                {
                    **self._binding_record(binding),
                    "actual_stage_ids": list(
                        dict.fromkeys(
                            item.stage_id
                            for item in self._invocations
                            if item.binding_id == binding.binding_id
                            and item.outcome == "returned"
                        )
                    ),
                    "actual_symbol_ids": list(
                        dict.fromkeys(
                            item.symbol_id
                            for item in self._invocations
                            if item.binding_id == binding.binding_id
                            and item.outcome == "returned"
                        )
                    ),
                }
                for binding in sorted(actual_bindings, key=lambda item: item.binding_id)
            ],
            "actual_stage_symbol_invocations": actual_uses,
            "actual_composition_crossing_invocations": crossing_uses,
            "composition_crossing_witnesses": list(composition_witnesses),
            "allowed_pathway_alternatives_actual_use": alternative_uses,
            "registered_compositions_exercised": [
                self._composition_record(binding) for binding in exercised_compositions
            ],
            "adapters_used": deepcopy(
                claim_envelope["required_qualifiers"]["adapter_cuts"]
            ),
            "producer_cuts_used": deepcopy(
                claim_envelope["required_qualifiers"]["producer_cuts"]
            ),
            "candidate_relations_exercised": [
                {
                    **self._candidates[item.candidate_id].to_record(),
                    "candidate_execution_witness": dict(item.execution_witness),
                }
                for item in self._candidate_uses
            ],
            "declared_but_unused": declared_but_unused,
            "pathway_use_graph": graph,
            "claim_envelope": claim_envelope,
            "blocked_claims": list(claim_envelope["blocked_claims"]),
            "undeclared_use_violations": [],
            "claim_qualified": bool(actual_bindings or self._candidate_uses),
            "claim_scope": CLAIM_SCOPE_BOUND_INVOCATIONS,
            "whole_run_causal_closure_claimed": False,
            "untracked_execution_observable_by_binding_plane": False,
            "external_or_untracked_causal_input": UNTRACKED_EXECUTION_STATUS,
            "unbound_execution_accepted_as_evidence": False,
            "semantic_selection_performed_by_binder": False,
            "receipt_digest": "",
        }
        record["receipt_digest"] = canonical_digest(record, excluding="receipt_digest")
        receipt = BindingReceipt(record)
        self._phase = "sealed"
        return receipt

    def bind_pathway(
        self,
        pathway_id: str,
        *,
        stage_ids: Sequence[str] | None = None,
        binding_id: str | None = None,
    ) -> BoundPathway:
        """Declare one exact admitted pathway without choosing it for the caller."""

        self._require_declaration_phase()
        available_stages = self.authority.stage_ids(pathway_id)
        declared_stages = available_stages if stage_ids is None else tuple(stage_ids)
        if not declared_stages:
            raise CausalPathwayBindingError(
                "a pathway binding needs at least one stage"
            )
        unknown_stages = sorted(set(declared_stages) - set(available_stages))
        if unknown_stages:
            raise SymbolBindingError(
                f"pathway {pathway_id!r} has no stages {unknown_stages}"
            )
        identity = binding_id or f"pathway:{pathway_id}"
        if identity in self._pathway_bindings:
            raise CausalPathwayBindingError(f"duplicate binding ID {identity!r}")
        binding = BoundPathway(
            session=self,
            binding_id=identity,
            pathway_id=pathway_id,
            stage_ids=declared_stages,
        )
        self._pathway_bindings[identity] = binding
        return binding

    def bind_composition(
        self,
        composition_id: str,
        *,
        binding_id: str | None = None,
    ) -> BoundComposition:
        """Declare one exact registered executable composition."""

        self._require_declaration_phase()
        composition = self.authority.composition(composition_id)
        status = str(composition["composition_status"])
        if status not in EXECUTABLE_COMPOSITION_STATUSES:
            raise UnbindableCompositionError(
                f"composition {composition_id} has non-bindable status {status}; "
                "open a distinct candidate only for genuinely new experimental work"
            )
        identity = binding_id or f"composition:{composition_id}"
        if identity in self._composition_bindings:
            raise CausalPathwayBindingError(f"duplicate binding ID {identity!r}")
        from_id = str(composition["from_pathway_id"])
        to_id = str(composition["to_pathway_id"])
        endpoints: dict[str, BoundPathway] = {}
        endpoint_specs = (
            (
                from_id,
                tuple(str(item) for item in composition["from_stage_ids"]),
                "from",
            ),
            (to_id, tuple(str(item) for item in composition["to_stage_ids"]), "to"),
        )
        for pathway_id, stages, direction in endpoint_specs:
            if pathway_id in endpoints:
                combined = tuple(
                    dict.fromkeys((*endpoints[pathway_id].stage_ids, *stages))
                )
                endpoints[pathway_id] = BoundPathway(
                    session=self,
                    binding_id=f"{identity}:pathway:{pathway_id}",
                    pathway_id=pathway_id,
                    stage_ids=combined,
                    composition_ids=(composition_id,),
                )
                continue
            endpoints[pathway_id] = BoundPathway(
                session=self,
                binding_id=f"{identity}:{direction}:{pathway_id}",
                pathway_id=pathway_id,
                stage_ids=stages,
                composition_ids=(composition_id,),
            )
        binding = BoundComposition(
            session=self,
            binding_id=identity,
            composition=composition,
            endpoints=endpoints,
        )
        self._composition_bindings[identity] = binding
        return binding

    def declare_alternatives(
        self,
        *,
        alternative_set_id: str,
        pathway_ids: Sequence[str],
        selection_authority: str,
    ) -> AllowedPathwayAlternatives:
        """Declare allowable choices without making a choice."""

        self._require_declaration_phase()
        if not alternative_set_id or alternative_set_id in self._alternatives:
            raise CausalPathwayBindingError("alternative_set_id must be unique")
        unique_pathways = tuple(dict.fromkeys(str(item) for item in pathway_ids))
        if len(unique_pathways) < 2:
            raise CausalPathwayBindingError(
                "dynamic alternatives require at least two pathways"
            )
        for pathway_id in unique_pathways:
            self.authority.pathway(pathway_id)
        if not selection_authority:
            raise CausalPathwayBindingError("selection_authority must be explicit")
        declaration = AllowedPathwayAlternatives(
            alternative_set_id=alternative_set_id,
            pathway_ids=unique_pathways,
            selection_authority=selection_authority,
        )
        self._alternatives[alternative_set_id] = declaration
        return declaration

    def declare_candidate(
        self,
        *,
        candidate_id: str,
        candidate_kind: str,
        purpose: str,
        owner: str,
        consumed_pathway_ids: Sequence[str] = (),
        consumed_composition_ids: Sequence[str] = (),
        proposed_source_pathway_id: str | None = None,
        proposed_target_pathway_id: str | None = None,
        proposed_relation: str | None = None,
        authority: Mapping[str, str] | None = None,
        producer_residue: Sequence[str] = (),
        adapter_residue: Sequence[str] = (),
        configured_residue: Sequence[str] = (),
        evidence_owner: str,
        mechanism_evidence: Mapping[str, Any] | None = None,
        blocked_claims: Sequence[str] = (),
    ) -> CandidateDeclaration:
        """Declare experimental work without altering admitted authorities."""

        self._require_declaration_phase()
        if not candidate_id or candidate_id in self._candidates:
            raise InvalidCandidateError("candidate_id must be non-empty and unique")
        try:
            self.authority.pathway(candidate_id)
        except UnknownPathwayError:
            pass
        else:
            raise InvalidCandidateError(
                "candidate ID collides with an admitted pathway"
            )
        try:
            self.authority.composition(candidate_id)
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
            self.authority.pathway(pathway_id)
        for composition_id in consumed_compositions:
            composition = self.authority.composition(composition_id)
            if composition["composition_status"] not in EXECUTABLE_COMPOSITION_STATUSES:
                raise InvalidCandidateError(
                    f"candidate cannot consume non-executable composition {composition_id}"
                )
        parsed_evidence = (
            CandidateMechanismEvidence.from_record(mechanism_evidence)
            if mechanism_evidence is not None
            else None
        )
        invalid_relabel_conflicts: tuple[Mapping[str, Any], ...] = ()
        if candidate_kind == "composition":
            if not proposed_source_pathway_id or not proposed_target_pathway_id:
                raise InvalidCandidateError(
                    "composition candidates require explicit source and target pathways"
                )
            self.authority.pathway(proposed_source_pathway_id)
            self.authority.pathway(proposed_target_pathway_id)
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
            invalid_relabel_conflicts = self.authority.invalid_relabels_for_endpoints(
                proposed_source_pathway_id,
                proposed_target_pathway_id,
            )
            normalized_relation = _normalized_claim_text(proposed_relation)
            blocked_relabels = {
                str(relabel)
                for composition in invalid_relabel_conflicts
                for relabel in composition["blocked_relabels"]
            }
            restated = sorted(
                relabel
                for relabel in blocked_relabels
                if _normalized_claim_text(relabel) in normalized_relation
            )
            if restated:
                raise InvalidCandidateError(
                    "candidate relation restates registered invalid relabels: "
                    f"{restated}"
                )
            if invalid_relabel_conflicts and parsed_evidence is None:
                conflict_ids = sorted(
                    str(item["composition_id"]) for item in invalid_relabel_conflicts
                )
                raise InvalidCandidateError(
                    "candidate endpoint pair conflicts with invalid relabel rows "
                    f"{conflict_ids}; distinct content-addressed mechanism "
                    "evidence is required"
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
            parsed_evidence.assert_current(
                self.authority.repository_root,
                candidate_kind=candidate_kind,
                proposed_source_pathway_id=proposed_source_pathway_id,
                proposed_target_pathway_id=proposed_target_pathway_id,
                proposed_relation=proposed_relation,
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
                    "candidate relation is admitted",
                    "candidate relation is native",
                    "candidate declaration is promotion",
                )
            )
        )
        declaration = CandidateDeclaration(
            _session=self,
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
            invalid_relabel_conflict_ids=tuple(
                str(item["composition_id"]) for item in invalid_relabel_conflicts
            ),
        )
        self._candidates[candidate_id] = declaration
        return declaration


def unbound_execution_classification() -> Mapping[str, Any]:
    """Return the mandatory provenance classification for legacy direct calls."""

    return MappingProxyType(
        {
            "causal_pathway_provenance": "unbound",
            "claim_qualified": False,
            "accepted_binding_receipt": False,
        }
    )

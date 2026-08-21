"""Content-addressed callable and binding identities.

This module owns source verification and identity derivation only. It does not
interpret claims, load causal authorities, or depend on binding sessions.
"""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, cast


class CausalPathwayBindingError(ValueError):
    """Base error for fail-closed binding operations."""


class AuthorityDriftError(CausalPathwayBindingError):
    """Raised when a knowledge or source-link authority no longer matches."""


class SymbolBindingError(CausalPathwayBindingError):
    """Raised when an exact stage symbol cannot be linked safely."""


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


def _canonical_value_digest(value: Any) -> str:
    """Return a canonical SHA-256 digest for any JSON-compatible value."""

    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


_BINDING_SEMANTIC_SYMBOL_FIELDS: Final[tuple[str, ...]] = (
    "symbol_id",
    "module",
    "qualified_symbol",
    "binding_role",
    "call_kind",
    "required_keyword_arguments",
)


def binding_semantics_digest(bindings: Mapping[str, Any]) -> str:
    """Digest the stage/crossing meaning independently of source-file hashes."""

    def semantic_symbol(symbol: Mapping[str, Any]) -> dict[str, Any]:
        return {
            field: deepcopy(symbol.get(field, {} if field.endswith("arguments") else ""))
            for field in _BINDING_SEMANTIC_SYMBOL_FIELDS
        }

    stage_bindings: list[dict[str, Any]] = [
        {
            "pathway_id": str(stage.get("pathway_id", "")),
            "stage_id": str(stage.get("stage_id", "")),
            "symbols": sorted(
                (
                    semantic_symbol(symbol)
                    for symbol in stage.get("symbols", [])
                    if isinstance(symbol, Mapping)
                ),
                key=lambda symbol: str(symbol["symbol_id"]),
            ),
        }
        for stage in bindings.get("stage_bindings", [])
        if isinstance(stage, Mapping)
    ]
    stage_bindings.sort(
        key=lambda stage: (str(stage["pathway_id"]), str(stage["stage_id"]))
    )
    crossing_bindings: list[dict[str, Any]] = []
    for crossing in bindings.get("composition_crossing_bindings", []):
        if not isinstance(crossing, Mapping):
            continue
        symbol = crossing.get("symbol", {})
        crossing_bindings.append(
            {
                "composition_id": str(crossing.get("composition_id", "")),
                "crossing_kind": str(crossing.get("crossing_kind", "")),
                "source_pathway_id": str(crossing.get("source_pathway_id", "")),
                "source_argument_name": str(
                    crossing.get("source_argument_name", "")
                ),
                "target_pathway_id": str(crossing.get("target_pathway_id", "")),
                "symbol": semantic_symbol(symbol)
                if isinstance(symbol, Mapping)
                else {},
            }
        )
    crossing_bindings.sort(key=lambda crossing: str(crossing["composition_id"]))
    return _canonical_value_digest(
        {
            "stage_bindings": stage_bindings,
            "composition_crossing_bindings": crossing_bindings,
        }
    )


def binding_source_manifest_digest(bindings: Mapping[str, Any]) -> str:
    """Digest the exact source paths and content hashes consumed by a map."""

    source_records: set[tuple[str, str]] = set()
    for stage in bindings.get("stage_bindings", []):
        if not isinstance(stage, Mapping):
            continue
        for symbol in stage.get("symbols", []):
            if isinstance(symbol, Mapping):
                source_records.add(
                    (
                        str(symbol.get("source_path", "")),
                        str(symbol.get("source_sha256", "")),
                    )
                )
    for crossing in bindings.get("composition_crossing_bindings", []):
        if not isinstance(crossing, Mapping):
            continue
        symbol = crossing.get("symbol", {})
        if isinstance(symbol, Mapping):
            source_records.add(
                (
                    str(symbol.get("source_path", "")),
                    str(symbol.get("source_sha256", "")),
                )
            )
    return _canonical_value_digest(
        [
            {"source_path": path, "source_sha256": digest}
            for path, digest in sorted(source_records)
        ]
    )


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


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


@dataclass
class _VerifiedSourceFile:
    """One fully verified source file with a cheap change-detection stamp."""

    path: Path
    expected_sha256: str
    stamp: tuple[int, int]

    @staticmethod
    def _stamp(path: Path) -> tuple[int, int]:
        try:
            status = path.stat()
        except OSError as exc:
            raise SymbolBindingError(
                f"binding source {path} is absent or unreadable"
            ) from exc
        return status.st_mtime_ns, status.st_size

    @classmethod
    def verify(cls, path: Path, *, expected_sha256: str) -> _VerifiedSourceFile:
        """Hash one source and bind the result to a stable file stamp."""

        before = cls._stamp(path)
        if sha256_file(path) != expected_sha256:
            raise SymbolBindingError(f"binding source {path} content is stale")
        after = cls._stamp(path)
        if before != after:
            raise SymbolBindingError(
                f"binding source {path} changed during identity verification"
            )
        return cls(path=path, expected_sha256=expected_sha256, stamp=after)

    def assert_current(self) -> None:
        """Reuse verification while the file stamp is unchanged."""

        current = self._stamp(self.path)
        if current == self.stamp:
            return
        if sha256_file(self.path) != self.expected_sha256:
            raise SymbolBindingError(
                f"binding source {self.path} content is stale"
            )
        verified = self._stamp(self.path)
        if current != verified:
            raise SymbolBindingError(
                f"binding source {self.path} changed during identity verification"
            )
        self.stamp = verified


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

    def _validated_definition(
        self,
        target: Callable[..., Any],
    ) -> tuple[Callable[..., Any], str, str]:
        definition = _callable_definition(target)
        module = str(getattr(definition, "__module__", ""))
        qualified_symbol = str(getattr(definition, "__qualname__", ""))
        if module != self.module or qualified_symbol != self.qualified_symbol:
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} resolved as "
                f"{module}.{qualified_symbol}, expected "
                f"{self.module}.{self.qualified_symbol}"
            )
        return definition, module, qualified_symbol

    def _resolved_source_path(
        self,
        definition: Callable[..., Any],
        repository_root: Path,
        *,
        expected_source: Path | None = None,
    ) -> Path:
        source_file = inspect.getsourcefile(definition)
        if source_file is None:
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} has no inspectable source file"
            )
        if expected_source is None:
            expected_source = (repository_root / self.source_path).resolve()
        actual_source = Path(source_file).resolve()
        if actual_source != expected_source:
            raise SymbolBindingError(
                f"binding symbol {self.symbol_id!r} resolved from {actual_source}, "
                f"expected {expected_source}"
            )
        return actual_source

    def _identity_from_verified_source(
        self,
        definition: Callable[..., Any],
        *,
        module: str,
        qualified_symbol: str,
    ) -> CallableIdentity:
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

    def callable_identity(
        self,
        target: Callable[..., Any],
        repository_root: Path,
    ) -> CallableIdentity:
        """Validate and describe a resolved callable against its source link."""

        definition, module, qualified_symbol = self._validated_definition(target)
        source = self._resolved_source_path(definition, repository_root)
        source_file = _VerifiedSourceFile.verify(
            source,
            expected_sha256=self.source_sha256,
        )
        identity = self._identity_from_verified_source(
            definition,
            module=module,
            qualified_symbol=qualified_symbol,
        )
        source_file.assert_current()
        return identity

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
class _CallableIdentityGuard:
    """Cached callable identity guarded by one verified source file."""

    symbol: SourceSymbolBinding
    expected_definition: Callable[..., Any]
    source_file: _VerifiedSourceFile
    identity: CallableIdentity
    identity_record: Mapping[str, Any]

    def assert_current(self, target: Callable[..., Any]) -> Mapping[str, Any]:
        """Reject callable replacement and re-hash only after source stat drift."""

        definition, _, _ = self.symbol._validated_definition(target)
        if definition is not self.expected_definition:
            raise SymbolBindingError(
                f"binding {self.symbol.symbol_id!r} callable identity changed"
            )
        self.source_file.assert_current()
        return self.identity_record


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


__all__ = [
    "AuthorityDriftError",
    "CallableIdentity",
    "CausalPathwayBindingError",
    "CompositionCrossingBinding",
    "SourceSymbolBinding",
    "SymbolBindingError",
    "binding_semantics_digest",
    "binding_source_manifest_digest",
    "canonical_digest",
    "sha256_file",
]

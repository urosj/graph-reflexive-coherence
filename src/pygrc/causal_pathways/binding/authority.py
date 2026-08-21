"""Accepted causal-pathway authority and binding-map admission."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

from .effects import EffectOutcomeContract
from .identity import (
    AuthorityDriftError,
    CausalPathwayBindingError,
    CompositionCrossingBinding,
    SourceSymbolBinding,
    SymbolBindingError,
    _canonical_value_digest,
    binding_semantics_digest,
    binding_source_manifest_digest,
    canonical_digest,
    sha256_file,
)

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


class UnknownPathwayError(CausalPathwayBindingError):
    """Raised when a pathway is absent from the admitted registry."""


class UnknownCompositionError(CausalPathwayBindingError):
    """Raised when a composition is absent from the admitted matrix."""


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


@dataclass(frozen=True)
class BindingAcceptanceAnchor:
    """Independently trusted acceptance decision for one exact binding map."""

    anchor_id: str
    accepted_binding_map_digest: str
    accepted_source_revision: str
    accepted_binding_semantics_digest: str
    accepted_source_manifest_digest: str
    effect_outcome_contracts_digest: str
    anchor_digest: str
    _effect_outcome_contracts: Mapping[str, EffectOutcomeContract] = field(
        repr=False,
        compare=False,
    )
    _record: Mapping[str, Any] = field(repr=False, compare=False)

    @classmethod
    def from_record(
        cls,
        record: Mapping[str, Any],
        *,
        trusted_anchor_digest: str,
    ) -> BindingAcceptanceAnchor:
        """Validate an anchor against a digest supplied outside the bundle."""

        if re.fullmatch(r"[0-9a-f]{64}", trusted_anchor_digest) is None:
            raise AuthorityDriftError(
                "trusted binding-acceptance anchor digest must be lowercase SHA-256"
            )
        declared_digest = str(record.get("anchor_digest", ""))
        actual_digest = canonical_digest(record, excluding="anchor_digest")
        if declared_digest != trusted_anchor_digest or actual_digest != declared_digest:
            raise AuthorityDriftError(
                "binding-acceptance anchor is not the independently trusted record"
            )
        expected_header = {
            "artifact": "causal-pathway-binding-acceptance-anchor",
            "schema_version": "causal_pathway_binding_acceptance_anchor_v1",
            "status": "accepted",
            "automatic_re_admission": False,
            "candidate_bundle_auto_discovery": False,
        }
        if any(record.get(field) != value for field, value in expected_header.items()):
            raise AuthorityDriftError(
                "binding-acceptance anchor header or review status is invalid"
            )
        anchor_id = str(record.get("anchor_id", ""))
        map_digest = str(record.get("accepted_binding_map_digest", ""))
        source_revision = str(record.get("accepted_source_revision", ""))
        semantics_digest = str(record.get("accepted_binding_semantics_digest", ""))
        source_manifest_digest = str(
            record.get("accepted_source_manifest_digest", "")
        )
        contract_records = record.get("effect_outcome_contracts")
        if not isinstance(contract_records, list):
            raise AuthorityDriftError(
                "binding-acceptance anchor lacks effect-outcome contracts"
            )
        contracts: dict[str, EffectOutcomeContract] = {}
        contract_ids: set[str] = set()
        for contract_record in contract_records:
            if not isinstance(contract_record, Mapping):
                raise AuthorityDriftError(
                    "effect-outcome contract must be a JSON object"
                )
            contract = EffectOutcomeContract.from_record(contract_record)
            if contract.symbol_id in contracts or contract.contract_id in contract_ids:
                raise AuthorityDriftError(
                    "effect-outcome contract symbol and contract IDs must be unique"
                )
            contracts[contract.symbol_id] = contract
            contract_ids.add(contract.contract_id)
        declared_contracts_digest = str(
            record.get("effect_outcome_contracts_digest", "")
        )
        if (
            record.get("effect_outcome_contract_count") != len(contracts)
            or _canonical_value_digest(
                [
                    contracts[symbol_id].to_record()
                    for symbol_id in sorted(contracts)
                ]
            )
            != declared_contracts_digest
        ):
            raise AuthorityDriftError(
                "binding-acceptance effect-outcome contract set is stale"
            )
        if not anchor_id or any(
            re.fullmatch(r"[0-9a-f]{64}", value) is None
            for value in (map_digest, semantics_digest, source_manifest_digest)
        ):
            raise AuthorityDriftError(
                "binding-acceptance anchor identities are missing or malformed"
            )
        if re.fullmatch(r"[0-9a-f]{40}", source_revision) is None:
            raise AuthorityDriftError(
                "binding-acceptance anchor source revision is malformed"
            )
        return cls(
            anchor_id=anchor_id,
            accepted_binding_map_digest=map_digest,
            accepted_source_revision=source_revision,
            accepted_binding_semantics_digest=semantics_digest,
            accepted_source_manifest_digest=source_manifest_digest,
            effect_outcome_contracts_digest=declared_contracts_digest,
            anchor_digest=declared_digest,
            _effect_outcome_contracts=MappingProxyType(contracts),
            _record=MappingProxyType(deepcopy(dict(record))),
        )

    def to_record(self) -> dict[str, Any]:
        """Return a copy of the externally supplied acceptance decision."""

        return deepcopy(dict(self._record))

    def assert_accepts(self, bindings: Mapping[str, Any]) -> None:
        """Reject a self-consistent map that differs from the reviewed anchor."""

        actual = {
            "binding_map_digest": str(bindings.get("binding_map_digest", "")),
            "source_revision": str(bindings.get("source_revision", "")),
            "binding_semantics_digest": binding_semantics_digest(bindings),
            "source_manifest_digest": binding_source_manifest_digest(bindings),
        }
        expected = {
            "binding_map_digest": self.accepted_binding_map_digest,
            "source_revision": self.accepted_source_revision,
            "binding_semantics_digest": self.accepted_binding_semantics_digest,
            "source_manifest_digest": self.accepted_source_manifest_digest,
        }
        mismatched = [field for field, value in expected.items() if actual[field] != value]
        if mismatched:
            raise AuthorityDriftError(
                "binding map is self-consistent but pending independent review: "
                f"anchor mismatches {mismatched}"
            )
        known_symbol_ids = {
            str(symbol.get("symbol_id", ""))
            for stage in bindings.get("stage_bindings", [])
            if isinstance(stage, Mapping)
            for symbol in stage.get("symbols", [])
            if isinstance(symbol, Mapping)
        }
        known_symbol_ids.update(
            str(symbol.get("symbol_id", ""))
            for crossing in bindings.get("composition_crossing_bindings", [])
            if isinstance(crossing, Mapping)
            for symbol in (crossing.get("symbol", {}),)
            if isinstance(symbol, Mapping)
        )
        unknown_contract_symbols = sorted(
            set(self._effect_outcome_contracts) - known_symbol_ids
        )
        if unknown_contract_symbols:
            raise AuthorityDriftError(
                "binding-acceptance anchor has contracts for unknown symbols: "
                f"{unknown_contract_symbols}"
            )

    def effect_outcome_contract(
        self,
        symbol_id: str,
    ) -> EffectOutcomeContract | None:
        return self._effect_outcome_contracts.get(symbol_id)


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
        binding_acceptance_anchor: BindingAcceptanceAnchor | None = None,
        trusted_anchor_digest: str | None = None,
    ) -> None:
        self._repository_root = repository_root
        self._documents = MappingProxyType(dict(documents))
        self._pathways = MappingProxyType(dict(pathways))
        self._compositions = MappingProxyType(dict(compositions))
        self._stage_symbols = MappingProxyType(dict(stage_symbols))
        self._composition_crossings = MappingProxyType(dict(composition_crossings))
        if binding_acceptance_anchor is None:
            if trusted_anchor_digest is not None:
                raise AuthorityDriftError(
                    "an independently trusted digest requires its acceptance anchor"
                )
            validated_anchor = None
        else:
            if trusted_anchor_digest is None:
                raise AuthorityDriftError(
                    "an acceptance anchor requires its independently trusted digest"
                )
            validated_anchor = BindingAcceptanceAnchor.from_record(
                binding_acceptance_anchor.to_record(),
                trusted_anchor_digest=trusted_anchor_digest,
            )
            validated_anchor.assert_accepts(documents["bindings"])
        self._binding_acceptance_anchor = validated_anchor
        self._trusted_anchor_digest = trusted_anchor_digest

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

    @property
    def binding_acceptance_status(self) -> str:
        """Return whether this self-consistent authority is externally accepted."""

        return (
            "accepted"
            if self._binding_acceptance_anchor is not None
            else "pending_independent_review"
        )

    @property
    def binding_acceptance_anchor_digest(self) -> str:
        """Return the independently trusted acceptance-anchor identity."""

        if self._binding_acceptance_anchor is None:
            return ""
        return self._binding_acceptance_anchor.anchor_digest

    @property
    def effect_outcome_contracts_digest(self) -> str:
        """Return the trusted mechanism-effect contract-set identity."""

        if self._binding_acceptance_anchor is None:
            return ""
        return self._binding_acceptance_anchor.effect_outcome_contracts_digest

    def effect_outcome_contract(
        self,
        symbol_id: str,
    ) -> EffectOutcomeContract | None:
        """Return the reviewed contract for a symbol, or no contract."""

        if self._binding_acceptance_anchor is None:
            return None
        return self._binding_acceptance_anchor.effect_outcome_contract(symbol_id)

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
                "binding_acceptance_status": self.binding_acceptance_status,
                "binding_acceptance_anchor_digest": (
                    self.binding_acceptance_anchor_digest
                ),
                "effect_outcome_contracts_digest": (
                    self.effect_outcome_contracts_digest
                ),
            }
        )

    def assert_current(self) -> None:
        """Fail closed if any consumed authority or source link has drifted."""

        current = type(self).load(
            self.repository_root,
            acceptance_anchor=(
                self._binding_acceptance_anchor.to_record()
                if self._binding_acceptance_anchor is not None
                else None
            ),
            trusted_anchor_digest=self._trusted_anchor_digest,
        )
        if dict(current.artifact_identities()) != dict(self.artifact_identities()):
            raise AuthorityDriftError(
                "loaded causal-pathway authority is no longer current"
            )
        if self._binding_acceptance_anchor is None:
            raise AuthorityDriftError(
                "self-consistent binding authority is pending independent review; "
                "claim artifacts require an independently supplied acceptance anchor"
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

    def callable_is_registered(self, symbol: SourceSymbolBinding) -> bool:
        """Return whether a candidate symbol aliases an admitted callable."""

        registered = (
            symbol
            for symbols in self._stage_symbols.values()
            for symbol in symbols
        )
        crossings = (
            crossing.symbol for crossing in self._composition_crossings.values()
        )
        candidate_source = (
            self.repository_root / symbol.source_path
        ).resolve()
        return any(
            existing.qualified_symbol == symbol.qualified_symbol
            and (
                existing.module == symbol.module
                or (self.repository_root / existing.source_path).resolve()
                == candidate_source
            )
            for existing in (*registered, *crossings)
        )

    @classmethod
    def load(
        cls,
        repository_root: str | Path,
        *,
        acceptance_anchor: Mapping[str, Any] | None = None,
        trusted_anchor_digest: str | None = None,
    ) -> CausalPathwayAuthority:
        """Load self-consistent authorities and optionally establish acceptance."""

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
        parsed_anchor: BindingAcceptanceAnchor | None = None
        if acceptance_anchor is not None or trusted_anchor_digest is not None:
            if acceptance_anchor is None or trusted_anchor_digest is None:
                raise AuthorityDriftError(
                    "acceptance anchor and independently trusted digest are both required"
                )
            parsed_anchor = BindingAcceptanceAnchor.from_record(
                acceptance_anchor,
                trusted_anchor_digest=trusted_anchor_digest,
            )
            parsed_anchor.assert_accepts(bindings)
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
            binding_acceptance_anchor=parsed_anchor,
            trusted_anchor_digest=trusted_anchor_digest,
        )

__all__ = [
    "BindingAcceptanceAnchor",
    "CausalPathwayAuthority",
    "UnknownCompositionError",
    "UnknownPathwayError",
]

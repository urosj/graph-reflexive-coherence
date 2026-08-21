"""Trusted mechanism-effect contracts and conservative result classification."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final, Protocol

from .identity import (
    AuthorityDriftError,
    _callable_bound_owner,
    _canonical_value_digest,
    canonical_digest,
)

RETURN_CATEGORIES: Final[tuple[str, ...]] = (
    "false",
    "true",
    "none",
    "empty",
    "other",
)
EFFECT_OUTCOMES: Final[frozenset[str]] = frozenset(
    {"committed", "observed", "rejected", "no_op", "unknown"}
)
CLAIM_QUALIFYING_EFFECT_OUTCOMES: Final[frozenset[str]] = frozenset(
    {"committed", "observed"}
)


def _return_category(result: object) -> str:
    """Classify only stable Python return shapes, without semantic inference."""

    if result is False:
        return "false"
    if result is True:
        return "true"
    if result is None:
        return "none"
    if isinstance(result, (str, bytes, tuple, list, dict, set, frozenset)) and not result:
        return "empty"
    return "other"


@dataclass(frozen=True)
class EffectOutcomeContract:
    """Trusted return-to-effect meaning for one exact mechanism symbol."""

    contract_id: str
    symbol_id: str
    effect_kind: str
    return_outcomes: Mapping[str, str]
    claim_qualifying_outcomes: frozenset[str]
    effect_probe: Mapping[str, Any] | None
    effect_contract_digest: str

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> EffectOutcomeContract:
        return_outcomes = record.get("return_outcomes")
        qualifying = record.get("claim_qualifying_outcomes")
        raw_probe = record.get("effect_probe")
        probe_outcomes: set[Any] = set()
        probe_is_valid = raw_probe is None
        if isinstance(raw_probe, Mapping):
            probe_kind = raw_probe.get("kind")
            if probe_kind == "boolean_attribute":
                probe_is_valid = (
                    set(raw_probe)
                    == {"kind", "attribute", "true_outcome", "false_outcome"}
                    and isinstance(raw_probe.get("attribute"), str)
                    and bool(raw_probe.get("attribute"))
                    and raw_probe.get("true_outcome") in EFFECT_OUTCOMES
                    and raw_probe.get("false_outcome") in EFFECT_OUTCOMES
                )
                probe_outcomes = {
                    raw_probe.get("true_outcome"),
                    raw_probe.get("false_outcome"),
                }
            elif probe_kind == "bound_instance_snapshot_digest":
                probe_is_valid = (
                    set(raw_probe)
                    == {
                        "kind",
                        "snapshot_method",
                        "changed_outcome",
                        "unchanged_outcome",
                    }
                    and isinstance(raw_probe.get("snapshot_method"), str)
                    and bool(raw_probe.get("snapshot_method"))
                    and raw_probe.get("changed_outcome") in EFFECT_OUTCOMES
                    and raw_probe.get("unchanged_outcome") in EFFECT_OUTCOMES
                )
                probe_outcomes = {
                    raw_probe.get("changed_outcome"),
                    raw_probe.get("unchanged_outcome"),
                }
        if (
            not isinstance(return_outcomes, Mapping)
            or set(return_outcomes) != set(RETURN_CATEGORIES)
            or any(value not in EFFECT_OUTCOMES for value in return_outcomes.values())
        ):
            raise AuthorityDriftError(
                "effect-outcome contract must classify every stable return category"
            )
        if (
            not isinstance(qualifying, list)
            or len(qualifying) != len(set(qualifying))
            or not set(qualifying) <= CLAIM_QUALIFYING_EFFECT_OUTCOMES
            or not set(qualifying)
            <= (set(return_outcomes.values()) | probe_outcomes)
        ):
            raise AuthorityDriftError(
                "effect-outcome contract has invalid claim-qualifying outcomes"
            )
        if not probe_is_valid:
            raise AuthorityDriftError(
                "effect-outcome contract has an invalid result probe"
            )
        contract_id = str(record.get("contract_id", ""))
        symbol_id = str(record.get("symbol_id", ""))
        effect_kind = str(record.get("effect_kind", ""))
        declared_digest = str(record.get("effect_contract_digest", ""))
        if (
            not contract_id
            or not symbol_id
            or not effect_kind
            or re.fullmatch(r"[0-9a-f]{64}", declared_digest) is None
            or canonical_digest(record, excluding="effect_contract_digest")
            != declared_digest
        ):
            raise AuthorityDriftError(
                "effect-outcome contract identity or content digest is invalid"
            )
        return cls(
            contract_id=contract_id,
            symbol_id=symbol_id,
            effect_kind=effect_kind,
            return_outcomes=MappingProxyType(dict(return_outcomes)),
            claim_qualifying_outcomes=frozenset(str(item) for item in qualifying),
            effect_probe=(
                None
                if raw_probe is None
                else MappingProxyType(dict(raw_probe))
            ),
            effect_contract_digest=declared_digest,
        )

    def to_record(self) -> dict[str, Any]:
        record = {
            "contract_id": self.contract_id,
            "symbol_id": self.symbol_id,
            "effect_kind": self.effect_kind,
            "return_outcomes": dict(self.return_outcomes),
            "claim_qualifying_outcomes": sorted(self.claim_qualifying_outcomes),
            "effect_contract_digest": self.effect_contract_digest,
        }
        if self.effect_probe is not None:
            record["effect_probe"] = dict(self.effect_probe)
        return record

    @staticmethod
    def _bound_instance_snapshot_digest(
        target: Callable[..., Any],
        snapshot_method: str,
    ) -> str | None:
        owner = _callable_bound_owner(target)
        snapshot = getattr(owner, snapshot_method, None)
        if not callable(snapshot):
            return None
        try:
            return _canonical_value_digest(snapshot())
        except Exception:  # noqa: BLE001 - probe failure must classify as unknown
            return None

    def capture_pre_call_evidence(
        self,
        target: Callable[..., Any],
    ) -> Mapping[str, Any] | None:
        """Capture trusted pre-call evidence without changing call semantics."""

        if (
            self.effect_probe is None
            or self.effect_probe.get("kind")
            != "bound_instance_snapshot_digest"
        ):
            return None
        snapshot_method = str(self.effect_probe["snapshot_method"])
        return MappingProxyType(
            {
                "before_digest": self._bound_instance_snapshot_digest(
                    target,
                    snapshot_method,
                )
            }
        )

    def classify(
        self,
        result: object,
        *,
        target: Callable[..., Any],
        pre_call_evidence: Mapping[str, Any] | None,
    ) -> tuple[str, str, bool, Mapping[str, Any] | None]:
        """Return category, explicit effect, claim eligibility, and probe evidence."""

        category = _return_category(result)
        outcome = self.return_outcomes[category]
        effect_evidence: Mapping[str, Any] | None = None
        if (
            self.effect_probe is not None
            and self.effect_probe.get("kind") == "boolean_attribute"
        ):
            attribute = str(self.effect_probe["attribute"])
            observed = getattr(result, attribute, None)
            observed_boolean = observed if isinstance(observed, bool) else None
            effect_evidence = MappingProxyType(
                {
                    "kind": "boolean_attribute",
                    "attribute": attribute,
                    "observed_boolean": observed_boolean,
                }
            )
            if observed_boolean is True:
                outcome = str(self.effect_probe["true_outcome"])
            elif observed_boolean is False:
                outcome = str(self.effect_probe["false_outcome"])
            else:
                outcome = "unknown"
        elif (
            self.effect_probe is not None
            and self.effect_probe.get("kind")
            == "bound_instance_snapshot_digest"
        ):
            snapshot_method = str(self.effect_probe["snapshot_method"])
            before_digest = (
                pre_call_evidence.get("before_digest")
                if pre_call_evidence is not None
                else None
            )
            after_digest = self._bound_instance_snapshot_digest(
                target,
                snapshot_method,
            )
            changed = (
                before_digest != after_digest
                if isinstance(before_digest, str)
                and isinstance(after_digest, str)
                else None
            )
            effect_evidence = MappingProxyType(
                {
                    "kind": "bound_instance_snapshot_digest",
                    "snapshot_method": snapshot_method,
                    "before_digest": before_digest,
                    "after_digest": after_digest,
                    "changed": changed,
                }
            )
            if changed is True:
                outcome = str(self.effect_probe["changed_outcome"])
            elif changed is False:
                outcome = str(self.effect_probe["unchanged_outcome"])
            else:
                outcome = "unknown"
        return (
            category,
            outcome,
            outcome in self.claim_qualifying_outcomes,
            effect_evidence,
        )


class _EffectContractProvider(Protocol):
    """Narrow provider needed to classify one exact symbol result."""

    def effect_outcome_contract(
        self,
        symbol_id: str,
    ) -> EffectOutcomeContract | None: ...


def _classify_returned_effect(
    authority: _EffectContractProvider,
    symbol_id: str,
    result: object,
    *,
    target: Callable[..., Any],
    pre_call_evidence: Mapping[str, Any] | None,
) -> tuple[str, str | None, str, str, bool, Mapping[str, Any] | None]:
    """Apply only the trusted exact-symbol outcome contract to a return."""

    contract = authority.effect_outcome_contract(symbol_id)
    if contract is None:
        return _return_category(result), None, "unreviewed", "unknown", False, None
    category, outcome, qualifying, effect_evidence = contract.classify(
        result,
        target=target,
        pre_call_evidence=pre_call_evidence,
    )
    return (
        category,
        contract.contract_id,
        contract.effect_kind,
        outcome,
        qualifying,
        effect_evidence,
    )


__all__ = [
    "CLAIM_QUALIFYING_EFFECT_OUTCOMES",
    "EFFECT_OUTCOMES",
    "RETURN_CATEGORIES",
    "EffectOutcomeContract",
]

"""Candidate C reference transport binding (P9-4.1).

The complete profile owns W_C_tr. E_H and E_M independently consume that
map; neither a live geometry nor a retained Hodge can supply mobility.
This local binding does not admit a selector, solve, step or lifecycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .grc_v4_codec import (
    JSONValue,
    V4SchemaError,
    canonical_json_bytes,
    decode_canonical_json,
    json_value,
    payload_identity,
)
from .grc_v4_geometry import GRCV4Graph, OneFormHodge, _identity
from .grc_v4_profile import CandidateCParams, GRCV4Profile
from .grc_v4_transport import CandidateCMobility, candidate_c_structural_hodge


@dataclass(frozen=True, slots=True)
class CandidateCTransport:
    """Fixed-graph/profile sibling constructors, with reconstructible inputs.

    Constructor identities name the typed recipe and its exact inputs. They
    differ from operator identities and the complete binding identity: eta
    changes only E_M; selector/geometry controls change the complete profile
    binding without changing either reference constructor. The Hodge output
    is the reference Hodge, never the generated or retained stage Hodge.
    """

    graph: GRCV4Graph
    profile: GRCV4Profile
    structural_hodge: OneFormHodge = field(init=False)
    mobility: CandidateCMobility = field(init=False)

    def __post_init__(self) -> None:
        if type(self.graph) is not GRCV4Graph or type(self.profile) is not GRCV4Profile:
            raise TypeError("C transport requires a typed graph and complete profile")
        params = self.profile.params_resolved.candidate
        if type(params) is not CandidateCParams:
            raise TypeError("C transport requires a Candidate C complete profile")
        # Both constructors enforce exact live-edge coverage. Check the declared
        # structural reference preimage too: matching dimensions is insufficient.
        hodge = candidate_c_structural_hodge(self.graph, params)
        payload_identity(
            "reference_hodge_identity_payload",
            {
                "schema_version": "grcv4-reference-hodge-identity-v1",
                "edge_weights": params.W_C_tr,
            },
            expected=self.profile.params_resolved.geometry.reference_hodge_digest,
        )
        mobility = CandidateCMobility(self.graph, params)
        object.__setattr__(self, "structural_hodge", hodge)
        object.__setattr__(self, "mobility", mobility)

    @property
    def params(self) -> CandidateCParams:
        params = self.profile.params_resolved.candidate
        assert isinstance(params, CandidateCParams)
        return params

    def _constructor_payload(self, *, mobility: bool) -> dict[str, JSONValue]:
        params = self.params
        payload: dict[str, JSONValue] = {
            "descriptor": "grcv4-c-reference-constructor-v1",
            "transport_id": params.transport_id,
            "constructor_id": params.E_M_policy_id
            if mobility
            else params.E_H_policy_id,
            "output_type": "physical_flux_mobility" if mobility else "one_form_hodge",
            "units_id": self.profile.params_resolved.common.units_id,
            "graph_digest": self.graph.graph_digest,
            "orientation_identity": self.graph.orientation_identity,
            "W_C_tr_content_digest": params.W_C_tr_content_digest,
        }
        if mobility:
            payload["eta_C"] = params.eta_C
        return payload

    @property
    def structural_hodge_constructor_payload(self) -> dict[str, JSONValue]:
        return self._constructor_payload(mobility=False)

    @property
    def mobility_constructor_payload(self) -> dict[str, JSONValue]:
        return self._constructor_payload(mobility=True)

    @property
    def structural_hodge_constructor_identity(self) -> str:
        return _identity(
            "grcv4-c-reference-constructor-sha256",
            self.structural_hodge_constructor_payload,
        )

    @property
    def mobility_constructor_identity(self) -> str:
        return _identity(
            "grcv4-c-reference-constructor-sha256", self.mobility_constructor_payload
        )

    @property
    def identity(self) -> str:
        return _identity("grcv4-c-reference-binding-sha256", self.to_payload())

    def to_payload(self) -> dict[str, JSONValue]:
        """Internal reconstruction record of source inputs, not a snapshot."""
        return {
            "schema_version": "grcv4-c-reference-binding-v1",
            "graph": self.graph.to_payload(),
            "profile": self.profile.to_payload(),
        }

    @classmethod
    def from_payload(cls, value: object) -> CandidateCTransport:
        payload = json_value(value)
        if (
            not isinstance(payload, dict)
            or set(payload) != {"schema_version", "graph", "profile"}
            or payload["schema_version"] != "grcv4-c-reference-binding-v1"
        ):
            raise V4SchemaError("expected exact Candidate C reference binding inputs")
        return cls(
            GRCV4Graph.from_payload(payload["graph"]),
            GRCV4Profile.from_canonical_bytes(canonical_json_bytes(payload["profile"])),
        )

    def to_canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.to_payload())

    @classmethod
    def from_canonical_bytes(cls, data: bytes | str) -> CandidateCTransport:
        return cls.from_payload(decode_canonical_json(data))

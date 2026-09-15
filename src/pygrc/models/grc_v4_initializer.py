"""Accepted one-pass target-only A construction; no total-current or lifecycle solve."""

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Self

from .grc_v4_candidate_a import CandidateADifferentialReference, _conductance
from .grc_v4_codec import (
    V4IdentityError, canonical_json_bytes, initializer_identity,
    load_initializer_schema, validate_initializer_payload,
)
from .grc_v4_geometry import (
    GRCV4ReferenceGeometry, NonfiniteGeometryError, PhysicalFlux, VertexScalar, _computed,
)
from .grc_v4_state import FrozenJSONMap, _vector

POLICY_ID = "grcv4-a-target-reference-pass-v1"
NUMERICAL_ID = "grcv4-a-reference-pass-binary64-v1"
HISTORY_POLICY = "candidate_a_target_reference_pass_initialization_log_history_v1"


class InitializerStageError(ValueError):
    """Preserve role and precise producer stage; no invented solver disposition."""
    def __init__(self, role: str, stage: str, message: str):
        super().__init__(role + ":" + stage + ": " + message)
        self.role, self.stage, self.code = role, stage, "nonfinite"


@dataclass(frozen=True, slots=True)
class CandidateAReferencePass:
    reference: GRCV4ReferenceGeometry
    differential_reference: CandidateADifferentialReference
    C: tuple[float, ...]
    role: str
    retain_derived: bool = True
    payload: FrozenJSONMap = field(init=False)

    def __post_init__(self):
        if type(self.reference) is not GRCV4ReferenceGeometry or type(self.differential_reference) is not CandidateADifferentialReference:
            raise TypeError("initializer requires typed target reference and differential recipe")
        if self.role not in ("current", "reset") or type(self.retain_derived) is not bool:
            raise ValueError("unknown initializer role or evidence choice")
        C = _vector(self.C, nonnegative=True)
        object.__setattr__(self, "C", C)
        ref, backend = self.reference, self.differential_reference
        graph, params = ref.graph, ref.profile.params_resolved.candidate
        policy = load_initializer_schema()["$defs"]["static_policy"]["const"]
        # Validate fixed recipes/profile BEFORE arithmetic, without W or current admission.
        validate_initializer_payload("target_reference", ref.to_payload())
        validate_initializer_payload("differential_reference", backend.to_payload())
        if (len(C) != len(graph.live_node_ids) or backend.graph != graph
                or backend.identity != params.descriptor_backend_id
                or backend.reference_weights != ref.edge_weights):
            raise V4IdentityError("initializer target C/graph/profile/differential preimages disagree")

        def stage(name, operation):
            try:
                return operation()
            except (NonfiniteGeometryError, OverflowError) as exc:
                raise InitializerStageError(self.role, name, str(exc)) from exc

        resource = VertexScalar(graph, C)
        D = stage("differential", lambda: backend.rebuild(resource))
        zero = PhysicalFlux(graph, (0.0,) * len(graph.live_edge_ids))
        W_base = stage("auxiliary_conductance", lambda: _conductance(graph, params, resource, D, zero))

        def mobility(weights):
            result = tuple(_computed(params.eta * w) for w in weights)
            if any(w <= 0 for w in result):
                raise NonfiniteGeometryError("positive mobility underflow; no mobility floor")
            return result

        M = stage("auxiliary_mobility", lambda: mobility(W_base))
        B = graph.incidence
        dC = tuple(sum((Fraction(B[i][e]) * Fraction(c) for i, c in enumerate(C)), Fraction())
                   for e in range(len(W_base)))
        # Zero-derivative site recipe was fixed by schema. No gauge projection.
        phi = stage("reference_potential", lambda: tuple(_computed(float(
            Fraction(params.kappa_c) * sum((Fraction(B[i][e]) * Fraction(w) * dC[e]
                                          for e, w in enumerate(W_base)), Fraction()))) for i in range(len(C))))
        flux = stage("reference_flux", lambda: tuple(_computed(float(
            -Fraction(m) * sum((Fraction(B[i][e]) * Fraction(x) for i, x in enumerate(phi)), Fraction())))
            for e, m in enumerate(M)))
        W = stage("final_conductance", lambda: _conductance(graph, params, resource, D, PhysicalFlux(graph, flux)))
        stage("final_mobility", lambda: mobility(W))
        payload = dict(schema_version="grcv4-a-reference-pass-construction-v1", role=self.role,
                       policy=policy, target_reference=ref.to_payload(), differential_reference=backend.to_payload(),
                       target_C=list(C), W_A_init=list(W),
                       derived=dict(W_base=list(W_base), Phi_base=list(phi), J_ref=list(flux)) if self.retain_derived else None)
        object.__setattr__(self, "payload", FrozenJSONMap(validate_initializer_payload("construction_payload", payload)))

    @property
    def W_A_init(self) -> tuple[float, ...]:
        return tuple(self.payload["W_A_init"])

    def to_record(self):
        payload = self.payload.to_dict()
        return dict(construction_id=initializer_identity("construction_payload", payload), payload=payload)

    @classmethod
    def from_record(cls, value: object) -> Self:
        record = validate_initializer_payload("construction_record", value)
        p = record["payload"]
        initializer_identity("construction_payload", p, expected=record["construction_id"])
        result = cls(GRCV4ReferenceGeometry.from_payload(p["target_reference"]),
                     CandidateADifferentialReference.from_payload(p["differential_reference"]),
                     p["target_C"], p["role"], p["derived"] is not None)
        if canonical_json_bytes(result.payload) != canonical_json_bytes(p):
            raise V4IdentityError("initializer output/intermediates do not recompute")
        return result


@dataclass(frozen=True, slots=True)
class CandidateAReferencePassPair:
    current: CandidateAReferencePass
    reset: CandidateAReferencePass

    def __post_init__(self):
        if type(self.current) is not CandidateAReferencePass or type(self.reset) is not CandidateAReferencePass:
            raise TypeError("initializer pair requires two computed invocations")
        if (self.current.role != "current" or self.reset.role != "reset"
                or self.current.reference != self.reset.reference
                or self.current.differential_reference != self.reset.differential_reference):
            raise V4IdentityError("initializer pair roles or fixed target inputs disagree")

    @classmethod
    def construct(cls, reference, backend, current_C, reset_C) -> Self:
        return cls(CandidateAReferencePass(reference, backend, current_C, "current"),
                   CandidateAReferencePass(reference, backend, reset_C, "reset"))

    def to_record(self):
        payload = dict(schema_version="grcv4-a-reference-pass-pair-v1",
                       current=self.current.to_record(), reset=self.reset.to_record())
        return dict(initializer_pair_id=initializer_identity("pair_payload", payload), payload=payload)

    @classmethod
    def from_record(cls, value: object) -> Self:
        data = validate_initializer_payload("pair_record", value)
        initializer_identity("pair_payload", data["payload"], expected=data["initializer_pair_id"])
        return cls(*(CandidateAReferencePass.from_record(data["payload"][r]) for r in ("current", "reset")))

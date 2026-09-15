"""Finite certified RG2b completions; no lifecycle/support authority.

The scalar reference domain and graph-general successor share ordinary-step
ownership. A fixed compact cutoff extends the lagged candidate maps;
enclosed graph transforms approximate its unique Lipschitz section. Neither a
CI root nor a previous geometry supplies that section. See P9-6.4ab-Review.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from fractions import Fraction
from functools import lru_cache
import math
from typing import Any, cast, TYPE_CHECKING

from .grc_v4_candidate_a import (
    CandidateACurrent,
    CandidateADifferentialReference,
    CandidateAWriter,
    ADMITTED_HISTORY_POLICIES,
)
from .grc_v4_candidate_c import CandidateCCurrent
from .grc_v4_ci import _Interval, _iv, _iexp, _itanh, _source
from .grc_v4_geometry import (
    GeometryStageInputs,
    GRCV4Geometry,
    OneFormHodge,
    H_profile,
    VertexScalar,
    _identity,
    _local_payload,
)
from .grc_v4_profile import RG2bParams, CandidateAParams
from .grc_v4_state import _number, FrozenJSONMap, GRCV4AuthoritativeState

if TYPE_CHECKING:
    from .grc_v4_step import OperationStage

EXTENSION = "rg2b_scalar_cubic_completion_v1:"
APPROXIMATION = "rg2b_enclosed_graph_transform_160bit_binary64_inverse64_depth16_v1"
ERROR_NORM = "rg2b_absolute_scalar_hodge_v1"
CONTAINMENT = "rg2b_derived_compact_linfty_C_W_certificate_v1"


def _graph_mode(inputs: GeometryStageInputs) -> bool:
    return getattr(
        inputs.geometry.reference.profile.params_resolved.realization,
        "extension_evaluator_id",
        "",
    ).startswith("rg2b_graph_cubic_completion_v1:")


class RG2bStageError(ValueError):
    """Fail closed on an unsupported or uncertified numerical section."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RG2bStageError(message)


@dataclass(frozen=True, slots=True)
class RG2bDomain:
    center_C: float
    center_W: float
    inner: float
    core: float
    outer: float
    h_radius: float
    section_lipschitz: float
    beat_dt: float

    def __post_init__(self) -> None:
        for name in self.__dataclass_fields__:
            object.__setattr__(self, name, _number(getattr(self, name)))
        _require(
            0 < self.inner < self.core < self.outer < self.center_C
            and self.center_W > 0
            and self.h_radius > 0
            and self.section_lipschitz > 0
            and self.beat_dt > 0,
            "invalid nested RG2b charts or positive beat configuration",
        )

    @property
    def identity(self) -> str:
        return EXTENSION + ":".join(
            getattr(self, n).hex() for n in self.__dataclass_fields__
        )

    @classmethod
    def from_identity(cls, value: object) -> RG2bDomain:
        _require(
            type(value) is str and value.startswith(EXTENSION),
            "unsupported frozen RG2b completion",
        )
        assert isinstance(value, str)
        try:
            result = cls(
                *(float.fromhex(x) for x in value[len(EXTENSION) :].split(":"))
            )
        except (TypeError, ValueError, OverflowError) as exc:
            raise RG2bStageError("invalid RG2b completion coordinates") from exc
        _require(result.identity == value, "noncanonical RG2b completion")
        return result


@lru_cache(maxsize=1)
def _ln2() -> _Interval:
    return _log_unit(Fraction(2))


def _log_unit(q: Fraction) -> _Interval:
    # q in [1,2]; log(q)=2*atanh((q-1)/(q+1)). Positive geometric tail.
    z = (q - 1) / (q + 1)
    power, total = z, Fraction()
    for n in range(64):
        total += power / (2 * n + 1)
        power *= z * z
    return _Interval(2 * total, 2 * total + 2 * power / (129 * (1 - z * z)))


def _log_point(q: Fraction) -> _Interval:
    _require(q > 0, "logarithm outside positive chart")
    exponent = q.numerator.bit_length() - q.denominator.bit_length()
    unit = q / Fraction(2) ** exponent
    if unit < 1:
        unit, exponent = unit * 2, exponent - 1
    return _log_unit(unit) + exponent * _ln2()


def _ilog(value: _Interval) -> _Interval:
    return _Interval(_log_point(value.lo).lo, _log_point(value.hi).hi)


@dataclass(frozen=True, slots=True)
class _Jet:
    """Interval chain rule for candidate maps, never a section derivative."""

    value: _Interval
    derivative: tuple[_Interval, ...] = ()

    def coerce(self, other: Any) -> _Jet:
        return (
            other
            if isinstance(other, _Jet)
            else _Jet(_iv(other), (_iv(0),) * len(self.derivative))
        )

    def __add__(self, other: Any) -> _Jet:
        other = self.coerce(other)
        return _Jet(
            self.value + other.value,
            tuple(
                a + b for a, b in zip(self.derivative, other.derivative, strict=True)
            ),
        )

    __radd__ = __add__

    def __neg__(self) -> _Jet:
        return _Jet(-self.value, tuple(-x for x in self.derivative))

    def __sub__(self, other: Any) -> _Jet:
        return self + -self.coerce(other)

    def __rsub__(self, other: Any) -> _Jet:
        return self.coerce(other) + -self

    def __mul__(self, other: Any) -> _Jet:
        other = self.coerce(other)
        return _Jet(
            self.value * other.value,
            tuple(
                a * other.value + self.value * b
                for a, b in zip(self.derivative, other.derivative, strict=True)
            ),
        )

    __rmul__ = __mul__

    def __truediv__(self, other: Any) -> _Jet:
        other = self.coerce(other)
        inverse = _iv(1) / other.value
        return _Jet(
            self.value * inverse,
            tuple(
                (a - self.value * inverse * b) * inverse
                for a, b in zip(self.derivative, other.derivative, strict=True)
            ),
        )

    def __rtruediv__(self, other: Any) -> _Jet:
        return self.coerce(other) / self

    def exp(self) -> _Jet:
        value = _iexp(self.value)
        return _Jet(value, tuple(value * d for d in self.derivative))

    def log(self) -> _Jet:
        return _Jet(_ilog(self.value), tuple(d / self.value for d in self.derivative))

    def tanh(self) -> _Jet:
        value = _itanh(self.value)
        derivative = _iv(1) - value * value
        derivative = _Interval(
            max(Fraction(), derivative.lo), min(Fraction(1), derivative.hi)
        )
        return _Jet(value, tuple(derivative * d for d in self.derivative))


def _declarations(
    inputs: GeometryStageInputs, backend: CandidateADifferentialReference | None
) -> RG2bDomain:
    if type(inputs) is not GeometryStageInputs:
        raise TypeError("RG2b requires typed captured inputs")
    ref = inputs.geometry.reference
    profile = ref.profile
    params = profile.params_resolved.realization
    approximation, norm, containment = APPROXIMATION, ERROR_NORM, CONTAINMENT
    domain_class = RG2bDomain
    if _graph_mode(inputs):
        from . import grc_v4_rg2b_graph as general

        approximation, norm, containment = (
            general.APPROXIMATION,
            general.ERROR_NORM,
            general.CONTAINMENT,
        )
        domain_class = general.RG2bGraphDomain
    _require(
        type(params) is RG2bParams
        and profile.identity_payload.profile_family_id in {"A_RG2b", "C_RG2b"}
        and params.approximation_policy_id == approximation
        and params.error_norm_id == norm
        and params.containment_certificate_id == containment
        and params.failure_policy_id == "fail_closed_on_uncertified_section_v1",
        "unsupported RG2b evaluator/error/containment declaration",
    )
    assert isinstance(params, RG2bParams)
    domain = domain_class.from_identity(params.extension_evaluator_id)
    graph = ref.graph
    _require(
        _graph_mode(inputs)
        or (
            len(graph.live_node_ids) == 2
            and len(graph.live_edge_ids) == 1
            and graph.oriented_edges[0].tail_node_id
            != graph.oriented_edges[0].head_node_id
        ),
        "initial RG2b completion requires two vertices and one non-loop edge",
    )
    _require(
        inputs.stage == "pre_read"
        and inputs.geometry == ref.geometry()
        and inputs.trial_current is None
        and inputs.current.Z_4 is None
        and inputs.reset.Z_4 is None,
        "RG2b requires reference pre-read inputs without solver/history authority",
    )
    _require(
        inputs.dt in (0, domain.beat_dt), "RG2b beat differs from frozen completion"
    )
    _require(
        all(
            v == float(i == j)
            for i, row in enumerate(ref.pairings.vertex.matrix)
            for j, v in enumerate(row)
        ),
        "initial RG2b completion requires unit vertex measure",
    )
    candidate = profile.params_resolved.candidate
    if isinstance(candidate, CandidateAParams):
        if type(backend) is not CandidateADifferentialReference:
            raise TypeError("A_RG2b requires its differential reference")
        _require(
            backend.graph == graph
            and backend.identity == candidate.descriptor_backend_id
            and backend.reference_weights == ref.edge_weights
            and domain.outer < domain.center_W
            and profile.params_resolved.lifecycle.history_policy_id in ADMITTED_HISTORY_POLICIES,
            "A_RG2b backend, positive mobility chart or writer mismatch",
        )
    else:
        if backend is not None:
            raise TypeError("C_RG2b has no A differential reference")
        _require(domain.center_W == 1, "C_RG2b has no mobility chart")
    return domain


def _coordinates(
    inputs: GeometryStageInputs, state: GRCV4AuthoritativeState
) -> tuple[Fraction, ...]:
    if _graph_mode(inputs):
        return tuple(map(Fraction, state.C + (() if state.W_A is None else state.W_A)))
    edge = inputs.geometry.reference.graph.oriented_edges[0]
    graph = inputs.geometry.reference.graph
    values = (
        state.C[graph.node_index(edge.tail_node_id)],
        state.C[graph.node_index(edge.head_node_id)],
    )
    return tuple(map(Fraction, values + (() if state.W_A is None else state.W_A)))


def _centers(inputs: GeometryStageInputs, domain: RG2bDomain) -> tuple[float, ...]:
    if _graph_mode(inputs):
        from .grc_v4_rg2b_graph import centers

        return centers(inputs, domain)
    return (domain.center_C, domain.center_C) + (
        (domain.center_W,) if inputs.current.W_A is not None else ()
    )


def _raw(
    inputs: GeometryStageInputs, domain: RG2bDomain, rank: int, values: list[_Jet]
) -> tuple[list[_Jet], _Jet, _Jet]:
    """Literal analytic scalar reduction of the full fixed-h A/C + D7 maps.

    With one edge the two WLS gradients agree exactly, so their contrast is
    zero even for nonzero beta and arbitrary host dimension/positions.
    Native current/writer owners independently execute the actual beat.
    """
    ref = inputs.geometry.reference
    p = ref.profile.params_resolved.candidate
    ct, ch, h = values[0], values[1], values[-1]
    dt = Fraction(domain.beat_dt)
    if isinstance(p, CandidateAParams):
        w = values[2]
        baseline = (
            -2
            * Fraction(p.eta)
            * w
            * (
                Fraction(p.kappa_c) * w
                + Fraction(p.kappa_Ah) * (h - ref.pairings.one_form.matrix[0][0])
            )
            * (ct - ch)
        )
        target = (
            -(Fraction(p.alpha) * (ct + ch) + Fraction(p.gamma) * baseline * baseline)
            / 2
        ).exp()
        _require(
            target.value.lo > Fraction(p.W_floor),
            "RG2b A pre-read floor chart is not strictly inactive",
        )
        contrast = (w - target) / (w + target)
        den = 1 - Fraction(p.zeta_A) * Fraction(p.chi_A) * contrast
        current = baseline / den
        flat = Fraction(p.chi_A) * contrast * current / h
        gain = Fraction(p.zeta_A)
    else:
        selected = ((ct + ch) / 2, (ct + ch) / 2) if rank == 1 else (ct, ch)
        deformation = (
            Fraction(p.kappa_M_C)
            / 2
            * ((selected[0] / p.C_ref).tanh() + (selected[1] / p.C_ref).tanh())
        ).exp()
        retained = h * deformation
        response = 1 / (1 + 2 * Fraction(p.tau_C) * retained)
        baseline = (
            -2
            * Fraction(p.eta_C)
            * Fraction(cast(float, p.W_C_tr[ref.graph.live_edge_ids[0]]))
            * Fraction(p.kappa_Phi_C)
            * retained
            * (ct - ch)
        )
        den = 1 - Fraction(p.zeta_C) * Fraction(p.chi_C) * response
        current = baseline / den
        flat = Fraction(p.chi_C) * response * current / h
        gain = Fraction(p.zeta_C)
    _require(
        den.value.lo > 0
        and den.value.hi / den.value.lo
        <= Fraction(ref.profile.params_resolved.solver.conditioning_limit),
        "RG2b whole-chart physical current block is uncertified",
    )
    f = [-dt * current, dt * current]
    _require(
        (ct + f[0]).value.lo > 0 and (ch + f[1]).value.lo > 0,
        "RG2b outer-chart continuity leaves positive resources",
    )
    if isinstance(p, CandidateAParams):
        writer_exponent = (
            -(Fraction(p.alpha) * (ct + ch) + Fraction(p.gamma) * current * current) / 2
        )
        _require(
            writer_exponent.exp().value.lo > Fraction(p.W_floor),
            "RG2b A writer floor chart is not strictly inactive",
        )
        a = _Jet(_iexp(_iv(-dt / Fraction(p.tau_A))), (_iv(0),) * len(h.derivative))
        f.append(w * (((1 - a) * (writer_exponent - w.log())).exp() - 1))
    return f, gain * flat * flat, current


@dataclass(frozen=True, slots=True)
class RG2bCertificate:
    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference | None = None
    domain: RG2bDomain = field(init=False)
    bounds: FrozenJSONMap = field(init=False)
    selector_rank: int = field(init=False)
    graph_data: Any = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        domain = _declarations(self.inputs, self.differential_reference)
        if _graph_mode(self.inputs):
            from .grc_v4_rg2b_graph import certificate, RG2bGraphDomain

            for name, value in certificate(
                self.inputs, self.differential_reference, cast(RG2bGraphDomain, domain)
            ).items():
                object.__setattr__(self, name, value)
            return
        ref = self.inputs.geometry.reference
        href = Fraction(ref.pairings.one_form.matrix[0][0])
        lower, upper = (
            href - Fraction(domain.h_radius),
            href + Fraction(domain.h_radius),
        )
        _require(
            lower > 0
            and upper / lower
            <= Fraction(ref.profile.params_resolved.solver.conditioning_limit),
            "RG2b Hodge ball is not SPD/conditioning certified",
        )
        p = ref.profile.params_resolved.candidate
        is_a = isinstance(p, CandidateAParams)
        # Admit the actual native policy/backend as well as the analytic scalar
        # reduction. Its current is a reference check, never the consumed beat.
        if is_a:
            CandidateACurrent(
                self.inputs,
                cast(CandidateADifferentialReference, self.differential_reference),
            )
        else:
            CandidateCCurrent(self.inputs)
        rank = 0
        if not isinstance(p, CandidateAParams):
            cutoff = Fraction(p.Lambda_C)
            _require(
                0 < cutoff < 2 * lower or cutoff > 2 * upper,
                "RG2b whole-ball selector stratum is uncertified",
            )
            rank = 1 if cutoff < 2 * lower else 2
        centers = (domain.center_C, domain.center_C) + (
            (domain.center_W,) if is_a else ()
        )
        boxes = [
            _Interval(
                Fraction(c) - Fraction(domain.outer),
                Fraction(c) + Fraction(domain.outer),
            )
            for c in centers
        ]
        boxes.append(_Interval(lower, upper))
        size = len(boxes)
        jets = [
            _Jet(value, tuple(_iv(int(i == j)) for j in range(size)))
            for i, value in enumerate(boxes)
        ]
        f, g, _ = _raw(self.inputs, domain, rank, jets)
        fm = max(x.value.magnitude for x in f)
        fx = max(sum(d.magnitude for d in x.derivative[:-1]) for x in f)
        fh = max(x.derivative[-1].magnitude for x in f)
        gm, gx, gh = (
            g.value.magnitude,
            sum(d.magnitude for d in g.derivative[:-1]),
            g.derivative[-1].magnitude,
        )
        cutoff_lip = Fraction(3 * (size - 1), 2) / (
            Fraction(domain.outer) - Fraction(domain.core)
        )
        fx += cutoff_lip * fm
        gx += cutoff_lip * gm
        lip = Fraction(domain.section_lipschitz)
        kh = abs(Fraction(ref.profile.params_resolved.geometry.kappa_H))
        ell = fx + fh * lip
        _require(ell < 1, "RG2b extended base map is not uniformly invertible")
        inverse = 1 / (1 - ell)
        _require(
            fm <= Fraction(domain.core) - Fraction(domain.inner),
            "RG2b K_minus containment is uncertified",
        )
        _require(
            kh * gm <= Fraction(domain.h_radius),
            "RG2b graph transform exceeds section value radius",
        )
        _require(
            kh * (gx + gh * lip) * inverse <= lip,
            "RG2b Lipschitz self-map is uncertified",
        )
        q = kh * (gh + (gx + gh * lip) * inverse * fh)
        _require(q < 1, "RG2b C0 graph transform is not contractive")
        result = dict(
            source_upper=gm,
            source_X_lipschitz=gx,
            source_h_lipschitz=gh,
            base_displacement_upper=fm,
            base_X_lipschitz=fx,
            base_h_lipschitz=fh,
            inverse_displacement_lipschitz=ell,
            inverse_lipschitz=inverse,
            contraction_upper=q,
            typed_geometry_gain=kh,
            section_lipschitz=lip,
            section_radius=Fraction(domain.h_radius),
            cutoff_lipschitz=cutoff_lip,
        )
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "selector_rank", rank)
        object.__setattr__(
            self, "bounds", FrozenJSONMap({k: str(v) for k, v in result.items()})
        )


def _cutoff(x: Fraction, center: float, domain: RG2bDomain) -> Fraction:
    distance = abs(x - Fraction(center))
    if distance <= Fraction(domain.core):
        return Fraction(1)
    if distance >= Fraction(domain.outer):
        return Fraction()
    u = (distance - Fraction(domain.core)) / (
        Fraction(domain.outer) - Fraction(domain.core)
    )
    return 1 - 3 * u * u + 2 * u * u * u


def _extended(
    cert: RG2bCertificate, x: tuple[Fraction, ...], h: _Interval
) -> tuple[list[_Interval], _Interval]:
    d = cert.domain
    centers = (d.center_C, d.center_C) + ((d.center_W,) if len(x) == 3 else ())
    cutoff = Fraction(1)
    for value, center in zip(x, centers, strict=True):
        cutoff *= _cutoff(value, center, d)
    if cutoff == 0:
        return [_iv(0) for _ in x], _iv(0)
    values = [_Jet(_iv(v)) for v in (*x, h)]
    f, g, _ = _raw(cert.inputs, d, cert.selector_rank, values)
    return [cutoff * v.value for v in f], cutoff * g.value


@dataclass(frozen=True, slots=True)
class CandidateRG2bSection:
    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference | None = None
    certificate: RG2bCertificate = field(init=False)
    geometry: GRCV4Geometry = field(init=False)
    enclosure: tuple[str, str] = field(init=False)
    error_upper: str = field(init=False)
    levels: int = field(init=False)
    evaluations: int = field(init=False)

    def __post_init__(self) -> None:
        cert = RG2bCertificate(self.inputs, self.differential_reference)
        if _graph_mode(self.inputs):
            from .grc_v4_rg2b_graph import section

            for name, value in dict(certificate=cert, **section(cert)).items():
                object.__setattr__(self, name, value)
            return
        ref = self.inputs.geometry.reference
        d, params = cert.domain, ref.profile.params_resolved.realization
        x = _coordinates(self.inputs, self.inputs.current)
        centers = (d.center_C, d.center_C) + ((d.center_W,) if len(x) == 3 else ())
        _require(
            all(
                abs(v - Fraction(c)) <= Fraction(d.core)
                for v, c in zip(x, centers, strict=True)
            ),
            "RG2b section query is outside K",
        )
        b = {k: Fraction(cast(str, v)) for k, v in cert.bounds.items()}
        href = Fraction(ref.pairings.one_form.matrix[0][0])
        kh = Fraction(ref.profile.params_resolved.geometry.kappa_H)
        assert isinstance(params, RG2bParams)
        tolerance = Fraction(params.error_tolerance)
        budget = params.iteration_limit
        calls = 0
        inverse_to_geometry = abs(kh) * (
            b["source_X_lipschitz"] + b["source_h_lipschitz"] * b["section_lipschitz"]
        )
        neutral = kh == 0 or b["source_upper"] == 0
        # Allocate geometric error after converting inverse-coordinate error
        # with its certified sensitivity. Do not demand sub-ULP state iterates
        # when their full possible error is negligible in the Hodge norm.
        guard = (
            tolerance / (32 * inverse_to_geometry)
            if inverse_to_geometry
            else Fraction()
        )

        def evaluate(level: int, target: tuple[Fraction, ...]) -> _Interval:
            nonlocal calls
            if level == 0 or neutral:
                return _iv(href)
            mid = target
            for _ in range(64):
                calls += 1
                _require(
                    calls <= budget, "RG2b deterministic evaluation budget exhausted"
                )
                gamma = evaluate(level - 1, mid)
                f, g = _extended(cert, mid, gamma)
                residual = max(
                    (
                        (_iv(v) - t + dv).magnitude
                        for v, t, dv in zip(mid, target, f, strict=True)
                    ),
                    default=Fraction(),
                )
                inverse_error = residual * b["inverse_lipschitz"]
                if inverse_error <= guard:
                    error = (
                        abs(kh)
                        * (
                            b["source_X_lipschitz"]
                            + b["source_h_lipschitz"] * b["section_lipschitz"]
                        )
                        * inverse_error
                    )
                    value = _iv(href) + kh * g
                    return _Interval(value.lo - error, value.hi + error)
                # Binary64 iterates are numerical work, enclosed by the exact
                # residual test above; no rounded stagnation earns admission.
                mid = tuple(
                    Fraction(float(t - (dv.lo + dv.hi) / 2))
                    for t, dv in zip(target, f, strict=True)
                )
            raise RG2bStageError("RG2b inverse enclosure unresolved")

        radius = b["section_radius"]
        chosen = None
        for level in range(17):
            tail = radius * b["contraction_upper"] ** level
            if neutral:
                tail = Fraction()
            if tail > tolerance / 4:
                continue
            value = evaluate(level, x)
            value = _Interval(value.lo - tail, value.hi + tail)
            rounded = float((value.lo + value.hi) / 2)
            error = max(
                abs(Fraction(rounded) - value.lo), abs(Fraction(rounded) - value.hi)
            )
            if error <= tolerance:
                chosen = (level, value, rounded, error)
                break
            # More graph transforms do not remove arithmetic uncertainty.
            raise RG2bStageError("RG2b approximation/error tolerance is uncertified")
        _require(
            chosen is not None,
            "RG2b graph-transform depth budget cannot certify tolerance",
        )
        assert chosen is not None
        level, value, rounded, error = chosen
        _require(
            abs(Fraction(rounded) - href) <= radius,
            "stored RG2b section exceeds its Hodge ball",
        )
        geometry = GRCV4Geometry(ref, OneFormHodge(ref.graph, ((rounded,),)))
        for name, v in dict(
            certificate=cert,
            geometry=geometry,
            enclosure=(str(value.lo), str(value.hi)),
            error_upper=str(error),
            levels=level,
            evaluations=calls,
        ).items():
            object.__setattr__(self, name, v)

    def to_payload(self) -> dict[str, Any]:
        return dict(
            numerics=cast(
                RG2bParams,
                self.inputs.geometry.reference.profile.params_resolved.realization,
            ).approximation_policy_id,
            inputs=self.inputs.to_payload(),
            differential_reference=None
            if self.differential_reference is None
            else self.differential_reference.to_payload(),
        )

    @property
    def identity(self) -> str:
        return _identity("grcv4-rg2b-section-sha256", self.to_payload())

    @classmethod
    def from_payload(cls, value: Any) -> Any:
        data = _local_payload(value, {"numerics", "inputs", "differential_reference"})
        inputs = GeometryStageInputs.from_payload(data["inputs"])
        _require(
            data["numerics"]
            == cast(
                RG2bParams,
                inputs.geometry.reference.profile.params_resolved.realization,
            ).approximation_policy_id,
            "unknown RG2b approximation",
        )
        return cls(
            inputs,
            None
            if data["differential_reference"] is None
            else CandidateADifferentialReference.from_payload(
                data["differential_reference"]
            ),
        )

    def classical_jacobian(self) -> None:
        raise RG2bStageError("Lipschitz-only RG2b; no admitted C1 section successor")


@dataclass(frozen=True, slots=True)
class ProvisionalCandidateRG2bStep:
    """One section current, common continuity, A writer, final section check.

    The generated geometry is a post-current diagnostic, never a corrector or
    a persisted state. Section approximation, native arithmetic discrepancy,
    and the final invariance bound are distinct. Publication remains pending.
    """

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference | None = None
    section: CandidateRG2bSection = field(init=False)
    reset_section: CandidateRG2bSection = field(init=False)
    restart: CandidateRG2bSection = field(init=False)
    point: Any = field(init=False)
    reset_point: Any = field(init=False)
    restart_point: Any = field(init=False)
    resource: Any = field(init=False)
    writer: CandidateAWriter | None = field(init=False)
    generated: GRCV4Geometry | None = field(init=False)
    next_inputs: GeometryStageInputs = field(init=False)
    diagnostics: FrozenJSONMap = field(init=False)

    def __post_init__(self) -> None:
        from .grc_v4_candidate_a import CandidateAStageError
        from .grc_v4_candidate_c import CandidateCStageError
        from .grc_v4_ci import CIStageError
        from .grc_v4_geometry import GeometryDomainError, NonfiniteGeometryError
        from .grc_v4_step import (
            CurrentSelection,
            ProvisionalResourceStep,
            ResourceBoundaryError,
            _resource_charge,
        )

        before = self.inputs
        d = _declarations(before, self.differential_reference)
        ref = before.geometry.reference
        _resource_charge(before, VertexScalar(ref.graph, before.current.C), "admission")
        _resource_charge(before, VertexScalar(ref.graph, before.reset.C), "admission")
        if before.dt != 0 and before.step_index >= 2**53 - 1:
            raise ResourceBoundaryError(
                "admission",
                "domain_failure",
                "RG2b step index exceeds safe integer range",
            )
        try:
            next_time = float(Fraction(before.time) + Fraction(before.dt))
        except OverflowError as exc:
            raise ResourceBoundaryError(
                "admission", "nonfinite_value", "RG2b clock overflow"
            ) from exc
        if not math.isfinite(next_time):
            raise ResourceBoundaryError(
                "admission", "nonfinite_value", "RG2b clock overflow"
            )

        def native(section: CandidateRG2bSection) -> Any:
            selected = replace(
                section.inputs, geometry=section.geometry, stage="rg2b_section"
            )
            return (
                CandidateACurrent(
                    selected,
                    cast(CandidateADifferentialReference, self.differential_reference),
                )
                if isinstance(ref.profile.params_resolved.candidate, CandidateAParams)
                else CandidateCCurrent(selected)
            )

        stage: OperationStage = "pre_read_reconstruction"
        try:
            for state in (before.current, before.reset):
                coords = _coordinates(before, state)
                centers = _centers(before, d)
                _require(
                    all(
                        abs(v - Fraction(c)) <= Fraction(d.inner)
                        for v, c in zip(coords, centers, strict=True)
                    ),
                    "RG2b current/reset ordinary prestate is outside K_minus",
                )
            reset = CandidateRG2bSection(
                replace(before, current=before.reset), self.differential_reference
            )
            reset_point = native(reset)
            stage = "candidate_solve"
            section = CandidateRG2bSection(before, self.differential_reference)
            point = native(section)
            selected = point.inputs
            selection = (
                None
                if before.dt == 0
                else CurrentSelection(selected, "valid_root", point.current)
            )
            stage = "continuity"
            resource = ProvisionalResourceStep(before, selection)
            writer = generated = None
            diagnostics = dict(
                regularity="Lipschitz_only",
                section_error_upper=section.error_upper,
                continuity_evaluations=resource.continuity_evaluations,
                carrier_writes=0,
            )
            if before.dt == 0:
                following, restart = before, section
                restart_point = point
                diagnostics["invariance_check"] = "not_a_positive_duration_transition"
            else:
                generated = H_profile(
                    _source(point, point.current),
                    reference=ref,
                    context=before.context,
                    profile=ref.profile,
                )
                if isinstance(point, CandidateACurrent):
                    stage = "history_write"
                    writer = CandidateAWriter(point, resource)
                    final = writer.authority.state
                else:
                    final = resource.consume(
                        expected_prestate=before, expected_selection=selection
                    )
                stage = "final_reconstruction"
                following = replace(
                    before,
                    current=final,
                    time=next_time,
                    step_index=before.step_index + 1,
                )
                restart = CandidateRG2bSection(following, self.differential_reference)
                restart_point = native(restart)
                kh = Fraction(ref.profile.params_resolved.geometry.kappa_H)
                if _graph_mode(before):
                    from .grc_v4_rg2b_graph import native_bridge

                    (
                        native_current_error,
                        native_state_error,
                        native_geometry_error,
                        current_norm,
                    ) = native_bridge(section, point, following, generated)
                else:
                    x = _coordinates(before, before.current)
                    y = _coordinates(following, following.current)
                    h = section.geometry.one_form_hodge.matrix[0][0]
                    jets = [_Jet(_iv(v)) for v in (*x, h)]
                    f, g, j = _raw(before, d, section.certificate.selector_rank, jets)
                    native_current_error = (
                        _iv(point.current.values[0]) - j.value
                    ).magnitude
                    native_state_error = max(
                        (_iv(actual) - old - delta.value).magnitude
                        for actual, old, delta in zip(y, x, f, strict=True)
                    )
                    analytic_generated = (
                        _iv(ref.pairings.one_form.matrix[0][0]) + kh * g.value
                    )
                    native_geometry_error = (
                        _iv(generated.one_form_hodge.matrix[0][0]) - analytic_generated
                    ).magnitude
                    current_norm = j.value.magnitude
                tolerance = Fraction(
                    cast(
                        RG2bParams, ref.profile.params_resolved.realization
                    ).error_tolerance
                )
                b = {
                    k: Fraction(cast(str, v))
                    for k, v in section.certificate.bounds.items()
                }
                solver = ref.profile.params_resolved.solver
                current_tolerance = (
                    Fraction(solver.absolute_tolerance)
                    + Fraction(solver.relative_tolerance) * current_norm
                )
                _require(
                    native_current_error <= current_tolerance
                    and native_geometry_error <= tolerance
                    and b["section_lipschitz"] * native_state_error <= tolerance,
                    "RG2b native candidate/continuity/writer arithmetic bridge is uncertified",
                )
                e = Fraction(section.error_upper)
                bound = (
                    Fraction(restart.error_upper)
                    + native_geometry_error
                    + abs(kh) * b["source_h_lipschitz"] * e
                    + b["section_lipschitz"]
                    * (native_state_error + b["base_h_lipschitz"] * e)
                )
                from .grc_v4_ci import _norm

                residual = _norm(
                    Fraction(a) - Fraction(b)
                    for row, old in zip(
                        restart.geometry.one_form_hodge.matrix,
                        generated.one_form_hodge.matrix,
                        strict=True,
                    )
                    for a, b in zip(row, old, strict=True)
                )
                _require(
                    residual <= bound,
                    "RG2b poststate invariance failed its independent error bound",
                )
                if _graph_mode(before):
                    from .grc_v4_rg2b_graph import rounded_upper

                    bound = rounded_upper(bound)
                    native_current_error = rounded_upper(native_current_error)
                    native_state_error = rounded_upper(native_state_error)
                    native_geometry_error = rounded_upper(native_geometry_error)
                diagnostics.update(
                    invariance_residual=str(residual),
                    invariance_error_bound=str(bound),
                    native_current_error=str(native_current_error),
                    native_state_error=str(native_state_error),
                    native_geometry_error=str(native_geometry_error),
                )
        except (
            RG2bStageError,
            CIStageError,
            CandidateAStageError,
            CandidateCStageError,
            GeometryDomainError,
            NonfiniteGeometryError,
            OverflowError,
        ) as exc:
            if (
                isinstance(exc, (NonfiniteGeometryError, OverflowError))
                or getattr(exc, "disposition", None) == "nonfinite"
            ):
                raise ResourceBoundaryError(stage, "nonfinite_value", str(exc)) from exc
            if getattr(exc, "disposition", None) == "singular":
                raise ResourceBoundaryError(stage, "singular_solver", str(exc)) from exc
            if getattr(exc, "disposition", None) == "conditioning_failure":
                raise ResourceBoundaryError(
                    stage, "conditioning_failure", str(exc)
                ) from exc
            if getattr(exc, "disposition", None) == "no_admitted_root":
                raise ResourceBoundaryError(
                    stage, "no_admitted_root", str(exc)
                ) from exc
            raise ResourceBoundaryError(stage, "domain_failure", str(exc)) from exc
        for name, value in dict(
            section=section,
            reset_section=reset,
            restart=restart,
            point=point,
            reset_point=reset_point,
            restart_point=restart_point,
            resource=resource,
            writer=writer,
            generated=generated,
            next_inputs=following,
            diagnostics=FrozenJSONMap(diagnostics),
        ).items():
            object.__setattr__(self, name, value)

    def to_payload(self) -> dict[str, Any]:
        return dict(
            numerics=cast(
                RG2bParams,
                self.inputs.geometry.reference.profile.params_resolved.realization,
            ).approximation_policy_id,
            inputs=self.inputs.to_payload(),
            differential_reference=None
            if self.differential_reference is None
            else self.differential_reference.to_payload(),
        )

    @classmethod
    def from_payload(cls, value: Any) -> Any:
        data = _local_payload(value, {"numerics", "inputs", "differential_reference"})
        inputs = GeometryStageInputs.from_payload(data["inputs"])
        _require(
            data["numerics"]
            == cast(
                RG2bParams,
                inputs.geometry.reference.profile.params_resolved.realization,
            ).approximation_policy_id,
            "unknown RG2b step recipe",
        )
        return cls(
            inputs,
            None
            if data["differential_reference"] is None
            else CandidateADifferentialReference.from_payload(
                data["differential_reference"]
            ),
        )

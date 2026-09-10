"""Local A/C persistent-carrier recipes; no lifecycle or support authority.

PC owns Z, independently of C and A's W. A declared compact base chart and a
symmetric star-supported Frobenius ball are admitted by uniform analytic
bounds. Stored binary64 points are also checked, without projection. Current
reads old Z; one scalar-ZOH writer consumes that current's held source.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
import math
from typing import Any, TYPE_CHECKING, cast

from .grc_v4_candidate_a import (
    CandidateACurrent,
    CandidateADifferentialReference,
    CandidateAStageError,
    CandidateAWriter,
    HISTORY_POLICY,
)
from .grc_v4_candidate_c import (
    CandidateCCurrent,
    CandidateCStageError,
    _c_exact,
    _c_inverse,
    _c_mm,
    _c_transpose,
)

# Shared exact norm/exponential utilities. No CI root or CI domain is invoked.
from .grc_v4_ci import CIStageError, _exp_bounds, _norm, _opnorm, _sqrt_upper
from .grc_v4_geometry import (
    GRCV4Geometry,
    GeometryDomainError,
    GeometryStageInputs,
    H_profile,
    K4Tensor,
    NonfiniteGeometryError,
    StarAssembly,
    VertexScalar,
    _computed,
    _identity,
    _local_payload,
)
from .grc_v4_profile import CandidateAParams, CandidateCParams, PCParams
from .grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState, _number, _vector

if TYPE_CHECKING:
    from .grc_v4_step import OperationStage, ProvisionalResourceStep

NORM_ID = "symmetric_star_frobenius_v1"
CHART_PREFIX = "pc_compact_base_chart_v1:"
NUMERICS = "pc_exact_input_enclosed_scalar_zoh_binary64_v1"
Point = CandidateACurrent | CandidateCCurrent


class PCStageError(ValueError):
    def __init__(self, disposition: str, message: str) -> None:
        super().__init__(message)
        self.disposition = disposition


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PCStageError("domain_failure", message)


@dataclass(frozen=True, slots=True)
class PCBaseChart:
    """0<=C, ||C||2<=M; A additionally has w_min<=W_e<=w_max.

    C's canonical unused W bounds are both 1. The norm, reference-centred
    geometry image and analytic bound recipe are fixed by the versioned IDs.
    All varying domain bounds therefore participate in complete profile identity.
    """

    resource_radius: float
    weight_lower: float = 1.0
    weight_upper: float = 1.0

    def __post_init__(self) -> None:
        for name in ("resource_radius", "weight_lower", "weight_upper"):
            object.__setattr__(self, name, _number(getattr(self, name)))
        _require(
            self.resource_radius > 0 and 0 < self.weight_lower <= self.weight_upper,
            "PC requires a positive compact base chart",
        )

    @property
    def identity(self) -> str:
        return CHART_PREFIX + ":".join(
            x.hex()
            for x in (self.resource_radius, self.weight_lower, self.weight_upper)
        )

    @classmethod
    def from_identity(cls, name: str) -> PCBaseChart:
        _require(
            type(name) is str and name.startswith(CHART_PREFIX),
            "unsupported PC source-envelope/base-chart declaration",
        )
        try:
            parts = name[len(CHART_PREFIX) :].split(":")
            _require(len(parts) == 3, "invalid PC base-chart coordinates")
            result = cls(*(float.fromhex(x) for x in parts))
        except (ValueError, OverflowError) as exc:
            raise PCStageError("domain_failure", "invalid PC base chart") from exc
        _require(result.identity == name, "noncanonical PC base-chart identity")
        return result


def _declarations(inputs: GeometryStageInputs) -> tuple[PCParams, PCBaseChart]:
    if type(inputs) is not GeometryStageInputs:
        raise TypeError("PC requires typed captured inputs")
    profile = inputs.geometry.reference.profile
    identity, params = profile.identity_payload, profile.params_resolved
    pc = params.realization
    _require(
        identity.profile_family_id in {"A_PC", "C_PC"}
        and type(pc) is PCParams
        and pc.carrier_norm_id == NORM_ID
        and pc.writer_id == "zero_order_hold_exponential_v1"
        and identity.solver_id == "direct_unique_root_v1"
        and params.solver.solver_kind == "direct"
        and params.solver.residual_norm_id == "edge_l2_v1",
        "unimplemented or inconsistent PC declaration",
    )
    assert isinstance(pc, PCParams)
    chart = PCBaseChart.from_identity(pc.source_envelope_id)
    if identity.candidate == "C":
        _require(
            chart.weight_lower == chart.weight_upper == 1,
            "C_PC has no independent mobility chart",
        )
    return pc, chart


def _ball(values: Any, radius: float, label: str) -> None:
    _require(
        sum((Fraction(x) ** 2 for x in values), Fraction()) <= Fraction(radius) ** 2,
        label + " exceeds the declared PC Frobenius ball",
    )


def _base_state(
    state: GRCV4AuthoritativeState, chart: PCBaseChart, pc: PCParams
) -> None:
    _ball(state.C, chart.resource_radius, "resource")
    if state.W_A is not None:
        _require(
            all(chart.weight_lower <= w <= chart.weight_upper for w in state.W_A),
            "A history lies outside the declared compact PC base chart",
        )
    assert state.Z_4 is not None
    _ball(state.Z_4, pc.radius, "carrier")


def carrier_geometry(
    inputs: GeometryStageInputs, state: GRCV4AuthoritativeState
) -> GRCV4Geometry:
    """Reconstruct from the supplied state, including an independent reset Z."""
    ref = inputs.geometry.reference
    n = len(ref.graph.live_edge_ids)
    _require(
        state.Z_4 is not None and len(state.Z_4) == n * n,
        "PC carrier coordinates must cover the exact live structural space",
    )
    assert state.Z_4 is not None
    return H_profile(
        K4Tensor(
            ref.graph,
            ref.K4_base,
            tuple(state.Z_4[i * n : (i + 1) * n] for i in range(n)),
        ),
        reference=ref,
        context=ref.context,
        profile=ref.profile,
    )


def _descriptor_bound(
    backend: CandidateADifferentialReference, radius: Fraction
) -> Fraction:
    """Uniform WLS gradient bound over ||C||<=M, using exact normal matrices.

    At each node ||b_i|| <= sqrt(2) M sum_j w_ij ||delta_ij||;
    ||gradient_i|| <= ||normal_i^-1|| ||b_i||. No sampled base state.
    """
    graph, d = backend.graph, backend.dimension
    bound = Fraction()
    for i, node in enumerate(graph.live_node_ids):
        a = [
            [Fraction(backend.regularization) * int(k == j) for j in range(d)]
            for k in range(d)
        ]
        rhs = Fraction()
        for edge in graph.oriented_edges:
            if node not in (edge.tail_node_id, edge.head_node_id):
                continue
            other = (
                edge.head_node_id if node == edge.tail_node_id else edge.tail_node_id
            )
            j = graph.node_index(other)
            delta = tuple(
                Fraction(y) - Fraction(x)
                for x, y in zip(backend.positions[i], backend.positions[j], strict=True)
            )
            w = Fraction(cast(float, backend.reference_weights[edge.edge_id]))
            rhs += w * _norm(delta)
            for k in range(d):
                for column in range(d):
                    a[k][column] += w * delta[k] * delta[column]
        bound = max(
            bound,
            _opnorm(_c_inverse(tuple(map(tuple, a))))
            * rhs
            * _sqrt_upper(Fraction(2))
            * radius,
        )
    return bound


@dataclass(frozen=True, slots=True)
class PCEnvelopeCertificate:
    """Sufficient whole-chart bounds, not a bound at the submitted C/W point.

    ||Z||F<=R gives ||h-h_ref||op<=|kappa_H|R. For A, |q_e|<=1
    gives a uniform current margin. C bounds Q^-1 R Q in physical coordinates
    and admits one strict-gap selector stratum. Star assembly is nonexpansive
    in Frobenius norm on vv^T, hence ||S||F<=|zeta| ||flat(read)||2^2.
    No matched-forcing contraction or endpoint hysteresis is claimed.
    """

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference | None = None
    bounds: FrozenJSONMap = field(init=False)

    def __post_init__(self) -> None:
        pc, chart = _declarations(self.inputs)
        ref = self.inputs.geometry.reference
        _require(
            bool(ref.graph.live_edge_ids), "PC requires a nonempty structural space"
        )
        _base_state(self.inputs.current, chart, pc)
        p = ref.profile.params_resolved.candidate
        weights = tuple(
            Fraction(cast(float, ref.edge_weights[e])) for e in ref.graph.live_edge_ids
        )
        radius = abs(Fraction(ref.profile.params_resolved.geometry.kappa_H)) * Fraction(
            pc.radius
        )
        lower, upper = min(weights) - radius, max(weights) + radius
        limit = Fraction(ref.profile.params_resolved.solver.conditioning_limit)
        _require(
            lower > 0 and upper / lower <= limit,
            "PC whole-ball geometry image is not SPD/conditioning certified",
        )
        b = _c_exact(ref.graph.incidence)
        bt = _c_transpose(b)
        b2 = _opnorm(_c_mm(bt, b))
        dc = _opnorm(bt) * Fraction(chart.resource_radius)
        extra: dict[str, Any] = {}
        if isinstance(p, CandidateAParams):
            backend = self.differential_reference
            if type(backend) is not CandidateADifferentialReference:
                raise TypeError("A_PC requires its declared differential reference")
            _require(
                backend.graph == ref.graph
                and backend.identity == p.descriptor_backend_id
                and backend.reference_weights == ref.edge_weights,
                "A PC differential reference/profile mismatch",
            )
            w = Fraction(chart.weight_upper)
            baseline = (
                Fraction(p.eta)
                * w
                * b2
                * (abs(Fraction(p.kappa_c)) * w + abs(Fraction(p.kappa_Ah)) * radius)
                * dc
            )
            beta = abs(Fraction(p.zeta_A) * Fraction(p.chi_A))
            margin, response = 1 - beta, Fraction(1)
            _require(margin > 0, "A PC whole-chart current inverse is uncertified")
            current = baseline / margin
            descriptor = _descriptor_bound(backend, Fraction(chart.resource_radius))
            # ||e_u + e_v|| is sqrt(2) for distinct endpoints, but 2 for
            # a loop: its resource term counts the same endpoint twice.
            endpoint_norm = (
                Fraction(2)
                if any(
                    e.tail_node_id == e.head_node_id for e in ref.graph.oriented_edges
                )
                else _sqrt_upper(Fraction(2))
            )
            exponent = (
                abs(Fraction(p.alpha)) * endpoint_norm * Fraction(chart.resource_radius)
                + abs(Fraction(p.beta)) * (2 * descriptor) ** 2
                + abs(Fraction(p.gamma)) * current**2
            ) / 2
            _require(
                exponent <= 700,
                "A PC conductance is not finite-certified over the base chart",
            )
            gain, chi = abs(Fraction(p.zeta_A)), abs(Fraction(p.chi_A))
            extra.update(
                conductance_exponent_absolute_upper=exponent,
                descriptor_norm_upper=descriptor,
            )
        else:
            assert isinstance(p, CandidateCParams)
            if self.differential_reference is not None:
                raise TypeError("C_PC has no A differential reference")
            stiffness = _c_mm(_c_mm(b, _c_exact(ref.pairings.one_form.matrix)), bt)
            shifted = tuple(
                tuple(
                    x - (Fraction(p.Lambda_C) if i == j else 0)
                    for j, x in enumerate(row)
                )
                for i, row in enumerate(stiffness)
            )
            try:
                shifted_inverse = _c_inverse(shifted)
            except CandidateCStageError as exc:
                if exc.disposition != "singular":
                    raise
                # This inverse certifies the selector chart. No physical
                # current block has been constructed or solved here.
                raise PCStageError(
                    "domain_failure",
                    "C PC selector cutoff lies on the reference spectrum",
                ) from exc
            gap = 1 / _opnorm(shifted_inverse) - b2 * radius
            _require(gap > 0, "C PC ball reaches an uncertified selector boundary")
            d = _exp_bounds(abs(Fraction(p.kappa_M_C)) / 2)[1]
            retained_lower, retained_upper = lower / (d * d), upper * d * d
            _require(
                retained_upper / retained_lower <= limit,
                "C PC retained Hodge conditioning is uncertified",
            )
            response = (
                Fraction(1)
                if p.tau_C == 0
                else upper**2
                / retained_lower
                * _sqrt_upper(retained_upper / retained_lower)
                * retained_upper
                / lower**2
            )
            beta = abs(Fraction(p.zeta_C) * Fraction(p.chi_C)) * response
            margin = 1 - beta
            _require(
                margin > 0,
                "C PC physical current inverse is uncertified over the chart",
            )
            mobility = max(
                Fraction(p.eta_C) * Fraction(cast(float, p.W_C_tr[e]))
                for e in ref.graph.live_edge_ids
            )
            baseline = (
                mobility * abs(Fraction(p.kappa_Phi_C)) * b2 * dc * retained_upper
            )
            current = baseline / margin
            gain, chi = abs(Fraction(p.zeta_C)), abs(Fraction(p.chi_C))
            extra.update(
                selector_gap_lower=gap,
                admitted_strata=1,
                physical_response_upper=response,
            )
        conditioning = (1 + beta) / margin
        _require(
            conditioning <= limit, "PC whole-chart current conditioning is uncertified"
        )
        flat = chi * response * current / lower
        source = gain * flat**2
        _require(
            source <= Fraction(pc.radius),
            "PC uniform source envelope exceeds the carrier radius",
        )
        extra.update(
            geometry_radius=radius,
            hodge_lower=lower,
            hodge_upper=upper,
            current_norm_upper=current,
            current_inverse_upper=1 / margin,
            current_conditioning_upper=conditioning,
            flat_norm_upper=flat,
            source_norm_upper=source,
            carrier_radius=Fraction(pc.radius),
        )
        object.__setattr__(
            self, "bounds", FrozenJSONMap({k: str(v) for k, v in extra.items()})
        )


def scalar_zoh(
    old: tuple[float, ...], source: tuple[float, ...], dt: float, tau: float
) -> tuple[float, ...]:
    """Enclose the real held-source law, then require a unique binary64 result.

    Exact dt/tau is never first rounded to binary64. Decimal exp is correctly
    rounded; adjacent Decimal values enclose it and its rounded argument.
    Rational affine evaluation avoids cancellation/overflow in signed values.
    At ratio>=1600 even max binary64 endpoint separation decays below half the
    smallest subnormal. Otherwise ambiguous rounding fails closed after a
    bounded precision refinement. Numerical underflow is not native release.
    """
    old, source = _vector(old), _vector(source)
    dt, tau = _number(dt), _number(tau)
    _require(
        len(old) == len(source) and dt >= 0 and tau > 0,
        "ZOH requires matching finite fields, dt>=0 and tau>0",
    )
    if dt == 0 or old == source:
        return old
    ratio = Fraction(dt) / Fraction(tau)
    if ratio >= 1600:
        return source
    for precision in (800, 1600):
        with localcontext(
            Context(
                prec=precision,
                rounding=ROUND_HALF_EVEN,
                Emin=-999999,
                Emax=999999,
                flags=[],
                traps=[],
            )
        ) as ctx:
            r = Decimal(ratio.numerator) / Decimal(ratio.denominator)
            lo = Fraction((-r.next_plus(ctx)).exp().next_minus(ctx))
            hi = Fraction((-r.next_minus(ctx)).exp().next_plus(ctx))
        result = []
        for z, s in zip(old, source, strict=True):
            ends = [Fraction(s) + a * (Fraction(z) - Fraction(s)) for a in (lo, hi)]
            rounded = [float(x) for x in ends]
            if rounded[0] != rounded[1]:
                break
            result.append(_computed(rounded[0]))
        else:
            return tuple(result)
    raise PCStageError("no_admitted_root", "PC writer rounding is unresolved")


@dataclass(frozen=True, slots=True)
class CandidatePCRead:
    """Old-Z geometry and the complete fixed-h candidate chain, with held S."""

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference | None = None
    certificate: PCEnvelopeCertificate = field(init=False)
    point: Point = field(init=False)
    structural_source: K4Tensor = field(init=False)

    def __post_init__(self) -> None:
        pc, _ = _declarations(self.inputs)
        _require(
            self.inputs.stage == "pre_read"
            and self.inputs.evaluation_index == 0
            and self.inputs.trial_current is None,
            "PC read requires fresh pre-read inputs",
        )
        old_geometry = carrier_geometry(self.inputs, self.inputs.current)
        _require(
            self.inputs.geometry == old_geometry,
            "PC pre-read geometry must derive from old committed Z",
        )
        certificate = PCEnvelopeCertificate(self.inputs, self.differential_reference)
        selected = replace(self.inputs, stage="pc_old_history")
        backend = self.differential_reference
        if self.inputs.geometry.reference.profile.identity_payload.candidate == "A":
            assert backend is not None
            a_point = CandidateACurrent(selected, backend)
            point: Point = a_point
            source = a_point.structural_source()
        else:
            point = CandidateCCurrent(selected)
            ref = selected.geometry.reference
            p = ref.profile.params_resolved.candidate
            assert isinstance(p, CandidateCParams)
            n = len(ref.graph.live_edge_ids)
            matrix = (
                tuple((0.0,) * n for _ in range(n))
                if p.zeta_C == 0
                else tuple(
                    tuple(
                        _computed(float(Fraction(p.zeta_C) * Fraction(x))) for x in row
                    )
                    for row in StarAssembly(point.read.causal_flat).matrix
                )
            )
            source = K4Tensor(ref.graph, ref.K4_base, matrix)
        _ball((x for row in source.increment for x in row), pc.radius, "stored source")
        for name, value in (
            ("certificate", certificate),
            ("point", point),
            ("structural_source", source),
        ):
            object.__setattr__(self, name, value)


@dataclass(frozen=True, slots=True)
class ProvisionalCandidatePCStep:
    """One continuity, A-only W writer, one Z writer, separate final readmission.

    Current/reset C,W,Z are independently admitted. Final C/W/Z must remain in
    the declared chart; no invariant base dynamics is presumed. Final surfaces
    are postconditions, never fed back into the same beat. These detached
    immutable recipes grant no live commit, reset/migration, or receipt authority.
    """

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference | None = None
    read: CandidatePCRead = field(init=False)
    reset_read: CandidatePCRead = field(init=False)
    resource: ProvisionalResourceStep = field(init=False)
    writer: CandidateAWriter | None = field(init=False)
    carrier_writes: int = field(init=False)
    restart: CandidatePCRead = field(init=False)
    next_inputs: GeometryStageInputs = field(init=False)

    def __post_init__(self) -> None:
        from .grc_v4_step import (
            CurrentSelection,
            ProvisionalResourceStep,
            ResourceBoundaryError,
            _resource_charge,
        )

        before = self.inputs
        pc, _ = _declarations(before)
        ref = before.geometry.reference
        _require(
            before.stage == "pre_read" and before.trial_current is None,
            "PC step requires fresh pre-read inputs",
        )
        if (
            ref.profile.identity_payload.candidate == "A"
            and ref.profile.params_resolved.lifecycle.history_policy_id
            != HISTORY_POLICY
        ):
            raise ValueError("unimplemented A retained-history writer policy")
        _resource_charge(before, VertexScalar(ref.graph, before.current.C), "admission")
        _resource_charge(before, VertexScalar(ref.graph, before.reset.C), "admission")
        if before.dt != 0 and before.step_index >= 2**53 - 1:
            raise ResourceBoundaryError(
                "admission",
                "domain_failure",
                "PC step index exceeds the safe integer domain",
            )
        try:
            next_time = float(Fraction(before.time) + Fraction(before.dt))
        except OverflowError as exc:
            raise ResourceBoundaryError(
                "admission", "nonfinite_value", "PC clock overflow"
            ) from exc
        if not math.isfinite(next_time):
            raise ResourceBoundaryError(
                "admission", "nonfinite_value", "PC clock overflow"
            )
        stage: OperationStage = "pre_read_reconstruction"
        try:
            reset_read = CandidatePCRead(
                replace(
                    before,
                    current=before.reset,
                    geometry=carrier_geometry(before, before.reset),
                ),
                self.differential_reference,
            )
            stage = "candidate_solve"
            read = CandidatePCRead(before, self.differential_reference)
            selection = (
                None
                if before.dt == 0
                else CurrentSelection(
                    read.point.inputs, "valid_root", read.point.current
                )
            )
            stage = "continuity"
            resource = ProvisionalResourceStep(before, selection)
            writer = None
            if before.dt == 0:
                following, restart = before, read
            else:
                stage = "history_write"
                if isinstance(read.point, CandidateACurrent):
                    writer = CandidateAWriter(read.point, resource)
                    final = writer.authority.state
                else:
                    final = resource.consume(
                        expected_prestate=before, expected_selection=selection
                    )
                assert before.current.Z_4 is not None
                source = tuple(
                    x for row in read.structural_source.increment for x in row
                )
                z = scalar_zoh(before.current.Z_4, source, before.dt, pc.tau_PC)
                _ball(z, pc.radius, "written carrier")
                final = GRCV4AuthoritativeState(final.C, final.W_A, z)
                stage = "final_reconstruction"
                following = replace(
                    before,
                    current=final,
                    geometry=carrier_geometry(before, final),
                    time=next_time,
                    step_index=before.step_index + 1,
                )
                restart = CandidatePCRead(
                    replace(following, dt=0), self.differential_reference
                )
        except (
            PCStageError,
            CIStageError,
            CandidateAStageError,
            CandidateCStageError,
            GeometryDomainError,
            NonfiniteGeometryError,
            OverflowError,
        ) as exc:
            disposition = getattr(exc, "disposition", "domain_failure")
            code = {
                "nonfinite": "nonfinite_value",
                "singular": "singular_solver",
                "conditioning_failure": "conditioning_failure",
                "no_admitted_root": "no_admitted_root",
            }.get(disposition, "domain_failure")
            if isinstance(exc, (OverflowError, NonfiniteGeometryError)):
                code = "nonfinite_value"
            raise ResourceBoundaryError(stage, cast(Any, code), str(exc)) from exc
        for name, value in (
            ("read", read),
            ("reset_read", reset_read),
            ("resource", resource),
            ("writer", writer),
            ("carrier_writes", int(before.dt > 0)),
            ("restart", restart),
            ("next_inputs", following),
        ):
            object.__setattr__(self, name, value)

    def to_payload(self) -> dict[str, Any]:
        return dict(
            schema_version="grcv4-pc-step-recipe-v1",
            numerics=NUMERICS,
            inputs=self.inputs.to_payload(),
            differential_reference=None
            if self.differential_reference is None
            else self.differential_reference.to_payload(),
        )

    @property
    def identity(self) -> str:
        return _identity("grcv4-pc-step-sha256", self.to_payload())

    @classmethod
    def from_payload(cls, value: object) -> ProvisionalCandidatePCStep:
        data = _local_payload(
            value,
            {"schema_version", "numerics", "inputs", "differential_reference"},
            "schema_version",
            "grcv4-pc-step-recipe-v1",
        )
        _require(data["numerics"] == NUMERICS, "unsupported PC step numerical recipe")
        backend = data["differential_reference"]
        return cls(
            GeometryStageInputs.from_payload(data["inputs"]),
            None
            if backend is None
            else CandidateADifferentialReference.from_payload(backend),
        )

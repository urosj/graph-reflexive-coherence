"""Bounded Candidate A and C OS realizations, without lifecycle/profile support.

All objects are provisional. Only the later complete-step/lifecycle owner can
commit authority; reconstructed geometry and residual work are never history.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from fractions import Fraction

from .grc_v4_candidate_a import (
    HISTORY_POLICY,
    CandidateACurrent,
    CandidateADifferentialReference,
    CandidateAStageError,
)
from .grc_v4_candidate_c import (
    CandidateCCurrent,
    CandidateCStageError,
    _c_exact,
    _c_float,
    _c_inertia,
    _c_inverse,
    _c_mm,
    _c_transpose,
)
from .grc_v4_geometry import (
    GRCV4Geometry,
    GeometryStageInputs,
    GeometryDomainError,
    NonfiniteGeometryError,
    H_profile,
    K4Tensor,
    Matrix,
    StarAssembly,
    _local_payload,
)
from .grc_v4_profile import OSParams


class OSStageError(ValueError):
    """A noncommitting local failure; not a lifecycle failure receipt."""

    def __init__(self, substage: str, message: str) -> None:
        super().__init__(substage + ": " + message)
        self.substage = substage


def _os_inputs(inputs: GeometryStageInputs) -> GeometryStageInputs:
    if type(inputs) is not GeometryStageInputs:
        raise TypeError("OS requires captured stage inputs")
    before = GeometryStageInputs.from_payload(inputs.to_payload())
    ref = before.geometry.reference
    params = ref.profile.params_resolved.realization
    if (
        ref.profile.identity_payload.profile_family_id != "C_OS"
        or type(params) is not OSParams
        or params.predictor_policy_id != "reference_geometry_predictor_v1"
        or params.corrector_policy_id != "one_fresh_geometry_corrector_v1"
        or params.split_residual_norm_id != "edge_l2_v1"
    ):
        raise ValueError("unimplemented Candidate C OS declaration")
    if (
        before.stage != "pre_read"
        or before.geometry != ref.geometry()
        or before.trial_current is not None
    ):
        raise ValueError("OS requires fresh reference pre-read inputs")
    return before


def _c_source(point: CandidateCCurrent) -> K4Tensor:
    """C's exact star adapter in the declared common structural coordinates.

    chi is already in causal_flat. zeta is applied once, outside the adapter.
    StarAssembly owns its rounded entries; multiplying those entries by the
    external gain is exact before one final binary64 rounding.
    """
    ref = point.inputs.geometry.reference
    zeta = point.algebra.transport.params.zeta_C
    size = len(ref.graph.oriented_edges)
    increment = (
        tuple((0.0,) * size for _ in range(size))
        if zeta == 0
        else _c_float(
            tuple(
                tuple(Fraction(zeta) * Fraction(x) for x in row)
                for row in StarAssembly(point.read.causal_flat).matrix
            )
        )
    )
    return K4Tensor(ref.graph, ref.K4_base, increment)


def _source_geometry(point: CandidateCCurrent) -> GRCV4Geometry:
    ref = point.inputs.geometry.reference
    return H_profile(
        _c_source(point),
        reference=ref,
        context=point.inputs.context,
        profile=ref.profile,
    )


def _selector_path_segments(
    predictor: CandidateCCurrent, corrector: CandidateCCurrent
) -> int:
    """Certify the entire affine geometry segment's fixed strict-gap rank.

    Same endpoint ranks alone do not exclude an interior crossing. Exact
    symmetric order settles monotone paths. Otherwise Neumann inverse bounds
    certify dyadic subsegments. At most 256 bisections are allowed; unresolved
    certification rejects, without another OS solve or geometry iteration.
    This certificate concerns selector rank, not all intermediate current maps.
    """
    rank = predictor.algebra.selector.rank
    if corrector.algebra.selector.rank != rank:
        raise CandidateCStageError(
            "domain_failure", "OS geometry update changes selector stratum"
        )
    graph = predictor.current.graph
    b = _c_exact(graph.incidence)
    matrices = []
    cutoff = Fraction(predictor.algebra.transport.params.Lambda_C)
    for point in (predictor, corrector):
        h = _c_exact(point.inputs.geometry.one_form_hodge.matrix)
        stiffness = _c_mm(_c_mm(b, h), _c_transpose(b))
        matrices.append(
            tuple(
                tuple(x - (cutoff if i == j else 0) for j, x in enumerate(row))
                for i, row in enumerate(stiffness)
            )
        )
    a, end = matrices
    delta = tuple(
        tuple(y - x for x, y in zip(row, other, strict=True))
        for row, other in zip(a, end, strict=True)
    )
    neg, _, pos = _c_inertia(delta)
    if not neg or not pos:
        return 1
    norm = max(sum(abs(x) for x in row) for row in delta)
    pending = [(Fraction(), Fraction(1))]
    certified = splits = 0
    while pending:
        lo, hi = pending.pop()
        mid = (lo + hi) / 2
        center = tuple(
            tuple(x + mid * d for x, d in zip(row, change, strict=True))
            for row, change in zip(a, delta, strict=True)
        )
        negative, zero, _ = _c_inertia(center)
        if zero or negative != rank:
            raise CandidateCStageError(
                "domain_failure", "OS geometry path crosses selector cutoff"
            )
        inverse_norm = max(sum(abs(x) for x in row) for row in _c_inverse(center))
        if inverse_norm * norm * (hi - lo) / 2 < 1:
            certified += 1
        else:
            splits += 1
            if splits > 256:
                raise CandidateCStageError(
                    "domain_failure", "OS selector path certificate unresolved"
                )
            pending.extend(((lo, mid), (mid, hi)))
    return certified


@dataclass(frozen=True, slots=True)
class OSSplitResidual:
    """Explicit geometry defect with an exact reference-relative norm check.

    edge_l2_v1 acts on reference-whitened edge coordinates here:
    ||Href^(-1/2) R Href^(-1/2)||_2 <= tolerance. For symmetric R this is
    equivalent to both tolerance*Href +/- R being positive semidefinite.
    Exact dyadic differences and inertia decide admission, including equality
    and subnormal limits. Rounded residual entries are presentation only:
    values is None if any exact entry cannot round to finite binary64.
    exact_values always retains the complete defect, including in that case.
    """

    geometry: GRCV4Geometry
    regenerated: GRCV4Geometry
    values: Matrix | None = field(init=False)
    exact_values: tuple[tuple[str, ...], ...] = field(init=False)
    admitted: bool = field(init=False)

    def __post_init__(self) -> None:
        if (
            type(self.geometry) is not GRCV4Geometry
            or type(self.regenerated) is not GRCV4Geometry
        ):
            raise TypeError("split residual requires typed geometry operands")
        ref = self.geometry.reference
        if self.regenerated.reference != ref:
            raise ValueError("split residual has foreign reference geometry")
        policy = ref.profile.params_resolved.realization
        if (
            type(policy) is not OSParams
            or policy.split_residual_norm_id != "edge_l2_v1"
        ):
            raise ValueError("unimplemented OS split norm")
        residual = tuple(
            tuple(Fraction(x) - Fraction(y) for x, y in zip(row, other, strict=True))
            for row, other in zip(
                self.geometry.one_form_hodge.matrix,
                self.regenerated.one_form_hodge.matrix,
                strict=True,
            )
        )
        t = Fraction(policy.tolerance)
        reference = ref.pairings.one_form.matrix
        admitted = all(
            _c_inertia(
                tuple(
                    tuple(
                        t * Fraction(h) + sign * r
                        for h, r in zip(row, other, strict=True)
                    )
                    for row, other in zip(reference, residual, strict=True)
                )
            )[0]
            == 0
            for sign in (-1, 1)
        )
        # Fraction conversion raises OverflowError outside binary64 range.
        # A missing display matrix must never veto the exact norm decision.
        try:
            values: Matrix | None = tuple(
                tuple(float(x) for x in row) for row in residual
            )
        except OverflowError:
            values = None
        object.__setattr__(self, "values", values)
        object.__setattr__(
            self, "exact_values", tuple(tuple(str(x) for x in row) for row in residual)
        )
        object.__setattr__(self, "admitted", admitted)


@dataclass(frozen=True, slots=True)
class CandidateCOSPass:
    """Exactly one positive-duration predictor/geometry/corrector pass.

    The residual evaluation generates a comparison geometry, which never
    feeds another current solve. Inputs/outputs are immutable provisional values.
    Resource/charge admission and final-C refresh belong to the step boundary.
    """

    inputs: GeometryStageInputs
    predictor: CandidateCCurrent = field(init=False)
    corrector: CandidateCCurrent = field(init=False)
    residual: OSSplitResidual = field(init=False)
    selector_path_segments: int = field(init=False)

    def __post_init__(self) -> None:
        before = _os_inputs(self.inputs)
        if before.dt <= 0:
            raise ValueError("OS pass requires positive duration")
        stage = "os_predictor"
        try:
            predictor = CandidateCCurrent(replace(before, stage="os_predictor"))
            stage = "geometry_update"
            geometry = _source_geometry(predictor)
            stage = "os_corrector"
            corrector = CandidateCCurrent(
                replace(before, geometry=geometry, stage="os_corrector")
            )
            segments = _selector_path_segments(predictor, corrector)
            stage = "split_residual"
            residual = OSSplitResidual(geometry, _source_geometry(corrector))
            if not residual.admitted:
                raise CandidateCStageError(
                    "domain_failure",
                    "declared OS split tolerance exceeded; no second iteration",
                )
        except (
            CandidateCStageError,
            GeometryDomainError,
            NonfiniteGeometryError,
        ) as exc:
            raise OSStageError(stage, str(exc)) from exc
        for name, value in (
            ("inputs", before),
            ("predictor", predictor),
            ("corrector", corrector),
            ("residual", residual),
            ("selector_path_segments", segments),
        ):
            object.__setattr__(self, name, value)


def _a_os_inputs(inputs: GeometryStageInputs) -> GeometryStageInputs:
    """Admit the A declaration independently of the C selector contract."""
    if type(inputs) is not GeometryStageInputs:
        raise TypeError("A OS requires captured stage inputs")
    before = GeometryStageInputs.from_payload(inputs.to_payload())
    ref = before.geometry.reference
    params = ref.profile.params_resolved.realization
    if (
        ref.profile.identity_payload.profile_family_id != "A_OS"
        or ref.profile.params_resolved.lifecycle.history_policy_id != HISTORY_POLICY
        or type(params) is not OSParams
        or params.predictor_policy_id != "reference_geometry_predictor_v1"
        or params.corrector_policy_id != "one_fresh_geometry_corrector_v1"
        or params.split_residual_norm_id != "edge_l2_v1"
    ):
        raise ValueError("unimplemented Candidate A OS declaration")
    if (
        before.stage != "pre_read"
        or before.geometry != ref.geometry()
        or before.trial_current is not None
    ):
        raise ValueError("A OS requires fresh reference pre-read inputs")
    return before


def _a_source_geometry(point: CandidateACurrent) -> GRCV4Geometry:
    ref = point.inputs.geometry.reference
    return H_profile(
        point.structural_source(),
        reference=ref,
        context=point.inputs.context,
        profile=ref.profile,
    )


@dataclass(frozen=True, slots=True)
class CandidateAOSPass:
    """One A predictor and fresh corrector, followed by a read-only defect.

    Incoming W_A supplies both current stages. Regeneration for the split
    residual supplies no second corrector and does not become retained state.
    The common reference-whitened split norm is independent of C's selector.
    """

    inputs: GeometryStageInputs
    differential_reference: CandidateADifferentialReference
    predictor: CandidateACurrent = field(init=False)
    corrector: CandidateACurrent = field(init=False)
    residual: OSSplitResidual = field(init=False)

    def __post_init__(self) -> None:
        before = _a_os_inputs(self.inputs)
        if before.dt <= 0:
            raise ValueError("A OS pass requires positive duration")
        stage = "os_predictor"
        try:
            predictor = CandidateACurrent(
                replace(before, stage="os_predictor"), self.differential_reference
            )
            stage = "geometry_update"
            geometry = _a_source_geometry(predictor)
            stage = "os_corrector"
            corrector = CandidateACurrent(
                replace(before, geometry=geometry, stage="os_corrector"),
                self.differential_reference,
            )
            stage = "split_residual"
            residual = OSSplitResidual(geometry, _a_source_geometry(corrector))
            if not residual.admitted:
                raise CandidateAStageError(
                    "domain_failure",
                    "declared OS split tolerance exceeded; no second iteration",
                )
        except (
            CandidateAStageError,
            CandidateCStageError,  # shared exact numerical utilities
            GeometryDomainError,
            NonfiniteGeometryError,
        ) as exc:
            raise OSStageError(stage, str(exc)) from exc
        for name, value in (
            ("inputs", before),
            ("predictor", predictor),
            ("corrector", corrector),
            ("residual", residual),
        ):
            object.__setattr__(self, name, value)

    def to_payload(self) -> dict[str, object]:
        return {
            "schema_version": "grcv4-a-os-pass-v1",
            "inputs": self.inputs.to_payload(),
            "differential_reference": self.differential_reference.to_payload(),
        }

    @classmethod
    def from_payload(cls, value: object) -> CandidateAOSPass:
        data = _local_payload(
            value,
            {"schema_version", "inputs", "differential_reference"},
            "schema_version",
            "grcv4-a-os-pass-v1",
        )
        return cls(
            GeometryStageInputs.from_payload(data["inputs"]),
            CandidateADifferentialReference.from_payload(
                data["differential_reference"]
            ),
        )

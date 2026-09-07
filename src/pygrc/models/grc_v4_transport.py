"""Candidate-owned mobility factors; no current solve or resource writer.

A mobility reads supplied retained W_A. C mobility reads only resolved W_C_tr
and eta_C; it has no selector or geometry input. E_H and E_M are sibling
constructors with distinct types and authorities, including at eta_C=1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar

from .grc_v4_geometry import (
    GRCV4Graph,
    Matrix,
    OneForm,
    OneFormHodge,
    PhysicalFlux,
    _computed,
    _diagonal,
    _identity,
    _require_coordinates,
)
from .grc_v4_profile import CandidateAParams, CandidateCParams
from .grc_v4_state import _number, _vector


def _positive_products(eta: float, weights: tuple[float, ...]) -> tuple[float, ...]:
    gain = _number(eta)
    if gain <= 0:
        raise ValueError("mobility gain must be strictly positive")
    # Reject underflow to zero as well as overflow. No floor or fallback.
    return _vector(tuple(_computed(gain * w) for w in weights), positive=True)


def _c_reference(graph: GRCV4Graph, params: CandidateCParams) -> tuple[float, ...]:
    if type(graph) is not GRCV4Graph or type(params) is not CandidateCParams:
        raise TypeError("C reference requires graph and resolved C parameters")
    if set(params.W_C_tr) != set(graph.live_edge_ids):
        raise ValueError("C transport reference must cover exactly the live edge IDs")
    return _vector(tuple(params.W_C_tr[e] for e in graph.live_edge_ids), positive=True)


@dataclass(frozen=True, slots=True)
class _Mobility:
    graph: GRCV4Graph
    diagonal: tuple[float, ...] = field(init=False)
    SOURCE: ClassVar[str]

    @property
    def matrix(self) -> Matrix:
        return _diagonal(self.diagonal)

    def apply(self, driving_form: OneForm) -> PhysicalFlux:
        _require_coordinates(driving_form, OneForm, self.graph)
        return PhysicalFlux(
            self.graph,
            tuple(
                _computed(m * x)
                for m, x in zip(self.diagonal, driving_form.values, strict=True)
            ),
        )


@dataclass(frozen=True, slots=True)
class CandidateAMobility(_Mobility):
    params: CandidateAParams
    retained_W_A: tuple[float, ...]
    SOURCE: ClassVar[str] = "candidate_A_retained_W_A"

    def __post_init__(self) -> None:
        if (
            type(self.graph) is not GRCV4Graph
            or type(self.params) is not CandidateAParams
        ):
            raise TypeError("A mobility requires graph and resolved A parameters")
        weights = _vector(self.retained_W_A, positive=True)
        if len(weights) != len(self.graph.oriented_edges):
            raise ValueError("retained W_A must follow live edge order")
        object.__setattr__(self, "retained_W_A", weights)
        object.__setattr__(
            self, "diagonal", _positive_products(self.params.eta, weights)
        )

    @property
    def identity(self) -> str:
        return _identity(
            "grcv4-mobility-sha256",
            {
                "descriptor_version": "grcv4-candidate-mobility-factor-v1",
                "source": self.SOURCE,
                "graph_digest": self.graph.graph_digest,
                "orientation_identity": self.graph.orientation_identity,
                "params": self.params.to_payload(),
                "retained_W_A": self.retained_W_A,
            },
        )


@dataclass(frozen=True, slots=True)
class CandidateCMobility(_Mobility):
    params: CandidateCParams
    SOURCE: ClassVar[str] = "candidate_C_profile_W_C_tr"

    def __post_init__(self) -> None:
        weights = _c_reference(self.graph, self.params)
        object.__setattr__(
            self, "diagonal", _positive_products(self.params.eta_C, weights)
        )

    @property
    def identity(self) -> str:
        return _identity(
            "grcv4-mobility-sha256",
            {
                "descriptor_version": "grcv4-candidate-mobility-factor-v1",
                "source": self.SOURCE,
                "graph_digest": self.graph.graph_digest,
                "orientation_identity": self.graph.orientation_identity,
                "params": self.params.to_payload(),
            },
        )


def candidate_c_structural_hodge(
    graph: GRCV4Graph, params: CandidateCParams
) -> OneFormHodge:
    """E_H(W_C_tr)=diag(W_C_tr), independently of E_M=eta_C diag(W_C_tr)."""
    return OneFormHodge(graph, _diagonal(_c_reference(graph, params)))

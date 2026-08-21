"""Branch-selection accounting shared by GRV2, GRV6, and GRV7."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


FIRST_EXECUTABLE_GATE = "GRV2"


@dataclass(frozen=True)
class BranchCandidate:
    candidate_id: str
    residual: float
    parameter_identity: str


def select_candidate(candidates: Iterable[BranchCandidate]) -> BranchCandidate:
    rows = list(candidates)
    if not rows:
        raise ValueError("selection requires complete nonempty candidate accounting")
    return min(rows, key=lambda row: (row.residual, row.parameter_identity, row.candidate_id))

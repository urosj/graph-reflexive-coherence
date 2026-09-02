"""Closed ET-C9 scenario, API, and view coverage contract."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .errors import SourceAdmissionError


SCENARIO_OWNERS: dict[int, tuple[str, ...]] = {
    1: ("D1",),
    2: ("F9",),
    3: ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "E3", "E4"),
    4: ("C1", "C4", "C5", "C6", "D2", "D3", "D4", "D5", "D6"),
    5: ("C2", "C3", "C7", "C9"),
    6: ("N1", "N2", "N3"),
    7: ("N5", "N6", "D7", "E2"),
    8: ("N4", "C8", "E1"),
}

FORENSIC_API_COVERAGE: dict[str, tuple[str, ...]] = {
    "gate_act": ("F3",),
    "debt_lifecycle": ("F2",),
    "reconstruction_path": ("F1", "N4"),
    "candidate_career": ("F4", "F5"),
    "pruned_choices_at": ("F6", "F7"),
    "negative_claims": ("F7", "E4"),
    "object_dependents": ("F8",),
    "contract_provenance": ("F8",),
    "gate_contribution": ("F3",),
}

WEB_VIEW_COVERAGE: dict[str, tuple[str, ...]] = {
    "focused_navigator": ("F3", "N1", "N2"),
    "family_navigation": ("F4", "F5", "N1", "E3"),
    "triangulation": ("F1", "F2", "F8", "N2"),
    "dependency_reach": ("F8", "N3", "E2"),
    "claim_ceiling": ("F7", "N6", "E2", "E4"),
    "alternative_layer": ("F5", "F6", "N5", "D7", "E3"),
    "lineage_scrubber": ("F3", "N4", "E1"),
    "ripple_view": ("C1", "C2", "C3", "C4", "C5", "C7", "C8", "C9"),
}


def expected_scenario_ids() -> tuple[str, ...]:
    return tuple(
        [f"F{index}" for index in range(1, 10)]
        + [f"N{index}" for index in range(1, 7)]
        + [f"C{index}" for index in range(1, 10)]
        + [f"D{index}" for index in range(1, 8)]
        + [f"E{index}" for index in range(1, 5)]
    )


def validate_coverage(payload: dict[str, Any]) -> None:
    rows = payload.get("scenario_rows")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise SourceAdmissionError("ET-C9 scenario rows are malformed")
    identifiers = [row.get("scenario_id") for row in rows]
    expected = expected_scenario_ids()
    if Counter(identifiers) != Counter(expected):
        raise SourceAdmissionError("ET-C9 scenario population is incomplete or duplicated")
    owner_by_scenario = {
        scenario_id: iteration
        for iteration, scenario_ids in SCENARIO_OWNERS.items()
        for scenario_id in scenario_ids
    }
    if len(owner_by_scenario) != len(expected):
        raise SourceAdmissionError("ET-C9 ownership map is incomplete")
    for row in rows:
        scenario_id = row["scenario_id"]
        if row.get("owner_iteration") != owner_by_scenario[scenario_id]:
            raise SourceAdmissionError(f"ET-C9 owner mismatch: {scenario_id}")
        if row.get("status") != "passed_reconciled":
            raise SourceAdmissionError(f"ET-C9 scenario is not reconciled: {scenario_id}")
        if row.get("scientific_claim_added") is not False:
            raise SourceAdmissionError(f"ET-C9 scenario adds authority: {scenario_id}")
        digest = row.get("owner_record_digest")
        if not isinstance(digest, str) or len(digest) != 64:
            raise SourceAdmissionError(f"ET-C9 owner digest is malformed: {scenario_id}")

    scenario_set = set(expected)
    api = payload.get("forensic_api_coverage")
    web = payload.get("web_view_coverage")
    if not isinstance(api, dict) or set(api) != set(FORENSIC_API_COVERAGE):
        raise SourceAdmissionError("ET-C9 forensic API population changed")
    if not isinstance(web, dict) or set(web) != set(WEB_VIEW_COVERAGE):
        raise SourceAdmissionError("ET-C9 web-view population changed")
    for surface, scenario_ids in {**api, **web}.items():
        if not isinstance(scenario_ids, list) or not scenario_ids:
            raise SourceAdmissionError(f"ET-C9 surface has no scenario: {surface}")
        if not set(scenario_ids) <= scenario_set:
            raise SourceAdmissionError(f"ET-C9 surface cites unknown scenario: {surface}")

"""Selector feedback analysis for GRC9 phenomenology discovery."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from .grc9_manifest import is_session_id


GRC9_SELECTOR_FEEDBACK_VERSION = "grc9_selector_feedback_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9/phenomenology_discovery/sessions")

_TARGETED_COVERAGE: Mapping[str, tuple[str, ...]] = {
    "spark_precursor_positive_control": (
        "S0005/spark_column_proxy_emitter",
        "S0005/spark_instability_emitter",
        "S0006/spark_column_proxy_eps_pass",
        "S0006/spark_column_proxy_eps_fail",
    ),
    "expansion_module_positive_control": (
        "S0005/spark_to_expansion_emitter",
        "S0006/spark_to_expansion_d_eff_low",
        "S0006/spark_to_expansion_d_eff_high",
    ),
    "column_reassignment_positive_control": (
        "S0005/spark_to_expansion_emitter",
        "S0021/dual_spark_combo",
    ),
    "growth_pressure_positive_control": (
        "S0005/growth_pressure_emitter",
        "S0006/growth_pressure_lambda_high",
        "S0006/growth_pressure_lambda_low",
        "S0021/growth_fission_combo",
    ),
    "fission_candidate_positive_control": (
        "S0005/post_expansion_fission_emitter",
        "S0006/post_expansion_fission_min_mass_pass",
        "S0006/post_expansion_fission_min_mass_fail",
        "S0021/spark_fission_combo",
        "S0021/spark_growth_fission_combo",
    ),
    "fission_candidate_negative_control": (
        "S0006/post_expansion_fission_min_mass_fail",
    ),
}

_DIAGNOSTIC_AMBIGUITY_FAMILIES = (
    "row_tensor_regime",
    "column_diagnostic_regime",
    "coarse_profile_sparsity",
    "budget_correction",
    "transport_pathway",
)

_DIAGNOSTIC_TARGETED_EXAMPLES: Mapping[str, tuple[str, ...]] = {
    "row_tensor_regime": (
        "row_tensor_strong_anisotropy_control",
        "row_tensor_flat_control",
    ),
    "column_diagnostic_regime": (
        "column_proxy_near_zero_control",
        "column_proxy_nonzero_control",
    ),
    "coarse_profile_sparsity": (
        "coarse_cache_populated_sparse_profile_control",
        "coarse_cache_populated_dense_profile_control",
    ),
    "budget_correction": (
        "budget_uniform_shift_trigger_control",
        "budget_simplex_projection_trigger_control",
    ),
    "transport_pathway": (
        "transport_short_path_dominant_control",
        "transport_long_path_dominant_control",
    ),
}


@dataclass(frozen=True)
class GRC9SelectorFeedbackItem:
    lane_name: str
    session_id: str
    classification: str
    reason: str
    targeted_coverage: tuple[str, ...] = ()
    proposed_examples: tuple[str, ...] = ()
    proposed_examples_available: tuple[str, ...] = ()
    proposed_examples_missing: tuple[str, ...] = ()

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "lane_name": self.lane_name,
            "session_id": self.session_id,
            "classification": self.classification,
            "reason": self.reason,
            "targeted_coverage": list(self.targeted_coverage),
            "proposed_examples": list(self.proposed_examples),
            "proposed_examples_available": list(self.proposed_examples_available),
            "proposed_examples_missing": list(self.proposed_examples_missing),
        }


@dataclass(frozen=True)
class GRC9SelectorFeedbackSession:
    session_id: str
    source_session_id: str
    source_report_path: str
    feedback_items: tuple[GRC9SelectorFeedbackItem, ...]
    iteration: str = "I06_1_selector_feedback_targeting"

    def to_mapping(self) -> Mapping[str, Any]:
        by_classification: dict[str, int] = {}
        for item in self.feedback_items:
            by_classification[item.classification] = (
                by_classification.get(item.classification, 0) + 1
            )
        return {
            "session_id": self.session_id,
            "iteration": self.iteration,
            "source_session_id": self.source_session_id,
            "source_report_path": self.source_report_path,
            "feedback_item_count": len(self.feedback_items),
            "classification_counts": dict(sorted(by_classification.items())),
            "feedback_items": [item.to_mapping() for item in self.feedback_items],
        }


def run_grc9_selector_feedback(
    *,
    session_id: str = "S0024",
    source_session_id: str = "S0022",
    session_root: str | Path | None = None,
) -> GRC9SelectorFeedbackSession:
    """Classify S0008 selector misses and targeted follow-up needs."""

    if not is_session_id(session_id):
        raise ValueError("session_id must use S0001-style formatting")
    if not is_session_id(source_session_id):
        raise ValueError("source_session_id must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    reports_root = root / "reports"
    reports_root.mkdir(parents=True, exist_ok=True)
    source_report_path = (
        DISCOVERY_SESSION_ROOT
        / source_session_id
        / "reports"
        / "selector_validation_report.json"
    )
    report = _read_required_json(source_report_path, "selector feedback source report")
    items = _feedback_items(report)
    session = GRC9SelectorFeedbackSession(
        session_id=session_id,
        source_session_id=source_session_id,
        source_report_path=str(source_report_path),
        feedback_items=items,
    )
    _write_json(reports_root / "selector_feedback_report.json", session.to_mapping())
    _write_summary_markdown(reports_root / "selector_feedback_summary.md", session)
    _write_json(root / "session_manifest.json", _session_manifest(session))
    _write_readme(root, session)
    return session


def _feedback_items(report: Mapping[str, Any]) -> tuple[GRC9SelectorFeedbackItem, ...]:
    validations = tuple(report.get("validations", ()))
    available_lane_names = {
        str(validation["lane_name"])
        for validation in validations
        if isinstance(validation, Mapping) and "lane_name" in validation
    }
    available_lane_refs = {
        f"{validation.get('session_id')}/{validation.get('lane_name')}"
        for validation in validations
        if isinstance(validation, Mapping)
        and validation.get("session_id") is not None
        and validation.get("lane_name") is not None
    }
    items: list[GRC9SelectorFeedbackItem] = []
    for validation in validations:
        lane_name = str(validation["lane_name"])
        session_id = str(validation["session_id"])
        missing = tuple(str(item) for item in validation.get("missing_selector_ids", ()))
        confidence_label = str(validation.get("confidence_label", ""))
        if missing or confidence_label == "rejected":
            items.append(_classify_miss(validation))
    items.extend(
        _diagnostic_ambiguities(
            validations,
            available_lane_names=available_lane_names,
            available_lane_refs=available_lane_refs,
        )
    )
    return tuple(items)


def _classify_miss(validation: Mapping[str, Any]) -> GRC9SelectorFeedbackItem:
    lane_name = str(validation["lane_name"])
    session_id = str(validation["session_id"])
    if lane_name in _TARGETED_COVERAGE:
        return GRC9SelectorFeedbackItem(
            lane_name=lane_name,
            session_id=session_id,
            classification="covered_by_existing_targeted_examples",
            reason=(
                "Generic S0004 lane missed its predicted lifecycle signature; "
                "the failure is already covered by repaired emitter, threshold, "
                "or combination fixtures."
            ),
            targeted_coverage=_TARGETED_COVERAGE[lane_name],
        )
    return GRC9SelectorFeedbackItem(
        lane_name=lane_name,
        session_id=session_id,
        classification="no_selector_expectation",
        reason="No Iteration 6.1 targeted selector action is assigned to this lane.",
    )


def _diagnostic_ambiguities(
    validations: Sequence[Mapping[str, Any]],
    *,
    available_lane_names: set[str],
    available_lane_refs: set[str],
) -> tuple[GRC9SelectorFeedbackItem, ...]:
    by_lane = {str(validation["lane_name"]): validation for validation in validations}
    items: list[GRC9SelectorFeedbackItem] = []
    for family in _DIAGNOSTIC_AMBIGUITY_FAMILIES:
        positive = by_lane.get(f"{family}_positive_control")
        negative = by_lane.get(f"{family}_negative_control")
        if positive is None or negative is None:
            continue
        positive_passed = tuple(positive.get("passed_selector_ids", ()))
        negative_passed = tuple(negative.get("passed_selector_ids", ()))
        if positive_passed and positive_passed == negative_passed:
            proposed = _DIAGNOSTIC_TARGETED_EXAMPLES[family]
            available, missing = _split_available_examples(
                proposed,
                available_lane_names=available_lane_names,
                available_lane_refs=available_lane_refs,
            )
            items.append(
                GRC9SelectorFeedbackItem(
                    lane_name=family,
                    session_id="S0004",
                    classification="selector_ambiguity_needs_targeted_examples",
                    reason=(
                        "Positive and negative diagnostic controls pass the same "
                        "surface-availability selectors; a discriminating fixture "
                        "pair is needed before stronger motif claims."
                    ),
                    proposed_examples=proposed,
                    proposed_examples_available=available,
                    proposed_examples_missing=missing,
                )
            )
    return tuple(items)


def _split_available_examples(
    examples: Sequence[str],
    *,
    available_lane_names: set[str],
    available_lane_refs: set[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    available: list[str] = []
    missing: list[str] = []
    for example in examples:
        if example in available_lane_names or example in available_lane_refs:
            available.append(example)
        else:
            missing.append(example)
    return tuple(available), tuple(missing)


def _session_manifest(session: GRC9SelectorFeedbackSession) -> Mapping[str, Any]:
    return {
        "session_id": session.session_id,
        "program": "grc9_phenomenology_discovery",
        "family": "grc9",
        "track": "phenomenology_discovery",
        "iteration": session.iteration,
        "session_kind": "selector_feedback",
        "phenomenon": "selector miss and ambiguity targeting",
        "seed_family": "saved telemetry",
        "control_role": "analysis",
        "status": "completed",
        "created_at": "2026-04-25",
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9_selector_feedback --session-id {session.session_id}"
        ),
        "input_paths": [session.source_report_path],
        "output_paths": [
            f"outputs/grc9/phenomenology_discovery/sessions/{session.session_id}/reports/selector_feedback_report.json",
            f"outputs/grc9/phenomenology_discovery/sessions/{session.session_id}/reports/selector_feedback_summary.md",
        ],
        "observation_summary": (
            f"Classified {len(session.feedback_items)} selector feedback items."
        ),
    }


def _write_readme(root: Path, session: GRC9SelectorFeedbackSession) -> None:
    lines = [
        f"# {session.session_id}. GRC9 Selector Feedback",
        "",
        "Status: `completed`",
        "",
        "This session classifies selector misses and ambiguities from S0008.",
        "",
        "Replay:",
        "",
        "```bash",
        f"PYTHONPATH=src ./.venv/bin/python -m pygrc.discovery.grc9_selector_feedback --session-id {session.session_id}",
        "```",
        "",
        "Primary reports:",
        "",
        "- `reports/selector_feedback_report.json`",
        "- `reports/selector_feedback_summary.md`",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_summary_markdown(path: Path, session: GRC9SelectorFeedbackSession) -> None:
    payload = session.to_mapping()
    lines = [
        f"# {session.session_id} Selector Feedback Summary",
        "",
        "## Scope",
        "",
        f"- Source selector session: `{session.source_session_id}`",
        f"- Feedback items: `{payload['feedback_item_count']}`",
        f"- Classification counts: `{payload['classification_counts']}`",
        "",
        "## Feedback Items",
        "",
    ]
    for item in session.feedback_items:
        lines.append(
            f"- `{item.session_id}/{item.lane_name}`: `{item.classification}`"
        )
        if item.targeted_coverage:
            lines.append(f"  - covered by: `{', '.join(item.targeted_coverage)}`")
        if item.proposed_examples:
            lines.append(f"  - proposed examples: `{', '.join(item.proposed_examples)}`")
        if item.proposed_examples_available:
            lines.append(
                f"  - available proposed examples: `{', '.join(item.proposed_examples_available)}`"
            )
        if item.proposed_examples_missing:
            lines.append(
                f"  - missing proposed examples: `{', '.join(item.proposed_examples_missing)}`"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_required_json(path: Path, description: str) -> Mapping[str, Any]:
    if not path.exists():
        raise FileNotFoundError(2, f"{description} missing", str(path))
    return _read_json(path)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", default="S0024")
    parser.add_argument("--source-session-id", default="S0022")
    parser.add_argument("--session-root", default=None)
    parser.add_argument("--full-json", action="store_true")
    args = parser.parse_args(argv)
    session = run_grc9_selector_feedback(
        session_id=args.session_id,
        source_session_id=args.source_session_id,
        session_root=args.session_root,
    )
    payload = session.to_mapping()
    if args.full_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            {
                "session_id": session.session_id,
                "iteration": session.iteration,
                "source_session_id": session.source_session_id,
                "feedback_item_count": payload["feedback_item_count"],
                "classification_counts": payload["classification_counts"],
                "report_path": str(
                    DISCOVERY_SESSION_ROOT
                    / session.session_id
                    / "reports"
                    / "selector_feedback_report.json"
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "GRC9_SELECTOR_FEEDBACK_VERSION",
    "GRC9SelectorFeedbackItem",
    "GRC9SelectorFeedbackSession",
    "run_grc9_selector_feedback",
]

"""Hessian comparator review for GRC9V3 discovery before motif cataloging."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from .grc9_manifest import is_session_id
from .grc9v3_discovery_runner import _run_discovery_lane
from .grc9v3_seed_generator import GRC9V3GeneratedSeed, generate_grc9v3_seed


GRC9V3_HESSIAN_COMPARATOR_REVIEW_VERSION = "grc9v3_hessian_comparator_review_v1"
DISCOVERY_SESSION_ROOT = Path("outputs/grc9v3/phenomenology_discovery/sessions")
EXPERIMENTAL_LOG_PATH = Path("outputs/grc9v3/phenomenology_discovery/ExperimentalLog.md")
HESSIAN_EVENT_PROBE_PROFILE = "grc9v3_discovery_hessian_event_probe_v1"
_DIAGNOSTIC_HESSIAN_LANES = (
    "complex_hessian_row_basis_complex_control",
    "complex_hessian_weighted_least_squares_complex_control",
)
_EVENTFUL_PREDICTED_SEQUENCE = (
    "hybrid_spark_candidate",
    "hybrid_mechanical_expansion",
    "hybrid_spark_completed",
)


@dataclass(frozen=True)
class GRC9V3HessianLaneReview:
    lane_name: str
    source_session_id: str
    artifact_root: str
    backend: str
    classification: str
    event_motif_eligible: bool
    event_count: int
    event_counts_by_kind: Mapping[str, int]
    predicted_event_sequence: tuple[str, ...]
    actual_event_sequence: tuple[str, ...]
    selector_confidence_label: str | None
    selector_confidence_score: int | None
    visual_status: str | None
    overlay_status: str | None
    checkpoint_link_count: int | None
    rationale: str

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "lane_name": self.lane_name,
            "source_session_id": self.source_session_id,
            "artifact_root": self.artifact_root,
            "backend": self.backend,
            "classification": self.classification,
            "event_motif_eligible": self.event_motif_eligible,
            "event_count": self.event_count,
            "event_counts_by_kind": dict(self.event_counts_by_kind),
            "predicted_event_sequence": list(self.predicted_event_sequence),
            "actual_event_sequence": list(self.actual_event_sequence),
            "selector_confidence_label": self.selector_confidence_label,
            "selector_confidence_score": self.selector_confidence_score,
            "visual_status": self.visual_status,
            "overlay_status": self.overlay_status,
            "checkpoint_link_count": self.checkpoint_link_count,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class GRC9V3HessianPairReview:
    pair_id: str
    lane_names: tuple[str, str]
    source_session_ids: tuple[str, ...]
    pair_kind: str
    event_delta_status: str
    same_initial_topology: bool
    same_initial_node_state: bool
    event_sequences_by_backend: Mapping[str, tuple[str, ...]]
    review_action: str
    notes: str

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "pair_id": self.pair_id,
            "lane_names": list(self.lane_names),
            "source_session_ids": list(self.source_session_ids),
            "pair_kind": self.pair_kind,
            "event_delta_status": self.event_delta_status,
            "same_initial_topology": self.same_initial_topology,
            "same_initial_node_state": self.same_initial_node_state,
            "event_sequences_by_backend": {
                key: list(value)
                for key, value in sorted(self.event_sequences_by_backend.items())
            },
            "review_action": self.review_action,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class GRC9V3HessianComparatorReviewSession:
    session_id: str
    diagnostic_source_session_id: str
    selector_session_id: str
    visual_session_id: str
    lane_reviews: tuple[GRC9V3HessianLaneReview, ...]
    pair_reviews: tuple[GRC9V3HessianPairReview, ...]
    report_path: str
    review_index_path: str

    def to_mapping(self) -> Mapping[str, Any]:
        return {
            "session_id": self.session_id,
            "version": GRC9V3_HESSIAN_COMPARATOR_REVIEW_VERSION,
            "diagnostic_source_session_id": self.diagnostic_source_session_id,
            "selector_session_id": self.selector_session_id,
            "visual_session_id": self.visual_session_id,
            "lane_review_count": len(self.lane_reviews),
            "pair_review_count": len(self.pair_reviews),
            "event_motif_eligible_count": sum(
                1 for item in self.lane_reviews if item.event_motif_eligible
            ),
            "diagnostic_comparator_count": sum(
                1 for item in self.lane_reviews if item.classification == "diagnostic_comparator"
            ),
            "eventful_probe_count": sum(
                1 for item in self.lane_reviews if item.classification == "eventful_backend_probe"
            ),
            "backend_event_delta_found_count": sum(
                1
                for item in self.pair_reviews
                if item.event_delta_status == "backend_event_delta_found"
            ),
            "lane_reviews": [item.to_mapping() for item in self.lane_reviews],
            "pair_reviews": [item.to_mapping() for item in self.pair_reviews],
            "report_path": self.report_path,
            "review_index_path": self.review_index_path,
        }


def run_grc9v3_hessian_comparator_review(
    *,
    session_id: str = "S0011",
    diagnostic_source_session_id: str = "S0008",
    selector_session_id: str = "S0009",
    visual_session_id: str = "S0010",
    session_root: str | Path | None = None,
    run_eventful_probe: bool = True,
    update_experimental_log: bool = True,
) -> GRC9V3HessianComparatorReviewSession:
    """Review Hessian lanes and run an eventful backend probe if requested."""

    for value in (session_id, diagnostic_source_session_id, selector_session_id, visual_session_id):
        if not is_session_id(value):
            raise ValueError("session ids must use S0001-style formatting")
    root = Path(session_root) if session_root is not None else DISCOVERY_SESSION_ROOT / session_id
    reports_root = root / "reports"
    lanes_root = root / "generated_lanes"
    reports_root.mkdir(parents=True, exist_ok=True)

    diagnostic_run_report = _read_required_json(
        DISCOVERY_SESSION_ROOT / diagnostic_source_session_id / "reports" / "run_report.json",
        "diagnostic source run report",
    )
    selector_manifest = _read_required_json(
        DISCOVERY_SESSION_ROOT / selector_session_id / "selector_manifest.json",
        "selector manifest",
    )
    visual_index = _read_required_json(
        DISCOVERY_SESSION_ROOT / visual_session_id / "visual_index.json",
        "visual index",
    )
    diagnostic_reviews = tuple(
        _diagnostic_lane_review(
            lane_name,
            diagnostic_run_report=diagnostic_run_report,
            selector_manifest=selector_manifest,
            visual_index=visual_index,
        )
        for lane_name in _DIAGNOSTIC_HESSIAN_LANES
    )
    diagnostic_pair = _pair_review(
        pair_id="s0008_hessian_diagnostic_pair",
        lane_reviews=diagnostic_reviews,
        pair_kind="diagnostic_comparator",
    )

    probe_reviews: tuple[GRC9V3HessianLaneReview, ...] = ()
    probe_pair: GRC9V3HessianPairReview | None = None
    if run_eventful_probe:
        probe_runs = tuple(
            _run_discovery_lane(
                seed=_event_probe_seed(backend),
                requested_steps=3,
                session_root=root,
                lanes_root=lanes_root,
            )
            for backend in ("row_basis_diagonal", "weighted_least_squares")
        )
        probe_reviews = tuple(_probe_lane_review(root.name, lane_run) for lane_run in probe_runs)
        probe_pair = _pair_review(
            pair_id=f"{session_id.lower()}_hessian_eventful_probe_pair",
            lane_reviews=probe_reviews,
            pair_kind="eventful_backend_probe",
        )

    pair_reviews = (diagnostic_pair, *((probe_pair,) if probe_pair is not None else ()))
    review_index_path = root / "hessian_comparator_review.json"
    report_path = reports_root / "hessian_comparator_review_report.json"
    session = GRC9V3HessianComparatorReviewSession(
        session_id=session_id,
        diagnostic_source_session_id=diagnostic_source_session_id,
        selector_session_id=selector_session_id,
        visual_session_id=visual_session_id,
        lane_reviews=(*diagnostic_reviews, *probe_reviews),
        pair_reviews=pair_reviews,
        report_path=str(report_path),
        review_index_path=str(review_index_path),
    )
    _write_json(review_index_path, _review_index_payload(session))
    _write_json(report_path, session.to_mapping())
    _write_json(root / "session_manifest.json", _session_manifest(session, run_eventful_probe))
    _write_summary_markdown(reports_root / "hessian_comparator_review_summary.md", session)
    _write_readme(root, session, run_eventful_probe=run_eventful_probe)
    if update_experimental_log and session_root is None:
        _append_experimental_log(session)
    return session


def _event_probe_seed(backend: str) -> GRC9V3GeneratedSeed:
    source_seed = generate_grc9v3_seed(
        "spark_to_expansion",
        "positive_control",
        parameter_overrides={
            "refined_fixture": True,
            "hessian_backend": backend,
            "expected_outcome": "eventful paired Hessian backend probe",
        },
    )
    lane_name = (
        "hessian_event_probe_weighted_least_squares_control"
        if backend == "weighted_least_squares"
        else "hessian_event_probe_row_basis_control"
    )
    expected_runtime_config = {
        key: value for key, value in dict(source_seed.expected_runtime_config).items()
    }
    modes = dict(expected_runtime_config.get("constitutive_semantic_modes", {}))
    modes["hessian_backend"] = backend
    expected_runtime_config["constitutive_semantic_modes"] = modes
    seed_parameters = dict(source_seed.seed_parameters)
    seed_parameters.update(
        {
            "seed_family": "hessian_event_probe",
            "source_seed_family": "spark_to_expansion",
            "hessian_backend": backend,
            "probe_kind": "eventful_backend_probe",
            "expected_outcome": "spark/expansion should occur under this backend; pair comparison checks whether backend changes the event sequence.",
        }
    )
    return replace(
        source_seed,
        seed_family="hessian_event_probe",
        seed_name=lane_name,
        lane_name=lane_name,
        control_role=(
            "weighted_least_squares_probe"
            if backend == "weighted_least_squares"
            else "row_basis_probe"
        ),
        profile=HESSIAN_EVENT_PROBE_PROFILE,
        seed_parameters=seed_parameters,
        expected_runtime_config=expected_runtime_config,
        predicted_event_sequence=_EVENTFUL_PREDICTED_SEQUENCE,
        required_checkpoint_overlays=(
            "node_overlay",
            "port_overlay",
            "module_overlay",
            "flow_overlay",
        ),
    )


def _diagnostic_lane_review(
    lane_name: str,
    *,
    diagnostic_run_report: Mapping[str, Any],
    selector_manifest: Mapping[str, Any],
    visual_index: Mapping[str, Any],
) -> GRC9V3HessianLaneReview:
    lane = _lane_by_name(diagnostic_run_report, lane_name)
    motif = _motif_by_lane(selector_manifest, lane_name)
    visual = _visual_record_by_lane(visual_index, lane_name)
    artifact_root = str(lane["artifact_root"])
    backend = _backend_from_run_summary(Path(artifact_root) / "telemetry" / "run_summary.json")
    return GRC9V3HessianLaneReview(
        lane_name=lane_name,
        source_session_id=str(lane.get("session_id", "S0008")),
        artifact_root=artifact_root,
        backend=backend,
        classification="diagnostic_comparator",
        event_motif_eligible=False,
        event_count=int(lane.get("event_count", 0)),
        event_counts_by_kind={
            str(key): int(value)
            for key, value in dict(lane.get("event_counts_by_kind", {})).items()
        },
        predicted_event_sequence=tuple(str(item) for item in lane.get("predicted_event_sequence", ())),
        actual_event_sequence=tuple(str(item) for item in lane.get("actual_event_sequence", ())),
        selector_confidence_label=(
            None if motif is None else str(motif.get("confidence_label", ""))
        ),
        selector_confidence_score=(
            None if motif is None else int(motif.get("confidence_score", 0))
        ),
        visual_status=None if visual is None else str(visual.get("visual_status", "")),
        overlay_status=None if visual is None else str(visual.get("overlay_status", "")),
        checkpoint_link_count=(
            None if visual is None else len(tuple(visual.get("checkpoint_links", ())))
        ),
        rationale=(
            "Backend/tensor surfaces are observed, but the lane has no predicted "
            "or actual lifecycle events; preserve it as a diagnostic comparator, "
            "not as event phenomenology."
        ),
    )


def _probe_lane_review(
    session_id: str,
    lane_run: Any,
) -> GRC9V3HessianLaneReview:
    backend = _backend_from_run_summary(Path(lane_run.artifact_root) / "telemetry" / "run_summary.json")
    event_count = int(lane_run.event_count)
    return GRC9V3HessianLaneReview(
        lane_name=str(lane_run.seed.lane_name),
        source_session_id=session_id,
        artifact_root=str(lane_run.artifact_root),
        backend=backend,
        classification="eventful_backend_probe",
        event_motif_eligible=False,
        event_count=event_count,
        event_counts_by_kind={
            str(key): int(value)
            for key, value in dict(lane_run.event_counts_by_kind).items()
        },
        predicted_event_sequence=tuple(str(item) for item in lane_run.seed.predicted_event_sequence),
        actual_event_sequence=tuple(str(item) for item in lane_run.actual_event_sequence),
        selector_confidence_label=None,
        selector_confidence_score=None,
        visual_status=None,
        overlay_status=None,
        checkpoint_link_count=lane_run.checkpoint_count,
        rationale=(
            "This is an eventful backend probe. It is eligible as a Hessian event "
            "delta only if its paired backend changes the lifecycle sequence."
        ),
    )


def _pair_review(
    *,
    pair_id: str,
    lane_reviews: Sequence[GRC9V3HessianLaneReview],
    pair_kind: str,
) -> GRC9V3HessianPairReview:
    if len(lane_reviews) != 2:
        raise ValueError("Hessian pair review requires exactly two lanes")
    by_backend = {item.backend: item for item in lane_reviews}
    event_sequences = {
        backend: tuple(item.actual_event_sequence)
        for backend, item in sorted(by_backend.items())
    }
    event_delta_found = len({event_sequences[key] for key in event_sequences}) > 1
    any_eventful = any(item.event_count > 0 for item in lane_reviews)
    if event_delta_found:
        event_delta_status = "backend_event_delta_found"
        review_action = "eligible_for_hessian_event_delta_review"
    elif any_eventful:
        event_delta_status = "eventful_no_backend_event_delta"
        review_action = "preserve_as_eventful_negative_delta_probe"
    else:
        event_delta_status = "no_event_delta_found"
        review_action = "preserve_as_diagnostic_comparator"
    same_topology = _same_snapshot_digest(lane_reviews, key="topology")
    same_node_state = _same_snapshot_digest(lane_reviews, key="nodes")
    return GRC9V3HessianPairReview(
        pair_id=pair_id,
        lane_names=(lane_reviews[0].lane_name, lane_reviews[1].lane_name),
        source_session_ids=tuple(sorted({item.source_session_id for item in lane_reviews})),
        pair_kind=pair_kind,
        event_delta_status=event_delta_status,
        same_initial_topology=same_topology,
        same_initial_node_state=same_node_state,
        event_sequences_by_backend=event_sequences,
        review_action=review_action,
        notes=(
            "Pair review compares row-basis diagonal and weighted-least-squares "
            "backends on matching graph/state inputs. A lifecycle motif requires "
            "a backend-dependent event sequence; backend/tensor evidence alone "
            "is diagnostic."
        ),
    )


def _same_snapshot_digest(
    lane_reviews: Sequence[GRC9V3HessianLaneReview],
    *,
    key: str,
) -> bool:
    digests = set()
    for item in lane_reviews:
        snapshot_path = Path(item.artifact_root) / "snapshots" / "initial_snapshot.json"
        if not snapshot_path.exists():
            return False
        snapshot = _read_json(snapshot_path)
        digests.add(_digest(snapshot.get(key)))
    return len(digests) == 1


def _backend_from_run_summary(path: Path) -> str:
    summary = _read_required_json(path, "run summary")
    return str(
        summary.get("family_extensions", {})
        .get("grc9v3", {})
        .get("backend_summary", {})
        .get("hessian_backend", "")
    )


def _lane_by_name(run_report: Mapping[str, Any], lane_name: str) -> Mapping[str, Any]:
    for lane in run_report.get("lanes", ()):
        if isinstance(lane, Mapping) and lane.get("lane_name") == lane_name:
            return lane
    raise ValueError(f"lane {lane_name!r} not found in run report")


def _motif_by_lane(
    selector_manifest: Mapping[str, Any],
    lane_name: str,
) -> Mapping[str, Any] | None:
    for motif in selector_manifest.get("motifs", ()):
        if isinstance(motif, Mapping) and motif.get("lane") == lane_name:
            return motif
    return None


def _visual_record_by_lane(
    visual_index: Mapping[str, Any],
    lane_name: str,
) -> Mapping[str, Any] | None:
    for record in visual_index.get("records", ()):
        if isinstance(record, Mapping) and record.get("lane_name") == lane_name:
            return record
    return None


def _review_index_payload(
    session: GRC9V3HessianComparatorReviewSession,
) -> Mapping[str, Any]:
    return {
        "version": GRC9V3_HESSIAN_COMPARATOR_REVIEW_VERSION,
        "session_id": session.session_id,
        "review_boundary": "hessian_backend_evidence_is_diagnostic_unless_backend_changes_lifecycle_events",
        "lane_reviews": [item.to_mapping() for item in session.lane_reviews],
        "pair_reviews": [item.to_mapping() for item in session.pair_reviews],
    }


def _session_manifest(
    session: GRC9V3HessianComparatorReviewSession,
    run_eventful_probe: bool,
) -> Mapping[str, Any]:
    return {
        "session_id": session.session_id,
        "program": "grc9v3_phenomenology_discovery",
        "family": "grc9v3",
        "track": "phenomenology_discovery",
        "iteration": "I08_1_hessian_comparator_review",
        "session_kind": "hessian_comparator_review",
        "phenomenon": "Hessian comparator classification and eventful backend probe",
        "seed_family": "hessian_backend_comparison",
        "control_role": "review_and_probe",
        "status": "completed",
        "created_at": "2026-04-26",
        "git_revision": _git_revision(),
        "dirty_worktree": None,
        "replay_command": (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_hessian_comparator_review --session-id {session.session_id}"
        ),
        "input_paths": [
            f"outputs/grc9v3/phenomenology_discovery/sessions/{session.diagnostic_source_session_id}/reports/run_report.json",
            f"outputs/grc9v3/phenomenology_discovery/sessions/{session.selector_session_id}/selector_manifest.json",
            f"outputs/grc9v3/phenomenology_discovery/sessions/{session.visual_session_id}/visual_index.json",
        ],
        "output_paths": [
            session.review_index_path,
            session.report_path,
        ],
        "telemetry_paths": sorted(
            {
                str(Path(item.artifact_root) / "telemetry")
                for item in session.lane_reviews
                if item.source_session_id == session.session_id
            }
        ),
        "checkpoint_paths": sorted(
            {
                str(Path(item.artifact_root) / "telemetry" / "graph_checkpoints")
                for item in session.lane_reviews
                if item.source_session_id == session.session_id
            }
        ),
        "prediction_summary": "Current S0008 Hessian lanes should classify as diagnostic comparators; the eventful probe should report whether backend choice changes lifecycle events.",
        "observation_summary": (
            f"{session.to_mapping()['diagnostic_comparator_count']} diagnostic lanes, "
            f"{session.to_mapping()['eventful_probe_count']} eventful probe lanes, "
            f"{session.to_mapping()['backend_event_delta_found_count']} backend event deltas found."
        ),
        "replay_notes": (
            "Replay re-runs the eventful backend probe and rebuilds the Hessian comparator review."
            if run_eventful_probe
            else "Replay rebuilds the review without running the eventful backend probe."
        ),
    }


def _write_summary_markdown(
    path: Path,
    session: GRC9V3HessianComparatorReviewSession,
) -> None:
    payload = session.to_mapping()
    lines = [
        f"# {session.session_id} Hessian Comparator Review Summary",
        "",
        "## Scope",
        "",
        f"- Diagnostic source session: `{session.diagnostic_source_session_id}`",
        f"- Selector session: `{session.selector_session_id}`",
        f"- Visual session: `{session.visual_session_id}`",
        f"- Lane reviews: `{payload['lane_review_count']}`",
        f"- Diagnostic comparators: `{payload['diagnostic_comparator_count']}`",
        f"- Eventful probe lanes: `{payload['eventful_probe_count']}`",
        f"- Backend event deltas found: `{payload['backend_event_delta_found_count']}`",
        "",
        "## Pair Reviews",
        "",
    ]
    for pair in session.pair_reviews:
        lines.append(
            f"- `{pair.pair_id}`: `{pair.event_delta_status}`, "
            f"action `{pair.review_action}`, same topology `{pair.same_initial_topology}`, "
            f"same node state `{pair.same_initial_node_state}`"
        )
    lines.extend(["", "## Lane Reviews", ""])
    for lane in session.lane_reviews:
        lines.append(
            f"- `{lane.source_session_id}/{lane.lane_name}`: `{lane.classification}`, "
            f"backend `{lane.backend}`, events `{lane.event_count}`, "
            f"event motif eligible `{lane.event_motif_eligible}`"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_readme(
    root: Path,
    session: GRC9V3HessianComparatorReviewSession,
    *,
    run_eventful_probe: bool,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {session.session_id}. GRC9V3 Hessian Comparator Review",
        "",
        "Status: `completed`",
        "",
        "This session separates Hessian backend diagnostics from lifecycle event motifs and records an eventful backend probe.",
        "",
        "Replay:",
        "",
        "```bash",
        (
            "PYTHONPATH=src ./.venv/bin/python -m "
            f"pygrc.discovery.grc9v3_hessian_comparator_review --session-id {session.session_id}"
        ),
        "```",
        "",
        f"Run eventful probe: `{run_eventful_probe}`",
        "",
        "Primary reports:",
        "",
        "- `hessian_comparator_review.json`",
        "- `reports/hessian_comparator_review_report.json`",
        "- `reports/hessian_comparator_review_summary.md`",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _append_experimental_log(session: GRC9V3HessianComparatorReviewSession) -> None:
    EXPERIMENTAL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not EXPERIMENTAL_LOG_PATH.exists():
        EXPERIMENTAL_LOG_PATH.write_text(_experimental_log_header(), encoding="utf-8")
    text = EXPERIMENTAL_LOG_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    payload = session.to_mapping()
    row = (
        f"| `{session.session_id}` | `completed` | `hessian_comparator_review` | "
        "`I08_1_hessian_comparator_review` | Hessian comparator classification and eventful backend probe | "
        "`hessian_backend_comparison` | "
        f"`outputs/grc9v3/phenomenology_discovery/sessions/{session.session_id}/` | "
        f"Iteration 8.1: {payload['diagnostic_comparator_count']} diagnostic lanes, "
        f"{payload['eventful_probe_count']} eventful probe lanes, "
        f"{payload['backend_event_delta_found_count']} backend event deltas found |"
    )
    prefix = f"| `{session.session_id}` |"
    filtered = [line for line in lines if not line.startswith(prefix)]
    filtered.append(row)
    EXPERIMENTAL_LOG_PATH.write_text("\n".join(filtered) + "\n", encoding="utf-8")


def _experimental_log_header() -> str:
    return "\n".join(
        [
            "# GRC9V3 Phenomenology Discovery Experimental Log",
            "",
            "## Session Index",
            "",
            "| Session | Status | Kind | Iteration | Phenomenon | Seed Family | Artifact Root | Notes |",
            "|---|---|---|---|---|---|---|---|",
        ]
    ) + "\n"


def _digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_required_json(path: Path, description: str) -> Mapping[str, Any]:
    if not path.exists():
        raise FileNotFoundError(2, f"{description} missing", str(path))
    return _read_json(path)


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _git_revision() -> str:
    try:
        result = subprocess.run(
            ("git", "rev-parse", "HEAD"),
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-id", default="S0011")
    parser.add_argument("--diagnostic-source-session-id", default="S0008")
    parser.add_argument("--selector-session-id", default="S0009")
    parser.add_argument("--visual-session-id", default="S0010")
    parser.add_argument("--session-root", default=None)
    parser.add_argument("--skip-eventful-probe", action="store_true")
    parser.add_argument("--full-json", action="store_true")
    args = parser.parse_args(argv)
    session = run_grc9v3_hessian_comparator_review(
        session_id=args.session_id,
        diagnostic_source_session_id=args.diagnostic_source_session_id,
        selector_session_id=args.selector_session_id,
        visual_session_id=args.visual_session_id,
        session_root=args.session_root,
        run_eventful_probe=not args.skip_eventful_probe,
    )
    payload = session.to_mapping()
    if args.full_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            {
                "session_id": session.session_id,
                "lane_review_count": payload["lane_review_count"],
                "pair_review_count": payload["pair_review_count"],
                "diagnostic_comparator_count": payload["diagnostic_comparator_count"],
                "eventful_probe_count": payload["eventful_probe_count"],
                "backend_event_delta_found_count": payload[
                    "backend_event_delta_found_count"
                ],
                "report_path": session.report_path,
                "review_index_path": session.review_index_path,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()


__all__ = [
    "GRC9V3_HESSIAN_COMPARATOR_REVIEW_VERSION",
    "GRC9V3HessianComparatorReviewSession",
    "GRC9V3HessianLaneReview",
    "GRC9V3HessianPairReview",
    "run_grc9v3_hessian_comparator_review",
]

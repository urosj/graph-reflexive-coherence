"""Identity-continuity matcher over normalized motion windows."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pygrc.core import canonicalize_json_value

from .motion import (
    MotionCarrierSet,
    MotionCompetingClaim,
    MotionEvidence,
    MotionRecord,
    MotionReport,
)
from .motion_loader import (
    MotionCheckpointEdgeEvidence,
    MotionCheckpointEvidence,
    MotionCheckpointNodeEvidence,
    MotionWindowLoadResult,
    load_motion_window,
)
from .motion_representative import (
    RepresentativeMotionSelection,
    select_representatives_for_checkpoint,
)


IDENTITY_MOTION_CLASSIFIER_ID = "motion_identity_continuity_matcher"
IDENTITY_MOTION_CLASSIFIER_VERSION = "motion_inference_iter5_v1"

_MIN_MATCH_SCORE = 0.50
_MIN_BRANCH_SCORE = 0.20
_STRONG_MATCH_SCORE = 0.75
_MASS_OVERLAP_WEIGHT = 0.40
_REPRESENTATIVE_CONTINUITY_WEIGHT = 0.10
_FLUX_PATH_WEIGHT = 0.20
_SUCCESSOR_CONTINUITY_WEIGHT = 0.20
_HIERARCHY_PROVENANCE_WEIGHT = 0.10
_GROUP_CONTINUITY_WEIGHT = 0.10
_DIAGNOSTIC_CONFIDENCE_CAP = 0.25
_COLLAPSE_MASS_RATIO = 0.75
_MIN_PATH_EDGE_FLUX = 1e-12


@dataclass(frozen=True)
class IdentityMotionGroup:
    """Checkpoint-local identity candidate group."""

    checkpoint_id: str
    step_index: int
    group_id: str
    node_ids: tuple[int, ...]
    basin_ids: tuple[str, ...]
    mass: float | None
    representative_node_id: int
    representative_selection_mode: str

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "checkpoint_id": self.checkpoint_id,
                "step_index": self.step_index,
                "group_id": self.group_id,
                "node_ids": list(self.node_ids),
                "basin_ids": list(self.basin_ids),
                "mass": self.mass,
                "representative_node_id": self.representative_node_id,
                "representative_selection_mode": self.representative_selection_mode,
            }
        )


@dataclass(frozen=True)
class IdentityMotionMatch:
    """Candidate old/new identity continuity match."""

    old_group_id: str
    new_group_id: str
    score: float
    mass_overlap_fraction: float
    representative_continuity: float
    flux_path_support: float
    successor_continuity: float
    hierarchy_provenance_continuity: float
    group_continuity: float
    shared_node_ids: tuple[int, ...]
    path_edge_ids: tuple[int, ...]

    def to_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "old_group_id": self.old_group_id,
                "new_group_id": self.new_group_id,
                "score": self.score,
                "mass_overlap_fraction": self.mass_overlap_fraction,
                "representative_continuity": self.representative_continuity,
                "flux_path_support": self.flux_path_support,
                "successor_continuity": self.successor_continuity,
                "hierarchy_provenance_continuity": self.hierarchy_provenance_continuity,
                "group_continuity": self.group_continuity,
                "shared_node_ids": list(self.shared_node_ids),
                "path_edge_ids": list(self.path_edge_ids),
            }
        )


@dataclass(frozen=True)
class IdentityMotionInferenceResult:
    """Identity-motion records plus matching diagnostics."""

    window_load_result: MotionWindowLoadResult
    records: tuple[MotionRecord, ...]
    groups: tuple[IdentityMotionGroup, ...]
    matches: tuple[IdentityMotionMatch, ...]
    diagnostic_only: bool
    matcher_diagnostics: Mapping[str, Any] = field(default_factory=dict)

    def to_report(
        self,
        *,
        source_session_id: str | None = None,
        source_artifact_paths: Sequence[str] = (),
    ) -> MotionReport:
        return MotionReport(
            source_session_id=source_session_id
            or _source_session_id_from_path(self.window_load_result.artifact_root),
            source_runtime_family=self.window_load_result.landscape_load_result.source_runtime_family,
            source_artifact_paths=tuple(source_artifact_paths),
            motion_window=self.window_load_result.motion_window,
            records=self.records,
        )

    def to_summary_mapping(self) -> dict[str, Any]:
        return canonicalize_json_value(
            {
                "classifier_id": IDENTITY_MOTION_CLASSIFIER_ID,
                "classifier_version": IDENTITY_MOTION_CLASSIFIER_VERSION,
                "source_runtime_family": (
                    self.window_load_result.landscape_load_result.source_runtime_family
                ),
                "record_count": len(self.records),
                "group_count": len(self.groups),
                "match_count": len(self.matches),
                "diagnostic_only": self.diagnostic_only,
                "matcher_diagnostics": canonicalize_json_value(dict(self.matcher_diagnostics)),
                "motion_window": self.window_load_result.motion_window.to_mapping(),
                "records": [record.to_mapping() for record in self.records],
                "groups": [group.to_mapping() for group in self.groups],
                "matches": [match.to_mapping() for match in self.matches],
            }
        )


def infer_identity_motion(
    path_or_result: str | Path | MotionWindowLoadResult,
    *,
    min_match_score: float = _MIN_MATCH_SCORE,
    allow_short_persistence_window: bool = True,
) -> IdentityMotionInferenceResult:
    """Infer identity continuity relationships across checkpoint windows."""

    if not 0.0 <= min_match_score <= 1.0:
        raise ValueError("min_match_score must be in [0, 1]")
    load_result = (
        path_or_result
        if isinstance(path_or_result, MotionWindowLoadResult)
        else load_motion_window(
            path_or_result,
            allow_short_persistence_window=allow_short_persistence_window,
        )
    )
    groups_by_checkpoint = {
        checkpoint.checkpoint_id: _groups_for_checkpoint(checkpoint)
        for checkpoint in load_result.checkpoint_evidence
    }
    records: list[MotionRecord] = []
    all_matches: list[IdentityMotionMatch] = []
    all_diagnostics: list[Mapping[str, Any]] = []
    for previous, current in zip(
        load_result.checkpoint_evidence,
        load_result.checkpoint_evidence[1:],
    ):
        old_groups = groups_by_checkpoint.get(previous.checkpoint_id, ())
        new_groups = groups_by_checkpoint.get(current.checkpoint_id, ())
        matches, diagnostics = _candidate_matches(previous, current, old_groups, new_groups)
        all_matches.extend(matches)
        all_diagnostics.append(diagnostics)
        records.extend(
            _records_for_checkpoint_pair(
                load_result,
                previous,
                current,
                old_groups,
                new_groups,
                matches,
                min_match_score=min_match_score,
            )
        )
    return IdentityMotionInferenceResult(
        window_load_result=load_result,
        records=tuple(records),
        groups=tuple(
            group
            for checkpoint in load_result.checkpoint_evidence
            for group in groups_by_checkpoint.get(checkpoint.checkpoint_id, ())
        ),
        matches=tuple(all_matches),
        diagnostic_only=load_result.availability.diagnostic_only,
        matcher_diagnostics=_aggregate_matcher_diagnostics(all_diagnostics),
    )


def infer_identity_motion_report(
    path_or_result: str | Path | MotionWindowLoadResult,
    *,
    source_session_id: str | None = None,
    source_artifact_paths: Sequence[str] = (),
    **kwargs: Any,
) -> MotionReport:
    """Infer identity motion and return a serializable motion report."""

    result = infer_identity_motion(path_or_result, **kwargs)
    return result.to_report(
        source_session_id=source_session_id,
        source_artifact_paths=source_artifact_paths,
    )


def _groups_for_checkpoint(
    checkpoint: MotionCheckpointEvidence,
) -> tuple[IdentityMotionGroup, ...]:
    selections = {
        selection.group_id: selection
        for selection in select_representatives_for_checkpoint(checkpoint)
    }
    groups: list[IdentityMotionGroup] = []
    for group_id, node_ids in _node_groups(checkpoint.nodes).items():
        selection = selections.get(group_id)
        if selection is None:
            continue
        mass = _group_mass(checkpoint.nodes, node_ids)
        basin_ids = tuple(
            sorted(
                set(
                    checkpoint.nodes[node_id].basin_id
                    for node_id in node_ids
                    if checkpoint.nodes[node_id].basin_id is not None
                )
            )
        )
        groups.append(
            IdentityMotionGroup(
                checkpoint_id=checkpoint.checkpoint_id,
                step_index=checkpoint.step_index,
                group_id=group_id,
                node_ids=tuple(sorted(node_ids)),
                basin_ids=basin_ids or (group_id,),
                mass=mass,
                representative_node_id=selection.representative_node_id,
                representative_selection_mode=selection.selection_mode,
            )
        )
    return tuple(sorted(groups, key=lambda group: group.group_id))


def _node_groups(
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
) -> dict[str, tuple[int, ...]]:
    grouped: dict[str, list[int]] = {}
    for node_id, node in sorted(nodes.items()):
        group_id = node.basin_id if node.basin_id is not None else f"node_{node_id}"
        grouped.setdefault(group_id, []).append(node_id)
    return {key: tuple(value) for key, value in sorted(grouped.items())}


def _candidate_matches(
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    old_groups: Sequence[IdentityMotionGroup],
    new_groups: Sequence[IdentityMotionGroup],
) -> tuple[tuple[IdentityMotionMatch, ...], Mapping[str, Any]]:
    matches: list[IdentityMotionMatch] = []
    edges = _edge_evidence_by_pair(previous, current)
    candidate_pairs, candidate_reasons = _candidate_match_pairs(
        previous,
        current,
        old_groups,
        new_groups,
        edges,
    )
    old_by_id = {group.group_id: group for group in old_groups}
    new_by_id = {group.group_id: group for group in new_groups}
    for old in old_groups:
        for new in new_groups:
            if (old.group_id, new.group_id) not in candidate_pairs:
                continue
            shared = tuple(sorted(set(old.node_ids) & set(new.node_ids)))
            mass_overlap = _mass_overlap_fraction(previous.nodes, current.nodes, old, new, shared)
            representative = 1.0 if old.representative_node_id == new.representative_node_id else 0.0
            path_edges = _path_edge_ids(
                old.representative_node_id,
                new.representative_node_id,
                edges,
            )
            flux_support = 1.0 if path_edges else 0.0
            successor = _successor_continuity(previous.nodes, old, new)
            hierarchy_provenance = _hierarchy_provenance_continuity(previous.nodes, current.nodes, old, new)
            group_continuity = 1.0 if old.group_id == new.group_id else 0.0
            score = min(
                1.0,
                _MASS_OVERLAP_WEIGHT * mass_overlap
                + _REPRESENTATIVE_CONTINUITY_WEIGHT * representative
                + _FLUX_PATH_WEIGHT * flux_support
                + _SUCCESSOR_CONTINUITY_WEIGHT * successor
                + _HIERARCHY_PROVENANCE_WEIGHT * hierarchy_provenance
                + _GROUP_CONTINUITY_WEIGHT * group_continuity,
            )
            if score <= 0.0:
                continue
            matches.append(
                IdentityMotionMatch(
                    old_group_id=old.group_id,
                    new_group_id=new.group_id,
                    score=float(score),
                    mass_overlap_fraction=float(mass_overlap),
                    representative_continuity=representative,
                    flux_path_support=flux_support,
                    successor_continuity=successor,
                    hierarchy_provenance_continuity=hierarchy_provenance,
                    group_continuity=group_continuity,
                    shared_node_ids=shared,
                    path_edge_ids=tuple(sorted(path_edges)),
                )
            )
    sorted_matches = tuple(
        sorted(
            matches,
            key=lambda match: (-match.score, match.old_group_id, match.new_group_id),
        )
    )
    all_pair_count = len(old_groups) * len(new_groups)
    diagnostics = {
        "previous_checkpoint_id": previous.checkpoint_id,
        "current_checkpoint_id": current.checkpoint_id,
        "previous_step_index": previous.step_index,
        "current_step_index": current.step_index,
        "old_group_count": len(old_groups),
        "new_group_count": len(new_groups),
        "all_pair_count": all_pair_count,
        "candidate_edge_count": len(candidate_pairs),
        "scored_pair_count": len(candidate_pairs),
        "all_pair_count_avoided": max(0, all_pair_count - len(candidate_pairs)),
        "candidate_generation_mode": "sparse_evidence_index",
        "candidate_reason_counts": _candidate_reason_counts(candidate_reasons),
        "match_count": len(sorted_matches),
    }
    return sorted_matches, diagnostics


def _candidate_match_pairs(
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    old_groups: Sequence[IdentityMotionGroup],
    new_groups: Sequence[IdentityMotionGroup],
    edges: Mapping[tuple[int, int], MotionCheckpointEdgeEvidence],
) -> tuple[set[tuple[str, str]], Mapping[tuple[str, str], tuple[str, ...]]]:
    old_by_node = _groups_by_node(old_groups)
    new_by_node = _groups_by_node(new_groups)
    old_by_group = {group.group_id: group for group in old_groups}
    new_by_group = {group.group_id: group for group in new_groups}
    new_by_token = _groups_by_provenance_token(current.nodes, new_groups)
    new_by_parent = _groups_by_hierarchy_parent(current.nodes, new_groups)
    new_by_representative = _groups_by_representative(new_groups)
    new_group_ids = set(new_by_group)
    pairs: set[tuple[str, str]] = set()
    reasons: dict[tuple[str, str], set[str]] = {}

    def add_pair(old_group_id: str, new_group_id: str, reason: str) -> None:
        if old_group_id not in old_by_group or new_group_id not in new_by_group:
            return
        pair = (old_group_id, new_group_id)
        pairs.add(pair)
        reasons.setdefault(pair, set()).add(reason)

    for old in old_groups:
        if old.group_id in new_group_ids:
            add_pair(old.group_id, old.group_id, "same_group_id")
        for node_id in old.node_ids:
            for new_group_id in new_by_node.get(node_id, ()):
                add_pair(old.group_id, new_group_id, "shared_node")
            successor = previous.nodes[node_id].successor_node_id
            if successor is not None:
                for new_group_id in new_by_node.get(successor, ()):
                    add_pair(old.group_id, new_group_id, "successor_node")
            parent_id = previous.nodes[node_id].hierarchy_parent_id
            if parent_id is not None:
                for new_group_id in new_by_parent.get(parent_id, ()):
                    add_pair(old.group_id, new_group_id, "hierarchy_parent")
            for token in previous.nodes[node_id].provenance_tokens:
                for new_group_id in new_by_token.get(token, ()):
                    add_pair(old.group_id, new_group_id, "provenance_token")
        for new_group_id in new_by_representative.get(old.representative_node_id, ()):
            add_pair(old.group_id, new_group_id, "representative_node")

    for old_id, reachable_nodes in _flux_reachable_nodes_by_old_group(old_groups, edges).items():
        for node_id in reachable_nodes:
            for new_group_id in new_by_node.get(node_id, ()):
                add_pair(old_id, new_group_id, "flux_reachable")

    return pairs, {
        pair: tuple(sorted(pair_reasons))
        for pair, pair_reasons in sorted(reasons.items())
    }


def _groups_by_node(groups: Sequence[IdentityMotionGroup]) -> dict[int, tuple[str, ...]]:
    result: dict[int, list[str]] = {}
    for group in groups:
        for node_id in group.node_ids:
            result.setdefault(node_id, []).append(group.group_id)
    return {
        node_id: tuple(sorted(group_ids))
        for node_id, group_ids in sorted(result.items())
    }


def _groups_by_representative(groups: Sequence[IdentityMotionGroup]) -> dict[int, tuple[str, ...]]:
    result: dict[int, list[str]] = {}
    for group in groups:
        result.setdefault(group.representative_node_id, []).append(group.group_id)
    return {
        node_id: tuple(sorted(group_ids))
        for node_id, group_ids in sorted(result.items())
    }


def _groups_by_provenance_token(
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
    groups: Sequence[IdentityMotionGroup],
) -> dict[str, tuple[str, ...]]:
    result: dict[str, set[str]] = {}
    for group in groups:
        for node_id in group.node_ids:
            for token in nodes[node_id].provenance_tokens:
                result.setdefault(token, set()).add(group.group_id)
    return {
        token: tuple(sorted(group_ids))
        for token, group_ids in sorted(result.items())
    }


def _groups_by_hierarchy_parent(
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
    groups: Sequence[IdentityMotionGroup],
) -> dict[str, tuple[str, ...]]:
    result: dict[str, set[str]] = {}
    for group in groups:
        for node_id in group.node_ids:
            parent_id = nodes[node_id].hierarchy_parent_id
            if parent_id is not None:
                result.setdefault(parent_id, set()).add(group.group_id)
    return {
        parent_id: tuple(sorted(group_ids))
        for parent_id, group_ids in sorted(result.items())
    }


def _flux_reachable_nodes_by_old_group(
    old_groups: Sequence[IdentityMotionGroup],
    edges: Mapping[tuple[int, int], MotionCheckpointEdgeEvidence],
) -> dict[str, tuple[int, ...]]:
    adjacency: dict[int, list[int]] = {}
    for edge in edges.values():
        if not _edge_has_flux(edge):
            continue
        adjacency.setdefault(edge.source_node_id, []).append(edge.target_node_id)
        adjacency.setdefault(edge.target_node_id, []).append(edge.source_node_id)
    result: dict[str, tuple[int, ...]] = {}
    for old in old_groups:
        reachable: set[int] = set()
        queue = [old.representative_node_id]
        visited = {old.representative_node_id}
        for node_id in queue:
            for neighbor in sorted(adjacency.get(node_id, ())):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                reachable.add(neighbor)
                queue.append(neighbor)
        result[old.group_id] = tuple(sorted(reachable))
    return result


def _candidate_reason_counts(
    candidate_reasons: Mapping[tuple[str, str], tuple[str, ...]],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for reasons in candidate_reasons.values():
        for reason in reasons:
            counts[reason] = counts.get(reason, 0) + 1
    return dict(sorted(counts.items()))


def _aggregate_matcher_diagnostics(
    diagnostics: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    reason_counts: dict[str, int] = {}
    for item in diagnostics:
        for reason, count in item.get("candidate_reason_counts", {}).items():
            reason_counts[str(reason)] = reason_counts.get(str(reason), 0) + int(count)
    return {
        "candidate_generation_mode": "sparse_evidence_index",
        "checkpoint_pair_count": len(diagnostics),
        "old_group_count_total": sum(int(item.get("old_group_count", 0)) for item in diagnostics),
        "new_group_count_total": sum(int(item.get("new_group_count", 0)) for item in diagnostics),
        "all_pair_count_total": sum(int(item.get("all_pair_count", 0)) for item in diagnostics),
        "candidate_edge_count_total": sum(int(item.get("candidate_edge_count", 0)) for item in diagnostics),
        "scored_pair_count_total": sum(int(item.get("scored_pair_count", 0)) for item in diagnostics),
        "all_pair_count_avoided_total": sum(
            int(item.get("all_pair_count_avoided", 0)) for item in diagnostics
        ),
        "match_count_total": sum(int(item.get("match_count", 0)) for item in diagnostics),
        "candidate_reason_counts": dict(sorted(reason_counts.items())),
        "checkpoint_pairs": [canonicalize_json_value(dict(item)) for item in diagnostics],
    }


def _records_for_checkpoint_pair(
    load_result: MotionWindowLoadResult,
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    old_groups: Sequence[IdentityMotionGroup],
    new_groups: Sequence[IdentityMotionGroup],
    matches: Sequence[IdentityMotionMatch],
    *,
    min_match_score: float,
) -> tuple[MotionRecord, ...]:
    strong = tuple(match for match in matches if match.score >= min_match_score)
    branch_matches = tuple(match for match in matches if match.score >= _MIN_BRANCH_SCORE)
    old_by_id = {group.group_id: group for group in old_groups}
    new_by_id = {group.group_id: group for group in new_groups}
    matches_by_old: dict[str, list[IdentityMotionMatch]] = {}
    matches_by_new: dict[str, list[IdentityMotionMatch]] = {}
    for match in branch_matches:
        matches_by_old.setdefault(match.old_group_id, []).append(match)
        matches_by_new.setdefault(match.new_group_id, []).append(match)
    records: list[MotionRecord] = []
    handled_old: set[str] = set()
    handled_new: set[str] = set()
    for old_id in sorted(matches_by_old):
        outgoing = tuple(sorted(matches_by_old[old_id], key=lambda match: match.new_group_id))
        if len(outgoing) > 1:
            records.append(
                _motion_record(
                    load_result,
                    previous,
                    current,
                    relationship="split",
                    old_groups=(old_by_id[old_id],),
                    new_groups=tuple(new_by_id[match.new_group_id] for match in outgoing),
                    matches=outgoing,
                    competing_relationships=("ambiguous", "dissolved"),
                )
            )
            handled_old.add(old_id)
            handled_new.update(match.new_group_id for match in outgoing)
    for new_id in sorted(matches_by_new):
        incoming = tuple(sorted(matches_by_new[new_id], key=lambda match: match.old_group_id))
        remaining = tuple(match for match in incoming if match.old_group_id not in handled_old)
        if len(remaining) > 1:
            relationship = _many_to_one_relationship(
                tuple(old_by_id[match.old_group_id] for match in remaining),
                new_by_id[new_id],
            )
            records.append(
                _motion_record(
                    load_result,
                    previous,
                    current,
                    relationship=relationship,
                    old_groups=tuple(old_by_id[match.old_group_id] for match in remaining),
                    new_groups=(new_by_id[new_id],),
                    matches=remaining,
                    competing_relationships=("collapsed", "ambiguous"),
                )
            )
            handled_old.update(match.old_group_id for match in remaining)
            handled_new.add(new_id)
    for match in strong:
        if match.old_group_id in handled_old or match.new_group_id in handled_new:
            continue
        old = old_by_id[match.old_group_id]
        new = new_by_id[match.new_group_id]
        relationship = _one_to_one_relationship(old, new, match)
        records.append(
            _motion_record(
                load_result,
                previous,
                current,
                relationship=relationship,
                old_groups=(old,),
                new_groups=(new,),
                matches=(match,),
                competing_relationships=_competing_for_relationship(relationship),
            )
        )
        handled_old.add(match.old_group_id)
        handled_new.add(match.new_group_id)
    for old in old_groups:
        if old.group_id in handled_old:
            continue
        weak = tuple(match for match in matches if match.old_group_id == old.group_id)
        if weak:
            records.append(
                _motion_record(
                    load_result,
                    previous,
                    current,
                    relationship="ambiguous",
                    old_groups=(old,),
                    new_groups=tuple(new_by_id[match.new_group_id] for match in weak[:2]),
                    matches=weak[:2],
                    competing_relationships=("dissolved", "walked"),
                )
            )
            handled_new.update(match.new_group_id for match in weak)
        else:
            records.append(
                _motion_record(
                    load_result,
                    previous,
                    current,
                    relationship="dissolved",
                    old_groups=(old,),
                    new_groups=(),
                    matches=(),
                    competing_relationships=("ambiguous",),
                )
            )
        handled_old.add(old.group_id)
    for new in new_groups:
        if new.group_id in handled_new:
            continue
        records.append(
            _motion_record(
                load_result,
                previous,
                current,
                relationship="emerged",
                old_groups=(),
                new_groups=(new,),
                matches=(),
                competing_relationships=("ambiguous",),
            )
        )
    return tuple(records)


def _one_to_one_relationship(
    old: IdentityMotionGroup,
    new: IdentityMotionGroup,
    match: IdentityMotionMatch,
) -> str:
    if old.group_id == new.group_id and old.representative_node_id == new.representative_node_id:
        return "stationary"
    if old.group_id == new.group_id:
        return "drifted"
    if match.flux_path_support > 0.0 or match.representative_continuity > 0.0:
        return "walked"
    return "ambiguous"


def _many_to_one_relationship(
    old_groups: Sequence[IdentityMotionGroup],
    new_group: IdentityMotionGroup,
) -> str:
    old_mass = sum(group.mass or 0.0 for group in old_groups)
    new_mass = new_group.mass or 0.0
    if old_mass > 0.0 and new_mass < old_mass * _COLLAPSE_MASS_RATIO:
        return "collapsed"
    return "merged"


def _motion_record(
    load_result: MotionWindowLoadResult,
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
    *,
    relationship: str,
    old_groups: Sequence[IdentityMotionGroup],
    new_groups: Sequence[IdentityMotionGroup],
    matches: Sequence[IdentityMotionMatch],
    competing_relationships: Sequence[str],
) -> MotionRecord:
    diagnostic_only = load_result.availability.diagnostic_only
    confidence = _confidence(relationship, matches, diagnostic_only=diagnostic_only)
    evidence_quality = _evidence_quality(relationship, confidence, diagnostic_only=diagnostic_only)
    degradation_reasons = _degradation_reasons(relationship, matches, diagnostic_only=diagnostic_only)
    step_ids = (previous.step_index, current.step_index)
    old_node_ids = tuple(sorted({node_id for group in old_groups for node_id in group.node_ids}))
    new_node_ids = tuple(sorted({node_id for group in new_groups for node_id in group.node_ids}))
    old_basin_ids = tuple(sorted({basin for group in old_groups for basin in group.basin_ids}))
    new_basin_ids = tuple(sorted({basin for group in new_groups for basin in group.basin_ids}))
    match_edge_ids = tuple(sorted({edge_id for match in matches for edge_id in match.path_edge_ids}))
    best_score = max((match.score for match in matches), default=0.0)
    return MotionRecord(
        motion_id=(
            f"motion_identity_step{previous.step_index:04d}_"
            f"{current.step_index:04d}_{relationship}_"
            f"{_safe_id('_'.join(group.group_id for group in old_groups) or 'none')}_to_"
            f"{_safe_id('_'.join(group.group_id for group in new_groups) or 'none')}"
        ),
        classifier_id=IDENTITY_MOTION_CLASSIFIER_ID,
        classifier_version=IDENTITY_MOTION_CLASSIFIER_VERSION,
        motion_kind="identity",
        relationship=relationship,
        confidence=confidence,
        evidence_quality=evidence_quality,
        source_runtime_family=load_result.landscape_load_result.source_runtime_family,
        step_window=(previous.step_index, current.step_index),
        step_ids=step_ids,
        old_carriers=MotionCarrierSet(
            node_ids=old_node_ids or tuple(group.representative_node_id for group in old_groups),
            basin_ids=old_basin_ids or tuple(group.group_id for group in old_groups),
            primitive_ids=() if old_groups else ("no_predecessor",),
        ),
        new_carriers=MotionCarrierSet(
            node_ids=new_node_ids or tuple(group.representative_node_id for group in new_groups),
            basin_ids=new_basin_ids or tuple(group.group_id for group in new_groups),
            primitive_ids=() if new_groups else ("no_successor",),
        ),
        evidence=MotionEvidence(
            telemetry_fields=(
                "checkpoint.node_records.basin_id",
                "checkpoint.node_records.coherence",
                "motion_identity.mass_overlap_fraction",
                "motion_identity.representative_continuity",
                "motion_identity.flux_path_support",
                "motion_identity.successor_continuity",
                "motion_identity.hierarchy_provenance_continuity",
                "motion_identity.group_continuity",
            ),
            checkpoint_ids=(previous.checkpoint_id, current.checkpoint_id),
            step_ids=step_ids,
            node_ids=tuple(sorted(set(old_node_ids) | set(new_node_ids))),
            edge_ids=match_edge_ids,
            budget_accountability=_budget_accountability(load_result),
            degradation_reasons=degradation_reasons,
        ),
        transferred_mass=_transferred_mass(old_groups, new_groups, matches),
        competing_claims=_competing_claims(relationship, best_score, competing_relationships),
        non_claims=(
            "not_authored_vs_observed_comparison",
            "identity_motion_requires_review_before_catalog_acceptance",
        ),
    )


def _confidence(
    relationship: str,
    matches: Sequence[IdentityMotionMatch],
    *,
    diagnostic_only: bool,
) -> float:
    if diagnostic_only:
        return _DIAGNOSTIC_CONFIDENCE_CAP
    if relationship in {"dissolved", "emerged"}:
        return 0.55
    if not matches:
        return 0.50
    best = max(match.score for match in matches)
    if relationship in {"stationary", "walked"} and best >= _STRONG_MATCH_SCORE:
        return 0.85
    if relationship in {"split", "merged", "collapsed"}:
        return min(0.80, max(0.60, best))
    if relationship == "drifted":
        return min(0.75, max(0.60, best))
    return min(0.60, max(0.45, best))


def _evidence_quality(
    relationship: str,
    confidence: float,
    *,
    diagnostic_only: bool,
) -> str:
    if diagnostic_only:
        return "diagnostic_only"
    if relationship == "ambiguous":
        return "partial"
    if confidence >= 0.80:
        return "strong"
    if confidence >= 0.50:
        return "partial"
    return "degraded"


def _degradation_reasons(
    relationship: str,
    matches: Sequence[IdentityMotionMatch],
    *,
    diagnostic_only: bool,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if diagnostic_only:
        reasons.append("diagnostic_only_window")
    if relationship == "ambiguous":
        reasons.append("competing_or_weak_continuity")
    if not matches and relationship in {"dissolved", "emerged"}:
        reasons.append("no_sufficient_continuity_match")
    if matches and not any(match.flux_path_support for match in matches):
        reasons.append("flux_path_support_unavailable")
    return tuple(sorted(set(reasons)))


def _competing_for_relationship(relationship: str) -> tuple[str, ...]:
    if relationship == "stationary":
        return ("ambiguous", "dissolved")
    if relationship == "drifted":
        return ("stationary", "walked", "ambiguous")
    if relationship == "walked":
        return ("drifted", "split", "ambiguous")
    if relationship == "split":
        return ("walked", "dissolved", "ambiguous")
    if relationship == "merged":
        return ("collapsed", "ambiguous")
    if relationship == "collapsed":
        return ("merged", "dissolved", "ambiguous")
    return ("ambiguous",)


def _competing_claims(
    relationship: str,
    best_score: float,
    competing_relationships: Sequence[str],
) -> tuple[MotionCompetingClaim, ...]:
    claims: list[MotionCompetingClaim] = []
    for index, competing in enumerate(dict.fromkeys(competing_relationships)):
        if competing == relationship:
            continue
        confidence = max(0.05, min(0.45, (1.0 - best_score) * 0.5 - index * 0.05))
        claims.append(
            MotionCompetingClaim(
                relationship=competing,
                confidence=confidence,
                reason=f"competing interpretation for {relationship} identity continuity",
                classifier_id=IDENTITY_MOTION_CLASSIFIER_ID,
            )
        )
    if not claims:
        claims.append(
            MotionCompetingClaim(
                relationship="ambiguous",
                confidence=0.10,
                reason="contract requires explicit competing interpretation",
                classifier_id=IDENTITY_MOTION_CLASSIFIER_ID,
            )
        )
    return tuple(claims)


def _mass_overlap_fraction(
    previous_nodes: Mapping[int, MotionCheckpointNodeEvidence],
    current_nodes: Mapping[int, MotionCheckpointNodeEvidence],
    old: IdentityMotionGroup,
    new: IdentityMotionGroup,
    shared_node_ids: Sequence[int],
) -> float:
    if not shared_node_ids:
        return 0.0
    old_total = old.mass if old.mass is not None else float(len(old.node_ids))
    new_total = new.mass if new.mass is not None else float(len(new.node_ids))
    if set(old.node_ids) == set(new.node_ids):
        return max(0.0, min(1.0, min(old_total, new_total) / max(old_total, new_total, 1e-12)))
    overlap = 0.0
    for node_id in shared_node_ids:
        old_node = previous_nodes[node_id]
        new_node = current_nodes[node_id]
        old_mass = _node_mass(old_node)
        new_mass = _node_mass(new_node)
        if old_mass is None or new_mass is None:
            overlap += 1.0
        else:
            overlap += min(old_mass, new_mass)
    denominator = max(min(old_total, new_total), 1e-12)
    return max(0.0, min(1.0, overlap / denominator))


def _path_edge_ids(
    start_node_id: int,
    end_node_id: int,
    edges: Mapping[tuple[int, int], MotionCheckpointEdgeEvidence],
) -> tuple[int, ...]:
    if start_node_id == end_node_id:
        return ()
    direct = edges.get(_pair_key(start_node_id, end_node_id))
    if _edge_has_flux(direct):
        return (direct.edge_id,)
    adjacency: dict[int, list[tuple[int, int]]] = {}
    for edge in edges.values():
        if not _edge_has_flux(edge):
            continue
        adjacency.setdefault(edge.source_node_id, []).append((edge.target_node_id, edge.edge_id))
        adjacency.setdefault(edge.target_node_id, []).append((edge.source_node_id, edge.edge_id))
    queue: list[tuple[int, tuple[int, ...], tuple[int, ...]]] = [(start_node_id, (start_node_id,), ())]
    for node_id, visited, path_edges in queue:
        for neighbor, edge_id in sorted(adjacency.get(node_id, ())):
            if neighbor in visited:
                continue
            candidate_edges = (*path_edges, edge_id)
            if neighbor == end_node_id:
                return tuple(candidate_edges)
            queue.append((neighbor, (*visited, neighbor), candidate_edges))
    return ()


def _edge_has_flux(edge: MotionCheckpointEdgeEvidence | None) -> bool:
    return (
        edge is not None
        and edge.signed_flux is not None
        and abs(float(edge.signed_flux)) > _MIN_PATH_EDGE_FLUX
    )


def _successor_continuity(
    previous_nodes: Mapping[int, MotionCheckpointNodeEvidence],
    old: IdentityMotionGroup,
    new: IdentityMotionGroup,
) -> float:
    new_nodes = set(new.node_ids)
    available = 0
    hits = 0
    for node_id in old.node_ids:
        successor = previous_nodes[node_id].successor_node_id
        if successor is None:
            continue
        available += 1
        if successor in new_nodes:
            hits += 1
    if available == 0:
        return 0.0
    return hits / available


def _hierarchy_provenance_continuity(
    previous_nodes: Mapping[int, MotionCheckpointNodeEvidence],
    current_nodes: Mapping[int, MotionCheckpointNodeEvidence],
    old: IdentityMotionGroup,
    new: IdentityMotionGroup,
) -> float:
    old_parent_ids = {
        previous_nodes[node_id].hierarchy_parent_id
        for node_id in old.node_ids
        if previous_nodes[node_id].hierarchy_parent_id is not None
    }
    new_parent_ids = {
        current_nodes[node_id].hierarchy_parent_id
        for node_id in new.node_ids
        if current_nodes[node_id].hierarchy_parent_id is not None
    }
    parent_score = _set_overlap_score(old_parent_ids, new_parent_ids)
    old_tokens = {
        token
        for node_id in old.node_ids
        for token in previous_nodes[node_id].provenance_tokens
    }
    new_tokens = {
        token
        for node_id in new.node_ids
        for token in current_nodes[node_id].provenance_tokens
    }
    token_score = _set_overlap_score(old_tokens, new_tokens)
    return max(parent_score, token_score)


def _set_overlap_score(first: set[str], second: set[str]) -> float:
    if not first or not second:
        return 0.0
    return len(first & second) / max(len(first), len(second))


def _edge_evidence_by_pair(
    previous: MotionCheckpointEvidence,
    current: MotionCheckpointEvidence,
) -> dict[tuple[int, int], MotionCheckpointEdgeEvidence]:
    result: dict[tuple[int, int], MotionCheckpointEdgeEvidence] = {}
    for source in (previous.edges, current.edges):
        for edge in source.values():
            key = _pair_key(edge.source_node_id, edge.target_node_id)
            existing = result.get(key)
            if existing is None or existing.signed_flux is None:
                result[key] = edge
    return result


def _group_mass(
    nodes: Mapping[int, MotionCheckpointNodeEvidence],
    node_ids: Sequence[int],
) -> float | None:
    masses: list[float] = []
    for node_id in node_ids:
        mass = _node_mass(nodes[node_id])
        if mass is not None:
            masses.append(mass)
    if not masses:
        return None
    return float(sum(masses))


def _node_mass(node: MotionCheckpointNodeEvidence) -> float | None:
    if node.basin_mass is not None:
        return float(node.basin_mass)
    if node.coherence is not None:
        return max(float(node.coherence), 0.0)
    return None


def _transferred_mass(
    old_groups: Sequence[IdentityMotionGroup],
    new_groups: Sequence[IdentityMotionGroup],
    matches: Sequence[IdentityMotionMatch],
) -> float | None:
    if matches:
        old_mass = sum(group.mass or 0.0 for group in old_groups)
        new_mass = sum(group.mass or 0.0 for group in new_groups)
        if old_mass > 0.0 or new_mass > 0.0:
            return min(old_mass, new_mass)
    return None


def _budget_accountability(load_result: MotionWindowLoadResult) -> str:
    modes = {
        graph.budget_audit.budget_accountability
        for graph in load_result.evidence_substrate.checkpoint_graphs
    }
    if "leak_error" in modes:
        return "leak_error"
    if modes == {"conserved_zero"}:
        return "conserved_zero"
    return "unavailable"


def _pair_key(first: int, second: int) -> tuple[int, int]:
    return (first, second) if first <= second else (second, first)


def _safe_id(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_") or "group"


def _source_session_id_from_path(path: Path) -> str:
    return path.name or "unknown_session"


__all__ = [
    "IDENTITY_MOTION_CLASSIFIER_ID",
    "IDENTITY_MOTION_CLASSIFIER_VERSION",
    "IdentityMotionGroup",
    "IdentityMotionInferenceResult",
    "IdentityMotionMatch",
    "infer_identity_motion",
    "infer_identity_motion_report",
]

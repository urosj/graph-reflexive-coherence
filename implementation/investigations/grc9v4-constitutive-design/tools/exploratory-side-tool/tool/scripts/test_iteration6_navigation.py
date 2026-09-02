#!/usr/bin/env python3
"""Focused ET-C6 Python compiler and projection tests."""

from __future__ import annotations

import copy
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.canonical import canonical_bytes, load_json_object, record_digest  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.web import hydrate_selection_projection, selection_payload  # noqa: E402


def main() -> int:
    repo_root = repository_root()
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")
    checks = 0

    def require(condition: bool, label: str) -> None:
        nonlocal checks
        if not condition:
            raise RuntimeError(f"ET-C6 focused test failed: {label}")
        checks += 1

    records = SIDE_TOOL_ROOT / "records"
    bundle = load_json_object(records / "ETC6StaticNavigationBundle.json")
    parity = load_json_object(records / "ETC6CrossSurfaceParity.json")
    require(bundle["bundle_digest"] == record_digest(bundle, "bundle_digest"), "bundle_digest")
    require(parity["parity_digest"] == record_digest(parity, "parity_digest"), "parity_digest")
    for node_id, expected in parity["selection_payloads"].items():
        actual = hydrate_selection_projection(bundle, node_id)
        require(canonical_bytes(actual) == canonical_bytes(expected), f"parity:{node_id}")
        require(selection_payload(bundle, node_id) == canonical_bytes(expected), f"payload:{node_id}")

    candidate_a = next(row for row in bundle["family_coverage"] if row["family_id"] == "candidate_A")
    lifecycle = next(row for row in bundle["family_coverage"] if row["family_id"] == "complete_step_lifecycle")
    require(candidate_a["object_count"] == len(candidate_a["node_ids"]) == 7, "N1_candidate_A")
    require(lifecycle["object_count"] == len(lifecycle["node_ids"]) == 12, "N1_lifecycle")
    require(sum(row["object_count"] for row in bundle["family_coverage"]) == 67, "N1_total")

    debt = hydrate_selection_projection(bundle, "debt_transformation:D7-DEBT-COVARIANCE-VERIFICATION")
    claim = hydrate_selection_projection(bundle, "current_claim:D10-CL-N-001")
    require(any(row["lens_id"] == "forward_work" for row in debt["triangulation"]), "N2_debt_forward_work")
    require(all(row["lens_id"] != "forward_work" for row in claim["triangulation"]), "N2_claim_no_forward_work")
    require(any(row["lens_id"] == "bearing_debt" for row in claim["triangulation"]), "N2_claim_bearing_debt")
    require(all(row["lens_id"] != "support" for row in debt["triangulation"]), "N2_debt_no_claim_support")

    obj = hydrate_selection_projection(bundle, "normative_object:A-DIRECTIONAL-CONTRAST")
    reach = obj["dependency_reach"]
    require(reach["classification"] == "dependency_reach_not_importance_priority_or_severity", "N3_boundary")
    require(set(reach["by_support_semantic"]) == {"required", "one_of", "conditional", "negative_boundary", "indeterminate_requires_review", "not_applicable"}, "N3_semantics")
    require(reach["annotation_display_only"]["transitive_count"] == 0, "N3_annotations_nonpropagating")

    for node_id in (
        "current_claim:D10-CL-N-001",
        "candidate:V4-A-temporalized-W",
        "candidate:V4-B-independent-derived-carrier",
        "normative_object:A-DIRECTIONAL-CONTRAST",
    ):
        projection = hydrate_selection_projection(bundle, node_id)
        require(projection["selection"]["source_record_id"], f"forensic_source:{node_id}")
        require(projection["selection"]["source_json_pointer"], f"forensic_pointer:{node_id}")
        require(len(projection["focus"]["nodes"]) <= 32, f"bounded_nodes:{node_id}")
        require(len(projection["focus"]["edges"]) <= 72, f"bounded_edges:{node_id}")

    try:
        hydrate_selection_projection(bundle, "claim:not-admitted")
    except KeyError:
        checks += 1
    else:
        raise RuntimeError("unknown selection did not fail closed")

    tampered = copy.deepcopy(bundle)
    tampered["selection_projections"].pop("current_claim:D10-CL-N-001")
    require(tampered["bundle_digest"] != record_digest(tampered, "bundle_digest"), "tamper_detected")
    require(bundle["authority"]["browser_propagation_rule"] is False, "no_browser_rule")
    require(bundle["authority"]["browser_mutation_authoring"] is False, "no_browser_mutation")
    require(bundle["snapshot_semantics"] == "build_time_snapshot_live_rescan_unavailable_in_static_browser", "snapshot_label")

    print(f"ET_C6_TEST_PASS checks={checks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

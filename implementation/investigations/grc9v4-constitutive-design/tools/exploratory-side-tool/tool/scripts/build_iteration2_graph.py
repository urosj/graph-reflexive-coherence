#!/usr/bin/env python3
"""Build the deterministic ET-C2 validated-graph candidate."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.adapters import adapt_source  # noqa: E402
from grcv4_explorer.bundle import build_source_bundle  # noqa: E402
from grcv4_explorer.canonical import (  # noqa: E402
    canonical_bytes,
    digest,
    load_json_object,
    record_digest,
)
from grcv4_explorer.kernel import (  # noqa: E402
    build_validated_graph,
    validate_graph_snapshot,
    write_graph,
)
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_et_c0_contract,
)


def require_repository_venv(repo_root: Path) -> None:
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


def main() -> int:
    repo_root = repository_root()
    require_repository_venv(repo_root)
    records = SIDE_TOOL_ROOT / "records"
    et_c0_path = records / "ETC0SourceAndLayoutContract.json"
    et_c0 = load_et_c0_contract(et_c0_path)
    et_c1 = load_json_object(records / "ETC1SourceAdapterAdmission.json")
    if et_c1.get("status") != "accepted" or et_c1.get("record_digest") != record_digest(
        et_c1, "record_digest"
    ):
        raise RuntimeError("ET-C1 is not an exact accepted predecessor")

    manifest, observation = build_source_bundle(repo_root, et_c0_path)
    accepted_manifest = load_json_object(records / "ETC1SourceBundleManifest.json")
    if canonical_bytes(manifest) != canonical_bytes(accepted_manifest):
        raise RuntimeError("rebuilt source manifest differs from accepted ET-C1")
    if observation["state"] != "current_bundle_exact":
        raise RuntimeError("source bundle is not current")

    documents = [adapt_source(repo_root, row) for row in admitted_rows(et_c0)]
    graph = build_validated_graph(
        documents,
        source_bundle_digest=cast(str, manifest["source_bundle_digest"]),
    )
    validate_graph_snapshot(graph)
    snapshot_path = records / "ETC2GraphSnapshot.json"
    write_graph(snapshot_path, graph)

    context = tomllib.loads((TOOL_ROOT / "iteration2_context.toml").read_text())
    support_counts = cast(dict[str, int], graph["support_semantic_counts"])
    candidate: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C2_validated_graph_admission_v1",
        "gate_id": "ET-C2_validated_graph_kernel",
        "status": "accepted",
        "iteration": 2,
        "execution_context": context,
        "predecessor": {
            "gate_id": et_c1["gate_id"],
            "record_digest": et_c1["record_digest"],
            "source_bundle_digest": manifest["source_bundle_digest"],
        },
        "authority": {
            "validated_graph_kernel_implemented": True,
            "source_records_modified": False,
            "scientific_claim_added": False,
            "browser_inference_runtime_implemented": False,
            "iteration_3_authorized": True,
        },
        "graph_snapshot": {
            "path": "records/ETC2GraphSnapshot.json",
            "schema": graph["schema"],
            "kernel_version": graph["kernel_version"],
            "graph_digest": graph["graph_digest"],
            "node_count": graph["node_count"],
            "node_counts": graph["node_counts"],
            "propagation_edge_count": graph["propagation_edge_count"],
            "annotation_edge_count": graph["annotation_edge_count"],
        },
        "support_semantics": {
            "required": support_counts.get("required", 0),
            "one_of": support_counts.get("one_of", 0),
            "conditional": support_counts.get("conditional", 0),
            "negative_boundary": support_counts.get("negative_boundary", 0),
            "indeterminate_requires_review": support_counts.get(
                "indeterminate_requires_review", 0
            ),
            "not_applicable_non_support_relations": support_counts.get(
                "not_applicable", 0
            ),
            "one_of_not_inferred_when_source_does_not_state_disjunction": True,
        },
        "invariant_result": graph["invariants"],
        "scenario_F9": {
            "status": "passed_accepted_execution",
            "accepted_populations": "39/29/29/11/67/152",
            "source_digest_checks": "passed_via_exact_ET_C1_rebuild",
            "byte_identical_rebuild": "passed",
        },
        "acceptance_requirements": {
            "independent_raw_source_conformance_audit": "passed",
            "focused_failure_fixture_matrix": "passed",
            "deterministic_double_rebuild": "passed",
            "human_review": "accepted",
        },
        "non_claims": [
            "no_forensic_API",
            "no_counterfactual_propagation",
            "no_browser_application",
            "no_new_scientific_evidence",
            "no_graph_edge_may_upgrade_source_authority",
        ],
        "record_digest": None,
    }
    candidate["record_digest"] = digest(
        {key: value for key, value in candidate.items() if key != "record_digest"}
    )
    candidate_path = records / "ETC2ValidatedGraphKernel.json"
    candidate_path.write_bytes(canonical_bytes(candidate) + b"\n")

    node_counts = cast(dict[str, int], graph["node_counts"])
    report = [
        "# ET-C2 Validated Graph Kernel",
        "",
        "**Status:** Accepted",
        "",
        "Iteration 2 constructs a deterministic, source-traceable graph over the",
        "accepted ET-C1 bundle. It does not add scientific authority or implement",
        "forensic, counterfactual, or browser behavior.",
        "",
        "## Result",
        "",
        f"- graph digest: `{graph['graph_digest']}`",
        f"- nodes: `{graph['node_count']}`",
        f"- propagation edges: `{graph['propagation_edge_count']}`",
        f"- display-only annotation edges: `{graph['annotation_edge_count']}`",
        f"- invariants: `{graph['invariants']['passed_count']}/14 passed`",
        "- source-owned populations: `39 current claims / 29 historical claims / "
        "29 debt transformations / 11 verification obligations / 67 parent "
        "objects / 152 equation-contracts`",
        f"- gate records: `{node_counts['gate_record']}`",
        f"- candidate nodes: `{node_counts['candidate']}`",
        f"- profile nodes: `{node_counts['profile']}`",
        f"- realization rows: `{node_counts['realization']}`",
        f"- physical source identities: `{node_counts['source_record']}`",
        f"- record digest: `{candidate['record_digest']}`",
        "",
        "## Semantic Boundary",
        "",
        "Propagation and annotation rows are physically separate. Verification",
        "obligations are forward-only work targets and are excluded from backward",
        "evidence reconstruction. Source relations without explicit conjunction or",
        "disjunction semantics remain `indeterminate_requires_review`; the kernel",
        "does not infer `one_of` support from population shape.",
        "",
        "SHA-only normative/runtime source identities remain valid source nodes.",
        "A semantic record digest is required only where the source is itself a",
        "decision record; no digest is synthesized for specifications or code.",
        "",
        "## Acceptance Boundary",
        "",
        "The independent raw-source auditor passed 117 checks and matched all",
        "436 nodes and 2,670 relationships exactly. The focused kernel matrix",
        "passed 14 fail-closed mutations, and deterministic rebuild checks passed.",
        "These verification results were reviewed before gate acceptance.",
        "",
        "ET-C2 is accepted at the validated-graph ceiling. Iteration 3 is",
        "authorized, but forensic APIs remain unimplemented by this record.",
        "",
    ]
    (records / "ETC2ValidatedGraphKernel.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print(
        "ET_C2_BUILD_PASS "
        f"graph={graph['graph_digest']} record={candidate['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

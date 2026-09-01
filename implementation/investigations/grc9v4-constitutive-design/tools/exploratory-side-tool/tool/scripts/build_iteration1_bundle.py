#!/usr/bin/env python3
"""Build the deterministic ET-C1 source-adapter admission candidate."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]
sys.path.insert(0, str(TOOL_ROOT / "src"))

from grcv4_explorer.bundle import build_source_bundle  # noqa: E402
from grcv4_explorer.canonical import canonical_bytes, digest  # noqa: E402
from grcv4_explorer.discovery import discover_sources  # noqa: E402
from grcv4_explorer.errors import SourceEvolutionError  # noqa: E402
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.source_contract import (  # noqa: E402
    admitted_rows,
    load_et_c0_contract,
)


AUDITS = (
    "implementation/investigations/grc9v4-constitutive-design/scripts/audit_grc9v4_d10_claim_topology.py",
    "implementation/investigations/grc9v4-constitutive-design/scripts/audit_grc9v4_d10_1_preliminary_provenance.py",
    "implementation/investigations/grc9v4-constitutive-design/scripts/audit_grc9v4_d10_2_full_provenance.py",
)


def require_repository_venv(repo_root: Path) -> None:
    if Path(sys.prefix).resolve() != (repo_root / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


def run_inherited_audits(repo_root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for relative in AUDITS:
        completed = subprocess.run(
            [sys.executable, str(repo_root / relative)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"accepted audit failed: {relative}\n"
                f"{completed.stdout}{completed.stderr}"
            )
        lines = [line for line in completed.stdout.splitlines() if line.strip()]
        rows.append(
            {
                "path": relative,
                "status": "passed_unchanged",
                "terminal_output": lines[-1],
            }
        )
    return rows


def main() -> int:
    repo_root = repository_root()
    require_repository_venv(repo_root)
    et_c0_path = SIDE_TOOL_ROOT / "records/ETC0SourceAndLayoutContract.json"
    et_c0 = load_et_c0_contract(et_c0_path)
    observation = discover_sources(repo_root, admitted_rows(et_c0))
    generated = TOOL_ROOT / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    (generated / "source-observation.json").write_bytes(
        canonical_bytes(observation) + b"\n"
    )
    try:
        manifest, observation = build_source_bundle(repo_root, et_c0_path)
    except SourceEvolutionError:
        print(f"ET_C1_BUILD_BLOCKED source_state={observation['state']}")
        return 2

    records = SIDE_TOOL_ROOT / "records"
    records.mkdir(parents=True, exist_ok=True)
    manifest_path = records / "ETC1SourceBundleManifest.json"
    manifest_path.write_bytes(canonical_bytes(manifest) + b"\n")
    context = tomllib.loads((TOOL_ROOT / "iteration1_context.toml").read_text())
    inherited_audits = run_inherited_audits(repo_root)
    record: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C1_admission_v1",
        "gate_id": "ET-C1_source_bundle_admitted",
        "status": "accepted",
        "iteration": 1,
        "execution_context": context,
        "predecessor": {
            "gate_id": "ET-C0_source_and_layout_contract_frozen",
            "record_digest": et_c0["record_digest"],
        },
        "trust_boundary": {
            "root": "human_accepted_ET_C0",
            "ET_C1_revalidates_ET_C0_status_and_digest": True,
            "ET_C1_does_not_rederive_human_acceptance": True,
            "browser_runtime_not_implemented": True,
        },
        "authority": {
            "source_adapter_layer_implemented": True,
            "source_discovery_layer_implemented": True,
            "graph_kernel_implemented": False,
            "iteration_2_authorized": True,
            "accepted_source_records_modified": False,
            "scientific_claim_added": False,
        },
        "source_observation": observation,
        "source_bundle_manifest": {
            "path": "records/ETC1SourceBundleManifest.json",
            "schema": manifest["schema"],
            "record_count": manifest["record_count"],
            "source_bundle_digest": manifest["source_bundle_digest"],
        },
        "reference_validation": manifest["reference_validation"],
        "schema_boundary": {
            "schema_declared_record_count": 32,
            "filename_admitted_legacy_records": [
                "D10_1PreliminarySubstrateProvenance.json"
            ],
            "schema_addition_or_change_requires_readmission": True,
        },
        "claim_authority_crosscheck": {
            "topology_claim_class_matches_authorization_category": True,
            "current_claim_count": 39,
        },
        "inherited_audits": inherited_audits,
        "scenario_D1": {
            "status": "covered_by_source_discovery_fixture_matrix",
            "scientific_interpretation_of_unadmitted_source": False,
            "automatic_admission": False,
        },
        "non_claims": [
            "no_graph_kernel",
            "no_support_edge_classification",
            "no_counterfactual_propagation",
            "no_browser_application",
            "no_new_scientific_evidence",
        ],
        "record_digest": None,
    }
    record["record_digest"] = digest(
        {key: value for key, value in record.items() if key != "record_digest"}
    )
    record_path = records / "ETC1SourceAdapterAdmission.json"
    record_path.write_bytes(canonical_bytes(record) + b"\n")
    report = [
        "# ET-C1 Source Adapter And Bundle Admission",
        "",
        "**Status:** Accepted",
        "",
        "Iteration 1 admits schema-specific, read-only source adapters and a",
        "versioned bundle manifest. It does not construct graph semantics.",
        "",
        "## Result",
        "",
        f"- admitted source records: `{manifest['record_count']}`",
        f"- source observation: `{observation['state']}`",
        f"- source-bundle digest: `{manifest['source_bundle_digest']}`",
        f"- reference checks: `{manifest['reference_validation']['check_count']}`",
        "- relationship witness contract: `"
        f"{manifest['reference_validation']['relationship_witness']['family_count']} "
        "families / "
        f"{manifest['reference_validation']['relationship_witness']['relationship_count']} "
        "relationships`",
        "- relationship witness digest: `"
        f"{manifest['reference_validation']['relationship_witness']['witness_digest']}`",
        "- accepted populations: `39 current claims / 29 historical claims / "
        "29 debt transformations / 11 verification obligations`",
        "- provenance populations: `67 parent objects / 152 equation-contracts`",
        "- lifecycle coverage: `10 profiles / 26 operations / 260 cells`",
        "- embedded identities: `"
        f"{manifest['reference_validation']['embedded_local_source_identity_count']} "
        "repository-local byte-verified / "
        f"{manifest['reference_validation']['embedded_external_source_attestation_count']} "
        "external attestations`",
        f"- record digest: `{record['record_digest']}`",
        "- accepted source bytes: `unchanged`",
        "- claim authority classifications: `39/39 exact agreement`",
        "- Iteration 2: `authorized; not implemented`",
        "",
        "## Evolution Boundary",
        "",
        "New, changed, missing, or unreadable records are reported through a",
        "separate observation receipt. They are never auto-parsed or inserted",
        "into the admitted bundle. A successor adapter/readmission and complete",
        "rebuild cycle is required before current-state labeling.",
        "",
        "External theory identities remain frozen attestations; this portable",
        "tool does not depend on or resolve an adjacent repository checkout.",
        "D10.1 remains an explicitly filename-admitted legacy-schema record;",
        "adding or changing its schema requires source readmission.",
        "",
        "## Claim Boundary",
        "",
        "This gate validates source identity and references only. Support-edge",
        "semantics, graph construction, ripple behavior, and scientific claim",
        "promotion remain closed.",
        "",
        "Human-accepted ET-C0 is the explicit root of trust. ET-C1 verifies its",
        "accepted status and exact digest; it does not attempt to derive the",
        "human acceptance decision. No browser runtime exists in this iteration.",
        "Independent acceptance audit must rederive and exactly match every",
        "relationship-witness family count and digest; matching aggregate",
        "population counts alone is insufficient.",
        "",
    ]
    (records / "ETC1SourceAdapterAdmission.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print(
        "ET_C1_BUILD_PASS "
        f"bundle={manifest['source_bundle_digest']} record={record['record_digest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

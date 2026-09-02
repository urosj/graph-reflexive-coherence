"""Build the deterministic ET-C1 source-bundle manifest."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .adapters import adapt_source
from .canonical import digest, file_sha256
from .discovery import discover_sources
from .errors import SourceAdmissionError, SourceEvolutionError
from .source_contract import admitted_rows, load_et_c0_contract
from .validation import validate_cross_source_contract


def build_source_bundle(
    repo_root: Path,
    et_c0_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    et_c0 = load_et_c0_contract(et_c0_path)
    rows = admitted_rows(et_c0)
    observation = discover_sources(repo_root, rows)
    if observation["state"] != "current_bundle_exact":
        raise SourceEvolutionError(f"source refresh required: {observation['state']}")

    hashes_before = {
        str(row["path"]): file_sha256(repo_root / str(row["path"])) for row in rows
    }
    documents = [adapt_source(repo_root, row) for row in rows]
    if len({document.record_identifier for document in documents}) != len(documents):
        raise SourceAdmissionError("admitted record identifiers are not unique")
    validation = validate_cross_source_contract(repo_root, documents)
    hashes_after = {
        str(row["path"]): file_sha256(repo_root / str(row["path"])) for row in rows
    }
    if hashes_before != hashes_after:
        raise SourceAdmissionError("source bytes changed during bundle admission")

    manifest: dict[str, Any] = {
        "schema": "grcv4_explorer_ET_C1_source_bundle_v1",
        "adapter_contract_version": "grcv4_explorer_source_adapters_v1",
        "ET_C0_record_digest": et_c0["record_digest"],
        "ET_C0_source_bundle_candidate_digest": et_c0["source_contract"][
            "source_bundle_candidate_digest"
        ],
        "source_observation_digest": observation["observation_digest"],
        "source_observation_state": observation["state"],
        "record_count": len(documents),
        "records": [document.manifest_row() for document in documents],
        "reference_validation": validation,
        "source_hashes_unchanged_during_admission": True,
        "source_bundle_digest": None,
    }
    manifest["source_bundle_digest"] = digest(
        {key: value for key, value in manifest.items() if key != "source_bundle_digest"}
    )
    return manifest, observation

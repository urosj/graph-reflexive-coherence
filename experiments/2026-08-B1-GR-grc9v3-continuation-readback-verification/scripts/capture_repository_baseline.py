"""Capture the clean GRV0 repository, theory, test, and numerical baseline."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import locale
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
from typing import Any

import numpy as np

from artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
    artifact_envelope,
    file_manifest,
    git,
    repo_relative,
    sha256_file,
    tracked_files,
    write_json,
)
from tangent_basis import basis_checks, zero_sum_basis


THEORY_REPO = REPO_ROOT.parent / "geometric-reflexive-coherence"
SPEC_RELATIVE = "experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/implementation/GRC9V3ContinuationReadBackVerificationSpecification.md"
EXPECTED_SPEC_SHA256 = "7ad99fb4acc6a7691d184a514f4836ffa3927600fc7cf504eb059134f3948e44"
COMMAND = ".venv/bin/python experiments/2026-08-B1-GR-grc9v3-continuation-readback-verification/scripts/capture_repository_baseline.py"


def envelope(payload: Any, schema: str, *, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return artifact_envelope(payload, schema_version=schema, generating_command=COMMAND, metadata=metadata)


def theory_blob(path: str) -> str:
    return git("ls-files", "-s", "--", path, cwd=THEORY_REPO).split()[1]


def dependency_versions() -> dict[str, str]:
    versions = {}
    for distribution in ("numpy", "networkx", "matplotlib", "PyYAML", "pyvis", "pytest"):
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            versions[distribution] = "not_installed"
    return versions


def blas_provider() -> str:
    config = getattr(np.__config__, "CONFIG", {})
    dependencies = config.get("Build Dependencies", {}) if isinstance(config, dict) else {}
    blas = dependencies.get("blas", {}) if isinstance(dependencies, dict) else {}
    return str(blas.get("name", "unknown")) if isinstance(blas, dict) else "unknown"


def run_existing_tests(log_path: Path) -> dict[str, Any]:
    command = [str(REPO_ROOT / ".venv/bin/python"), "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]
    environment = dict(os.environ)
    environment["PYTHONPATH"] = "src"
    started = time.monotonic()
    result = subprocess.run(command, cwd=REPO_ROOT, env=environment, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    duration = time.monotonic() - started
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.stdout, encoding="utf-8")
    match = re.search(r"Ran (\d+) tests? in", result.stdout)
    skipped = re.search(r"skipped=(\d+)", result.stdout)
    counts = {"run": int(match.group(1)) if match else None, "passed": int(match.group(1)) if match and result.returncode == 0 else None, "failed_or_error": 0 if result.returncode == 0 else None, "skipped": int(skipped.group(1)) if skipped else 0}
    return {"command": "PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -p test_*.py", "duration_seconds": duration, "return_code": result.returncode, "result": "passed" if result.returncode == 0 else "failed", "counts": counts, "log_path": repo_relative(log_path)}


def protected_manifest() -> dict[str, Any]:
    paths = tracked_files(["src/pygrc", "tests", "specs/grc-9-spec.md", "specs/grc-9-v3-spec.md"])
    payload = file_manifest(paths)
    payload.update({"manifest_id": "protected_path_manifest_v0", "scope": "all_tracked_PyGRC_source_existing_tests_and_GRC9_specs", "substrate_base_revision": git("merge-base", "main", "HEAD")})
    return envelope(payload, "b1_protected_path_manifest_v0")


def experiment_manifest() -> dict[str, Any]:
    experiment_relative = repo_relative(EXPERIMENT_ROOT)
    paths = tracked_files([experiment_relative])
    excluded_prefixes = (f"{experiment_relative}/outputs/", f"{experiment_relative}/reports/")
    explicit_exclusion = f"{experiment_relative}/outputs/experiment_path_manifest.json"
    included = [path for path in paths if not path.startswith(excluded_prefixes) and path != explicit_exclusion]
    payload = file_manifest(included)
    payload.update({"manifest_id": "experiment_path_manifest", "scope": "all_committed_experiment_files_except_outputs_reports_and_self", "excluded": ["outputs/", "reports/", "outputs/experiment_path_manifest.json"]})
    return envelope(payload, "b1_experiment_path_manifest_v1")


def theory_manifest() -> dict[str, Any]:
    revision = git("rev-parse", "HEAD", cwd=THEORY_REPO)
    sources = []
    for path, role in (("core/2026-08-TheContinuationSpectrum.md", "controlling_continuation_theory"), ("core/2026-08-ReadBack.md", "controlling_readback_theory")):
        sources.append({"path": path, "source_role": role, "git_blob": theory_blob(path), "sha256": sha256_file(THEORY_REPO / path)})
    return envelope({"repository": "github.com/urosj/geometric-reflexive-coherence", "revision": revision, "dirty": bool(git("status", "--porcelain", cwd=THEORY_REPO)), "sources": sources}, "b1_theory_source_manifest_v1")


def fixed_topology_envelope() -> dict[str, Any]:
    mappings = {
        "model_family": {"value": "GRC9V3", "runtime_surface": "src/pygrc/models/grc_9_v3.py::GRC9V3"},
        "frame_mode": {"value": "fixed_port_chart", "runtime_surface": "GRCParams.constitutive_semantic_modes.frame_mode"},
        "boundary_mode": {"value": "prune", "runtime_surface": "GRCParams.constitutive_semantic_modes.boundary_mode"},
        "boundary_action_required": {"value": "prune_noop", "runtime_surface": "GRC9V3.step/apply_boundary_behavior plus per-row no-topology-change assertion"},
        "curvature_backend": {"value": "none", "runtime_surface": "GRCParams.constitutive_semantic_modes.curvature_backend"},
        "spark_lane": {"value": "current_hybrid_signed_hessian", "runtime_surface": "GRCParams.constitutive_semantic_modes.spark_lane"},
        "choice_backend": {"value": "disabled", "runtime_surface": "GRCParams.constitutive_semantic_modes.choice_backend"},
        "quadrature_mode": {"value": "unit_measure", "runtime_surface": "GRCParams.constitutive_semantic_modes.quadrature_mode"},
        "lambda_birth": {"value": 0.0, "runtime_surface": "GRCParams.evolution.lambda_birth"},
        "rng_seed": {"value": 31000, "runtime_surface": "GRCParams.evolution.rng_seed"},
    }
    return envelope({"fixed_topology": True, "mappings": mappings, "required_runtime_assertions": ["strictly_positive_nodes", "no_spark_candidates", "no_expansion_events", "no_growth_events", "no_choice_or_collapse_events", "no_topology_change", "budget_correction_is_noop_for_tangent_perturbations"], "all_specification_names_mapped": True, "ambient_coordinate_identification": "canonical_coordinate_identity_with_fixed_dimension_node_edge_row_port_order_and_orientation", "branch_dependent_metric_transport": "explicit_fixed_reference_isometry_congruence_or_normalization_required_when_metric_varies"}, "b1_fixed_topology_envelope_v1")


def tangent_registry() -> dict[str, Any]:
    records = []
    for size in (2, 3):
        basis = zero_sum_basis(size)
        records.append({"topology_order_family": f"{size}_node_canonical_order", "node_order": list(range(size)), "basis": basis.tolist(), **basis_checks(basis)})
    return envelope({"records": records, "ambient_identification": "canonical_fixed_topology_coordinate_identity", "metric_transport_rule": "declare_fixed_reference_representation_when_inner_product_varies"}, "b1_tangent_basis_registry_v1")


def numerical_environment() -> dict[str, Any]:
    payload = {"python_executable": ".venv/bin/python", "python_version": platform.python_version(), "implementation": platform.python_implementation(), "platform_system": platform.system(), "platform_release": platform.release(), "machine": platform.machine(), "dependency_versions": dependency_versions(), "blas_lapack_provider": blas_provider(), "thread_controls": {key: os.environ.get(key, "unset") for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")}, "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "unset"), "locale": locale.setlocale(locale.LC_ALL, None), "float_info": {"epsilon": sys.float_info.epsilon, "mantissa_digits": sys.float_info.mant_dig, "max": sys.float_info.max, "min": sys.float_info.min}, "numerical_dependency_policy": "repository_dependencies_only_no_experiment_addition"}
    return envelope(payload, "b1_numerical_environment_v1")


def capture(output_root: Path, *, clean_input_already_verified: bool = False) -> dict[str, Any]:
    if not clean_input_already_verified and git("status", "--porcelain"):
        raise RuntimeError("GRV0 requires a clean committed P0 input revision")
    specification = REPO_ROOT / SPEC_RELATIVE
    if sha256_file(specification) != EXPECTED_SPEC_SHA256:
        raise RuntimeError("controlling specification digest does not match P0 preregistration")
    execution_revision = git("rev-parse", "HEAD")
    substrate_revision = git("merge-base", "main", "HEAD")
    output_root.mkdir(parents=True, exist_ok=True)
    protected = protected_manifest()
    experiment = experiment_manifest()
    theory = theory_manifest()
    numerical = numerical_environment()
    fixed = fixed_topology_envelope()
    tangents = tangent_registry()
    named = {"protected_path_manifest_v0.json": protected, "experiment_path_manifest.json": experiment, "theory_source_manifest.json": theory, "numerical_environment.json": numerical, "fixed_topology_envelope.json": fixed, "tangent_basis_registry.json": tangents}
    for name, record in named.items():
        write_json(output_root / name, record)
    test = run_existing_tests(output_root / "logs/grv0_existing_tests.log")
    dependency_hashes = {name: sha256_file(REPO_ROOT / name) for name in ("pyproject.toml", "uv.lock", "requirements.txt", "requirements-dev.txt")}
    theory_identity_path = output_root / "theory_contract_identity.json"
    if not theory_identity_path.exists():
        from serialize_theory_contract import serialize

        serialize(output_root)
    theory_identity = json.loads(theory_identity_path.read_text(encoding="utf-8"))
    baseline_payload = {"repository": "github.com/urosj/graph-reflexive-coherence", "substrate_base_revision": substrate_revision, "experiment_execution_revision": execution_revision, "branch_name": git("branch", "--show-current"), "dirty": False, "theory_repository": "github.com/urosj/geometric-reflexive-coherence", "theory_revision": theory["payload"]["revision"], "protected_path_manifest_v0_path": "outputs/protected_path_manifest_v0.json", "protected_path_manifest_v1_expected_path": "outputs/protected_path_manifest_v1.json", "protected_tree_sha256": protected["payload"]["tree_sha256"], "experiment_tree_sha256": experiment["payload"]["tree_sha256"], "experiment_path_manifest_path": "outputs/experiment_path_manifest.json", "theory_source_manifest_path": "outputs/theory_source_manifest.json", "specification_sha256": EXPECTED_SPEC_SHA256, "theory_contract_sha256": theory_identity["payload"]["part_i_and_appendix_a_sha256"], "assumption_registry_sha256": json.loads((output_root / "theory_assumption_registry.json").read_text(encoding="utf-8"))["payload_sha256"], "python_version": platform.python_version(), "dependency_hashes": dependency_hashes, "test_command": test["command"], "test_result": test["result"], "test_duration_seconds": test["duration_seconds"], "test_counts": test["counts"], "test_log_path": test["log_path"], "runtime_change_authorized": False, "src_change_authorized": False, "existing_test_change_authorized": False, "positive_evidence_opened": False, "positive_continuation_evidence_opened": False, "positive_retention_evidence_opened": False, "positive_readback_evidence_opened": False, "positive_writeback_evidence_opened": False}
    baseline = envelope(baseline_payload, "b1_grc9v3_verification_v3_4_1", metadata={"created_at_utc": datetime.now(timezone.utc).isoformat()})
    write_json(output_root / "baseline_manifest.json", baseline)
    if test["result"] != "passed":
        raise RuntimeError("complete existing test suite failed; see GRV0 log")
    return {"execution_revision": execution_revision, "substrate_revision": substrate_revision, "baseline": baseline, "named_artifacts": named, "test": test}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=EXPERIMENT_ROOT / "outputs")
    args = parser.parse_args()
    capture(args.output_root)


if __name__ == "__main__":
    main()

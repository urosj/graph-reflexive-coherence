#!/usr/bin/env python3
"""Audit the ET-C0 source and layout contract candidate."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, cast


SCRIPT = Path(__file__).resolve()
TOOL_ROOT = SCRIPT.parents[1]
SIDE_TOOL_ROOT = SCRIPT.parents[2]


def repository_root() -> Path:
    for candidate in SIDE_TOOL_ROOT.parents:
        if (candidate / "pyproject.toml").is_file() and (
            candidate / "implementation/investigations/grc9v4-constitutive-design"
        ).is_dir():
            return candidate
    raise RuntimeError("cannot discover repository root")


REPO_ROOT = repository_root()
RECORD_PATH = SIDE_TOOL_ROOT / "records/ETC0SourceAndLayoutContract.json"
REPORT_PATH = SIDE_TOOL_ROOT / "records/ETC0SourceAndLayoutContract.md"
SCENARIOS_PATH = SIDE_TOOL_ROOT / "GRCV4ExploratorySideToolUserScenarios.md"


def require_repository_venv() -> None:
    if Path(sys.prefix).resolve() != (REPO_ROOT / ".venv").resolve():
        raise RuntimeError("run this command with the repository .venv Python")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independently_derive_populations() -> dict[str, int]:
    decisions = (
        REPO_ROOT / "implementation/investigations/grc9v4-constitutive-design/decisions"
    )

    def load(name: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            json.loads((decisions / name).read_text(encoding="utf-8")),
        )

    topology = load("D10NormativeClaimTopology.json")
    debt = load("D10DebtClaimTransformationLedger.json")
    provenance = load("D10_2FullSubstrateProvenanceAndPromotionAudit.json")
    d9_debt = load("D9ResidualDebtLedger.json")
    return {
        "current_claims": len(topology["claims"]),
        "historical_claims": len(topology["historical_claim_nodes"]),
        "transformed_debts": len(debt["debt_transformations"]),
        "verification_obligations": len(debt["verification_obligations"]),
        "D9_predecessor_obligation_occurrences": len(
            d9_debt["post_spec_verification_obligations"]
        ),
        "parent_objects": len(provenance["normatively_load_bearing_objects"]),
        "equation_contract_rows": len(
            provenance["normative_equation_contract_registry"]
        ),
    }


def main() -> int:
    require_repository_venv()
    record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))
    report = REPORT_PATH.read_text(encoding="utf-8")
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append((name, bool(condition), detail))

    expected_record_digest = digest(
        {key: value for key, value in record.items() if key != "record_digest"}
    )
    check("record_digest", record["record_digest"] == expected_record_digest)
    check("status_accepted", record["status"] == "accepted")
    check(
        "gate_candidate_exact",
        record["gate_candidate"] == "ET-C0_source_and_layout_contract_frozen",
    )
    check("iteration_1_authorized", record["authority"]["iteration_1_authorized"])
    check(
        "python_execution_repository_venv_only",
        record["setup_contract"]["tool_python_execution"] == "repository_venv_only",
    )
    check(
        "global_node_npm_forbidden",
        not record["setup_contract"]["global_node_or_npm_execution_allowed"],
    )
    check("source_count_33", record["source_contract"]["record_count"] == 33)
    source_rows = record["source_contract"]["records"]
    check("source_rows_33", len(source_rows) == 33)
    check("source_ids_unique", len({row["source_id"] for row in source_rows}) == 33)
    for row in source_rows:
        path = REPO_ROOT / row["path"]
        check(f"source_exists:{row['source_id']}", path.is_file())
        check(
            f"source_path_relative:{row['source_id']}",
            not Path(row["path"]).is_absolute(),
        )
        data = json.loads(path.read_text(encoding="utf-8"))
        check(
            f"source_status:{row['source_id']}",
            data[row["status_field"]] == row["expected_status"],
        )
        field = row["canonical_digest_field"]
        recomputed = digest({key: value for key, value in data.items() if key != field})
        check(
            f"source_digest:{row['source_id']}",
            data[field] == row["canonical_digest"] == recomputed,
        )
        check(f"source_SHA:{row['source_id']}", file_sha256(path) == row["file_sha256"])
    source_identity = {
        "schema": record["source_contract"]["source_bundle_identity_payload_schema"],
        "records": source_rows,
    }
    check(
        "source_bundle_candidate_digest",
        digest(source_identity)
        == record["source_contract"]["source_bundle_candidate_digest"],
    )
    setup = record["setup_contract"]["setup_identity"]
    environment_path = SIDE_TOOL_ROOT / "records/ETC9EnvironmentConformance.json"
    environment = (
        json.loads(environment_path.read_text(encoding="utf-8"))
        if environment_path.is_file()
        else None
    )
    environment_rows = {
        row["path"]: row
        for row in environment.get("current_dependency_rows", [])
    } if isinstance(environment, dict) else {}
    if environment is not None:
        check(
            "ET_C9_environment_digest",
            environment["environment_digest"]
            == digest(
                {
                    key: value
                    for key, value in environment.items()
                    if key != "environment_digest"
                }
            ),
        )
    for row in setup["dependency_files"]:
        current_sha = file_sha256(REPO_ROOT / row["path"])
        successor = environment_rows.get(row["path"])
        successor_accounts_for_change = (
            successor is not None
            and successor["ET_C0_file_sha256"] == row["file_sha256"]
            and successor["current_file_sha256"] == current_sha
            and successor["classification"]
            == "ET_C6_admitted_toolchain_successor"
            and environment["ET_C0_record_digest"] == record["record_digest"]
            and environment["scientific_source_identity_changed"] is False
        )
        check(
            f"dependency_SHA:{row['path']}",
            current_sha == row["file_sha256"] or successor_accounts_for_change,
        )
    check(
        "setup_identity_digest",
        digest(setup) == record["setup_contract"]["setup_identity_digest"],
    )
    population = record["accepted_population_contract"]
    independently_derived = independently_derive_populations()
    expected_population = {
        "current_claims": 39,
        "historical_claims": 29,
        "transformed_debts": 29,
        "verification_obligations": 11,
        "D9_predecessor_obligation_occurrences": 4,
        "parent_objects": 67,
        "equation_contract_rows": 152,
    }
    check(
        "population_derived_from_sources",
        population["source_derived"] == independently_derived,
    )
    check(
        "source_derived_population_matches_admission",
        independently_derived == expected_population,
    )
    check(
        "recorded_expected_population_exact",
        population["expected_admission"] == expected_population,
    )
    check("population_derivation_gate_passed", population["derived_equals_expected"])
    scenario_ids = re.findall(
        r"^### ([FNCDE]\d+)\.", SCENARIOS_PATH.read_text(), re.MULTILINE
    )
    owned = [
        item
        for values in record["scenario_contract"]["ownership"].values()
        for item in values
    ]
    check("scenario_headings_35", len(scenario_ids) == 35, str(len(scenario_ids)))
    check("scenario_ids_unique", len(set(scenario_ids)) == 35)
    check(
        "scenario_ownership_exact", set(owned) == set(scenario_ids) and len(owned) == 35
    )
    check(
        "output_classes_exact",
        record["output_classes"]
        == [
            "forensic_evidence_trace",
            "speculative_structural_counterfactual",
        ],
    )
    check("no_absolute_path_in_record", b"/home/" not in RECORD_PATH.read_bytes())
    check("no_absolute_path_in_report", b"/home/" not in REPORT_PATH.read_bytes())
    check("report_digest_bound", record["record_digest"] in report)
    for audit in record["accepted_audit_contract"]:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / audit["path"])],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        check(
            f"accepted_audit:{audit['path']}",
            completed.returncode == 0,
            completed.stdout + completed.stderr,
        )
    ignore_paths = (
        ".venv/bin/python",
        str((TOOL_ROOT / ".tooling/node/probe").relative_to(REPO_ROOT)),
        str((TOOL_ROOT / "web/node_modules/probe").relative_to(REPO_ROOT)),
        str((TOOL_ROOT / ".cache/probe").relative_to(REPO_ROOT)),
        str((TOOL_ROOT / "generated/probe").relative_to(REPO_ROOT)),
    )
    for path in ignore_paths:
        ignore_result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--quiet", path],
            cwd=REPO_ROOT,
            check=False,
        )
        check(f"ignored:{path}", ignore_result.returncode == 0)
    status = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    changed_paths = [line[3:] for line in status if len(line) >= 4]
    allowed_prefix = (
        "implementation/investigations/grc9v4-constitutive-design/tools/"
        "exploratory-side-tool/"
    )
    check(
        "write_envelope_tool_only",
        all(path.startswith(allowed_prefix) for path in changed_paths),
        repr(changed_paths),
    )
    doctor = subprocess.run(
        [sys.executable, str(TOOL_ROOT / "scripts/doctor.py")],
        cwd=SIDE_TOOL_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    check("doctor_pass", doctor.returncode == 0, doctor.stdout + doctor.stderr)
    failures = [row for row in checks if not row[1]]
    for name, _, detail in failures:
        print(f"FAIL {name}: {detail}")
    print(
        f"checks={len(checks)} passed={len(checks) - len(failures)} failed={len(failures)}"
    )
    if failures:
        return 1
    print("ET_C0_AUDIT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

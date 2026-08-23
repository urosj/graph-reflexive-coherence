"""Diagnose a failed B2 I8 full-suite receipt without changing repository code."""

from __future__ import annotations

import re
import subprocess

from b2_artifact_io import (
    EXPERIMENT_ROOT,
    REPO_ROOT,
    git,
    read_json,
    repo_relative,
    sha256_file,
    write_json,
)


SOURCE_PATH = EXPERIMENT_ROOT / "outputs/gates/b2_i8_full_suite_verification.json"
OUTPUT_PATH = EXPERIMENT_ROOT / "outputs/gates/b2_i8_full_suite_failure_audit.json"
COMMAND = ".venv/bin/python -m pytest -q --lf"
TELEMETRY_REPLAY_NODEID = (
    "tests/telemetry/test_experiments.py::TelemetryRepresentativeExperimentTest::"
    "test_run_grcv3_representative_experiment_emits_artifacts_and_replay_stable_reports"
)


def main() -> None:
    source = read_json(SOURCE_PATH)
    if source["status"] != "failed" or source["exit_code"] == 0:
        raise ValueError("failure audit requires a failed full-suite receipt")

    result = subprocess.run(
        [".venv/bin/python", "-m", "pytest", "-q", "--lf"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    failed_nodeids = re.findall(r"^FAILED (?P<nodeid>\S+)", result.stdout, re.MULTILINE)
    missing_paths = sorted(
        set(
            re.findall(
                r"(?:missing|No such file or directory): '([^']+)'",
                result.stdout,
            )
        )
    )
    source_paths = sorted({nodeid.split("::", 1)[0] for nodeid in failed_nodeids})
    unchanged = (
        subprocess.run(
            ["git", "diff", "--quiet", "main", "--", "src", "specs", "tests"],
            cwd=REPO_ROOT,
            check=False,
        ).returncode
        == 0
    )
    summary_lines = [
        line.strip() for line in result.stdout.splitlines() if line.strip()
    ]
    summary = summary_lines[-1] if summary_lines else "no_pytest_summary"
    payload = {
        "audit_id": "B2-I8-full-suite-failure-audit",
        "status": "full_suite_blocked_preexisting_repository_debt",
        "input_execution_revision": git("rev-parse", "HEAD"),
        "main_reference_revision": git("rev-parse", "main"),
        "source_full_suite_receipt_path": repo_relative(SOURCE_PATH),
        "source_full_suite_receipt_sha256": sha256_file(SOURCE_PATH),
        "source_full_suite_input_execution_revision": source[
            "input_execution_revision"
        ],
        "diagnostic_command": COMMAND,
        "diagnostic_exit_code": result.returncode,
        "diagnostic_summary_without_duration": re.sub(
            r" in \d+(?:\.\d+)?s", "", summary
        ),
        "failed_test_count": len(failed_nodeids),
        "failed_test_nodeids": failed_nodeids,
        "failed_test_source_paths": source_paths,
        "missing_ignored_evidence_path_count": len(missing_paths),
        "missing_ignored_evidence_paths": missing_paths,
        "telemetry_replay_digest_failure_present": (
            TELEMETRY_REPLAY_NODEID in failed_nodeids
        ),
        "src_specs_tests_equal_main": unchanged,
        "B2_changed_runtime_or_existing_tests": not unchanged,
        "B2_regression_established": False,
        "full_repository_suite_passed": False,
        "B2_C6_ready": False,
        "B2_C6_blocker": "full_existing_repository_test_suite_not_passing",
        "repair_authorized_in_B2": False,
        "scientific_boundary": (
            "failure_localization_does_not_waive_the_full_suite_closeout_gate"
        ),
    }
    write_json(OUTPUT_PATH, payload)
    print(
        f"I8 full-suite failure audit: {len(failed_nodeids)} failures; "
        f"{len(missing_paths)} missing ignored paths; B2-C6 blocked"
    )


if __name__ == "__main__":
    main()

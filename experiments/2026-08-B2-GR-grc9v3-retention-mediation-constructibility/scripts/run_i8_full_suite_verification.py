"""Run and record the repository-wide verification required before B2 closeout."""

from __future__ import annotations

import re
import subprocess

from b2_artifact_io import EXPERIMENT_ROOT, REPO_ROOT, git, write_json


OUTPUT_PATH = EXPERIMENT_ROOT / "outputs/gates/b2_i8_full_suite_verification.json"
COMMAND = ".venv/bin/python -m pytest -q"


def main() -> None:
    result = subprocess.run(
        [".venv/bin/python", "-m", "pytest", "-q"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    summary_lines = [
        line.strip() for line in result.stdout.splitlines() if line.strip()
    ]
    summary = summary_lines[-1] if summary_lines else "no_pytest_summary"
    match = re.search(r"(?P<count>\d+) passed", result.stdout)
    payload = {
        "verification_id": "B2-I8-full-repository-suite",
        "status": "passed" if result.returncode == 0 and match else "failed",
        "input_execution_revision": git("rev-parse", "HEAD"),
        "command": COMMAND,
        "exit_code": result.returncode,
        "passed_test_count": int(match.group("count")) if match else 0,
        "summary_without_duration": re.sub(r" in \d+(?:\.\d+)?s", "", summary),
        "verification_scope": "full_repository_pytest_suite",
        "runtime_change_authorized": False,
        "scientific_evidence_role": "verification_only",
    }
    write_json(OUTPUT_PATH, payload)
    print(payload["summary_without_duration"], flush=True)
    if payload["status"] != "passed":
        raise SystemExit(result.returncode or 1)


if __name__ == "__main__":
    main()

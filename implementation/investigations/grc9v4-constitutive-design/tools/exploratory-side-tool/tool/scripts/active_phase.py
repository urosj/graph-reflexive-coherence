"""Select a verifier, never authorize a phase from its name or a flag."""

from pathlib import Path
import subprocess

OPENING = "implementation/Phase-9-GRCV4-PhaseOpening.json"
OPENING_COMMIT = "7c772d36bd4cf12b4a444b7b954b74612de2926f"
PHASE9_AUDITOR = "implementation/phase-9-grcv4/verification/audit_phase9_implementation.py"
HISTORICAL_AUDITOR = (
    "implementation/investigations/grc9v4-constitutive-design/"
    "scripts/audit_grcv4_post_d10_specifications.py"
)


def phase9_present(root: Path) -> bool:
    # History prevents deleting the current marker to regain the old route.
    # Selection is only a hint: the selected verifier checks every binding.
    return (root / OPENING).exists() or subprocess.run(
        ["git", "merge-base", "--is-ancestor", OPENING_COMMIT, "HEAD"],
        cwd=root,
        capture_output=True,
        check=False,
    ).returncode == 0


def verification_script(root: Path) -> Path:
    return root / (PHASE9_AUDITOR if phase9_present(root) else HISTORICAL_AUDITOR)

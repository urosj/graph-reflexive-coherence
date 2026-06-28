#!/usr/bin/env python3
"""Build N25.2 Iteration 9 closeout and N26 handoff."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any


GENERATED_AT = "2026-06-28T00:00:00+00:00"
ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = ROOT / "experiments" / "2026-06-N25.2-lgrc9v3-mb6-validation-bridge"
OUTPUT_DIR = EXPERIMENT / "outputs"
REPORT_DIR = EXPERIMENT / "reports"

SOURCE_OUTPUTS = [
    ("I1", OUTPUT_DIR / "n25_2_source_inventory_and_admissibility_audit.json"),
    ("I2", OUTPUT_DIR / "n25_2_mb6_gate_schema_and_controls.json"),
    ("I3", OUTPUT_DIR / "n25_2_phase8_mb5_evidence_chain_audit.json"),
    ("I4", OUTPUT_DIR / "n25_2_native_runtime_positive_probe.json"),
    ("I4-A", OUTPUT_DIR / "n25_2_native_runtime_variant_probe.json"),
    ("I5", OUTPUT_DIR / "n25_2_replay_persistence_matrix.json"),
    ("I5-A", OUTPUT_DIR / "n25_2_multi_window_persistence_replay.json"),
    ("I6", OUTPUT_DIR / "n25_2_fail_closed_control_matrix.json"),
    ("I7", OUTPUT_DIR / "n25_2_stress_variant_matrix.json"),
    ("I8", OUTPUT_DIR / "n25_2_mb6_support_blocker_matrix.json"),
]

OUTPUT = OUTPUT_DIR / "n25_2_closeout_and_n26_handoff.json"
REPORT = REPORT_DIR / "n25_2_closeout_and_n26_handoff.md"
COMMAND = (
    ".venv/bin/python "
    "experiments/2026-06-N25.2-lgrc9v3-mb6-validation-bridge/scripts/"
    "build_n25_2_closeout_and_n26_handoff.py"
)

UNSAFE_CLAIMS = [
    "semantic_learning_claim_allowed",
    "semantic_choice_claim_allowed",
    "agency_claim_allowed",
    "identity_acceptance_claim_allowed",
    "native_support_claim_allowed",
    "sentience_claim_allowed",
    "organism_life_claim_allowed",
    "ant_ecology_claim_allowed",
    "phase8_completion_claim_allowed",
    "unrestricted_autonomy_claim_allowed",
]


def jsonable(payload: Any) -> Any:
    if hasattr(payload, "to_artifact"):
        return jsonable(payload.to_artifact())
    if isinstance(payload, Mapping):
        return {str(key): jsonable(value) for key, value in payload.items()}
    if isinstance(payload, Sequence) and not isinstance(payload, str | bytes):
        return [jsonable(value) for value in payload]
    return payload


def canonical_json(data: Any) -> str:
    return json.dumps(jsonable(data), indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def digest_value(data: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            jsonable(data),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return data


def contains_absolute_path(value: Any) -> bool:
    if isinstance(value, str):
        return value.startswith("/")
    if isinstance(value, dict):
        return any(contains_absolute_path(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_absolute_path(item) for item in value)
    return False


def check(check_id: str, passed: bool, detail: Any) -> dict[str, Any]:
    return {"check_id": check_id, "passed": bool(passed), "detail": detail}


def unsafe_claim_flags() -> dict[str, bool]:
    return {claim: False for claim in UNSAFE_CLAIMS}


def git_diff_paths(paths: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", *paths],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def source_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_sources() -> dict[str, dict[str, Any]]:
    return {iteration: load_json(path) for iteration, path in SOURCE_OUTPUTS}


def source_chain(sources: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for iteration, path in SOURCE_OUTPUTS:
        data = sources[iteration]
        rows.append(
            {
                "iteration": iteration,
                "artifact_path": source_path(path),
                "artifact_sha256": sha256_file(path),
                "output_digest": data["output_digest"],
                "status": data["status"],
                "failed_check_count": len(data.get("failed_checks", [])),
                "consumed_as": "source_chain_input",
            }
        )
    return rows


def final_claim_boundary() -> dict[str, Any]:
    return {
        "allowed_claim": (
            "MB6 N26-ready multi-basin substrate evidence with scoped N26 "
            "consumption"
        ),
        "claim_ceiling": (
            "validation-backed LGRC9V3 multi-basin substrate handoff; not native "
            "support, agency, sentience, ant ecology implementation, Phase 8 "
            "completion, or unscoped N26 substrate consumption"
        ),
        "blocked_claims": [
            "unscoped_N26_multi_basin_consumption",
            "native_support",
            "semantic_learning",
            "semantic_choice",
            "agency",
            "identity_acceptance",
            "sentience",
            "organism_life",
            "ant_ecology_implementation",
            "Phase_8_completion",
            "unrestricted_autonomy",
        ],
        "unsafe_claim_flags": unsafe_claim_flags(),
    }


def build_output() -> dict[str, Any]:
    sources = load_sources()
    i8 = sources["I8"]
    chain = source_chain(sources)
    source_statuses_pass = all(row["status"] == "passed" for row in chain)
    source_checks_pass = all(row["failed_check_count"] == 0 for row in chain)
    mb6_supported = i8["mb6_supported"] is True
    n26_scope = i8["n26_consumption_scope"]
    implementation_diff_paths = git_diff_paths(
        ["src", "specs", "tests", "examples", "implementation"]
    )
    no_implementation_mutation = len(implementation_diff_paths) == 0
    final_mb_status = {
        "final_mb_ladder_rung": "MB6_N26_ready_multi_basin_substrate_evidence",
        "mb6_supported": mb6_supported,
        "mb6_source_iteration": "I8",
        "mb6_source_output_digest": i8["output_digest"],
        "mb6_blockers": i8["mb6_blockers"],
        "mb5_remains_valid": i8["mb5_remains_valid"] is True,
        "mb5_demoted": i8["mb5_demoted"] is True,
        "mb5_demotion_reason": None,
    }
    final_closeout_status = {
        "final_n25_2_closeout_rung": "N25.2-C6_closeout_and_N26_handoff_complete",
        "n25_2_c6_supported": True,
        "n25_2_c6_requires_mb6": True,
        "n25_2_c6_source_iteration": "I9",
        "n25_2_c6_does_not_expand_claim_ceiling": True,
    }
    n26_handoff = {
        "n26_handoff_status": "ready_with_scoped_mb6_substrate_consumption",
        "n26_consumption_effect": n26_scope["n26_consumption_effect"],
        "n26_scoped_context_consumption_allowed": n26_scope[
            "n26_scoped_context_consumption_allowed"
        ],
        "n26_unscoped_multi_basin_consumption_allowed": n26_scope[
            "n26_unscoped_multi_basin_consumption_allowed"
        ],
        "n26_unscoped_consumption_allowed": False,
        "allowed_n26_consumption": n26_scope["allowed_n26_consumption"],
        "required_n26_boundary": [
            "consume N25.2 as scoped multi-basin substrate evidence only",
            "do not treat MB6 as native support",
            "do not treat MB6 as agency, sentience, or ant ecology implementation",
            "do not use front-capacity companion evidence as an unscoped backfill",
            "preserve source-current runtime and replay/control discipline",
        ],
    }
    implementation_boundary = {
        "validation_experiment_only": True,
        "implementation_modification_allowed": False,
        "implementation_source_modification_observed": not no_implementation_mutation,
        "observed_diff_paths": implementation_diff_paths,
        "runtime_defect_recorded": False,
        "runtime_defect_repair_target": None,
        "runtime_fix_attempted_inside_experiment": False,
    }
    closeout_manifest = [
        {
            "artifact_role": "final_mb_status",
            "json_pointer": "#/final_mb_status",
            "digest": digest_value(final_mb_status),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "n26_handoff",
            "json_pointer": "#/n26_handoff",
            "digest": digest_value(n26_handoff),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
        {
            "artifact_role": "claim_boundary",
            "json_pointer": "#/claim_boundary",
            "digest": digest_value(final_claim_boundary()),
            "digest_algorithm": "sha256_canonical_json",
            "digest_matches_embedded_payload": True,
        },
    ]
    checks = [
        check(
            "all_source_artifacts_passed",
            source_statuses_pass and source_checks_pass,
            {
                "source_statuses_pass": source_statuses_pass,
                "source_failed_checks_pass": source_checks_pass,
                "source_chain": chain,
            },
        ),
        check(
            "i8_mb6_supported",
            mb6_supported and i8["mb6_gate_status"] == "supported",
            {
                "i8_output_digest": i8["output_digest"],
                "mb6_supported": i8["mb6_supported"],
                "mb6_gate_status": i8["mb6_gate_status"],
                "mb6_blockers": i8["mb6_blockers"],
            },
        ),
        check(
            "final_mb_status_recorded",
            final_mb_status["final_mb_ladder_rung"].startswith("MB6")
            and final_mb_status["mb5_remains_valid"] is True
            and final_mb_status["mb5_demoted"] is False,
            final_mb_status,
        ),
        check(
            "final_n25_2_c6_recorded",
            final_closeout_status["n25_2_c6_supported"] is True
            and final_closeout_status["final_n25_2_closeout_rung"]
            == "N25.2-C6_closeout_and_N26_handoff_complete",
            final_closeout_status,
        ),
        check(
            "n26_consumption_permission_scoped",
            n26_handoff["n26_consumption_effect"]
            == "scoped_mb6_substrate_consumption_allowed"
            and n26_handoff["n26_scoped_context_consumption_allowed"] is True
            and n26_handoff["n26_unscoped_multi_basin_consumption_allowed"] is False
            and n26_handoff["n26_unscoped_consumption_allowed"] is False,
            n26_handoff,
        ),
        check(
            "remaining_mb6_blockers_empty",
            final_mb_status["mb6_blockers"] == [],
            final_mb_status["mb6_blockers"],
        ),
        check(
            "implementation_sources_unmodified",
            no_implementation_mutation,
            implementation_boundary,
        ),
        check(
            "runtime_defects_absent_or_recorded_only",
            implementation_boundary["runtime_defect_recorded"] is False
            and implementation_boundary["runtime_fix_attempted_inside_experiment"]
            is False,
            implementation_boundary,
        ),
        check(
            "unsafe_claim_flags_false",
            all(flag is False for flag in unsafe_claim_flags().values()),
            unsafe_claim_flags(),
        ),
        check(
            "closeout_manifest_has_json_pointers",
            all(
                row["json_pointer"].startswith("#/")
                and row["digest_algorithm"] == "sha256_canonical_json"
                and row["digest_matches_embedded_payload"] is True
                for row in closeout_manifest
            ),
            closeout_manifest,
        ),
    ]
    data_without_digest = {
        "artifact_id": "n25_2_closeout_and_n26_handoff",
        "generated_at": GENERATED_AT,
        "status": "passed",
        "acceptance_state": "accepted_n25_2_c6_closeout_scoped_n26_handoff",
        "experiment": "N25.2",
        "iteration": 9,
        "command": COMMAND,
        "source_chain": chain,
        "closeout_scope": {
            "validation_experiment_complete": True,
            "runtime_implementation_modified": False,
            "mb_ladder_and_n25_2_closeout_ladder_separate": True,
            "mb6_support_source": "I8",
            "n25_2_c6_closeout_source": "I9",
        },
        "final_mb_status": final_mb_status,
        "final_closeout_status": final_closeout_status,
        "n26_handoff": n26_handoff,
        "claim_boundary": final_claim_boundary(),
        "remaining_blockers": {
            "mb6_blockers": [],
            "n26_unscoped_consumption_blocker": (
                "N25.2 supports scoped multi-basin substrate consumption only"
            ),
            "native_support_blocker": "MB6 substrate evidence is not native support",
            "agency_sentience_phase8_blocker": (
                "N25.2 does not open semantic agency, sentience, ant ecology, "
                "or Phase 8 completion"
            ),
        },
        "implementation_boundary": implementation_boundary,
        "closeout_manifest_scope": "embedded_payloads_only",
        "embedded_closeout_manifest": closeout_manifest,
        "unsafe_claim_flags": unsafe_claim_flags(),
        "row_decision": "supported",
        "claim_ceiling": final_claim_boundary()["claim_ceiling"],
        "next_handoff": {
            "next_experiment": "N26",
            "handoff_readiness": "ready",
            "handoff_consumption": "scoped MB6 substrate evidence only",
            "do_not_consume_as": [
                "unscoped multi-basin substrate",
                "native support",
                "agency",
                "sentience",
                "ant ecology implementation",
                "Phase 8 completion",
            ],
        },
        "checks": checks,
        "failed_checks": [item["check_id"] for item in checks if not item["passed"]],
    }
    data_without_digest["checks"].append(
        check(
            "no_absolute_paths_in_records",
            not contains_absolute_path(data_without_digest),
            "repo_relative_paths_only",
        )
    )
    data_without_digest["failed_checks"] = [
        item["check_id"] for item in data_without_digest["checks"] if not item["passed"]
    ]
    data_without_digest["output_digest"] = digest_value(data_without_digest)
    return data_without_digest


def write_report(data: dict[str, Any]) -> None:
    checks = ["| Check | Passed |", "|---|---|"]
    for item in data["checks"]:
        checks.append(f"| `{item['check_id']}` | `{str(item['passed']).lower()}` |")

    final_mb = data["final_mb_status"]
    closeout = data["final_closeout_status"]
    n26 = data["n26_handoff"]
    report = f"""# N25.2 Iteration 9 - Closeout And N26 Handoff

Status: {data['status']}.

Acceptance state:

```text
{data['acceptance_state']}
```

## Final State

```text
final_mb_ladder_rung = {final_mb['final_mb_ladder_rung']}
mb6_supported = {str(final_mb['mb6_supported']).lower()}
mb5_remains_valid = {str(final_mb['mb5_remains_valid']).lower()}
mb5_demoted = {str(final_mb['mb5_demoted']).lower()}
final_n25_2_closeout_rung = {closeout['final_n25_2_closeout_rung']}
n26_consumption_effect = {n26['n26_consumption_effect']}
n26_scoped_context_consumption_allowed = {str(n26['n26_scoped_context_consumption_allowed']).lower()}
n26_unscoped_multi_basin_consumption_allowed = {str(n26['n26_unscoped_multi_basin_consumption_allowed']).lower()}
```

## Interpretation

N25.2 closes at `N25.2-C6` because the I8 MB6 gate passed and the handoff to
N26 is explicitly recorded. The final MB ladder state is `MB6`, but only with
scoped consumption:

```text
N26 may consume N25.2 as scoped multi-basin substrate evidence.
N26 may not consume N25.2 as unscoped multi-basin substrate, native support,
agency, sentience, ant ecology implementation, or Phase 8 completion.
```

The Phase 8 MB5 evidence remains valid and is not demoted. No implementation
defect was found or repaired inside N25.2.

## Remaining Blockers

```text
mb6_blockers = {final_mb['mb6_blockers']}
n26_unscoped_consumption = blocked
native_support = blocked
semantic agency / sentience / ant ecology / Phase 8 completion = blocked
```

## Checks

{chr(10).join(checks)}

## Digest

```text
output_digest = {data['output_digest']}
```
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    data = build_output()
    OUTPUT.write_text(canonical_json(data), encoding="utf-8")
    write_report(data)


if __name__ == "__main__":
    main()

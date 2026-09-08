"""Recheck the frozen P9-4.8 HOLD review, not a runtime conformance runner.

Run from any working directory using the repository .venv. A changed scientific
source requires a successor review; this checker never refreshes its own inputs.
"""

from __future__ import annotations

import ast
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
PHASE = "implementation/phase-9-grcv4/"
RECORD = PHASE + "tranche-4/P9-4.8-GateReview.json"
RUN = PHASE + "evidence/P9-4.7b/authoritative-vector/run.json"


def read(name):
    return json.loads((ROOT / name).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def catalog_ids():
    catalog = read("specs/grc-v4-conformance-fixtures.json")
    return {
        row["id"]
        for group in (
            "common_cases",
            "candidate_c_cases",
            "realization_cases",
            "lifecycle_cases",
        )
        for row in catalog[group]
        if group != "realization_cases" or row["id"] == "OS-ONE-PASS"
    }


def check_decision(record, observations):
    """Consistency with this human HOLD decision; cannot issue a future PASS."""
    ids = [row["fixture_id"] for row in record["catalog_rows"]]
    require(
        len(ids) == len(set(ids)) and set(ids) == catalog_ids(),
        "catalog coverage drift",
    )
    require(record["verdict"] == "HOLD", "unsupported gate promotion")
    require(
        record["accepted_generic_runtime_support"] == []
        and record["admitted_specialization_support_sets"] == []
        and record["nominated_complete_profiles"] == [],
        "invented profile support",
    )
    require(
        {b["id"] for b in record["blockers"]}
        == {"G2-COS-INTERFACE", "G2-COS-PARENTS", "G2-COS-FIXTURES"},
        "unclosed blocker removed",
    )
    require(record["observations"] == observations, "mechanical observation drift")


def observations():
    # Imports inspect actual public objects; fixture construction declares exact
    # profiles but does not execute or claim another migration/step.
    sys.path.insert(0, str(ROOT))
    from pygrc.core.interfaces import GRCModel
    from pygrc.models import grc_v4
    from pygrc.models.grc_v4_lifecycle import CandidateCOSOperation
    from pygrc.models.grc_v4_profile import list_supported_profiles
    from tests.models.test_grc_v4_lifecycle import dyadic_fixture, os_fixture

    for module_name in (
        grc_v4.__name__,
        CandidateCOSOperation.__module__,
        list_supported_profiles.__module__,
    ):
        module = sys.modules[module_name]
        require(
            Path(module.__file__).resolve()
            == ROOT / "src" / (module_name.replace(".", "/") + ".py"),
            "foreign installed runtime module",
        )
    required = set(GRCModel.__abstractmethods__) | {
        "run",
        "run_v4",
        "active_profile_id",
        "active_model_identity",
        "get_supported_profile",
        "list_supported_model_identities",
    }
    source = dyadic_fixture().geometry.reference
    target = os_fixture(
        candidate={"chi_C": 0, "zeta_C": 0}, geometry={"kappa_H": 0}
    ).geometry.reference
    require(source.graph == target.graph, "positive migration graph drift")
    require(
        source.profile.complete_profile_id != target.profile.complete_profile_id,
        "positive migration endpoints collapsed",
    )
    vector = read("specs/grc-v4-conformance-vectors.json")[
        "grcv4_mapped_topology_event_vectors"
    ][0]
    return {
        "public_GRCV4_present": hasattr(grc_v4, "GRCV4"),
        "receiver_is_GRCModel": issubclass(CandidateCOSOperation, GRCModel),
        "missing_receiver_methods": sorted(
            n for n in required if not hasattr(CandidateCOSOperation, n)
        ),
        "public_supported_profiles": sorted(list_supported_profiles()),
        "same_graph_migration_profiles": [
            {
                "complete_profile_id": ref.profile.complete_profile_id,
                "params_hash": ref.profile.params_resolved.params_hash,
            }
            for ref in (source, target)
        ],
        "mapped_fixture_id": vector["fixture_id"],
        "mapped_event_id": vector["expected"]["event_id"],
        "mapped_source_profile": vector["runtime_inputs"]["source_state"][
            "active_model_identity"
        ],
        "mapped_target_profile": vector["request"]["target_profile_id"],
    }


def verify_inputs(record):
    commit = record["reviewed_runtime_commit"]
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=ROOT, check=True
    )
    for row in record["source_bindings"]:
        path = Path(row["path"])
        require(not path.is_absolute() and ".." not in path.parts, "nonportable input")
        require(
            sha256((ROOT / path).read_bytes()).hexdigest() == row["sha256"],
            "changed review input: " + row["path"],
        )
    for row in record["catalog_rows"]:
        *module, cls, method = row["test"].split(".")
        tree = ast.parse((ROOT / ("/".join(module) + ".py")).read_text())
        require(
            any(
                c.name == cls
                and any(
                    isinstance(f, ast.FunctionDef) and f.name == method for f in c.body
                )
                for c in tree.body
                if isinstance(c, ast.ClassDef)
            ),
            "missing indexed test: " + row["test"],
        )
    run = read(RUN)
    names = subprocess.check_output(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            *run["source"]["scopes"],
        ],
        cwd=ROOT,
        text=True,
    ).splitlines()
    current = {
        n: sha256((ROOT / n).read_bytes()).hexdigest() for n in sorted(set(names))
    }
    digest = sha256(
        json.dumps(current, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    require(
        len(current) == run["source"]["file_count"]
        and digest == run["source"]["manifest_sha256"],
        "scientific source manifest drift",
    )
    require(run["release_id"] == record["release_id"], "release mismatch")
    require(
        run["authoritative_fixture"]["request_modified"] is False
        and run["authoritative_fixture"]["mandatory_row_waived"] is False
        and run["authoritative_fixture"]["event_id"]
        == record["observations"]["mapped_event_id"],
        "mapped row is not exact execution evidence",
    )
    return len(current)


def pressure(record, actual):
    controls = {
        "missing_catalog_row": lambda r: r["catalog_rows"].pop(),
        "duplicate_catalog_row": lambda r: r["catalog_rows"].append(
            r["catalog_rows"][0]
        ),
        "family_label_as_profile": lambda r: r["nominated_complete_profiles"].append(
            "C_OS"
        ),
        "empty_population_vacuous_pass": lambda r: r.update(verdict="PASS"),
        "unreviewed_support": lambda r: r["accepted_generic_runtime_support"].append(
            actual["mapped_target_profile"]
        ),
        "borrowed_mapped_identity": lambda r: r["observations"].update(
            mapped_event_id="grc-event-sha256:" + "0" * 64
        ),
        "lineage_debt_silently_closed": lambda r: r["blockers"].pop(1),
    }
    for name, mutate in controls.items():
        altered = deepcopy(record)
        mutate(altered)
        try:
            check_decision(altered, actual)
        except ValueError:
            continue
        raise ValueError("review mutation escaped: " + name)
    return list(controls)


def main():
    record = read(RECORD)
    count = verify_inputs(record)
    actual = observations()
    check_decision(record, actual)
    controls = pressure(record, actual)
    print(
        json.dumps(
            {
                "review_check": "passed",
                "gate": "HOLD",
                "catalog_rows": len(catalog_ids()),
                "scientific_source_files": count,
                "mutation_controls_rejected": controls,
                "numerical_tests_rerun": 0,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

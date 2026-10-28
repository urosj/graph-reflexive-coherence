"""Execute public API integration; --check only authenticates retained evidence."""

import argparse
import hashlib
import json
import lzma
from pathlib import Path
import sys
import subprocess
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
BASE = "implementation/phase-9-grcv4/tranche-9/"
FAMILIES = ("C_OS", "C_CI", "A_CI", "A_PC")
CLASSES = dict(
    zip(
        (*FAMILIES, "boundary", "contracts", "architecture"),
        (
            "COSPublic",
            "CCIPublic",
            "ACIPublic",
            "APCPublic",
            "BoundaryPublic",
            "PublicContractTests",
            "ArchitectureTests",
        ),
    )
)
CASES = ("construction", "expansion_replay", "branch_crossings", "profile_migration")
NAMES = (
    "test_profile_migration_and_atomic_negative_paths",
    "test_public_branch_migrations_and_exact_disabled_projection",
    "test_public_construction_step_default_and_discovery",
    "test_public_expansion_reset_rebase_and_replay",
)
BOUNDARY_NAMES = (
    "test_configuration_and_target_registry",
    "test_direct_c_to_a_never_uses_generic_initializer",
    "test_publication_failure_and_typed_boundaries",
    "test_saved_selection_is_checked_before_public_execution",
)

CONTRACT_NAMES = (
    "test_candidate_and_carrier_axes_are_independent",
    "test_contract_wire_and_execution_options_are_closed",
    "test_known_target_declaration_is_not_runtime_support",
    "test_known_unavailable_families_reject_before_execution",
    "test_realization_parameters_do_not_collapse_to_common_solver_knobs",
    "test_ten_complete_typed_configurations_roundtrip",
)
ARCHITECTURE_NAMES = (
    "test_accepted_crossing_checkpoints_replay_unchanged",
    "test_accepted_mixed_checkpoints_replay_unchanged",
    "test_all_ten_dispatch_preserves_closed_scientific_handlers",
    "test_branch_owns_the_only_ledger_and_artifact_bundle",
    "test_execution_selection_is_independent",
    "test_predecessor_event_checkpoint_bytes_match",
    "test_public_replay_counts_and_bounded_cost",
    "test_rejection_and_late_failure_keep_whole_publication",
    "test_transition_preserves_artifact_prefix_and_never_publishes",
)
ARCHITECTURE_CASES = {
    "execution_selection",
    "dispatch",
    "artifact_transfer",
    "rollback",
    "event_predecessor_parity",
    "accepted_replay",
    "replay_assessment",
    "branch_ownership",
    "accepted_crossing_replay",
}

CONTRACT_FAMILIES = tuple(
    c + "_" + r for c in "AC" for r in ("OS", "CI", "PC", "CI_PC", "RG2b")
)


def cases(family):
    return (
        set()
        if family == "boundary"
        else {"families", "execution_scope"}
        if family == "contracts"
        else ARCHITECTURE_CASES
        if family == "architecture"
        else set(CASES)
    )


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(
        body,
        record_digest=sha(
            json.dumps(
                body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode()
        ),
    )


def filename(f):
    if f not in CLASSES:
        raise ValueError("unselected family")
    return BASE + "P9-9.4b-" + f + ".json"


def predecessor(root):
    from p994a_acceptance import decision, PATH

    value = decision(root)
    return dict(
        path=PATH,
        sha256=sha((root / PATH).read_bytes()),
        record_digest=value["record_digest"],
    )


def run(root, family):
    sys.path[:0] = [str(root), str(root / "src")]
    if family == "contracts":
        from tests.models import test_grc_9_v4_contracts as tests
    elif family == "architecture":
        from tests.models import test_grc_9_v4_architecture as tests
    else:
        from tests.models import test_grc_9_v4 as tests
    from examples.grcv4.catalog import Catalog

    tests.EVIDENCE.clear()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        getattr(tests, CLASSES[family])
    )
    roster = [t.id() for t in suite]
    sources = list((root / "src").rglob("*.py"))
    sources += list((root / "src/pygrc/models/grc_v4_assets").glob("*.json"))
    sources += list((root / "tests/models").glob("test_grc*.py"))
    sources += [
        root / "examples/grcv4/catalog.py",
        root / "examples/grcv4/run_selection.py",
        Path(__file__).resolve(),
    ]
    inputs = [root / BASE / ("P9-9.1b-" + f + ".json") for f in FAMILIES]
    inputs += [
        root / "specs/grc-9-v4-spec.md",
        root / "specs/grc-common-interface-v4-ext.md",
        root / BASE / "P9-9.4a-Authority.json",
        root / "examples/grcv4/configurations.json",
    ]
    if family in ("boundary", "contracts"):
        catalog = Catalog(root=root)
        for f in CONTRACT_FAMILIES if family == "contracts" else FAMILIES:
            entry = catalog.entry("native-small-" + f)
            inputs += [
                root / ref["path"] for ref in [entry["data"], *entry["evidence"]]
            ]

    def refs(paths):
        return [
            dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
            for p in sorted(set(paths))
        ]

    prior = predecessor(root)
    before = refs(sources + inputs)
    start = time.monotonic()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.skipped:
        raise RuntimeError("public suite failed")
    if refs(sources + inputs) != before:
        raise ValueError("execution inputs changed during run")
    if set(tests.EVIDENCE) != cases(family):
        raise ValueError("incomplete public evidence")
    imported = {
        Path(m.__file__).resolve()
        for m in list(sys.modules.values())
        if getattr(m, "__file__", None)
    }
    return seal(
        dict(
            schema="p994b-public-api-execution-v1",
            family=family,
            outcome="passed",
            tests=roster,
            tests_run=result.testsRun,
            failures=0,
            errors=0,
            skips=0,
            predecessor=prior,
            elapsed_seconds=time.monotonic() - start,
            source_refs=refs(
                [p for p in sources if p in imported or p.suffix == ".json"]
            ),
            input_refs=refs(inputs),
            execution=dict(
                python=sys.version.split()[0],
                exact_backend="flint",
                numerical_policy="legacy_exact_v1",
                workers_per_record=1,
            ),
            evidence=tests.EVIDENCE,
            user_accepted=False,
            public_api=True,
            full_GRC9V4_conformance=False,
            aggregate_closed=False,
            scope="ten_family_contracts_four_family_native_execution",
        )
    )


def read(root, family):
    p = Path(root) / filename(family)
    q = p.with_suffix(".json.xz")
    if p.exists() and q.exists():
        raise ValueError("ambiguous evidence representation")
    return json.loads(p.read_bytes() if p.exists() else lzma.decompress(q.read_bytes()))


def check(root, family):
    root = Path(root).resolve()
    v = read(root, family)
    names = (
        CONTRACT_NAMES
        if family == "contracts"
        else BOUNDARY_NAMES
        if family == "boundary"
        else ARCHITECTURE_NAMES
        if family == "architecture"
        else NAMES
    )
    module = (
        "tests.models.test_grc_9_v4_contracts"
        if family == "contracts"
        else "tests.models.test_grc_9_v4_architecture"
        if family == "architecture"
        else "tests.models.test_grc_9_v4"
    )
    if (
        v != seal(v)
        or v["schema"] != "p994b-public-api-execution-v1"
        or v["family"] != family
        or v["outcome"] != "passed"
        or v["tests_run"] != len(names)
        or v["tests"] != [module + "." + CLASSES[family] + "." + n for n in names]
        or any(
            v[k]
            for k in (
                "failures",
                "errors",
                "skips",
                "user_accepted",
                "full_GRC9V4_conformance",
                "aggregate_closed",
            )
        )
        or v["public_api"] is not True
        or v["predecessor"] != predecessor(root)
        or set(v["evidence"]) != cases(family)
        or v["scope"] != "ten_family_contracts_four_family_native_execution"
        or v["execution"]["exact_backend"] != "flint"
        or v["execution"]["numerical_policy"] != "legacy_exact_v1"
    ):
        raise ValueError("invalid public API evidence")
    if family == "contracts":
        from pygrc.models.grc_9_v4_contracts import describe_families

        rows = v["evidence"]["families"]
        if len(rows) != 10 or [r["profile_family_id"] for r in rows] != list(
            CONTRACT_FAMILIES
        ):
            raise ValueError("all-ten contract coverage mismatch")
        for row, contract in zip(rows, describe_families()):
            if (
                any(row[k] != value for k, value in contract.to_payload().items())
                or row["roundtrip"] is not True
            ):
                raise ValueError("family contract projection mismatch")
        scope = v["evidence"]["execution_scope"]
        if scope != {
            "available": list(FAMILIES),
            "known_unavailable": [f for f in CONTRACT_FAMILIES if f not in FAMILIES],
            "no_unselected_execution": True,
        }:
            raise ValueError("contract recognition widened runtime scope")
    if family == "architecture":
        e = v["evidence"]
        if (
            e["execution_selection"]
            != dict(
                registered_owner_does_not_enable=True,
                missing_selected_owner_rejects=True,
                execution_families=list(FAMILIES),
            )
            or e["dispatch"]
            != dict(
                families=sorted(CONTRACT_FAMILIES),
                exact_type_rejection=True,
                routing_only_for_unselected=True,
            )
            or e["artifact_transfer"]
            != dict(
                complete_bundle_preserved=True,
                dropped_prefix_rejected=True,
                preparation_has_no_publication=True,
            )
            or e["rollback"]
            != dict(rejection=True, late_failure=True, whole_publication_unchanged=True)
            or e["event_predecessor_parity"]
            != dict(
                families=list(FAMILIES),
                results_and_checkpoint_bytes_equal=True,
                predecessor_commit="7b16696a",
            )
            or e["accepted_replay"]
            != dict(
                families=list(FAMILIES),
                checkpoint_bytes_equal=True,
                accepted_execution_records_unchanged=True,
            )
            or e["accepted_crossing_replay"]
            != dict(
                families=list(FAMILIES),
                checkpoint_bytes_equal=True,
                historical_execution_unchanged=True,
            )
            or e["branch_ownership"]
            != dict(
                immutable_enabled_branch=True,
                sole_receipt_ledger=True,
                complete_artifact_bundle=True,
                no_nested_enabled_owner=True,
                stale_transition_rejected=True,
                artifact_loss_rejected=True,
                mixed_replay_equal=True,
            )
        ):
            raise ValueError("architecture boundary coverage mismatch")
        replay = e["replay_assessment"]
        if (
            replay["family"] != "C_OS"
            or replay["outer_actions"] != 3
            or replay["initial_prefix_actions"] != 0
            or replay["executed_actions"] != dict(ordinary=2, expansion=1)
            or replay["standalone_event_checkpoint_replays"] != 0
            or replay["scope"] != "one_small_three_action_case_not_a_scaling_benchmark"
            or replay["decision"]
            != "retain_checkpoint_layouts; revisit_single_owner_single_journal_after_all_ten_enabled"
            or any(
                not 0 <= replay[k] < 3600
                for k in ("construction_seconds", "forward_seconds", "load_seconds")
            )
        ):
            raise ValueError("replay assessment mismatch")
    if family in FAMILIES:
        e = v["evidence"]
        required = {
            "construction": ("explicit_positive_step", "no_implicit_default"),
            "expansion_replay": (
                "event_committed",
                "positive_target_step",
                "reset_rebase_clock_preserved",
                "save_load_replay",
                "duplicate_independent",
            ),
            "branch_crossings": (
                "both_directions",
                "native_step_observables_equal",
                "enabled_continuation",
                "typed_request_not_discarded",
            ),
            "profile_migration": (
                "committed",
                "late_failure_atomic",
                "stale_source_rejected",
                "tampered_state_rejected",
                "negative_duration_rejected",
            ),
        }
        if any(e[case][k] is not True for case, keys in required.items() for k in keys):
            raise ValueError("public coverage mismatch")
        if family == "A_PC":
            exclusion = e["profile_migration"]["native_fixture_exclusion"]
            if (
                exclusion["committed"]
                or exclusion["failure"]["stage"] != "target_readmission"
                or e["profile_migration"]["source_path"] != "CI_to_PC_companion"
            ):
                raise ValueError("PC-to-CI admission exclusion lost")
    for ref in v["source_refs"] + v["input_refs"]:
        from p994b_runtime_successor import historical_source

        p = (root / ref["path"]).resolve()
        if (
            Path(ref["path"]).is_absolute()
            or not p.is_relative_to(root)
            or (
                sha(p.read_bytes()) != ref["sha256"]
                and historical_source(root, ref["path"], ref["sha256"]) != ref["sha256"]
            )
        ):
            raise ValueError("public API input drift: " + ref["path"])
    return v


def status(root):
    root = Path(root).resolve()
    records = [check(root, f) for f in CLASSES]
    refs = []
    for name in [filename(f) for f in CLASSES] + [
        BASE + "P9-9.4b-Review.md",
        BASE + "P9-9.4b-Architecture.md",
    ]:
        p = root / name
        if not p.exists():
            p = p.with_suffix(".json.xz")
        refs.append(
            dict(path=p.relative_to(root).as_posix(), sha256=sha(p.read_bytes()))
        )
    return dict(
        schema="p994b-public-api-status-v1",
        iteration="P9-9.4b",
        families=list(FAMILIES),
        contract_families=list(CONTRACT_FAMILIES),
        contract_matrix=records[-2]["evidence"]["families"],
        architecture=records[-1]["evidence"],
        records=[
            dict(
                family=v["family"],
                tests=v["tests_run"],
                outcome=v["outcome"],
                record_digest=v["record_digest"],
                elapsed_seconds=v["elapsed_seconds"],
            )
            for v in records
        ],
        user_accepted=False,
        public_api=True,
        full_GRC9V4_conformance=False,
        aggregate_closed=False,
        state="executed_pending_review",
        check_level="retained_integrity_only_no_native_rerun",
        source_refs=refs,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=CLASSES, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument(
        "--refresh-uncommitted",
        action="store_true",
        help="Replace only an uncommitted, unaccepted development record after a new run",
    )
    args = parser.parse_args()
    if args.run:
        p = ROOT / filename(args.family)
        existing = p if p.exists() else p.with_suffix(".json.xz")
        if existing.exists():
            tracked = (
                subprocess.run(
                    [
                        "git",
                        "cat-file",
                        "-e",
                        "HEAD:" + existing.relative_to(ROOT).as_posix(),
                    ],
                    cwd=ROOT,
                    capture_output=True,
                ).returncode
                == 0
            )
            if (
                not args.refresh_uncommitted
                or tracked
                or read(ROOT, args.family)["user_accepted"]
            ):
                raise FileExistsError(
                    "retained committed/accepted record cannot be replaced"
                )
        v = run(ROOT, args.family)
        raw = (json.dumps(v, indent=2) + "\n").encode()
        if len(raw) > 1_000_000:
            p = p.with_suffix(".json.xz")
            raw = lzma.compress(raw)
        if existing.exists() and existing != p:
            raise ValueError(
                "changed storage representation requires explicit maintenance"
            )
        with p.open("wb" if existing.exists() else "xb") as stream:
            stream.write(raw)
    else:
        v = check(ROOT, args.family)
    print(
        json.dumps(
            dict(
                family=args.family,
                mode=(
                    "contract_validation"
                    if args.run and args.family == "contracts"
                    else "native_execution"
                    if args.run
                    else "retained_integrity_only"
                ),
                outcome=v["outcome"],
                record_digest=v["record_digest"],
            )
        )
    )


if __name__ == "__main__":
    main()

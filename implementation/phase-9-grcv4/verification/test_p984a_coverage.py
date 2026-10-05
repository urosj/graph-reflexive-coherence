"""Literal inventory oracle and adversarial controls for the P9-8.4a record."""

import hashlib
import json
import unittest
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import prepare_p984a_coverage as coverage

from pygrc.models.grc_v4_codec import canonical_json_bytes

# Independently transcribed fixture meanings. Do not obtain these expectations
# from the producer, its generated record, or a pointer chosen by that record.
FROZEN_PATH = "specs/grc-v4-conformance-vectors.json"
EXPANSIONS = {
    "G9-EXPAND-" + suffix: (degree, chirality, phase, nodes, family)
    for suffix, degree, chirality, phase, nodes, family in (
        ("D30-CHIRALITY-POSITIVE", 30, 1, None, 4, "C_OS"),
        ("D30-CHIRALITY-NEGATIVE", 30, -1, None, 4, "C_OS"),
        ("D31-CHIRALITY-NEGATIVE-PHASE-1", 31, -1, 1, 5, "C_OS"),
        ("D31-CHIRALITY-NEGATIVE-PHASE-2", 31, -1, 2, 5, "C_OS"),
        ("D31-CHIRALITY-NEGATIVE-PHASE-3", 31, -1, 3, 5, "C_OS"),
        ("D31-CHIRALITY-POSITIVE-PHASE-1", 31, 1, 1, 5, "C_OS"),
        ("D31-CHIRALITY-POSITIVE-PHASE-2", 31, 1, 2, 5, "C_OS"),
        ("D31-CHIRALITY-POSITIVE-PHASE-3", 31, 1, 3, 5, "C_OS"),
        ("D45-CHIRALITY-POSITIVE", 45, 1, None, 7, "C_OS"),
        ("D45-CHIRALITY-NEGATIVE", 45, -1, None, 7, "C_OS"),
        ("D52-CHIRALITY-NEGATIVE-PHASE-1", 52, -1, 1, 8, "C_OS"),
        ("D52-CHIRALITY-NEGATIVE-PHASE-2", 52, -1, 2, 8, "C_OS"),
        ("D52-CHIRALITY-NEGATIVE-PHASE-3", 52, -1, 3, 8, "C_OS"),
        ("D52-CHIRALITY-POSITIVE-PHASE-1", 52, 1, 1, 8, "C_OS"),
        ("D52-CHIRALITY-POSITIVE-PHASE-2", 52, 1, 2, 8, "C_OS"),
        ("D52-CHIRALITY-POSITIVE-PHASE-3", 52, 1, 3, 8, "C_OS"),
        ("C-PC-CARRIER-RESET", 30, 1, None, 4, "C_PC"),
    )
}
META_BASE = "G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-1"
NORMALIZATION = "grc9v4-event-namespace-and-role-covariance-normalization-v1"
METAMORPHICS = {
    "G9-METAMORPHIC-SOURCE-EDGE-ORDER-PERMUTATION": (
        "source_edge_input_order_permutation",
        None,
        1,
        1,
        None,
        "P9-8.4e",
    ),
    "G9-METAMORPHIC-CYCLIC-CHART-ROTATION": (
        "cyclic_chart_rotation",
        "G9-EXPAND-D52-CHIRALITY-POSITIVE-PHASE-2",
        1,
        2,
        NORMALIZATION,
        "P9-8.4f",
    ),
    "G9-METAMORPHIC-REFLECTION-CHIRALITY-CONJUGACY": (
        "reflection_chirality_conjugacy",
        "G9-EXPAND-D52-CHIRALITY-NEGATIVE-PHASE-3",
        -1,
        3,
        NORMALIZATION,
        "P9-8.4f",
    ),
}
EXPECTED_FAMILIES = {
    "A_OS",
    "C_OS",
    "A_CI",
    "C_CI",
    "A_PC",
    "C_PC",
    "A_CI_PC",
    "C_CI_PC",
    "A_RG2b",
    "C_RG2b",
}


def independent_digest(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = coverage.build()
        cls.bundle = json.loads((coverage.ROOT / FROZEN_PATH).read_text())

    def rehash_reject(self, record):
        record["record_digest"] = coverage.record_digest(record)
        with self.assertRaisesRegex(ValueError, "source-derived inventory"):
            coverage.validate(record)

    def test_retained_record_reconstructs_without_a_runtime_call(self):
        stored = json.loads((coverage.ROOT / coverage.OUTPUT).read_text())
        self.assertEqual(stored, self.record)
        self.assertFalse(stored["runtime_executed"])
        # The producer reads Python sources through AST; it never imports these
        # numerical/fixture owners to manufacture evidence.
        self.assertNotIn(
            "tests.models.test_grc_9_v4_lifecycle", __import__("sys").modules
        )

    def test_literal_fixture_and_family_role_cartesian_product(self):
        self.assert_cell_semantics(self.record)

    def assert_cell_semantics(self, record):
        names = set(EXPANSIONS) | set(METAMORPHICS)
        actual = {
            (r["fixture_id"], r["family"], r["role"]) for r in record["coverage_cells"]
        }
        self.assertEqual(
            actual,
            {
                (n, f, role)
                for n in names
                for f in EXPECTED_FAMILIES
                for role in ("current", "reset")
            },
        )
        self.assertEqual(len(record["coverage_cells"]), 400)
        applicable = [r for r in record["coverage_cells"] if r["applicable"]]
        self.assertEqual(len(applicable), 382)
        counts = Counter(r["family"] for r in applicable)
        self.assertEqual(
            counts, {f: 40 if f == "C_PC" else 38 for f in EXPECTED_FAMILIES}
        )
        for row in record["coverage_cells"]:
            name, family, role = row["fixture_id"], row["family"], row["role"]
            self.assertEqual(row["id"], f"{name}::{family}::{role}")
            self.assertEqual(
                row["owner"],
                "P9-8.4b" if name in EXPANSIONS else METAMORPHICS[name][-1],
            )
            included = name != "G9-EXPAND-C-PC-CARRIER-RESET" or family == "C_PC"
            self.assertIs(row["applicable"], included)
            self.assertEqual(
                row["literal_identity_matches_family"],
                family == (EXPANSIONS[name][-1] if name in EXPANSIONS else "C_OS"),
            )
            self.assertEqual(
                row["stages"],
                {
                    stage: "not_applicable"
                    if not included
                    else "required_reset_preservation_without_source_beat"
                    if stage == "source_schedule" and role == "reset"
                    else "pending_exact_case_mapping"
                    for stage in (
                        "source_admission",
                        "source_schedule",
                        "fresh_trigger_request",
                        "mechanical_history_transfer",
                        "target_readmission",
                        "receipt_publication",
                        "target_continuation",
                        "final_read",
                    )
                },
            )
            self.assertEqual(
                row["comparison_contracts"],
                ["exact_frozen", "native_companion", "numerical", "history_and_charge"]
                + (["covariance"] if name in METAMORPHICS else []),
            )
            self.assertFalse(row["runtime_executed_by_P984a"])

    def test_exact_fixture_hashes_degrees_chiralities_and_phases(self):
        self.assert_fixture_semantics(self.record)

    def assert_fixture_semantics(self, record):
        fixtures = {r["id"]: r for r in record["fixture_inventory"]}
        self.assertEqual(len(record["fixture_inventory"]), 20)
        self.assertEqual(set(fixtures), set(EXPANSIONS) | set(METAMORPHICS))
        for field, id_key, expected_ids in (
            ("grc9_expansion_vectors", "fixture_id", EXPANSIONS),
            ("grc9_metamorphic_vectors", "vector_id", METAMORPHICS),
        ):
            source_rows = self.bundle[field]
            self.assertEqual(len(source_rows), len(expected_ids))
            self.assertEqual({r[id_key] for r in source_rows}, set(expected_ids))
            for index, payload in enumerate(source_rows):
                name = payload[id_key]
                row = fixtures[name]
                self.assertEqual(
                    row["source"],
                    {
                        "path": FROZEN_PATH,
                        "pointer": f"/{field}/{index}",
                        "jcs_sha256": independent_digest(payload),
                    },
                )
                if name in EXPANSIONS:
                    request, expected = payload["request"], payload["expected"]
                    meaning = EXPANSIONS[name]
                    for key in ("capacity_request", "chirality", "module_nodes"):
                        self.assertIs(type(row[key]), int)
                    self.assertIs(type(row["phase"]), type(meaning[2]))
                    self.assertEqual(
                        tuple(
                            row[k]
                            for k in (
                                "capacity_request",
                                "chirality",
                                "phase",
                                "module_nodes",
                                "literal_family",
                            )
                        ),
                        meaning,
                    )
                    self.assertEqual(
                        (
                            request["target_effective_degree"],
                            request["module_chirality"],
                            request["growth_phase"],
                            expected["canonical_module_node_count"],
                            expected["identity_payloads"]["target_profile"][
                                "profile_family_id"
                            ],
                        ),
                        meaning,
                    )
                    self.assertEqual(row["kind"], "expansion")
                    self.assertEqual(row["owner"], "P9-8.4b")
                    self.assertEqual(row["request"], request)
                    for key in (
                        "event_id",
                        "target_graph_digest",
                        "target_complete_profile_id",
                    ):
                        self.assertEqual(row[key], expected[key])
                    self.assertEqual(
                        row["comparison"], payload["numeric_comparison_policy"]
                    )
                else:
                    kind, target, sign, phase, policy, owner = METAMORPHICS[name]
                    for key in (
                        "chirality",
                        "phase",
                        "target_chirality",
                        "target_phase",
                    ):
                        self.assertIs(type(row[key]), int)
                    self.assertEqual(
                        tuple(
                            row[k]
                            for k in (
                                "kind",
                                "base",
                                "target",
                                "chirality",
                                "phase",
                                "target_chirality",
                                "target_phase",
                                "normalization_policy_id",
                                "owner",
                                "literal_family",
                            )
                        ),
                        (
                            kind,
                            META_BASE,
                            target,
                            1,
                            1,
                            sign,
                            phase,
                            policy,
                            owner,
                            "C_OS",
                        ),
                    )
                    self.assertEqual(
                        (
                            payload["kind"],
                            payload["base_vector_id"],
                            payload.get("expected_target_vector_id"),
                            payload.get("normalization_policy_id"),
                        ),
                        (kind, META_BASE, target, policy),
                    )

    def test_frozen_cutoff_witness_and_companion_identity_are_distinct(self):
        # Exact literal incidence calculation verifies the recorded obstruction
        # independently of the current implementation's selector.
        graph = self.bundle["port_graph_envelope_vectors"][0]["payload"]
        witness = {n: Fraction(0) for n in graph["live_node_ids"]}
        witness.update({"outside-1": Fraction(1), "outside-4": Fraction(-1)})
        product = dict.fromkeys(witness, Fraction(0))
        for edge in graph["edges"]:
            a, b = edge["tail"]["node_id"], edge["head"]["node_id"]
            difference = witness[a] - witness[b]
            product[a] += difference
            product[b] -= difference
        self.assertEqual(product, witness)
        frozen_id = next(
            r for r in self.record["fixture_inventory"] if r["id"] == coverage.PINNED
        )["target_complete_profile_id"]
        for data in self.record["families"].values():
            self.assertNotEqual(
                data["subject_bindings"]["target"]["profile_id"], frozen_id
            )
            self.assertEqual(data["baseline_schedule"]["source_reset_beats"], 0)
            self.assertEqual(data["baseline_schedule"]["target_beats_per_role"], 10)
            self.assertIn("not_frozen_identity_replay", data["reusable_scope"])
            self.assertEqual(data["baseline_request"]["module_chirality"], 1)
            self.assertEqual(data["baseline_request"]["growth_phase"], 3)

    def test_large_reports_keep_forty_distinct_outcomes_and_no_events(self):
        rows = self.record["larger_graph_cells"]
        self.assertEqual(len(rows), 20)
        self.assertEqual(
            {(r["family"], r["role"]) for r in rows},
            {(f, role) for f in EXPECTED_FAMILIES for role in ("current", "reset")},
        )
        counts = Counter(
            r["status"] for row in rows for r in row["recorded_probe_results"].values()
        )
        self.assertEqual(counts, {"passed": 16, "incomplete": 16, "rejected": 8})
        for row in rows:
            self.assertEqual(row["id"], f"large::{row['family']}::{row['role']}")
            self.assertEqual(row["events_committed"], 0)
            self.assertEqual(row["physical_steps"], 0)
            self.assertEqual(row["prerequisite_owner"], f"P9-8.4g[{row['family']}]")
            self.assertEqual(row["execution_owner"], f"P9-8.4h[{row['family']}]")
            if row["family"] in {"C_RG2b", "A_RG2b"}:
                self.assertEqual(
                    row["disposition"], "blocked_new_cyclic_completion_proof"
                )

    def assert_carrier_crosswalk(self, record):
        crosswalk = record["carrier_requirement_crosswalk"]
        self.assertEqual(crosswalk["authority"]["path"], "specs/grc-9-v4-spec.md")
        self.assertIn("literal_C_PC_fixture", crosswalk["exclusion_rule"])
        self.assertIn("all_four_persistent_families", crosswalk["exclusion_rule"])
        self.assertIn(
            "not_a_mathematical_impossibility", crosswalk["applicability_scope"]
        )
        rows = crosswalk["rows"]
        self.assertEqual(len(rows), 8)
        self.assertEqual(
            {(r["family"], r["role"]) for r in rows},
            {
                (f, role)
                for f in ("C_PC", "A_PC", "C_CI_PC", "A_CI_PC")
                for role in ("current", "reset")
            },
        )
        cases = {r["id"]: r for r in record["coverage_cells"]}
        larger = {r["id"]: r for r in record["larger_graph_cells"]}
        for row in rows:
            f, role = row["family"], row["role"]
            shared = {
                f"{name}::{f}::{role}"
                for name, meaning in EXPANSIONS.items()
                if meaning[-1] == "C_OS"
            }
            self.assertEqual(len(row["shared_expansion_cells"]), 16)
            self.assertEqual(set(row["shared_expansion_cells"]), shared)
            self.assertEqual(row["owner"], "P9-8.4b")
            self.assertEqual(
                row["literal_fixture_cells"],
                [f"G9-EXPAND-C-PC-CARRIER-RESET::{f}::{role}"] if f == "C_PC" else [],
            )
            self.assertEqual(len(row["covariance_cells"]), 3)
            self.assertEqual(
                set(row["covariance_cells"]),
                {f"{name}::{f}::{role}" for name in METAMORPHICS},
            )
            for key in (
                "shared_expansion_cells",
                "literal_fixture_cells",
                "covariance_cells",
            ):
                for cell_id in row[key]:
                    case = cases[cell_id]
                    self.assertTrue(case["applicable"])
                    self.assertEqual((case["family"], case["role"]), (f, role))
            self.assertEqual(row["larger_cell"], f"large::{f}::{role}")
            self.assertEqual(row["larger_prerequisite_owner"], f"P9-8.4g[{f}]")
            self.assertEqual(row["larger_execution_owner"], f"P9-8.4h[{f}]")
            self.assertEqual(
                larger[row["larger_cell"]]["execution_owner"],
                row["larger_execution_owner"],
            )
            # The selected loss/reset policy in the spec applies to the whole
            # actual carrier of each role. A W remains a distinct unsigned channel.
            self.assertEqual(
                row["obligations_by_stage"],
                {
                    "mechanical_history_transfer": [
                        "archive_whole_actual_source_Z_for_this_role",
                        "initialize_whole_target_Z_to_canonical_zero",
                        "preserve_unsigned_A_W_by_stable_edge_lineage_and_initialize_new_edges"
                        if f in {"A_PC", "A_CI_PC"}
                        else "rederive_C_reference_without_candidate_history",
                    ],
                    "target_readmission": [
                        "fresh_reference_and_full_target_admission_for_this_role",
                        "zero_Z_is_present_carrier_not_absent_history",
                    ],
                    "receipt_publication": [
                        "bind_both_carrier_content_digest_preimages_for_this_role",
                        "declare_carrier_history_loss_without_partial_preservation",
                    ],
                    "target_continuation": [
                        "read_actual_incoming_Z_and_write_Z_once_from_the_same_source",
                    ],
                    "final_read": [
                        "verify_actual_final_carrier_without_history_repair"
                    ],
                },
            )
            self.assertEqual(
                row["disposition"], "pending_case_execution_and_independent_comparison"
            )
            self.assertFalse(row["runtime_executed_by_P984a"])

    def test_carrier_requirements_survive_literal_fixture_exclusions(self):
        self.assert_carrier_crosswalk(self.record)

    def test_independent_table_rejects_a_consistently_wrong_fixture_generator(self):
        original = coverage.fixture_inventory

        def wrong_phase(*args):
            rows = original(*args)
            next(
                r for r in rows if r["id"] == "G9-EXPAND-D52-CHIRALITY-NEGATIVE-PHASE-1"
            )["phase"] = 3
            return rows

        with patch.object(coverage, "fixture_inventory", wrong_phase):
            bad = coverage.build()
            coverage.validate(bad)  # A freshly regenerated wrong record is consistent.
            with self.assertRaises(AssertionError):
                self.assert_fixture_semantics(bad)

    def test_independent_cells_reject_consistently_wrong_generator_assignments(self):
        original = coverage.coverage_cells
        for mutation in ("owner", "exemption"):

            def wrong_cells(*args, mutation=mutation):
                rows = original(*args)
                if mutation == "owner":
                    rows[0]["owner"] = "P9-8.4f"
                else:
                    # Preserve 382/18 and every per-family count while excluding
                    # the wrong A_PC case. Aggregate counting cannot catch this.
                    a = next(
                        r
                        for r in rows
                        if r["family"] == "A_PC"
                        and r["role"] == "current"
                        and r["applicable"]
                    )
                    b = next(
                        r
                        for r in rows
                        if r["family"] == "A_PC"
                        and r["role"] == "current"
                        and not r["applicable"]
                    )
                    a["applicable"], b["applicable"] = False, True
                return rows

            with (
                self.subTest(mutation=mutation),
                patch.object(coverage, "coverage_cells", wrong_cells),
            ):
                bad = coverage.build()
                coverage.validate(bad)
                with self.assertRaises(AssertionError):
                    self.assert_cell_semantics(bad)

    def test_independent_semantics_reject_metadata_and_stage_misassignments(self):
        for field, value in (
            ("chirality", -1),
            ("chirality", True),
            ("phase", 1),
            ("literal_family", "A_OS"),
            ("owner", "P9-8.4e"),
            ("event_id", "foreign"),
        ):
            bad = deepcopy(self.record)
            bad["fixture_inventory"][0][field] = value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                self.assert_fixture_semantics(bad)
        bad = deepcopy(self.record)
        bad["fixture_inventory"][0]["source"] = deepcopy(
            bad["fixture_inventory"][1]["source"]
        )
        with self.assertRaises(AssertionError):
            self.assert_fixture_semantics(bad)
        for mutation in (
            "missing_stage",
            "wrong_reset_schedule",
            "missing_covariance_contract",
        ):
            bad = deepcopy(self.record)
            if mutation == "missing_stage":
                stages = bad["coverage_cells"][0]["stages"]
                stages["unrelated_stage"] = stages.pop("final_read")
            elif mutation == "wrong_reset_schedule":
                row = next(r for r in bad["coverage_cells"] if r["role"] == "reset")
                row["stages"]["source_schedule"] = "pending_exact_case_mapping"
            else:
                row = next(
                    r for r in bad["coverage_cells"] if r["fixture_id"] in METAMORPHICS
                )
                row["comparison_contracts"].remove("covariance")
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                self.assert_cell_semantics(bad)

    def test_independent_crosswalk_rejects_missing_or_misrouted_requirements(self):
        for mutation in (
            "drop_role",
            "duplicate_role",
            "foreign_cell",
            "drop_layout",
            "drop_covariance",
            "candidate_history",
            "partial_carrier",
            "missing_receipt",
            "wrong_large_owner",
        ):
            bad = deepcopy(self.record)
            rows = bad["carrier_requirement_crosswalk"]["rows"]
            row = next(r for r in rows if r["family"] == "A_PC")
            if mutation == "drop_role":
                rows.pop()
            elif mutation == "duplicate_role":
                rows[-1] = deepcopy(rows[0])
            elif mutation == "foreign_cell":
                row["shared_expansion_cells"][0] = rows[0]["shared_expansion_cells"][0]
            elif mutation == "drop_layout":
                row["shared_expansion_cells"].pop()
            elif mutation == "drop_covariance":
                row["covariance_cells"].pop()
            elif mutation == "candidate_history":
                row["obligations_by_stage"]["mechanical_history_transfer"][2] = (
                    "drop_A_W"
                )
            elif mutation == "partial_carrier":
                row["obligations_by_stage"]["mechanical_history_transfer"][1] = (
                    "reset_new_edges_only"
                )
            elif mutation == "missing_receipt":
                row["obligations_by_stage"].pop("receipt_publication")
            else:
                row["larger_prerequisite_owner"] = "P9-8.4h[A_PC]"
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                self.assert_carrier_crosswalk(bad)

    def test_norms_solver_tolerances_and_comparison_budgets_are_separate(self):
        rows = self.record["families"]
        cci = rows["C_CI"]
        self.assertEqual(
            cci["subject_bindings"]["source"]["parameters"]["geometry_radius"], 2**-18
        )
        self.assertIn("infinity", cci["comparison_budget"]["geometry_error_norm"])
        self.assertIn(
            "l2",
            cci["subject_bindings"]["source"]["realization_contract"][
                "residual_norm_id"
            ],
        )
        self.assertEqual(
            rows["C_CI_PC"]["comparison_budget"]["geometry_error_norm"],
            "Frobenius_root_error_bound",
        )
        self.assertEqual(
            rows["C_PC"]["comparison_budget"]["kind"],
            "bounded_dense_crosscheck_not_certified_full_error",
        )
        for f in ("A_RG2b", "C_RG2b"):
            self.assertIn(
                "native_current_L2_and_geometry_error_bridges", rows[f]["prerequisites"]
            )
            self.assertIn(
                "induced_infinity",
                rows[f]["subject_bindings"]["source"]["realization_contract"][
                    "error_norm_id"
                ],
            )
        self.assertIsNone(
            self.record["comparison_contracts"]["numerical"][
                "new_subject_default_budget"
            ]
        )

    def test_source_bindings_are_portable_current_and_unique(self):
        refs = self.record["source_bindings"]
        self.assertEqual(len(refs), len({r["path"] for r in refs}))
        for ref in refs:
            self.assertFalse(Path(ref["path"]).is_absolute())
            self.assertNotIn("..", Path(ref["path"]).parts)
            self.assertEqual(
                hashlib.sha256((coverage.ROOT / ref["path"]).read_bytes()).hexdigest(),
                ref["sha256"],
            )

    def test_atomic_and_additional_obligations_retain_their_owners(self):
        self.assertEqual(len(self.record["atomic_handoff"]), 5)
        self.assertEqual(
            {r["owner"] for r in self.record["atomic_handoff"]}, {"P9-8.5"}
        )
        self.assertEqual(
            {r["owner"] for r in self.record["additional_work_register"]},
            {f"P9-8.4{c}" for c in "cdef"},
        )

    def test_claim_statuses_are_bound_design_semantics(self):
        claims = self.record["scientific_claim_mapping"]["equation_contracts"]
        self.assertEqual(len(claims), 20)
        claim = next(
            r
            for r in claims
            if r["equation_contract_id"] == "D11-G9-EC-DIHEDRAL-COVARIANCE"
        )
        self.assertEqual(
            claim["support_semantics"],
            "accepted_design_level_combinatorial_covariance_with_runtime_verification_pending",
        )

    def test_rehashed_omission_duplicate_and_role_drop_reject(self):
        for mutation in ("omit", "duplicate", "drop_reset"):
            bad = deepcopy(self.record)
            if mutation == "omit":
                bad["coverage_cells"].pop()
            elif mutation == "duplicate":
                bad["coverage_cells"][-1] = deepcopy(bad["coverage_cells"][0])
            else:
                bad["coverage_cells"] = [
                    r for r in bad["coverage_cells"] if r["role"] != "reset"
                ]
            with self.subTest(mutation=mutation):
                self.rehash_reject(bad)

    def test_rehashed_scope_promotion_and_false_exemption_reject(self):
        for mutation in ("promotion", "exemption", "new_acceptance", "stage"):
            bad = deepcopy(self.record)
            if mutation == "promotion":
                bad["runtime_executed"] = True
            elif mutation == "new_acceptance":
                bad["new_runtime_acceptance"] = True
            elif mutation == "stage":
                bad["coverage_cells"][0]["stages"]["target_readmission"] = "passed"
            else:
                bad["coverage_cells"][0]["applicable"] = False
            with self.subTest(mutation=mutation):
                self.rehash_reject(bad)

    def test_rehashed_fixture_profile_and_phase_substitution_reject(self):
        for mutation in ("phase", "profile", "fixture_hash"):
            bad = deepcopy(self.record)
            if mutation == "phase":
                bad["fixture_inventory"][0]["phase"] = 1
            elif mutation == "profile":
                bad["families"]["A_OS"]["subject_bindings"]["source"]["profile_id"] = (
                    bad["families"]["C_OS"]["subject_bindings"]["source"]["profile_id"]
                )
            else:
                bad["fixture_inventory"][0]["source"]["jcs_sha256"] = "0" * 64
            with self.subTest(mutation=mutation):
                self.rehash_reject(bad)

    def test_rehashed_budget_norm_or_claim_upgrade_reject(self):
        for mutation in ("budget", "norm", "claim"):
            bad = deepcopy(self.record)
            if mutation == "budget":
                bad["comparison_contracts"]["numerical"][
                    "new_subject_default_budget"
                ] = 1
            elif mutation == "norm":
                bad["families"]["C_CI"]["comparison_budget"]["geometry_error_norm"] = (
                    "max_entry"
                )
            else:
                bad["scientific_claim_mapping"]["equation_contracts"][17][
                    "support_semantics"
                ] = "runtime_proved"
            with self.subTest(mutation=mutation):
                self.rehash_reject(bad)

    def test_rehashed_probe_success_and_missing_stage_requirements_reject(self):
        for mutation in ("probe", "required_fields", "event"):
            bad = deepcopy(self.record)
            if mutation == "probe":
                row = next(
                    r for r in bad["larger_graph_cells"] if r["family"] == "A_RG2b"
                )
                row["recorded_probe_results"]["source"]["status"] = "passed"
            elif mutation == "event":
                bad["larger_graph_cells"][0]["events_committed"] = 1
            else:
                del bad["harness_contract"]["input_required"]["comparison_budgets"]
            with self.subTest(mutation=mutation):
                self.rehash_reject(bad)

    def test_changed_bound_source_rejects_even_when_old_record_rehashed(self):
        original = coverage.Sources.bind

        def altered(sources, path):
            ref = original(sources, path)
            if path == "specs/grc-9-v4-spec.md":
                ref["sha256"] = "0" * 64
            return ref

        with (
            patch.object(coverage.Sources, "bind", altered),
            self.assertRaisesRegex(ValueError, "source-derived inventory"),
        ):
            coverage.validate(deepcopy(self.record))


if __name__ == "__main__":
    unittest.main()

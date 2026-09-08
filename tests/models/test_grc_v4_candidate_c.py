"""P9-4.1 reference-map and constructor pressure; no candidate solve claims.

Expectations use scalar rational products, explicit coordinate permutations
and independent ASCII hashing. Profile helpers construct inputs only.
"""

from __future__ import annotations

from copy import deepcopy
from contextlib import contextmanager
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import random
import sys
from types import ModuleType
from typing import Any, Callable, Iterator
import unittest

from pygrc.models.grc_v4_candidate_c import CandidateCTransport
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_geometry import (
    GRCV4Graph,
    GRCV4Geometry,
    OneForm,
    OneFormHodge,
    OrientedEdge,
    PhysicalFlux,
    PhysicalFluxFlatMap,
)
from pygrc.models.grc_v4_profile import GRCV4Profile, resolve_profile
from tests.models.test_grc_v4_geometry import (
    _P934Result,
    _p934_coverage,
    _p934_ids,
    _p934_loaded_sources,
    graph_payload,
    stage_reference_fixture,
)
from tests.models.test_grc_v4_profile import family_fixture, reidentify


def profile_fixture(
    weights: dict[str, Any] | None = None,
    *,
    eta: float = 3,
    realization: str = "OS",
    changes: dict[str, dict[str, Any]] | None = None,
) -> GRCV4Profile:
    weights = {"a": 5, "z": 2} if weights is None else weights
    params, identity = family_fixture("C", realization)
    params["candidate"].update(
        W_C_tr=weights,
        W_C_tr_content_digest=payload_identity(
            "wctr_identity_payload",
            {"schema_version": "grcv4-wctr-identity-v1", "W_C_tr": weights},
        ),
        eta_C=eta,
    )
    params["geometry"]["reference_hodge_digest"] = payload_identity(
        "reference_hodge_identity_payload",
        {
            "schema_version": "grcv4-reference-hodge-identity-v1",
            "edge_weights": weights,
        },
    )
    if changes:
        for group, updates in changes.items():
            if group == "identity":
                identity.update(updates)
            else:
                params[group].update(updates)
    reidentify(params, identity)
    return resolve_profile(params, identity)


class CandidateCReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = GRCV4Graph.from_payload(graph_payload())
        self.binding = CandidateCTransport(self.graph, profile_fixture())

    def test_exact_siblings_and_typed_operator_actions(self) -> None:
        bound = self.binding
        self.assertEqual(bound.params.transport_id, "C-HM-STIFFNESS-BASELINE-v1")
        self.assertEqual(bound.structural_hodge.matrix, ((2, 0), (0, 5)))
        self.assertEqual(bound.mobility.matrix, ((6, 0), (0, 15)))
        self.assertIs(type(bound.structural_hodge), OneFormHodge)
        self.assertEqual(
            bound.mobility.apply(OneForm(self.graph, (2, -3))),
            PhysicalFlux(self.graph, (12, -45)),
        )
        self.assertEqual(
            PhysicalFluxFlatMap(bound.structural_hodge)
            .flat(PhysicalFlux(self.graph, (4, 10)))
            .values,
            (2, 2),
        )
        with self.assertRaises(TypeError):
            PhysicalFluxFlatMap(bound.mobility)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            bound.mobility.apply(PhysicalFlux(self.graph, (2, 3)))  # type: ignore[arg-type]

    def test_equal_matrices_still_have_separate_constructor_identities(self) -> None:
        bound = CandidateCTransport(self.graph, profile_fixture(eta=1))
        self.assertEqual(bound.structural_hodge.matrix, bound.mobility.matrix)
        self.assertNotEqual(
            bound.structural_hodge_constructor_identity,
            bound.mobility_constructor_identity,
        )
        # Independent JSON/SHA oracle for these ASCII, integer-token payloads.
        for payload, identity, policy, kind in [
            (
                bound.structural_hodge_constructor_payload,
                bound.structural_hodge_constructor_identity,
                "diag_W_C_tr_structural_hodge_v1",
                "one_form_hodge",
            ),
            (
                bound.mobility_constructor_payload,
                bound.mobility_constructor_identity,
                "eta_C_diag_W_C_tr_mobility_v1",
                "physical_flux_mobility",
            ),
        ]:
            self.assertEqual(payload["constructor_id"], policy)
            self.assertEqual(payload["output_type"], kind)
            expected = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            self.assertEqual(
                identity, "grcv4-c-reference-constructor-sha256:" + expected
            )

    def test_gain_changes_only_mobility_constructor(self) -> None:
        altered = CandidateCTransport(self.graph, profile_fixture(eta=7))
        self.assertEqual(altered.mobility.diagonal, (14, 35))
        self.assertEqual(altered.structural_hodge, self.binding.structural_hodge)
        self.assertEqual(
            altered.structural_hodge_constructor_identity,
            self.binding.structural_hodge_constructor_identity,
        )
        self.assertNotEqual(
            altered.mobility_constructor_identity,
            self.binding.mobility_constructor_identity,
        )
        self.assertNotEqual(altered.identity, self.binding.identity)

    def test_map_value_and_stable_id_are_identity_inputs(self) -> None:
        for weights in [{"a": 5, "z": 3}, {"a": 2, "z": 5}]:
            altered = CandidateCTransport(self.graph, profile_fixture(weights))
            self.assertNotEqual(
                altered.params.W_C_tr_content_digest,
                self.binding.params.W_C_tr_content_digest,
            )
            self.assertNotEqual(
                altered.structural_hodge_constructor_identity,
                self.binding.structural_hodge_constructor_identity,
            )
            self.assertNotEqual(
                altered.mobility_constructor_identity,
                self.binding.mobility_constructor_identity,
            )
        reordered = CandidateCTransport(self.graph, profile_fixture({"z": 2, "a": 5}))
        self.assertEqual(
            reordered.to_canonical_bytes(), self.binding.to_canonical_bytes()
        )
        self.assertEqual(reordered.identity, self.binding.identity)

    def test_unrelated_profile_controls_do_not_condition_reference_constructors(
        self,
    ) -> None:
        for changes in [
            {"candidate": {name: value}}
            for name, value in [
                ("kappa_M_C", 0),
                ("kappa_M_C", 19),
                ("chi_C", 0),
                ("zeta_C", 0),
                ("tau_C", 0),
                ("C_ref", 17),
                ("Lambda_C", 11),
                ("kappa_Phi_C", 23),
            ]
        ] + [{"geometry": {"kappa_H": 9}}]:
            with self.subTest(changes=changes):
                bound = CandidateCTransport(
                    self.graph, profile_fixture(changes=changes)
                )
                self.assertEqual(bound.mobility.matrix, self.binding.mobility.matrix)
                self.assertEqual(
                    bound.structural_hodge_constructor_identity,
                    self.binding.structural_hodge_constructor_identity,
                )
                self.assertEqual(
                    bound.mobility_constructor_identity,
                    self.binding.mobility_constructor_identity,
                )
                if bound.profile != self.binding.profile:
                    self.assertNotEqual(bound.identity, self.binding.identity)

    def test_all_five_declarations_bind_without_advertising_execution(self) -> None:
        from pygrc.models.grc_v4_profile import list_supported_profiles

        for realization in ["OS", "CI", "RG2b", "PC", "CI+PC"]:
            with self.subTest(realization=realization):
                bound = CandidateCTransport(
                    self.graph, profile_fixture(realization=realization)
                )
                self.assertEqual(
                    bound.mobility_constructor_identity,
                    self.binding.mobility_constructor_identity,
                )
                self.assertEqual(
                    bound.profile.identity_payload.realization, realization
                )
        self.assertEqual(list_supported_profiles(), frozenset())

    def test_units_declaration_is_part_of_each_typed_constructor_identity(self) -> None:
        bound = CandidateCTransport(
            self.graph,
            profile_fixture(
                changes={
                    "common": {"units_id": "test_alternative_units_v1"},
                    "identity": {"units_id": "test_alternative_units_v1"},
                }
            ),
        )
        self.assertEqual(bound.mobility.matrix, self.binding.mobility.matrix)
        self.assertNotEqual(
            bound.mobility_constructor_identity,
            self.binding.mobility_constructor_identity,
        )
        self.assertNotEqual(
            bound.structural_hodge_constructor_identity,
            self.binding.structural_hodge_constructor_identity,
        )
        # These are declarations. No unit conversion or executable-profile
        # admission is inferred for this alternative synthetic unit policy.

    def test_complete_reference_geometry_agrees_with_sibling_hodge(self) -> None:
        reference = stage_reference_fixture()
        bound = CandidateCTransport(reference.graph, reference.profile)
        self.assertEqual(bound.structural_hodge, reference.pairings.one_form)
        for matrix in [((2.0, 0.0), (0.0, 7.0)), ((9.0, 2.0), (2.0, 3.0))]:
            trial = GRCV4Geometry(reference, OneFormHodge(reference.graph, matrix))
            self.assertNotEqual(trial.one_form_hodge, bound.structural_hodge)
            rebuilt = CandidateCTransport(
                trial.reference.graph, trial.reference.profile
            )
            self.assertEqual(rebuilt.mobility.matrix, bound.mobility.matrix)
            self.assertEqual(
                rebuilt.mobility_constructor_identity,
                bound.mobility_constructor_identity,
            )
            with self.assertRaises(TypeError):
                CandidateCTransport(reference.graph, trial)  # type: ignore[arg-type]

        with self.assertRaises(TypeError):
            CandidateCTransport(reference.graph, reference.geometry())  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            CandidateCTransport(reference.graph, bound.structural_hodge)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            replace(bound, h=reference.geometry())  # type: ignore[call-arg]

    def test_reference_hodge_mismatch_rejects_even_with_reidentified_profile(
        self,
    ) -> None:
        wrong = payload_identity(
            "reference_hodge_identity_payload",
            {
                "schema_version": "grcv4-reference-hodge-identity-v1",
                "edge_weights": {"z": 5, "a": 2},
            },
        )
        profile = profile_fixture(
            changes={"geometry": {"reference_hodge_digest": wrong}}
        )
        with self.assertRaises(ValueError):
            CandidateCTransport(self.graph, profile)

    def test_map_must_cover_exact_target_edges_without_copy_or_resize(self) -> None:
        for weights in [
            {"z": 2},
            {"a": 5},
            {"z": 2, "a": 5, "extra": 1},
            {"a": 5, "renamed-z": 2},
        ]:
            with (
                self.subTest(weights=weights),
                self.assertRaisesRegex(ValueError, "exactly"),
            ):
                CandidateCTransport(self.graph, profile_fixture(weights))

    def test_map_domain_and_gain_reject_without_repair(self) -> None:
        invalid: list[Any] = [
            0,
            -0.0,
            -1,
            True,
            None,
            "2",
            [],
            {},
            math.inf,
            -math.inf,
            math.nan,
            2**53,
        ]
        for bad in invalid:
            with self.subTest(weight=bad), self.assertRaises((TypeError, ValueError)):
                profile_fixture({"a": 5, "z": bad})
            with self.subTest(gain=bad), self.assertRaises((TypeError, ValueError)):
                profile_fixture(eta=bad)
        for weights in [{}, {"": 2, "a": 5}, {1: 2, "a": 5}]:
            with (
                self.subTest(weights=weights),
                self.assertRaises((TypeError, ValueError)),
            ):
                profile_fixture(weights)  # type: ignore[arg-type]

    def test_transport_and_constructor_policy_ids_cannot_be_substituted(self) -> None:
        for name, bad in [
            ("transport_id", "C-HM-STIFFNESS-BASELINE-v2"),
            ("E_H_policy_id", "eta_C_diag_W_C_tr_mobility_v1"),
            ("E_M_policy_id", "diag_W_C_tr_structural_hodge_v1"),
        ]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                profile_fixture(changes={"candidate": {name: bad}})

    def test_complete_profile_and_map_identity_tampering_rejects(self) -> None:
        original: Any = self.binding.to_payload()
        for field in [
            "complete_profile_id",
            "params_hash",
            "W_C_tr_content_digest",
            "W_C_tr",
        ]:
            value = deepcopy(original)
            profile = value["profile"]
            if field == "complete_profile_id":
                profile[field] = profile[field][:-1] + (
                    "0" if profile[field][-1] != "0" else "1"
                )
            elif field == "params_hash":
                profile["identity_payload"][field] = "grcv4-params-sha256:" + "0" * 64
            elif field == "W_C_tr":
                profile["params_resolved"]["candidate"][field]["z"] = 7
            else:
                profile["params_resolved"]["candidate"][field] = (
                    "grcv4-wctr-sha256:" + "0" * 64
                )
            with self.subTest(field=field), self.assertRaises(ValueError):
                CandidateCTransport.from_payload(value)
        self.assertEqual(original, self.binding.to_payload())

    def test_binary64_positive_extremes_and_product_boundaries(self) -> None:
        tiny = math.ulp(0.0)
        for eta, weight in [
            (1, tiny),
            (1, sys.float_info.max),
            (tiny, sys.float_info.max),
            (sys.float_info.max, tiny),
            (0.5, 2 * tiny),
            (2, sys.float_info.max / 2),
            (0.1, 0.3),
            (math.nextafter(1, 2), tiny),
        ]:
            with self.subTest(eta=eta, weight=weight):
                expected = float(Fraction(eta) * Fraction(weight))
                bound = CandidateCTransport(
                    self.graph, profile_fixture({"z": weight, "a": weight}, eta=eta)
                )
                self.assertEqual(bound.mobility.diagonal, (expected, expected))
                self.assertGreater(expected, 0)
                self.assertEqual(
                    CandidateCTransport.from_canonical_bytes(
                        bound.to_canonical_bytes()
                    ),
                    bound,
                )
        for eta, weight in [(0.5, tiny), (tiny, tiny), (2, sys.float_info.max)]:
            with self.subTest(eta=eta, weight=weight), self.assertRaises(ValueError):
                CandidateCTransport(
                    self.graph, profile_fixture({"z": weight, "a": weight}, eta=eta)
                )

    def test_random_scalar_rational_oracle_across_wide_exponents(self) -> None:
        rng = random.Random(941)
        for _ in range(80):
            eta = math.ldexp(rng.uniform(0.5, 1), rng.randint(-500, 500))
            weights = {
                edge: math.ldexp(rng.uniform(0.5, 1), rng.randint(-500, 500))
                for edge in reversed(self.graph.live_edge_ids)
            }
            bound = CandidateCTransport(self.graph, profile_fixture(weights, eta=eta))
            self.assertEqual(
                bound.mobility.diagonal,
                tuple(
                    float(Fraction(eta) * Fraction(weights[e]))
                    for e in self.graph.live_edge_ids
                ),
            )

    def test_graph_outliers_and_signed_permutation_covariance(self) -> None:
        # Loops, parallel edges, disconnected components and an isolated vertex.
        edges = (
            OrientedEdge("parallel-2", "u", "v"),
            OrientedEdge("loop", "u", "u"),
            OrientedEdge("parallel-1", "u", "v"),
            OrientedEdge("far", "x", "y"),
        )
        graph = GRCV4Graph(("u", "v", "x", "y", "isolated"), edges)
        weights = {"far": 7, "parallel-1": 5, "loop": 3, "parallel-2": 2}
        base = CandidateCTransport(graph, profile_fixture(weights))
        form = (2, 3, -4, 5)
        flux = base.mobility.apply(OneForm(graph, form)).values
        rng = random.Random(941)
        for _ in range(30):
            order = rng.sample(range(4), 4)
            signs = [rng.choice([-1, 1]) for _ in order]
            target_edges = tuple(
                OrientedEdge(
                    edges[i].edge_id,
                    edges[i].tail_node_id if sign == 1 else edges[i].head_node_id,
                    edges[i].head_node_id if sign == 1 else edges[i].tail_node_id,
                )
                for i, sign in zip(order, signs, strict=True)
            )
            target = GRCV4Graph(tuple(reversed(graph.live_node_ids)), target_edges)
            bound = CandidateCTransport(target, base.profile)
            moved_form = tuple(
                sign * form[i] for i, sign in zip(order, signs, strict=True)
            )
            self.assertEqual(
                bound.mobility.apply(OneForm(target, moved_form)).values,
                tuple(sign * flux[i] for i, sign in zip(order, signs, strict=True)),
            )
            self.assertEqual(
                bound.params.W_C_tr_content_digest, base.params.W_C_tr_content_digest
            )
            self.assertEqual(
                bound.structural_hodge.matrix,
                tuple(
                    tuple(weights[edges[i].edge_id] if i == j else 0 for j in order)
                    for i in order
                ),
            )
        renamed = GRCV4Graph(
            graph.live_node_ids,
            tuple(replace(e, edge_id="new:" + e.edge_id) for e in edges),
        )
        with self.assertRaises(ValueError):
            CandidateCTransport(renamed, base.profile)
        readmitted = CandidateCTransport(
            renamed, profile_fixture({"new:" + e: v for e, v in weights.items()})
        )
        self.assertEqual(readmitted.mobility.matrix, base.mobility.matrix)
        self.assertNotEqual(
            readmitted.mobility_constructor_identity, base.mobility_constructor_identity
        )

    def test_unicode_and_numeric_looking_edge_ids_roundtrip(self) -> None:
        graph = GRCV4Graph(
            (1, "1"),
            (
                OrientedEdge("e\u0301", 1, "1"),
                OrientedEdge("é", "1", 1),
                OrientedEdge("01", 1, 1),
                OrientedEdge("1", "1", "1"),
            ),
        )
        bound = CandidateCTransport(
            graph, profile_fixture({"1": 7, "01": 5, "é": 3, "e\u0301": 2})
        )
        self.assertEqual(bound.mobility.diagonal, (6, 9, 15, 21))
        restored = CandidateCTransport.from_canonical_bytes(bound.to_canonical_bytes())
        self.assertEqual(restored, bound)
        self.assertEqual(restored.identity, bound.identity)

    def test_noncanonical_duplicate_or_extra_wire_authority_rejects(self) -> None:
        encoded = self.binding.to_canonical_bytes()
        for wire in [
            b" " + encoded,
            encoded.replace(b'"z":2', b'"z":2,"z":7', 1),
            encoded.replace(b'"z":2', b'"z":NaN', 1),
        ]:
            with self.subTest(data=wire[:40]), self.assertRaises(ValueError):
                CandidateCTransport.from_canonical_bytes(wire)
        for name in [
            "mobility",
            "structural_hodge",
            "C",
            "h",
            "history",
            "constructor_id",
        ]:
            data: Any = self.binding.to_payload()
            data[name] = [[2, 0], [0, 5]]
            before = canonical_json_bytes(data)
            with self.subTest(name=name), self.assertRaises(ValueError):
                CandidateCTransport.from_payload(data)
            self.assertEqual(canonical_json_bytes(data), before)

    def test_no_mutable_source_or_output_aliases(self) -> None:
        data: Any = self.binding.to_payload()
        restored = CandidateCTransport.from_payload(data)
        expected = restored.to_canonical_bytes()
        data["profile"]["params_resolved"]["candidate"]["W_C_tr"]["z"] = 19
        projected: Any = restored.to_payload()
        projected["graph"]["live_node_ids"].append("extra")
        descriptor = restored.mobility_constructor_payload
        descriptor["eta_C"] = 0
        self.assertEqual(restored.to_canonical_bytes(), expected)
        self.assertEqual(restored.mobility.diagonal, (6, 15))
        with self.assertRaises(FrozenInstanceError):
            restored.mobility = self.binding.mobility  # type: ignore[misc]
        with self.assertRaises(TypeError):
            restored.params.W_C_tr["z"] = 9  # type: ignore[index]

    def test_wrong_candidate_bare_params_and_graph_duplicates_reject(self) -> None:
        ref = stage_reference_fixture(candidate="A")
        for source in [
            ref.profile,
            self.binding.params,
            self.binding.profile.to_payload(),
            None,
        ]:
            with self.subTest(source=type(source)), self.assertRaises(TypeError):
                CandidateCTransport(self.graph, source)  # type: ignore[arg-type]
        data = graph_payload()
        data["oriented_edges"].append(data["oriented_edges"][0].copy())
        with self.assertRaises(ValueError):
            GRCV4Graph.from_payload(data)
        # Schema requires a nonempty C map; an edgeless target cannot bind it.
        with self.assertRaises(ValueError):
            CandidateCTransport(GRCV4Graph(("isolated",), ()), self.binding.profile)


class CandidateCCaptureTests(unittest.TestCase):
    """Synthetic gate controls; these do not substitute for numeric leaf tests."""

    @contextmanager
    def fixture(
        self,
    ) -> Iterator[tuple[Path, dict[str, ModuleType], Callable[[], dict[str, str]]]]:
        from importlib.machinery import ModuleSpec
        import tempfile
        from unittest.mock import patch

        names = (
            "pygrc.models.grc_v4_geometry",
            "pygrc.models.grc_v4_transport",
            "tests.models.test_grc_v4_geometry",
            "tests.models.test_grc_v4_transport",
            "pygrc.models.grc_v4_candidate_c",
            "tests.models.test_grc_v4_candidate_c",
        )
        source = (
            "from dataclasses import dataclass\n"
            "def mobility(eta, weight):\n    return eta * weight\n"
            "class Probe:\n"
            "    @staticmethod\n    def static():\n        return 1\n"
            "    @classmethod\n    def cls(cls):\n        return 2\n"
            "    @property\n    def value(self):\n        return 3\n"
            "@dataclass(frozen=True)\nclass Generated:\n    value: int\n"
        )
        with tempfile.TemporaryDirectory(prefix="p941-capture-") as folder:
            root = Path(folder).resolve()
            modules = {}
            paths = []
            for name in names:
                prefix = "src/" if name.startswith("pygrc.") else ""
                path = root / (prefix + name.replace(".", "/") + ".py")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source)
                paths.append(path)
                module = ModuleType(name)
                module.__file__ = str(path)
                module.__spec__ = ModuleSpec(name, loader=None, origin=str(path))
                modules[name] = module
            main = ModuleType("__main__")
            leaf = modules[names[-1]]
            main.__file__, main.__spec__ = leaf.__file__, leaf.__spec__
            modules["__main__"] = main
            kept = {
                n: m
                for n, m in sys.modules.items()
                if n not in {"pygrc", "tests", "__main__"}
                and not n.startswith(("tests.", "pygrc.", "grcv4_explorer."))
            }

            def hashes() -> dict[str, str]:
                return {
                    str(path.relative_to(root)): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in paths
                }

            with patch.dict(sys.modules, {**kept, **modules}, clear=True):
                for module in modules.values():
                    exec(
                        compile(
                            source, str(module.__file__), "exec", dont_inherit=True
                        ),
                        module.__dict__,
                    )
                yield root, modules, hashes

    def execute(
        self,
        root: Path,
        hashes: Callable[[], dict[str, str]],
        action: Callable[[], None] = lambda: None,
    ) -> dict[str, Any]:
        case = unittest.FunctionTestCase(action)
        return _p941_execute(
            root, hashes(), {case.id()}, unittest.TestSuite([case]), hashes
        )

    def test_matching_live_sources_and_main_alias_pass(self) -> None:
        with self.fixture() as (root, modules, hashes):
            result = self.execute(root, hashes)
            self.assertEqual(result["status"], "passed", result)
            self.assertEqual(result["results"]["tests_run"], 1)
            self.assertEqual(
                result["loaded_sources_before"], result["loaded_sources_after"]
            )
            self.assertEqual(set(result["loaded_sources_before"]), set(modules))
            self.assertEqual(
                result["loaded_sources_before"]["__main__"][
                    "source_declared_code_objects_checked"
                ],
                4,
            )

    def test_same_path_stale_code_and_main_alias_reject(self) -> None:
        for name in (
            "pygrc.models.grc_v4_candidate_c",
            "tests.models.test_grc_v4_candidate_c",
            "__main__",
        ):
            with self.subTest(module=name), self.fixture() as (root, modules, hashes):
                module = modules[name]
                stale = "def mobility(eta, weight):\n    return weight\n"
                exec(
                    compile(stale, str(module.__file__), "exec", dont_inherit=True),
                    module.__dict__,
                )
                self.assertEqual(module.mobility(3, 2), 2)
                result = self.execute(root, hashes)
                self.assertEqual(result["status"], "failed")
                self.assertIn("code differs", result["capture_error"])
                self.assertTrue(result["source_unchanged"])
                self.assertNotIn("results", result)  # no test execution or reload
                self.assertEqual(module.mobility(3, 2), 2)

    def test_foreign_wrong_local_and_missing_origins_reject(self) -> None:
        from importlib.machinery import ModuleSpec

        for mode in (
            "foreign",
            "wrong_local",
            "wrong_spec",
            "no_spec",
            "no_file",
            "missing_leaf",
            "main_no_spec",
        ):
            with self.subTest(mode=mode), self.fixture() as (root, modules, hashes):
                name = "pygrc.models.grc_v4_candidate_c"
                module = modules[name]
                if mode == "main_no_spec":
                    modules["__main__"].__spec__ = None
                elif mode == "foreign":
                    module.__file__ = str(root.parent / "foreign.py")
                elif mode == "wrong_local":
                    module.__file__ = modules["pygrc.models.grc_v4_transport"].__file__
                    module.__spec__ = ModuleSpec(name, None, origin=module.__file__)
                elif mode == "wrong_spec":
                    module.__spec__ = ModuleSpec(
                        name, None, origin=str(root / "wrong.py")
                    )
                elif mode == "no_spec":
                    module.__spec__ = None
                elif mode == "no_file":
                    del module.__file__
                else:
                    del sys.modules[name]
                result = self.execute(root, hashes)
                self.assertEqual(result["status"], "failed")
                self.assertNotIn("results", result)
                self.assertIn(
                    "mismatch" if mode != "missing_leaf" else "not loaded",
                    result["capture_error"],
                )

    def test_replaced_declared_slots_cannot_hide_as_generated_or_foreign(self) -> None:
        for mode in (
            "generated_filename",
            "foreign_owner",
            "deleted",
            "property_getter",
        ):
            with self.subTest(mode=mode), self.fixture() as (root, modules, hashes):
                module = modules["pygrc.models.grc_v4_candidate_c"]
                if mode == "generated_filename":
                    module.mobility.__code__ = module.mobility.__code__.replace(
                        co_filename="<string>"
                    )
                elif mode == "foreign_owner":
                    module.mobility.__module__ = "foreign"
                elif mode == "deleted":
                    del module.mobility
                else:
                    module.Probe.value = property()
                result = self.execute(root, hashes)
                self.assertEqual(result["status"], "failed")
                self.assertIn("code differs", result["capture_error"])

    def test_disk_change_during_execution_fails(self) -> None:
        for mode in ("edited", "deleted"):
            with self.subTest(mode=mode), self.fixture() as (root, modules, hashes):
                path = Path(str(modules["pygrc.models.grc_v4_candidate_c"].__file__))

                def change() -> None:
                    if mode == "deleted":
                        path.unlink()
                    else:
                        path.write_bytes(
                            path.read_bytes() + b"\n# changed during test\n"
                        )

                result = self.execute(root, hashes, change)
                self.assertEqual(result["results"]["tests_run"], 1)
                self.assertEqual(result["status"], "failed")
                self.assertFalse(result["source_unchanged"])
                if mode == "deleted":
                    self.assertIn("FileNotFoundError", result["source_snapshot_error"])

    def test_postrun_live_changes_and_late_imports_are_checked(self) -> None:
        from importlib.machinery import ModuleSpec

        for mode in ("changed_code", "removed_module", "late_good", "late_stale"):
            with self.subTest(mode=mode), self.fixture() as (root, modules, hashes):
                name = "pygrc.models.grc_v4_candidate_c"
                module = modules[name]
                extra = root / "src/pygrc/models/late_probe.py"
                extra.write_text("def value():\n    return 2\n")

                def snapshot() -> dict[str, str]:
                    return {
                        **hashes(),
                        str(extra.relative_to(root)): hashlib.sha256(
                            extra.read_bytes()
                        ).hexdigest(),
                    }

                def change() -> None:
                    if mode == "changed_code":
                        exec(
                            compile(
                                "def mobility(eta, weight):\n    return weight\n",
                                str(module.__file__),
                                "exec",
                                dont_inherit=True,
                            ),
                            module.__dict__,
                        )
                    elif mode == "removed_module":
                        del sys.modules[name]
                    else:
                        late = ModuleType("pygrc.models.late_probe")
                        late.__file__ = str(extra)
                        late.__spec__ = ModuleSpec(
                            late.__name__, None, origin=str(extra)
                        )
                        source = (
                            extra.read_bytes()
                            if mode == "late_good"
                            else b"def value():\n    return 1\n"
                        )
                        exec(
                            compile(source, str(extra), "exec", dont_inherit=True),
                            late.__dict__,
                        )
                        sys.modules[late.__name__] = late

                result = self.execute(root, snapshot, change)
                self.assertEqual(result["results"]["tests_run"], 1)
                self.assertTrue(result["source_unchanged"])
                self.assertEqual(
                    result["status"],
                    "passed" if mode == "late_good" else "failed",
                    result,
                )
                if mode == "late_good":
                    self.assertNotIn(
                        "pygrc.models.late_probe", result["loaded_sources_before"]
                    )
                    self.assertIn(
                        "pygrc.models.late_probe", result["loaded_sources_after"]
                    )

    def test_roster_and_nonpassing_outcomes_still_reject(self) -> None:
        with self.fixture() as (root, _, hashes):
            for mode in ("empty", "missing", "duplicate", "skip", "failure", "subtest"):
                with self.subTest(mode=mode):

                    class Probe(unittest.TestCase):
                        def test_case(self) -> None:
                            if mode == "skip":
                                self.skipTest("ordinary test_case name")
                            if mode == "failure":
                                self.fail("intentional failure")
                            if mode == "subtest":
                                with self.subTest():
                                    self.fail("intentional subtest failure")

                    case = Probe("test_case")
                    required = (
                        {case.id(), "missing"} if mode == "missing" else {case.id()}
                    )
                    cases = (
                        []
                        if mode == "empty"
                        else [case, Probe("test_case")]
                        if mode == "duplicate"
                        else [case]
                    )
                    result = _p941_execute(
                        root, hashes(), required, unittest.TestSuite(cases), hashes
                    )
                    self.assertEqual(result["status"], "failed", result)
                    self.assertFalse(result["coverage"]["passed"])


_P941_CAPTURE_METHODS = (
    "test_matching_live_sources_and_main_alias_pass",
    "test_same_path_stale_code_and_main_alias_reject",
    "test_foreign_wrong_local_and_missing_origins_reject",
    "test_replaced_declared_slots_cannot_hide_as_generated_or_foreign",
    "test_disk_change_during_execution_fails",
    "test_postrun_live_changes_and_late_imports_are_checked",
    "test_roster_and_nonpassing_outcomes_still_reject",
)


_P941_METHODS = (
    "test_exact_siblings_and_typed_operator_actions",
    "test_equal_matrices_still_have_separate_constructor_identities",
    "test_gain_changes_only_mobility_constructor",
    "test_map_value_and_stable_id_are_identity_inputs",
    "test_unrelated_profile_controls_do_not_condition_reference_constructors",
    "test_all_five_declarations_bind_without_advertising_execution",
    "test_units_declaration_is_part_of_each_typed_constructor_identity",
    "test_complete_reference_geometry_agrees_with_sibling_hodge",
    "test_reference_hodge_mismatch_rejects_even_with_reidentified_profile",
    "test_map_must_cover_exact_target_edges_without_copy_or_resize",
    "test_map_domain_and_gain_reject_without_repair",
    "test_transport_and_constructor_policy_ids_cannot_be_substituted",
    "test_complete_profile_and_map_identity_tampering_rejects",
    "test_binary64_positive_extremes_and_product_boundaries",
    "test_random_scalar_rational_oracle_across_wide_exponents",
    "test_graph_outliers_and_signed_permutation_covariance",
    "test_unicode_and_numeric_looking_edge_ids_roundtrip",
    "test_noncanonical_duplicate_or_extra_wire_authority_rejects",
    "test_no_mutable_source_or_output_aliases",
    "test_wrong_candidate_bare_params_and_graph_duplicates_reject",
)


def _p941_loaded_sources(root: Path, hashes: dict[str, str]) -> dict[str, Any]:
    """Check origins and live source code; not hostile-interpreter attestation."""
    import inspect
    from types import CodeType

    leaf_modules = {
        "pygrc.models.grc_v4_candidate_c",
        "tests.models.test_grc_v4_candidate_c",
    }
    # A local file can still be the wrong module. Bind names to their actual
    # package paths, including the second instance created by `python -m`.
    aliases = {}
    for name, module in tuple(sys.modules.items()):
        spec = getattr(module, "__spec__", None)
        canonical = getattr(spec, "name", None) if name == "__main__" else name
        if name == "__main__" and (
            getattr(module, "__file__", None)
            == str(root / "tests/models/test_grc_v4_candidate_c.py")
            or __name__ == "__main__"
        ):
            canonical = "tests.models.test_grc_v4_candidate_c"
        if not isinstance(canonical, str) or not (
            canonical in {"pygrc", "tests"}
            or canonical.startswith(("pygrc.", "tests.", "grcv4_explorer."))
        ):
            continue
        prefix = "src/" if canonical.split(".")[0] == "pygrc" else ""
        if canonical.startswith("grcv4_explorer."):
            prefix = (
                "implementation/investigations/grc9v4-constitutive-design/"
                "tools/exploratory-side-tool/tool/src/"
            )
        stem = prefix + canonical.replace(".", "/")
        file = getattr(module, "__file__", None)
        path = Path(file).resolve() if file else None
        if path not in {root / (stem + ".py"), root / stem / "__init__.py"}:
            raise RuntimeError("loaded module path mismatch: " + name)
        if spec is None or spec.name != canonical or spec.origin is None:
            raise RuntimeError("loaded module origin mismatch: " + name)
        if Path(spec.origin).resolve() != path:
            raise RuntimeError("loaded module origin mismatch: " + name)
        relative = str(path.relative_to(root))
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if hashes.get(relative) != digest:
            raise RuntimeError("loaded source bytes not in snapshot: " + name)
        if canonical not in leaf_modules and canonical != "pygrc":
            continue

        # Audit source-declared slots, including properties and class/static
        # methods. Generated dataclass methods have no source declaration and
        # are not treated as fresh-compiled source. Nested function code is
        # compared recursively as part of its enclosing function's code object.
        codes: list[CodeType] = []

        def collect(code: CodeType) -> None:
            if "<" not in code.co_qualname:
                codes.append(code)
            for item in code.co_consts:
                if isinstance(item, CodeType):
                    collect(item)

        collect(compile(data, str(path), "exec", dont_inherit=True))
        checked = 0
        for code in codes:
            obj: Any = module
            for part in code.co_qualname.split("."):
                obj = inspect.getattr_static(obj, part, None)
            if inspect.isclass(obj):
                if obj.__module__ != name:
                    raise RuntimeError("loaded class owner mismatch: " + name)
                continue
            if isinstance(obj, (classmethod, staticmethod)):
                obj = obj.__func__
            candidates = (
                (obj.fget, obj.fset, obj.fdel) if isinstance(obj, property) else (obj,)
            )
            if not any(
                callable(candidate)
                and inspect.isfunction(live := inspect.unwrap(candidate))
                and live.__module__ == name
                and live.__code__.co_filename == str(path)
                and live.__code__.co_qualname == code.co_qualname
                and live.__code__ == code
                for candidate in candidates
            ):
                raise RuntimeError(
                    "loaded code differs from snapshot: "
                    + name
                    + "."
                    + code.co_qualname
                )
            checked += 1
        aliases[name] = {
            "path": relative,
            "sha256": digest,
            "source_declared_code_objects_checked": checked,
        }
    loaded = _p934_loaded_sources(root, hashes)
    for name in leaf_modules:
        if name not in loaded:
            raise RuntimeError("required leaf module not loaded: " + name)
    loaded.update(aliases)
    return loaded


def _p941_execute(
    root: Path,
    before: dict[str, str],
    required: set[str],
    suite: unittest.TestSuite,
    source_hashes: Callable[[], dict[str, str]],
) -> dict[str, Any]:
    """The same before/run/after gate serves full and explicitly focused runs."""
    import io
    import time
    from typing import cast

    record: dict[str, Any] = {"status": "failed"}
    stream = io.StringIO()
    start = time.monotonic()
    try:
        names = _p934_ids(suite)
        record["coverage"] = _p934_coverage(required, names)
        if not record["coverage"]["passed"]:
            raise RuntimeError("discovery differs from the independently pinned roster")
        record["loaded_sources_before"] = _p941_loaded_sources(root, before)
        result = cast(
            _P934Result,
            unittest.TextTestRunner(stream=stream, resultclass=_P934Result).run(suite),
        )
        record["coverage"] = _p934_coverage(required, names, result.rows)
        record["results"] = {
            "tests_run": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skips": len(result.skipped),
            "nonpassing_methods": [r for r in result.rows if r["status"] != "passed"],
            "executed_ids_sha256": hashlib.sha256(
                canonical_json_bytes(sorted(r["test"] for r in result.rows))
            ).hexdigest(),
        }
        record["loaded_sources_after"] = _p941_loaded_sources(root, before)
        if any(
            record["loaded_sources_after"].get(name) != row
            for name, row in record["loaded_sources_before"].items()
        ):
            raise RuntimeError("loaded sources disappeared or changed during execution")
        if (
            result.wasSuccessful()
            and not result.skipped
            and result.testsRun == len(names)
            and record["coverage"]["passed"]
        ):
            record["status"] = "passed"
    except Exception as exc:
        record["capture_error"] = type(exc).__name__ + ": " + str(exc)
    finally:
        try:
            record["source_unchanged"] = before == source_hashes()
        except Exception as exc:
            record["source_unchanged"] = False
            record["source_snapshot_error"] = type(exc).__name__ + ": " + str(exc)
        if not record["source_unchanged"]:
            record["status"] = "failed"
        record["elapsed_seconds"] = round(time.monotonic() - start, 3)
    if record["status"] != "passed":
        record["failure_output"] = stream.getvalue().replace(str(root), "<checkout>")
    return record


def capture_p941(output: str, *, scope: str = "full") -> int:
    """One manifest; source is recovered from Git, without copying source blobs.

    The inherited pinned method roster and audited result collector detect
    omission, duplicates, skips and subtest failures. All source bytes are
    observed before/after, with only this leaf's two overrides over its base.
    """
    from datetime import datetime, timezone
    import importlib.metadata
    import os
    import platform
    import subprocess
    from tests.models.test_grc_v4_step import p935_required

    if scope not in {"full", "focused"}:
        raise ValueError("unknown capture scope")
    root = Path(__file__).resolve().parents[2]
    destination = (root / output).resolve()
    if not destination.is_relative_to(
        root
        / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated"
    ):
        raise ValueError(
            "capture destination must be inside the side tool generated directory"
        )
    wheelhouse = (root / os.environ.get("GRCV4_WHEELHOUSE", "<missing>")).resolve()
    if scope == "full" and (
        os.environ.get("GRCV4_PACKAGE_TESTS") != "1"
        or not wheelhouse.is_relative_to(root)
        or not wheelhouse.is_dir()
    ):
        raise ValueError(
            "full capture requires enabled package tests and repository-local dependency wheels"
        )
    base = subprocess.check_output(
        ["git", "rev-parse", "2e90398"], cwd=root, text=True
    ).strip()
    scopes = [
        "src",
        "tests",
        "specs",
        "pyproject.toml",
        "uv.lock",
        "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
    ]
    overrides = {
        "src/pygrc/models/grc_v4_candidate_c.py",
        "tests/models/test_grc_v4_candidate_c.py",
    }

    def source_hashes() -> dict[str, str]:
        names = set(
            subprocess.check_output(
                [
                    "git",
                    "ls-files",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                    "--",
                    *scopes,
                ],
                cwd=root,
                text=True,
            ).splitlines()
        )
        return {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in sorted(names)
        }

    before = source_hashes()
    # Git diff also sees staged changes, while the explicit overrides cover
    # this leaf's new files before they have been staged.
    changed = set(
        subprocess.check_output(
            ["git", "diff", "--name-only", base, "--", *scopes], cwd=root, text=True
        ).splitlines()
    )
    untracked = set(
        subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard", "--", *scopes],
            cwd=root,
            text=True,
        ).splitlines()
    )
    if (changed | untracked) != overrides:
        raise ValueError(
            "capture source differs from the two reviewed P9-4.1 overrides"
        )
    inherited = p935_required(root)
    if scope == "focused":
        inherited = {
            name
            for name in inherited
            if name.startswith(
                (
                    "tests.models.test_grc_v4_geometry.CaptureIntegrityTests.",
                    "tests.models.test_grc_v4_transport.MobilityTests.",
                )
            )
        }
    required = (
        inherited
        | {
            "tests.models.test_grc_v4_candidate_c.CandidateCReferenceTests." + name
            for name in _P941_METHODS
        }
        | {
            "tests.models.test_grc_v4_candidate_c.CandidateCCaptureTests." + name
            for name in _P941_CAPTURE_METHODS
        }
    )
    suite = (
        unittest.defaultTestLoader.discover(
            str(root / "tests"), top_level_dir=str(root)
        )
        if scope == "full"
        else unittest.defaultTestLoader.loadTestsFromNames(sorted(required))
    )
    destination.mkdir(parents=True, exist_ok=False)
    record: dict[str, Any] = {
        "schema": "phase9_leaf_run_v1",
        "iteration_id": "P9-4.1",
        "scope": scope,
        "status": "running",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "base_commit": base,
            "scopes": scopes,
            "overrides_sha256": {n: before[n] for n in sorted(overrides)},
            "manifest_sha256": hashlib.sha256(canonical_json_bytes(before)).hexdigest(),
            "file_count": len(before),
            "reconstruction": "Recover the two override files from the Git commit containing this record (or a later commit with matching hashes), overlay on base_commit, and verify the manifest hash. No uncommitted source blob is preserved separately.",
        },
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": sorted(
            f"{d.metadata['Name']}=={d.version}"
            for d in importlib.metadata.distributions()
        ),
        "environment": {
            "GRCV4_PACKAGE_TESTS": os.environ.get("GRCV4_PACKAGE_TESTS"),
            "GRCV4_WHEELHOUSE": str(wheelhouse.relative_to(root))
            if wheelhouse.is_relative_to(root) and wheelhouse.is_dir()
            else None,
            **{
                key: os.environ.get(key)
                for key in ["PYTHONHASHSEED", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"]
            },
        },
        "wheel_requirements": sorted(p.name for p in wheelhouse.glob("*.whl"))
        if scope == "full"
        else [],
        "replay_command": [
            ".venv/bin/python",
            "-m",
            "tests.models.test_grc_v4_candidate_c",
            "--capture-p941" if scope == "full" else "--capture-p941-focused",
            "<fresh-repository-relative-generated-directory>",
        ],
        "claim_ceiling": "Reference transport constructors only; no selector, baseline flux, solve, beat, lifecycle or runtime conformance.",
    }
    record["required_ids"] = sorted(required)
    record.update(_p941_execute(root, before, required, suite, source_hashes))
    passed = record["status"] == "passed"
    if passed:
        loaded_before = record.pop("loaded_sources_before")
        loaded_after = record.pop("loaded_sources_after")
        record["loaded_sources"] = {
            "before": loaded_before,
            "added_after": {
                name: row
                for name, row in loaded_after.items()
                if name not in loaded_before
            },
            "before_rechecked_after": True,
        }
    record["live_source_check_limits"] = (
        "Before/after source, origin and applicable live-code checks detect stale or "
        "wrong local code. They do not attest a hostile interpreter, transient "
        "changes restored between checkpoints, arbitrary globals/default values, "
        "generated dataclass methods, or native dependency internals. Source-declared "
        "leaf slots and the python -m alias are checked explicitly."
    )
    record["completed_utc"] = datetime.now(timezone.utc).isoformat()
    (destination / "run.json").write_text(
        json.dumps(record, indent=2, allow_nan=False) + "\n"
    )
    print(
        json.dumps(
            {
                "status": record["status"],
                **record.get("results", {}),
                "capture_error": record.get("capture_error"),
                "source_unchanged": record["source_unchanged"],
            }
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in {
        "--capture-p941",
        "--capture-p941-focused",
    }:
        raise SystemExit(
            capture_p941(
                sys.argv[2],
                scope="focused" if sys.argv[1].endswith("-focused") else "full",
            )
        )
    unittest.main()

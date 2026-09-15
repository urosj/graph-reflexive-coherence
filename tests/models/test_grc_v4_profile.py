"""Profile declaration/identity checks, not ten-profile runtime conformance."""

from __future__ import annotations

from collections.abc import Callable
from copy import copy, deepcopy
from dataclasses import FrozenInstanceError
from hashlib import sha256
import json
import math
from pathlib import Path
import operator
from typing import Any
import unittest

from pygrc.models.grc_v4_codec import (
    V4IdentityError, V4SchemaError, V4WireError, canonical_json_bytes,
    payload_identity,
)
from pygrc.models.grc_v4_profile import (
    CandidateAParams, CandidateCParams, GRCV4CommonParams,
    GRCV4Profile, GRCV4ProfileIdentityPayload, GRCV4ProfileTemplate,
    GRCV4ResolvedParams, get_supported_profile, list_supported_profiles,
    resolve_parameters, resolve_profile, resolve_profile_template,
    validate_profile_references,
)

ROOT = Path(__file__).resolve().parents[2]


def bundle() -> dict[str, Any]:
    value = json.loads((ROOT / "specs/grc-v4-conformance-vectors.json").read_text())
    assert isinstance(value, dict)
    return value


def fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    rows = bundle()["identity_vectors"]
    return deepcopy(rows[0]["payload"]), deepcopy(rows[1]["payload"])


def reidentify(params: dict[str, Any], identity: dict[str, Any]) -> None:
    # This helper creates *mutated inputs* only, never an expected digest.
    identity["params_hash"] = payload_identity("resolved_params", params)


def family_fixture(candidate: str, realization: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Explicit synthetic parameter examples, not certified numerical domains."""
    params, identity = fixture()
    if candidate == "A":
        params["candidate"] = {
            "schema_version": "grcv4-candidate-a-params-v1",
            "eta": 1, "kappa_c": 0, "site_potential_id": "test_site_potential_v1",
            "W_floor": 0.1, "alpha": 1, "beta": 1, "gamma": 1, "kappa_Ah": 0,
            "chi_A": 1, "zeta_A": 1, "tau_A": 1,
            "descriptor_backend_id": "test_descriptor_v1",
            "conductance_evaluator_id": "curvature_disabled_G_W_v1",
        }
        params["lifecycle"]["history_policy_id"] = "test_retained_a_history_v1"
        params["geometry"]["candidate_adapter_id"] = "test_a_adapter_v1"
    ci = {
        "schema_version": "grcv4-ci-params-v1",
        "contraction_domain_id": "test_contraction_v1",
        "root_selector_id": "unique_admitted_root_v1",
        "iteration_limit": 10, "residual_norm_id": "edge_l2_v1", "tolerance": 0,
    }
    pc = {
        "schema_version": "grcv4-pc-params-v1", "tau_PC": 1, "radius": 1,
        "carrier_norm_id": "test_norm_v1", "source_envelope_id": "test_envelope_v1",
        "writer_id": "zero_order_hold_exponential_v1",
    }
    if realization == "CI":
        params["realization"] = ci
    elif realization == "PC":
        params["realization"] = pc
    elif realization == "CI+PC":
        params["realization"] = {
            **ci, **pc, "schema_version": "grcv4-cipc-params-v1", "rho_inst": 1,
        }
    elif realization == "RG2b":
        params["realization"] = {
            "schema_version": "grcv4-rg2b-params-v1",
            "extension_evaluator_id": "test_evaluator_v1",
            "approximation_policy_id": "test_approximation_v1",
            "error_norm_id": "test_norm_v1", "error_tolerance": 0,
            "containment_certificate_id": "test_certificate_v1",
            "iteration_limit": 10, "failure_policy_id": "fail_closed_on_uncertified_section_v1",
        }
    identity.update(
        profile_family_id=f"{candidate}_{realization.replace('+', '_')}",
        candidate=candidate, realization=realization,
        candidate_c_transport_id=(
            "C-HM-STIFFNESS-BASELINE-v1" if candidate == "C" else None
        ), composition_gain=2 if realization == "CI+PC" else None,
    )
    reidentify(params, identity)
    return params, identity


class ProfileTests(unittest.TestCase):
    def test_full_profile_canonical_roundtrip_preserves_identity_and_types(self) -> None:
        values = [float(2**53 - 1), float(2**53), 1e16, 1e20, 2.0**68,
                  math.nextafter(1e21, 0), 1e21, math.nextafter(1e21, math.inf),
                  5e-324, -5e-324, -1e20, -1e21, 1.7976931348623157e308]
        for value in values:
            params, identity = fixture()
            params["candidate"]["kappa_Phi_C"] = value
            params["solver"]["iteration_limit"] = 10.0
            reidentify(params, identity)
            original = resolve_profile(params, identity)
            restored = GRCV4Profile.from_canonical_bytes(original.to_canonical_bytes())
            with self.subTest(value=value):
                self.assertEqual(restored, original)
                self.assertEqual(restored.to_canonical_bytes(), original.to_canonical_bytes())
                self.assertEqual(restored.complete_profile_id, original.complete_profile_id)
                self.assertEqual(operator.index(restored.params_resolved.solver.iteration_limit), 10)

    def test_profile_canonical_restoration_rejects_forgery_and_extra_fields(self) -> None:
        profile = resolve_profile(*fixture())
        for mode in ["extra", "missing", "wrong_id", "boolean_id", "stale_params"]:
            data = profile.to_payload()
            if mode == "extra":
                data["arbitrary"] = 1
            elif mode == "missing":
                del data["complete_profile_id"]
            elif mode == "wrong_id":
                data["complete_profile_id"] = "grcv4-profile-sha256:" + "0" * 64
            elif mode == "boolean_id":
                data["complete_profile_id"] = True
            else:
                data["params_resolved"] = {}
            with self.subTest(mode=mode), self.assertRaises((V4SchemaError, V4IdentityError)):
                GRCV4Profile.from_canonical_bytes(canonical_json_bytes(data))

    def test_integral_fields_resolve_identically_through_every_constructor(self) -> None:
        from pygrc.models import grc_v4_profile as p

        for realization, section in [("CI", "realization"), ("RG2b", "realization"),
                                     ("CI+PC", "realization"), ("OS", "solver")]:
            for number in [1, 1.0, 10, 10.0, float(2**53 - 1)]:
                params, identity = family_fixture("C", realization)
                params[section]["iteration_limit"] = number
                reidentify(params, identity)
                kind = p._PARAMETER_CLASSES[params[section]["schema_version"]]
                records = [kind.from_payload(params[section]), kind(**params[section]),
                           getattr(resolve_parameters(params), section),
                           getattr(resolve_profile(params, identity).params_resolved, section)]
                expected = deepcopy(params)
                expected[section]["iteration_limit"] = int(number)
                for record in records:
                    with self.subTest(realization=realization, number=number):
                        value = getattr(record, "iteration_limit")
                        self.assertIs(type(value), int)
                        self.assertEqual(operator.index(value), int(number))
                        self.assertEqual(canonical_json_bytes(record.to_payload()),
                                         canonical_json_bytes(expected[section]))
                expected_identity = deepcopy(identity)
                reidentify(expected, expected_identity)
                self.assertEqual(resolve_profile(params, identity),
                                 resolve_profile(expected, expected_identity))

    def test_integral_resolution_does_not_truncate_or_admit_booleans(self) -> None:
        from pygrc.models import grc_v4_profile as p

        for realization, section in [("CI", "realization"), ("RG2b", "realization"),
                                     ("CI+PC", "realization"), ("OS", "solver")]:
            for number in [True, False, 1.5, 0, -1, -0.0, 2**53, float(2**53),
                           float("nan"), float("inf")]:
                params, _ = family_fixture("C", realization)
                params[section]["iteration_limit"] = number
                kind = p._PARAMETER_CLASSES[params[section]["schema_version"]]
                constructors: list[Callable[[], object]] = [
                    lambda: kind.from_payload(params[section]),
                    lambda: kind(**params[section]),
                    lambda: resolve_parameters(params)]
                for construct in constructors:
                    with self.subTest(realization=realization, number=number):
                        with self.assertRaises((V4SchemaError, V4WireError)):
                            construct()
        params, _ = family_fixture("C", "CI+PC")
        params["realization"]["rho_inst"] = 1.0
        self.assertIs(type(getattr(resolve_parameters(params).realization, "rho_inst")), int)
        candidate = resolve_parameters(params).candidate
        assert isinstance(candidate, CandidateCParams)
        self.assertIs(type(candidate.chi_C), int)
        params["candidate"]["chi_C"] = 0.125
        candidate = resolve_parameters(params).candidate
        assert isinstance(candidate, CandidateCParams)
        self.assertEqual(candidate.chi_C, 0.125)

    def test_reference_values_must_match_without_repair_or_mobility_transfer(self) -> None:
        k4 = next(r["payload"] for r in bundle()["subdigest_identity_vectors"]
                  if r["vector_id"] == "SUBDIGEST-K4-BASE")
        weights = {f"old-{i}": i / 4 for i in range(1, 10)}
        for realization in ["CI", "OS", "RG2b", "PC", "CI+PC"]:
            for mode in ["match", "rehash_conflict", "mobility_scaled"]:
                params, identity = family_fixture("C", realization)
                params["candidate"]["W_C_tr"] = deepcopy(weights)
                params["candidate"]["W_C_tr_content_digest"] = payload_identity(
                    "wctr_identity_payload", {"schema_version": "grcv4-wctr-identity-v1",
                                             "W_C_tr": weights})
                hodge: dict[str, Any] = {
                    "schema_version": "grcv4-reference-hodge-identity-v1",
                    "edge_weights": deepcopy(weights)}
                if mode == "rehash_conflict":
                    hodge["edge_weights"]["old-1"] = 17
                elif mode == "mobility_scaled":
                    hodge["edge_weights"] = {edge: value * params["candidate"]["eta_C"]
                                            for edge, value in weights.items()}
                params["geometry"]["reference_hodge_digest"] = payload_identity(
                    "reference_hodge_identity_payload", hodge)
                reidentify(params, identity)
                profile = resolve_profile(params, identity)
                before = canonical_json_bytes([profile.to_payload(), hodge])
                def check() -> None:
                    validate_profile_references(profile, live_edge_ids=list(reversed(weights)),
                                                k4_preimage=k4, reference_hodge_preimage=hodge)
                with self.subTest(realization=realization, mode=mode):
                    if mode == "match":
                        check()
                    else:
                        with self.assertRaisesRegex(V4IdentityError, "reference.*weights"):
                            check()
                    self.assertEqual(before, canonical_json_bytes([profile.to_payload(), hodge]))

    def test_published_c_os_exact_resolution_and_roundtrip(self) -> None:
        params, identity = fixture()
        expected = bundle()["identity_vectors"][1]["expected_identifier"]
        profile = resolve_profile(params, identity, expected_complete_profile_id=expected)
        self.assertEqual(profile.complete_profile_id, expected)
        self.assertEqual(profile.params_resolved.to_payload(), params)
        self.assertEqual(profile.identity_payload.to_payload(), identity)
        self.assertIsInstance(profile.params_resolved.candidate, CandidateCParams)
        self.assertEqual(profile, resolve_profile(
            profile.to_payload()["params_resolved"],
            profile.to_payload()["identity_payload"],
        ))

    def test_all_ten_declared_shapes_not_executable_support(self) -> None:
        for candidate in ["A", "C"]:
            for realization in ["CI", "OS", "RG2b", "PC", "CI+PC"]:
                with self.subTest(candidate=candidate, realization=realization):
                    params, identity = family_fixture(candidate, realization)
                    profile = resolve_profile(params, identity)
                    self.assertEqual(profile.params_resolved.to_payload(), params)
                    self.assertEqual(profile.identity_payload.realization, realization)
                    self.assertIsInstance(profile.params_resolved.candidate,
                                          CandidateAParams if candidate == "A"
                                          else CandidateCParams)
                    with self.assertRaises(V4IdentityError):
                        get_supported_profile(profile.complete_profile_id)
        self.assertEqual(list_supported_profiles(), frozenset({'grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d', 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4', 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946', 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e', 'grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75', 'grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f', 'grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689', 'grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b', 'grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b'}))

    def test_every_required_parameter_and_unknown_field(self) -> None:
        for candidate, realization in [("A", "CI+PC"), ("C", "OS"), ("C", "RG2b")]:
            original, _ = family_fixture(candidate, realization)
            for section, values in original.items():
                if not isinstance(values, dict):
                    continue
                for name in [*values, "unexpected"]:
                    params = deepcopy(original)
                    if name == "unexpected":
                        params[section][name] = 1
                    else:
                        del params[section][name]
                    with self.subTest(section=section, field=name):
                        with self.assertRaises(V4SchemaError):
                            resolve_parameters(params)
        params, _ = fixture()
        del params["common"]
        with self.assertRaises(V4SchemaError):
            resolve_parameters(params)

    def test_no_environment_or_implicit_numeric_defaults(self) -> None:
        params, _ = fixture()
        del params["common"]["default_step_request"]
        with self.assertRaises(V4SchemaError):
            resolve_parameters(params)
        params, _ = fixture()
        del params["candidate"]["eta_C"]
        with self.assertRaises(V4SchemaError):
            resolve_parameters(params)

    def test_forbidden_numbers_and_adapter_scalars(self) -> None:
        for value in [True, False, float("nan"), float("inf"), -0.0, 2**53, "1", None]:
            params, _ = fixture()
            params["candidate"]["eta_C"] = value
            with self.subTest(value=value):
                with self.assertRaises((V4SchemaError, V4WireError)):
                    resolve_parameters(params)
        for candidate, realization, key in [
            ("A", "OS", "tau_A"), ("A", "OS", "W_floor"),
            ("C", "OS", "eta_C"), ("C", "OS", "C_ref"),
        ]:
            params, _ = family_fixture(candidate, realization)
            params["candidate"][key] = 0
            with self.assertRaises(V4SchemaError):
                resolve_parameters(params)

    def test_each_realization_rejects_noncanonical_policy(self) -> None:
        cases = [
            ("CI", "root_selector_id", "choose_arbitrary_root"),
            ("OS", "corrector_policy_id", "two_correctors"),
            ("RG2b", "failure_policy_id", "fallback"),
            ("PC", "writer_id", "euler"),
            ("CI+PC", "rho_inst", 0),
            ("CI+PC", "rho_inst", True),
        ]
        for realization, key, value in cases:
            params, _ = family_fixture("C", realization)
            params["realization"][key] = value
            with self.subTest(realization=realization, key=key):
                with self.assertRaises(V4SchemaError):
                    resolve_parameters(params)

    def test_exact_discriminants_and_prohibited_successors(self) -> None:
        for field, value in [
            ("candidate", "B"), ("profile_family_id", "B_OS"),
            ("realization", "CI_PC"), ("candidate", "A"),
            ("profile_family_id", "C_CI"), ("candidate_c_transport_id", None),
            ("composition_gain", 2),
        ]:
            params, identity = fixture()
            identity[field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaises(V4SchemaError):
                    resolve_profile(params, identity)
        params, identity = family_fixture("C", "CI+PC")
        for gain in [0, 1, True, 3]:
            identity["composition_gain"] = gain
            with self.assertRaises(V4SchemaError):
                resolve_profile(params, identity)

    def test_schema_valid_cross_record_disagreement(self) -> None:
        params, _ = family_fixture("A", "OS")
        _, identity = fixture()
        reidentify(params, identity)
        with self.assertRaisesRegex(V4IdentityError, "candidate/realization"):
            resolve_profile(params, identity)
        for field in ["differential_backend_id", "context_contract_id", "units_id",
                      "gauge_id", "normalization_id", "domain_id"]:
            params, identity = fixture()
            identity[field] = "different_v1"
            with self.subTest(field=field):
                with self.assertRaises(V4IdentityError):
                    resolve_profile(params, identity)

    def test_all_trajectory_sections_change_parameter_identity(self) -> None:
        fields = {
            "common": "domain_id", "candidate": "chi_C", "realization": "tolerance",
            "geometry": "kappa_H", "solver": "conditioning_limit",
            "charge": "absolute_tolerance", "lifecycle": "history_policy_id",
        }
        original, original_identity = fixture()
        for section, field in fields.items():
            params, identity = fixture()
            old = params[section][field]
            params[section][field] = old + 1 if isinstance(old, (int, float)) else old + "_2"
            with self.subTest(section=section):
                with self.assertRaises(V4IdentityError):
                    resolve_profile(params, identity)
                if section == "common":
                    identity[field] = params[section][field]
                reidentify(params, identity)
                changed = resolve_profile(params, identity)
                self.assertNotEqual(changed.complete_profile_id,
                                    resolve_profile(original, original_identity).complete_profile_id)

    def test_published_semantic_parameter_digest_negative(self) -> None:
        row = next(r for r in bundle()["semantic_admission"]["negative_vectors"]
                   if r["invariant"] == "identity_payload_matches_resolved_parameters")
        data = row["input"]
        with self.assertRaises(V4IdentityError):
            resolve_profile(data["resolved_params"], data["profile_identity"])

    def test_candidate_c_map_digest_and_transport_cannot_be_inferred(self) -> None:
        for key, value in [
            ("W_C_tr", {"different-edge": 1}), ("W_C_tr", [1] * 9),
            ("transport_id", "H1_as_mobility"),
            ("E_H_policy_id", "eta_C_diag_W_C_tr_mobility_v1"),
            ("E_M_policy_id", "diag_W_C_tr_structural_hodge_v1"),
        ]:
            params, _ = fixture()
            params["candidate"][key] = value
            with self.subTest(key=key):
                with self.assertRaises((V4SchemaError, V4IdentityError)):
                    resolve_parameters(params)
        for invalid_weight in [0, -1, True]:
            params, _ = fixture()
            params["candidate"]["W_C_tr"]["old-1"] = invalid_weight
            with self.assertRaises(V4SchemaError):
                resolve_parameters(params)

    def test_referenced_content_and_stable_edge_coverage(self) -> None:
        params, identity = fixture()
        profile = resolve_profile(params, identity)
        rows = {r["vector_id"]: r["payload"] for r in bundle()["subdigest_identity_vectors"]}
        kwargs: dict[str, Any] = {
            "live_edge_ids": list(params["candidate"]["W_C_tr"]),
            "k4_preimage": rows["SUBDIGEST-K4-BASE"],
            "reference_hodge_preimage": rows["SUBDIGEST-REFERENCE-HODGE"],
        }
        validate_profile_references(profile, **kwargs)
        for roster in [kwargs["live_edge_ids"][:-1],
                       kwargs["live_edge_ids"] + ["extra"],
                       kwargs["live_edge_ids"] + ["old-1"], "old-1"]:
            with self.assertRaises((V4SchemaError, V4IdentityError)):
                validate_profile_references(profile, **{**kwargs, "live_edge_ids": roster})
        changed = deepcopy(kwargs)
        changed["k4_preimage"]["K4_base"][0][0] += 1
        with self.assertRaises(V4IdentityError):
            validate_profile_references(profile, **changed)

    def test_published_wctr_live_edge_negative(self) -> None:
        row = next(r for r in bundle()["semantic_admission"]["negative_vectors"]
                   if r["invariant"] == "target_W_C_tr_matches_live_edges")
        params, identity = fixture()
        params["candidate"]["W_C_tr"] = row["input"]["target_W_C_tr"]
        params["candidate"]["W_C_tr_content_digest"] = payload_identity(
            "wctr_identity_payload", {"schema_version": "grcv4-wctr-identity-v1",
                                     "W_C_tr": params["candidate"]["W_C_tr"]})
        graph = row["input"]["target_graph"]
        expected_edges = [edge["edge_id"] for edge in graph["edges"]]
        hodge = {"schema_version": "grcv4-reference-hodge-identity-v1",
                 "edge_weights": {edge: 1 for edge in expected_edges}}
        params["geometry"]["reference_hodge_digest"] = payload_identity(
            "reference_hodge_identity_payload", hodge)
        reidentify(params, identity)
        profile = resolve_profile(params, identity)
        k4 = next(r["payload"] for r in bundle()["subdigest_identity_vectors"]
                  if r["vector_id"] == "SUBDIGEST-K4-BASE")
        with self.assertRaisesRegex(V4IdentityError, "target_W_C_tr_matches_live_edges"):
            validate_profile_references(profile, live_edge_ids=expected_edges,
                                        k4_preimage=k4, reference_hodge_preimage=hodge)

    def test_deep_immutability_explicit_projection_and_copy(self) -> None:
        params, identity = fixture()
        params["common"]["default_step_request"] = {
            "schema_version": "grcv4-step-request-v1", "operation_id": "default",
            "dt": 0.1, "context_value": {"x": [True, {"n": 1}]},
            "boundary_input": None, "external_source": None,
        }
        reidentify(params, identity)
        profile = resolve_profile(params, identity)
        before = canonical_json_bytes(profile.to_payload())
        params["common"]["default_step_request"]["context_value"]["x"].clear()
        params["candidate"]["W_C_tr"].clear()
        identity.clear()
        detached = profile.to_payload()
        detached.clear()
        self.assertEqual(before, canonical_json_bytes(profile.to_payload()))
        for value in [profile, profile.params_resolved, profile.params_resolved.candidate,
                      profile.identity_payload]:
            with self.assertRaises((FrozenInstanceError, AttributeError, TypeError)):
                setattr(value, "schema_version", "different")
            self.assertEqual(copy(value), value)
            self.assertEqual(deepcopy(value), value)

    def test_nested_boolean_identity_does_not_use_python_equality(self) -> None:
        params, _ = fixture()
        common = params["common"]
        common["default_step_request"] = {
            "schema_version": "grcv4-step-request-v1", "operation_id": "default",
            "dt": 0, "context_value": {"value": True},
            "boundary_input": None, "external_source": None,
        }
        a = GRCV4CommonParams.from_payload(common)
        common["default_step_request"]["context_value"]["value"] = 1
        b = GRCV4CommonParams.from_payload(common)
        self.assertNotEqual(a, b)
        self.assertEqual(len({a, b}), 2)

    def test_template_identity_discriminants_and_source(self) -> None:
        rows = bundle()["identity_vectors"]
        for row in [r for r in rows if r["schema_ref"] == "#/$defs/profile_template_payload"]:
            template = GRCV4ProfileTemplate.from_payload(row["payload"])
            self.assertEqual(template.profile_template_id, row["expected_identifier"])
            changed = deepcopy(row["payload"])
            changed["topology_dependent_map_policy_id"] = "arbitrary_map"
            with self.assertRaises(V4SchemaError):
                GRCV4ProfileTemplate.from_payload(changed)
        source = resolve_profile(*fixture())
        c_row = rows[2]
        self.assertEqual(resolve_profile_template(c_row["payload"], source=source).profile_template_id,
                         c_row["expected_identifier"])
        wrong = deepcopy(c_row["payload"])
        wrong["source_complete_profile_id"] = "grcv4-profile-sha256:" + "0" * 64
        with self.assertRaises(V4IdentityError):
            resolve_profile_template(wrong, source=source)

    def test_direct_profile_constructor_cannot_skip_identity_validation(self) -> None:
        params, identity = fixture()
        with self.assertRaises(V4IdentityError):
            GRCV4Profile(GRCV4ProfileIdentityPayload.from_payload(identity),
                         GRCV4ResolvedParams.from_payload(params),
                         "grcv4-profile-sha256:" + "0" * 64)
        with self.assertRaises(V4SchemaError):
            GRCV4ResolvedParams("grcv4-resolved-params-v1", **{
                k: v for k, v in params.items() if k != "schema_version"
            })

    def test_nested_default_is_identity_bearing_and_has_no_event(self) -> None:
        params, identity = fixture()
        params["common"]["default_step_request"] = {
            "schema_version": "grcv4-step-request-v1", "operation_id": "default",
            "dt": 0, "context_value": {}, "boundary_input": None, "external_source": None,
        }
        with self.assertRaises(V4IdentityError):
            resolve_profile(params, identity)
        params["common"]["default_step_request"]["topology_event"] = {}
        with self.assertRaises(V4SchemaError):
            resolve_parameters(params)

    def test_profile_digest_has_no_self_reference(self) -> None:
        params, identity = fixture()
        profile = resolve_profile(params, identity)
        self.assertNotIn("params_hash", params)
        self.assertNotIn("complete_profile_id", identity)
        self.assertEqual(profile.complete_profile_id.split(":")[1],
                         sha256(canonical_json_bytes(identity)).hexdigest())


class AcceptedG2RegistryTests(unittest.TestCase):
    """The accepted exact declaration is discoverable without widening scope."""

    accepted_id = "grcv4-profile-sha256:a6b853ee382895eb78b1a7955a0df22f95d68b27cb0f762503e8c424c2f59b6d"

    def test_lossless_accepted_declaration_matches_retained_execution(self) -> None:
        phase = ROOT / "implementation/phase-9-grcv4"
        acceptance = json.loads((phase / "tranche-4/P9-4.8B-G2Acceptance.json").read_text())
        run = json.loads((ROOT / acceptance["fixture_run"]["path"]).read_text())
        prestate = run["objects"][acceptance["fixture_run"]["nominated_prestate_object"]]
        profile = get_supported_profile(self.accepted_id)
        self.assertEqual(list_supported_profiles(), frozenset({self.accepted_id, 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4', 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946', 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e', 'grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75', 'grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f', 'grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689', 'grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b', 'grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b'}))
        self.assertEqual(acceptance["accepted_generic_runtime_support"], [self.accepted_id])
        self.assertEqual(profile.to_payload(), acceptance["accepted_profile"])
        self.assertEqual(profile.to_payload(), prestate["reference"]["profile"])
        self.assertEqual(GRCV4Profile.from_canonical_bytes(profile.to_canonical_bytes()), profile)

    def test_registry_is_immutable_and_resolution_does_not_promote_other_profiles(self) -> None:
        profile = get_supported_profile(self.accepted_id)
        detached = profile.to_payload()
        detached.clear()
        again = get_supported_profile(self.accepted_id)
        self.assertEqual(again, profile)
        self.assertIsNot(again, profile)
        with self.assertRaises((FrozenInstanceError, AttributeError, TypeError)):
            profile.complete_profile_id = "C_OS"
        for candidate in ("A", "C"):
            for realization in ("CI", "OS", "RG2b", "PC", "CI+PC"):
                declared = resolve_profile(*family_fixture(candidate, realization))
                with self.assertRaises(V4IdentityError):
                    get_supported_profile(declared.complete_profile_id)
        self.assertEqual(list_supported_profiles(), frozenset({self.accepted_id, 'grcv4-profile-sha256:e4c04a83240a33d77c50a26ca6effbb6ce142774bd01f0966861dd517a94e2c4', 'grcv4-profile-sha256:16ed65f7f65d4716e1be3e384f6fa0f957d26dd7b7a3f7e1b43ad1aa3f250946', 'grcv4-profile-sha256:a56ef981821478cc50a3551a914dd6240e0dc62c9ca69d52305bd59a3405f69e', 'grcv4-profile-sha256:058ae6b1f923c85952ffdfa083af74e3b56dd450f309190f307c3ea56ac2aa75', 'grcv4-profile-sha256:6105daf6f5111fdc51640194298b1b8398d608684791050d85b696bcd681f64f', 'grcv4-profile-sha256:5f2f848af0f482699ac6cb88e4e1bd1a66458774bac2c3cc6df9f74cc47d7689', 'grcv4-profile-sha256:3a7a084788c59a55b4232fb98e9c5529c1aa4c7c71074c9d3288982fa2fd2a5b', 'grcv4-profile-sha256:12abb2946bfaa616df2a42bd571732e2be3000736f5078d45f8dbf53682b212b'}))

    def test_family_labels_and_unknown_exact_ids_fail_closed(self) -> None:
        for key in ("C_OS", "A_OS", "GRC9V4", "grcv4-profile-sha256:" + "0" * 64,
                    self.accepted_id + " ", None, [], {}):
            with self.subTest(key=key), self.assertRaises(V4IdentityError):
                get_supported_profile(key)


if __name__ == "__main__":
    unittest.main()

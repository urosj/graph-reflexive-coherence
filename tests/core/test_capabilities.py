"""Contract tests for the shared capability vocabulary."""

from __future__ import annotations

import unittest

from pygrc.core import (
    ALL_CAPABILITIES,
    BASIN_ATTRIBUTES,
    BOUNDARY_BARRIER,
    CHOICE_COLLAPSE_SEMANTICS,
    FAMILY_CAPABILITY_PROFILES,
    GRC9V3_CAPABILITY_PROFILE,
    GRC9_CAPABILITY_PROFILE,
    GRCV2_CAPABILITY_PROFILE,
    GRCV3_CAPABILITY_PROFILE,
    HOST_EMBEDDING_FRAME,
    INTRINSIC_FRAME,
    MULTI_METRIC_EDGES,
    PORT_GRAPH,
    SINGLE_WEIGHT_EDGES,
    UnsupportedCapabilityError,
)


class CapabilityContractTest(unittest.TestCase):
    """Validate the shared capability vocabulary and family profiles."""

    def test_common_vocabulary_contains_required_spec_names(self) -> None:
        self.assertIn(SINGLE_WEIGHT_EDGES, ALL_CAPABILITIES)
        self.assertIn(MULTI_METRIC_EDGES, ALL_CAPABILITIES)
        self.assertIn(PORT_GRAPH, ALL_CAPABILITIES)
        self.assertIn(BASIN_ATTRIBUTES, ALL_CAPABILITIES)
        self.assertIn(CHOICE_COLLAPSE_SEMANTICS, ALL_CAPABILITIES)
        self.assertIn(INTRINSIC_FRAME, ALL_CAPABILITIES)
        self.assertIn(HOST_EMBEDDING_FRAME, ALL_CAPABILITIES)
        self.assertIn(BOUNDARY_BARRIER, ALL_CAPABILITIES)

    def test_family_profiles_exist_for_all_four_families(self) -> None:
        self.assertEqual(
            {"GRCV2", "GRCV3", "GRC9", "GRC9V3"},
            set(FAMILY_CAPABILITY_PROFILES),
        )

    def test_profiles_accept_valid_minimum_claims(self) -> None:
        GRCV2_CAPABILITY_PROFILE.validate_claims(set(GRCV2_CAPABILITY_PROFILE.required))
        GRCV3_CAPABILITY_PROFILE.validate_claims(set(GRCV3_CAPABILITY_PROFILE.required))
        GRC9_CAPABILITY_PROFILE.validate_claims(set(GRC9_CAPABILITY_PROFILE.required))
        GRC9V3_CAPABILITY_PROFILE.validate_claims(
            set(GRC9V3_CAPABILITY_PROFILE.required)
        )

    def test_profiles_reject_forbidden_claims(self) -> None:
        with self.assertRaises(UnsupportedCapabilityError):
            GRC9_CAPABILITY_PROFILE.validate_claims(
                set(GRC9_CAPABILITY_PROFILE.required | {HOST_EMBEDDING_FRAME})
            )

    def test_profiles_reject_missing_required_claims(self) -> None:
        with self.assertRaises(UnsupportedCapabilityError):
            GRCV3_CAPABILITY_PROFILE.validate_claims(
                set(GRCV3_CAPABILITY_PROFILE.required - {BASIN_ATTRIBUTES})
            )

    def test_profiles_reject_unknown_capabilities(self) -> None:
        with self.assertRaises(UnsupportedCapabilityError):
            GRCV2_CAPABILITY_PROFILE.validate_claims(
                set(GRCV2_CAPABILITY_PROFILE.required | {"not_a_real_capability"})
            )

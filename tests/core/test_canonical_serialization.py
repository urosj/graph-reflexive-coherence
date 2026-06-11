"""Tests for canonical JSON conversion and canonical JSON encoding."""

from __future__ import annotations

import math
from types import MappingProxyType
import unittest

from pygrc.core import canonical_json_dumps, canonicalize_json_value


class CanonicalSerializationTest(unittest.TestCase):
    """Validate the shared Phase 3 canonical serialization primitives."""

    def test_canonicalize_json_value_normalizes_supported_nested_values(self) -> None:
        value = {
            "tuple_value": (3, 1),
            "set_value": {"beta", "alpha"},
            "mapping_proxy": MappingProxyType({"b": 2, "a": 1}),
        }

        canonical = canonicalize_json_value(value)

        self.assertEqual(
            {
                "mapping_proxy": {"a": 1, "b": 2},
                "set_value": ["alpha", "beta"],
                "tuple_value": [3, 1],
            },
            canonical,
        )

    def test_canonical_json_dumps_is_stable_for_identical_semantic_input(self) -> None:
        left = {"b": [3, 2], "a": {"y": 2, "x": 1}, "set": {"gamma", "alpha"}}
        right = {"set": {"alpha", "gamma"}, "a": {"x": 1, "y": 2}, "b": [3, 2]}

        self.assertEqual(canonical_json_dumps(left), canonical_json_dumps(right))

    def test_canonicalize_json_value_rejects_non_finite_float(self) -> None:
        with self.assertRaises(ValueError):
            canonicalize_json_value({"bad": math.inf})

        with self.assertRaises(ValueError):
            canonical_json_dumps({"bad": math.nan})

    def test_canonicalize_json_value_rejects_non_string_mapping_keys(self) -> None:
        with self.assertRaises(TypeError):
            canonicalize_json_value({1: "not allowed"})

    def test_canonicalize_json_value_rejects_unsupported_value_types(self) -> None:
        with self.assertRaises(TypeError):
            canonicalize_json_value(object())


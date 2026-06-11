"""Contract tests for the shared backend-selection architecture."""

from __future__ import annotations

import unittest

from pygrc.core import (
    BACKEND_SELECTIONS_KEY,
    COMMON_BACKEND_CATEGORIES,
    BackendSelection,
    GRCParams,
    build_backend_selection,
    build_backend_selection_payload,
    restore_backend_selections,
    validate_supported_backend_selections,
)


class BackendSelectionContractTest(unittest.TestCase):
    """Validate the common backend-selection surface for later families."""

    def test_backend_selection_builds_canonical_immutable_payload(self) -> None:
        selection = build_backend_selection(
            category="geometry",
            name="induced_local_frame",
            params={"epsilon": 1e-9, "axes": ["pca", "laplacian"]},
        )

        self.assertIsInstance(selection, BackendSelection)
        self.assertEqual("geometry", selection.category)
        self.assertEqual("induced_local_frame", selection.name)
        self.assertEqual(
            {
                "category": "geometry",
                "name": "induced_local_frame",
                "params": {"axes": ["pca", "laplacian"], "epsilon": 1e-9},
            },
            selection.canonical_payload(),
        )

        with self.assertRaises(TypeError):
            selection.params["epsilon"] = 1.0  # type: ignore[index]

    def test_backend_selection_rejects_invalid_category_or_name_tokens(self) -> None:
        with self.assertRaises(ValueError):
            build_backend_selection(category=" geometry", name="induced_local_frame")

        with self.assertRaises(ValueError):
            build_backend_selection(category="geometry", name="InducedLocalFrame")

        with self.assertRaises(ValueError):
            build_backend_selection(category="spark-trigger", name="baseline")

    def test_backend_selection_payload_is_stable_independent_of_input_order(self) -> None:
        left = build_backend_selection_payload(
            [
                build_backend_selection(
                    category="spark",
                    name="signed_hessian_plus_attractor_delta",
                    params={"epsilon_spark": 1e-3, "min_children": 1},
                ),
                build_backend_selection(
                    category="geometry",
                    name="induced_local_frame",
                    params={"regularization": 1e-9},
                ),
            ]
        )
        right = build_backend_selection_payload(
            {
                "geometry": build_backend_selection(
                    category="geometry",
                    name="induced_local_frame",
                    params={"regularization": 1e-9},
                ),
                "spark": build_backend_selection(
                    category="spark",
                    name="signed_hessian_plus_attractor_delta",
                    params={"min_children": 1, "epsilon_spark": 1e-3},
                ),
            }
        )

        self.assertEqual(left, right)
        self.assertEqual(
            {
                "geometry": {
                    "name": "induced_local_frame",
                    "params": {"regularization": 1e-9},
                },
                "spark": {
                    "name": "signed_hessian_plus_attractor_delta",
                    "params": {"epsilon_spark": 1e-3, "min_children": 1},
                },
            },
            left,
        )

    def test_backend_selection_payload_can_participate_in_params_identity(self) -> None:
        left = GRCParams.from_mapping(
            {
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    BACKEND_SELECTIONS_KEY: build_backend_selection_payload(
                        [
                            build_backend_selection(
                                category="geometry",
                                name="induced_local_frame",
                                params={"regularization": 1e-9},
                            ),
                            build_backend_selection(
                                category="spark",
                                name="signed_hessian_plus_attractor_delta",
                                params={"epsilon_spark": 1e-3, "min_children": 1},
                            ),
                        ]
                    )
                },
            }
        )
        right = GRCParams.from_mapping(
            {
                "dt": 0.1,
                "constitutive_semantic_modes": {
                    BACKEND_SELECTIONS_KEY: build_backend_selection_payload(
                        [
                            build_backend_selection(
                                category="spark",
                                name="signed_hessian_plus_attractor_delta",
                                params={"min_children": 1, "epsilon_spark": 1e-3},
                            ),
                            build_backend_selection(
                                category="geometry",
                                name="induced_local_frame",
                                params={"regularization": 1e-9},
                            ),
                        ]
                    )
                },
            }
        )

        self.assertEqual(left.canonical_identity(), right.canonical_identity())

    def test_backend_selection_payload_roundtrips_to_objects(self) -> None:
        payload = build_backend_selection_payload(
            [
                build_backend_selection(
                    category="choice",
                    name="sink_compatibility",
                    params={"epsilon_choice": 1e-2},
                )
            ]
        )

        restored = restore_backend_selections(payload)

        self.assertEqual(("choice",), tuple(restored))
        self.assertEqual("sink_compatibility", restored["choice"].name)
        self.assertEqual({"epsilon_choice": 1e-2}, dict(restored["choice"].params))

    def test_supported_backend_selection_validation_rejects_unknown_names(self) -> None:
        selection = build_backend_selection(
            category="geometry",
            name="induced_local_frame",
        )

        validate_supported_backend_selections(
            {"geometry": selection},
            allowed_names_by_category={
                "geometry": {"induced_local_frame", "host_embedding"},
            },
        )

        with self.assertRaises(ValueError):
            validate_supported_backend_selections(
                {"geometry": selection},
                allowed_names_by_category={"spark": {"signed_hessian_degeneracy"}},
            )

        with self.assertRaises(ValueError):
            validate_supported_backend_selections(
                {
                    "geometry": build_backend_selection(
                        category="geometry",
                        name="combinatorial",
                    )
                },
                allowed_names_by_category={
                    "geometry": {"induced_local_frame", "host_embedding"},
                },
            )

    def test_common_backend_category_vocabulary_exposes_expected_names(self) -> None:
        self.assertEqual(
            (
                "geometry",
                "metric",
                "curvature",
                "spark",
                "birth",
                "split",
                "boundary",
                "differential_summary",
                "hierarchy_update",
                "choice",
                "causal",
                "coarse_graining",
            ),
            COMMON_BACKEND_CATEGORIES,
        )

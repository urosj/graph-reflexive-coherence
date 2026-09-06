"""Independent P9-2.1 ownership tests; synthetic records are NOT admitted models."""

from __future__ import annotations

from array import array
from collections import UserDict, UserString
from collections.abc import Callable, Set
from copy import deepcopy
from dataclasses import fields, replace
from hashlib import sha256
import json
import importlib
from numbers import Integral
import operator
from pathlib import Path
from types import MappingProxyType
from typing import Any
import unittest

from pygrc.core.events import GRCEvent
from pygrc.core.types import GRCState, StepResult
from pygrc.models.grc_v4_state import (
    FrozenJSONMap,
    GRCStateSurface,
    GRCV4AuthoritativeState,
    GRCV4Event,
    GRCV4LifecycleResult,
    GRCV4LifecycleState,
    GRCV4ResetBaseline,
    GRCV4State,
    GRCV4StepResult,
    StepResultSurface,
)


def fixture(candidate: str = "C", realization: str = "OS") -> dict[str, Any]:
    """Explicit independent shape example, with unverified identity labels."""
    profile_id = "grcv4-profile-sha256:" + "1" * 64
    graph_id = "grc-graph-sha256:" + "2" * 64
    history = [0.5] if candidate == "A" else None
    carrier = [-0.25, 0.5] if realization in ("PC", "CI+PC") else None
    current: Any = {"C": [1.0, 2.0], "W_A": history, "Z_4": carrier}
    baseline: Any = {"C": [2.0, 1.0], "W_A": history, "Z_4": carrier}
    return {
        "step_index": 3,
        "time": 0.75,
        "graph": {
            "schema_version": "grcv4-serialized-graph-v1",
            "live_node_ids": ["v0", "v1"],
            "oriented_edges": [
                {"edge_id": "e0", "tail_node_id": "v0", "head_node_id": "v1"}
            ],
        },
        "graph_digest": graph_id,
        "orientation_identity": "v0-to-v1",
        "profile": {
            "identity_payload": {"candidate": candidate, "realization": realization},
            "params_resolved": {"reference": {"values": [1.0, 2.0]}},
            "complete_profile_id": profile_id,
        },
        "context_contract_id": "no-context",
        "context_value_digest": None,
        "current": GRCV4AuthoritativeState(**current),
        "reset": GRCV4ResetBaseline(
            authoritative=GRCV4AuthoritativeState(**baseline),
            graph_digest=graph_id,
            orientation_identity="v0-to-v1",
            active_model_identity=profile_id,
            context_contract_id="no-context",
            Q_target=3.0,
            reset_digest="grcv4-reset-sha256:" + "3" * 64,
        ),
        "Q_target": 3.0,
        "receipt_ledger": [
            {
                "receipt_id": "historical-test-label",
                "identity_payload": {"nested": [1, {"x": 2}]},
            }
        ],
        "scientific_state_digest": "grcv4-state-sha256:" + "4" * 64,
        "lifecycle_digest": "grcv4-lifecycle-sha256:" + "5" * 64,
    }


def fixture_id(prefix: str, payload: object) -> str:
    """Independent ASCII fixture preimages (no integral-valued float tokens)."""
    raw = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()
    return prefix + ":" + sha256(raw).hexdigest()


def successful_fixture() -> dict[str, Any]:
    core = {
        "operation_id": "test:step",
        "actual_charge_delta": 0,
        "information_losses": [],
        "disposition": "committed",
        "parent_receipt_ids": [],
    }
    for prefix in ("source", "target"):
        for key, grammar in {
            "state_digest": "grcv4-state",
            "graph_digest": "grc-graph",
            "model_identity": "grcv4-profile",
            "authoritative_digest": "grcv4-authoritative",
            "reset_digest": "grcv4-reset",
        }.items():
            core[prefix + "_" + key] = grammar + "-sha256:" + "1" * 64
    core.update(
        resource_transform_digest="grcv4-resource-transform-sha256:" + "2" * 64,
        history_bundle_digest="grcv4-history-map-sha256:" + "3" * 64,
    )
    payload = {"schema_version": "grcv4-step-commit-receipt-v1", "core": core}
    return {
        "schema_version": "grcv4-successful-receipt-envelope-v1",
        "receipt_id": fixture_id("grc-receipt-sha256", payload),
        "commit_id": "grc-commit-sha256:" + "4" * 64,
        "identity_payload": payload,
    }


def rejected_fixture(*, charge: bool = False) -> dict[str, Any]:
    data = result_fixture()
    stage, code, solver = (
        ("charge_admission", "charge_failure", "valid_root")
        if charge
        else ("admission", "invalid_duration", None)
    )
    state = "grcv4-state-sha256:" + "1" * 64
    life = "grcv4-lifecycle-sha256:" + "2" * 64
    identity = {
        "schema_version": "grcv4-failure-receipt-v1",
        "operation_id": "test:step",
        "stage": stage,
        "code": code,
        "source_state_digest": state,
        "observed_poststate_digest": state,
    }
    receipt = {
        "schema_version": "grcv4-failure-receipt-envelope-v1",
        "receipt_id": fixture_id("grc-receipt-sha256", identity),
        "identity_payload": identity,
    }
    failure = {
        "stage": stage,
        "code": code,
        "solver_disposition": solver,
        "message": "fixture rejection",
        "prestate_digest": state,
        "poststate_digest": state,
        "pre_lifecycle_digest": life,
        "post_lifecycle_digest": life,
        "failure_receipt": deepcopy(receipt),
    }
    data.update(
        operation_disposition="rejected",
        committed=False,
        commit_id=None,
        events=[],
        solver_disposition=solver,
        failure=failure,
        emitted_receipts=[receipt],
    )
    return data


def result_fixture() -> dict[str, Any]:
    return {
        "step_index": 3,
        "time": 0.75,
        "events": [GRCEvent("example", 3, {"nested": [1, {"x": 2}]}, "GRCV4")],
        "observables": {"current": [0.125, -0.125]},
        "active_profile_id": "grcv4-profile-sha256:" + "1" * 64,
        "active_model_identity": "grcv4-profile-sha256:" + "1" * 64,
        "operation_disposition": "committed",
        "solver_disposition": "valid_root",
        "committed": True,
        "commit_id": "grc-commit-sha256:" + "4" * 64,
        "failure": None,
        "emitted_receipts": [successful_fixture()],
    }


def mutate(value: Any, key: Any, replacement: Any) -> None:
    """Deliberately cross the static read-only boundary to test runtime rejection."""
    operator.setitem(value, key, replacement)


class FrozenJSONTests(unittest.TestCase):
    def test_deep_input_and_output_independence(self) -> None:
        source: dict[str, Any] = {"a": [{"b": [1, 2]}], "unicode": "e\u0301"}
        original = deepcopy(source)
        frozen = FrozenJSONMap(source)
        source["a"][0]["b"][0] = 99
        self.assertEqual(original, frozen.to_dict())
        output: Any = frozen.to_dict()
        output["a"][0]["b"].append(99)
        self.assertEqual(original, frozen.to_dict())
        self.assertEqual("e\u0301", frozen["unicode"])

    def test_proxy_cannot_retain_its_writable_backing(self) -> None:
        backing = {"nested": [1, 2]}
        frozen = FrozenJSONMap(MappingProxyType(backing))
        backing["nested"].append(3)
        backing["other"] = []
        self.assertEqual({"nested": [1, 2]}, frozen.to_dict())

    def test_nested_public_and_backing_mutation_rejected(self) -> None:
        frozen: Any = FrozenJSONMap({"a": [{"b": [1, 2]}]})
        actions: tuple[Callable[[], None], ...] = (
            lambda: operator.setitem(frozen, "a", 1),
            lambda: setattr(frozen, "_items", ()),
            lambda: operator.setitem(frozen._items, 0, ("a", 1)),
            lambda: operator.setitem(frozen["a"], 0, 1),
            lambda: operator.setitem(frozen["a"][0], "b", 1),
            lambda: operator.setitem(frozen["a"][0]["b"], 0, 1),
        )
        for action in actions:
            with (
                self.subTest(action=action),
                self.assertRaises((TypeError, AttributeError)),
            ):
                action()
        self.assertFalse(hasattr(frozen, "__dict__"))

    def test_cycles_rejected_but_shared_acyclic_values_copied(self) -> None:
        cyclic: list[Any] = []
        cyclic.append(cyclic)
        cyclic_map: dict[str, Any] = {}
        cyclic_map["self"] = cyclic_map
        for value in (cyclic, cyclic_map):
            with self.subTest(value=type(value)), self.assertRaises(ValueError):
                FrozenJSONMap({"cycle": value})
        shared = [1, 2]
        frozen = FrozenJSONMap({"a": shared, "b": shared})
        shared.append(3)
        self.assertEqual({"a": [1, 2], "b": [1, 2]}, frozen.to_dict())

    def test_non_json_payloads_rejected(self) -> None:
        for value in (object(), {1}, bytearray(b"x"), lambda: 1, GRCEvent("x", 0)):
            with self.subTest(value=type(value)), self.assertRaises(TypeError):
                FrozenJSONMap({"bad": value})
        with self.assertRaises(TypeError):
            invalid: Any = {1: "not a string"}
            FrozenJSONMap(invalid)

    def test_numeric_and_unicode_boundaries(self) -> None:
        for value in (float("nan"), float("inf"), -float("inf"), -0.0, 2**53):
            with self.subTest(value=value), self.assertRaises(ValueError):
                FrozenJSONMap({"bad": value})
        for payload in ({"bad": "\ud800"}, {"\ud800": "bad"}):
            with self.assertRaises(UnicodeError):
                FrozenJSONMap(payload)
        good = {"zero": 0.0, "limit": 2**53 - 1, "flag": True, "null": None}
        self.assertEqual(good, FrozenJSONMap(good).to_dict())

    def test_order_independent_mapping_equality_and_hash(self) -> None:
        first = FrozenJSONMap({"a": [1], "b": 2})
        second = FrozenJSONMap({"b": 2, "a": [1]})
        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        self.assertEqual(["a", "b"], list(first))
        self.assertEqual(first, deepcopy(first))

    def test_boolean_number_types_survive_for_later_identity_validation(self) -> None:
        # H1: Python equality/hash are not an identity oracle. Compare typed
        # detached JSON; the later JCS codec still owns scientific identities.
        for left, right in (
            ({"x": True}, {"x": 1}),
            ({"x": False}, {"x": 0.0}),
            ({"x": [{"flag": True}]}, {"x": [{"flag": 1}]}),
        ):
            first, second = FrozenJSONMap(left), FrozenJSONMap(right)
            self.assertNotEqual(
                json.dumps(first.to_dict(), sort_keys=True),
                json.dumps(second.to_dict(), sort_keys=True),
            )


class AuthorityTests(unittest.TestCase):
    def test_array_inputs_detached_in_all_channels(self) -> None:
        values: dict[str, Any] = {"C": array("d", [1, 2]), "W_A": [0.5], "Z_4": [-1, 1]}
        state = GRCV4AuthoritativeState(**values)
        for value in values.values():
            value[0] = 99
        self.assertEqual((1.0, 2.0), state.C)
        self.assertEqual((0.5,), state.W_A)
        self.assertEqual((-1.0, 1.0), state.Z_4)
        for value in (state.C, state.W_A, state.Z_4):
            self.assertIs(type(value), tuple)
            with self.assertRaises(TypeError):
                mutate(value, 0, 99)

    def test_invalid_numeric_authority_rejected(self) -> None:
        for key, value in (
            ("C", [-1]),
            ("W_A", [0]),
            ("W_A", [-1]),
            ("Z_4", [float("nan")]),
            ("C", [True]),
            ("C", ["1"]),
            ("C", [-0.0]),
            ("C", [2**53]),
            ("W_A", [float("inf")]),
            ("Z_4", [object()]),
        ):
            data: dict[str, Any] = {"C": [1], "W_A": None, "Z_4": None, key: value}
            with (
                self.subTest(key=key, value=value),
                self.assertRaises((TypeError, ValueError)),
            ):
                GRCV4AuthoritativeState(**data)

    def test_authority_does_not_acquire_derived_state(self) -> None:
        self.assertEqual(
            ["C", "W_A", "Z_4"], [f.name for f in fields(GRCV4AuthoritativeState)]
        )
        data: dict[str, Any] = {"C": [1], "W_A": None, "Z_4": None, "T_C": [1]}
        with self.assertRaises(TypeError):
            GRCV4AuthoritativeState(**data)

    def test_all_ten_coordinate_shapes_without_advertising_profiles(self) -> None:
        for candidate in ("A", "C"):
            for realization in ("CI", "OS", "RG2b", "PC", "CI+PC"):
                with self.subTest(candidate=candidate, realization=realization):
                    value = GRCV4LifecycleState(**fixture(candidate, realization))
                    for state in (value.current, value.reset.authoritative):
                        self.assertEqual(candidate == "A", state.W_A is not None)
                        self.assertEqual(
                            realization in ("PC", "CI+PC"), state.Z_4 is not None
                        )

    def test_wrong_current_or_reset_coordinate_shapes_rejected(self) -> None:
        for candidate, realization, key, wrong in (
            ("C", "OS", "W_A", (1.0,)),
            ("A", "OS", "W_A", None),
            ("C", "OS", "Z_4", (1.0,)),
            ("C", "PC", "Z_4", None),
            ("A", "CI+PC", "Z_4", None),
        ):
            for slot in ("current", "reset"):
                data = fixture(candidate, realization)
                if slot == "current":
                    data[slot] = replace(data[slot], **{key: wrong})
                else:
                    data[slot] = replace(
                        data[slot],
                        authoritative=replace(data[slot].authoritative, **{key: wrong}),
                    )
                with (
                    self.subTest(
                        candidate=candidate, realization=realization, slot=slot
                    ),
                    self.assertRaises(ValueError),
                ):
                    GRCV4LifecycleState(**data)

    def test_schema_agrees_with_authoritative_and_reset_field_sets(self) -> None:
        root = Path(__file__).resolve().parents[2]
        schema = json.loads((root / "specs/grc-v4-contract-schema.json").read_text())[
            "$defs"
        ]
        self.assertEqual(
            set(schema["authoritative_state"]["required"]),
            {f.name for f in fields(GRCV4AuthoritativeState)},
        )
        self.assertEqual(
            set(schema["grcv4_reset_payload"]["required"]) | {"reset_digest"},
            {f.name for f in fields(GRCV4ResetBaseline)},
        )


@Integral.register
class IntegralScalarAdapter:
    """Test-only integral adapter: detect conversion/absolute value before guarding."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __int__(self) -> int:
        return self.value

    def __abs__(self) -> int:
        raise AssertionError("absolute value used before exact Python-int conversion")

    def __float__(self) -> float:
        raise AssertionError("adapter rounded before exact Python-int conversion")


def coordinate(channel: str, values: Any) -> tuple[float, ...] | None:
    data: dict[str, Any] = {"C": [1.0, 2.0], "W_A": None, "Z_4": None}
    data[channel] = values
    result = GRCV4AuthoritativeState(**data)
    return {"C": result.C, "W_A": result.W_A, "Z_4": result.Z_4}[channel]


def scalar_record(field: str, value: Any) -> object:
    """Cover every clock/target owner, not only authoritative coordinate arrays."""
    data = fixture()
    if field == "reset.Q_target":
        return replace(data["reset"], Q_target=value)
    if field == "lifecycle.time":
        data["time"] = value
        return GRCV4LifecycleState(**data)
    if field == "lifecycle.Q_target":
        data["Q_target"] = value
        data["reset"] = replace(data["reset"], Q_target=value)
        return GRCV4LifecycleState(**data)
    if field == "result.time":
        return GRCV4StepResult(**(result_fixture() | {"time": value}))
    raise AssertionError("unknown test owner")


SCALAR_OWNERS = (
    "reset.Q_target",
    "lifecycle.time",
    "lifecycle.Q_target",
    "result.time",
)


class NumericInputBoundaryTests(unittest.TestCase):
    def test_integral_adapters_guard_before_abs_or_float(self) -> None:
        unsafe = (2**53, 2**53 + 1, 2**64 - 1, -(2**53 + 1), -(2**63))
        for channel in ("C", "W_A", "Z_4"):
            for number in unsafe:
                with (
                    self.subTest(channel=channel, number=number),
                    self.assertRaises(ValueError),
                ):
                    coordinate(channel, [IntegralScalarAdapter(number)])
        for owner in SCALAR_OWNERS:
            for number in unsafe:
                with (
                    self.subTest(owner=owner, number=number),
                    self.assertRaises(ValueError),
                ):
                    scalar_record(owner, IntegralScalarAdapter(number))

    def test_safe_integral_adapters_preserve_exact_value(self) -> None:
        for channel in ("C", "W_A", "Z_4"):
            for number in (1, 2**53 - 1):
                with self.subTest(channel=channel, number=number):
                    self.assertEqual(
                        (float(number),),
                        coordinate(channel, [IntegralScalarAdapter(number)]),
                    )
        self.assertEqual(
            (float(-(2**53 - 1)),),
            coordinate("Z_4", [IntegralScalarAdapter(-(2**53 - 1))]),
        )
        for owner in SCALAR_OWNERS:
            scalar_record(owner, IntegralScalarAdapter(2**53 - 1))

    def test_finite_float_domain_not_replaced_by_integer_domain(self) -> None:
        for number in (
            float(2**53),
            float(2**53 + 2),
            float.fromhex("0x1.fffffffffffffp+1023"),
        ):
            for channel in ("C", "W_A", "Z_4"):
                with self.subTest(channel=channel, number=number):
                    self.assertEqual((number,), coordinate(channel, [number]))
            for owner in SCALAR_OWNERS:
                scalar_record(owner, number)

    def test_unordered_mapping_and_raw_byte_containers_reject(self) -> None:
        class CustomSet(Set[float]):
            def __iter__(self) -> Any:
                return iter((1.0, 2.0))

            def __len__(self) -> int:
                return 2

            def __contains__(self, value: object) -> bool:
                return value in (1.0, 2.0)

        factories: tuple[Callable[[], Any], ...] = (
            lambda: {1: -999.0, 2: float("nan")},
            lambda: UserDict({1: -999.0, 2: float("nan")}),
            lambda: MappingProxyType({1: -999.0}),
            lambda: {1.0, 2.0},
            lambda: frozenset((1.0, 2.0)),
            CustomSet,
            lambda: b"\x01\x02",
            lambda: bytearray((1, 2)),
            lambda: "",
            lambda: UserString(""),
            dict,
            set,
            frozenset,
            bytes,
            bytearray,
        )
        for channel in ("C", "W_A", "Z_4"):
            for factory in factories:
                value = factory()
                with (
                    self.subTest(channel=channel, kind=type(value)),
                    self.assertRaises(TypeError),
                ):
                    coordinate(channel, value)

    def test_one_shot_and_untyped_iterables_reject_without_consumption(self) -> None:
        consumed = []

        def values() -> Any:
            consumed.append(True)
            yield 1.0
            yield 2.0

        class SizedIterable:
            def __len__(self) -> int:
                return 2

            def __iter__(self) -> Any:
                return values()

        for channel in ("C", "W_A", "Z_4"):
            for value in (values(), iter((1.0, 2.0)), SizedIterable()):
                with (
                    self.subTest(channel=channel, kind=type(value)),
                    self.assertRaises(TypeError),
                ):
                    coordinate(channel, value)
        self.assertEqual([], consumed)
        shared = values()
        data: Any = {"C": shared, "W_A": shared, "Z_4": shared}
        with self.assertRaises(TypeError):
            GRCV4AuthoritativeState(**data)
        self.assertEqual([], consumed)

    def test_ordered_sequences_and_typed_views_remain_supported(self) -> None:
        factories: tuple[Callable[[], Any], ...] = (
            lambda: [1.0, 2.0],
            lambda: (1.0, 2.0),
            lambda: range(1, 3),
            lambda: array("d", [1.0, 2.0]),
            lambda: array("q", [1, 2]),
            lambda: memoryview(array("d", [1.0, 2.0])),
            lambda: memoryview(array("d", [1.0, 99.0, 2.0]))[::2],
            lambda: memoryview(array("d", [2.0, 1.0]))[::-1],
        )
        for channel in ("C", "W_A", "Z_4"):
            for factory in factories:
                source = factory()
                result = coordinate(channel, source)
                self.assertEqual((1.0, 2.0), result)
                if isinstance(source, (list, array, memoryview)):
                    source[0] = 9 if not isinstance(source, memoryview) else 9.0
                    self.assertEqual((1.0, 2.0), result)
            empty_inputs: tuple[Any, ...] = ([], (), array("d"), memoryview(array("d")))
            for empty in empty_inputs:
                self.assertEqual((), coordinate(channel, empty))

    def test_multidimensional_or_nonnumeric_buffers_reject(self) -> None:
        matrix = memoryview(array("d", [1, 2, 3, 4])).cast("B").cast("d", shape=[2, 2])
        for channel in ("C", "W_A", "Z_4"):
            with self.subTest(channel=channel), self.assertRaises(TypeError):
                coordinate(channel, matrix)


class OptionalNumpyInputBoundaryTests(unittest.TestCase):
    """Real adapter regressions; NumPy remains optional and never a runtime import."""

    np: Any

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.np = importlib.import_module("numpy")
        except ImportError:
            raise unittest.SkipTest("NumPy adapter probes unavailable; not a pass")

    def test_signed_unsigned_unsafe_scalars_in_every_coordinate(self) -> None:
        np = self.np
        values = (
            np.int64(2**53),
            np.int64(2**53 + 1),
            np.uint64(2**53),
            np.uint64(2**53 + 1),
            np.uint64(2**64 - 1),
            np.int64(-(2**53 + 1)),
            np.int64(-(2**63)),
        )
        for channel in ("C", "W_A", "Z_4"):
            for number in values:
                for source in ([number], np.array([number], dtype=number.dtype)):
                    with (
                        self.subTest(
                            channel=channel, number=repr(number), source=type(source)
                        ),
                        self.assertRaises(ValueError),
                    ):
                        coordinate(channel, source)

    def test_signed_unsigned_safe_endpoints_and_bool_distinction(self) -> None:
        np = self.np
        for channel in ("C", "W_A", "Z_4"):
            for dtype in (np.int64, np.uint64):
                value = dtype(2**53 - 1)
                self.assertEqual((float(2**53 - 1),), coordinate(channel, [value]))
                self.assertEqual(
                    (float(2**53 - 1),),
                    coordinate(channel, np.array([value], dtype=dtype)),
                )
            with self.assertRaises(TypeError):
                coordinate(channel, [np.bool_(True)])
            self.assertEqual(
                (float(2**53 + 2),), coordinate(channel, [np.float64(2**53 + 2)])
            )
        self.assertEqual(
            (float(-(2**53 - 1)),), coordinate("Z_4", [np.int64(-(2**53 - 1))])
        )

    def test_integral_scalar_targets_and_clocks(self) -> None:
        np = self.np
        for owner in SCALAR_OWNERS:
            for value in (
                np.int64(2**53),
                np.int64(2**53 + 1),
                np.int64(-(2**63)),
                np.uint64(2**64 - 1),
            ):
                with (
                    self.subTest(owner=owner, value=repr(value)),
                    self.assertRaises(ValueError),
                ):
                    scalar_record(owner, value)
            for value in (
                np.int64(2**53 - 1),
                np.uint64(2**53 - 1),
                np.float64(2**53 + 2),
            ):
                scalar_record(owner, value)

    def test_numpy_views_detach_without_flattening_or_dtype_coercion(self) -> None:
        np = self.np
        for channel in ("C", "W_A", "Z_4"):
            for source in (
                np.array([1.25, 2.5]),
                np.array([1.25, 99.0, 2.5])[::2],
                np.array([2.5, 1.25])[::-1],
            ):
                result = coordinate(channel, source)
                source[0] = 99
                self.assertEqual((1.25, 2.5), result)
            for source in (
                np.array(1.0),
                np.array([[1.0], [2.0]]),
                np.array([1, 2], dtype=object),
                np.array([True, False]),
                np.array([], dtype=object),
                np.array([], dtype=bool),
            ):
                with (
                    self.subTest(
                        channel=channel, shape=source.shape, dtype=source.dtype
                    ),
                    self.assertRaises(TypeError),
                ):
                    coordinate(channel, source)


class LifecycleOwnershipTests(unittest.TestCase):
    def test_nested_graph_profile_and_receipt_inputs_detached(self) -> None:
        data = fixture()
        value = GRCV4LifecycleState(**data)
        data["graph"]["live_node_ids"].append("v2")
        data["graph"]["oriented_edges"][0]["edge_id"] = "changed"
        data["profile"]["params_resolved"]["reference"]["values"][0] = 99
        data["receipt_ledger"][0]["identity_payload"]["nested"][1]["x"] = 99
        self.assertEqual(fixture()["graph"], value.graph.to_dict())
        self.assertEqual(fixture()["profile"], value.profile.to_dict())
        self.assertEqual(
            fixture()["receipt_ledger"], [r.to_dict() for r in value.receipt_ledger]
        )

    def test_common_state_projection_has_no_duplicate_storage(self) -> None:
        state = GRCV4State(GRCV4LifecycleState(**fixture()))
        common: GRCStateSurface = state
        self.assertIsInstance(state, GRCStateSurface)
        self.assertEqual(state.budget_target, common.budget_target)
        self.assertNotIsInstance(state, GRCState)
        self.assertEqual(["lifecycle"], [f.name for f in fields(state)])
        self.assertEqual(
            (3, 0.75, 3.0, None),
            (state.step_index, state.time, state.budget_target, state.remainder),
        )
        for name in ("step_index", "time", "budget_target", "remainder", "lifecycle"):
            with (
                self.subTest(name=name),
                self.assertRaises((TypeError, AttributeError)),
            ):
                setattr(state, name, 42)
        self.assertFalse(hasattr(state, "__dict__"))
        self.assertFalse(hasattr(state, "rng_state"))

    def test_reset_is_reduced_and_distinct_from_live_state(self) -> None:
        state = GRCV4LifecycleState(**fixture())
        self.assertEqual((1.0, 2.0), state.current.C)
        self.assertEqual((2.0, 1.0), state.reset.authoritative.C)
        self.assertIsNot(state.current, state.reset.authoritative)
        for name in (
            "receipt_ledger",
            "step_index",
            "time",
            "rng_state",
            "cached_quantities",
        ):
            self.assertFalse(hasattr(state.reset, name))
        with self.assertRaises((TypeError, AttributeError)):
            setattr(state.reset, "Q_target", 9)

    def test_duplicate_values_do_not_reintroduce_writable_aliases(self) -> None:
        state = GRCV4State(GRCV4LifecycleState(**fixture("A", "PC")))
        duplicate = deepcopy(state)
        self.assertEqual(state, duplicate)
        detached: Any = duplicate.lifecycle.profile.to_dict()
        detached["params_resolved"]["reference"]["values"][0] = 99
        self.assertEqual(state, duplicate)
        with self.assertRaises(TypeError):
            mutate(duplicate.lifecycle.reset.authoritative.C, 0, 99)

    def test_invalid_clock_and_context_mismatches_rejected(self) -> None:
        for name, wrong in (
            ("step_index", True),
            ("step_index", -1),
            ("time", -1),
            ("time", float("inf")),
            ("Q_target", 4),
            ("graph_digest", "other"),
            ("orientation_identity", "other"),
            ("context_contract_id", "other"),
        ):
            data = fixture()
            data[name] = wrong
            with (
                self.subTest(name=name, wrong=wrong),
                self.assertRaises((TypeError, ValueError)),
            ):
                GRCV4LifecycleState(**data)

    def test_missing_profile_payloads_and_unknown_shapes_rejected(self) -> None:
        for key in ("identity_payload", "params_resolved", "complete_profile_id"):
            data = fixture()
            del data["profile"][key]
            with self.assertRaises(ValueError):
                GRCV4LifecycleState(**data)
        for candidate, realization in (("B", "OS"), ("C", "future")):
            with self.assertRaises(ValueError):
                GRCV4LifecycleState(**fixture(candidate, realization))


class ResultOwnershipTests(unittest.TestCase):
    def test_common_result_projection_and_schema_fields(self) -> None:
        value = GRCV4StepResult(**result_fixture())
        common: StepResultSurface = value
        self.assertIsInstance(value, StepResultSurface)
        self.assertEqual("example", common.events[0].kind)
        self.assertNotIsInstance(value, StepResult)
        self.assertEqual((3, 0.75), (value.step_index, value.time))
        schema = json.loads(
            (
                Path(__file__).resolve().parents[2]
                / "specs/grc-v4-contract-schema.json"
            ).read_text()
        )["$defs"]
        self.assertEqual(
            set(schema["step_result"]["required"]),
            {"events" if f.name == "_events" else f.name for f in fields(value)},
        )
        with self.assertRaises((TypeError, AttributeError)):
            setattr(value, "step_index", 99)

    def test_legacy_event_and_nested_payload_detached_in_both_directions(self) -> None:
        data = result_fixture()
        value = GRCV4StepResult(**data)
        data["events"][0].kind = "changed"
        data["events"][0].payload["nested"][1]["x"] = 99
        data["events"].clear()
        event = value.events[0]
        self.assertEqual("example", event.kind)
        self.assertIsInstance(event, GRCEvent)
        self.assertEqual({"nested": [1, {"x": 2}]}, event.payload)
        event.payload["nested"].append(99)
        event.kind = "caller-edit"
        self.assertEqual({"nested": [1, {"x": 2}]}, value.events[0].payload)
        self.assertEqual("example", value.events[0].kind)
        duplicate = deepcopy(value)
        duplicate.events[0].payload["nested"].append(101)
        self.assertEqual(value, duplicate)
        with self.assertRaises((TypeError, AttributeError)):
            setattr(value._events[0], "kind", "changed")

    def test_observables_and_operation_delta_not_ledger_aliases(self) -> None:
        data = fixture()
        data["receipt_ledger"] = [successful_fixture()]
        ledger = data["receipt_ledger"]
        lifecycle = GRCV4LifecycleState(**data)
        step_data = result_fixture()
        step_data["emitted_receipts"] = ledger
        result = GRCV4StepResult(**step_data)
        ledger[0]["receipt_id"] = "changed"
        ledger.append({"receipt_id": "another"})
        step_data["observables"]["current"][0] = 99
        self.assertEqual(1, len(lifecycle.receipt_ledger))
        self.assertEqual(1, len(result.emitted_receipts))
        self.assertEqual({"current": [0.125, -0.125]}, result.observables.to_dict())
        self.assertIsNot(lifecycle.receipt_ledger, result.emitted_receipts)

    def test_failure_and_receipt_payloads_detached(self) -> None:
        data = rejected_fixture()
        before = deepcopy(data)
        value = GRCV4StepResult(**data)
        data["failure"]["failure_receipt"]["identity_payload"]["operation_id"] = (
            "changed"
        )
        data["emitted_receipts"][0]["identity_payload"]["operation_id"] = "changed"
        self.assertIsNone(value.solver_disposition)
        self.assertIsNotNone(value.failure)
        assert value.failure is not None
        self.assertEqual(before["failure"], value.failure.to_payload())
        self.assertEqual(
            before["emitted_receipts"][0], value.emitted_receipts[0].to_payload()
        )

    def test_charge_rejection_does_not_erase_valid_solver_disposition(self) -> None:
        data = rejected_fixture(charge=True)
        value = GRCV4StepResult(**data)
        self.assertEqual("valid_root", value.solver_disposition)
        self.assertFalse(value.committed)

    def test_inconsistent_step_result_shapes_rejected(self) -> None:
        for changes in (
            {"committed": 1},
            {"commit_id": None},
            {"failure": {"bad": 1}},
            {"solver_disposition": "singular"},
            {"solver_disposition": None},
            {"operation_disposition": "rejected"},
            {"time": -1},
            {"events": [object()]},
            {"observables": {"bad": object()}},
        ):
            data = result_fixture()
            data.update(changes)
            with (
                self.subTest(changes=changes),
                self.assertRaises((TypeError, ValueError)),
            ):
                GRCV4StepResult(**data)

    def test_lifecycle_result_owns_detached_values(self) -> None:
        step = rejected_fixture()
        data: dict[str, Any] = {
            k: step[k]
            for k in [
                "operation_disposition",
                "committed",
                "commit_id",
                "failure",
                "emitted_receipts",
            ]
        }
        before = deepcopy(data)
        result = GRCV4LifecycleResult(**data)
        data["failure"]["message"] = "changed"
        data["emitted_receipts"][0]["identity_payload"]["operation_id"] = "changed"
        self.assertEqual(
            before["emitted_receipts"][0], result.emitted_receipts[0].to_payload()
        )
        assert result.failure is not None
        self.assertEqual(before["failure"], result.failure.to_payload())
        with self.assertRaises(ValueError):
            replace(result, committed=True)

    def test_v4_event_input_is_refrozen_and_legacy_unchanged(self) -> None:
        data = result_fixture()
        event = GRCV4Event("v4-example", 3, FrozenJSONMap({"nested": [1]}))
        data["events"] = [event]
        value = GRCV4StepResult(**data)
        self.assertEqual(event.to_common_event(), value.events[0])
        legacy = GRCState()
        legacy.step_index = 9
        legacy.event_log.append(GRCEvent("legacy", 9))
        self.assertEqual(9, legacy.step_index)
        self.assertEqual(1, len(legacy.event_log))


if __name__ == "__main__":
    unittest.main()

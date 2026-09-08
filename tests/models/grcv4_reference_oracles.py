"""Independent P9 reference calculations, not production or profile admission.

No production, NumPy solver or frozen vector-generator imports. The small JCS
writer deliberately covers only printable ASCII and exact dyadic numbers with
at most six fractional bits with fractional magnitude below 2**16; integral
values may span the safe-integer range. Other identity cases
must use published bytes or a separately reviewed oracle, never a silent
fallback to the production codec. Numeric comparisons may use general finite
binary64; their encoding is not mistaken for a scientific identity.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any, Literal
import unittest

ROOT = Path(__file__).resolve().parents[2]
IMPORTED_SOURCE_SHA256 = sha256(Path(__file__).read_bytes()).hexdigest()
MAX_FRACTIONAL_MAGNITUDE = 2**16
VECTOR_PATH = "specs/grc-v4-conformance-vectors.json"
VECTOR_SHA256 = "9d9917511816f8d6ca97feca14de3ffca6b720504041f879bb1fa3e8e57b4e22"
RELEASE_ID = "grcv4-spec-release-sha256:7b8b4d4e32e48fd35f70421cce7f547eebb21dd81389764061efe6e1a8c19886"
# Historical evidence remains inspectable under its own published authority.
PREDECESSOR_RELEASE_ID = "grcv4-spec-release-sha256:9f4c8fe5b57b1c477d834a3e4dae3f98a2b18c70e6e7f598e3c9652170c8645f"


class OracleDomainError(ValueError):
    """Reference writer unavailable for this input, not production rejection."""


def number(value: object) -> float:
    if type(value) not in (int, float):
        raise ValueError("expected a native real, not a boolean or adapter")
    if type(value) is int and abs(value) > 2**53 - 1:
        raise ValueError("unsafe input integer")
    assert isinstance(value, (int, float))
    result = float(value)
    if not math.isfinite(result) or (result == 0 and math.copysign(1, result) < 0):
        raise ValueError("nonfinite or negative zero")
    return result


def ascii_jcs(value: Any) -> bytes:
    """Independent, explicitly restricted identity oracle, not a general codec."""
    active: set[int] = set()

    def emit(v: Any) -> str:
        if v is None:
            return "null"
        if type(v) is bool:
            return "true" if v else "false"
        if type(v) is str:
            if any(not 32 <= ord(c) < 127 for c in v):
                raise ValueError("ASCII oracle string domain exceeded")
            return json.dumps(v, ensure_ascii=True)
        if type(v) in (int, float):
            x = number(v)
            if abs(x) > 2**53 - 1:
                raise ValueError("ASCII oracle number domain exceeded")
            q = Fraction(x)
            if q.denominator > 64:
                raise ValueError("ASCII oracle requires a small exact dyadic")
            if q.denominator != 1 and abs(x) >= MAX_FRACTIONAL_MAGNITUDE:
                raise OracleDomainError("fractional identity oracle magnitude exceeded")
            # At |x| < 2**16 the binary64 rounding interval is narrower than
            # 2**-36. A different <=6-place decimal is at least 10**-6 away,
            # so no shorter decimal can round to this exact dyadic. At larger
            # magnitudes that argument fails: exact decimal != shortest JCS.
            # All safe integers and this fractional subset use fixed notation.
            return str(int(q)) if q.denominator == 1 else format(x, ".6f").rstrip("0")
        if type(v) not in (dict, list, tuple):
            raise ValueError("expected primitive JSON containers")
        if id(v) in active:
            raise ValueError("cyclic reference fixture")
        active.add(id(v))
        try:
            if type(v) is dict:
                if any(type(k) is not str for k in v):
                    raise ValueError("non-string object key")
                return (
                    "{" + ",".join(emit(k) + ":" + emit(v[k]) for k in sorted(v)) + "}"
                )
            return "[" + ",".join(emit(x) for x in v) + "]"
        finally:
            active.remove(id(v))

    return emit(value).encode("ascii")


def identity(prefix: str, payload: Any) -> str:
    return prefix + ":" + sha256(ascii_jcs(payload)).hexdigest()


def scientific_id(state: dict[str, Any]) -> str:
    return identity("grcv4-state-sha256", state)


def lifecycle_id(state: dict[str, Any], ledger: list[dict[str, Any]]) -> str:
    return identity(
        "grcv4-lifecycle-sha256",
        {
            "schema_version": "grcv4-lifecycle-envelope-v1",
            "scientific_state_digest": scientific_id(state),
            "receipt_ids": [r["receipt_id"] for r in ledger],
        },
    )


@dataclass(frozen=True, slots=True)
class ComparisonPolicy:
    """Exact binary64 values or explicitly scoped numeric tolerance.

    Never applies tolerance to IDs, booleans, counts, ordering, request bytes,
    failure atomicity or ledger envelopes. The caller selects numeric fields;
    a passing tolerance test does not make their scientific digests equal.
    """

    mode: Literal["exact_binary64", "absolute_relative"] = "exact_binary64"
    absolute: float = 0.0
    relative: float = 0.0
    scope: str = "declared_numeric_field_only"

    def __post_init__(self) -> None:
        for value in (self.absolute, self.relative):
            if number(value) < 0:
                raise ValueError("negative comparison tolerance")
        if self.mode not in ("exact_binary64", "absolute_relative"):
            raise ValueError("unknown comparison policy")
        if self.mode == "exact_binary64" and (self.absolute or self.relative):
            raise ValueError("exact comparison cannot carry tolerance")
        if type(self.scope) is not str or not self.scope:
            raise ValueError("comparison scope is required")

    def accepts(self, actual: object, expected: object) -> bool:
        # Revalidate even if an unsupported caller forged this frozen value.
        ComparisonPolicy(self.mode, self.absolute, self.relative, self.scope)
        a, e = number(actual), number(expected)
        if self.mode == "exact_binary64":
            return a.hex() == e.hex()
        # Exact rational comparison avoids overflow in difference/threshold;
        # no inf <= inf false positive or hidden rounding enlargement.
        delta = abs(Fraction(a) - Fraction(e))
        bound = Fraction(self.absolute) + Fraction(self.relative) * max(
            abs(Fraction(e)), Fraction(1)
        )
        return delta <= bound


def balanced_charge(values: list[float]) -> float:
    """Adjacent balanced tree, carrying an odd last entry; no resource repair."""
    if type(values) is not list:
        raise ValueError("explicit canonical vertex order required")
    current = [number(v) for v in values]
    if any(v < 0 for v in current):
        raise ValueError("negative resource")
    while len(current) > 1:
        current = [
            float(Fraction(current[i]) + Fraction(current[i + 1]))
            if i + 1 < len(current)
            else current[i]
            for i in range(0, len(current), 2)
        ]
        if any(not math.isfinite(v) for v in current):
            raise ValueError("nonfinite charge")
    return current[0] if current else 0.0


def clock_target(index: int, time: float, dt: float) -> tuple[int, float]:
    """Explicit fixture clock convention, not additional frozen source authority.

    Positive fixture beats increment the index once and use one RN-even
    binary64 addition. Zero duration leaves the fixture's clock unchanged.
    A future operation owner must bind its accepted clock convention explicitly.
    """
    if type(index) is not int or not 0 <= index <= 2**53 - 1:
        raise ValueError("invalid clock index")
    t, duration = number(time), number(dt)
    if t < 0 or duration < 0:
        raise ValueError("negative clock/duration")
    if duration == 0:
        return index, t
    next_time = float(Fraction(t) + Fraction(duration))
    if index == 2**53 - 1 or not math.isfinite(next_time):
        raise ValueError("unrepresentable fixture clock")
    return index + 1, next_time


def expected_negative(
    request: dict[str, Any], state: dict[str, Any], ledger: list[dict[str, Any]]
) -> dict[str, Any]:
    """Hand-derived rejection outcome, independent of production receipts/results."""
    if number(request["dt"]) >= 0:
        raise ValueError("negative-duration oracle only")
    payload = {
        "schema_version": "grcv4-failure-receipt-v1",
        "operation_id": request["operation_id"],
        "stage": "admission",
        "code": "invalid_duration",
        "source_state_digest": scientific_id(state),
        "observed_poststate_digest": scientific_id(state),
    }
    receipt = {
        "schema_version": "grcv4-failure-receipt-envelope-v1",
        "receipt_id": identity("grc-receipt-sha256", payload),
        "identity_payload": payload,
    }
    return {
        "operation_disposition": "rejected",
        "solver_disposition": None,
        "committed": False,
        "commit_id": None,
        "events": [],
        "stage": "admission",
        "code": "invalid_duration",
        "step_index": state["step_index"],
        "time": state["time"],
        "poststate": deepcopy(state),
        "post_ledger": deepcopy(ledger),
        "prestate_digest": scientific_id(state),
        "poststate_digest": scientific_id(state),
        "pre_lifecycle_digest": lifecycle_id(state, ledger),
        "post_lifecycle_digest": lifecycle_id(state, ledger),
        "emitted_receipts": [receipt],
    }


def prefix_fixture() -> dict[str, Any]:
    """Concrete three-node fixture declaration, NOT an admitted C_OS beat.

    Reuse the frozen parameter vocabulary, not its unrelated nine-edge ID.
    All graph/reference/reset preimages are present and independently rehashed.
    """
    raw = (ROOT / VECTOR_PATH).read_bytes()
    if sha256(raw).hexdigest() != VECTOR_SHA256:
        raise ValueError("frozen vector bytes changed")
    vectors = json.loads(raw)
    params = deepcopy(vectors["identity_vectors"][0]["payload"])
    profile = deepcopy(vectors["identity_vectors"][1]["payload"])
    graph = {
        "schema_version": "grc9v4-port-graph-v1",
        "live_node_ids": ["a", "b", "c"],
        "edges": [
            {
                "edge_id": "e0",
                "kind": "boundary",
                "tail": {"node_id": "a", "port": 1},
                "head": {"node_id": "b", "port": 1},
            },
            {
                "edge_id": "e1",
                "kind": "boundary",
                "tail": {"node_id": "b", "port": 2},
                "head": {"node_id": "c", "port": 1},
            },
        ],
    }
    wctr = {"schema_version": "grcv4-wctr-identity-v1", "W_C_tr": {"e0": 2, "e1": 3}}
    hodge = {
        "schema_version": "grcv4-reference-hodge-identity-v1",
        "edge_weights": {"e0": 2, "e1": 3},
    }
    k4 = {"schema_version": "grcv4-k4-identity-v1", "K4_base": [[2, 1], [1, 2]]}
    params["candidate"].update(
        W_C_tr=wctr["W_C_tr"], W_C_tr_content_digest=identity("grcv4-wctr-sha256", wctr)
    )
    params["geometry"].update(
        K4_base_digest=identity("grcv4-k4-sha256", k4),
        reference_hodge_digest=identity("grcv4-hodge-sha256", hodge),
    )
    profile["params_hash"] = identity("grcv4-params-sha256", params)
    profile_id = identity("grcv4-profile-sha256", profile)
    reset = {
        "schema_version": "grcv4-reset-baseline-v1",
        "active_model_identity": profile_id,
        "graph_digest": identity("grc-graph-sha256", graph),
        "orientation_identity": "tail_to_head_edge_id_order_v1",
        "authoritative": {"C": [1, 1, 1], "W_A": None, "Z_4": None},
        "Q_target": 3,
        "context_contract_id": "constant_zero_context_v1",
    }
    state = {k: deepcopy(v) for k, v in reset.items() if k != "schema_version"}
    state.update(
        schema_version="grcv4-scientific-state-v1",
        step_index=3,
        time=0.75,
        authoritative={"C": [0.5, 1, 1.5], "W_A": None, "Z_4": None},
        reset_digest=identity("grcv4-reset-sha256", reset),
        context_value_digest=None,
    )
    request = {
        "schema_version": "grcv4-step-request-input-v1",
        "operation_id": "P9-2.5:negative-duration",
        "dt": -0.25,
        "context_value": {},
        "boundary_input": None,
        "external_source": None,
    }
    return {
        "fixture_id": "P9-2.5-THREE-NODE-NEGATIVE-PREFIX",
        "fixture_class": "engineering_prefix_not_profile_admission",
        "profile_identity": profile,
        "params": params,
        "graph": graph,
        "reference_hodge": hodge,
        "K4_base": k4,
        "reset": reset,
        "prestate": state,
        "pre_ledger": [],
        "request": request,
        "source_profile_id": profile_id,
        "target_profile_id": profile_id,
        "context_contract": {
            "id": "constant_zero_context_v1",
            "value": {},
            "meaning": "zero external context",
        },
        "domain_status": "declared_not_runtime_admitted",
    }


class ReferenceOracleTests(unittest.TestCase):
    def test_fractional_magnitude_guard_and_safe_integral_endpoints(self) -> None:
        # Python's independently implemented shortest repr is sufficient here:
        # the guarded dyadics use fixed notation and the proof above excludes
        # competing shorter decimals. Separate Node pressure covers JCS too.
        for denominator in [2, 4, 8, 16, 32, 64]:
            for sign in (-1, 1):
                for numerator in (1, 3, 5, 7, 15, 31, 63):
                    for magnitude in (
                        0,
                        2**15,
                        2**16 - 1,
                        2**16,
                        2**30,
                        2**36,
                        2**48,
                        2**52,
                    ):
                        x = sign * (magnitude + numerator / denominator)
                        with self.subTest(binary64=x.hex()):
                            if (
                                not x.is_integer()
                                and abs(x) >= MAX_FRACTIONAL_MAGNITUDE
                            ):
                                with self.assertRaises(OracleDomainError):
                                    ascii_jcs(x)
                            else:
                                expected = str(int(x)) if x.is_integer() else repr(x)
                                self.assertEqual(ascii_jcs(x), expected.encode())
        for x in [-(2**53 - 1), 2**53 - 1, float(2**53 - 1), -float(2**53 - 1)]:
            self.assertEqual(ascii_jcs(x), str(int(x)).encode())
        for x in [2**53, float(2**53), 1 / 128, -1 / 128]:
            with self.assertRaises(ValueError):
                ascii_jcs(x)

    def test_audited_large_dyadics_are_unavailable_not_noncanonical_identities(
        self,
    ) -> None:
        for value in [2.0**36 + 1 / 64, 2.0**48 + 1 / 16, 1e15 + 0.25]:
            for sign in [-1, 1]:
                with self.assertRaises(OracleDomainError):
                    ascii_jcs(sign * value)
                self.assertEqual(number(sign * value), sign * value)

    def test_published_ascii_preimages(self) -> None:
        vectors = json.loads((ROOT / VECTOR_PATH).read_text())
        for row in vectors["identity_vectors"][:2]:
            self.assertEqual(
                ascii_jcs(row["payload"]), row["canonical_jcs_utf8"].encode()
            )
            self.assertEqual(
                identity(row["expected_identifier"].split(":")[0], row["payload"]),
                row["expected_identifier"],
            )

    def test_ascii_writer_fails_outside_its_declared_domain(self) -> None:
        for value in [
            0.1,
            1e20,
            -0.0,
            float("nan"),
            float("inf"),
            "é",
            "line\n",
            {1: "x"},
            {1},
            2**53,
        ]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                ascii_jcs(value)
        recursive: list[Any] = []
        recursive.append(recursive)
        with self.assertRaises(ValueError):
            ascii_jcs(recursive)
        self.assertNotEqual(ascii_jcs(True), ascii_jcs(1))

    def test_numeric_policies_are_explicit_finite_and_overflow_safe(self) -> None:
        self.assertFalse(ComparisonPolicy().accepts(1.0, math.nextafter(1.0, 2)))
        self.assertTrue(ComparisonPolicy("absolute_relative", 0.25).accepts(1.25, 1))
        self.assertFalse(
            ComparisonPolicy("absolute_relative", 0.25).accepts(
                math.nextafter(1.25, 2), 1
            )
        )
        self.assertFalse(
            ComparisonPolicy("absolute_relative", 0, 1).accepts(-1e308, 1e308)
        )
        for value in [True, -0.0, float("nan"), float("inf"), -1]:
            with self.assertRaises(ValueError):
                ComparisonPolicy("absolute_relative", value)
        for value in [True, -0.0, float("nan"), float("inf")]:
            with self.assertRaises(ValueError):
                ComparisonPolicy().accepts(value, 1)
        with self.assertRaises(ValueError):
            ComparisonPolicy("exact_binary64", 1)

    def test_charge_is_ordered_binary64_without_repair(self) -> None:
        values = [float(2**53), 1.0, 1.0, 1.0]
        self.assertEqual(balanced_charge(values), float(2**53 + 2))
        self.assertEqual(values, [float(2**53), 1.0, 1.0, 1.0])
        self.assertEqual(balanced_charge([0.5, 1, 1.5]), 3)
        self.assertEqual(balanced_charge([]), 0)
        with self.assertRaises((OverflowError, ValueError)):
            balanced_charge([1e308, 1e308])

    def test_clock_allows_rounded_tiny_increment_without_a_strict_time_increase(
        self,
    ) -> None:
        self.assertEqual(clock_target(3, 0.75, 5e-324), (4, 0.75))
        self.assertEqual(clock_target(3, 0.75, 0), (3, 0.75))
        self.assertEqual(clock_target(3, 0.75, 0.25), (4, 1))
        for dt in [-1, -0.0, True, float("inf")]:
            with self.assertRaises(ValueError):
                clock_target(3, 0.75, dt)
        with self.assertRaises(ValueError):
            clock_target(2**53 - 1, 0, 1)

    def test_reference_fixture_reidentifies_and_separates_live_reset(self) -> None:
        case = prefix_fixture()
        self.assertEqual(len(case["graph"]["edges"]), len(case["K4_base"]["K4_base"]))
        self.assertNotEqual(
            case["prestate"]["authoritative"], case["reset"]["authoritative"]
        )
        self.assertNotEqual(
            case["source_profile_id"],
            "grcv4-profile-sha256:618ef0aaecdbfbf89c26c5be163fdb197d349a15ab71c8aa64bb669a42f2195c",
        )
        expected = expected_negative(case["request"], case["prestate"], [])
        self.assertEqual(expected["poststate"], case["prestate"])
        case["prestate"]["authoritative"]["C"][0] = 99
        self.assertNotEqual(expected["poststate"], case["prestate"])


if __name__ == "__main__":
    unittest.main()

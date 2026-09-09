"""P9-2.5 execution/evidence harness; no complete numerical model exists yet.

The only production execution adapter is the negative-duration prefix. Caller
overrides are unconditionally mutation controls, never runtime conformance.
Independent expectations are computed before invocation. A matching imported
record, a passing control, or a stored manifest grants no execution authority.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
import math
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import tempfile
from typing import Any
import unittest
from unittest.mock import patch
import uuid

from pygrc.models.grc_v4 import GRCV4StepRequestInput
from pygrc.models.grc_v4_codec import canonical_json_bytes, validate_payload
from pygrc.models.grc_v4_profile import resolve_profile, validate_profile_references
from pygrc.models.grc_v4_state import GRCV4StepResult
from pygrc.models import grc_v4_step as production
from tests.models import grcv4_reference_oracles as oracle

ROOT = Path(__file__).resolve().parents[2]
IMPORTED_SOURCE_SHA256 = sha256(Path(__file__).read_bytes()).hexdigest()
SOURCE_PATHS = (
    "tests/models/grcv4_conformance_harness.py",
    "tests/models/grcv4_reference_oracles.py",
    "src/pygrc/models/grc_v4.py",
    "src/pygrc/models/grc_v4_step.py",
    "src/pygrc/models/grc_v4_state.py",
    "src/pygrc/models/grc_v4_profile.py",
    "src/pygrc/models/grc_v4_codec.py",
    "src/pygrc/models/grc_v4_assets/__init__.py",
    "src/pygrc/models/grc_v4_assets/asset-index.json",
    "src/pygrc/models/grc_v4_assets/grc-v4-contract-schema.json",
    "pyproject.toml",
    "specs/grc-v4-spec.md",
    "specs/grc-common-interface-v4-ext.md",
    "specs/grc-v4-contract-schema.json",
    "specs/grc-v4-conformance-fixtures.json",
    oracle.VECTOR_PATH,
    "specs/grc-v4-specification-release.json",
    "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md",
    "implementation/investigations/grc9v4-constitutive-design/decisions/D10_2FullSubstrateProvenanceAndPromotionAudit.json",
)


class HarnessError(ValueError):
    """Bad harness input or failed comparison, not a V4 FailureReceipt."""


def record_bytes(value: Any) -> bytes:
    """Deterministic evidence JSON, explicitly NOT a general scientific JCS codec."""
    active: set[int] = set()

    def copy(v: Any) -> Any:
        if v is None or type(v) is bool:
            return v
        if type(v) is str:
            v.encode("utf-8")
            return v
        if type(v) in (int, float):
            oracle.number(v)
            return (
                int(v)
                if type(v) is float and v.is_integer() and abs(v) <= 2**53 - 1
                else v
            )
        if type(v) not in (dict, list, tuple) or id(v) in active:
            raise HarnessError("non-JSON or cyclic evidence")
        active.add(id(v))
        try:
            if type(v) is dict:
                if any(type(k) is not str for k in v):
                    raise HarnessError("evidence object keys must be strings")
                return {copy(k): copy(x) for k, x in v.items()}
            return [copy(x) for x in v]
        finally:
            active.remove(id(v))

    return json.dumps(
        copy(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def parse_record(raw: bytes) -> dict[str, Any]:
    if type(raw) is not bytes:
        raise HarnessError("exact immutable evidence bytes required")

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise HarnessError("duplicate evidence key")
            result[key] = value
        return result

    value = json.loads(raw, object_pairs_hook=pairs)
    if type(value) is not dict or record_bytes(value) != raw:
        raise HarnessError("noncanonical evidence record")
    return value


def same(actual: Any, expected: Any, label: str) -> None:
    if record_bytes(actual) != record_bytes(expected):
        raise HarnessError(label)


def relative_file(root: Path, path: str) -> Path:
    if type(path) is not str or "\\" in path:
        raise HarnessError("repository-relative POSIX path required")
    parts = PurePosixPath(path)
    if (
        parts.is_absolute()
        or not parts.parts
        or any(p in (".", "..") for p in path.split("/"))
        or str(parts) != path
    ):
        raise HarnessError("noncanonical repository-relative path")
    target = root / path
    if not target.resolve().is_relative_to(root.resolve()):
        raise HarnessError("path escapes repository")
    return target


def file_binding(root: Path, path: str) -> dict[str, str]:
    target = relative_file(root, path)
    return {"path": path, "sha256": sha256(target.read_bytes()).hexdigest()}


def verify_bindings(root: Path, rows: list[dict[str, str]]) -> None:
    seen: set[str] = set()
    if type(rows) is not list or not rows:
        raise HarnessError("nonempty exact source bindings required")
    for row in rows:
        if set(row) != {"path", "sha256"} or row["path"] in seen:
            raise HarnessError("invalid or duplicate source binding")
        seen.add(row["path"])
        same(file_binding(root, row["path"]), row, "source bytes changed")


def environment() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.system(),
        "machine": platform.machine(),
        "float_format": getattr(float, "__getformat__")("double"),
        "mantissa_bits": sys.float_info.mant_dig,
        "rounds": sys.float_info.rounds,
        "dependencies": {
            name: version(name) for name in ("rfc8785", "jsonschema", "numpy")
        },
        "numeric_backend_used": "stdlib_fraction_and_binary64_no_numpy_solver",
    }


@dataclass(frozen=True, slots=True)
class Fixture:
    payload_bytes: bytes

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Fixture:
        return cls(record_bytes(payload))

    def __post_init__(self) -> None:
        data = parse_record(self.payload_bytes)
        expected = {
            "fixture_id",
            "fixture_class",
            "profile_identity",
            "params",
            "graph",
            "reference_hodge",
            "K4_base",
            "reset",
            "prestate",
            "pre_ledger",
            "request",
            "source_profile_id",
            "target_profile_id",
            "context_contract",
            "domain_status",
        }
        if set(data) != expected or not data["fixture_id"]:
            raise HarnessError("closed fixture fields required")
        if (
            data["fixture_class"] != "engineering_prefix_not_profile_admission"
            or data["domain_status"] != "declared_not_runtime_admitted"
        ):
            raise HarnessError("fixture cannot claim admitted runtime support")
        GRCV4StepRequestInput.from_payload(data["request"])
        profile = resolve_profile(data["params"], data["profile_identity"])
        same(
            profile.complete_profile_id,
            data["source_profile_id"],
            "wrong source profile",
        )
        same(
            data["target_profile_id"],
            data["source_profile_id"],
            "prefix cannot change profile",
        )
        graph = data["graph"]
        validate_payload("port_graph_payload", graph)
        edge_ids = [e["edge_id"] for e in graph["edges"]]
        nodes = graph["live_node_ids"]
        if len(set(edge_ids)) != len(edge_ids) or any(
            e[p]["node_id"] not in nodes
            for e in graph["edges"]
            for p in ("tail", "head")
        ):
            raise HarnessError("ambiguous fixture graph references")
        # Content/reference checking only. This is not graph/SPD/domain admission.
        validate_profile_references(
            profile,
            live_edge_ids=edge_ids,
            k4_preimage=data["K4_base"],
            reference_hodge_preimage=data["reference_hodge"],
        )
        for field, schema, prefix in [
            ("K4_base", "k4_identity_payload", "grcv4-k4-sha256"),
            (
                "reference_hodge",
                "reference_hodge_identity_payload",
                "grcv4-hodge-sha256",
            ),
        ]:
            validate_payload(schema, data[field])
            key = "K4_base_digest" if field == "K4_base" else "reference_hodge_digest"
            same(
                oracle.identity(prefix, data[field]),
                data["params"]["geometry"][key],
                "reference preimage mismatch",
            )
        matrix = data["K4_base"]["K4_base"]
        if len(matrix) != len(edge_ids) or any(len(r) != len(edge_ids) for r in matrix):
            raise HarnessError("reference matrix dimensions differ from graph")
        validate_payload("grcv4_reset_payload", data["reset"])
        validate_payload("scientific_state_payload", data["prestate"])
        if profile.identity_payload.profile_family_id != "C_OS":
            raise HarnessError(
                "current concrete fixture adapter is C_OS declarations only"
            )
        for state in (data["prestate"], data["reset"]):
            same(
                state["active_model_identity"],
                data["source_profile_id"],
                "state profile mismatch",
            )
            same(
                state["graph_digest"],
                oracle.identity("grc-graph-sha256", graph),
                "state graph mismatch",
            )
            same(
                state["context_contract_id"],
                data["params"]["common"]["context_contract_id"],
                "state context mismatch",
            )
            authority = state["authoritative"]
            if (
                len(authority["C"]) != len(nodes)
                or authority["W_A"] is not None
                or authority["Z_4"] is not None
            ):
                raise HarnessError("authority shape differs from concrete C_OS fixture")
        same(
            data["prestate"]["reset_digest"],
            oracle.identity("grcv4-reset-sha256", data["reset"]),
            "reset preimage mismatch",
        )
        same(
            data["context_contract"],
            {
                "id": data["prestate"]["context_contract_id"],
                "value": {},
                "meaning": "zero external context",
            },
            "unresolved context contract",
        )
        if data["prestate"]["context_value_digest"] is not None:
            raise HarnessError("current fixture uses null prior context digest")
        if type(data["pre_ledger"]) is not list:
            raise HarnessError("ordered persistent ledger required")
        for receipt in data["pre_ledger"]:
            production.SuccessfulReceiptEnvelope.from_payload(receipt)

    def to_payload(self) -> dict[str, Any]:
        return parse_record(self.payload_bytes)


def ordinary_clock_controls(
    prestate: dict[str, Any], request: dict[str, Any], poststate: dict[str, Any]
) -> None:
    """Necessary fixture checks, never a complete-step oracle or stage evidence."""
    index, time = oracle.clock_target(
        prestate["step_index"], prestate["time"], request["dt"]
    )
    same(
        [poststate["step_index"], poststate["time"]],
        [index, time],
        "ordinary fixture clock progression",
    )
    if request["dt"] == 0:
        same(poststate, prestate, "zero-duration identity, no writer advancement")


def assess_negative(
    data: dict[str, Any], expected: dict[str, Any], observed: dict[str, Any]
) -> None:
    """Independent expected/actual checks, then the production relational checker.

    This function accepts supplied observations; calling it is NOT execution.
    The harness's execution wrapper separately records the actual invocation.
    """
    same(
        expected,
        oracle.expected_negative(data["request"], data["prestate"], data["pre_ledger"]),
        "foreign or altered expectation",
    )
    same(observed["request"], data["request"], "foreign request")
    same(observed["prestate"], data["prestate"], "foreign captured source")
    same(observed["pre_ledger"], data["pre_ledger"], "foreign captured ledger")
    same(
        observed["poststate"],
        expected["poststate"],
        "scientific payload changed on rejection",
    )
    same(
        observed["post_ledger"],
        expected["post_ledger"],
        "persistent ledger changed on rejection",
    )
    same(observed["reset_before"], data["reset"], "foreign captured reset")
    same(observed["reset_after"], data["reset"], "reset changed on rejection")
    same(
        observed["outcome"],
        {
            "stage": expected["stage"],
            "code": expected["code"],
            "solver": expected["solver_disposition"],
        },
        "observed outcome differs from oracle",
    )
    result = GRCV4StepResult.from_payload(observed["result"])
    payload = result.to_payload()
    for key in (
        "operation_disposition",
        "solver_disposition",
        "committed",
        "commit_id",
        "events",
        "step_index",
        "time",
        "emitted_receipts",
    ):
        same(payload[key], expected[key], "independent result mismatch: " + key)
    same(payload["observables"], {}, "unexpected prefix observables")
    assert result.failure is not None
    for field in (
        "prestate_digest",
        "poststate_digest",
        "pre_lifecycle_digest",
        "post_lifecycle_digest",
    ):
        same(
            getattr(result.failure, field),
            expected[field],
            "independent failure identity: " + field,
        )
    production.bind_step_result(
        result,
        request=GRCV4StepRequestInput.from_payload(data["request"]),
        prestate=observed["prestate"],
        poststate=observed["poststate"],
        pre_ledger=observed["pre_ledger"],
        post_ledger=observed["post_ledger"],
        observed_stage="admission",
        observed_code="invalid_duration",
        observed_solver=None,
    )


Operation = Callable[[GRCV4StepRequestInput, dict[str, Any]], GRCV4StepResult]
MISSING = object()


def observation_error(value: Any, path: str) -> dict[str, str] | None:
    """Describe an unencodable observation without coercion or calling repr hooks."""
    active: set[int] = set()

    def visit(v: Any, where: str, depth: int) -> dict[str, str] | None:
        code, representation = "", ""
        if v is MISSING:
            code, representation = "missing_subject_field", "<missing>"
        elif depth > 64:
            code, representation = "capture_depth_limit", "<depth-limit>"
        elif type(v) is float and (
            not math.isfinite(v) or (v == 0 and math.copysign(1, v) < 0)
        ):
            code, representation = "invalid_float", v.hex()
        elif type(v) is int and abs(v) > 2**53 - 1:
            code, representation = (
                "unsafe_integer",
                "<int bits=" + str(v.bit_length()) + ">",
            )
        elif type(v) is str:
            try:
                v.encode("utf-8")
            except UnicodeError:
                code, representation = "invalid_unicode", ascii(v[:80])
        elif v is None or type(v) in (bool, int, float):
            return None
        elif type(v) not in (dict, list, tuple):
            code, representation = "unsupported_type", "<" + type(v).__name__ + ">"
        elif id(v) in active:
            code, representation = "cyclic_container", "<cycle>"
        else:
            active.add(id(v))
            try:
                if type(v) is dict:
                    for key, item in v.items():
                        if type(key) is not str:
                            return {
                                "stage": "admission",
                                "field_path": where,
                                "type": type(key).__name__,
                                "code": "non_string_key",
                                "representation": "<non-string key>",
                            }
                        error = visit(key, where + "[key]", depth + 1)
                        if error is None:
                            error = visit(
                                item,
                                where + "[" + json.dumps(key, ensure_ascii=True) + "]",
                                depth + 1,
                            )
                        if error is not None:
                            return error
                else:
                    for i, item in enumerate(v):
                        error = visit(item, where + "[" + str(i) + "]", depth + 1)
                        if error is not None:
                            return error
            finally:
                active.remove(id(v))
        if not code:
            return None
        return {
            "stage": "admission",
            "field_path": where,
            "type": "missing" if v is MISSING else type(v).__name__,
            "code": code,
            "representation": representation,
        }

    return visit(value, path, 0)


def comparison_error(
    data: dict[str, Any], expected: dict[str, Any], observed: dict[str, Any]
) -> dict[str, Any] | None:
    try:
        assess_negative(data, expected, observed)
    except (ValueError, TypeError, KeyError, AssertionError) as exc:
        return {
            "kind": "comparison",
            "diagnostics": [
                {
                    "stage": "admission",
                    "field_path": "$.actual",
                    "type": type(exc).__name__,
                    "code": "comparison_failed",
                    "representation": str(exc),
                }
            ],
        }
    return None


def run_negative(
    fixture: Fixture, *, operation: Operation | None = None
) -> dict[str, Any]:
    """Execute the owned prefix once; overrides are always harness controls."""
    if type(fixture) is not Fixture:
        raise HarnessError("exact fixture value required")
    fixture = Fixture(fixture.payload_bytes)  # Revalidate unsupported forged values.
    data = fixture.to_payload()
    expected = oracle.expected_negative(
        data["request"], data["prestate"], data["pre_ledger"]
    )
    subject = {
        "state": deepcopy(data["prestate"]),
        "ledger": deepcopy(data["pre_ledger"]),
        "reset": deepcopy(data["reset"]),
    }
    request = GRCV4StepRequestInput.from_payload(data["request"])
    observed = {
        "prestate": deepcopy(subject["state"]),
        "pre_ledger": deepcopy(subject["ledger"]),
        "reset_before": deepcopy(subject["reset"]),
        "request": request.to_payload(),
        "outcome": {"stage": "admission", "code": "invalid_duration", "solver": None},
    }

    # Outcome labels describe the negative-duration admission branch entered
    # here, not fields read back from a result or imported receipt. This is a
    # harness-owned captured subject, not evidence of a mutable model rollback.
    def default_operation(
        req: GRCV4StepRequestInput, state: dict[str, Any]
    ) -> GRCV4StepResult:
        return production.negative_duration_result(
            req,
            prestate=state["state"],
            receipt_ledger=state["ledger"],
            active_profile_id=data["source_profile_id"],
        )[0]

    invoke: Operation = default_operation if operation is None else operation
    error: dict[str, Any] | None = None
    result_payload: Any = MISSING
    try:
        result = invoke(request, subject)
        if type(result) is not GRCV4StepResult:
            raise HarnessError("operation did not return a result")
        result_payload = result.to_payload()
    except Exception as exc:
        error = {
            "kind": "invocation",
            "diagnostics": [
                {
                    "stage": "admission",
                    "field_path": "$.operation",
                    "type": type(exc).__name__,
                    "code": "operation_raised",
                    "representation": "<exception; no interpreter-local traceback>",
                }
            ],
        }
    captures = {
        "poststate": subject.get("state", MISSING),
        "post_ledger": subject.get("ledger", MISSING),
        "reset_after": subject.get("reset", MISSING),
    }
    if result_payload is not MISSING:
        captures["result"] = result_payload
    capture_errors = []
    for field, value in captures.items():
        diagnostic = observation_error(value, "$." + field)
        if diagnostic is not None:
            capture_errors.append(diagnostic)
        else:
            observed[field] = json.loads(record_bytes(value))
    if capture_errors:
        # Omit an unencodable field and describe it explicitly; never replace
        # it with a repaired scientific value, a null, or a V4 FailureReceipt.
        error = {
            "kind": "capture",
            "diagnostics": capture_errors
            + (error["diagnostics"] if error is not None else []),
        }
    checks: list[dict[str, Any]] = []
    if error is None:
        error = comparison_error(data, expected, observed)
    checks.append(
        {
            "check": "independent_negative_prefix_and_bindings",
            "passed": error is None,
            "error": error,
        }
    )
    report = {
        "schema": "p925_harness_observation_failure_v1"
        if capture_errors
        else "p925_prefix_assessment_v1",
        "fixture": data,
        "expected": expected,
        "actual": observed,
        "checks": checks,
        "passed": error is None,
        "invocations": 1,
        "evidence_class": "executed_negative_duration_prefix"
        if operation is None
        else "harness_mutation_control",
        "runtime_profile_conformance": False,
        "parent_lineage_validated": False,
        "comparison_policy": {
            "mode": "exact_payload_and_receipt_identity",
            "numeric_tolerance": None,
        },
        "request_jcs_hex": canonical_json_bytes(data["request"]).hex(),
    }
    return parse_record(record_bytes(report))


def provenance(root: Path) -> dict[str, Any]:
    bindings = [file_binding(root, name) for name in SOURCE_PATHS]
    checker_bindings = []
    for checker_origin, path, imported_hash in (
        (__file__, SOURCE_PATHS[0], IMPORTED_SOURCE_SHA256),
        (oracle.__file__, SOURCE_PATHS[1], oracle.IMPORTED_SOURCE_SHA256),
    ):
        if Path(checker_origin).resolve() != relative_file(root, path).resolve():
            raise HarnessError("foreign harness or oracle origin")
        row = file_binding(root, path)
        same(
            row["sha256"],
            imported_hash,
            "checker changed since import; use a fresh process",
        )
        checker_bindings.append(row)
    loaded = []
    # Bind the actually imported repository modules, not merely same-named
    # files on disk. A foreign installed pygrc cannot borrow checkout identity.
    for name, module in sorted(tuple(sys.modules.items())):
        if name != "pygrc" and not name.startswith("pygrc."):
            continue
        origin = Path(getattr(module, "__file__", "")).resolve()
        if not origin.is_file() or not origin.is_relative_to(
            (root / "src/pygrc").resolve()
        ):
            raise HarnessError("foreign or unresolved loaded repository module")
        loaded.append(file_binding(root, origin.relative_to(root.resolve()).as_posix()))
    if not loaded:
        raise HarnessError("no loaded repository implementation")

    def git(*args: str) -> bytes:
        return subprocess.check_output(["git", "-C", str(root), *args])

    return {
        "base_commit": git("rev-parse", "HEAD").decode().strip(),
        "tracked_dirty_diff_sha256": sha256(
            git("diff", "--binary", "HEAD", "--", *SOURCE_PATHS)
        ).hexdigest(),
        "untracked_source_paths": sorted(
            git("ls-files", "--others", "--exclude-standard", "--", *SOURCE_PATHS)
            .decode()
            .splitlines()
        ),
        "source_bindings": bindings,
        "loaded_module_bindings": loaded,
        "loaded_checker_bindings": checker_bindings,
        "execution_policy": "fresh_repository_CLI; import-time_checker_hashes_are_not_bytecode_attestation",
        "environment": environment(),
        "release_id": oracle.RELEASE_ID,
        "claim_ceiling": "bounded_prefix_execution_not_runtime_profile_conformance",
    }


def validate_report(report: dict[str, Any]) -> None:
    """Verify assessment content, not the historical fact of execution."""
    if set(report) != {
        "schema",
        "fixture",
        "expected",
        "actual",
        "checks",
        "passed",
        "invocations",
        "evidence_class",
        "runtime_profile_conformance",
        "parent_lineage_validated",
        "comparison_policy",
        "request_jcs_hex",
    }:
        raise HarnessError("closed assessment fields required")
    Fixture.from_payload(report["fixture"])
    if report["schema"] not in (
        "p925_prefix_assessment_v1",
        "p925_harness_observation_failure_v1",
    ):
        raise HarnessError("unknown assessment")
    same(report["runtime_profile_conformance"], False, "unsupported conformance")
    same(report["parent_lineage_validated"], False, "unsupported lineage")
    same(report["invocations"], 1, "incorrect invocation count")
    same(
        report["request_jcs_hex"],
        canonical_json_bytes(report["fixture"]["request"]).hex(),
        "request bytes mismatch",
    )
    same(
        report["comparison_policy"],
        {"mode": "exact_payload_and_receipt_identity", "numeric_tolerance": None},
        "comparison policy changed",
    )
    if (
        report["evidence_class"]
        not in ("executed_negative_duration_prefix", "harness_mutation_control")
        or type(report["passed"]) is not bool
    ):
        raise HarnessError("invalid assessment classification")
    same(
        report["expected"],
        oracle.expected_negative(
            report["fixture"]["request"],
            report["fixture"]["prestate"],
            report["fixture"]["pre_ledger"],
        ),
        "altered expectation",
    )
    if report["passed"]:
        same(
            report["schema"], "p925_prefix_assessment_v1", "capture failure cannot pass"
        )
        assess_negative(report["fixture"], report["expected"], report["actual"])
        same(
            report["checks"],
            [
                {
                    "check": "independent_negative_prefix_and_bindings",
                    "passed": True,
                    "error": None,
                }
            ],
            "inconsistent passing checks",
        )
    else:
        if len(report["checks"]) != 1:
            raise HarnessError("inconsistent failing assessment")
        check = report["checks"][0]
        if (
            set(check) != {"check", "passed", "error"}
            or check["passed"] is not False
            or check["check"] != "independent_negative_prefix_and_bindings"
        ):
            raise HarnessError("closed failing check required")
        error = check["error"]
        if (
            type(error) is not dict
            or set(error) != {"kind", "diagnostics"}
            or error["kind"] not in ("comparison", "invocation", "capture")
        ):
            raise HarnessError("closed failure diagnostic required")
        diagnostics = error["diagnostics"]
        if type(diagnostics) is not list or not 1 <= len(diagnostics) <= 5:
            raise HarnessError("failure diagnostics required")
        for d in diagnostics:
            if (
                type(d) is not dict
                or set(d) != {"stage", "field_path", "type", "code", "representation"}
                or any(type(v) is not str or not v for v in d.values())
                or d["stage"] != "admission"
            ):
                raise HarnessError("closed observation diagnostic required")
        actual = report["actual"]
        for observed_field, fixture_field in (
            ("request", "request"),
            ("prestate", "prestate"),
            ("pre_ledger", "pre_ledger"),
            ("reset_before", "reset"),
        ):
            same(
                actual[observed_field],
                report["fixture"][fixture_field],
                "foreign failure input capture",
            )
        if error["kind"] == "comparison":
            same(
                report["schema"], "p925_prefix_assessment_v1", "wrong comparison schema"
            )
            reconstructed = comparison_error(
                report["fixture"], report["expected"], actual
            )
            if reconstructed is None:
                raise HarnessError("passing comparison relabelled as failure")
            same(error, reconstructed, "comparison diagnostic mismatch")
        else:
            # Exception/encoding occurrence is recorded, not independently
            # re-executed here. Its envelope and missing-capture scope are checked.
            capture_fields = {"poststate", "post_ledger", "reset_after", "result"}
            missing: set[str] = set()
            for d in diagnostics:
                if d["code"] == "operation_raised":
                    same(d["field_path"], "$.operation", "wrong invocation path")
                    missing.add("result")
                elif error["kind"] == "capture" and d["code"] in {
                    "missing_subject_field",
                    "capture_depth_limit",
                    "invalid_float",
                    "unsafe_integer",
                    "invalid_unicode",
                    "unsupported_type",
                    "cyclic_container",
                    "non_string_key",
                }:
                    field = d["field_path"].removeprefix("$.").split("[", 1)[0]
                    if (
                        not d["field_path"].startswith("$.")
                        or field not in capture_fields
                    ):
                        raise HarnessError("wrong capture diagnostic path")
                    missing.add(field)
                else:
                    raise HarnessError("unsupported failure diagnostic")
            same(
                sorted(capture_fields - actual.keys()),
                sorted(missing),
                "missing capture/diagnostic mismatch",
            )
            expected_schema = (
                "p925_harness_observation_failure_v1"
                if error["kind"] == "capture"
                else "p925_prefix_assessment_v1"
            )
            same(report["schema"], expected_schema, "wrong failure schema")
            if error["kind"] == "invocation" and len(diagnostics) != 1:
                raise HarnessError("one recorded invocation error required")
            if error["kind"] == "capture" and all(
                d["code"] == "operation_raised" for d in diagnostics
            ):
                raise HarnessError("capture failure requires a capture diagnostic")


def retain_run(
    root: Path,
    relative_dir: str,
    report: dict[str, Any],
    source: dict[str, Any],
    command: str,
) -> dict[str, Any]:
    """Write a new run under the existing evidence vocabulary; never overwrite."""
    import re

    if (
        re.fullmatch(
            r"implementation/phase-9-grcv4/evidence/P9-2\.5/[A-Za-z0-9][A-Za-z0-9_-]{0,95}",
            relative_dir,
        )
        is None
    ):
        raise HarnessError("registered P9-2.5 run directory required")
    directory = relative_file(root, relative_dir)
    validate_report(report)
    same(
        report["fixture"],
        oracle.prefix_fixture(),
        "CLI retention supports only the exact default fixture",
    )
    same(
        report["evidence_class"],
        "executed_negative_duration_prefix",
        "CLI retention cannot reproduce control callbacks",
    )
    same(
        report["schema"],
        "p925_prefix_assessment_v1",
        "capture diagnostics use the separate test-evidence route",
    )
    verify_bindings(root, source["source_bindings"])
    same(source, provenance(root), "source or execution environment changed")
    expected_command = (
        ".venv/bin/python -m tests.models.grcv4_conformance_harness --output "
        + relative_dir
    )
    same(command, expected_command, "nonportable or foreign reproduction command")
    files = {
        "inputs.json": report["fixture"],
        "expected.json": report["expected"],
        "actual.json": report,
        "receipts.json": {
            "emitted_delta": report["actual"]
            .get("result", {})
            .get("emitted_receipts", []),
            "pre_ledger": report["actual"]["pre_ledger"],
            "post_ledger": report["actual"]["post_ledger"],
        },
    }
    if any((directory / name).exists() for name in (*files, "run.json")):
        raise HarnessError(
            "run exists; choose a new run ID instead of overwriting evidence"
        )
    encoded = {name: record_bytes(value) + b"\n" for name, value in files.items()}
    manifest = {
        "schema": "phase9_prefix_execution_run_v1",
        "iteration_id": "P9-2.5",
        "run_id": str(uuid.uuid4()),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        **source,
        "evidence_class": report["evidence_class"],
        "passed": report["passed"],
        "command": command,
        "artifacts": [
            {"path": relative_dir + "/" + name, "sha256": sha256(raw).hexdigest()}
            for name, raw in sorted(encoded.items())
        ],
        "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
        "review_disposition": "pending_user_review",
        "parent_lineage_validated": False,
    }
    directory.mkdir(parents=True, exist_ok=True)
    for name, raw in encoded.items():
        with (directory / name).open("xb") as handle:
            handle.write(raw)
    with (directory / "run.json").open("xb") as handle:
        handle.write(record_bytes(manifest) + b"\n")
    return manifest


def inspect_run(root: Path, relative_dir: str) -> dict[str, Any]:
    """Inspect original output without executing or replacing it.

    Hash linkage is integrity, not an authenticated execution/acceptance token.
    Current-source equality is reported separately from historical consistency.
    """
    directory = relative_file(root, relative_dir)
    manifest = parse_record((directory / "run.json").read_bytes().removesuffix(b"\n"))
    same(manifest["schema"], "phase9_prefix_execution_run_v1", "unknown run")
    for field in (
        "accepted_generic_runtime_support",
        "admitted_specialization_support_sets",
    ):
        same(manifest[field], [], "run cannot promote support")
    same(manifest["parent_lineage_validated"], False, "run cannot certify lineage")
    if manifest["release_id"] not in {oracle.RELEASE_ID, oracle.PREDECESSOR_RELEASE_ID}:
        raise HarnessError("foreign release")
    names = ["actual.json", "expected.json", "inputs.json", "receipts.json"]
    same(
        [r["path"] for r in manifest["artifacts"]],
        [relative_dir + "/" + n for n in names],
        "foreign run artifacts",
    )
    verify_bindings(root, manifest["artifacts"])
    records = {
        name: parse_record((directory / name).read_bytes().removesuffix(b"\n"))
        for name in names
    }
    report = records["actual.json"]
    validate_report(report)
    same(records["inputs.json"], report["fixture"], "foreign fixture")
    same(records["expected.json"], report["expected"], "foreign expectation")
    same(
        records["receipts.json"],
        {
            "emitted_delta": report["actual"]
            .get("result", {})
            .get("emitted_receipts", []),
            "pre_ledger": report["actual"]["pre_ledger"],
            "post_ledger": report["actual"]["post_ledger"],
        },
        "foreign receipt delta or persistent ledger",
    )
    for field in ("evidence_class", "passed"):
        same(manifest[field], report[field], "manifest assessment mismatch")
    same(
        [r["path"] for r in manifest["source_bindings"]],
        list(SOURCE_PATHS),
        "incomplete source bindings",
    )
    if "loaded_checker_bindings" in manifest:
        same(
            [r["path"] for r in manifest["loaded_checker_bindings"]],
            list(SOURCE_PATHS[:2]),
            "incomplete loaded checker bindings",
        )
    try:
        verify_bindings(root, manifest["source_bindings"])
        if "loaded_module_bindings" in manifest:
            verify_bindings(root, manifest["loaded_module_bindings"])
        if "loaded_checker_bindings" in manifest:
            verify_bindings(root, manifest["loaded_checker_bindings"])
        current = True
    except (OSError, ValueError):
        current = False
    return {
        "record_integrity": "verified_not_execution_authority",
        "recorded_assessment_passed": report["passed"],
        "evidence_class": report["evidence_class"],
        "runtime_profile_conformance": False,
        "parent_lineage_validated": False,
        "failure_evidence_basis": "independent_comparison"
        if report["passed"]
        else report["checks"][0]["error"]["kind"] + "_diagnostic_not_reexecuted",
        "current_source_bytes_match": current,
        "current_environment_matches": environment() == manifest["environment"],
        "loaded_module_provenance_bound": "loaded_module_bindings" in manifest,
        "loaded_checker_provenance_bound": "loaded_checker_bindings" in manifest,
        "run_id": manifest["run_id"],
    }


class HarnessTests(unittest.TestCase):
    def fixture(self) -> Fixture:
        return Fixture.from_payload(oracle.prefix_fixture())

    def test_real_prefix_compared_to_independent_expected_bytes(self) -> None:
        report = run_negative(self.fixture())
        self.assertTrue(report["passed"], report["checks"])
        self.assertEqual(report["evidence_class"], "executed_negative_duration_prefix")
        self.assertEqual(report["invocations"], 1)
        self.assertFalse(report["runtime_profile_conformance"])
        self.assertFalse(report["parent_lineage_validated"])
        self.assertEqual(report["actual"]["prestate"], report["actual"]["poststate"])

    def test_nonnegative_requests_never_become_completed_prefix_runs(self) -> None:
        for dt in [0, 5e-324, 0.25, 1e308]:
            data = oracle.prefix_fixture()
            data["request"]["dt"] = dt
            calls: list[bool] = []

            def forbidden(*args: Any) -> Any:
                calls.append(True)
                raise AssertionError("must not execute")

            with self.assertRaises(ValueError):
                run_negative(Fixture.from_payload(data), operation=forbidden)
            self.assertEqual(calls, [])

    def test_exact_request_distinction_survives_equal_failure_receipts(self) -> None:
        records = []
        for dt, context in [
            (-0.25, {}),
            (-1, {"input": [True, "α"]}),
            (-5e-324, {}),
            (-1e308, {}),
        ]:
            data = oracle.prefix_fixture()
            data["request"].update(dt=dt, context_value=context)
            records.append(run_negative(Fixture.from_payload(data)))
        self.assertTrue(all(r["passed"] for r in records))
        self.assertEqual(len({r["request_jcs_hex"] for r in records}), 4)
        self.assertEqual(
            len(
                {
                    r["actual"]["result"]["emitted_receipts"][0]["receipt_id"]
                    for r in records
                }
            ),
            1,
        )

    def test_fixture_and_report_are_detached_and_forged_values_revalidate(self) -> None:
        data = oracle.prefix_fixture()
        fixture = Fixture.from_payload(data)
        data["prestate"]["authoritative"]["C"][0] = 99
        self.assertEqual(fixture.to_payload()["prestate"]["authoritative"]["C"][0], 0.5)
        self.assertTrue(run_negative(fixture)["passed"])
        object.__setattr__(fixture, "payload_bytes", b"{}")
        with self.assertRaises(HarnessError):
            run_negative(fixture)
        with self.assertRaises(HarnessError):
            Fixture(bytearray(b"{}"))  # type: ignore[arg-type]

    def test_reference_identity_and_dimensions_fail_before_invocation(self) -> None:
        for change in [
            "profile",
            "graph",
            "reset",
            "hodge",
            "K4",
            "C",
            "context",
            "extra",
            "support",
        ]:
            data = oracle.prefix_fixture()
            if change == "profile":
                data["source_profile_id"] = "grcv4-profile-sha256:" + "a" * 64
            elif change == "graph":
                data["graph"]["edges"][0]["edge_id"] = "foreign"
            elif change == "reset":
                data["reset"]["authoritative"]["C"][0] = 2
            elif change == "hodge":
                data["reference_hodge"]["edge_weights"]["e0"] = 4
            elif change == "K4":
                data["K4_base"]["K4_base"] = [[1]]
            elif change == "C":
                data["prestate"]["authoritative"]["C"].pop()
            elif change == "context":
                data["context_contract"]["value"] = {"hidden": 1}
            elif change == "extra":
                data["capability"] = "supported"
            else:
                data["domain_status"] = "admitted"
            with (
                self.subTest(change=change),
                self.assertRaises((ValueError, TypeError)),
            ):
                Fixture.from_payload(data)

    def test_record_codec_rejects_ambiguous_unordered_and_invalid_values(self) -> None:
        for raw in [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":-0.0}', b"{}\n", b"[]"]:
            with self.assertRaises((ValueError, TypeError)):
                parse_record(raw)
        for value in [
            {1: 2},
            {"x": set()},
            {"x": b"raw"},
            {"x": -0.0},
            {"x": 2**53},
            {"x": "\ud800"},
        ]:
            with self.assertRaises((ValueError, TypeError, UnicodeError)):
                record_bytes(value)
        self.assertNotEqual(record_bytes({"x": True}), record_bytes({"x": 1}))

    def test_rehashed_wrong_source_and_foreign_request_are_rejected(self) -> None:
        report = run_negative(self.fixture())
        for field in ("prestate", "request", "result", "outcome", "reset_after"):
            observed = deepcopy(report["actual"])
            if field == "prestate":
                observed[field]["authoritative"]["C"] = [1, 1, 1]
            elif field == "request":
                observed[field]["operation_id"] = "foreign"
            elif field == "result":
                receipt = observed[field]["emitted_receipts"][0]
                receipt["identity_payload"]["source_state_digest"] = (
                    "grcv4-state-sha256:" + "f" * 64
                )
                receipt["identity_payload"]["observed_poststate_digest"] = receipt[
                    "identity_payload"
                ]["source_state_digest"]
                receipt["receipt_id"] = oracle.identity(
                    "grc-receipt-sha256", receipt["identity_payload"]
                )
            elif field == "outcome":
                observed[field]["solver"] = "valid_root"
            else:
                observed[field]["authoritative"]["C"] = [0, 0, 3]
            with self.subTest(field=field), self.assertRaises((ValueError, TypeError)):
                assess_negative(report["fixture"], report["expected"], observed)

    def test_mutating_operation_is_a_failing_control_not_an_accepted_rejection(
        self,
    ) -> None:
        for changed in ("state", "ledger", "reset"):

            def mutate(
                req: GRCV4StepRequestInput, subject: dict[str, Any]
            ) -> GRCV4StepResult:
                result = production.negative_duration_result(
                    req,
                    prestate=subject["state"],
                    receipt_ledger=subject["ledger"],
                    active_profile_id=subject["state"]["active_model_identity"],
                )[0]
                if changed == "ledger":
                    subject["ledger"].append(result.emitted_receipts[0].to_payload())
                else:
                    subject[changed]["authoritative"]["C"][0] = 99
                return result

            report = run_negative(self.fixture(), operation=mutate)
            self.assertFalse(report["passed"], changed)
            self.assertEqual(report["evidence_class"], "harness_mutation_control")

    def test_noop_imported_result_does_not_receive_execution_class(self) -> None:
        prior = run_negative(self.fixture())
        result = GRCV4StepResult.from_payload(prior["actual"]["result"])
        report = run_negative(self.fixture(), operation=lambda req, subject: result)
        self.assertTrue(report["passed"])
        self.assertEqual(report["evidence_class"], "harness_mutation_control")

    def test_full_ledger_detects_commit_envelope_change_with_unchanged_receipt_ids(
        self,
    ) -> None:
        data = oracle.prefix_fixture()
        # Hand-built historical content only, deliberately not DAG admission.
        state = data["prestate"]
        core: dict[str, Any] = {
            "operation_id": "prior:step",
            "actual_charge_delta": 0,
            "information_losses": [],
            "disposition": "committed",
            "parent_receipt_ids": [],
            "resource_transform_digest": "grcv4-resource-transform-sha256:" + "2" * 64,
            "history_bundle_digest": "grcv4-history-map-sha256:" + "3" * 64,
        }
        for side in ("source", "target"):
            for key, value in {
                "state_digest": oracle.scientific_id(state),
                "graph_digest": state["graph_digest"],
                "model_identity": state["active_model_identity"],
                "authoritative_digest": oracle.identity(
                    "grcv4-authoritative-sha256", state["authoritative"]
                ),
                "reset_digest": state["reset_digest"],
            }.items():
                core[side + "_" + key] = value
        payload = {"schema_version": "grcv4-step-commit-receipt-v1", "core": core}
        data["pre_ledger"] = [
            {
                "schema_version": "grcv4-successful-receipt-envelope-v1",
                "receipt_id": oracle.identity("grc-receipt-sha256", payload),
                "commit_id": "grc-commit-sha256:" + "4" * 64,
                "identity_payload": payload,
            }
        ]
        report = run_negative(Fixture.from_payload(data))
        self.assertTrue(report["passed"], report["checks"])
        self.assertEqual(len(report["actual"]["post_ledger"]), 1)
        self.assertNotEqual(
            report["actual"]["post_ledger"],
            report["actual"]["result"]["emitted_receipts"],
        )
        bad = deepcopy(report["actual"])
        bad["post_ledger"][0]["commit_id"] = "grc-commit-sha256:" + "5" * 64
        self.assertEqual(
            oracle.lifecycle_id(state, bad["pre_ledger"]),
            oracle.lifecycle_id(state, bad["post_ledger"]),
        )
        with self.assertRaisesRegex(HarnessError, "persistent ledger changed"):
            assess_negative(data, report["expected"], bad)

    def test_production_checker_bypass_does_not_choose_expected_values(self) -> None:
        report = run_negative(self.fixture())
        bad = deepcopy(report["actual"])
        bad["poststate"]["authoritative"]["C"][0] = 9
        with patch.object(production, "bind_step_result", return_value=None):
            with self.assertRaisesRegex(HarnessError, "scientific payload changed"):
                assess_negative(report["fixture"], report["expected"], bad)

    def test_invalid_transition_characterizations_are_rejected_by_fixture_oracle(
        self,
    ) -> None:
        pre = oracle.prefix_fixture()["prestate"]
        for dt, changes in [
            (0.25, {"time": 99}),
            (0.25, {"step_index": 3}),
            (0.25, {"step_index": 2, "time": 0.25}),
            (0, {"authoritative": {"C": [1, 1, 1], "W_A": None, "Z_4": None}}),
        ]:
            post = deepcopy(pre)
            post.update(step_index=4, time=1)
            if dt == 0:
                post = deepcopy(pre)
            post.update(changes)
            with self.assertRaises(HarnessError):
                ordinary_clock_controls(pre, {"dt": dt}, post)
        post = deepcopy(pre)
        post["step_index"] = 4
        ordinary_clock_controls(pre, {"dt": 5e-324}, post)

    def test_paths_and_source_identity_are_portable_and_fail_closed(self) -> None:
        for path in ["/absolute", "../escape", "a/../b", "a//b", "./a", "a\\b", ""]:
            with self.assertRaises(HarnessError):
                relative_file(ROOT, path)
        rows = [file_binding(ROOT, SOURCE_PATHS[0])]
        verify_bindings(ROOT, rows)
        with self.assertRaises(HarnessError):
            verify_bindings(ROOT, rows * 2)
        rows[0]["sha256"] = "0" * 64
        with self.assertRaises(HarnessError):
            verify_bindings(ROOT, rows)

    def test_expected_payload_and_passing_label_cannot_be_rehashed_into_authority(
        self,
    ) -> None:
        report = run_negative(self.fixture())
        for field in (
            "expected",
            "actual",
            "request_jcs_hex",
            "runtime_profile_conformance",
            "parent_lineage_validated",
            "comparison_policy",
            "checks",
        ):
            bad = deepcopy(report)
            if field == "expected":
                bad[field]["poststate"]["authoritative"]["C"][0] = 9
            elif field == "actual":
                bad[field]["outcome"]["code"] = "domain_failure"
            elif field == "request_jcs_hex":
                bad[field] = "00"
            elif field in ("runtime_profile_conformance", "parent_lineage_validated"):
                bad[field] = True
            else:
                bad[field] = {}
            with self.subTest(field=field), self.assertRaises((ValueError, TypeError)):
                validate_report(parse_record(record_bytes(bad)))

    def test_retained_run_is_portable_inspectable_and_never_overwritten(self) -> None:
        import shutil

        scratch = (
            ROOT
            / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/tool/generated"
        )
        scratch.mkdir(parents=True, exist_ok=True)
        report = run_negative(self.fixture())
        source = provenance(ROOT)
        relative = "implementation/phase-9-grcv4/evidence/P9-2.5/test-run"
        command = (
            ".venv/bin/python -m tests.models.grcv4_conformance_harness --output "
            + relative
        )
        with tempfile.TemporaryDirectory(prefix="p925-retention-", dir=scratch) as temp:
            root = Path(temp)
            for row in source["source_bindings"]:
                target = relative_file(root, row["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], target)
            for row in source["loaded_module_bindings"]:
                target = relative_file(root, row["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], target)
            # Isolate git provenance only; exact source bytes and environment
            # are still verified. No runtime code is imported from this copy.
            with patch(__name__ + ".provenance", return_value=source):
                retain_run(root, relative, report, source, command)
                with self.assertRaisesRegex(HarnessError, "run exists"):
                    retain_run(root, relative, report, source, command)
                for field in ("base_commit", "environment", "source_bindings"):
                    bad = deepcopy(source)
                    bad[field] = [] if field == "source_bindings" else "changed"
                    with self.assertRaises((ValueError, TypeError)):
                        retain_run(root, relative, report, bad, command)
            inspected = inspect_run(root, relative)
            self.assertTrue(inspected["current_source_bytes_match"])
            self.assertTrue(inspected["recorded_assessment_passed"])
            self.assertEqual(
                inspected["evidence_class"], "executed_negative_duration_prefix"
            )
            self.assertFalse(inspected["runtime_profile_conformance"])
            self.assertFalse(inspected["parent_lineage_validated"])
            self.assertTrue(inspected["loaded_checker_provenance_bound"])
            # An existing inspection-only control must remain a control in the
            # summary. New CLI-backed retention rejects such callbacks below.
            actual_path, manifest_path = (
                root / relative / "actual.json",
                root / relative / "run.json",
            )
            old_actual, old_manifest = (
                actual_path.read_bytes(),
                manifest_path.read_bytes(),
            )
            control = deepcopy(report)
            control["evidence_class"] = "harness_mutation_control"
            actual_path.write_bytes(record_bytes(control) + b"\n")
            manifest = json.loads(old_manifest)
            manifest["evidence_class"] = "harness_mutation_control"
            for row in manifest["artifacts"]:
                if row["path"].endswith("/actual.json"):
                    row["sha256"] = sha256(actual_path.read_bytes()).hexdigest()
            manifest_path.write_bytes(record_bytes(manifest) + b"\n")
            self.assertEqual(
                inspect_run(root, relative)["evidence_class"],
                "harness_mutation_control",
            )
            actual_path.write_bytes(old_actual)
            manifest_path.write_bytes(old_manifest)
            (root / SOURCE_PATHS[0]).write_bytes(b"changed source")
            self.assertFalse(inspect_run(root, relative)["current_source_bytes_match"])
            actual = root / relative / "actual.json"
            actual.write_bytes(b"{}\n")
            with self.assertRaisesRegex(HarnessError, "source bytes changed"):
                inspect_run(root, relative)

    def test_oracles_and_production_keep_one_way_import_boundary(self) -> None:
        import ast

        def imports(path: Path) -> list[str]:
            result: list[str] = []
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.Import):
                    result.extend(x.name for x in node.names)
                elif isinstance(node, ast.ImportFrom):
                    result.append(node.module or "")
            return result

        self.assertFalse(
            any(
                x.startswith(("pygrc", "numpy", "tests"))
                for x in imports(Path(oracle.__file__))
            )
        )
        for path in (ROOT / "src/pygrc/models").glob("grc_v4*.py"):
            self.assertFalse(
                any(
                    "grcv4_reference_oracles" in x or "grcv4_conformance_harness" in x
                    for x in imports(path)
                )
            )

    def test_foreign_loaded_code_cannot_borrow_repository_source_identity(self) -> None:
        with patch.object(
            production, "__file__", str(ROOT / "foreign-installed-module.py")
        ):
            with self.assertRaisesRegex(HarnessError, "foreign or unresolved"):
                provenance(ROOT)

    def test_fresh_interpreter_binds_lazy_assets_before_execution(self) -> None:
        command = [
            sys.executable,
            "-c",
            (
                "from tests.models.grcv4_conformance_harness import "
                "Fixture, ROOT, oracle, provenance, run_negative, same; "
                "fixture=Fixture.from_payload(oracle.prefix_fixture()); "
                "before=provenance(ROOT); "
                "report=run_negative(fixture); "
                "same(before,provenance(ROOT),'execution source changed'); "
                "assert report['passed'], report['checks']"
            ),
        ]
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_large_time_is_oracle_unavailable_before_any_operation(self) -> None:
        for value in [2.0**36 + 1 / 64, 1e15 + 0.25]:
            data = oracle.prefix_fixture()
            data["prestate"]["time"] = value
            fixture = Fixture.from_payload(data)  # Scientific binary64 remains valid.
            calls: list[bool] = []
            with self.assertRaises(oracle.OracleDomainError):
                run_negative(fixture, operation=lambda *a: calls.append(True))  # type: ignore[arg-type]
            self.assertEqual(calls, [])
            # Current production still accepts the input; the narrowed oracle
            # is unavailable, not a failing production/clock/domain result.
            result = production.negative_duration_result(
                GRCV4StepRequestInput.from_payload(data["request"]),
                prestate=data["prestate"],
                receipt_ledger=data["pre_ledger"],
                active_profile_id=data["source_profile_id"],
            )[0]
            self.assertEqual(result.to_payload()["operation_disposition"], "rejected")

    def test_cli_retention_rejects_nondefault_fixture_and_control_before_writing(
        self,
    ) -> None:
        data = oracle.prefix_fixture()
        data["request"].update(dt=-1, context_value={"custom": True})
        base = run_negative(self.fixture())
        custom = run_negative(Fixture.from_payload(data))
        control = run_negative(
            self.fixture(),
            operation=lambda *a: GRCV4StepResult.from_payload(base["actual"]["result"]),
        )
        self.assertEqual(
            custom["actual"]["result"]["emitted_receipts"],
            base["actual"]["result"]["emitted_receipts"],
        )
        self.assertNotEqual(custom["request_jcs_hex"], base["request_jcs_hex"])
        for report, reason in [
            (custom, "exact default fixture"),
            (control, "control callbacks"),
        ]:
            relative = (
                "implementation/phase-9-grcv4/evidence/P9-2.5/rejected-"
                + uuid.uuid4().hex
            )
            command = (
                ".venv/bin/python -m tests.models.grcv4_conformance_harness --output "
                + relative
            )
            with patch(
                __name__ + ".provenance",
                side_effect=AssertionError("must reject before retention"),
            ):
                with self.assertRaisesRegex(HarnessError, reason):
                    retain_run(ROOT, relative, report, {}, command)
            self.assertFalse((ROOT / relative).exists())

    def test_malformed_capture_is_diagnostic_only_and_preserves_valid_inputs(
        self,
    ) -> None:
        class Hostile:
            def __repr__(self) -> str:
                raise AssertionError("do not call repr hooks")

            def __deepcopy__(self, memo: Any) -> Any:
                raise AssertionError("do not call copy hooks")

        cycle: list[Any] = []
        cycle.append(cycle)
        base = run_negative(self.fixture())
        for value, code in [
            (float("nan"), "invalid_float"),
            (float("inf"), "invalid_float"),
            (-0.0, "invalid_float"),
            (Hostile(), "unsupported_type"),
            (cycle, "cyclic_container"),
            ("\ud800", "invalid_unicode"),
            (2**53, "unsafe_integer"),
            ({1: "x"}, "non_string_key"),
        ]:

            def mutate(
                req: GRCV4StepRequestInput, subject: dict[str, Any]
            ) -> GRCV4StepResult:
                subject["state"]["authoritative"]["C"][0] = value
                return GRCV4StepResult.from_payload(base["actual"]["result"])

            report = run_negative(self.fixture(), operation=mutate)
            validate_report(report)
            self.assertFalse(report["passed"])
            self.assertEqual(report["schema"], "p925_harness_observation_failure_v1")
            self.assertEqual(report["evidence_class"], "harness_mutation_control")
            self.assertNotIn("poststate", report["actual"])
            self.assertEqual(report["actual"]["prestate"], base["actual"]["prestate"])
            self.assertEqual(report["expected"], base["expected"])
            diagnostic = report["checks"][0]["error"]["diagnostics"][0]
            self.assertEqual(diagnostic["code"], code)
            self.assertTrue(
                diagnostic["field_path"].startswith(
                    '$.poststate["authoritative"]["C"][0]'
                )
            )
            self.assertEqual(parse_record(record_bytes(report)), report)
            for key, replacement in [
                ("stage", "solve"),
                ("field_path", "$.unobserved"),
                ("code", "valid_root"),
            ]:
                bad = deepcopy(report)
                bad["checks"][0]["error"]["diagnostics"][0][key] = replacement
                with self.assertRaises(HarnessError):
                    validate_report(bad)

    def test_missing_subject_and_invocation_errors_are_separate_from_comparisons(
        self,
    ) -> None:
        base = run_negative(self.fixture())
        for field in ("state", "ledger", "reset"):

            def remove(
                req: GRCV4StepRequestInput, subject: dict[str, Any]
            ) -> GRCV4StepResult:
                del subject[field]
                return GRCV4StepResult.from_payload(base["actual"]["result"])

            report = run_negative(self.fixture(), operation=remove)
            validate_report(report)
            self.assertEqual(report["checks"][0]["error"]["kind"], "capture")
            self.assertEqual(
                report["checks"][0]["error"]["diagnostics"][0]["code"],
                "missing_subject_field",
            )

        def raises(
            req: GRCV4StepRequestInput, subject: dict[str, Any]
        ) -> GRCV4StepResult:
            raise RuntimeError("local exception text must not be exported")

        report = run_negative(self.fixture(), operation=raises)
        validate_report(report)
        self.assertEqual(report["checks"][0]["error"]["kind"], "invocation")
        self.assertNotIn("local exception text", record_bytes(report).decode())

    def test_failed_reports_require_closed_diagnostics_and_actual_comparison_failure(
        self,
    ) -> None:
        base = run_negative(self.fixture())
        for checks in [
            [{"passed": False}],
            [
                {
                    "check": "independent_negative_prefix_and_bindings",
                    "passed": False,
                    "error": "wrong",
                }
            ],
        ]:
            bad = deepcopy(base)
            bad.update(passed=False, checks=checks)
            with self.assertRaises(HarnessError):
                validate_report(bad)

        def mutate(
            req: GRCV4StepRequestInput, subject: dict[str, Any]
        ) -> GRCV4StepResult:
            subject["state"]["authoritative"]["C"][0] = 99
            return GRCV4StepResult.from_payload(base["actual"]["result"])

        failed = run_negative(self.fixture(), operation=mutate)
        validate_report(failed)
        bad = deepcopy(base)
        bad.update(passed=False, checks=deepcopy(failed["checks"]))
        with self.assertRaisesRegex(HarnessError, "passing comparison relabelled"):
            validate_report(bad)
        failed["checks"][0]["error"]["diagnostics"][0]["representation"] = (
            "forged reason"
        )
        with self.assertRaisesRegex(HarnessError, "diagnostic mismatch"):
            validate_report(failed)

    def test_checker_origins_and_import_time_hashes_are_bound(self) -> None:
        self.fixture()
        source = provenance(ROOT)
        self.assertEqual(
            [r["path"] for r in source["loaded_checker_bindings"]],
            list(SOURCE_PATHS[:2]),
        )
        for module in (sys.modules[__name__], oracle):
            with patch.object(module, "__file__", str(ROOT / "foreign-checker.py")):
                with self.assertRaisesRegex(HarnessError, "foreign harness or oracle"):
                    provenance(ROOT)
            with patch.object(module, "IMPORTED_SOURCE_SHA256", "0" * 64):
                with self.assertRaisesRegex(HarnessError, "changed since import"):
                    provenance(ROOT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        required=True,
        help="new repository-relative P9-2.5 evidence run directory",
    )
    args = parser.parse_args()
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        raise HarnessError("use the repository .venv")
    # Resolve fixture/schema assets before capturing the execution environment;
    # lazy package loading must not masquerade as changed executable source.
    fixture = Fixture.from_payload(oracle.prefix_fixture())
    source = provenance(ROOT)
    report = run_negative(fixture)
    command = (
        ".venv/bin/python -m tests.models.grcv4_conformance_harness --output "
        + args.output
    )
    manifest = retain_run(ROOT, args.output, report, source, command)
    print(
        json.dumps(
            {
                "passed": report["passed"],
                "evidence_class": report["evidence_class"],
                "run_id": manifest["run_id"],
                "output": args.output,
                "runtime_profile_conformance": False,
            }
        )
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

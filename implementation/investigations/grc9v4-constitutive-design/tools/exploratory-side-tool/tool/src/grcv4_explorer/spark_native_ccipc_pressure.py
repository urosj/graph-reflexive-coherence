"""Bounded native C_CI_PC pressure evidence; never a completion endpoint grant."""

import hashlib
from pathlib import Path

from .canonical import digest, load_json_object, record_digest
from .errors import SourceAdmissionError

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CCIPC-Pressure.json"
RECORD_DIGEST = "4ddef633eb50925789d5a5d7b7bd19620ba3f39f3885d972ce8d4adc8cd178aa"


def checked_record(root):
    import sys

    sys.path.insert(0, str(Path(root) / "implementation/phase-9-grcv4/verification"))
    from p991a6_aos_epoch import previous_bytes

    root = Path(root).resolve()
    value = load_json_object(root / RECORD)
    if (
        value.get("record_digest") != RECORD_DIGEST
        or record_digest(value, "record_digest") != RECORD_DIGEST
        or value.get("schema") != "grc9v4-native-ccipc-pressure-v1"
        or value.get("family") != "C_CI_PC"
        or value.get("native_endpoint_verified") is not False
        or value.get("native_completion_support") is not False
        or value.get("full_trajectory_runs") != 0
        or value.get("tests_passed") != 27
    ):
        raise SourceAdmissionError("Unbound C_CI_PC pressure or changed endpoint scope")
    for row in [*value["source_bindings"], value["evidence"]]:
        p = root / row["path"]
        try:
            raw = previous_bytes(root, row["path"])
        except ValueError as error:
            raise SourceAdmissionError(str(error)) from error
        if (
            not p.resolve().is_relative_to(root)
            or hashlib.sha256(raw).hexdigest() != row["sha256"]
        ):
            raise SourceAdmissionError(
                "Changed C_CI_PC pressure source: " + row["path"]
            )
    return value


def native_ccipc_pressure(root):
    value = checked_record(root)
    body = {
        "schema": "grc9v4_native_ccipc_pressure_surface_v1",
        "record_digest": value["record_digest"],
        "tests_passed": value["tests_passed"],
        "mutations": len(value["measurements"]["mutations"]),
        "finite_segment_directions": 60
        if value["prior_60_direction_certificate_checks_retained"]
        else 0,
        "native_endpoint_verified": False,
        "native_completion_support": False,
        "full_trajectory_runs": 0,
        "scope": value["scope"],
        "pending_campaign": value["pending_campaign"],
        "carrier_spaces": {"source": 58, "target": 46},
        "runtime_changed": value["runtime_changed"],
        "cancellation": value["measurements"]["geometry_cancellation"],
        "same_source": value["measurements"]["same_source"],
        "uncertain_inputs": value["measurements"]["uncertain_inputs"],
        "solver_work": value["measurements"]["solver_work"],
        "source_url": "/api/native-spark/c-ci-pc/pressure/source",
    }
    return dict(body, projection_digest=digest(body))


def native_ccipc_pressure_source(root):
    checked_record(root)
    return (Path(root) / RECORD).read_bytes()

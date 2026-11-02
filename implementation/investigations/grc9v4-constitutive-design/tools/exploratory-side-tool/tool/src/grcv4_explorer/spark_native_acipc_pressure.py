"""Bounded native A_CI_PC pressure evidence; never a completion endpoint grant."""

import hashlib
from pathlib import Path

from .canonical import digest, load_json_object, record_digest
from .errors import SourceAdmissionError

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-ACIPC-Pressure.json"
RECORD_DIGEST = "0cbe3e220cb28be2493efcb54b96f20221494e32f0809892956833d61aeee346"


def checked_record(root):
    import sys

    sys.path.insert(0, str(Path(root) / "implementation/phase-9-grcv4/verification"))
    root = Path(root).resolve()
    value = load_json_object(root / RECORD)
    if (
        value.get("record_digest") != RECORD_DIGEST
        or record_digest(value, "record_digest") != RECORD_DIGEST
        or value.get("schema") != "grc9v4-native-acipc-pressure-v1"
        or value.get("family") != "A_CI_PC"
        or value.get("native_endpoint_verified") is not False
        or value.get("native_completion_support") is not False
        or value.get("full_trajectory_runs") != 0
        or value.get("tests_passed") != 26
    ):
        raise SourceAdmissionError("Unbound A_CI_PC pressure or changed endpoint scope")
    for row in [*value["source_bindings"], value["evidence"]]:
        p = root / row["path"]
        try:
            raw = p.read_bytes()
        except ValueError as error:
            raise SourceAdmissionError(str(error)) from error
        if (
            not p.resolve().is_relative_to(root)
            or hashlib.sha256(raw).hexdigest() != row["sha256"]
        ):
            raise SourceAdmissionError("Changed A_CI_PC pressure source: " + row["path"])
    return value


def native_acipc_pressure(root):
    value = checked_record(root)
    body = {
        "schema": "grc9v4_native_acipc_pressure_surface_v1",
        "record_digest": value["record_digest"],
        "tests_passed": value["tests_passed"],
        "mutations": len(value["measurements"]["mutations"]),
        "finite_segment_directions": 76,
        "native_endpoint_verified": False,
        "native_completion_support": False,
        "full_trajectory_runs": 0,
        "scope": value["scope"],
        "pending_campaign": value["pending_campaign"],
        "state_channels": ["C", "W_A", "Z_4"],
        "runtime_changed": value["runtime_changed"],
        "measurements": value["measurements"],
        "elapsed_seconds": value["elapsed_seconds"],
        "evidence_bytes": (Path(root) / value["evidence"]["path"]).stat().st_size,
        "source_url": "/api/native-spark/a-ci-pc/pressure/source",
    }
    return dict(body, projection_digest=digest(body))


def native_acipc_pressure_source(root):
    checked_record(root)
    return (Path(root) / RECORD).read_bytes()

"""Bounded native A_OS pressure evidence; never a completion endpoint grant."""

import hashlib
from pathlib import Path

from .canonical import digest, load_json_object, record_digest
from .errors import SourceAdmissionError

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-AOS-Pressure.json"
RECORD_DIGEST = "53cb1d37a1181ad7d8142ec281ee4e13de25e1574ddafb480e6252fff75945b9"


def checked_record(root):
    root = Path(root).resolve()
    value = load_json_object(root / RECORD)
    if (
        value.get("record_digest") != RECORD_DIGEST
        or record_digest(value, "record_digest") != RECORD_DIGEST
        or value.get("schema") != "grc9v4-native-aos-pressure-v1"
        or value.get("family") != "A_OS"
        or value.get("native_endpoint_verified") is not False
        or value.get("native_completion_support") is not False
        or value.get("full_trajectory_runs") != 0
        or value.get("tests_passed") != 25
    ):
        raise SourceAdmissionError("Unbound A_OS pressure or changed endpoint scope")
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
            raise SourceAdmissionError("Changed A_OS pressure source: " + row["path"])
    return value


def native_aos_pressure(root):
    value = checked_record(root)
    body = {
        "schema": "grc9v4_native_aos_pressure_surface_v1",
        "record_digest": value["record_digest"],
        "tests_passed": value["tests_passed"],
        "mutations": len(value["measurements"]["mutations"]),
        "finite_segment_directions": 30
        if value["prior_30_direction_certificate_checks_retained"]
        else 0,
        "native_endpoint_verified": False,
        "native_completion_support": False,
        "full_trajectory_runs": 0,
        "scope": value["scope"],
        "pending_campaign": value["pending_campaign"],
        "state_channels": ["C", "W_A"],
        "runtime_changed": value["runtime_changed"],
        "weighted_row": value["measurements"]["weighted_row"],
        "formation": value["measurements"]["formation"],
        "next_history": value["measurements"]["next_history"],
        "lineage": value["measurements"]["lineage"],
        "split": value["measurements"]["split"],
        "mixed_derivatives": value["measurements"]["mixed_derivatives"],
        "scope_limits": value["measurements"]["domain_scope"],
        "source_url": "/api/native-spark/a-os/pressure/source",
    }
    return dict(body, projection_digest=digest(body))


def native_aos_pressure_source(root):
    checked_record(root)
    return (Path(root) / RECORD).read_bytes()

"""Source-bound C_RG2b pressure projection; no native completion grant."""

from hashlib import sha256
from pathlib import Path

from .canonical import digest, load_json_object, record_digest
from .errors import SourceAdmissionError

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CRG2b-Pressure.json"
RECORD_DIGEST = "2d81fbf0f7cce59523602449421ee27d86df4c81b2dfc277e4d3f045413883a3"


def checked_record(root):
    root = Path(root).resolve()
    value = load_json_object(root / RECORD)
    if (
        value.get("record_digest") != RECORD_DIGEST
        or record_digest(value, "record_digest") != RECORD_DIGEST
        or value.get("schema") != "grc9v4-native-crg2b-pressure-v1"
        or value.get("family") != "C_RG2b"
        or value.get("native_endpoint_verified") is not False
        or value.get("native_completion_support") is not False
        or value.get("runtime_changed") is not False
        or value.get("full_trajectory_runs") != 0
        or value.get("tests_passed") != 15
    ):
        raise SourceAdmissionError("Unbound C_RG2b pressure or changed scope")
    for row in [*value["source_bindings"], value["evidence"]]:
        p = root / row["path"]
        if (
            not p.resolve().is_relative_to(root)
            or sha256(p.read_bytes()).hexdigest() != row["sha256"]
        ):
            raise SourceAdmissionError("Changed C_RG2b pressure source: " + row["path"])
    return value


def native_crg2b_pressure(root):
    value = checked_record(root)
    body = {
        k: value[k]
        for k in (
            "record_digest",
            "tests_passed",
            "elapsed_seconds",
            "measurements",
            "scope",
            "native_endpoint_verified",
            "native_completion_support",
            "full_trajectory_runs",
            "state_channels",
            "runtime_changed",
            "pending_campaign",
        )
    }
    body.update(
        schema="grc9v4_native_crg2b_pressure_surface_v1",
        evidence_bytes=(Path(root) / value["evidence"]["path"]).stat().st_size,
        source_url="/api/native-spark/c-rg2b/pressure/source",
    )
    return dict(body, projection_digest=digest(body))


def native_crg2b_pressure_source(root):
    checked_record(root)
    return (Path(root) / RECORD).read_bytes()

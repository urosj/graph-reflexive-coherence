"""Native C_RG2b steps 1–4: current-source-bound preflight, no endpoint grant."""

import hashlib
import json
import lzma
from pathlib import Path

from .canonical import digest, record_digest
from .errors import SourceAdmissionError

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CRG2b-Preflight.json.xz"
RECORD_DIGEST = "086286549265840588354ffc98d508f1872e8dbb40b8b872661de9409f4cbe8d"
CONTENT_DIGEST = "086286549265840588354ffc98d508f1872e8dbb40b8b872661de9409f4cbe8d"


def load_json_object(path):
    try:
        value = json.loads(lzma.decompress(path.read_bytes()))
    except (OSError, lzma.LZMAError, ValueError) as error:
        raise SourceAdmissionError(
            "Cannot read compressed C_RG2b preflight"
        ) from error
    if not isinstance(value, dict):
        raise SourceAdmissionError("C_RG2b preflight must be an object")
    return value


def checked_record(root):
    root = Path(root).resolve()
    value = load_json_object(root / RECORD)
    if (
        value.get("record_digest") != RECORD_DIGEST
        or record_digest(value, "record_digest") != CONTENT_DIGEST
        or value.get("schema") != "grc9v4-native-crg2b-preflight-v1"
        or value.get("family") != "C_RG2b"
        or value.get("native_endpoint_verified") is not False
        or value.get("native_completion_support") is not False
        or value.get("full_trajectory_runs") != 0
        or value.get("user_accepted") is not False
    ):
        raise SourceAdmissionError(
            "Unbound C_RG2b preflight or changed endpoint scope"
        )
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
            raise SourceAdmissionError("Changed current C_RG2b source: " + row["path"])
    return value


def native_crg2b(root):
    from .spark_native_crg2b_pressure import native_crg2b_pressure

    value = checked_record(root)
    keys = (
        "status",
        "native_endpoint_verified",
        "native_completion_support",
        "full_trajectory_runs",
        "endpoint_expectations_verified",
        "family",
        "target_vertices",
        "target_edges",
        "numerical_policy_id",
        "certificate_precision_bits",
        "sampling_cap_seconds",
        "elapsed_seconds",
        "estimate",
        "optimization",
        "memory",
        "stop_conditions",
        "synthetic_window_scope",
        "reset_scope",
        "expected_endpoints",
    )
    body = {k: value[k] for k in keys}
    body.update(
        pressure=native_crg2b_pressure(root),
        schema="grc9v4_native_crg2b_preflight_surface_v1",
        record_digest=value["record_digest"],
        sample_counts={role: len(rows) for role, rows in value["samples"].items()},
        flint_version=value["machine"]["flint"],
        flint_threads=value["machine"]["flint_threads"],
        tests=value["tests"],
        caches=value["caches"]["final"],
        duration=value["duration"],
        state_channels=value["state_channels"],
        evidence_storage=value["evidence_storage"],
        full_domain_dimension=value["full_domain_dimension"],
        next_leaf="P9-9.1a.6-C_RG2b.5",
        source_url="/api/native-spark/c-rg2b/preflight/source",
    )
    return dict(body, projection_digest=digest(body))


def native_crg2b_source(root):
    checked_record(root)
    return lzma.decompress((Path(root) / RECORD).read_bytes())

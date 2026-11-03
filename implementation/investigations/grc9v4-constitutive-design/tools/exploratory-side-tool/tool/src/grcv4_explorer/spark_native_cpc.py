"""Native C_PC steps 1–4: current-source-bound preflight, no endpoint grant."""

import hashlib
from pathlib import Path

from .canonical import digest, load_json_object, record_digest
from .errors import SourceAdmissionError
from .spark_native_cpc_pressure import native_cpc_pressure

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.6-CPC-Preflight.json"
RECORD_DIGEST = '56177c5b39cf1bc6626057c0d45aa98e5a2d3d01149ea48a76a08b56d4023ad0'


def checked_record(root):
    import sys

    sys.path.insert(0, str(Path(root) / "implementation/phase-9-grcv4/verification"))
    from p991a6_cpc_campaign_epoch import previous_bytes

    root = Path(root).resolve()
    value = load_json_object(root / RECORD)
    if (
        value.get("record_digest") != RECORD_DIGEST
        or record_digest(value, "record_digest") != RECORD_DIGEST
        or value.get("schema") != "grc9v4-native-cpc-preflight-v1"
        or value.get("family") != "C_PC"
        or value.get("native_endpoint_verified") is not False
        or value.get("native_completion_support") is not False
        or value.get("full_trajectory_runs") != 0
        or value.get("user_accepted") is not False
    ):
        raise SourceAdmissionError("Unbound C_PC preflight or changed endpoint scope")
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
            raise SourceAdmissionError("Changed current C_PC source: " + row["path"])
    return value


def native_cpc(root):
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
        "memory",
        "stop_conditions",
        "synthetic_window_scope",
        "reset_scope",
        "expected_endpoints",
    )
    body = {k: value[k] for k in keys}
    body.update(
        pressure=native_cpc_pressure(root),
        schema="grc9v4_native_cpc_preflight_surface_v1",
        record_digest=value["record_digest"],
        sample_counts={role: len(rows) for role, rows in value["samples"].items()},
        flint_version=value["machine"]["flint"],
        flint_threads=value["machine"]["flint_threads"],
        tests=value["tests"],
        domain_cache=value["caches"]["domain_final"],
        state_channels=value["state_channels"],
        full_domain_dimension=value["full_domain_dimension"],
        precision_comparison_passed=value["precision_comparison"][
            "identical_represented_states"
        ],
        next_leaf="P9-9.1a.6-C_PC.5",
        source_url="/api/native-spark/c-pc/preflight/source",
    )
    return dict(body, projection_digest=digest(body))


def native_cpc_source(root):
    checked_record(root)
    return (Path(root) / RECORD).read_bytes()

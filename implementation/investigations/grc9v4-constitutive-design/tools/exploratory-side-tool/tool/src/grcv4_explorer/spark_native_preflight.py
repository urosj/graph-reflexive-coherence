"""Measured native C_OS cost estimate, separate from endpoint acceptance."""
from pathlib import Path
from .basin import _bound_file
from .canonical import load_json_object, record_digest, digest
from .errors import SourceAdmissionError

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.4-Preflight.json"
RECORD_DIGEST = "51cc6d92034f521b09b0a3ccfcd06c94cc1cdd835ccaadb41620d5cf2c856c29"


def checked_record(root):
    root = Path(root)
    value = load_json_object(root/RECORD)
    if (record_digest(value, "record_digest") != RECORD_DIGEST or value.get("record_digest") != RECORD_DIGEST
            or value.get("schema") != "grc9v4-native-spark-preflight-v1"
            or value.get("native_endpoint_verified") is not False or value.get("native_completion_support") is not False
            or value.get("full_trajectory_runs") != 0 or value.get("endpoint_expectations_verified") is not False):
        raise SourceAdmissionError("unbound native preflight or changed endpoint scope")
    for row in [*value["source_bindings"], value["evidence"]]:
        _bound_file(root, row["path"], row["sha256"])
    return value


def native_preflight(root):
    value = checked_record(root)
    body = dict(schema="grc9v4_native_spark_preflight_surface_v1", record_digest=value["record_digest"],
        status=value["status"], native_endpoint_verified=False, native_completion_support=False,
        full_trajectory_runs=0, family="C_OS", target_vertices=15, target_edges=16,
        sample_counts={role: len(rows) for role, rows in value["samples"].items()},
        numerical_policy_id=value["numerical_policy_id"], flint_version=value["machine"]["flint"],
        flint_threads=value["machine"]["flint_threads"], certificate_precision_bits=value["certificate_precision_bits"],
        sampling_cap_seconds=value["sampling_cap_seconds"], elapsed_seconds=value["elapsed_seconds"],
        estimate=value["estimate"], memory=value["memory"], stop_conditions=value["stop_conditions"],
        expected_endpoints=value["expected_endpoints"], endpoint_expectations_verified=False,
        synthetic_window_scope=value["synthetic_window_scope"], reset_scope=value["reset_scope"],
        graph_cache_hits=value["caches"]["final_graph"]["hits"],
        proof_cache_warm_hits=value["caches"]["proof_warm"]["hits"]-value["caches"]["proof_cold"]["hits"],
        next_leaf="P9-9.1a.5", source_url="/api/native-spark/c-os/preflight/source")
    return dict(body, projection_digest=digest(body))


def native_preflight_source(root):
    checked_record(root)
    return (Path(root)/RECORD).read_bytes()

"""Read-only native numerical-bridge evidence; no completion capability grant."""
from pathlib import Path
from .basin import _bound_file
from .canonical import load_json_object, record_digest, digest
from .errors import SourceAdmissionError

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.2-Verification.json"
RECORD_DIGEST = "fc0fc9c105bab7df9af30c5aa53297b1177d39ce68d9f95e8ee04bd596c79cc8"


def checked_record(root):
    root = Path(root)
    value = load_json_object(root / RECORD)
    if (record_digest(value, "record_digest") != value.get("record_digest") or
            value.get("record_digest") != RECORD_DIGEST or
            value.get("schema") != "grc9v4-native-spark-numerics-v1" or
            value.get("native_completion_support") is not False or
            value.get("native_endpoint_verified") is not False or
            value.get("native_owner_steps") != 0 or value.get("native_events_published") != 0):
        raise SourceAdmissionError("unbound native numerical evidence or changed scope")
    for row in value["source_bindings"]:
        _bound_file(root, row["path"], row["sha256"])
    return value


def native_cos_numerics(root):
    value = checked_record(root)
    budget = value["numerical_budget"]
    body = dict(schema="grc9v4_native_spark_numerical_surface_v1", family="C_OS",
        status=value["status"], record_digest=value["record_digest"],
        numerical_policy_id=value["numerical_policy_id"], exact_backend=value["exact_backend"],
        native_completion_support=False, native_endpoint_verified=False, user_accepted=False,
        native_kernel_steps=value["native_kernel_steps"], native_owner_steps=0,
        source_vertices=12, source_edges=13, target_vertices=15, target_edges=16,
        charge="21", duration="32", exact_charge_preserved=True,
        full_step_error=budget["full_step_error"], image_margin=budget["image_margin"],
        error_display=format(budget["error_display"], ".6g"), margin_display=format(budget["margin_display"], ".6g"),
        diagnostic_error=budget["spatial_evaluation_error"], reference_cache_verified=True,
        timings_seconds={k: format(v, ".6g") for k,v in value["timings_seconds"].items()},
        timing_scope=value["timing_scope"], next_leaf="P9-9.1a.3",
        source_url="/api/native-spark/c-os/numerical-bridge/source")
    return dict(body, projection_digest=digest(body))


def native_cos_numerics_source(root):
    checked_record(root)
    return (Path(root) / RECORD).read_bytes()

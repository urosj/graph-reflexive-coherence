"""Native lifecycle evidence projection; synthetic windows are labelled."""
from pathlib import Path
from .basin import _bound_file
from .canonical import load_json_object, record_digest, digest
from .errors import SourceAdmissionError

RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.3-Verification.json"
RECORD_DIGEST = "f5ab540b117417500a8dc28b7d8c60cf7ef4446d14296939d04e7e43bbf50cc3"


def checked_record(root):
    root = Path(root)
    value = load_json_object(root/RECORD)
    if (record_digest(value, "record_digest") != RECORD_DIGEST or value.get("record_digest") != RECORD_DIGEST
            or value.get("schema") != "grc9v4-native-spark-lifecycle-verification-v1"
            or value.get("native_completion_support") is not False or value.get("native_endpoint_verified") is not False
            or value.get("full_trajectory_runs") != 0 or value.get("user_accepted") is not False):
        raise SourceAdmissionError("unbound native lifecycle evidence or changed scope")
    for row in value["source_bindings"]:
        _bound_file(root, row["path"], row["sha256"])
    return value


def native_lifecycle(root):
    value = checked_record(root)
    keys = ("status", "tests_passed", "native_completion_support", "native_endpoint_verified",
            "user_accepted", "full_trajectory_runs", "actual_public_source_beats", "actual_public_events",
            "positive_window_fixture", "duplicate_before_completion_single_credit", "atomic_child_registration",
            "late_failure_rollback", "cold_source_event_replay", "accounting_scope", "cross_process_global_uniqueness",
            "certificate_precision_bits", "exact_charge", "duration", "next_leaf",
            "pressure_tests_passed", "mandatory_roster_checked", "duplicate_delivery_rejected",
            "pressure_scope", "deferred_pressure", "fixture_counts_scope")
    body = dict(schema="grc9v4_native_spark_lifecycle_surface_v1", record_digest=value["record_digest"],
                **{k: value[k] for k in keys}, source_url="/api/native-spark/c-os/lifecycle/source")
    return dict(body, projection_digest=digest(body))


def native_lifecycle_source(root):
    checked_record(root)
    return (Path(root)/RECORD).read_bytes()

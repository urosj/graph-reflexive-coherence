"""Exact declarations with accepted native completion evidence.

This packaged roster describes capability, not a promise of entry for arbitrary
states and not completion of the currently observed occurrence. No repository,
Git checkout or numerical replay is needed for public discovery.
"""

import json
from hashlib import sha256
from importlib.resources import files

from .grc_9_v4_completion_codec import digest

ASSET = "grc-9-v4-native-spark-support.json"
ASSET_SHA256 = "f122d3b26e27cd2feecbca7d9e0bd50966bef2e5c4a47899eb9f346c7b7a0543"


def declaration(config):
    """Bind the full static reference, specialization, policy and charge leaf."""
    return digest(
        {
            "reference": config.reference.to_payload(),
            "specialization": config.specialization.to_payload(),
            "charge": str(config.current.charge),
            "numerical_policy": config.reference.profile.NUMERICS,
        }
    )


def registry():
    raw = files("pygrc.models.grc_v4_assets").joinpath(ASSET).read_bytes()
    if sha256(raw).hexdigest() != ASSET_SHA256:
        raise ValueError("changed native spark support roster")
    return json.loads(raw)


def match(config):
    if config.policy is None:
        return None
    key = declaration(config)
    for row in registry()["families"]:
        if row["family"] == config.reference.profile.FAMILY:
            for subject in row["subjects"]:
                if subject["declaration_digest"] == key:
                    return {**row, "matched_subject": subject["role"]}
    return None


def status(config, completion):
    row = match(config)
    supported = row is not None
    return dict(
        disposition="bounded_native_spark_completion_supported"
        if supported
        else "native_spark_declaration_outside_reviewed_support",
        execution_families=[config.reference.profile.FAMILY],
        complete_profile_ids=[config.reference.profile.complete_profile_id],
        model_identities=[config.model_identity],
        compatibility_branch="enabled_spark_v4",
        full_GRC9V4_conformance=False,
        optional_completion=supported,
        native_endpoint_verified=supported,
        endpoint_verification_scope="accepted_campaign_for_exact_declaration",
        current_occurrence_completed=bool(
            completion.event is not None
            and completion.evidence is not None
            and completion.evidence.get("decision") == "completed"
        ),
        campaign_record_digest=None if row is None else row["campaign_record_digest"],
        matched_subject=None if row is None else row["matched_subject"],
        universal_entry_guarantee=False,
        hierarchy_tracking=False,
        accounting_scope="process_shared_publication_v1",
        cross_process_global_uniqueness=False,
        branch_crossing_available=False,
    )

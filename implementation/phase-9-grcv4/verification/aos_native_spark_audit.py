"""Independent A_OS stage ownership, exact edge lineage and full-state audit."""

import json
from hashlib import sha256

from aos_native_spark_oracle import (
    Reference,
    audit_read,
    classify,
    contains,
    need,
    verify_step,
)
from cos_native_spark_oracle import vector
from flint import arb_mat, ctx
from flint import fmpq as Q

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_codec import canonical_json_bytes

POLICY = "spark_aos_arb256_flux128_conductance192_v1"


def digest(value):
    return sha256(canonical_json_bytes(value)).hexdigest()


def separation(A, B):
    """A resolved lower bound, not a difference of rounded display values."""
    need((A.nrows(), A.ncols()) == (B.nrows(), B.ncols()), "same comparison space")
    lower = max(abs(x).lower().fmpq() for x in (A - B).entries())
    need(lower > 0, "mutation fixture does not resolve the proposed difference")
    return str(lower)


def fixed_read(graph, C, W, H, payload):
    expected = Reference(graph).read(arb_mat(vector(C)), arb_mat(vector(W)), H)
    need(set(payload) == set(expected), "complete fixed-H read")
    for name, value in expected.items():
        need(contains(payload[name], value), "fixed-H " + name)
    return expected


def audit_step(config, before, step, certificate=None, role="current"):
    need(step.before == before, "captured immutable prestate")
    need(
        step.profile_id == config.reference.profile.complete_profile_id,
        "actual complete profile",
    )
    need(step.numerical_policy_id == POLICY, "A_OS numerical policy")
    for read in (step.consumed_read, step.restart_read):
        need(
            read["precision_bits"] == 256 and read["numerical_policy_id"] == POLICY,
            "fixed production precision and policy",
        )
    result = verify_step(step, certificate, role)
    expected = classify(
        step.after.graph.to_payload(),
        step.after.C,
        step.after.W_A,
        config.policy.to_payload(),
    )
    report = dict(
        result,
        exact_weighted_classification={
            "basins": expected[0],
            "terminals": expected[1],
            "rows": expected[2],
        },
        actual_profile_verified=True,
    )

    return json.loads(canonical_json_bytes(report))


def audit_event(source, target, event):
    need(
        source.reference.profile.FAMILY == target.reference.profile.FAMILY == "A_OS",
        "A_OS event profiles",
    )
    need(
        event["source"] == source.current.to_payload(),
        "actual post-writer event source",
    )
    need(
        event["target_graph"] == target.reference.graph.graph_digest,
        "actual target graph",
    )
    need("carrier_history" not in event, "A_OS has no persistent Z")
    history = event["conductance_history"]
    need(
        history["disposition"] == "exact_transport"
        and history["information_loss"] == "none",
        "lossless scalar history",
    )
    old_ids = list(source.reference.graph.live_edge_ids)
    new_ids = list(target.reference.graph.live_edge_ids)
    added = sorted(set(new_ids) - set(old_ids))
    need(
        set(old_ids) <= set(new_ids) and len(added) == 3,
        "complete stable edge injection",
    )
    need(
        history["source_edge_ids"] == old_ids
        and history["target_edge_ids"] == new_ids
        and history["new_edge_ids"] == added
        and history["new_edge_seed"] == "1",
        "edge roster",
    )
    archive = {
        role: getattr(source, role).to_payload() for role in ("current", "reset")
    }
    need(history["source_archive"] == archive, "actual both-role source archive")
    content = {
        "schema_version": "grcv4-exact-conductance-history-v1",
        "subject": "candidate",
        "content": archive,
    }
    carrier = history["history_policy"]["carrier"]
    need(
        carrier["policy_id"] == "carrier_not_applicable_v1"
        and carrier["disposition"] == "not_applicable"
        and carrier["source_history_digest"] is None,
        "no inherited carrier channel",
    )
    candidate = history["history_policy"]["candidate"]
    need(
        candidate["source_history_digest"]
        == "grcv4-history-content-sha256:" + digest(content),
        "complete candidate history binding",
    )
    need(
        candidate["policy_id"]
        == "candidate_a_exact_old_edge_lineage_positive_bond_seed_v1",
        "selected lineage policy",
    )
    module = event["module"]
    need(len(module) == 4, "four-node expansion module")
    reports = {}
    for role in ("current", "reset"):
        before, after = getattr(source, role), getattr(target, role)
        old = dict(zip(old_ids, before.W_A, strict=True))
        need(
            after.W_A == tuple(old.get(edge, "1") for edge in new_ids),
            "exact old-edge lineage " + role,
        )
        C = dict(zip(before.graph.live_node_ids, map(Q, before.C), strict=True))
        actual = dict(zip(after.graph.live_node_ids, map(Q, after.C), strict=True))
        removed = set(C) - set(actual)
        need(len(removed) == 1, "one expanded source node")
        parent = next(iter(removed))
        need(parent == event["expanded"], "expanded parent identity")
        expected = {node: value for node, value in C.items() if node != parent}
        expected.update(
            {
                node: C[parent] * share
                for node, share in zip(
                    module, map(Q, ("0", "1/128", "63/64", "1/128")), strict=True
                )
            }
        )
        need(actual == expected, "A allocation, zero core and copied exterior " + role)
        need(
            sum(actual.values())
            == sum(C.values())
            == Q(before.charge)
            == Q(after.charge),
            "exact event charge",
        )
        with _ARB_CONTEXT_LOCK, ctx.workprec(768):
            audit_read(
                Reference(before.graph.to_payload()),
                before,
                history["fresh_source_reads"][role],
            )
        reports[role] = {
            "old_edges": len(old),
            "new_edges": len(added),
            "zero_core": actual[module[0]] == 0,
            "exact_charge": str(sum(actual.values())),
            "complete_history": True,
        }
    return reports

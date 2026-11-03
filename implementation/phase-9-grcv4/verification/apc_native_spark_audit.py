"""Independent A_PC stage ownership, exact edge lineage and full-state audit."""

import json
from hashlib import sha256

from apc_native_spark_pressure_oracle import (
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

POLICY = "spark_apc_arb256_flux128_conductance192_carrier192_v1"


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
    need(step.numerical_policy_id == POLICY, "A_PC numerical policy")
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
        source.reference.profile.FAMILY == target.reference.profile.FAMILY == "A_PC",
        "A_PC event profiles",
    )
    need(
        event["source"] == source.current.to_payload(),
        "actual post-writer event source",
    )
    need(
        event["target_graph"] == target.reference.graph.graph_digest,
        "actual target graph",
    )
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
    carrier = event["carrier_history"]
    need(
        carrier["disposition"] == "whole_carrier_reset"
        and carrier["information_loss"] == "carrier_history_loss"
        and carrier["target_all_dense_entries_zero"] is True
        and carrier["target_dense_entries"] == len(new_ids) ** 2,
        "explicit whole-carrier loss",
    )
    need(
        carrier["target_initializer_id"] == "canonical_zero_carrier_v1"
        and carrier["native_release"] is False
        and carrier["target_carrier_pairs"]
        == [
            list(p)
            for p in Reference(target.reference.graph.to_payload()).carrier_pairs
        ],
        "complete target carrier declaration",
    )
    need(carrier["source_archive"] == archive, "actual both-role carrier archive")
    need(
        carrier["history_policy"] == history["history_policy"], "one two-channel policy"
    )
    cp = carrier["history_policy"]["carrier"]
    need(
        cp["policy_id"] == "whole_carrier_reset_with_loss_receipt_v1"
        and cp["disposition"] == "whole_carrier_reset"
        and cp["information_loss"] == "carrier_history_loss"
        and cp["source_history_digest"]
        == "grcv4-history-content-sha256:"
        + digest(
            {
                "schema_version": "grcv4-exact-carrier-history-v1",
                "subject": "carrier",
                "content": archive,
            }
        ),
        "complete independent carrier policy binding",
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
        need(
            all(Q(x) == 0 for row in after.Z_4 for x in row),
            "whole target Z zero " + role,
        )
        need(
            carrier["fresh_source_reads"][role] == history["fresh_source_reads"][role],
            "both channels archive the same full source read",
        )
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


def audit_trace(step, trace):
    """Independently authenticate the frozen source and both writer stages."""
    from cos_native_spark_oracle import matrix
    from flint import arb

    need(
        [r["stage"] for r in trace]
        == ["incoming", "W_writer", "Z_writer", "write", "returned"],
        "exact two-read/two-writer/one-write trace",
    )
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        ref = Reference(step.before.graph.to_payload())
        for row, state in ((trace[0], step.before), (trace[-1], step.after)):
            need(row["state"] == state.to_payload(), "trace complete read state")
            audit_read(ref, state, row["read"])
        before = step.before
        r = ref.selected(
            arb_mat(vector(before.C)),
            arb_mat(vector(before.W_A)),
            arb_mat(matrix(before.Z_4)),
        )
        w, z = trace[1], trace[2]
        need(
            w["state"] == z["state"] == before.to_payload(),
            "two frozen writer subjects",
        )
        need(w["final_C"] == list(step.after.C), "W writer validated final C")
        need(
            w["held_source_before"] == w["held_source_after"] == z["source"],
            "W preparation cannot mutate held S",
        )
        need(contains(z["source"], r["source"]), "Z writer frozen incoming S")
        need(
            w["writer"] == step.writer.to_dict()
            and z["writer"] == step.carrier_writer.to_dict(),
            "actual prepared histories",
        )
        need(
            trace[3]["state"] == before.to_payload()
            and trace[3]["after"] == step.after.to_payload(),
            "one full publication",
        )
        d = (-arb(1)).exp()
        ideal_z = d * arb_mat(matrix(before.Z_4)) + (1 - d) * r["source"]
        need(contains(z["writer"]["ideal"], ideal_z), "old Z plus held S")
        need(
            contains(
                w["writer"]["exponent"],
                ref.log_drive(
                    arb_mat(vector(step.after.C)),
                    arb_mat(vector(before.W_A)),
                    r["selected"]["current"],
                ),
            ),
            "final C old W consumed J",
        )
    return {
        "fresh_reads": 2,
        "W_writers": 1,
        "Z_writers": 1,
        "full_state_writes": 1,
        "same_consumed_source": True,
        "different_writer_stages": True,
    }


def audit_probe_pair(kind, payloads):
    """Recompute both algebraic discriminators from the frozen exact subjects."""
    from cos_native_spark_oracle import incidence, matrix
    from flint import fmpq_mat as M

    from pygrc.models.grc_v4_spark_carrier import exact_state

    left, right = map(exact_state, payloads)
    need(
        left.graph == right.graph and left.C == right.C, "matched probe graph/resources"
    )
    _n, m = len(left.C), len(left.W_A)
    B, C = incidence(left.graph.to_payload()), vector(left.C)

    def diagonal(values):
        return M([[Q(values[i]) if i == j else 0 for j in range(m)] for i in range(m)])

    need(
        all(Q(99, 100) < Q(w) < Q(101, 100) for s in (left, right) for w in s.W_A),
        "probe W domain",
    )
    need(all(0 <= Q(c) <= 4 for c in left.C), "probe resource domain")
    effective = [diagonal(s.W_A) + matrix(s.Z_4) / 2 for s in (left, right)]
    site = M([[(Q(c) - 2) ** 3 - (Q(c) - 2)] for c in left.C])
    phi = [B * k * B.transpose() * C / 64 - site for k in effective]
    need(phi[0] == phi[1], "exact equal probe potential")
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        reference = Reference(left.graph.to_payload())
        a, b = [
            reference.selected(
                arb_mat(vector(s.C)), arb_mat(vector(s.W_A)), arb_mat(matrix(s.Z_4))
            )
            for s in (left, right)
        ]
        if kind == "equal_potential":
            need(effective[0] == effective[1], "compensated exact stiffness")
            delta = (
                -(diagonal(right.W_A) - diagonal(left.W_A))
                * B.transpose()
                * phi[0]
                / 1024
            )
            need(
                any(x != 0 for x in delta.entries()),
                "nonzero independent mobility change",
            )
            need(
                all(
                    x.contains(y)
                    for x, y in zip(
                        (
                            b["selected"]["baseline"] - a["selected"]["baseline"]
                        ).entries(),
                        delta.entries(),
                        strict=True,
                    )
                ),
                "exact mobility difference",
            )
            return {
                "exact_potential_equal": True,
                "effective_stiffness_equal": True,
                "current_separation": separation(
                    a["selected"]["current"], b["selected"]["current"]
                ),
            }
        need(kind == "equal_current" and left.W_A == right.W_A, "matched probe W")
        E = matrix(right.Z_4) - matrix(left.Z_4)
        need(
            E * B.transpose() * C == M(m, 1),
            "carrier perturbation annihilates resource gradient",
        )
        for key in ("baseline", "drive", "q", "current"):
            need(
                all(
                    x.contains(0)
                    for x in (a["selected"][key] - b["selected"][key]).entries()
                ),
                "matched exact " + key,
            )
        return {
            "exact_potential_equal": True,
            "exact_current_equal": True,
            "flat_separation": separation(
                a["selected"]["causal_flat"], b["selected"]["causal_flat"]
            ),
            "source_separation": separation(a["source"], b["source"]),
        }

"""Independent A_CI stage ownership, exact edge lineage and full-state audit."""

import json
from hashlib import sha256

from aci_native_spark_oracle import (
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

POLICY = "spark_aci_arb256_flux128_conductance192_v1"


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
    need(step.numerical_policy_id == POLICY, "A_CI numerical policy")
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
        source.reference.profile.FAMILY == target.reference.profile.FAMILY == "A_CI",
        "A_CI event profiles",
    )
    need(
        event["source"] == source.current.to_payload(),
        "actual post-writer event source",
    )
    need(
        event["target_graph"] == target.reference.graph.graph_digest,
        "actual target graph",
    )
    need("carrier_history" not in event, "A_CI has no persistent Z")
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


def admit_proposal(reference, C, W, proposal):
    """Independent mathematical admission, not a native warm-start policy."""
    from aos_native_spark_oracle import upper

    need(upper(proposal) < Q(1, 32), "proposal outside declared root ball")
    residual = upper(
        reference.read(C, W, reference.geometry(proposal))["causal_flat"] - proposal
    )
    error = residual / (1 - reference.rate)
    need(upper(proposal) + error < Q(1, 32), "whole root enclosure leaves ball")
    return residual, error


def derivative_mutation(math, C, L, variant):
    """Explicit faulty derivatives; independent finite segments decide rejection."""
    from unittest.mock import patch

    from flint import arb_mat

    original_parts = math.flat_partials
    original_exponent = math.exponent
    original_rows = math.rows

    def parts(c, w, flat, rows=None):
        selected, H, Ff, Jf = original_parts(c, w, flat, rows)
        if variant == "omit_Ff":
            Ff = arb_mat(math.m, math.m)
        elif variant == "freeze_root":
            Jf = arb_mat(math.m, math.m)
        elif variant == "freeze_read_drive":
            dHs = [
                arb_mat(
                    [
                        [
                            math.overlap[i][j]
                            * (
                                (flat[j, 0] if i == k else 0)
                                + (flat[i, 0] if j == k else 0)
                            )
                            / 8
                            for j in range(math.m)
                        ]
                        for i in range(math.m)
                    ]
                )
                for k in range(math.m)
            ]
            pack = lambda cols: arb_mat(
                [[cols[j][i, 0] for j in range(math.m)] for i in range(math.m)]
            )
            dj0 = (
                -math.diag(w)
                * math.Bt
                * math.B
                * pack([h * math.Bt * c for h in dHs])
                / 65536
            )
            Jf = arb_mat(
                [
                    [dj0[i, j] / (1 - selected["q"][i, 0] / 4) for j in range(math.m)]
                    for i in range(math.m)
                ]
            )
            Ff = H.solve(
                math.diag(selected["q"]) * Jf / 2
                - pack([h * selected["causal_flat"] for h in dHs])
            )
        return selected, H, Ff, Jf

    def exponent(c, *args, **kwargs):
        value, derivative = original_exponent(c, *args, **kwargs)
        if variant == "freeze_read_drive" and c is C and derivative is not None:
            derivative = arb_mat(derivative.nrows(), derivative.ncols())
        return value, derivative

    def rows(c, w, dc=None, dw=None):
        values, derivatives = original_rows(c, w, dc, dw)
        if variant == "omit_row_denominator" and dc is not None:
            for i, node_rows in enumerate(math.terms):
                for a, terms in enumerate(node_rows):
                    if terms:
                        den = sum(w[k, 0] for k, j in terms)
                        for column in range(dc.ncols()):
                            derivatives[i][a][column] += (
                                values[i][a]
                                * sum(dw[k, column] for k, j in terms)
                                / den
                            )
        return values, derivatives

    with (
        patch.object(math, "flat_partials", parts),
        patch.object(math, "exponent", exponent),
        patch.object(math, "rows", rows),
    ):
        result = math.jacobian(C, L)
    if variant in ("drop_C_from_logW", "drop_logW_from_C"):
        rr, cc = (
            (range(math.n), range(math.n, math.n + math.m))
            if variant == "drop_C_from_logW"
            else (range(math.n, math.n + math.m), range(math.n))
        )
        for i in rr:
            for j in cc:
                result[i, j] = 0
    return result


def audit_trace(step, trace):
    """Recheck retained operand ownership without running the native solver."""
    from cpc_native_spark_pressure_oracle import decode
    from flint import arb

    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        writers = [i for i, row in enumerate(trace) if row["stage"] == "writer"]
        need(len(writers) == 1, "trace one physical writer")
        need(
            sum(row["stage"] == "root_start" for row in trace) == 2,
            "trace incoming and returned root",
        )
        count = 0
        for state, records in (
            (step.before, trace[: writers[0]]),
            (step.after, trace[writers[0] + 1 :]),
        ):
            C, W = arb_mat(vector(state.C)), arb_mat(vector(state.W_A))
            with ctx.workprec(256):
                cp = arb_mat([[arb(Q(x)).mid()] for x in state.C])
                wp = arb_mat([[arb(Q(x)).mid()] for x in state.W_A])
            reads = [
                row
                for row in records
                if row["stage"] == "fixed_read" and row["phase"] == "root"
            ]
            drives = [
                row
                for row in records
                if row["stage"] == "drive" and row["phase"] == "root"
            ]
            need(
                len(reads) == len(drives) and len(reads) >= 2, "trace root evaluations"
            )
            need(
                [row["subject_mode"] for row in reads[-2:]] == ["actual_input"] * 2,
                "trace actual-input residual and enclosed root read",
            )
            for row, drive in zip(reads, drives, strict=True):
                if row["subject_mode"] == "actual_input":
                    need(
                        contains(row["C"], C) and contains(row["W"], W),
                        "trace actual frozen C/W",
                    )
                    cc, ww = state.C, state.W_A
                else:
                    need(
                        decode(row["C"]) == cp and decode(row["W"]) == wp,
                        "trace frozen proposal input midpoints",
                    )
                    cc = tuple(str(x.fmpq()) for x in cp.entries())
                    ww = tuple(str(x.fmpq()) for x in wp.entries())
                need(
                    row["C"] == drive["C"]
                    and row["W"] == drive["W"]
                    and row["result"]["baseline"] == drive["J"],
                    "trace read drive uses baseline current",
                )
                H = decode(row["H"])
                point = arb_mat(
                    [
                        [H[i, j].mid() for j in range(H.ncols())]
                        for i in range(H.nrows())
                    ]
                )
                fixed_read(state.graph.to_payload(), cc, ww, point, row["result"])
                # Reference drive is exp of this evaluation, not retained W.
                need(
                    all(
                        a.exp().overlaps(b)
                        for a, b in zip(
                            decode(drive["value"]).entries(),
                            decode(row["result"]["drive"]).entries(),
                            strict=True,
                        )
                    ),
                    "trace fresh reference evaluation",
                )
                count += 1
        drives = [
            row for row in trace if row["stage"] == "drive" and row["phase"] == "writer"
        ]
        need(len(drives) == 1, "trace one writer target")
        drive = drives[0]
        need(
            contains(drive["C"], arb_mat(vector(step.after.C)))
            and contains(drive["W"], arb_mat(vector(step.before.W_A)))
            and drive["J"] == step.writer.to_dict()["selected_current"],
            "trace final C incoming W selected J writer",
        )
        need(
            trace[writers[0]]["writer"] == step.writer.to_dict(),
            "trace committed writer witness",
        )
        return {
            "root_reads": count,
            "root_solves": 2,
            "writers": 1,
            "actual_input_admission": True,
            "proposal_midpoints_not_state": True,
        }

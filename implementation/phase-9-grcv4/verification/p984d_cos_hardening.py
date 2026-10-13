"""Bounded successor pressure; original deep campaign remains immutable.

Exact-real, pointwise Arb enclosures are distinct from represented continuity
and finite neighborhood probes. No uniform tube or public step-owner claim.
"""

import argparse
from dataclasses import replace
from fractions import Fraction as Q
import json
from unittest.mock import patch

from flint import arb, arb_mat, ctx
import p984d_cos as prior

b = prior.b
SELF = b.HERE + "p984d_cos_hardening.py"
TEST = b.HERE + "test_p984d_cos_hardening.py"
INPUTS = b.BASE + "P9-8.4d-COSHardeningCases.json"
RESULTS = b.BASE + "P9-8.4d-COSHardeningResults.json"
REVIEW = b.BASE + "P9-8.4d-COSHardeningReview.md"
BITS = 192


def a(x):
    q = Q(x)
    return arb(q.numerator) / arb(q.denominator)


def lower(x):
    return Q(str(x.lower().fmpq()))


def upper(x):
    return Q(str(x.upper().fmpq()))


def norm(x):
    return max(
        sum(max(abs(lower(x[i, j])), abs(upper(x[i, j]))) for j in range(x.ncols()))
        for i in range(x.nrows())
    )


def eye(n):
    return arb_mat([[int(i == j) for j in range(n)] for i in range(n)])


def matrix(rows):
    return arb_mat([[a(v) for v in row] for row in rows])


def connected_unit_tree(inputs):
    ref = inputs.geometry.reference
    g = ref.graph
    n, m = len(g.live_node_ids), len(g.live_edge_ids)
    b.require(
        m == n - 1
        and all(v == 1 for v in ref.profile.params_resolved.candidate.W_C_tr.values()),
        "unit tree required",
    )
    reached = {g.live_node_ids[0]}
    while True:
        following = reached | {
            v
            for e in g.oriented_edges
            if e.tail_node_id in reached or e.head_node_id in reached
            for v in (e.tail_node_id, e.head_node_id)
        }
        if following == reached:
            break
        reached = following
    b.require(len(reached) == n, "connected tree required")
    expected = tuple(tuple(float(i == j) for j in range(m)) for i in range(m))
    b.require(
        inputs.geometry.one_form_hodge.matrix == expected
        and ref.pairings.one_form.matrix == expected,
        "identity reference required",
    )
    return n, m


def interval_os(inputs):
    """Full exact-real OS map at a represented prestate, not a staged solver.

    Connected unit tree and ||H-I||_infty < 1 imply
    lambda_2(B H B^T) >= (1-||H-I||)*2/[N(N-1)].
    Once this exceeds Lambda_C > 0, the selector is exactly the constant
    projector. Thus H_M=t H and flux response=(I+tau*t*H*B^T B)^-1.
    Arb encloses exp/tanh and all inverses; no production/dense solve is used.
    """
    n, m = connected_unit_tree(inputs)
    p = inputs.geometry.reference.profile.params_resolved
    c = matrix([[v] for v in inputs.current.C])
    incidence = matrix(inputs.geometry.reference.graph.incidence)
    ident = eye(m)
    mean = sum((a(v) for v in inputs.current.C), a(0)) / n
    t = (a(p.candidate.kappa_M_C) * (mean / a(p.candidate.C_ref)).tanh()).exp()
    chi, zeta = a(p.candidate.chi_C), a(p.candidate.zeta_C)

    def read(h):
        deviation = norm(h - ident)
        gap = (1 - deviation) * Q(2, n * (n - 1)) - Q(p.candidate.Lambda_C)
        b.require(
            Q(p.candidate.Lambda_C) > 0 and deviation < 1 and gap > 0,
            "constant selector not certified",
        )
        baseline = (
            -a(p.candidate.eta_C)
            * a(p.candidate.kappa_Phi_C)
            * incidence.transpose()
            * incidence
            * (t * h)
            * incidence.transpose()
            * c
        )
        response = (
            ident + a(p.candidate.tau_C) * t * h * incidence.transpose() * incidence
        ).inv()
        bound = norm(zeta * chi * response)
        b.require(bound < 1, "current inverse not certified")
        current = (ident - zeta * chi * response).inv() * baseline
        return current, chi * response * current, gap, bound

    predictor, flux, _, _ = read(ident)
    bv = inputs.geometry.reference.graph.incidence
    overlap = [
        [Q(sum(abs(row[i]) * abs(row[j]) for row in bv)) / 2 for j in range(m)]
        for i in range(m)
    ]
    h = ident + matrix([[0] * m for _ in range(m)])
    for i in range(m):
        for j in range(m):
            h[i, j] += (
                a(p.geometry.kappa_H)
                * zeta
                * a(overlap[i][j])
                * flux[i, 0]
                * flux[j, 0]
            )
    current, _, gap, bound = read(h)
    after = c - a(inputs.dt) * incidence * current
    b.require(all(after[i, 0].is_finite() for i in range(n)), "nonfinite interval")
    return (
        after,
        current,
        dict(
            selector_gap_lower=str(gap),
            current_contraction_upper=str(bound),
            geometry_deviation_upper=str(norm(h - ident)),
        ),
    )


def point_sign(captured):
    inputs = b.GeometryStageInputs.from_payload(captured["pass"]["inputs"])
    with ctx.workprec(BITS):
        after, current, domain = interval_os(inputs)
        observed = captured["poststate"]["current"]["C"]
        selected = captured["selection"]["current"]
        incidence = inputs.geometry.reference.graph.incidence
        # Literal binary64 continuity, distinct from the exact-real enclosure.
        staged = [
            c - inputs.dt * sum(v * j for v, j in zip(row, selected, strict=True) if v)
            for c, row in zip(inputs.current.C, incidence, strict=True)
        ]
        b.require(staged == observed, "represented continuity drift")
        lows = [lower(after[i, 0]) for i in range(len(observed))]
        errors = [
            max(abs(Q(x) - lower(after[i, 0])), abs(Q(x) - upper(after[i, 0])))
            for i, x in enumerate(observed)
        ]
        current_errors = [
            max(abs(Q(v) - lower(current[i, 0])), abs(Q(v) - upper(current[i, 0])))
            for i, v in enumerate(selected)
        ]
        b.require(
            all(
                error <= Q(2, 10**13) * (1 + abs(Q(v)))
                for error, v in zip(current_errors, selected, strict=True)
            ),
            "full-law current comparison failed",
        )
        b.require(
            min(lows) > 0 and all(e < lo for e, lo in zip(errors, lows, strict=True)),
            "positive sign separation not certified",
        )
        return dict(
            inputs_digest=b.digest(inputs.to_payload()),
            domain=domain,
            exact_real_minimum_lower=str(min(lows)),
            maximum_endpoint_width=str(
                max(upper(after[i, 0]) - lows[i] for i in range(len(lows)))
            ),
            represented_minimum=min(observed),
            maximum_coordinate_error_upper=str(max(errors)),
            minimum_sign_separation=str(
                min(lo - e for lo, e in zip(lows, errors, strict=True))
            ),
            current_error_upper=str(
                max(
                    max(
                        abs(Q(v) - lower(current[i, 0])),
                        abs(Q(v) - upper(current[i, 0])),
                    )
                    for i, v in enumerate(selected)
                )
            ),
            represented_continuity_exact=True,
            scope="pointwise_full_real_OS_at_saved_represented_prestate_not_accumulated_trajectory_tube",
        )


def center(manifest):
    return next(
        c
        for c in manifest["cases"]
        if c["request"]["target_effective_degree"] == 94
        and c["request"]["growth_phase"] == 1
        and c["request"]["module_chirality"] == 1
    )


def declaration():
    return b.seal(
        dict(
            schema="p984d-cos-hardening-inputs-v1",
            predecessor=b.bind((prior.INPUTS, prior.RESULTS)),
            source_bindings=b.bind(
                (
                    SELF,
                    TEST,
                    prior.SELF,
                    prior.consumer.SELF,
                    b.SELF,
                    "tests/models/test_grc_v4_candidate_c.py",
                    "src/pygrc/models/grc_9_v4_lifecycle.py",
                    "src/pygrc/models/grc_9_v4_expansion.py",
                    "src/pygrc/models/grc_v4_transport.py",
                    "src/pygrc/models/grc_v4_step.py",
                )
            ),
            native=dict(
                layout="D94 E+1 P1",
                shares=[
                    [1 / 4, 1 / 2, 1 / 4],
                    [22 / 64, 21 / 64, 21 / 64],
                    [1 / 4, 3 / 8, 3 / 8],
                ],
                target_attempts_per_role=2,
                late_receipt_failure_probe=True,
            ),
            signs=dict(
                layouts="all six D94",
                roles=list(prior.ROLES),
                beats=[1, 2],
                precision_bits=BITS,
            ),
            neighborhood=dict(
                layout="D94 E+1 P1",
                share_radius=1 / 4096,
                resource_radius=1 / 16384,
                roles=list(prior.ROLES),
                beats=10,
                directions="center; six oriented pairwise share transfers; plus/minus resource transfer between first two external nodes",
                scope="nine finite target-continuation probes; not a box or new source-trigger/event admission",
            ),
            user_accepted=False,
            aggregate_closed=False,
        )
    )


def charge(values):
    values = tuple(values)
    while len(values) > 1:
        values = tuple(
            values[i] + values[i + 1] if i + 1 < len(values) else values[i]
            for i in range(0, len(values), 2)
        )
    return values[0]


def native_exclusions(manifest, declared):
    case = center(manifest)
    spec = manifest["expected_source"]["specialization"]
    specialization = b.native.GRC9V4Specialization(
        b.FrozenJSONMap(spec["resolved"]), b.FrozenJSONMap(spec["identity_payload"])
    )
    # Reuse the exact retained postbeat; no replay of the twenty-case campaign.
    seed = b.native.GRC9V4COSState(
        b.GeometryStageInputs.from_payload(manifest["expected_source"]["inputs"]),
        specialization,
    )
    rows = []
    with b.exact_backend(b.ExactBackend.FLINT):
        for index, shares in enumerate(declared["native"]["shares"]):
            owner = b.native.GRC9V4COSOperation(seed)
            request = replace(
                b.GRC9V4ExpansionRequestInput.from_payload(case["request"]),
                resource_distribution=tuple(shares),
                operation_id=f"p984d-hardening-exclusion-{index}",
            )
            outcome = owner.expand(request)
            b.require(outcome.committed, "excluded fixture failed before continuation")
            published = owner._published
            snapshot = owner.checkpoint()
            current = owner.state.inputs
            core = outcome.emitted_receipts[0].identity_payload.to_dict()["core"]
            reduced_delta = Q(charge(current.current.C)) - Q(
                charge(seed.inputs.current.C)
            )
            b.require(
                Q(core["actual_charge_delta"]) == reduced_delta,
                "charge receipt hides prescribed reduction delta",
            )
            row = dict(
                shares=shares,
                event_committed=True,
                request=request.to_payload(),
                target_digest=b.digest(current.to_payload()),
                exact_coordinate_deltas={
                    r: str(
                        sum(map(Q, getattr(current, r).C))
                        - sum(map(Q, getattr(seed.inputs, r).C))
                    )
                    for r in prior.ROLES
                },
                reduced_charge_delta=str(reduced_delta),
                receipt_charge_delta=core["actual_charge_delta"],
                roles={},
            )
            for role in prior.ROLES:
                incoming = replace(current, current=getattr(current, role), dt=b.DT)
                stages = []
                for beat in (1, 2):
                    preimage = incoming.to_payload()
                    expected = b.dense_os(incoming)
                    try:
                        step = b.ProvisionalCandidateCOSStep(incoming)
                    except Exception as exc:
                        b.require(
                            min(expected["C"]) < 0 and "nonnegative" in str(exc),
                            "unexpected native rejection",
                        )
                        b.require(
                            incoming.to_payload() == preimage
                            and owner._published is published
                            and owner.checkpoint() == snapshot,
                            "failed provisional continuation mutated inputs/event publication",
                        )
                        stages.append(
                            dict(
                                beat=beat,
                                outcome="rejected",
                                exception=type(exc).__name__,
                                stage=getattr(exc, "stage", None),
                                code=getattr(exc, "code", None),
                                message=str(exc),
                                dense_minimum=float(min(expected["C"])),
                                prestate_preserved=True,
                                event_publication_preserved=True,
                            )
                        )
                        break
                    b.comparison(
                        step.next_inputs.current.C,
                        expected["C"],
                        case["comparison"],
                        "excluded_C",
                    )
                    stages.append(
                        dict(
                            beat=beat,
                            outcome="passed",
                            minimum_C=min(step.next_inputs.current.C),
                        )
                    )
                    incoming = step.next_inputs
                row["roles"][role] = stages
            rows.append(row)
        owner = b.native.GRC9V4COSOperation(seed)
        published = owner._published
        checkpoint = owner.checkpoint()
        with patch.object(
            b.native,
            "_event_receipts",
            side_effect=ValueError("injected late receipt failure"),
        ):
            rejected = owner.expand(request)
        b.require(
            not rejected.committed
            and rejected.failure.stage == "commit"
            and owner._published is published
            and owner.checkpoint() == checkpoint,
            "late event failure published partial state",
        )
        rows[-1]["late_event_failure"] = dict(
            stage=rejected.failure.stage,
            code=rejected.failure.code,
            whole_publication_preserved=True,
        )
    b.require(
        rows[0]["roles"]["current"][-1]["outcome"] == "rejected"
        and len(rows[0]["roles"]["current"]) == 1,
        "first exclusion disappeared",
    )
    b.require(
        rows[1]["roles"]["current"][-1]["outcome"] == "rejected"
        and len(rows[1]["roles"]["current"]) == 2,
        "second exclusion disappeared",
    )
    b.require(
        Q(rows[2]["exact_coordinate_deltas"]["current"]) == Q(1, 2**53),
        "rounding exclusion disappeared",
    )
    return rows


def sign_checks(manifest, record):
    execution = prior.previous.expand(record["execution"])
    rows = []
    for case, row in zip(manifest["cases"], execution["cases"], strict=True):
        if case["request"]["target_effective_degree"] != 94:
            continue
        for obs, captured in zip(
            row["observations"], row["consumption_evidence"], strict=True
        ):
            if obs["stage"] == "target_continuation" and obs["beat"] in (1, 2):
                rows.append(
                    dict(
                        case_id=case["case_id"],
                        role=obs["role"],
                        beat=obs["beat"],
                        **point_sign(captured["value"]),
                    )
                )
    b.require(len(rows) == 24, "sign roster drift")
    return rows


def neighborhood(manifest, declared):
    case = center(manifest)
    base = prior.target(manifest, case)
    variants = [("center", base)]
    delta = declared["neighborhood"]["share_radius"]
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            shares = list(case["request"]["resource_distribution"])
            shares[i] += delta
            shares[j] -= delta
            variants.append((f"share_{j}_to_{i}", prior.target(manifest, case, shares)))
    external = [
        i
        for i, n in enumerate(base.geometry.reference.graph.live_node_ids)
            if not (isinstance(n, str) and n.startswith("grc-event-"))
    ][:2]
    b.require(len(external) == 2, "external resource directions missing")
    for sign in (-1, 1):
        roles = {}
        for role in prior.ROLES:
            original = getattr(base, role)
            c = list(original.C)
            c[external[0]] += sign * declared["neighborhood"]["resource_radius"]
            c[external[1]] -= sign * declared["neighborhood"]["resource_radius"]
            roles[role] = replace(original, C=tuple(c))
        variants.append((f"external_transfer_{sign}", replace(base, **roles)))
    rows = []
    for label, target in variants:
        row = dict(probe=label, target_digest=b.digest(target.to_payload()), roles={})
        for role in prior.ROLES:
            incoming = replace(target, current=getattr(target, role), dt=b.DT)
            minima = []
            for beat in range(10):
                expected = b.dense_os(incoming)
                minima.append(float(min(expected["C"])))
                if minima[-1] < 0:
                    break
                incoming = replace(
                    incoming,
                    current=b.GRCV4AuthoritativeState(
                        tuple(map(float, expected["C"])), None, None
                    ),
                )
            row["roles"][role] = dict(
                minima=minima,
                completed_beats=len(minima),
                positive=all(x > 0 for x in minima),
                exact_transfer_delta=str(
                    sum(map(Q, getattr(target, role).C))
                    - sum(map(Q, getattr(base, role).C))
                ),
            )
        rows.append(row)
    b.require(len(rows) == 9, "neighborhood roster drift")
    return rows


def check(declared, result):
    b.check_bindings(b.read(prior.INPUTS)["source_bindings"])
    b.check_digest(declared)
    b.check_bindings(declared["source_bindings"])
    b.check_bindings(declared["predecessor"])
    b.require(declared == declaration(), "hardening declaration drift")
    b.check_digest(result)
    b.require(
        result["inputs_digest"] == declared["record_digest"]
        and result["user_accepted"] is False
        and result["aggregate_closed"] is False,
        "hardening result binding/scope",
    )
    b.require(
        len(result["signs"]) == 24
        and len(result["native"]) == 3
        and len(result["neighborhood"]) == 9,
        "hardening result roster",
    )
    for row in result["signs"]:
        b.require(
            Q(row["exact_real_minimum_lower"]) > 0
            and Q(row["minimum_sign_separation"]) > 0,
            "invalid sign evidence",
        )
        b.require(
            Q(row["domain"]["selector_gap_lower"]) > 0
            and Q(row["domain"]["current_contraction_upper"]) < 1
            and row["represented_continuity_exact"] is True,
            "sign domain drift",
        )
    expected = [
        (c["case_id"], role, beat)
        for c in b.read(prior.INPUTS)["cases"]
        if c["request"]["target_effective_degree"] == 94
        for role in prior.ROLES
        for beat in (1, 2)
    ]
    b.require(
        [(r["case_id"], r["role"], r["beat"]) for r in result["signs"]] == expected,
        "sign subject drift",
    )
    for index, row in enumerate(result["native"]):
        b.require(
            row["shares"] == declared["native"]["shares"][index]
            and row["event_committed"] is True,
            "native subject drift",
        )
        b.require(
            Q(row["reduced_charge_delta"]) == Q(row["receipt_charge_delta"]),
            "receipt charge drift",
        )
        if index < 2:
            steps = row["roles"]["current"]
            b.require(
                len(steps) == index + 1
                and steps[-1]["outcome"] == "rejected"
                and steps[-1]["dense_minimum"] < 0
                and steps[-1]["prestate_preserved"]
                and steps[-1]["event_publication_preserved"],
                "native exclusion drift",
            )
    rounding = result["native"][2]
    b.require(
        Q(rounding["exact_coordinate_deltas"]["current"]) == Q(1, 2**53)
        and rounding["late_event_failure"]["whole_publication_preserved"] is True,
        "rounding/atomicity control drift",
    )
    return dict(
        status="passed_bounded_hardening",
        native_events=3,
        pointwise_sign_certificates=24,
        neighborhood_probes=9,
        neighborhood_positive_roles=sum(
            v["positive"]
            for row in result["neighborhood"]
            for v in row["roles"].values()
        ),
        native_rerun=False,
        intervals_recomputed=False,
        uniform_tube=False,
        public_ordinary_step_owner_tested=False,
        user_accepted=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run", "check", "recheck"))
    args = parser.parse_args()
    if args.action == "prepare":
        b.write_new(INPUTS, declaration())
        return
    declared = b.read(INPUTS)
    b.require(declared == declaration(), "declaration drift")
    if args.action in ("check", "recheck"):
        result = b.read(RESULTS)
        summary = check(declared, result)
        if args.action == "recheck":
            b.require(
                sign_checks(b.read(prior.INPUTS), b.read(prior.RESULTS))
                == result["signs"],
                "interval recheck drift",
            )
            b.require(
                neighborhood(b.read(prior.INPUTS), declared) == result["neighborhood"],
                "neighborhood recheck drift",
            )
            summary["intervals_recomputed"] = True
        print(json.dumps(summary, indent=2))
        return
    b.require(not (b.ROOT / RESULTS).exists(), "refuse to overwrite evidence")
    manifest = b.read(prior.INPUTS)
    result = dict(
        schema="p984d-cos-hardening-results-v1",
        inputs_digest=declared["record_digest"],
        user_accepted=False,
        aggregate_closed=False,
    )
    result["signs"] = sign_checks(manifest, b.read(prior.RESULTS))
    print("24 pointwise signs checked", flush=True)
    result["neighborhood"] = neighborhood(manifest, declared)
    print("nine neighborhood probes checked", flush=True)
    result["native"] = native_exclusions(manifest, declared)
    result = b.seal(result)
    check(declared, result)
    b.write_new(RESULTS, result)
    print(json.dumps(check(declared, result), indent=2))


if __name__ == "__main__":
    main()

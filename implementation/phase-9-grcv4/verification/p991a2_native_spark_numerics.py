"""Bounded C_OS native numerical checks. Never runs a completion trajectory."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import lzma
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
INV = "implementation/investigations/grc9v4-constitutive-design/"
EVIDENCE = INV + "evidence/spark-completion/"
EARLY = EVIDENCE + "applicability/earlier-closure/"
RECORD = "implementation/phase-9-grcv4/tranche-9/P9-9.1a.2-Verification.json"
SCRIPT = "implementation/phase-9-grcv4/verification/p991a2_native_spark_numerics.py"


def read(name):
    raw = (ROOT / name).read_bytes()
    return json.loads(lzma.decompress(raw) if name.endswith(".xz") else raw)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                             allow_nan=False).encode()).hexdigest()


def seal(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=digest(body))


def profile(graph, **changes):
    """Explicit test subject; does not add a registry/release support claim."""
    from pygrc.models.grc_v4_codec import payload_identity
    from pygrc.models.grc_v4_profile import get_supported_profile, list_supported_profiles, resolve_profile
    from pygrc.models.grc_v4_spark_state import QuarticCOSProfile, QuarticSite

    old = next(p for p in map(get_supported_profile, sorted(list_supported_profiles()))
               if p.identity_payload.profile_family_id == "C_OS")
    p, identity = old.params_resolved.to_payload(), old.identity_payload.to_payload()
    weights = {e: 1 for e in graph.live_edge_ids}
    p["candidate"].update(Lambda_C=1/64, kappa_M_C=0, kappa_Phi_C=1/64, eta_C=1/1024,
                          tau_C=1, chi_C=1/2, zeta_C=1/2, W_C_tr=weights,
                          W_C_tr_content_digest=payload_identity("wctr_identity_payload",
                              dict(schema_version="grcv4-wctr-identity-v1", W_C_tr=weights)))
    m = len(weights)
    p["geometry"].update(kappa_H=1/2,
        K4_base_digest=payload_identity("k4_identity_payload", dict(
            schema_version="grcv4-k4-identity-v1", K4_base=[[0]*m for _ in range(m)])),
        reference_hodge_digest=payload_identity("reference_hodge_identity_payload", dict(
            schema_version="grcv4-reference-hodge-identity-v1", edge_weights=weights)))
    p["realization"]["tolerance"] = 1e-11
    p["solver"]["conditioning_limit"] = 10**12
    for section, values in changes.items():
        (identity if section == "identity" else p[section]).update(values)
    identity["params_hash"] = payload_identity("resolved_params", p)
    return QuarticCOSProfile(resolve_profile(p, identity), QuarticSite())


def subjects():
    from pygrc.models.grc_v4_geometry import GRCV4Graph
    from pygrc.models.grc_v4_spark_state import ExactResources

    prepared = read(EVIDENCE + "SC2SourceBeat.json.xz")["checks"]["prepared"]
    graph = GRCV4Graph.from_payload(prepared["source_graph"])
    states = {role: ExactResources(graph, tuple(prepared[role+"_prestate"][v]
                for v in graph.live_node_ids), "21") for role in ("current", "reset")}
    domain = read(EARLY + "CEarlierDomain.json")
    return prepared, graph, states, domain


def transfer(state, chirality):
    from pygrc.models.grc_9_v4_expansion import _allocate
    from pygrc.models.grc_v4_geometry import GRCV4Graph

    # The existing native allocator supplies the frozen scientific chart. The
    # future lifecycle supplies a real receipt-derived event ID, not this name.
    target, module, _ = _allocate(state.graph.port_graph, "v", "sc2-positive-module", chirality, (0, 0, 0))
    shares = {module[0]: "0", module[1]: "1/64", module[2]: "31/32", module[3]: "1/64"}
    matrix = tuple(tuple(shares.get(node, "0") if old == "v" else str(int(node == old))
                         for old in state.graph.live_node_ids) for node in target.live_node_ids)
    return state.transfer(GRCV4Graph.from_port_graph(target), matrix), matrix


def oracle(step, *, literal=False):
    """Different resolvent/similarity solve and independent Arb equation path."""
    from flint import arb, fmpq, fmpq_mat, ctx
    sys.path.insert(0, str(ROOT / INV / "research"))
    from spark_completion_os_reference import COSReference

    graph = step.before.graph.to_payload()
    source = dict(zip(step.before.graph.live_node_ids, step.before.C, strict=True))
    if literal:
        exact = COSReference(graph, "rational")
        C = exact.vector(source)
        _, flat = exact.direct_similarity_read(C, exact.I, exact.q(1, 1024))
        # Build geometry from literal vertex-star restrictions, independently of
        # the native overlap matrix implementation.
        H = exact.I + fmpq_mat([[sum(flat[i, 0]*flat[j, 0]/8
                    for node in exact.nodes if node in exact.edges[i] and node in exact.edges[j])
                    for j in range(exact.m)] for i in range(exact.m)])
        current, _ = exact.direct_similarity_read(C, H, exact.q(1, 1024))
        need(tuple(map(str, current.entries())) == step.exact_current, "literal similarity current disagrees")
        need(H == fmpq_mat([[fmpq(x) for x in row] for row in step.selected_geometry]), "literal star assembly disagrees")
    with ctx.workprec(256):
        model = COSReference(graph, "arb")
        result = model.step(model.vector(source), eta=model.q(1, 1024), dt=model.q(32))
        need(all(result["corrector"]["current"][i, 0].contains(fmpq(x))
                 for i, x in enumerate(step.exact_current)), "Arb current enclosure disagrees")
        for i, value in enumerate(step.after.C):
            delta = abs(arb(fmpq(value))-result["after"][i, 0])
            need(delta.upper() <= arb(fmpq(step.componentwise_error_bounds[i])), "whole-step error not enclosed")
        # Both geometry consumers must contribute at these nonstationary points.
        if literal:
            C = model.vector(source); H = result["geometry"]
            zero = model.read(C, model.I, model.q(1,1024))["current"]
            need(any(not zero[i,0].overlaps(result["corrector"]["current"][i,0])
                     for i in range(model.m)), "generated geometry was vacuous")
    return dict(independent_arb_bits=256, full_step_enclosed=True, literal_similarity_checked=literal)


def row_oracle(state):
    from fractions import Fraction as Q
    sys.path.insert(0, str(ROOT / INV / "research"))
    import spark_completion_basins as independent

    policy = dict(sign=-1, gradient=Q(4), hessian=Q(1, 4), contrast=Q(1, 2), core_resource=Q(1, 2))
    values = dict(zip(state.graph.live_node_ids, map(Q, state.C), strict=True))
    edges = [(e.tail.node_id, e.tail.port, e.head.node_id, e.head.port, Q(1))
             for e in state.graph.port_graph.edges]
    expected = independent.row_intervals(state.graph.live_node_ids, edges, values, values)
    classification = independent.classify(state.graph.live_node_ids, edges, values, policy)
    need(state.edge_orders(-1) == tuple(int(values[a] > values[b])-int(values[a] < values[b])
         for a,_,b,_,_ in edges), "exact landscape edge order disagrees")
    rows = state.spatial_diagnostics(**{k: v if k == "sign" else str(v) for k, v in policy.items()})
    for row in rows:
        node = row["node_id"]
        need(tuple(row["gradient"]) == tuple(str(x[0]) for x in expected[node]), "exact fixed-row arithmetic disagrees")
        need(row["seed"] == (node in classification["seeds"]), "strict seed predicate disagrees")
        adjacent = independent.neighbors(state.graph.live_node_ids, edges)[node]
        anchor = node in classification["seeds"] and bool(adjacent) and values[node] > Q(1,2) and all(
            values[node]-values[v] > Q(1,2) for v in adjacent)
        need(row["anchor"] == anchor, "strict anchor predicate disagrees")
    return dict(arithmetic_error="0", rows_digest=digest([r.to_dict() for r in rows]),
                seeds=sorted(classification["seeds"]), complete_basins_oracle={k: sorted(v) for k,v in classification["basins"].items()})


def domain_budget(domain):
    from flint import fmpq as Q, fmpq_mat as M
    from pygrc.models.grc_v4_geometry import GRCV4Graph
    from pygrc.models.grc_v4_spark_cos import SparkCOSKernel

    proofs = read(EARLY + "CEarlierProofs.json")
    need(seal(domain) == domain and seal(proofs) == proofs, "retained scientific digest drift")
    proof = proofs["proofs"]["C_OS"]
    need(proofs["domain_digest"] == proof["domain_digest"] == domain["record_digest"], "domain binding drift")
    graph = GRCV4Graph.from_payload(domain["graphs"]["1"])
    n, d = len(graph.live_node_ids), domain["resource_dimension"]
    T = M([[Q(x) for x in row] for row in domain["basis"]]); radii = list(map(Q, domain["axis_radii"]))
    diagonal = lambda xs: M([[xs[i] if i == j else 0 for j in range(d)] for i in range(d)])
    S = M([[int(i == j) if i < d else -1 for j in range(d)] for i in range(n)])*T*diagonal(radii)
    U = diagonal([1/r for r in radii])*T.inv()*M([[int(i == j) for j in range(n)] for i in range(d)])
    need(n == 15 and d == 14 and U*S == diagonal([1]*d), "full-rank exact chart")
    need(all(sum(S[i,j] for i in range(n)) == 0 for j in range(d)), "charge-tangent chart")
    center = [Q(domain["center"][v]) for v in graph.live_node_ids]
    need(sum(center) == 21, "center exact charge")
    halfwidth = [sum(abs(S[i,j]) for j in range(d)) for i in range(n)]
    minimum = min(c-r for c,r in zip(center,halfwidth)); maximum = max(c+r for c,r in zip(center,halfwidth))
    need(minimum > 0, "positive whole domain")
    kernel = SparkCOSKernel(graph, profile(graph))
    result = kernel.uniform_rounding_bound(tuple(tuple(str(U[i,j]) for j in range(n)) for i in range(d)),
                                           proof["strict_image_margin"][0])
    # Independent universal conditioning bound. H=I+PSD, lambda_max(H)<=||H||inf.
    # A is similar to 3I/4+sqrt(H)Lsqrt(H), so ||A^-1||inf <= (4/3)m ||H||inf.
    B = M([[int(e.tail_node_id == v)-int(e.head_node_id == v) for e in graph.oriented_edges] for v in graph.live_node_ids])
    L = B.transpose()*B; m = L.nrows(); I = M([[int(i == j) for j in range(m)] for i in range(m)])
    norm = lambda a: max(sum(abs(a[i,j]) for j in range(a.ncols())) for i in range(a.nrows()))
    shifted = max(abs(minimum-2), abs(maximum-2))
    potential = norm(B*B.transpose())*maximum/64 + shifted**3+shifted
    flat = norm((3*I/4+L).inv())*norm(B.transpose())*potential/2048
    overlap_norm = max(sum(sum(abs(B[k,i]*B[k,j]) for k in range(n)) for j in range(m)) for i in range(m))
    Hbound = 1+overlap_norm*flat**2/8
    condition = Q(4,3)*m*m*(Q(3,4)+Hbound*norm(L))*Hbound
    need(condition < 10**12 and m*Hbound < 10**12, "whole-domain numerical stage conditioning unproved")
    tolerance = Q(*float(1e-11).as_integer_ratio())
    need(Q(proof["OS_split_upper"][1]) < tolerance, "unchanged binary64 OS split tolerance")
    error = Q(result["full_step_error"]); margin = Q(result["image_margin"])
    return dict(result, domain_digest=domain["record_digest"], U_S_identity=True,
        center_charge="21", full_dimension=d, positive_resource_lower=str(minimum),
        whole_domain_condition_upper=str(condition), whole_domain_H_infinity_upper=str(Hbound),
        selected_conditioning_limit="1000000000000", OS_split_upper=proof["OS_split_upper"][1],
        OS_tolerance_exact=str(tolerance), remaining_image_margin=str(margin-error),
        error_to_margin_ratio=str(error/margin), error_display=float(error), margin_display=float(margin),
        spatial_evaluation_error="0", spatial_agreement="exact rational formulas on authoritative C; accepted whole-domain predicates unchanged")


def run():
    from flint import fmpq
    from pygrc.models.grc_v4_exact import current_exact_backend
    from pygrc.models.grc_v4_spark_cos import SparkCOSKernel
    from pygrc.models.grc_v4_spark_state import ExactResources, QuarticCOSProfile, NUMERICAL_POLICY

    start = time.perf_counter()
    prepared, graph, states, domain = subjects()
    kernel = SparkCOSKernel(graph, profile(graph)); before_cache = kernel.cache_info()
    need(QuarticCOSProfile.from_canonical_bytes(kernel.profile.to_canonical_bytes()) == kernel.profile, "profile round trip")
    restored = ExactResources.from_canonical_bytes(states["current"].to_canonical_bytes())
    need(restored == states["current"], "source lossless round trip")
    outer_backend = current_exact_backend()
    t = time.perf_counter(); source = kernel.step(restored); source_seconds = time.perf_counter()-t
    need(current_exact_backend() is outer_backend, "native operation leaked backend scope")
    source_check = oracle(source, literal=True)
    # The reset role is read, never advanced by the source beat.
    kernel.reference_read(states["reset"])
    source_error = max(abs(fmpq(source.after.C[i])-fmpq(prepared["capture"]["current"][v]))
                       for i,v in enumerate(graph.live_node_ids))
    need(source_error <= max(map(fmpq, source.componentwise_error_bounds)), "source prefix error")
    source_rows = row_oracle(source.after)
    need(source_rows["complete_basins_oracle"] == {"p": sorted(graph.live_node_ids)}, "fresh source parent")
    post_rows = source.after.spatial_diagnostics(sign=-1, gradient="4", hessian="1/4", contrast="1/2", core_resource="1/2")
    v = next(r for r in post_rows if r["node_id"] == "v")
    need(fmpq(v["gradient_squared"]) < 16 and fmpq(v["minimum_signed_gradient"]) < fmpq(1,8), "fresh exact hybrid predicate")
    results, times, target_by_role = {}, {}, {}
    for role, source_state in (("current", source.after), ("reset", states["reset"])):
        target, matrix = transfer(source_state, 1)
        need(target.graph.to_payload() == domain["graphs"]["1"], "native mechanical target differs")
        need(ExactResources.from_canonical_bytes(target.to_canonical_bytes()) == target, "event state round trip")
        # An independently declared column-stochastic event cannot amplify the
        # infinity error by more than its exact maximum row sum (here one).
        norm = max(sum(fmpq(x) for x in row) for row in matrix)
        event_error = max(abs(fmpq(target.C[i])-fmpq(prepared["transferred_"+role][v]))
                          for i,v in enumerate(target.graph.live_node_ids))
        need(event_error <= norm*(source_error if role == "current" else 0), "exact event error propagation")
        target_kernel = SparkCOSKernel(target.graph, profile(target.graph))
        t = time.perf_counter(); step = target_kernel.step(target); times[role] = time.perf_counter()-t
        check = oracle(step)
        results[role] = dict(profile_id=step.profile_id, prestate=target.to_payload(), after=step.after.to_payload(),
            flux=list(step.flux), step_error_bounds=list(step.componentwise_error_bounds),
            split_squared_digest=digest(step.split_frobenius_squared),
            split_squared_display=float(fmpq(step.split_frobenius_squared)),
            event_prefix_error=str(event_error), allocation_infinity_norm=str(norm),
            source_reset_advanced=False, oracle=check, diagnostics=row_oracle(step.after))
        target_by_role[role] = step
    current = target_by_role["current"]
    # Changing-state continuation and a cold reference-fact comparison, not
    # repeated identical-state timing advertised as trajectory performance.
    warm_kernel = SparkCOSKernel(current.after.graph, profile(current.after.graph))
    t = time.perf_counter(); second = warm_kernel.step(current.after); times["current_second"] = time.perf_counter()-t
    oracle(second)
    need(second.exact_current != current.exact_current and second.after != current.after, "stale current reuse")
    mirror, _ = transfer(source.after, -1)
    need(mirror.graph.to_payload() == domain["graphs"]["-1"], "opposite chiral target differs")
    mirror_kernel = SparkCOSKernel(mirror.graph, profile(mirror.graph))
    mirror_step = mirror_kernel.step(mirror)
    need(mirror_step.after.C == current.after.C and mirror_step.exact_current == current.exact_current,
         "chiral constitutive covariance")
    row_oracle(mirror_step.after)
    cache = kernel.cache_info()
    need(cache["hits"] > before_cache["hits"], "reference cache not reused")
    numerical_budget = domain_budget(domain)
    paths = [SCRIPT, "src/pygrc/models/grc_v4_spark_state.py", "src/pygrc/models/grc_v4_spark_cos.py",
             EVIDENCE+"SC2SourceBeat.json.xz", EARLY+"CEarlierDomain.json", EARLY+"CEarlierProofs.json",
             INV+"research/spark_completion_os_reference.py", INV+"research/spark_completion_basins.py",
             "tests/models/test_grc_v4_spark_numerics.py", "specs/grc-v4-spark-native-numerical-policy.md",
             *("src/pygrc/models/"+name+".py" for name in (
                 "grc_v4_exact", "grc_v4_numerics", "_grc_v4_matrix", "_grc_v4_matrix_flint",
                 "grc_v4_profile", "grc_v4_geometry", "grc_v4_codec", "grc_9_v4_topology", "grc_9_v4_expansion"))]
    # The scientific inputs are the same bytes already bound by committed .1.
    accepted = {r["path"]: r["sha256"] for r in read("implementation/phase-9-grcv4/tranche-9/P9-9.1a.1-Verification.json")["source_bindings"]}
    for name in paths[3:6]:
        need(sha256((ROOT/name).read_bytes()).hexdigest() == accepted[name], "accepted input bytes changed")
    return seal(dict(schema="grc9v4-native-spark-numerics-v1", leaf="P9-9.1a.2",
        status="bounded_numerical_bridge_verified_review_pending", user_accepted=False,
        numerical_policy_id=NUMERICAL_POLICY, exact_backend="flint", native_kernel_steps=5,
        native_owner_steps=0, native_events_published=0, native_completion_support=False,
        native_endpoint_verified=False, numerical_campaigns=0,
        source=dict(profile_id=source.profile_id, before=source.before.to_payload(), after=source.after.to_payload(),
                    exact_prefix_error=str(source_error), oracle=source_check, diagnostics=source_rows),
        target_steps=results, changing_state_second_after=second.after.to_payload(),
        chiral_equation_covariance=True, reset_source_not_advanced=True,
        reference_cache_hit_observed=True, stale_current_control_passed=True,
        numerical_budget=numerical_budget,
        prefix_control=dict(input_error="0", exact_event_transfer=True,
            step_error="h B times the sole flux-rounding error, checked at every step",
            entry_rule="test actual exact native state membership; never import research target or assume beat 374/375",
            accumulated_orbit_shadow_bound_claimed=False, full_native_prefix_execution="P9-9.1a.5 after runtime preflight"),
        timings_seconds=dict(source_step=source_seconds, **times, bounded_check_total=time.perf_counter()-start),
        timing_scope="numerical-kernel checks only; not owner/event/completion performance estimate",
        source_bindings=[dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths]))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--write", action="store_true"); parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.write:
        (ROOT / RECORD).write_text(json.dumps(result, indent=2)+"\n")
    elif args.check:
        retained = read(RECORD); need(seal(retained) == retained, "verification digest changed")
        stable = lambda v: {k: x for k,x in v.items() if k not in ("record_digest", "timings_seconds")}
        need(stable(retained) == stable(result), "bounded numerical evidence differs")
    print(json.dumps(dict(status="PASS", native_kernel_steps=result["native_kernel_steps"],
          numerical_budget=result["numerical_budget"]["error_display"],
          timings_seconds=result["timings_seconds"], native_completion_support=False)))


if __name__ == "__main__":
    main()

"""A_OS ordering and chart covariance, with independent saved-entry equations."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from dataclasses import replace
import json
import lzma

import p984d_aos_runtime as deep
import p984e_cos as ordering
import p984e_aci as maps
import p984f_cos as chart
from pygrc.models.grc_9_v4_expansion import aos_profile_template

b, r, o = deep.b, deep.runtime, deep.oracle
SELF = b.HERE + "p984ef_aos.py"
TEST = b.HERE + "test_p984ef_aos.py"
ROLES = o.ROLES
POLICY = dict(norm="componentwise_abs_plus_relative", atol=2e-13, rtol=2e-13)


def paths(checkpoint):
    b.require(checkpoint in ("e", "f"), "unsupported covariance checkpoint")
    stem = b.BASE + "P9-8.4" + checkpoint + "-AOS"
    return stem + "Inputs.json", stem + "Results.json.xz"


def declarations(checkpoint):
    return ordering.declarations() if checkpoint == "e" else chart.declarations()


def mapping(a, c, d, old=None, new=None):
    return chart.mapping(a, c, d, old, new) if "ports" in d else maps.mapping(a, c, d, old, new)


def transported(graph, d, old=None, new=None):
    return chart.transported_graph(graph, d, old, new) if "ports" in d else maps.transported_graph(graph, d, old, new)


def transform(value, d):
    before = b.GeometryStageInputs.from_payload(value)
    original = value["reference"]["graph"]
    if "ports" in d:
        graph = transported(original, d)
    else:
        nodes, edges = maps.labels(d)
        graph = deepcopy(original)
        graph["live_node_ids"] = [nodes[original["live_node_ids"][i]] for i in d["node_order"]]
        graph["edges"] = []
        for i in d["edge_order"]:
            e = deepcopy(original["edges"][i])
            e["edge_id"] = edges[e["edge_id"]]
            for end in ("tail", "head"):
                e[end]["node_id"] = nodes[e[end]["node_id"]]
            if d["signs"][i] < 0:
                e["tail"], e["head"] = e["head"], e["tail"]
            graph["edges"].append(e)
    ni, ei, signs = mapping(original, graph, d)
    ref = r.aos.reference(graph)
    h = value["H1_form"]
    h = tuple(tuple(float(h[i][j] * signs[k] * signs[l]) if h[i][j] else 0.0
                    for l, j in enumerate(ei)) for k, i in enumerate(ei))
    states = {role: r.state(dict(C=[value[role]["C"][i] for i in ni],
                                W_A=[value[role]["W_A"][i] for i in ei], Z_4=None)) for role in ROLES}
    return replace(before, geometry=b.GRCV4Geometry(ref, b.OneFormHodge(ref.graph, h)), **states)


def make_manifest(checkpoint):
    native = o.read(deep.INPUTS)
    deep.check_manifest(native)
    prior = o.read(deep.RESULTS)
    b.check_digest(prior)
    b.require(prior["manifest_digest"] == native["record_digest"] and
              not prior["user_accepted"] and not prior["aggregate_closed"], "deep prerequisite identity")
    execution = deep.storage.expand(prior["execution"])
    b.check_digest(execution)
    b.require([r["case_id"] for r in execution["cases"]] == [c["case_id"] for c in native["cases"]]
              and all(r["case_passed"] and r["outcome"] == "passed_named_case" and
                      r["event_committed"] and r["first_failure"] is None for r in execution["cases"]),
              "deep native prerequisite incomplete")
    boundary = o.read(o.boundary.INPUTS)["cases"] + o.read(o.equations.INPUTS)["cases"]
    deep_cases = o.read(o.INPUTS)["cases"]
    selections = ([(boundary, 52, 1, 1), (deep_cases, 94, -1, 3)] if checkpoint == "e"
                  else [(boundary, degree, ch, None if degree == 45 else 1)
                        for degree in (45, 52) for ch in (1, -1)])
    cases = [next(c for c in cases if (c["request"]["target_effective_degree"],
        c["request"]["module_chirality"], c["request"]["growth_phase"]) == (degree, ch, phase))
        for cases, degree, ch, phase in selections]
    bound = {x["path"] for x in native["source_bindings"]}
    bound |= {SELF, TEST, deep.INPUTS, deep.RESULTS, ordering.SELF, maps.SELF, chart.SELF,
              o.boundary.INPUTS, o.equations.INPUTS}
    return b.seal(dict(schema="p984ef-aos-inputs-v1", checkpoint=checkpoint,
        family="A_OS", initial_inputs=native["initial_inputs"], specialization=native["specialization"],
        cases=cases, transforms=declarations(checkpoint), comparison=POLICY,
        scope=dict(steps_per_role=2, required_history_cells=20 if checkpoint == "e" else 24,
                   events=12 if checkpoint == "e" else 16,
                   target_steps=48 if checkpoint == "e" else 64,
                   unsigned_W=True, carrier=False, uniform_trajectory_enclosure=False),
        source_bindings=b.bind(bound), user_accepted=False, aggregate_closed=False))


def check_manifest(m):
    b.check_digest(m)
    b.check_bindings(m["source_bindings"])
    b.require(m == make_manifest(m["checkpoint"]), "covariance declaration drift")


def nominal(before):
    paper = r.aos.PaperAOS(before.geometry.reference.graph.port_graph.to_payload())
    return o.equations.evaluate(paper, r.capture.authority(before.current), "saved_entry", "current", 0)["output"]


def step(before, backend):
    expected = nominal(before)
    value, after = r.checked_step(before, backend, expected)
    return dict(native=value, nominal=expected), after


def read(before, backend):
    expected = nominal(before)
    return dict(native=r.checked_read(before, backend, expected), nominal=expected)


def source(m, d):
    before = transform(m["initial_inputs"], d)
    spec = m["specialization"]
    seed = r.native.GRC9V4AOSState(before, r.native.GRC9V4Specialization(
        r.FrozenJSONMap(spec["resolved"]), r.FrozenJSONMap(spec["identity_payload"])))
    value, after = step(before, seed.differential_reference)
    return dict(kind=d["kind"], step=value, state=replace(seed, inputs=replace(after, dt=0)).to_payload())


def case_for(seed, case, d, checkpoint):
    c = deepcopy(case)
    request = c["request"]
    ref = seed.inputs.geometry.reference
    if "ports" in d:
        shares = [0.0] * 3
        for i, x in enumerate(request["resource_distribution"], 1):
            shares[d["branches"][str(i)] - 1] = x
        request.update(module_chirality=request["module_chirality"] * d["chirality_factor"],
                       growth_phase=None if request["growth_phase"] is None else d["branches"][str(request["growth_phase"])] ,
                       resource_distribution=shares)
        source_node = "source-s"
    else:
        source_node = maps.labels(d)[0]["source-s"]
    request.update(operation_id="p984" + checkpoint + "-aos-" + case["fixture_id"] + "-" + d["kind"],
                   source_node_id=source_node, source_graph_digest=ref.graph.graph_digest,
                   target_profile_template_id=aos_profile_template(ref).profile_template_id)
    # Native request freshness and exact W history are recomputed by the shared
    # consumer; the expected graph comes only from independent chart algebra.
    c["target"]["port_graph"] = transported(case["target"]["port_graph"], d, case["event_id"], case["event_id"])
    return c


def execute_variant(job):
    m, d = job
    with b.exact_backend(b.ExactBackend.FLINT):
        src = source(m, d)
        seed = r.seed_from_payload(src["state"])
        rows = []
        for case in m["cases"]:
            c = case_for(seed, case, d, m["checkpoint"])
            request = r.fresh_request(seed, c)
            owner = r.native.GRC9V4AOSOperation(seed)
            before = owner.checkpoint()
            stale = dict(request.to_payload(), source_state_digest="grcv4-state-sha256:" + "0" * 64)
            rejected = owner.expand(r.GRC9V4ExpansionRequestInput.from_payload(stale))
            b.require(not rejected.committed and owner.checkpoint() == before, "stale request rollback")
            owner, outcome, event = r.event_capture(seed, request)
            b.require(outcome.committed, "covariance event rejected: " + str(outcome.failure))
            event.update(actual_target=owner.state.to_payload(), receipts=[x.to_payload() for x in outcome.emitted_receipts],
                         replay_identical=r.native.GRC9V4AOSOperation.replay(owner.checkpoint()).checkpoint() == owner.checkpoint())
            target = r.check_event(event, seed, request, c)
            roles = {}
            for role in ROLES:
                incoming = replace(target.inputs, current=getattr(target.inputs, role), dt=r.aos.DT)
                steps = []
                for _ in range(2):
                    value, incoming = step(incoming, target.differential_reference)
                    steps.append(value)
                roles[role] = dict(steps=steps, final=read(incoming, target.differential_reference))
            rows.append(dict(layout=case["fixture_id"], kind=d["kind"], request=request.to_payload(),
                event=event, roles=roles, stale_failure=rejected.failure.to_payload(), rollback_exact=True))
    print(m["checkpoint"], d["kind"], "completed", flush=True)
    return src, rows


def pair(a, c, indices):
    ni, ei, signs = indices
    errors = []
    for key in a:
        av = b.np.asarray(a[key])
        if key == "C":
            expected = av[ni]
        elif key == "W_A":
            expected = av[ei]
        elif av.ndim == 2:
            expected = av[b.np.ix_(ei, ei)] * b.np.outer(signs, signs)
        else:
            expected = av[ei] * signs
        errors.append(b.comparison(c[key], expected, POLICY, "A_OS_covariance_" + key)["maximum_error"])
    return max(errors)


def outputs(row):
    return r.capture.outputs(row["native"])


def check(m, record, *, numerics=False):
    check_manifest(m)
    b.check_digest(record)
    b.require(record["schema"] == "p984ef-aos-results-v1" and record["manifest_digest"] == m["record_digest"]
              and record["user_accepted"] is False and record["aggregate_closed"] is False, "covariance result scope")
    data = deep.storage.expand(record["execution"])
    b.require([s["kind"] for s in data["sources"]] == [d["kind"] for d in m["transforms"]], "source roster")
    b.require([(x["layout"], x["kind"]) for x in data["cases"]] ==
              [(c["fixture_id"], d["kind"]) for d in m["transforms"] for c in m["cases"]], "case roster")
    maximum = 0.0
    for src, d in zip(data["sources"], m["transforms"], strict=True):
        before = transform(m["initial_inputs"], d)
        seed = r.seed_from_payload(src["state"])
        following = r.check_step_record(before, src["step"]["native"], seed.differential_reference,
                                        src["step"]["nominal"], numerics=numerics)
        b.require(seed.inputs == replace(following, dt=0), "source poststate drift")
        indices = mapping(m["initial_inputs"]["reference"]["graph"], before.geometry.reference.graph.to_payload(), d)
        maximum = max(maximum, pair(outputs(data["sources"][0]["step"]), outputs(src["step"]), indices))
        for case in m["cases"]:
            row = next(x for x in data["cases"] if x["kind"] == d["kind"] and x["layout"] == case["fixture_id"])
            base = next(x for x in data["cases"] if x["kind"] == "base" and x["layout"] == case["fixture_id"])
            c = case_for(seed, case, d, m["checkpoint"])
            target = r.check_event(row["event"], seed, r.GRC9V4ExpansionRequestInput.from_payload(row["request"]), c)
            b.require(row["rollback_exact"] is True and row["stale_failure"] and set(row["roles"]) == set(ROLES), "missing rollback/role")
            bg = base["event"]["actual_target"]["inputs"]["reference"]["graph"]
            tg = target.inputs.geometry.reference.graph.to_payload()
            be = base["event"]["checkpoint"]["reference_currents"][0]["event_id"]
            te = row["event"]["checkpoint"]["reference_currents"][0]["event_id"]
            indices = mapping(bg, tg, d, be, te)
            for role in ROLES:
                a = base["event"]["actual_target"]["inputs"][role]
                z = row["event"]["actual_target"]["inputs"][role]
                maximum = max(maximum, pair({k:a[k] for k in ("C", "W_A")}, z, indices))
                incoming = replace(target.inputs, current=getattr(target.inputs, role), dt=r.aos.DT)
                rr, br = row["roles"][role], base["roles"][role]
                b.require(len(rr["steps"]) == 2, "continuation horizon")
                for k, value in enumerate(rr["steps"]):
                    incoming = r.check_step_record(incoming, value["native"], target.differential_reference,
                                                  value["nominal"], numerics=numerics)
                    maximum = max(maximum, pair(outputs(br["steps"][k]), outputs(value), indices))
                final = rr["final"]
                r.capture.check_pass(final["native"], incoming, target.differential_reference)
                r.check_read_record(incoming, final["native"], final["nominal"], numerics=numerics)
                maximum = max(maximum, pair(outputs(br["final"]), outputs(final), indices))
    return dict(family="A_OS", checkpoint="8.4" + m["checkpoint"], status="passed_pending_acceptance",
        successful_history_cells=m["scope"]["required_history_cells"], native_events=len(data["cases"]),
        target_steps=4*len(data["cases"]), maximum_covariance_error=maximum,
        user_accepted=False, aggregate_closed=False, numerical_trajectories_rerun=False)


def run(m, workers):
    check_manifest(m)
    result_path = paths(m["checkpoint"])[1]
    b.require(not (b.ROOT / result_path).exists(), "refuse overwrite")
    with ProcessPoolExecutor(max_workers=workers) as pool:
        values = list(pool.map(execute_variant, [(m, d) for d in m["transforms"]]))
    data = dict(sources=[x[0] for x in values], cases=[r for x in values for r in x[1]])
    compact = deep.storage.compact(data)
    b.require(deep.storage.expand(compact) == data, "lossy covariance storage")
    record = b.seal(dict(schema="p984ef-aos-results-v1", manifest_digest=m["record_digest"],
                        execution=compact, user_accepted=False, aggregate_closed=False))
    status = check(m, record)
    with (b.ROOT / result_path).open("xb") as stream:
        stream.write(lzma.compress(json.dumps(record, separators=(",", ":"), allow_nan=False).encode() + b"\n"))
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "run", "check"))
    parser.add_argument("checkpoint", choices=("e", "f"))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--numerics", action="store_true")
    args = parser.parse_args()
    b.require(1 <= args.workers <= 4, "workers outside 1..4")
    inputs, result = paths(args.checkpoint)
    if args.action == "prepare":
        b.write_new(inputs, make_manifest(args.checkpoint))
    elif args.action == "run":
        print(json.dumps(run(o.read(inputs), args.workers), indent=2))
    else:
        print(json.dumps(check(o.read(inputs), o.read(result), numerics=args.numerics), indent=2))

"""SC-1 exact finite-observation reference, not a native completion evaluator.

Inputs here are synthetic rational graph histories. No root, nine-port event,
physical basin, native execution or completed-spark authority is supplied by
acceptance of these inputs. Native capture/certificate verification is SC-2.
"""
from copy import deepcopy
from fractions import Fraction as F
from itertools import combinations


class Unresolved(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise Unresolved(reason)


def regions(nodes, edges, bands, margin):
    """All-route regions, including cyclic/ambiguous exclusion; no chooser."""
    need(set(bands) == set(edges), "incomplete_edge_capture")
    adjacent = {v: set() for v in nodes}
    incoming = {v: set() for v in nodes}
    for e, (u, v) in edges.items():
        lo, hi = bands[e]
        need(lo <= hi, "invalid_interval")
        if lo == hi == 0:
            continue
        if hi < 0:
            lo, hi, u, v = -hi, -lo, v, u
        need(lo > margin, "unresolved_or_small_current_sign")
        adjacent[u].add(v)
        incoming[v].add(u)
    reach = {}
    for v in nodes:
        seen, pending = set(), [v]
        while pending:
            w = pending.pop()
            if w not in seen:
                seen.add(w)
                pending.extend(adjacent[w] - seen)
        reach[v] = seen
    components = {frozenset(w for w in reach[v] if v in reach[w]) for v in nodes}
    terminals = {c for c in components if not set().union(*(adjacent[v] for v in c)) - c}
    sinks = {next(iter(c)) for c in terminals if len(c) == 1
             and next(iter(c)) not in adjacent[next(iter(c))]
             and incoming[next(iter(c))]}
    result = {s: set() for s in sinks}
    for v in nodes:
        destinations = {c for c in terminals if c & reach[v]}
        for s in sinks:
            if destinations == {frozenset((s,))}:
                result[s].add(v)
    return result


def certificate(case):
    p = case["policy"]
    need(p["beats"] >= 2 and p["duration"] > 0 and p["current_margin"] > 0
         and p["minimum_mass"] > 0 and 0 < p["separation"] < 2
         and p["diameter"] >= 0 and p["W_scale"] > 0 and p["Z_scale"] > 0,
         "invalid_research_policy")
    old, new, module = set(case["source_nodes"]), set(case["target_nodes"]), set(case["module"])
    v = case["expanded_node"]
    need(v in old and module and not module & old and new == (old - {v}) | module,
         "invalid_expansion_lineage")
    parent_regions = regions(old, case["source_edges"], case["source_bands"], p["current_margin"])
    parents = [(s, r) for s, r in parent_regions.items() if v in r]
    need(len(parents) == 1, "missing_parent_organization")
    parent_sink, parent = parents[0]
    collapse = {x: v if x in module else x for x in new}
    footprint = {x for x in new if collapse[x] in parent}
    samples = case["samples"]
    need(len(samples) == p["beats"] + 1, "wrong_window_size")
    need(samples[-1]["time"] - samples[0]["time"] >= p["duration"], "short_elapsed_time")
    q = sum(samples[0]["C"].values())
    need(q > 0, "zero_charge")
    need(set(case["event_C"]) == new and sum(case["event_C"].values()) == q,
         "inconsistent_event_charge")
    need(sum(case["source_C"].values()) == q, "inconsistent_source_charge")
    need(all(sum(case["event_C"][x] for x in new if collapse[x] == i) == case["source_C"][i]
             for i in old), "resource_lineage_mismatch")
    observed = []
    for k, s in enumerate(samples):
        need(s["episode"] == samples[0]["episode"] and s["role"] == "current"
             and s["operation"] == "ordinary_commit" and s["read_stage"] == "fresh_selected",
             "window_boundary_or_wrong_capture")
        need(set(s["C"]) == new and min(s["C"].values()) >= 0
             and sum(s["C"].values()) == q, "resource_or_charge_domain")
        need((s["W"] is None) == (samples[0]["W"] is None)
             and (s["Z"] is None) == (samples[0]["Z"] is None), "history_channel_changed")
        for channel in ("W", "Z"):
            if s[channel] is not None:
                need(len(s[channel]) == len(samples[0][channel]), "history_shape_changed")
        need(s["W"] is None or min(s["W"]) > 0, "nonpositive_W")
        previous_C = samples[k-1]["C"] if k else case["event_C"]
        previous_time = samples[k-1]["time"] if k else case["event_time"]
        dt = s["time"] - previous_time
        need(dt > 0 and (k == 0 or s["beat"] == samples[k-1]["beat"] + 1),
             "nonconsecutive_or_zero_duration")
        need(set(s["used_current"]) == set(case["target_edges"]), "incomplete_used_current")
        expected = dict(previous_C)
        for e, (a, b) in case["target_edges"].items():
            expected[a] -= dt * s["used_current"][e]
            expected[b] += dt * s["used_current"][e]
        need(expected == s["C"], "continuity_stage_mismatch")
        r = regions(new, case["target_edges"], s["bands"], p["current_margin"])
        observed.append({a: members for a, members in r.items()
                         if members <= footprint and (a in module or a == parent_sink)})
    anchors = set.intersection(*(set(r) for r in observed))
    need(len(anchors) >= 2 and anchors & module, "no_additional_child")
    cores = {a: set.intersection(*(r[a] for r in observed)) for a in anchors}
    projected = []
    for s in samples:
        mu = {}
        for a, core in cores.items():
            mass = sum(s["C"][x] for x in core)
            need(mass > p["minimum_mass"], "insufficient_persistent_core_mass")
            mu[a] = {i: sum(s["C"][x] for x in core if collapse[x] == i) / mass for i in parent}
        projected.append(mu)
    separation = min(sum(abs(mu[a][i] - mu[b][i]) for i in parent)
                     for mu in projected for a, b in combinations(anchors, 2))
    need(separation > p["separation"], "indistinct_parent_footprints")
    diameter = F(0)
    for a, b in combinations(samples, 2):
        diameter = max(diameter, *(abs(a["C"][i] - b["C"][i])/q for i in new))
        for channel in ("W", "Z"):
            if a[channel] is not None:
                diameter = max(diameter, *(abs(x-y)/p[channel+"_scale"]
                                         for x, y in zip(a[channel], b[channel], strict=True)))
    need(diameter <= p["diameter"], "full_state_window_drift")
    return dict(child_count=len(anchors & module), descendant_count=len(anchors),
                additional_count=len(anchors)-1, minimum_separation=str(separation),
                full_state_diameter=str(diameter), elapsed=str(samples[-1]["time"]-samples[0]["time"]),
                level="conditional_finite_observation", completed_spark=False,
                attractor_proved=False, native_conformance=False)


def synthetic_case():
    """Continuity-consistent finite countermodel, not constitutive admission."""
    source_C = {"p": F(1, 2), "a": F(2), "b": F(2)}
    event_C = {"x": F(1, 4), "y": F(1, 4), "a": F(2), "b": F(2)}
    edges = {"a-x": ("a", "x"), "b-y": ("b", "y"), "x-y": ("x", "y")}
    currents = {"a-x": F(1, 8), "b-y": F(1, 8), "x-y": F(0)}
    samples = []
    c = dict(event_C)
    for k in range(1, 4):
        for edge, (a, b) in edges.items():
            c[a] -= F(1, 4)*currents[edge]
            c[b] += F(1, 4)*currents[edge]
        samples.append(dict(C=dict(c), W=(F(1),)*3, Z=(F(0),)*3,
            time=F(k, 4), beat=k, role="current", episode="fixed", operation="ordinary_commit",
            read_stage="fresh_selected", used_current=dict(currents),
            bands={e: (j, j) for e, j in currents.items()}))
    return dict(source_nodes=set(source_C), target_nodes=set(event_C), source_C=source_C,
        source_edges={"a-p": ("a", "p"), "b-p": ("b", "p")},
        source_bands={"a-p": (F(1, 8),)*2, "b-p": (F(1, 8),)*2},
        target_edges=edges, expanded_node="p", module={"x", "y"},
        event_C=event_C, event_time=F(0), samples=samples,
        policy=dict(beats=2, duration=F(1, 2), current_margin=F(1, 16),
                    minimum_mass=F(1), separation=F(1), diameter=F(1, 64),
                    W_scale=F(1), Z_scale=F(1)))


def checks():
    results = {"positive_finite_observation": certificate(synthetic_case())}

    def rejection(name, mutate, reason):
        case = synthetic_case()
        mutate(case)
        try:
            certificate(case)
        except Unresolved as error:
            need(str(error) == reason, name + ": wrong rejection: " + str(error))
        else:
            raise AssertionError(name + ": unexpectedly accepted")
        results[name] = reason

    rejection("missing_parent", lambda c: c["source_bands"].update({e:(F(0),F(0)) for e in c["source_edges"]}), "missing_parent_organization")
    rejection("zero_duration_replay", lambda c: c["samples"][1].update(time=c["samples"][0]["time"]), "nonconsecutive_or_zero_duration")
    rejection("insufficient_physical_duration", lambda c: c["policy"].update(duration=F(1)), "short_elapsed_time")
    rejection("reset_cannot_extend_live_window", lambda c: c["samples"][1].update(episode="reset"), "window_boundary_or_wrong_capture")
    rejection("reset_role_is_not_live", lambda c: c["samples"][1].update(role="reset"), "window_boundary_or_wrong_capture")
    rejection("failed_attempt_is_not_a_beat", lambda c: c["samples"][1].update(operation="failed"), "window_boundary_or_wrong_capture")
    rejection("consumed_current_is_not_fresh_read", lambda c: c["samples"][1].update(read_stage="consumed"), "window_boundary_or_wrong_capture")
    rejection("missing_beat", lambda c: c["samples"][1].update(beat=9), "nonconsecutive_or_zero_duration")
    rejection("wrong_continuity_operand", lambda c: c["samples"][1]["used_current"].update({"a-x": F(0)}), "continuity_stage_mismatch")
    rejection("unresolved_zero_edge", lambda c: c["samples"][1]["bands"].update({"x-y": (-F(1,1000),F(1,1000))}), "unresolved_or_small_current_sign")
    rejection("sign_margin_equality", lambda c: c["policy"].update(current_margin=F(1,8)), "unresolved_or_small_current_sign")
    rejection("transient_sink", lambda c: c["samples"][1]["bands"].update({"x-y": (F(1,8),)*2}), "no_additional_child")
    rejection("strict_separation_boundary", lambda c: c["policy"].update(separation=F(61,36)), "indistinct_parent_footprints")
    rejection("mass_boundary", lambda c: c["policy"].update(minimum_mass=F(9,4)), "insufficient_persistent_core_mass")
    rejection("W_drift_hidden_by_C", lambda c: c["samples"][1].update(W=(F(2),)*3), "full_state_window_drift")
    rejection("Z_drift_hidden_by_C", lambda c: c["samples"][1].update(Z=(F(1),)*3), "full_state_window_drift")
    rejection("missing_history", lambda c: c["samples"][1].update(W=None), "history_channel_changed")

    def allocation_only(c):
        c["module"]={"x","y","u","w"}
        c["target_nodes"]={"a","b"}|c["module"]
        c["event_C"]={"a":F(2),"b":F(2),**{n:F(1,8) for n in c["module"]}}
        c["target_edges"].update({"u-x":("u","x"),"w-y":("w","y")})
        used={e:F(1,8) if e in ("u-x","w-y") else F(0) for e in c["target_edges"]}
        previous=dict(c["event_C"])
        for s in c["samples"]:
            for e,(a,b) in c["target_edges"].items():
                previous[a]-=F(1,4)*used[e];previous[b]+=F(1,4)*used[e]
            s.update(C=dict(previous),used_current=dict(used),bands={e:(j,j) for e,j in used.items()},
                     W=(F(1),)*5,Z=(F(0),)*5)
        c["policy"]["minimum_mass"]=F(1,8)

    rejection("new_allocations_are_not_distinct_parent_footprints", allocation_only,
              "indistinct_parent_footprints")

    def foreign_region(c):
        c["source_nodes"].add("foreign");c["target_nodes"].add("foreign")
        c["source_C"]["foreign"]=c["event_C"]["foreign"]=F(1)
        c["target_edges"]["foreign-x"]=("foreign","x")
        for s in c["samples"]:
            s["C"]["foreign"]=F(1);s["used_current"]["foreign-x"]=F(0)
            s["bands"]["foreign-x"]=(F(1,8),)*2

    rejection("unrelated_region_not_imported_as_child", foreign_region, "no_additional_child")
    # The initial graph stays connected through an exactly zero edge. Treating
    # a signed-zero uncertainty as an absent edge would invent two child regions.
    need(regions({"a","b","c"}, {"ab":("a","b"),"ac":("a","c")},
                 {"ab":(F(1),)*2,"ac":(F(1),)*2}, F(0))
         == {"b":{"b"},"c":{"c"}}, "ambiguous_branch_assigned")
    need(regions({"a","b","c"}, {"ab":("a","b"),"ba":("b","a"),"ac":("a","c")},
                 {"ab":(F(1),)*2,"ba":(F(1),)*2,"ac":(F(1),)*2}, F(0))
         == {"c":{"a","b","c"}}, "leaking_cycle_not_assigned")
    need(regions({"a","b"}, {"ab":("a","b"),"ba":("b","a")},
                 {"ab":(F(1),)*2,"ba":(F(1),)*2}, F(0)) == {}, "cycle_invented_sink")
    results["all_route_controls"] = "ambiguous branch, leaking cycle, terminal cycle"
    # Keep the successful window intact and append a continuity-consistent
    # later sample that loses one fresh sink. No constitutive law is asserted.
    case=synthetic_case()
    original=certificate(case)
    later=deepcopy(case["samples"][-1]);later["time"]+=F(1,4);later["beat"]+=1
    for e,(a,b) in case["target_edges"].items():
        later["C"][a]-=F(1,4)*later["used_current"][e]
        later["C"][b]+=F(1,4)*later["used_current"][e]
    later["bands"]["x-y"]=(F(1,8),)*2
    case["samples"].append(later);case["policy"].update(beats=3,duration=F(3,4))
    try:
        certificate(case)
    except Unresolved as error:
        need(str(error)=="no_additional_child", "wrong later-loss rejection")
        results["finite_observation_does_not_imply_future_persistence"] = dict(
            original_window=original, appended_sample_loses_child=True)
    else:
        raise AssertionError("loss of one child was not detected")
    # Change identifiers and serialization order, preserving actual lineage.
    case=synthetic_case();rename={"p":"z", "a":"d", "b":"c", "x":"b", "y":"a"}
    for field in ("source_nodes","target_nodes","module"):
        case[field]={rename[n] for n in case[field]}
    case["expanded_node"]=rename[case["expanded_node"]]
    for field in ("source_C","event_C"):
        case[field]={rename[n]:c for n,c in reversed(list(case[field].items()))}
    for field in ("source_edges","target_edges"):
        case[field]={e:(rename[a],rename[b]) for e,(a,b) in reversed(list(case[field].items()))}
    for sample in case["samples"]:
        sample["C"]={rename[n]:c for n,c in reversed(list(sample["C"].items()))}
    need(certificate(case)==original, "relabel_or_order_changes_decision")
    results["relabel_and_order_covariance"]=True
    case=synthetic_case()
    for field in ("source_edges","target_edges"):
        case[field]={e:(b,a) for e,(a,b) in case[field].items()}
    case["source_bands"]={e:(-hi,-lo) for e,(lo,hi) in case["source_bands"].items()}
    for sample in case["samples"]:
        sample["bands"]={e:(-hi,-lo) for e,(lo,hi) in sample["bands"].items()}
        sample["used_current"]={e:-j for e,j in sample["used_current"].items()}
    need(certificate(case)==original, "edge_orientation_changes_decision")
    results["edge_orientation_covariance"]=True
    # Exact continuity accumulation, including a finite represented-error budget.
    q, c0, inflow, duration, error = F(9,2), F(1,4), F(1,8), F(35), F(1,16)
    need(c0 + duration*inflow - error > q, "long_lived_sink_bound_not_excluding")
    results["uniform_inflow_exclusion"] = dict(charge=str(q), initial=str(c0), inflow=str(inflow),
        duration=str(duration), total_error=str(error), forced_resource=str(c0+duration*inflow-error))
    return results

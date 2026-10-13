"""Preregistered resource-only A_PC companion; no implicit native credit."""

import argparse
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import json
import sys

import p984d_apc_feasibility as exclusion

prior, r, b = exclusion.prior, exclusion.r, exclusion.b
o = r.oracle
SELF = b.HERE + "p984d_apc_companion.py"
TEST = b.HERE + "test_p984d_apc_companion.py"
PLAN = b.BASE + "P9-8.4d-APCSourceCompanionPlan.md"
ACCEPTANCE = b.BASE + "P9-8.4d-APCAllocationAcceptance.json"
INPUTS = b.BASE + "P9-8.4d-APCSourceCompanionInputs.json"
RESULTS = b.BASE + "P9-8.4d-APCSourceCompanionResults.json"
REVIEW = b.BASE + "P9-8.4d-APCSourceCompanionReview.md"
PILOT = "P984D-D94-E-1-P3::A_PC"
DEBT = "D11-G9-DEBT-CANONICAL-PORT-ALLOCATION"
OBLIGATION = "D11-G9-VERIFY-RESOURCE-HISTORY-TARGET-READMISSION-AND-ATOMICITY"


def authority_traces():
    side = b.ROOT / "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
    sys.path.insert(0, str(side / "tool/src"))
    from grcv4_explorer.successor import load_successor_forensic_context
    from grcv4_explorer.forensic import contract_provenance, debt_lifecycle
    context = load_successor_forensic_context(b.ROOT, side)
    return [contract_provenance(context, name) for name in (
        "D10.2-EC-PARENT-REAL-PC", "D11-G9-EC-RESOURCE-DISTRIBUTION",
        "D11-G9-EC-LIFECYCLE-READMISSION")] + [debt_lifecycle(context, DEBT)]


def acceptance():
    record = b.read(exclusion.RESULTS)
    exclusion.check(record)
    return b.seal(dict(schema="p984d-apc-allocation-acceptance-v1",
        status="accepted_by_user", date="2026-10-12",
        evidence=b.bind([exclusion.RESULTS, exclusion.REVIEW]),
        evidence_digest=record["record_digest"], accepted_scope=exclusion.domain(),
        companion_authorized=True, native_cells_accepted=0,
        general_impossibility_accepted=False, aggregate_closed=False))


def initial(manifest):
    before = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    nodes = before.geometry.reference.graph.live_node_ids
    old = before.current
    values = list(old.C)
    center = nodes.index("source-s")
    outside = [i for i, n in enumerate(nodes) if n != "source-s"]
    b.require(len(outside) == 9 and Q(values[center]) == 3, "unexpected source recipe")
    values[center] -= 3/4
    for i in outside[:8]:
        values[i] += 3/32
    changed = replace(before, current=replace(old, C=tuple(values)))
    b.require(sum(map(Q, values)) == sum(map(Q, old.C)), "charge-changing companion")
    b.require(changed.reset == before.reset and changed.current.W_A == old.W_A
        and changed.current.Z_4 == old.Z_4 and changed.current.C != changed.reset.C,
        "history substitution")
    return changed


def make_manifest():
    old = b.read(prior.INPUTS)
    prior.check_manifest(old)
    accepted = b.read(ACCEPTANCE)
    b.require(accepted == acceptance(), "exclusion acceptance drift")
    before = initial(old)
    paths = {row["path"] for row in old["source_bindings"]} | {
        SELF, TEST, PLAN, ACCEPTANCE, exclusion.SELF, exclusion.RESULTS,
        exclusion.REVIEW, prior.INPUTS}
    return b.seal(dict(schema="p984d-apc-source-companion-inputs-v1",
        family="A_PC", source_bindings=b.bind(sorted(paths)),
        initial_inputs=before.to_payload(), old_manifest_digest=old["record_digest"],
        layout_cases=old["cases"], pilot=PILOT, source_current_beats=1,
        source_reset_beats=0, target_beats_per_role=10,
        change="initial_current_charge_preserving_center_to_eight_exterior_vertices_only",
        current_center="9/4", exterior_increment="3/32", changed_exterior_count=8,
        authority_traces=authority_traces(),
        ledger_disposition=dict(design_debt=DEBT, design_reopened=False,
            forward_obligation=OBLIGATION, runtime_obligation="open",
            new_missing_authority_debt=False, historical_ledger_changed=False),
        stop_rule="stop_on_first_failed_pilot_before_native_or_any_source_search",
        user_accepted=False, aggregate_closed=False))


def check_manifest(manifest):
    b.check_digest(manifest)
    b.check_bindings(manifest["source_bindings"])
    b.require(manifest == make_manifest(), "companion preregistration drift")


def independent_source(manifest):
    before = b.GeometryStageInputs.from_payload(manifest["initial_inputs"])
    graph = before.geometry.reference.graph.port_graph.to_payload()
    state = before.current
    output = o.PaperAPC(graph).step(state.C, state.W_A, state.Z_4)
    proof = o.check_step(graph, state.C, state.W_A, state.Z_4, output)
    # Metadata from the unchanged one-beat schedule, never the old scientific image.
    original = r.state(b.read(prior.INPUTS)["expected_source"])
    current = b.GRCV4AuthoritativeState(tuple(output["C"]), tuple(output["W_A"]), tuple(output["Z_4"]))
    after = replace(original.inputs, current=current, reset=before.reset)
    after = replace(after, geometry=r.geometry(after, current))
    seed = replace(original, inputs=after)
    r.charge_record(seed.inputs, current)
    r.charge_record(seed.inputs, before.reset)
    return seed, dict(output=output, errors={k:str(v) for k,v in proof["errors"].items()})


def bind_case(seed, old):
    case = deepcopy(old)
    request = case["request"]
    request.update(source_state_digest=seed.scientific_digest,
        history_policy=o.history_policy(b.authority_payload(seed.inputs.current),
            b.authority_payload(seed.inputs.reset)),
        operation_id=request["operation_id"]+"-source-companion")
    identity = case["oracle"]["event_identity"]
    identity["source_state_digest"] = seed.scientific_digest
    for key in ("candidate_history_policy_digest", "carrier_history_policy_digest"):
        identity[key] = request["history_policy"][key]
    layout = next(x for x in prior.construction.layouts() if x["id"] == case["fixture_id"])
    case["oracle"] = prior.construction.previous.target_oracle(seed.to_payload(), case, request, layout)
    case["changes_from_frozen"] = ["preregistered_initial_current_resources_and_resulting_source_image"]
    return case


def stage(graph, c, w, z):
    """Retain signed full-equation intervals even when the positivity gate fails."""
    output = o.PaperAPC(graph).step(c, w, z)
    high = o.IntervalRows(o.model_for(graph))
    h = high.I + o.number(o.KAPPA_H) * o.IV.matrix(
        [list(z[i*len(w):(i+1)*len(w)]) for i in range(len(w))])
    read = high.read("A", o.vector(c), o.vector(w), h)
    cn = o.vector(c) - o.number(b.DT)*high.B*read["J"]
    signs = [[str(o.endpoint(v, side)) for side in (0, 1)] for v in cn]
    try:
        proof = o.check_step(graph, c, w, z, output)
        error, bounds = None, {k:str(v) for k,v in proof["errors"].items()}
    except ValueError as exc:
        error, bounds = str(exc), None
    return dict(input=dict(C=list(c), W_A=list(w), Z_4=list(z)), output=output,
        resource_intervals=signs, error=error, errors=bounds)


def run(manifest):
    check_manifest(manifest)
    seed, source = independent_source(manifest)
    old = next(c for c in manifest["layout_cases"] if c["case_id"] == PILOT)
    case = bind_case(seed, old)
    target = r.independent_target(seed, case)
    graph = case["oracle"]["target_graph"]
    trajectories = {}
    for role in r.ROLES:
        state = getattr(target.inputs, role)
        c, w, z = state.C, state.W_A, state.Z_4
        rows = []
        for index in range(1, 11):
            row = dict(index=index, **stage(graph,c,w,z))
            rows.append(row)
            if row["error"] is not None:
                break
            c,w,z = (row["output"][k] for k in ("C","W_A","Z_4"))
        trajectories[role] = rows
    failed = [dict(role=role,index=row["index"],message=row["error"])
        for role,rows in trajectories.items() for row in rows if row["error"]]
    return b.seal(dict(schema="p984d-apc-source-companion-results-v1",
        manifest_digest=manifest["record_digest"], source=source, nominal_source=seed.to_payload(),
        case=case,target=target.to_payload(),trajectories=trajectories,
        failures=failed, status="pilot_infeasible" if failed else "pilot_positive_pending_remaining_layouts",
        native_source_steps=0,native_target_steps=0,topology_events=0,
        runtime_cells_closed=0,uniform_neighborhood_proved=False,
        user_accepted=False,aggregate_closed=False))


def check(manifest, record, *, numerics=False):
    check_manifest(manifest)
    b.check_digest(record)
    b.require(record["schema"]=="p984d-apc-source-companion-results-v1"
        and record["manifest_digest"]==manifest["record_digest"],"result binding drift")
    b.require(all(type(record[k]) is int and record[k]==0 for k in (
        "native_source_steps","native_target_steps","topology_events","runtime_cells_closed"))
        and all(record[k] is False for k in ("uniform_neighborhood_proved","user_accepted","aggregate_closed")),
        "companion scope promotion")
    seed=r.state(record["nominal_source"])
    old=next(c for c in manifest["layout_cases"] if c["case_id"]==PILOT)
    b.require(record["case"]==bind_case(seed,old)
        and record["target"]==r.independent_target(seed,record["case"]).to_payload(),"transfer drift")
    failures=[]
    b.require(set(record["trajectories"])==set(r.ROLES),"both roles required")
    for role,rows in record["trajectories"].items():
        current=b.authority_payload(getattr(r.state(record["target"]).inputs,role))
        for i,row in enumerate(rows,1):
            b.require(row["index"]==i and row["input"]==current,"trajectory linkage drift")
            current={k:row["output"][k] for k in ("C","W_A","Z_4")}
            if row["error"]:
                b.require(i==len(rows) and any(Q(p[1])<0 for p in row["resource_intervals"]),
                    "unsubstantiated exclusion")
                failures.append(dict(role=role,index=i,message=row["error"]))
        b.require(len(rows)==10 or rows[-1]["error"] is not None,"incomplete trajectory")
    b.require(record["failures"]==failures and record["status"]==(
        "pilot_infeasible" if failures else "pilot_positive_pending_remaining_layouts"),"outcome drift")
    if numerics:
        b.require(record==run(manifest),"companion equations drift")
    return dict(status=record["status"],failures=failures,native_events=0,runtime_cells_closed=0,
        interval_equations_recomputed=numerics,uniform_neighborhood_proved=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare",action="store_true")
    mode.add_argument("--run",action="store_true")
    mode.add_argument("--check",action="store_true")
    parser.add_argument("--recheck-numerics",action="store_true")
    args=parser.parse_args()
    b.require(not args.recheck_numerics or args.check,"recheck requires check")
    if args.prepare:
        b.write_new(ACCEPTANCE,acceptance())
        b.write_new(INPUTS,make_manifest())
        print("Companion preregistered; no trajectories executed")
        return
    manifest=b.read(INPUTS)
    if args.run:
        result=run(manifest)
        b.write_new(RESULTS,result)
    else:
        result=b.read(RESULTS)
    print(json.dumps(check(manifest,result,numerics=args.recheck_numerics),indent=2))


if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Read-only CI-0/PC-0 stage pressure; NOT a CAN-LSF witness or ATC engine.

Run with repository .venv Python. Default: fresh evidence on stdout.
--check: compare source identities and record integrity without a numerical run.
All generated records remain proposed until separately reviewed/admitted.
"""
from dataclasses import replace
import argparse
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
INV = "implementation/investigations/grc9v4-constitutive-design"
SIDE = ROOT / INV / "tools/exploratory-side-tool"
RECORD = ROOT / INV / "evidence/atc-ci-pc/ATCCIPCStepBoundaryAudit.json"
sys.path[:0] = [str(ROOT / "src"), str(ROOT), str(SIDE / "tool/src")]

from grcv4_explorer.atc import load_current_forensic_context, reconstruction_path, debt_lifecycle
from grcv4_explorer.canonical import digest, record_digest, file_sha256
from pygrc.models import grc_v4_ci as ci, grc_v4_pc as pc
from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
from pygrc.models.grc_v4_state import GRCV4AuthoritativeState
from pygrc.models.grc_v4_step import ResourceBoundaryError
from tests.models.test_grc_v4_ci import fixture as ci_fixture
from tests.models.test_grc_v4_pc import configure as pc_configure


def require(ok, reason):
    if not ok:
        raise AssertionError(reason)


def joint_root_evidence(root):
    """Bind selected J/h, residuals and the certificate, not only the recipe."""
    trial = root.selected
    interval = lambda x: dict(lo=str(x.lo), hi=str(x.hi))
    body = dict(recipe=root.to_payload(), selected_inputs=trial.inputs.to_payload(),
        current=trial.point.current.values,
        hodge=trial.inputs.geometry.one_form_hodge.matrix,
        generated_hodge=trial.generated.one_form_hodge.matrix,
        structural_source=trial.structural_source.increment,
        current_residual=[str(x) for x in trial.current_residual],
        geometry_residual=[[str(x) for x in row] for row in trial.geometry_residual],
        analytic_current_residual=[interval(x) for x in trial.analytic_current_residual],
        analytic_geometry_residual=[[interval(x) for x in row] for row in trial.analytic_geometry_residual],
        certificate_bounds=root.certificate.bounds.to_dict(), evaluations=root.evaluations)
    return dict(selected_root_digest=digest(body), recipe_identity=root.identity,
        domain_id=root.inputs.geometry.reference.profile.params_resolved.realization.contraction_domain_id,
        certificate_digest=digest(body["certificate_bounds"]), selected_hodge=body["hodge"])


def audit_family(family):
    graph = GRCV4Graph(("p", "u0", "u1", "v0", "v1"), tuple(
        OrientedEdge("e" + str(i), "p", v)
        for i, v in enumerate(("u0", "u1", "v0", "v1"))))
    before, backend = ci_fixture("A", graph=graph, C=(1.5, 1., 1., 2., 2.),
                                 W=(.75, .75, .625, .625))
    before = replace(before, reset=GRCV4AuthoritativeState(
        (1.25, 1.125, 1.125, 2., 2.), (.7, .7, .6, .6), None))
    if family == "A_PC":
        z = tuple(.25 if i == j else 0. for i in range(4) for j in range(4))
        rz = tuple(.5 if i == j else 0. for i in range(4) for j in range(4))
        before = pc_configure(before, z=z, reset_z=rz, weight_lower=.5, weight_upper=1.)
    module = ci if family == "A_CI" else pc
    Step = ci.ProvisionalCandidateCIStep if family == "A_CI" else pc.ProvisionalCandidatePCStep
    Read = ci.CandidateCIRoot if family == "A_CI" else pc.CandidatePCRead
    read_name = "CandidateCIRoot" if family == "A_CI" else "CandidatePCRead"
    payload = before.to_payload()
    with patch.object(module, "CandidateAWriter", wraps=module.CandidateAWriter) as writer:
        with patch.object(module, read_name, wraps=Read) as reads:
            if family == "A_PC":
                with patch.object(pc, "scalar_zoh", wraps=pc.scalar_zoh) as carrier:
                    step = Step(before, backend)
                source = tuple(x for row in step.read.structural_source.increment for x in row)
                require(carrier.call_count == 1, "one carrier write")
                require(carrier.call_args.args == (before.current.Z_4, source, before.dt,
                    before.geometry.reference.profile.params_resolved.realization.tau_PC),
                    "old carrier and pre-continuity held source")
            else:
                step = Step(before, backend)
        require(writer.call_count == 1, "one A writer")
    selected = step.root.selected.point if family == "A_CI" else step.read.point
    restart = step.restart.selected.point if family == "A_CI" else step.restart.point
    after = step.next_inputs
    require(reads.call_count == 3, "independent reset, live, final reads")
    require(reads.call_args_list[0].args[0].current == before.reset, "actual reset role")
    require(reads.call_args_list[1].args[0].current == before.current, "actual live role")
    require(reads.call_args_list[2].args[0].current == after.current, "final written state")
    require(reads.call_args_list[2].args[0].dt == 0, "read-only poststate solve")
    require(writer.call_args.args[0] is selected, "writer consumes selected pre-continuity current")
    require(step.resource.continuity_evaluations == 1, "one continuity evaluation")
    require(after.current.C == step.resource.provisional_state.C, "final resource matches continuity")
    require(after.reset == before.reset and after.current != after.reset, "independent reset unchanged")
    require(after.step_index == before.step_index + 1 and after.time == before.time + before.dt,
            "one temporal advancement")
    require(selected.current.values != restart.current.values, "fixture discriminates consumed vs poststate read")
    require(before.to_payload() == payload, "no mutation of captured prestate")
    fresh = Read(replace(after, dt=0), backend)
    fresh_point = fresh.selected.point if family == "A_CI" else fresh.point
    require(fresh_point.current == restart.current, "fresh poststate read equals restart")
    joint = None
    if family == "A_CI":
        require(fresh_point.inputs.geometry == restart.inputs.geometry, "fresh CI geometry equals restart")
        require(fresh == step.restart, "entire CI root, selected point and certificate equal restart")
        joint = joint_root_evidence(fresh)
        require(joint == joint_root_evidence(step.restart), "canonical joint-root evidence matches")
    if family == "A_PC":
        require(step.writer.authority.state.Z_4 == before.current.Z_4, "W writer preserves old Z")
        require(after.current.Z_4 != before.current.Z_4, "carrier changes in this fixture")
        require(restart.inputs.geometry == pc.carrier_geometry(after, after.current),
                "poststate read uses new committed carrier")
        require(restart.inputs.geometry != selected.inputs.geometry, "old/new geometries discriminate")
    else:
        require(after.current.Z_4 is None and step.carrier_writes == 0, "CI has no carrier writer")
    with patch.object(module, "CandidateAWriter", side_effect=AssertionError("zero duration wrote W")):
        with patch.object(pc, "scalar_zoh", side_effect=AssertionError("zero duration wrote Z")):
            zero = Step(replace(after, dt=0), backend)
    require(zero.next_inputs == replace(after, dt=0) and zero.resource.continuity_evaluations == 0,
            "zero-duration admission is not another beat or an event")
    calls = []
    def fail_final(inputs, differential):
        calls.append(inputs)
        if len(calls) == 3:
            error = ci.CIStageError if family == "A_CI" else pc.PCStageError
            raise error("no_admitted_root", "injected final read rejection")
        return Read(inputs, differential)
    with patch.object(module, read_name, side_effect=fail_final):
        try:
            Step(before, backend)
        except ResourceBoundaryError as exc:
            require((exc.stage, exc.code) == ("final_reconstruction", "no_admitted_root"),
                    "final rejection retains its stage")
        else:
            raise AssertionError("final read rejection was ignored")
    require(before.to_payload() == payload, "failed provisional step left captured state intact")
    return dict(family=family,
        before=payload, after=after.to_payload(),
        consumed_stage=selected.inputs.stage, event_read_stage=restart.inputs.stage,
        consumed_current=selected.current.values, poststate_current=restart.current.values,
        continuity_evaluations=1, W_writes=1, Z_writes=step.carrier_writes,
        independent_role_reads=True, fresh_poststate_read_matches=True,
        joint_root=joint, injected_failure_type="CIStageError" if family == "A_CI" else "PCStageError",
        zero_duration_is_identity=True, injected_final_rejection_preserves_prestate=True,
        scope="shipped zero-site-derivative stage fixture; not nonlinear research physics, live owner or native ATC")


def run():
    context = load_current_forensic_context(ROOT, SIDE)
    queries = []
    for kind, ids, query in (
        ("claim", ("ATC-LSF-G7-CL-06", "ATC-LSF-G56-CL-01"), reconstruction_path),
        ("debt", ("ATC7-DB-05", "ATC7-DB-15", "ATC7-DB-16", "ATC7-DB-24", "ATC7-DB-26"), debt_lifecycle)):
        for identifier in ids:
            trace = query(context, identifier)
            queries.append(dict(kind=kind, identifier=identifier, trace_digest=trace["trace_digest"],
                classification=trace["rows"][0]["classification"], source_ref=trace["rows"][0]["source_ref"],
                edge_ref_count=len(trace["rows"][0]["edge_refs"]),
                edge_refs_digest=digest(trace["rows"][0]["edge_refs"])))
    results = [audit_family(family) for family in ("A_CI", "A_PC")]
    paths = {Path(__file__).resolve(), ROOT / "specs/grc-v4-spec.md",
        ROOT / INV / "decisions/ATCCIPCRealizationNativeProgram.md",
        ROOT / INV / "decisions/ATC1Acceptance.md",
        ROOT / INV / "research/atc_sector_reference.py",
        SIDE / "records/ATCAOSResearchAdmission.json"}
    for name, module in list(sys.modules.items()):
        path = getattr(module, "__file__", None)
        if path and name.startswith(("pygrc.", "tests.models.", "grcv4_explorer.")):
            path = Path(path).resolve()
            if path.suffix == ".py" and path.is_relative_to(ROOT):
                paths.add(path)
    record = dict(schema="grcv4_atc_ci_pc_step_boundary_v1", status="review_feedback_integrated_boundary_hardened",
        CI0_staging_review="PASS (user review); full-root evidence hardened afterward",
        scientific_acceptance=False, graph_admitted=False, native_ATC_executed=False,
        CI_causal_witness_proved=False, PC_causal_witness_proved=False, ATC2_closed=False,
        authority_graph_digest=context.graph_digest, authority_traces=queries, cases=results,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=file_sha256(p)) for p in sorted(paths)])
    record["record_digest"] = record_digest(record, "record_digest")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        record = json.loads(RECORD.read_text())
        require(record["record_digest"] == record_digest(record, "record_digest"), "record identity")
        for b in record["source_bindings"]:
            require(file_sha256(ROOT / b["path"]) == b["sha256"], "source drift: " + b["path"])
        require(load_current_forensic_context(ROOT, SIDE).graph_digest == record["authority_graph_digest"],
                "authority graph changed")
        print(json.dumps(dict(status="passed", scope="retained identity checks only", record_digest=record["record_digest"])))
    else:
        print(json.dumps(run(), indent=2))


if __name__ == "__main__":
    main()

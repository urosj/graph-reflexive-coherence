"""Shared checkout-only numerical runner for the A and C five-realization examples.

Fixtures construct identity-bound inputs; production provisional steps do all
numerical work. This is not a new supported-profile registration or a lifecycle
receipt campaign. Reports distinguish retained poststate from read diagnostics.
"""

import argparse
from dataclasses import replace
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path

import numpy as np

from pygrc.models.grc_v4_ci import ProvisionalCandidateCIStep
from pygrc.models.grc_v4_pc import ProvisionalCandidatePCStep
from pygrc.models.grc_v4_profile import resolve_profile
from pygrc.models.grc_v4_realizations import CandidateAOSPass, CandidateCOSPass
from pygrc.models.grc_v4_rg2b import ProvisionalCandidateRG2bStep
from pygrc.models.grc_v4_rg2b_graph import RG2bGraphDomain
from pygrc.models.grc_v4_step import (
    ProvisionalCandidateAOSStep,
    ProvisionalCandidateCOSStep,
)
from tests.models.test_grc_v4_ci import configure as ci_configure
from tests.models.test_grc_v4_cipc import configure as cipc_configure
from tests.models.test_grc_v4_pc import configure as pc_configure
from tests.models.test_grc_v4_profile import reidentify
from tests.models.test_grc_v4_rg2b_graph import graph_fixture

FAMILIES = ("OS", "CI", "RG2b", "PC", "CI+PC")
DT = 2**-10
GAIN = 0.075
STEPS = 10


def make_inputs(candidate):
    domain = RG2bGraphDomain(
        2.0,
        2.0 if candidate == "A" else 1.0,
        0.125,
        0.25,
        0.375,
        0.015625,
        0.125,
        DT,
    )
    rg, backend = graph_fixture(
        candidate,
        n=4,
        pairs=[(0, 1), (1, 2), (1, 3)],
        domain=domain,
        gain=GAIN,
        tolerance=1e-11,
        C=(2.12, 1.88, 2.10, 1.90),
    )
    ref = rg.geometry.reference
    params = ref.profile.params_resolved.to_payload()
    identity = ref.profile.identity_payload.to_payload()
    params["realization"] = dict(
        schema_version="grcv4-os-params-v1",
        predictor_policy_id="reference_geometry_predictor_v1",
        corrector_policy_id="one_fresh_geometry_corrector_v1",
        split_residual_norm_id="edge_l2_v1",
        tolerance=1e-10,
    )
    identity.update(realization="OS", profile_family_id=candidate + "_OS")
    reidentify(params, identity)
    os = replace(
        rg, geometry=replace(ref, profile=resolve_profile(params, identity)).geometry()
    )
    ci = ci_configure(rg, gain=GAIN, radius=0.2, tolerance=1e-12)
    pc = pc_configure(
        rg,
        gain=GAIN,
        radius=1.0,
        resource_radius=4.25,
        weight_lower=1.75,
        weight_upper=2.25,
        tau=2 * DT,
    )
    cipc = cipc_configure(pc, domain_radius=0.2, tolerance=1e-12)
    states = dict(zip(FAMILIES, (os, ci, rg, pc, cipc), strict=True))
    for state in states.values():
        r = state.geometry.reference
        assert r.graph == ref.graph and r.edge_weights == ref.edge_weights
        assert r.K4_base == ref.K4_base and r.context == ref.context
        assert (
            r.profile.params_resolved.candidate == ref.profile.params_resolved.candidate
        )
        assert state.current.C == rg.current.C and state.current.W_A == rg.current.W_A
        assert state.current.Z_4 is None or not any(state.current.Z_4)
        assert state.reset == state.current and state.dt == DT
    return states, backend


def source_matrix(point):
    """Literal normalized star outer products, independent of source assembler."""
    graph = point.inputs.geometry.reference.graph
    flat = np.array(point.read.causal_flat.values)
    p = point.inputs.geometry.reference.profile.params_resolved.candidate
    zeta = p.zeta_A if point.inputs.current.W_A is not None else p.zeta_C
    stars = [
        [
            i
            for i, e in enumerate(graph.oriented_edges)
            if v in (e.tail_node_id, e.head_node_id)
        ]
        for v in graph.live_node_ids
    ]
    counts = np.array([sum(i in star for star in stars) for i in range(len(flat))])
    out = np.zeros((len(flat), len(flat)))
    for star in stars:
        local = np.zeros(len(flat))
        local[star] = flat[star] / np.sqrt(counts[star])
        out += zeta * np.outer(local, local)
    return out


def read_diagnostics(point):
    is_a = point.inputs.current.W_A is not None
    algebra = point if is_a else point.algebra
    p = point.inputs.geometry.reference.profile.params_resolved.candidate
    zeta = p.zeta_A if is_a else p.zeta_C
    result = dict(
        H=point.inputs.geometry.one_form_hodge.matrix,
        potential=algebra.potential.values,
        J0=algebra.baseline.values,
        J=point.current.values,
        read_flux=point.read.flux.values,
        feedback_current=(zeta * np.array(point.read.flux.values)).tolist(),
        causal_flat=point.read.causal_flat.values,
        source=source_matrix(point).tolist(),
    )
    if is_a:
        result.update(
            W_hat_A=point.W_hat_A,
            contrast=point.contrast,
            descriptors=point.descriptors,
        )
    else:
        result.update(
            T_C=algebra.selector.selected.values,
            retained_hodge=algebra.retained_hodge.matrix,
            deformation=algebra.deformation,
            mobility=algebra.transport.mobility.diagonal,
            response=algebra.flux_response,
        )
    return result


def advance(name, before, backend):
    if name == "OS":
        step = (
            ProvisionalCandidateAOSStep(before, backend)
            if backend is not None
            else ProvisionalCandidateCOSStep(before)
        )
        point = step.os_pass.corrector
        extra = dict(
            predictor=read_diagnostics(step.os_pass.predictor),
            split_defect=step.os_pass.residual.values,
            split_admitted=step.os_pass.residual.admitted,
        )
    elif name in ("CI", "CI+PC"):
        step = ProvisionalCandidateCIStep(before, backend)
        point = step.root.selected.point
        extra = dict(
            root_evaluations=step.root.evaluations,
            joint_residual_l2=math.sqrt(float(step.root.selected.residual_squared)),
        )
    elif name == "PC":
        step = ProvisionalCandidatePCStep(before, backend)
        point, extra = step.read.point, dict(current_solver="direct")
    else:
        step = ProvisionalCandidateRG2bStep(before, backend)
        point = step.point
        extra = dict(
            section_evaluations=step.section.evaluations,
            section_error_upper=float(Fraction(step.section.error_upper)),
            section_diagnostics=dict(step.diagnostics),
        )
    after = step.next_inputs
    diagnostic = read_diagnostics(point)
    graph, profile = before.geometry.reference.graph, before.geometry.reference.profile
    p = profile.params_resolved.candidate
    zeta = p.zeta_A if backend is not None else p.zeta_C
    # Independent identities: continuity, constitutive current closure, carrier
    # write, and the realization-specific geometry equation. No clipping.
    np.testing.assert_allclose(
        after.current.C,
        np.array(before.current.C)
        - DT * np.array(graph.incidence) @ np.array(diagnostic["J"]),
        rtol=0,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        diagnostic["J"],
        np.array(diagnostic["J0"]) + zeta * np.array(diagnostic["read_flux"]),
        rtol=1e-10,
        atol=1e-12,
    )
    assert min(after.current.C) >= 0
    assert math.isclose(sum(after.current.C), before.Q_target, rel_tol=0, abs_tol=1e-11)
    assert after.reset == before.reset and after.receipt_ids == before.receipt_ids
    assert after.step_index == before.step_index + 1 and after.time == before.time + DT
    n = len(graph.live_edge_ids)
    href = np.array(before.geometry.reference.pairings.one_form.matrix)
    old_z = (
        np.zeros((n, n))
        if before.current.Z_4 is None
        else np.array(before.current.Z_4).reshape(n, n)
    )
    source = np.array(diagnostic["source"])
    if name in ("PC", "CI+PC"):
        a = math.exp(-DT / profile.params_resolved.realization.tau_PC)
        np.testing.assert_allclose(
            np.array(after.current.Z_4).reshape(n, n),
            a * old_z + (1 - a) * source,
            rtol=1e-10,
            atol=1e-14,
        )
    else:
        assert after.current.Z_4 is None
    if name != "RG2b":
        operand = (
            np.array(extra["predictor"]["source"])
            if name == "OS"
            else source
            if name == "CI"
            else old_z
            if name == "PC"
            else old_z + source
        )
        np.testing.assert_allclose(
            diagnostic["H"], href + GAIN * operand, rtol=0, atol=2e-12
        )
    # W has a separate post-continuity target. Never label the read-stage W_hat
    # as the writer target or assert that C has a missing/zero W history.
    if backend is not None:
        assert min(after.current.W_A) > 0
        extra.update(
            writer_target=step.writer.W_drv_A,
            writer_descriptors=step.writer.descriptors,
        )
        a = math.exp(-DT / p.tau_A)
        np.testing.assert_allclose(
            after.current.W_A,
            np.exp(
                a * np.log(before.current.W_A) + (1 - a) * np.log(step.writer.W_drv_A)
            ),
            rtol=1e-12,
            atol=1e-14,
        )
    else:
        assert after.current.W_A is None
    # Reuse already executed final readmission. OS alone needs a new read-only
    # predictor/corrector pass: no continuity, clock or history write follows it.
    if name == "OS":
        next_read = (
            CandidateAOSPass(after, backend)
            if backend is not None
            else CandidateCOSPass(after)
        ).corrector
    elif name in ("CI", "CI+PC"):
        next_read = step.restart.selected.point
    elif name == "PC":
        next_read = step.restart.point
    else:
        next_read = step.restart_point
    continuation = read_diagnostics(next_read)
    effects = dict(
        delta_C_baseline=(
            -DT * np.array(graph.incidence) @ np.array(diagnostic["J0"])
        ).tolist(),
        delta_C_readback=(
            -DT * np.array(graph.incidence) @ np.array(diagnostic["feedback_current"])
        ).tolist(),
        delta_C=(np.array(after.current.C) - np.array(before.current.C)).tolist(),
        delta_W=None
        if backend is None
        else (np.array(after.current.W_A) - np.array(before.current.W_A)).tolist(),
        delta_Z=None
        if after.current.Z_4 is None
        else (np.array(after.current.Z_4) - np.array(before.current.Z_4)).tolist(),
        delta_next_J=(np.array(continuation["J"]) - np.array(diagnostic["J"])).tolist(),
        delta_next_H=(np.array(continuation["H"]) - np.array(diagnostic["H"])).tolist(),
    )
    np.testing.assert_allclose(
        effects["delta_C"],
        np.array(effects["delta_C_baseline"]) + np.array(effects["delta_C_readback"]),
        rtol=0,
        atol=1e-12,
    )
    return after, dict(
        step=after.step_index,
        time_after=after.time,
        C_before=before.current.C,
        W_before=before.current.W_A,
        Z_before=before.current.Z_4,
        read=diagnostic,
        diagnostics=extra,
        effects=effects,
        continuation=continuation,
        C_after=after.current.C,
        W_after=after.current.W_A,
        Z_after=after.current.Z_4,
    )


def norm(value):
    return float(np.linalg.norm(value))


def packed(value):
    if value is None:
        return None
    a = np.array(value)
    if a.ndim == 1 and len(a) == 9:
        a = a.reshape(3, 3)
    return a[np.triu_indices(len(a))].tolist()


def fmt(value):
    if value is None:
        return "—"
    a = np.array(value).ravel()
    return "[" + ", ".join(f"{x:.12g}" for x in a) + "]"


def markdown(report):
    lines = [
        f"# Candidate {report['candidate']}: five realizations, ten steps",
        "",
        "Four-node branch: `v000 -> v001 -> v002`, with `v001 -> v003`.",
        "",
        f"Node order: `{report['nodes']}`; edge order: `{report['edges']}`.",
        "",
        f"Initial C: `{report['initial']['C']}`; W: `{report['initial']['W_A']}`. Persistent Z starts at zero.",
        "",
        f"Reference edge weights: `{report['edge_weights']}`. dt={DT}; kappa_H={GAIN}; tau_PC={2 * DT}.",
        "",
        "Within each candidate comparison, topology, initial resource/history, candidate coefficients, reference geometry and time step are identical. Only realization/solver declarations and the presence of Z differ.",
        "",
        "These are production provisional numerical steps, not published lifecycle receipts or newly accepted support. All ten steps include the step owner's admission/reconstruction checks. JSON retains full binary64 values, exact declarations, all matrices and extra solver diagnostics.",
        "",
        "C/W/Z columns are **post-step retained state**. J0/J/read-back, H, source S, potentials and candidate-derived quantities belong to the **read before that step's continuity/write**. H and S are not extra retained state. `W_hat` is the read target, not the post-continuity writer target. C's T_C and retained Hodge are rederived, not W-like memory.",
        "",
        "Continuation is a read-only reconstruction on the poststate, under that realization's next-read policy. It does not execute an eleventh physical step. Δnext J/H combines resource and applicable history/carrier effects; it is not an isolated W-only or Z-only causal intervention. In contrast, ΔC_baseline + ΔC_readback is the exact declared current decomposition at the selected read, up to rounding. Reconstructing each next read is checked against the following step's actual read.",
        "",
        "Symmetric matrices are packed as `[00,01,02,11,12,22]`. Geometry tables show H−Href so small nonzero feedback remains visible. No claim that every pair must separate above numerical error; inspect the printed deltas and method-specific error bounds.",
        "",
    ]
    href = np.array(report["H_reference"])
    lines += [
        "## Geometry-feedback overview",
        "",
        "Read-stage Frobenius norms make carrier build-up visible even when resources nearly overlap. The last column is an observed norm ratio, not a universal gain or an assertion of exact equilibrium.",
        "",
        "| Step | OS ‖H−Href‖F | CI ‖H−Href‖F | RG2b ‖H−Href‖F | PC ‖H−Href‖F | CI+PC ‖H−Href‖F | (CI+PC)/CI norm ratio |",
        "|---|---|---|---|---|---|---|",
    ]
    for i in range(report["steps"]):
        magnitudes = {
            name: norm(np.array(report["runs"][name][i]["read"]["H"]) - href)
            for name in FAMILIES
        }
        ratio = magnitudes["CI+PC"] / magnitudes["CI"] if magnitudes["CI"] else None
        lines.append(
            f"| {i + 1} | "
            + " | ".join(f"{magnitudes[name]:.9e}" for name in FAMILIES)
            + f" | {('—' if ratio is None else format(ratio, '.9f'))} |"
        )
    lines += [""]
    for name in FAMILIES:
        rows = report["runs"][name]
        lines += [
            f"## {name}",
            "",
            "### Retained state",
            "",
            "| Step | C after (all nodes) | W_A after (all edges) | Z after (symmetric packing) |",
            "|---|---|---|---|",
        ]
        for r in rows:
            lines.append(
                f"| {r['step']} | {fmt(r['C_after'])} | {fmt(r['W_after'])} | {fmt(packed(r['Z_after']))} |"
            )
        lines += [
            "",
            "### Current and potential at the read",
            "",
            "| Step | J0 | Total J | Read-back flux | Potential |",
            "|---|---|---|---|---|",
        ]
        for r in rows:
            d = r["read"]
            lines.append(
                f"| {r['step']} | {fmt(d['J0'])} | {fmt(d['J'])} | {fmt(d['read_flux'])} | {fmt(d['potential'])} |"
            )
        lines += [
            "",
            "### Read-back and continuation effects",
            "",
            "| Step | Feedback current ζ·read | ΔC baseline | ΔC read-back | ΔW | ΔZ (packed) |",
            "|---|---|---|---|---|---|",
        ]
        for r in rows:
            e = r["effects"]
            lines.append(
                f"| {r['step']} | {fmt(r['read']['feedback_current'])} | {fmt(e['delta_C_baseline'])} | {fmt(e['delta_C_readback'])} | {fmt(e['delta_W'])} | {fmt(packed(e['delta_Z']))} |"
            )
        lines += [
            "",
            "| Step | Next-read J | Δnext J | Next-read H−Href (packed) | Δnext H (packed) | Next-read source S (packed) |",
            "|---|---|---|---|---|---|",
        ]
        for r in rows:
            c, e = r["continuation"], r["effects"]
            lines.append(
                f"| {r['step']} | {fmt(c['J'])} | {fmt(e['delta_next_J'])} | {fmt(packed(np.array(c['H']) - href))} | {fmt(packed(e['delta_next_H']))} | {fmt(packed(c['source']))} |"
            )
        lines += [
            "",
            "### Structural feedback at the read",
            "",
            "| Step | H−Href (symmetric packing) | S (symmetric packing) | Causal flat read |",
            "|---|---|---|---|",
        ]
        for r in rows:
            d = r["read"]
            lines.append(
                f"| {r['step']} | {fmt(packed(np.array(d['H']) - href))} | {fmt(packed(d['source']))} | {fmt(d['causal_flat'])} |"
            )
        if report["candidate"] == "A":
            lines += [
                "",
                "### Candidate-A read quantities",
                "",
                "| Step | W_hat_A (read target) | W_drv_A (writer target) | Contrast | Descriptors |",
                "|---|---|---|---|---|",
            ]
            for r in rows:
                d = r["read"]
                lines.append(
                    f"| {r['step']} | {fmt(d['W_hat_A'])} | {fmt(r['diagnostics']['writer_target'])} | {fmt(d['contrast'])} | {fmt(d['descriptors'])} |"
                )
        else:
            lines += [
                "",
                "### Candidate-C read quantities",
                "",
                "| Step | T_C | Retained Hodge (symmetric packing) | Deformation |",
                "|---|---|---|---|",
            ]
            for r in rows:
                d = r["read"]
                lines.append(
                    f"| {r['step']} | {fmt(d['T_C'])} | {fmt(packed(d['retained_hodge']))} | {fmt(d['deformation'])} |"
                )
        lines += [""]
        lines += [
            "### Numerical checks",
            "",
            "| Step | Method-specific check (not a shared error norm) |",
            "|---|---|",
        ]
        for r in rows:
            d = r["diagnostics"]
            if name == "OS":
                summary = f"split admitted={d['split_admitted']}; diagnostic ‖defect‖F={norm(d['split_defect']):.9e} (admission uses the declared reference-whitened norm)"
            elif name in ("CI", "CI+PC"):
                summary = f"joint residual={d['joint_residual_l2']:.9e}; live-root evaluations={d['root_evaluations']}"
            elif name == "RG2b":
                summary = f"section error upper={d['section_error_upper']:.9e}; section evaluations={d['section_evaluations']}"
            else:
                summary = "direct current solve; whole-chart carrier admission and ZOH writer passed"
            lines.append(f"| {r['step']} | {summary} |")
        lines += [""]
    lines += [
        "## All five end states",
        "",
        "| Realization | Final C | Final W_A | Final Z (symmetric packing) | Total C |",
        "|---|---|---|---|---|",
    ]
    for name in FAMILIES:
        r = report["runs"][name][-1]
        lines.append(
            f"| {name} | {fmt(r['C_after'])} | {fmt(r['W_after'])} | {fmt(packed(r['Z_after']))} | {sum(r['C_after']):.15g} |"
        )
    lines += [
        "",
        "### Pairwise end-state distances",
        "",
        "Euclidean distance for C/W; Frobenius distance for Z. Absent carrier slots are not treated as zero-valued stored carriers. These are observed floating-point differences, not proofs of separation beyond the certified numerical errors.",
        "",
        "| Pair | ‖ΔC‖₂ | ‖ΔW‖₂ | ‖ΔZ‖F | ‖Δnext J‖₂ | ‖Δnext H‖F |",
        "|---|---|---|---|---|---|",
    ]
    for r in report["end_distances"]:
        lines.append(
            f"| {r['pair']} | {r['C']:.12e} | {('—' if r['W'] is None else format(r['W'], '.12e'))} | {('—' if r['Z'] is None else format(r['Z'], '.12e'))} | {r['next_J']:.12e} | {r['next_H']:.12e} |"
        )
    return "\n".join(lines) + "\n"


def run(candidate):
    states, backend = make_inputs(candidate)
    reference = states["RG2b"].geometry.reference
    report = dict(
        candidate=candidate,
        steps=STEPS,
        dt=DT,
        gain=GAIN,
        nodes=reference.graph.live_node_ids,
        edges=reference.graph.live_edge_ids,
        graph=reference.graph.to_payload(),
        edge_weights=dict(reference.edge_weights),
        H_reference=reference.pairings.one_form.matrix,
        K4_base=reference.K4_base,
        differential_reference=None if backend is None else backend.to_payload(),
        initial=dict(C=states["RG2b"].current.C, W_A=states["RG2b"].current.W_A),
        declarations={
            name: state.geometry.reference.profile.to_payload()
            for name, state in states.items()
        },
        runs={name: [] for name in FAMILIES},
        end_distances=[],
    )
    print(
        f"Candidate {candidate}: four nodes, three branch edges; ten physical steps",
        flush=True,
    )
    for k in range(1, STEPS + 1):
        for name in FAMILIES:
            states[name], row = advance(name, states[name], backend)
            if k > 1:
                previous = report["runs"][name][-1]["continuation"]
                for field in ("J", "H", "source", "read_flux"):
                    np.testing.assert_allclose(
                        row["read"][field], previous[field], rtol=0, atol=2e-12
                    )
            report["runs"][name].append(row)
            print(
                f"{k:2d} {name:5s} C={fmt(row['C_after'])} W={fmt(row['W_after'])} ||Z||={norm(row['Z_after']) if row['Z_after'] is not None else 'absent'} ||H-Href||={norm(np.array(row['read']['H']) - np.array(report['H_reference'])):.9e}",
                flush=True,
            )
    for a, b in itertools.combinations(FAMILIES, 2):
        x, y = states[a].current, states[b].current
        nx, ny = (
            report["runs"][a][-1]["continuation"],
            report["runs"][b][-1]["continuation"],
        )
        report["end_distances"].append(
            dict(
                pair=f"{a} / {b}",
                C=norm(np.array(x.C) - np.array(y.C)),
                W=None if x.W_A is None else norm(np.array(x.W_A) - np.array(y.W_A)),
                Z=None
                if x.Z_4 is None or y.Z_4 is None
                else norm(np.array(x.Z_4) - np.array(y.Z_4)),
                next_J=norm(np.array(nx["J"]) - np.array(ny["J"])),
                next_H=norm(np.array(nx["H"]) - np.array(ny["H"])),
            )
        )
    print("Final pairwise distances:", flush=True)
    print(json.dumps(report["end_distances"], indent=2), flush=True)
    return report


def main(candidate):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, help="write full JSON and Markdown evolution reports"
    )
    parser.add_argument(
        "--render-from",
        type=Path,
        help="render retained JSON without rerunning numerical steps",
    )
    args = parser.parse_args()
    report = (
        run(candidate)
        if args.render_from is None
        else json.loads(args.render_from.read_text())
    )
    if report["candidate"] != candidate:
        parser.error("retained report belongs to the other candidate")
    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        stem = args.output_dir / f"candidate_{candidate.lower()}_five"
        stem.with_suffix(".json").write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n"
        )
        stem.with_suffix(".md").write_text(markdown(report))

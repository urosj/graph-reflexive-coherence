"""Concrete 100/400 -> 107/407 declaration examples for all ten native families.

The compact records reconstruct complete authoritative histories; no family is
represented only by a future-work label. Numerical admission is a separate,
executable command and records actual outcomes without implicit retuning.
"""

from __future__ import annotations

import argparse
import json
import math
import signal
import time
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import prepare_p983_graph_admission as common

from pygrc.models import grc_9_v4_expansion as expansion
from pygrc.models import grc_9_v4_lifecycle as native
from pygrc.models.grc_9_v4_topology import (
    GRC9V4CandidateADifferentialReference,
    GRC9V4PortGraph,
)
from pygrc.models.grc_v4_ci import CIBoundedDomain, CIContractionCertificate
from pygrc.models.grc_v4_codec import canonical_json_bytes, payload_identity
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_geometry import (
    GeometryStageInputs,
    GRCV4Context,
    GRCV4Graph,
    GRCV4ReferenceGeometry,
)
from pygrc.models.grc_v4_pc import PCBaseChart, PCEnvelopeCertificate, carrier_geometry
from pygrc.models.grc_v4_profile import GRCV4Profile, resolve_profile
from pygrc.models.grc_v4_realizations import CandidateAOSPass, CandidateCOSPass
from pygrc.models.grc_v4_rg2b import RG2bCertificate
from pygrc.models.grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState

ROOT = common.ROOT
BASE = Path(common.BASE)
REQUEST = BASE / "P9-8.3-AllRealizationsRequest.json"
OUTPUT = BASE / "larger-graph-examples"
FAMILIES = common.FAMILIES
NAMES = {f: f.replace("_", "") for f in FAMILIES}


def settings(request=None):
    request = json.loads((ROOT / REQUEST).read_text()) if request is None else request
    common.require(
        set(request) == {"schema", "purpose", "selection_policy", "families"},
        "unknown request field",
    )
    common.require(
        request["schema"] == "p983-all-realizations-request-v1",
        "unknown request schema",
    )
    common.require(
        set(request["families"]) == set(FAMILIES), "all ten declarations required"
    )
    for family, selected in request["families"].items():
        keys = {"kappa_H", "candidate_overrides", "ordinary_dt"}
        if family not in {"A_PC", "C_PC"}:
            keys.add("tolerance")
        if "CI" in family:
            keys.add("geometry_radius")
        if family.endswith("PC"):
            keys.update(
                {
                    "carrier_radius",
                    "resource_radius",
                    "weight_lower",
                    "weight_upper",
                    "tau_PC",
                }
            )
        common.require(set(selected) == keys, "missing or unknown family setting")
        common.require(
            type(selected["candidate_overrides"]) is dict,
            "candidate overrides must be explicit",
        )
        common.require(
            type(selected["ordinary_dt"]) in (int, float)
            and math.isfinite(selected["ordinary_dt"])
            and selected["ordinary_dt"] > 0,
            "ordinary duration must be finite and positive",
        )
    return request


def profile_for(graph, family, selected):
    proposal = json.loads((ROOT / common.REQUEST).read_text())
    vectors = json.loads((ROOT / common.VECTORS).read_text())
    c = common.profile_for(graph, proposal, vectors)
    params, identity = c.params_resolved.to_payload(), c.identity_payload.to_payload()
    if family.startswith("A_"):
        path = ROOT / BASE / "P9-8.3A.1-AOS-Oracle.json"
        accepted = json.loads(path.read_text())["source"]["reference"]["profile"]
        params["candidate"] = deepcopy(accepted["params_resolved"]["candidate"])
        params["lifecycle"] = deepcopy(accepted["params_resolved"]["lifecycle"])
        params["candidate"]["descriptor_backend_id"] = (
            GRC9V4CandidateADifferentialReference(graph).identity
        )
        params["geometry"]["candidate_adapter_id"] = "candidate_a_exact_star_adapter_v1"
        identity.update(candidate="A", candidate_c_transport_id=None)
    candidate = identity["candidate"]
    realization = family[2:].replace("_", "+")
    params["geometry"]["kappa_H"] = selected["kappa_H"]
    params["candidate"].update(selected["candidate_overrides"])
    identity.update(
        profile_family_id=family,
        realization=realization,
        composition_gain=2 if realization == "CI+PC" else None,
    )
    if realization in {"PC", "CI+PC"}:
        params["realization"] = {
            "schema_version": "grcv4-pc-params-v1",
            "tau_PC": selected["tau_PC"],
            "radius": selected["carrier_radius"],
            "carrier_norm_id": "symmetric_star_frobenius_v1",
            "source_envelope_id": PCBaseChart(
                selected["resource_radius"],
                selected["weight_lower"],
                selected["weight_upper"],
            ).identity,
            "writer_id": "zero_order_hold_exponential_v1",
        }
    if realization in {"CI", "CI+PC"}:
        if realization == "CI":
            params["realization"] = {}
        params["realization"].update(
            schema_version="grcv4-ci-params-v1"
            if realization == "CI"
            else "grcv4-cipc-params-v1",
            contraction_domain_id=CIBoundedDomain(selected["geometry_radius"]).identity,
            root_selector_id="unique_admitted_root_v1",
            iteration_limit=60,
            residual_norm_id="joint_current_geometry_l2_v1",
            tolerance=selected["tolerance"],
        )
        if realization == "CI+PC":
            params["realization"]["rho_inst"] = 1
        params["solver"].update(solver_kind="fixed_point", iteration_limit=60)
        identity["solver_id"] = "ci_reduced_fixed_point_v1"
    elif realization == "RG2b":
        from pygrc.models import grc_9_v4_arg2b, grc_9_v4_rg2b

        implementation = grc_9_v4_arg2b if candidate == "A" else grc_9_v4_rg2b
        params["realization"] = {
            "schema_version": "grcv4-rg2b-params-v1",
            "extension_evaluator_id": implementation.EXTENSION,
            "approximation_policy_id": implementation.APPROXIMATION,
            "error_norm_id": implementation.ERROR_NORM,
            "containment_certificate_id": implementation.CONTAINMENT,
            "error_tolerance": selected["tolerance"],
            "iteration_limit": 300,
            "failure_policy_id": "fail_closed_on_uncertified_section_v1",
        }
    elif realization == "OS":
        params["realization"]["tolerance"] = selected["tolerance"]
    identity["params_hash"] = payload_identity("resolved_params", params)
    return resolve_profile(params, identity)


def recipe(family, role):
    current = role == "current"
    c = [2.0] * 100
    plus, minus, delta = (20, 70, 1 / 64) if current else (30, 80, 1 / 32)
    c[plus] += delta
    c[minus] -= delta
    return {
        "C": c,
        "W_A": [
            1 + (1 if i % 2 == 0 else -1) * (1 if current else -1) / 65536
            for i in range(400)
        ]
        if family.startswith("A_")
        else None,
        "Z_4": {
            "recipe": "alternating_diagonal_v1",
            "scale": (1 if current else -1) / 4096,
        }
        if family.endswith("PC")
        else None,
    }


def authority(data, edge_count):
    common.require(set(data) == {"C", "W_A", "Z_4"}, "unknown history field")
    z = data["Z_4"]
    if z is not None:
        common.require(
            z["recipe"] in {"alternating_diagonal_v1", "zero_v1"},
            "unknown carrier recipe",
        )
        common.require(
            set(z)
            == (
                {"recipe", "scale"}
                if z["recipe"] == "alternating_diagonal_v1"
                else {"recipe"}
            ),
            "unknown carrier field",
        )
        values = [0.0] * edge_count**2
        if z["recipe"] == "alternating_diagonal_v1":
            for i in range(edge_count):
                values[i * edge_count + i] = z["scale"] * (-1 if i % 2 else 1)
        z = tuple(values)
    return GRCV4AuthoritativeState(
        tuple(data["C"]), None if data["W_A"] is None else tuple(data["W_A"]), z
    )


def make_state(graph, profile, spec, roles, family):
    ref = GRCV4ReferenceGeometry(
        GRCV4Graph.from_port_graph(graph),
        profile,
        GRCV4Context("constant_zero_context_v1", FrozenJSONMap({})),
        tuple((0.0,) * len(graph.edges) for _ in graph.edges),
        FrozenJSONMap({e.edge_id: 1.0 for e in graph.edges}),
    )
    inputs = GeometryStageInputs(
        ref.geometry(),
        ref.context,
        roles["current"],
        roles["reset"],
        "larger-" + family,
        200.0,
        (),
        0,
        0.0,
        0.0,
        "pre_read",
        0,
        None,
    )
    if family in {"C_PC", "A_PC"}:
        inputs = replace(inputs, geometry=carrier_geometry(inputs, roles["current"]))
    return getattr(native, "GRC9V4" + NAMES[family] + "State")(inputs, spec)


def identities(state):
    return {
        "model_identity": state.model_identity,
        "scientific_digest": state.scientific_digest,
        "reset_digest": state.reset_digest,
    }


def materialize(record, side):
    """Reconstruct a native state solely from a portable example and check identity."""
    common.require(
        record["record_digest"] == common.record_digest(record),
        "example digest mismatch",
    )
    common.require(record["family"] in FAMILIES, "unknown family")
    validate_claims(record)
    data = record[side]
    graph = GRC9V4PortGraph.from_envelope(data["graph"])
    profile = GRCV4Profile.from_canonical_bytes(canonical_json_bytes(data["profile"]))
    spec = native.GRC9V4Specialization(
        FrozenJSONMap(record["specialization"]["resolved"]),
        FrozenJSONMap(record["specialization"]["identity_payload"]),
    )
    roles = {
        role: authority(data["roles"][role], len(graph.edges))
        for role in ("current", "reset")
    }
    state = make_state(graph, profile, spec, roles, record["family"])
    common.require(
        all(data[key] == value for key, value in identities(state).items()),
        "state identity mismatch",
    )
    return state


def validate_claims(record):
    """Prepared examples cannot self-promote by recomputing their digest."""
    common.require(
        record["schema"] == "p983-larger-family-example-v1", "unknown example schema"
    )
    common.require(
        record["disposition"] == "concrete_declarations_and_transfer_prepared",
        "false construction scope",
    )
    common.require(
        record["selected_configuration"] == settings()["families"][record["family"]],
        "configuration request drift",
    )
    common.require(
        record["execution"]
        == {
            "numerical_admission": "not_run",
            "physical_steps": 0,
            "events_committed": 0,
            "supported_profiles_added": [],
        },
        "preparation cannot claim execution",
    )


def build(family, shared=None):
    common.require(family in FAMILIES, "unknown family")
    shared = common.prepare() if shared is None else shared
    selected = settings()["families"][family]
    graph = common.source_graph()
    profile = profile_for(graph, family, selected)
    spec = native.GRC9V4Specialization(
        FrozenJSONMap(shared["specialization"]["resolved"]),
        FrozenJSONMap(shared["specialization"]["identity_payload"]),
    )
    recipes = {role: recipe(family, role) for role in ("current", "reset")}
    roles = {role: authority(value, 400) for role, value in recipes.items()}
    state = make_state(graph, profile, spec, roles, family)
    request = deepcopy(shared["event_request"])
    template = getattr(expansion, NAMES[family].lower() + "_profile_template")(
        state.inputs.geometry.reference
    )
    request.update(
        operation_id="larger-" + family,
        source_state_digest=state.scientific_digest,
        target_profile_template_id=template.profile_template_id,
    )
    if family.startswith("A_"):
        history = (
            expansion.apc_history_policy
            if family.endswith("PC")
            else expansion.aos_history_policy
        )
        request["history_policy"] = history(roles["current"], roles["reset"])
    elif family.endswith("PC"):
        request["history_policy"] = expansion.cpc_history_policy(
            roles["current"], roles["reset"]
        )
    request = expansion.GRC9V4ExpansionRequestInput.from_payload(request)
    plan = expansion.GRC9V4ExpansionPlan(
        graph,
        state.scientific_digest,
        request,
        expansion.GRC9ExpansionPolicy.from_payload(spec.resolved["expansion"]),
    )
    constructor = getattr(expansion, "GRC9V4" + NAMES[family] + "Expansion")
    extra = (
        (roles["current"], roles["reset"])
        if family.startswith("A_") or family.endswith("PC")
        else ()
    )
    transfer = constructor(plan, state.inputs.geometry.reference, *extra)
    targets = {role: transfer.transfer(value) for role, value in roles.items()}
    target = make_state(
        plan.target_graph, transfer.target.profile, spec, targets, family
    )
    target_recipes = {
        role: {
            "C": list(value.C),
            "W_A": None if value.W_A is None else list(value.W_A),
            "Z_4": {"recipe": "zero_v1"} if value.Z_4 is not None else None,
        }
        for role, value in targets.items()
    }
    result = {
        "schema": "p983-larger-family-example-v1",
        "family": family,
        "disposition": "concrete_declarations_and_transfer_prepared",
        "selected_configuration": selected,
        "specialization": spec.to_payload(),
        "source": {
            "graph": graph.to_envelope(),
            "profile": profile.to_payload(),
            "roles": recipes,
            **identities(state),
        },
        "target": {
            "graph": plan.target_graph.to_envelope(),
            "profile": transfer.target.profile.to_payload(),
            "roles": target_recipes,
            **identities(target),
        },
        "event_request": request.to_payload(),
        "event_id": plan.event_id,
        "graph_facts": {
            "source": common.graph_facts(graph),
            "target": common.graph_facts(plan.target_graph),
        },
        "reference_recipe": shared["reference_recipe"],
        "execution": {
            "numerical_admission": "not_run",
            "physical_steps": 0,
            "events_committed": 0,
            "supported_profiles_added": [],
        },
    }
    result["record_digest"] = common.record_digest(result)
    return result, state, target


class ProbeTimeout(TimeoutError):
    """An operational time limit, never a scientific rejection."""


def _timeout(signum, frame):
    raise ProbeTimeout("numerical probe time budget exhausted; no admission conclusion")


def numerical_owner(family):
    if family.endswith("RG2b"):
        return "RG2bCertificate"
    if "CI" in family:
        return "CIContractionCertificate"
    if family.endswith("PC"):
        return "PCEnvelopeCertificate"
    return "CandidateAOSPass" if family.startswith("A_") else "CandidateCOSPass"


def probe_report(record, source, target):
    report = {
        "schema": "p983-larger-numerical-probe-v1",
        "family": record["family"],
        "prepared_digest": record["record_digest"],
        "scope": "numerical_read_or_certificate_only; timeout_is_not_rejection",
        "physical_steps": 0,
        "events_committed": 0,
        "supported_profiles_added": [],
        "source": deepcopy(source),
        "target": deepcopy(target),
    }
    for side in ("source", "target"):
        for result in report[side].values():
            result.setdefault("owner", numerical_owner(record["family"]))
            result.setdefault("numerical_budget_seconds", None)
            result.setdefault("read_dt", 0)
    report["record_digest"] = common.record_digest(report)
    return report


def admit(state, max_seconds=None):
    """Actual numerical owner, separately for each role; no success fabricated."""
    family = state.FAMILY
    read_dt = (
        settings()["families"][family]["ordinary_dt"] if family.endswith("OS") else 0
    )
    backend = (
        GRC9V4CandidateADifferentialReference(
            state.inputs.geometry.reference.graph.port_graph
        )
        if family.startswith("A_")
        else None
    )
    results = {}
    for role in ("current", "reset"):
        values = getattr(state.inputs, role)
        inputs = replace(state.inputs, current=values, reset=values)
        if family in {"C_PC", "A_PC"}:
            inputs = replace(inputs, geometry=carrier_geometry(inputs, values))
        start = time.perf_counter()
        previous_handler = None
        if max_seconds is not None:
            previous_handler = signal.signal(signal.SIGALRM, _timeout)
            signal.setitimer(signal.ITIMER_REAL, max_seconds)
        try:
            if family.endswith("RG2b"):
                checked = RG2bCertificate(inputs, backend)
            elif "CI" in family:
                checked = CIContractionCertificate(inputs, backend)
            elif family.endswith("PC"):
                checked = PCEnvelopeCertificate(inputs, backend)
            elif family.startswith("A_"):
                checked = CandidateAOSPass(replace(inputs, dt=read_dt), backend)
            else:
                checked = CandidateCOSPass(replace(inputs, dt=read_dt))
            results[role] = {
                "status": "passed",
                "owner": type(checked).__name__,
                "bounds": checked.bounds.to_dict()
                if hasattr(checked, "bounds")
                else None,
            }
        except ValueError as exc:
            results[role] = {
                "status": "rejected",
                "error_type": type(exc).__name__,
                "reason": str(exc),
            }
        except ProbeTimeout as exc:
            results[role] = {"status": "incomplete", "reason": str(exc)}
        finally:
            if max_seconds is not None:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous_handler)
        results[role]["numerical_budget_seconds"] = max_seconds
        results[role]["read_dt"] = read_dt
        results[role]["seconds"] = time.perf_counter() - start
        print(f"{family} {role}: {results[role]['status']}", flush=True)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=FAMILIES)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--admit", action="store_true")
    parser.add_argument(
        "--numerical-budget",
        type=float,
        default=60,
        help="Seconds per numerical probe; setup is separate (0 means unlimited).",
    )
    args = parser.parse_args()
    common.require(
        math.isfinite(args.numerical_budget) and args.numerical_budget >= 0,
        "invalid numerical budget",
    )
    shared = None if args.admit and not args.write else common.prepare()
    for family in (args.family,) if args.family else FAMILIES:
        with exact_backend(ExactBackend.FLINT):
            path = ROOT / OUTPUT / (family + ".json")
            if args.admit and not args.write:
                record = json.loads(path.read_text())
                source, target = (
                    materialize(record, side) for side in ("source", "target")
                )
            else:
                record, source, target = build(family, shared)
            if args.admit:
                print(
                    f"{family}: native inputs reconstructed; numerical probes starting",
                    flush=True,
                )
                report = probe_report(
                    record,
                    admit(source, args.numerical_budget or None),
                    admit(target, args.numerical_budget or None),
                )
                (ROOT / OUTPUT).mkdir(exist_ok=True)
                (ROOT / OUTPUT / (family + "-Admission.json")).write_text(
                    json.dumps(report, indent=2) + "\n"
                )
            path = ROOT / OUTPUT / (family + ".json")
            if args.write:
                path.parent.mkdir(exist_ok=True)
                path.write_text(json.dumps(record, indent=2) + "\n")
            else:
                common.require(
                    canonical_json_bytes(json.loads(path.read_text()))
                    == canonical_json_bytes(record),
                    "example drift",
                )
        print(
            f"{family}: concrete source/target contracts and transfers prepared",
            flush=True,
        )


if __name__ == "__main__":
    main()

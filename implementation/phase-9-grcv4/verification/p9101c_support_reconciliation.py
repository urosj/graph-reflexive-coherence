"""Reconcile accepted exact subjects; no native execution or support promotion."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import rfc8785

import p996_acceptance as historical_acceptance
import p9101a_acceptance as basin_acceptance
import p9101b_acceptance as target_acceptance
import p9101c_target_basin as exact_basin

execution = target_acceptance.execution
ROOT, BASE, FAMILIES = execution.ROOT, execution.BASE, execution.FAMILIES
PATH = BASE + "P9-10.1c-SupportReconciliation.json"
REVIEW = BASE + "P9-10.1c-Review.md"
SELF = "implementation/phase-9-grcv4/verification/p9101c_support_reconciliation.py"
sha = execution.sha


def seal(value):
    """Shared browser/Python numeric canonicalization for inherited limits."""
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=sha(rfc8785.dumps(body)))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ref(root, name, pointer=None):
    require(
        not Path(name).is_absolute() and ".." not in Path(name).parts,
        "nonportable evidence path",
    )
    from p9_aos_historical import reference
    value = reference(root, name)
    if pointer is not None:
        value["json_pointer"] = pointer
    return value


def inputs(root):
    root = Path(root).resolve()
    # The accepted historical review is immutable. The a/b validators bind the
    # current numerical sources; do not recursively replay the old campaigns.
    old = historical_acceptance.decision(root)
    historical = json.loads((root / old["evidence"]["path"]).read_bytes())
    a, b = basin_acceptance.status(root), target_acceptance.status(root)
    return dict(
        historical=historical,
        historical_acceptance=old,
        basin=a,
        targets=b,
        basin_records={
            f: basin_acceptance.execution.load(root, f)[0] for f in FAMILIES
        },
        target_records={f: execution.load(root, f)[0] for f in FAMILIES},
        exact_target_basin={f: exact_basin.check(root, f) for f in FAMILIES},
    )


def subject(state):
    from pygrc.models.grc_v4_profile import resolve_profile
    from pygrc.models.grc_9_v4_lifecycle import GRC9V4Specialization
    from pygrc.models.grc_9_v4_identity import model_identity
    from pygrc.models.grc_v4_state import FrozenJSONMap

    reference = state["inputs"]["reference"]
    declared = reference["profile"]
    profile = resolve_profile(declared["params_resolved"], declared["identity_payload"])
    require(
        profile.complete_profile_id == declared["complete_profile_id"],
        "profile identity drift",
    )
    s = state["specialization"]
    specialization = GRC9V4Specialization(
        FrozenJSONMap(s["resolved"]), FrozenJSONMap(s["identity_payload"])
    )
    model = model_identity(profile.complete_profile_id, specialization)
    require(model == state["model_identity"], "combined model identity drift")
    graph = reference["graph"]
    return dict(
        complete_profile_id=profile.complete_profile_id,
        specialization_id=specialization.specialization_id,
        model_identity=model,
        graph_content_sha256=sha(
            json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()
        ),
        graph_vertices=len(graph["live_node_ids"]),
        graph_edges=len(graph["edges"]),
    ), specialization


def basin_subject(state, extension):
    from pygrc.models.grc_v4_geometry import GRCV4Graph
    from pygrc.models.grc_9_v4_basin import validate_observation, POLICY_ID
    from pygrc.models.grc_9_v4_identity import has_basin

    identity, specialization = subject(state)
    require(
        has_basin(specialization), "basin evidence requires explicit v2 declaration"
    )
    require(
        extension["policy_id"] == POLICY_ID
        and extension["replay_mode"] == "exact_observation",
        "missing exact basin observations",
    )
    graph = GRCV4Graph.from_payload(state["inputs"]["reference"]["graph"])
    roles = []
    for role in ("current", "reset"):
        value = extension[role + "_observation"]
        validate_observation(value, graph.port_graph)
        binding = value["binding"]
        state_digest = state[
            "scientific_digest" if role == "current" else "reset_digest"
        ]
        require(
            binding["role"] == role
            and binding["role_state_digest"] == state_digest.split(":")[-1]
            and binding["model_identity"] == identity["model_identity"]
            and binding["profile_id"] == identity["complete_profile_id"],
            "basin role/state/model mismatch",
        )
        roles.append(
            dict(
                role=role,
                observation_digest=value["observation_digest"],
                role_state_digest=binding["role_state_digest"],
                read_identity=binding["read_identity"],
                root_certificate_binding=binding["root_certificate_binding"],
            )
        )
    return dict(subject=identity, observations=roles, policy_id=POLICY_ID)


def assemble(root, data):
    from pygrc.models.grc_9_v4_identity import model_identity

    root = Path(root).resolve()
    prior, a, b = data["historical"], data["basin"], data["targets"]
    require(
        data["historical_acceptance"]["record_digest"] == historical_acceptance.DIGEST
        and data["historical_acceptance"]["user_accepted"] is True,
        "unaccepted historical support review",
    )
    for value, closed in ((a, "P9_10_1a_closed"), (b, "P9_10_1b_closed")):
        require(
            value["user_accepted"] is True
            and value[closed] is True
            and value["families"] == list(FAMILIES)
            and value["full_GRC9V4_conformance"] is False,
            "unaccepted or widened successor scope",
        )
    require(
        a["acceptance"]["record_digest"] == basin_acceptance.ACCEPTANCE
        and b["acceptance"]["record_digest"] == target_acceptance.ACCEPTANCE,
        "successor decision mismatch",
    )
    require(
        prior["matrix_counts"]
        == dict(
            total=40,
            bounded_accepted=16,
            unselected_not_executed=24,
            failed=0,
            unaccounted=0,
        ),
        "target cells must not fill other-family source cells",
    )
    require(
        prior["optional_completion"]
        == dict(selected=False, executed=False, blocking_selected_scope=False),
        "optional scope widening",
    )
    require(
        len(prior["authority"]) == 16
        and all(
            r["support_disposition"] == "indeterminate_requires_review"
            for r in prior["authority"]
        ),
        "historical forensic authority promoted",
    )
    require(
        [r["id"] for r in prior["open_items"]]
        == ["basin_surface", "umbrella_compatibility", "target_identity_scope"],
        "historical holds changed",
    )
    rows = []
    for family in FAMILIES:
        old = next(r for r in prior["rows"] if r["family"] == family)
        ar, br = data["basin_records"][family], data["target_records"][family]
        require(
            ar["group"] == family and br["family"] == family,
            "missing or substituted family record",
        )
        aref = next(
            r
            for r in a["records"]
            if r["family"] == family and "Pressure-" in r["path"]
        )
        bref = next(r for r in b["records"] if r["family"] == family)
        require(
            ar["record_digest"] == aref["record_digest"]
            and br["record_digest"] == bref["record_digest"],
            "successor execution reference mismatch",
        )
        observations = ar["evidence"]["observations"]
        selected = {}
        for label in ("initial", "after_supported_expansion"):
            matches = [
                (i, o) for i, o in enumerate(observations) if o["label"] == label
            ]
            require(len(matches) == 1, "ambiguous basin observation subject")
            i, observation = matches[0]
            selected[label] = dict(
                **basin_subject(
                    observation["saved_native_state"], observation["observations"]
                ),
                evidence_kind="accepted_native_capture_with_independent_saved_state_equations",
                source_ref=dict(aref, json_pointer=f"/evidence/observations/{i}"),
            )
        source = selected["initial"]["subject"]
        require(
            source["complete_profile_id"] == old["source"]["complete_profile_id"]
            and source["graph_content_sha256"] == old["source"]["graph_content_sha256"]
            and source["model_identity"] != old["source"]["model_identity"],
            "source v2 identity confused with historical v1",
        )
        versions = []
        v1_specialization = None
        for version in ("v1", "v2"):
            record = br["evidence"][version]
            owner = record["final_checkpoint"]["owner"]
            identity, specialization = subject(owner["state"])
            require(
                identity == record["subject"]
                and record["source_subject"] == old["enabled_expansion_target"],
                "expanded target aliased to another subject",
            )
            require(
                record["outcome"] == "successful_target_compatibility"
                and record["surfaces"] == dict.fromkeys(execution.SURFACES, "passed")
                and record["enabled_continuation"]["committed"] is True
                and record["disabled_replay"]
                and record["enabled_replay"],
                "refusal substituted for successful compatibility",
            )
            if version == "v1":
                require(
                    identity == old["enabled_expansion_target"]
                    and "basin" not in owner,
                    "v1 target silently upgraded",
                )
                v1_specialization = specialization
                basin = dict(status="historical_v1_without_basin_policy")
            else:
                expected = v1_specialization.with_basin_policy()
                require(
                    specialization == expected
                    and identity["model_identity"]
                    == model_identity(
                        old["enabled_expansion_target"]["complete_profile_id"], expected
                    ),
                    "unrelated v2 target substituted",
                )
                basin = dict(
                    **basin_subject(owner["state"], owner["basin"]),
                    status="accepted_native_capture_and_replay_for_this_exact_target",
                    independent_equation_pressure_transferred=False,
                )
                direct, direct_ref = data["exact_target_basin"][family]
                exact_basin.validate(direct, record)
                require(
                    direct["family"] == family
                    and direct["record_digest"] == direct_ref["record_digest"]
                    and direct["predecessor"]["record_digest"] == br["record_digest"],
                    "exact-target basin evidence attribution drift",
                )
                basin["direct_independent_check"] = dict(
                    status="passed_on_this_exact_v2_target_pending_P9_10_1c_acceptance",
                    user_accepted=False,
                    source_ref=direct_ref,
                    native_role_captures=direct["native_role_captures"],
                    exact_root_signs_claimed=False,
                    boundaries=[
                        dict(
                            label=case["label"],
                            fixture_identity=case["fixture_identity"],
                            **basin_subject(
                                case["saved_native_state"], case["observations"]
                            ),
                            oracle_assumptions=case["oracle_assumptions"],
                            realization_checks=case["realization_checks"],
                            role_equations=case["role_equations"],
                        )
                        for case in direct["observations"]
                    ],
                    return_carrier=direct["return_carrier"],
                    distinct_return_resources=direct["distinct_return_resources"],
                    distinct_return_W_A=direct["distinct_return_W_A"],
                )
            versions.append(
                dict(
                    version=version,
                    subject=identity,
                    surfaces=record["surfaces"],
                    outcome=record["outcome"],
                    basin=basin,
                    source_ref=dict(bref, json_pointer=f"/evidence/{version}"),
                )
            )
        require(
            selected["after_supported_expansion"]["subject"]["model_identity"]
            != versions[1]["subject"]["model_identity"],
            "distinct basin-pressure target evidence must not be flattened",
        )
        rows.append(
            dict(
                family=family,
                historical_source_v1=old["source"],
                source_basin_v2=selected["initial"],
                basin_pressure_expansion_v2=selected["after_supported_expansion"],
                expanded_target_compatibility=versions,
                complete_profile_is_not_family_wide_support=True,
                inherited_limits={
                    k: deepcopy(old[k])
                    for k in (
                        "numerical_domain",
                        "numerical_scope",
                        "excluded_crossing",
                        "profile_migration_scope",
                        "mechanism_review",
                        "legacy_refusal_code",
                    )
                },
            )
        )
    names = {
        SELF,
        historical_acceptance.PATH,
        historical_acceptance.c.PATH,
        basin_acceptance.PATH,
        target_acceptance.PATH,
        "implementation/phase-9-grcv4/verification/p996_acceptance.py",
        "implementation/phase-9-grcv4/verification/p9101a_acceptance.py",
        "implementation/phase-9-grcv4/verification/p9101b_acceptance.py",
    }
    for view in (a, b):
        names.update(r["path"] for r in (*view["records"], *view["source_refs"]))
    for direct, direct_ref in data["exact_target_basin"].values():
        names.add(direct_ref["path"])
        names.update(r["path"] for r in direct["source_refs"])
    return seal(
        dict(
            schema="p9101c-support-reconciliation-v1",
            iteration="P9-10.1c",
            state="reconciled_pending_user_acceptance",
            user_accepted=False,
            P9_10_1c_closed=False,
            P9_10_1_closed=False,
            aggregate_closed=False,
            families=list(FAMILIES),
            population=prior["population"],
            unselected_families=prior["unselected_families"],
            prerequisites=dict(
                historical_support=historical_acceptance.DIGEST,
                basin_acceptance=a["acceptance"],
                target_acceptance=b["acceptance"],
            ),
            rows=rows,
            historical_open_items=prior["open_items"],
            resolved_holds=[
                dict(
                    id="basin_surface",
                    disposition="resolved_bounded_explicit_v2_successors",
                    evidence=a["acceptance"],
                    scope="Accepted baseline diagnostic and both-role lifecycle; v1 unchanged; no physical basin lineage or attractor claim.",
                ),
                dict(
                    id="target_identity_scope",
                    disposition="resolved_for_exact_tested_v1_and_v2_targets",
                    evidence=b["acceptance"],
                    scope="Successful four-surface compatibility on exact expanded targets; no transfer to arbitrary targets or parameterizations.",
                ),
            ],
            open_items=[
                dict(
                    **{
                        k: deepcopy(v)
                        for k, v in prior["open_items"][1].items()
                        if k != "owner"
                    },
                    historical_owner="P9-10.1",
                    owner="future execution/contract scope decision; P9-10.4 publication and P9-G4 full-label boundary",
                    blocking_bounded_four_family_closure=False,
                    blocking_umbrella_capability_and_full_conformance=True,
                )
            ],
            source_matrix_counts=prior["matrix_counts"],
            additional_target_cells=dict(
                v1=16, explicit_v2=16, credited_to_other_source_families=0
            ),
            authority=prior["authority"],
            optional_completion=prior["optional_completion"],
            new_scientific_claims=[],
            new_G2_G3_support=[],
            G4_accepted=False,
            full_GRC9V4_conformance=False,
            compatibility_capability_advertised=False,
            native_execution=False,
            exact_target_basin_checks=dict(
                families=4,
                boundaries=8,
                role_captures=16,
                new_expansion_events=0,
                new_enabled_steps=0,
                user_accepted=False,
                scope="Direct independent checks on the four exact 10.1b v2 targets at migration and disabled return. Earlier evidence retained separately; no transferred numerical attribution.",
            ),
            new_native_steps=0,
            new_native_events=0,
            check_level="retained_identity_and_classification_reconciliation_not_native_rerun",
            numerical_limits="Preserve inherited CI resolution and pointwise A_PC margins; fixed-H basin equation bounds do not certify the unknown exact CI-root signs. No trajectory or parameter-tube upgrade.",
            next_work="Review bounded P9-10.1c and any requested corrections before closing P9-10.1. P9-10.2–10.6 and G4 remain separate; the all-forty restriction remains.",
            source_refs=[ref(root, n) for n in sorted(names)],
        )
    )


def build(root=ROOT):
    return assemble(root, inputs(root))


def check(root=ROOT, value=None):
    root = Path(root).resolve()
    if value is None:
        value = json.loads((root / PATH).read_bytes())
    require(
        value == seal(value) and value == build(root),
        "support reconciliation differs from accepted subjects or scope",
    )
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build() if args.prepare else check()
    if args.prepare:
        with (ROOT / PATH).open("x") as out:
            out.write(json.dumps(value, indent=2) + "\n")
    print(
        json.dumps(
            dict(
                record_digest=value["record_digest"],
                state=value["state"],
                resolved_holds=[h["id"] for h in value["resolved_holds"]],
                open_items=[h["id"] for h in value["open_items"]],
            ),
            indent=2,
        )
    )

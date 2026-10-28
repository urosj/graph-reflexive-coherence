"""P9-9.6: reconcile exact accepted subjects; no trajectories or support promotion."""

import argparse
from dataclasses import fields
import json
from pathlib import Path
import re
import sys

import p991b_acceptance as a1
import p991b_lifecycle as c1
import p992_acceptance as a2
import p992_compatibility as c2
import p993_acceptance as a3
import p993_matrix as c3
import p994a_acceptance as a4
import p994a_crossings as c4
import p994b_acceptance as a4b
import p994b_public_api as c4b
import p995_acceptance as a5
import p995_public_conflict as c5
import p986_acceptance as a8
import p986_first_group as c8
import phase9_specialization_acceptance as g3

ROOT = Path(__file__).resolve().parents[3]
BASE = c5.BASE
PATH = BASE + "P9-9.6-SupportReview.json"
REVIEW = BASE + "P9-9.6-Review.md"
SELF = "implementation/phase-9-grcv4/verification/p996_support_review.py"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool"
SPEC = "specs/grc-9-v4-spec.md"
FAMILIES = c5.FAMILIES
POPULATION = tuple(c4b.CONTRACT_FAMILIES)
MANDATORY = {
    "port_graph",
    "mechanical_refinement",
    "column_coarse_graining",
    "basin_attributes",
    "quadrature_budget",
    "intrinsic_frame",
}
OPTIONAL = {"completed_spark", "hierarchy_tracking"}
CAPABILITY = "grc9v3_disabled_compatibility"
sha, seal = c5.sha, c5.seal


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(root, name):
    return json.loads((root / name).read_bytes())


def reference(root, name, pointer=None):
    p = (root / name).resolve()
    require(
        not Path(name).is_absolute() and p.is_relative_to(root),
        "nonportable review source",
    )
    result = dict(path=name, sha256=sha(p.read_bytes()))
    if pointer is not None:
        result["json_pointer"] = pointer
    return result


def inputs(root):
    """Authenticate each accepted stage once. All calls are retained checks."""
    sys.path.insert(0, str(root / SIDE / "tool/src"))
    from grcv4_explorer.tranche8_end import tranche8_end_reviews

    accepted = {
        "9.1b": a1.decision(root),
        "9.2": a2.decision(root),
        "9.3": a3.decision(root),
        "9.4a": a4.decision(root),
        "9.4b": a4b.decision(root),
        "9.5": a5.decision(root),
    }
    records = {
        "9.1b": {f: c1.check(root, f) for f in FAMILIES},
        "9.2": {f: c2.check(root, f) for f in c2.RECORDS},
        "9.4a": {f: c4.check(root, f) for f in FAMILIES},
        "9.4b": {f: c4b.check(root, f) for f in c4b.CLASSES},
        "9.5": {f: c5.check(root, f) for f in FAMILIES},
    }
    matrix = c3.check(root)
    require(
        matrix["record_digest"] == accepted["9.3"]["matrix"]["record_digest"],
        "unaccepted matrix",
    )
    generic = g3.accepted(root)
    return dict(
        accepted=accepted,
        records=records,
        matrix=matrix,
        generic=generic,
        generic_review=read(root, generic["review"]["path"]),
        numerical=a8.status(root),
        end=tranche8_end_reviews(root),
    )


def subject(state):
    """Read exact identities without constructing a numerical owner."""
    from pygrc.models.grc_v4_profile import resolve_profile
    from pygrc.models.grc_v4_codec import payload_identity
    from pygrc.models.grc_9_v4_lifecycle import GRC9V4Specialization
    from pygrc.models.grc_v4_state import FrozenJSONMap

    ref = state["inputs"]["reference"]
    declared = ref["profile"]
    profile = resolve_profile(declared["params_resolved"], declared["identity_payload"])
    require(
        profile.complete_profile_id == declared["complete_profile_id"],
        "profile identity drift",
    )
    s = state["specialization"]
    specialization = GRC9V4Specialization(
        FrozenJSONMap(s["resolved"]), FrozenJSONMap(s["identity_payload"])
    )
    model = payload_identity(
        "complete_model_identity_payload",
        dict(
            schema_version="grc9v4-complete-identity-v1",
            grcv4_complete_profile_id=profile.complete_profile_id,
            specialization_id=specialization.specialization_id,
        ),
    )
    require(model == state["model_identity"], "combined model identity drift")
    require(
        s["resolved"]["spark"]["child_stabilization"] is None,
        "unreviewed completion request",
    )
    return dict(
        complete_profile_id=profile.complete_profile_id,
        model_identity=model,
        specialization_id=specialization.specialization_id,
        graph_content_sha256=sha(
            json.dumps(ref["graph"], sort_keys=True, separators=(",", ":")).encode()
        ),
        graph_vertices=len(ref["graph"]["live_node_ids"]),
        graph_edges=len(ref["graph"]["edges"]),
    )


def assemble(root, data):
    """Derive the support boundary from checked evidence, not a family-name union."""
    accepted, records = data["accepted"], data["records"]
    require(
        set(accepted) == {"9.1b", "9.2", "9.3", "9.4a", "9.4b", "9.5"},
        "missing accepted stage",
    )
    require(
        all(v["user_accepted"] is True for v in accepted.values()),
        "unaccepted prerequisite",
    )
    for stage, groups in records.items():
        require(
            set(groups)
            == set(
                c2.RECORDS
                if stage == "9.2"
                else c4b.CLASSES
                if stage == "9.4b"
                else FAMILIES
            ),
            "missing execution group",
        )
        for family, record in groups.items():
            require(
                record["record_digest"]
                == accepted[stage]["executions"][family]["record_digest"],
                "execution/acceptance mismatch",
            )
    matrix = data["matrix"]
    require(
        matrix["counts"]
        == dict(
            total=40,
            bounded_accepted=16,
            unselected_not_executed=24,
            failed=0,
            unaccounted=0,
        ),
        "compatibility scope widening",
    )
    require(
        data["numerical"]["user_accepted"]
        and data["end"]["first_group_closed"]
        and not data["numerical"]["aggregate_closed"],
        "unaccepted numerical scope",
    )
    spec = (root / SPEC).read_text()
    section = spec.split("## Capabilities\n", 1)[1].split(
        "## Specialization identity", 1
    )[0]
    must = set(re.findall(r"^- `([^`]+)`", section, re.M))
    require(
        must == MANDATORY
        and "all 40 profile-by-surface delegate\nvectors pass" in section,
        "frozen capability contract changed",
    )
    from pygrc.models.grc_9_v4_contracts import EnabledGRC9V4State

    state_fields = sorted(f.name for f in fields(EnabledGRC9V4State))
    rows = []
    for family in FAMILIES:
        lifecycle = records["9.1b"][family]["evidence"]["mixed_snapshot"]
        source, target = subject(lifecycle["initial"]), subject(lifecycle["state"])
        public = records["9.4b"][family]["evidence"]
        require(
            public["construction"]["active_model_identity"] == source["model_identity"],
            "public source alias",
        )
        public_target = public["expansion_replay"]["final_checkpoint"]["owner"]["state"]
        require(subject(public_target) == target, "public target alias")
        cells = [r for r in matrix["cells"] if r["family"] == family]
        require(
            len(cells) == 4 and {r["surface"] for r in cells} == set(c2.SURFACES),
            "incomplete family compatibility",
        )
        require(
            all(
                r["complete_profile_id"] == source["complete_profile_id"]
                and r["model_identity"] == source["model_identity"]
                and r["disposition"] == "bounded_accepted"
                for r in cells
            ),
            "component/source identity mismatch",
        )
        caps = public["construction"]["capabilities"]
        require(
            not (set(caps) & (OPTIONAL | {CAPABILITY})),
            "unreviewed capability promotion",
        )
        crossing = records["9.4a"][family]["evidence"]
        entry = crossing["roundtrip"]["disabled_checkpoint"]["state"]["binding"]
        require(
            entry["active_model_identity"] == source["model_identity"],
            "crossing/source identity mismatch",
        )
        nomination = next(
            r
            for r in data["generic_review"]["profiles"]
            if r["profile_family_id"] == family
        )
        scientific = next(
            r
            for r in data["numerical"]["decision"]["families"]
            if r["family"] == family
        )
        refs = {stage: dict(accepted[stage]["executions"][family]) for stage in records}
        failure = records["9.5"][family]["evidence"]["rejection"]["failure"]
        require(
            failure["code"] == "legacy_expansion_target_undefined",
            "legacy refusal missing",
        )
        rows.append(
            dict(
                family=family,
                disposition="bounded_partial_support_evidence_reconciled",
                generic_G2_profile_id=nomination["nomination"]["complete_profile_id"],
                source=source,
                enabled_expansion_target=target,
                evidence=refs,
                disabled_cells=cells,
                disabled_scope="exact_source_model_defined_legacy_domain",
                expanded_target_disabled_surfaces="not_executed_for_this_exact_target_identity",
                public_capabilities=caps,
                missing_mandatory_capabilities=sorted(MANDATORY - set(caps)),
                readable_state_missing_basin_identity="basin_identity"
                not in state_fields,
                legacy_refusal_code=failure["code"],
                crossing_domain="same_graph_explicit_typed_migration_no_automatic_fallback",
                excluded_crossing=crossing["excluded_domain"],
                profile_migration_scope={
                    k: v
                    for k, v in public["profile_migration"].items()
                    if k != "final_checkpoint"
                },
                numerical_domain=scientific["exact_domain"],
                numerical_scope=scientific["scientific_scope"],
                mechanism_review=dict(
                    path="implementation/phase-9-grcv4/tranche-8/P9-Tranche8-FirstGroupMechanisms.json",
                    json_pointer="/" + family,
                    record_digest=data["end"]["records"]["mechanisms"]["record_digest"],
                ),
                complete_profile_is_not_family_wide_support=True,
            )
        )
    require(
        all(
            r["missing_mandatory_capabilities"] == ["basin_attributes"]
            and r["readable_state_missing_basin_identity"]
            for r in rows
        ),
        "basin surface finding changed; re-review",
    )
    legacy = data["generic_review"]["legacy_bindings"]
    for ref in legacy:
        require(
            sha((root / ref["path"]).read_bytes()) == ref["sha256"],
            "legacy source changed",
        )
    authority = read(root, BASE + "P9-9.2-Authority.json")
    traces = authority["traces"]
    authority_rows = [
        dict(
            contract_id=key,
            trace_digest=v["trace_digest"],
            support_disposition=v["rows"][0]["payload"]["support_disposition"],
        )
        for key, v in sorted(traces.items())
    ]
    names = {
        SELF,
        SPEC,
        "specs/grc-v4-conformance-fixtures.json",
        "src/pygrc/models/grc_9_v4.py",
        "src/pygrc/models/grc_9_v4_contracts.py",
        "src/pygrc/models/grc_9_v4_api_lifecycle.py",
        g3.RECORD,
        data["generic"]["review"]["path"],
        a8.ACCEPTANCE,
        c8.RESULT,
        "implementation/phase-9-grcv4/tranche-8/P9-Tranche8-FirstGroupAcceptance.json",
        "implementation/phase-9-grcv4/tranche-8/P9-Tranche8-FirstGroupMechanisms.json",
        "implementation/phase-9-grcv4/tranche-8/P9-Tranche8-FirstGroupEndResults.md",
        a1.PATH,
        a2.PATH,
        a3.PATH,
        a4.PATH,
        a4b.PATH,
        a5.PATH,
        c3.PATH,
        BASE + "P9-9.2-Authority.json",
        c5.AUTHORITY,
    }
    for value in accepted.values():
        for ref in value.get("executions", {}).values():
            names.add(ref["path"])
        if "review" in value:
            names.add(value["review"]["path"])
    names.update(c8.path(f) for f in FAMILIES)
    return seal(
        dict(
            schema="p996-bounded-support-review-v1",
            iteration="P9-9.6",
            verdict="bounded_evidence_reconciled_full_conformance_held",
            families=list(FAMILIES),
            population=list(POPULATION),
            unselected_families=[f for f in POPULATION if f not in FAMILIES],
            rows=rows,
            matrix_counts=matrix["counts"],
            mandatory_capabilities=sorted(MANDATORY),
            optional_completion=dict(
                selected=False, executed=False, blocking_selected_scope=False
            ),
            public_api_available=True,
            user_accepted=False,
            aggregate_closed=False,
            full_GRC9V4_conformance=False,
            compatibility_capability_advertised=False,
            native_execution=False,
            new_scientific_claims=[],
            new_G2_G3_support=[],
            G4_accepted=False,
            inherited_test_methods=sum(
                r["tests_run"] for groups in records.values() for r in groups.values()
            ),
            new_native_steps=0,
            new_native_events=0,
            legacy_source_unchanged=True,
            legacy_regressions_rerun=False,
            frozen_release_changed=False,
            authority=authority_rows,
            open_items=[
                dict(
                    id="basin_surface",
                    kind="mandatory_interface_gap",
                    owner="P9-10.1",
                    detail="Baseline seed predicate exists, but public basin_attributes and basin_identity are absent. Define/expose/test the required baseline basin surface before a full-conformance claim; this is separate from optional completion/hierarchy.",
                ),
                dict(
                    id="umbrella_compatibility",
                    kind="frozen_capability_scope_limit",
                    owner="P9-10.1",
                    detail="The frozen capability requires all forty delegate vectors. Six-family/twenty-four-cell work remains unselected; sixteen passing cells do not authorize that capability or a full label. Do not silently reinterpret the spec.",
                ),
                dict(
                    id="target_identity_scope",
                    kind="evidence_limit",
                    owner="P9-10.1",
                    detail="Expanded target profiles have different complete/model identities. Their enabled public evolution is tested; do not transfer source-only disabled-cell acceptance to those identities or arbitrary registered declarations.",
                ),
            ],
            next_work="Review this bounded disposition, then resolve/route named holds in P9-10.1 before support publication and P9-G4.",
            source_refs=[reference(root, n) for n in sorted(names)],
        )
    )


def build(root):
    root = Path(root).resolve()
    return assemble(root, inputs(root))


def check(root, value=None):
    root = Path(root).resolve()
    if value is None:
        value = read(root, PATH)
    require(
        value == seal(value) and value == build(root),
        "support review differs from accepted subjects or scope",
    )
    return value


def status(root):
    root = Path(root).resolve()
    v = check(root)
    return dict(
        schema="p996-support-status-v1",
        iteration="P9-9.6",
        verdict=v["verdict"],
        families=v["families"],
        unselected_families=v["unselected_families"],
        state="review_complete_pending_acceptance",
        user_accepted=False,
        aggregate_closed=False,
        full_GRC9V4_conformance=False,
        compatibility_capability_advertised=False,
        G4_accepted=False,
        check_level="retained_reconciliation_only_no_native_rerun",
        record_digest=v["record_digest"],
        rows=v["rows"],
        matrix_counts=v["matrix_counts"],
        open_items=v["open_items"],
        optional_completion=v["optional_completion"],
        next_work=v["next_work"],
        source_refs=[reference(root, n) for n in (PATH, REVIEW)],
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    a = p.parse_args()
    if a.write:
        v = build(ROOT)
        raw = (json.dumps(v, indent=2) + "\n").encode()
        require(
            len(raw) <= 1_000_000,
            "review exceeds compact evidence threshold; use compressed representation",
        )
        with (ROOT / PATH).open("xb") as f:
            f.write(raw)
    else:
        v = check(ROOT)
    print(
        json.dumps(
            {
                k: v[k]
                for k in ("verdict", "families", "record_digest", "new_native_steps")
            }
        )
    )


if __name__ == "__main__":
    main()

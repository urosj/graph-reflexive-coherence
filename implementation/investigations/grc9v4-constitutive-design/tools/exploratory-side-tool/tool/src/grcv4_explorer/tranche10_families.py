"""Per-family basin rollout; retained checks only, with exact review identities."""
from pathlib import Path
import sys

REVIEWS = {"A_OS": "485e499f5500670944de798c873b8cab322932984d4e0c52df5f195acf4e6db9",
           "C_PC": "f9937fa25a07eac6e61e06b5c0153232e6b5d6ce2603d58d801780b03e4950b7",
           "C_CI_PC": "de9b3b958432c063db1af9159e60a7f11efe779ead4a3d5a7f7aa8cdbaa34ebb",
           "A_CI_PC": "5273b53bcff71482518ba71cc0fc58809e39667a6e1b19a23860289cf799e34c",
           "C_RG2b": "2a933e93a9edbeddf9e1808154e97f7513a936018d2effc7c361652d788f68d7"}


def checker(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root / "implementation/phase-9-grcv4/verification"))
    import p910_family_basin
    return root, p910_family_basin


def checked(root, family):
    if family not in REVIEWS:
        raise KeyError("family has no selected Tranche 10 extension")
    root, c = checker(root)
    value = c.check(family)
    if value["record_digest"] != REVIEWS[family]:
        raise ValueError("family basin review subject changed")
    return root, c, value


def family_basin_status(root, family="A_OS"):
    root, c, value = checked(root, family)
    import p910_family_acceptance as acceptance
    accepted = acceptance.decision(root, value)
    _, stored = c.load(family, root=root)
    view = dict(schema="p910-family-basin-view-v1", family=family,
        status=value["status"], user_accepted=False, P9_10_1_closed=False, P9_10_2_closed=False,
        G4_accepted=False, full_GRC9V4_conformance=False, new_support=[],
        first_group_accepted=["C_OS", "C_CI", "A_CI", "A_PC"],
        remaining_families=value["remaining_families"], verification_record_digest=value["record_digest"],
        native_tests=value["native_tests"], exact_targets={k: value["target_compatibility"][k]["subject"] for k in ("v1", "v2")},
        boundaries=[dict(label=case["label"], role_equations=({role: {k: v for k, v in eq.items() if k != "section_record"}
                                        for role, eq in case["role_equations"].items()}
                                       if family == "C_RG2b" else case["role_equations"]),
                         realization_checks=case["realization_checks"],
                         observation_digests={role: case["observations"][role+"_observation"]["observation_digest"]
                                              for role in ("current", "reset")})
                    for case in value["direct_target"]["observations"]],
        verification=value["verification"], evidence=[stored, *value["parts"]],
        source_refs=value["source_refs"],
        limits=["represented_flow_not_attractor", "exact_subjects_not_family_wide_conformance",
                "fixed_geometry_bounds_not_uniform_trajectory_or_exact_CI_root", "no_G4_or_new_support"],
        next_work=value["next_work"])
    if family == "C_RG2b":
        view["limits"] = ["represented_flow_not_attractor", "exact_subjects_not_family_wide_conformance",
                          "fixed_H_current_error_separate_from_Lipschitz_section_error",
                          "C1_unresolved_no_universal_exact_section_signs", "no_G4_or_new_support"]
    if accepted is not None:
        ref = dict(**c.v.reference(root, acceptance.path(family)), record_digest=accepted["record_digest"])
        view.update(status=accepted["status"], user_accepted=True,
                    P9_10_1_closed=True, P9_10_2_closed=True,
                    all_ten_P9_10_1_closed=False, all_ten_P9_10_2_closed=False,
                    acceptance=ref, next_work=accepted["next_work"],
                    evidence=[*view["evidence"], ref])
    return c.seal(view)


def family_basin_source(root, name, family="A_OS"):
    root, c, value = checked(root, family)
    _, stored = c.load(family, root=root)
    refs = {r["path"]: r for r in [*value["source_refs"], *value["prerequisites"], *value["parts"], stored]}
    import p910_family_acceptance as acceptance
    accepted = acceptance.decision(root, value)
    if accepted is not None:
        ref = c.v.reference(root, acceptance.path(family))
        refs[ref["path"]] = ref
        refs.update((ref["path"], ref) for ref in accepted["review_sources"])
    path = Path(name)
    if name not in refs or path.is_absolute() or ".." in path.parts or not (root/path).resolve().is_relative_to(root):
        raise KeyError("not an indexed family basin source")
    raw = (root / name).read_bytes()
    if c.v.sha(raw) != refs[name]["sha256"]:
        return c.successor.read_source(root, refs[name])
    return raw, refs[name]

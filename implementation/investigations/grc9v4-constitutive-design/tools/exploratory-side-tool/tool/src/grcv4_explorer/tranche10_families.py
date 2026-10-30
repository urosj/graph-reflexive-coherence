"""Per-family basin rollout; retained checks only, with exact review identities."""
from pathlib import Path
import sys

REVIEWS = {"A_OS": "485e499f5500670944de798c873b8cab322932984d4e0c52df5f195acf4e6db9"}


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
    _, stored = c.load(family, root=root)
    return c.seal(dict(schema="p910-family-basin-view-v1", family=family,
        status=value["status"], user_accepted=False, P9_10_1_closed=False, P9_10_2_closed=False,
        G4_accepted=False, full_GRC9V4_conformance=False, new_support=[],
        first_group_accepted=["C_OS", "C_CI", "A_CI", "A_PC"],
        remaining_families=value["remaining_families"], verification_record_digest=value["record_digest"],
        native_tests=value["native_tests"], exact_targets={k: value["target_compatibility"][k]["subject"] for k in ("v1", "v2")},
        boundaries=[dict(label=case["label"], role_equations=case["role_equations"],
                         realization_checks=case["realization_checks"],
                         observation_digests={role: case["observations"][role+"_observation"]["observation_digest"]
                                              for role in ("current", "reset")})
                    for case in value["direct_target"]["observations"]],
        verification=value["verification"], evidence=[stored, *value["parts"]],
        source_refs=value["source_refs"],
        limits=["represented_flow_not_attractor", "exact_subjects_not_family_wide_conformance",
                "fixed_geometry_bounds_not_uniform_trajectory_or_exact_CI_root", "no_G4_or_new_support"],
        next_work=value["next_work"]))


def family_basin_source(root, name, family="A_OS"):
    root, c, value = checked(root, family)
    _, stored = c.load(family, root=root)
    refs = {r["path"]: r for r in [*value["source_refs"], *value["prerequisites"], *value["parts"], stored]}
    path = Path(name)
    if name not in refs or path.is_absolute() or ".." in path.parts or not (root/path).resolve().is_relative_to(root):
        raise KeyError("not an indexed family basin source")
    raw = (root / name).read_bytes()
    if c.v.sha(raw) != refs[name]["sha256"]:
        raise ValueError("family basin source changed")
    return raw, refs[name]

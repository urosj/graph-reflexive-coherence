"""Pinned per-family user decisions over unchanged Tranche 10 execution."""
import json
from pathlib import Path

import p910_family_basin as execution

ACCEPTANCES = {"A_OS": "6ea2d269b653c50dc4a5b046ec6088ca1cd88637fc91818b715e3bb62047c9a4",
               "C_PC": "28517601d0e71be406ac8d3a54c3de5888210e9ab9e2322106d196d51f20ff6d",
               "C_CI_PC": "2023cfb84100a383851cc76cd19f1738042d536ea4008a4c5916daf8a89615f4",
               "A_CI_PC": "0f590b46e43f84fdac4995483418d50e0c5537ef56221d845a51a5a75c18aaf7",
               "C_RG2b": "ceaa967a90c13ef566ec719f693593619fa474cae726b57e2746561e1057b37f",
               "A_RG2b": "33ec5d2090ea958dce57e2581c1f0e6267f90ece5244c22dd82edc816ef6f5ac"}


def path(family):
    if family not in ACCEPTANCES:
        raise KeyError("no selected family acceptance")
    return execution.BASE + "P9-10-" + family.replace("_", "") + "-Acceptance.json"


def decision(root, evidence):
    root = Path(root).resolve()
    family = evidence["family"]
    if family not in ACCEPTANCES:
        return None
    value = json.loads((root / path(family)).read_bytes())
    _, stored = execution.load(family, root=root)
    execution.require(evidence == execution.seal(evidence)
        and value == execution.seal(value) and value["record_digest"] == ACCEPTANCES[family]
        and value["schema"] == "p910-family-basin-acceptance-v1" and value["family"] == family
        and value["status"] == "accepted_bounded_family_basin"
        and value["verification_record_digest"] == evidence["record_digest"]
        and value["evidence"] == [stored, *evidence["parts"]]
        and value["checkpoints"] == ["10.1a", "10.1b", "10.1c", "10.2"]
        and all(value[k] is True for k in ("user_accepted", "P9_10_1_closed", "P9_10_2_closed"))
        and all(value[k] is False for k in ("all_ten_P9_10_1_closed", "all_ten_P9_10_2_closed",
                                           "full_GRC9V4_conformance", "G4_accepted"))
        and value["new_support"] == [] and value["remaining_families"] == evidence["remaining_families"],
        "family acceptance identity or scope changed")
    for ref in [*value["evidence"], *value["review_sources"]]:
        execution.require(execution.v.reference(root, ref["path"])["sha256"] == ref["sha256"],
                          "accepted family evidence/review changed")
    return value

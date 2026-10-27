"""Reconcile frozen disabled contracts with accepted components; no native run."""

import argparse
import json
from pathlib import Path
import re

import p992_acceptance as acceptance
import p992_compatibility as c

ROOT = Path(__file__).resolve().parents[3]
PATH = c.BASE + "P9-9.3-Matrix.json"
REVIEW = c.BASE + "P9-9.3-Review.md"
CATALOG = "specs/grc-v4-conformance-fixtures.json"
SPEC = "specs/grc-9-v4-spec.md"
CHECKER = "implementation/phase-9-grcv4/verification/p993_matrix.py"
POPULATION = {
    a + "_" + r for a in ("A", "C") for r in ("CI", "OS", "RG2b", "PC", "CI_PC")
}


def catalog(root):
    value = json.loads((root / CATALOG).read_bytes())["disabled_compatibility"]
    rows = value["matrix"]
    if (
        value["independent_case_count"] != 40
        or value["surfaces"] != list(c.SURFACES)
        or value["target"] != "exact_embedded_grc9v3_delegate"
        or value["legacy_target_modified"]
        or len(rows) != 10
        or {r["profile"] for r in rows} != POPULATION
    ):
        raise ValueError("invalid frozen compatibility population")
    contracts = []
    for row in rows:
        if set(row) != {"profile", *c.SURFACES}:
            raise ValueError("missing or extra compatibility surface")
        for surface in c.SURFACES:
            expected = f"D10.2-EC-DISABLED-{row['profile']}-{surface.upper()}"
            if row[surface] != expected:
                raise ValueError("contract/profile/surface alias")
            contracts.append(expected)
    section = (
        (root / SPEC)
        .read_text()
        .split("## Exact disabled GRC9V3 compatibility\n", 1)[1]
        .split("\n## ", 1)[0]
    )
    spec_ids = re.findall(
        r"D10\.2-EC-DISABLED-[AC]_[A-Za-z0-9_]+-(?:TRANSITION|STATE|OBSERVABLE|LIFECYCLE)",
        section,
    )
    if (
        len(contracts) != 40
        or len(set(contracts)) != 40
        or sorted(spec_ids) != sorted(contracts)
    ):
        raise ValueError("specification/catalog matrix disagreement")
    return rows


def build(root):
    root = Path(root).resolve()
    accepted = acceptance.decision(root)
    records = {f: c.check(root, f) for f in c.RECORDS}
    rows = []
    for declared in catalog(root):
        family = declared["profile"]
        for surface in c.SURFACES:
            selected = family in c.FAMILIES
            iteration = f"P9-9.2-{family}-{surface}"
            vector = f"DISABLED-{family}-{surface.upper()}"
            cell = dict(
                family=family,
                surface=surface,
                iteration_id=iteration,
                contract_id=declared[surface],
                vector_id=vector,
                disposition="bounded_accepted"
                if selected
                else "unselected_not_executed",
                complete_profile_id=None,
                model_identity=None,
                target_spec_version=None,
                execution=None,
                acceptance=None,
                reason="accepted_defined_domain_delegate_component"
                if selected
                else "outside_selected_four_family_scope",
            )
            if selected:
                executed = records[family]["cells"][surface]
                subject = accepted["executions"][family]
                binding = {
                    k: executed[k]
                    for k in (
                        "contract_id",
                        "complete_profile_id",
                        "model_identity",
                        "target_spec_version",
                    )
                }
                if (
                    executed["iteration_id"] != iteration
                    or executed["profile_family"] != family
                    or executed["vector_id"] != vector
                    or executed["contract_id"] != declared[surface]
                    or accepted["accepted_cells"][iteration] != binding
                    or records[family]["record_digest"] != subject["record_digest"]
                ):
                    raise ValueError("accepted cell identity mismatch")
                cell.update(
                    binding,
                    execution=dict(subject, json_pointer="/cells/" + surface),
                    acceptance=dict(
                        path=acceptance.PATH,
                        record_digest=accepted["record_digest"],
                        cell_id=iteration,
                    ),
                )
            rows.append(cell)
    if {
        r["iteration_id"] for r in rows if r["disposition"] == "bounded_accepted"
    } != set(accepted["accepted_cells"]):
        raise ValueError("unreconciled accepted cell")
    names = [
        CATALOG,
        SPEC,
        CHECKER,
        acceptance.PATH,
        *[v["path"] for v in accepted["executions"].values()],
        accepted["review"]["path"],
        accepted["authority"]["path"],
    ]
    return c.seal(
        dict(
            schema="p993-disabled-matrix-reconciliation-v1",
            iteration="P9-9.3",
            outcome="passed",
            selected_families=list(c.FAMILIES),
            population_families=sorted(POPULATION),
            counts=dict(
                total=40,
                bounded_accepted=16,
                unselected_not_executed=24,
                failed=0,
                unaccounted=0,
            ),
            cells=rows,
            user_accepted=False,
            native_execution=False,
            aggregate_closed=False,
            full_GRC9V4_conformance=False,
            public_API_implemented=False,
            crossings_executed=False,
            new_runtime_support=[],
            new_scientific_claims=[],
            remaining_work=["P9-9.4a", "P9-9.4b", "P9-9.5", "P9-9.6"],
            source_refs=[
                dict(path=n, sha256=c.sha((root / n).read_bytes())) for n in names
            ],
        )
    )


def check(root, value=None):
    root = Path(root).resolve()
    if value is None:
        value = json.loads((root / PATH).read_bytes())
    if value != c.seal(value) or value != build(root):
        raise ValueError(
            "matrix does not match frozen contracts and accepted execution evidence"
        )
    return value


def status(root):
    root = Path(root).resolve()
    matrix = check(root)
    view = acceptance.status(root)
    projected = {(r["family"], r["surface"], r["state"]) for r in view["cells"]}
    expected = {
        (
            r["family"],
            r["surface"],
            "bounded_accepted"
            if r["disposition"] == "bounded_accepted"
            else "unselected",
        )
        for r in matrix["cells"]
    }
    if len(view["cells"]) != 40 or projected != expected:
        raise ValueError("published compatibility matrix drift")
    view["matrix_reconciliation"] = dict(
        iteration="P9-9.3",
        outcome=matrix["outcome"],
        record_digest=matrix["record_digest"],
        user_accepted=False,
        native_execution=False,
    )
    view["source_refs"].extend(
        dict(path=n, sha256=c.sha((root / n).read_bytes())) for n in (PATH, REVIEW)
    )
    return view


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        value = build(ROOT)
        with (ROOT / PATH).open("x") as handle:
            json.dump(value, handle, indent=2)
            handle.write("\n")
    else:
        value = check(ROOT)
    print(
        json.dumps(
            dict(
                outcome=value["outcome"],
                counts=value["counts"],
                native_execution=False,
                record_digest=value["record_digest"],
            )
        )
    )


if __name__ == "__main__":
    main()

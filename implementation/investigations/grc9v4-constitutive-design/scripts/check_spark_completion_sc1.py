"""SC-1 conditional mathematics and exact synthetic pressure, no native runs."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = "implementation/investigations/grc9v4-constitutive-design/"
SIDE = INV + "tools/exploratory-side-tool"
OUTPUT = INV + "evidence/spark-completion/SC1Checks.json"
sys.path.insert(0, str(ROOT / SIDE / "tool/src"))
from grcv4_explorer.basin import load_basin_forensic_context
from grcv4_explorer.forensic import contract_provenance

def load_reference(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / INV / "research" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reference = load_reference("sc1_window", "spark_completion_window.py")
basins = load_reference("sc1_basins", "spark_completion_basins.py")
pressure = load_reference("sc1_pressure", "spark_completion_pressure.py")


def contraction_checks():
    # An affine full-state toy in the infinity norm. It is not a V4 model.
    radius, q, error = F(1,4), F(1,2), F(1,32)
    image_radius = q*radius
    assert image_radius + error < radius
    distance = radius
    for n in range(1,9):
        distance=q*distance+error
        assert distance == q**n*radius + error*(1-q**n)/(1-q)
    # Stable eigenvalues alone do not certify this box/infinity norm.
    nonnormal = ((F(1,2),F(1)), (F(0),F(1,2)))
    row_bound=max(sum(abs(x) for x in row) for row in nonnormal)
    assert row_bound == F(3,2) and row_bound*radius > radius
    # Numerical recurrence control does not imply domain invariance by itself.
    excessive_error = F(3,16)
    assert image_radius+excessive_error > radius
    return dict(
        scope="exact affine countermodels, not a GRCV4 operator certificate",
        q=str(q), domain_radius=str(radius), full_step_error=str(error),
        strict_image_slack=str(radius-image_radius-error),
        eight_step_error_bound=str(distance), asymptotic_error_floor=str(error/(1-q)),
        nonnormal_spectral_radius=str(F(1,2)), nonnormal_infinity_bound=str(row_bound),
        nonnormal_box_not_invariant=True, excessive_rounding_rejected=True)


def build():
    context=load_basin_forensic_context(ROOT,ROOT/SIDE)
    ids=("D10.2-EC-PARENT-CORE-INCIDENCE-CONTINUITY",
         "D10.2-EC-PARENT-L-AUTHORITATIVE-CURRENT",
         "D10.2-EC-PARENT-L-POSTCONTINUITY-REFRESH",
         "P9-EC-GRC9-BASIN-CEILING", "P9-EC-GRC9-BASIN-IDENTITY",
         "D10.2-EC-PARENT-GRC9-CHILD-BASIN-STABILIZATION",
         "D10.2-EC-PARENT-BASE-GRC9-ROW-BASIS-DIFFERENTIAL",
         "P9-EC-GRC9-BASIN-SEEDS",
         "D11-C-EC-C-HM-STIFFNESS", "D11-C-EC-C-DIRECT-POTENTIAL-DECOMPOSITION",
         "D11-C-EC-C-J0-CURRENT", "D10.2-EC-PARENT-BASE-POTENTIAL",
         "D10.2-EC-PARENT-A-READ-CLOSURE", "D10.2-EC-PARENT-A-RETAINED-WRITER",
         "D10.2-EC-CI-A-ROOT", "D10.2-EC-PC-ZOH-WRITER")
    traces={name:contract_provenance(context,name) for name in ids}
    sources=(INV+"research/spark_completion_window.py",
             INV+"research/spark_completion_basins.py",
             INV+"research/spark_completion_pressure.py",
             INV+"scripts/check_spark_completion_sc1.py",
             INV+"decisions/SparkCompletionSC1Contract.md",
             INV+"decisions/SparkCompletionSC1EquilibriumExclusion.md",
             INV+"evidence/spark-completion/review/SC1ScientificPressureReview.md",
             INV+"evidence/spark-completion/review/SC1ScientificPressureSubmitted.json",
             INV+"evidence/spark-completion/SC1ClaimDebtLedger.json",
             INV+"evidence/spark-completion/InitialFeasibility.json",
             "specs/grc-v4-spec.md", "specs/grc-9-v4-spec.md", "specs/grc-9-v4-basin-interface.md",
             "specs/grc-v4-contract-schema.json",
             INV+"drafts/2026-09-GRC-V4.md", "papers/2026-02-GRC-V3.md")
    sources += tuple("implementation/phase-9-grcv4/tranche-10/P9-10.1a-Pressure-"+f+".json.xz"
                     for f in ("C_OS","C_CI","A_CI","A_PC"))
    geometric, contraction = basins.checks(), contraction_checks()
    independent = pressure.checks(ROOT, basins, contraction, geometric)
    return dict(schema="grc9v4-spark-sc1-research-checks-v1",
        status="conditional_mathematics_reviewed_precision_fixed_bounded_exclusion_recorded", predecessor_commit="0d27440b",
        proposed_policy_id="grc9v4-certified-geometric-child-basins-v1",
        SC1_definition_supplied=True, SC1_accepted=False, new_policy_admitted=False,
        source_use={"papers/2026-02-GRC-V3.md":"direction for spatial basin meaning; physical-flux routing not inherited"},
        sources=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in sources],
        forensic_traces=traces, geometric_basins=geometric,
        finite_reference=reference.checks(), contraction_controls=contraction,
        independent_pressure=independent,
        seed_meaning="exact_row_scientific_anchor_with_certified_represented_agreement",
        numerical_lift="fixed_exact_charge_slice_requires_proved_constraint_preservation",
        bounded_exclusion="No SC-1 persistent-anchor contracting domain under the inspected closed zero-site tree bindings; A extends to positive-denominator connected graphs under the stated premises",
        finite_reference_role="independent observational controls, not geometric-completion prerequisites",
        native_steps=0, native_events=0, constitutive_trajectory_proved=False,
        actual_V4_contraction_proved=False, exact_CI_root_claim=False,
        actual_V4_stable_child_basin_domain_proved=False, completed_spark=False,
        accepted_authority=False, debts_closed=[],
        next="Identify an admitted mechanism for nonconstant admissible equilibria before any SC-2 witness search; do not rerun the excluded bindings")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args=parser.parse_args();value=build();path=ROOT/OUTPUT
    if args.write:
        with path.open("x") as stream:
            stream.write(json.dumps(value,indent=2,ensure_ascii=False)+"\n")
    elif json.loads(path.read_bytes())!=value:
        raise ValueError("SC-1 retained evidence or bound source changed")
    print("PASS: 15 geometric groups, 25 window groups; independent 5,422-case pressure and 112 retained declarations; numerical regression controls; 16 forensic traces. No native trajectory or completion claim.")


if __name__=="__main__":
    main()

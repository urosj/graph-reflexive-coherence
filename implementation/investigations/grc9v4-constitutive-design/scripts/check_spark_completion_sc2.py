"""SC-2 mechanism equations and provenance; no native trajectory or evaluator."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
INV="implementation/investigations/grc9v4-constitutive-design/"
SIDE=INV+"tools/exploratory-side-tool"
OUTPUT=INV+"evidence/spark-completion/SC2MechanismChecks.json"
sys.path.insert(0,str(ROOT/SIDE/"tool/src"))
from grcv4_explorer.basin import load_basin_forensic_context
from grcv4_explorer.forensic import contract_provenance

def build():
    path=ROOT/INV/"research/spark_completion_mechanism.py"
    spec=importlib.util.spec_from_file_location("sc2_mechanism",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    context=load_basin_forensic_context(ROOT,ROOT/SIDE)
    ids=("D10.2-EC-PARENT-BASE-POTENTIAL","D10.2-EC-PARENT-CORE-INCIDENCE-CONTINUITY",
         "D10.2-EC-GEOM-PROFILE","D10.2-EC-GEOM-HODGE-UPDATE",
         "D10.2-EC-PC-ZOH-WRITER","D10.2-EC-C-READBACK",
         "D10.2-EC-PARENT-REAL-OS","D11-C-EC-C-J0-CURRENT",
         "D11-C-EC-C-DIRECT-POTENTIAL-DECOMPOSITION","D11-C-EC-C-J0-SWITCH-SEPARATION")
    traces={name:contract_provenance(context,name) for name in ids}
    sources=(
        INV+"research/spark_completion_mechanism.py",INV+"scripts/check_spark_completion_sc2.py",
        INV+"decisions/SparkCompletionSC2MechanismAnalysis.md",
        INV+"evidence/spark-completion/SC2ClaimDebtLedger.json",
        INV+"evidence/spark-completion/review/SC2ScientificPressureReview.md",
        INV+"evidence/spark-completion/SC1Checks.json",
        "specs/grc-v4-spec.md","specs/grc-9-v4-spec.md",
        INV+"drafts/2026-09-GRC-V4.md","papers/2025-12-GRC-V2.md",
        "src/pygrc/models/grc_v4_geometry.py","src/pygrc/models/grc_v4_candidate_a.py",
        "src/pygrc/models/grc_v4_candidate_c.py","src/pygrc/models/grc_v4_step.py")
    return dict(
        schema="grc9v4-spark-sc2-mechanism-checks-v1",
        status="scientifically_reviewed_conditional_mechanism_not_admitted",
        sources=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in sources],
        forensic_traces=traces,mechanism=module.checks(),
        source_use={"papers/2025-12-GRC-V2.md":"direction for double-well choice only; V4 signs and stability rederived"},
        proposed_binding="SC2-homogeneous-quartic-site-proposal",
        accepted_equation_channel_not_concrete_evaluator=True,
        native_site_evaluators="zero_derivative_only_in_inspected_A_and_C_current_implementations",
        permanent_K4_base_not_additive_forcing=True,
        SC2_closed=False,accepted_authority=False,debts_closed=[])

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write",action="store_true");group.add_argument("--check",action="store_true")
    args=parser.parse_args();value=build();path=ROOT/OUTPUT
    if args.write:
        with path.open("x") as stream:stream.write(json.dumps(value,indent=2,ensure_ascii=False)+"\n")
    elif value!=json.loads(path.read_bytes()):
        raise ValueError("SC-2 source or retained exact check changed")
    print("PASS: exact equilibrium/stability bounds, read/source, 120 branch boxes and negative controls; 10 forensic traces. No native completion.")
if __name__=="__main__":
    main()

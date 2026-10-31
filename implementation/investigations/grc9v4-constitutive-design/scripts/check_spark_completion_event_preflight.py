"""Exact source/parent/D11/charge preflight; no native event or trajectory."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
SIDE=INV+'tools/exploratory-side-tool'
OUTPUT=INV+'evidence/spark-completion/SC2EventPreflight.json'
sys.path[:0]=[str(ROOT/'src'),str(ROOT/INV/'research'),str(ROOT/SIDE/'tool/src')]
from spark_completion_event_preflight import checks
from grcv4_explorer.basin import load_basin_forensic_context
from grcv4_explorer.forensic import contract_provenance


def build():
    context=load_basin_forensic_context(ROOT,ROOT/SIDE)
    ids=('D10.2-EC-PARENT-GRC9-HYBRID-SPARK',
         'D10.2-EC-PARENT-BASE-GRC9-ROW-BASIS-DIFFERENTIAL',
         'D11-G9-EC-SATURATED-SOURCE-PORT-BIJECTION',
         'D11-G9-EC-N-CAPACITY-FLOOR','D11-G9-EC-EXACT-OLD-PORT-MAP',
         'D11-G9-EC-PRIMARY-LATIN-TRANSVERSAL','D11-G9-EC-RESOURCE-DISTRIBUTION',
         'D11-G9-EC-FIXED-BOND-SEED','D11-G9-EC-LIFECYCLE-READMISSION')
    traces={key:contract_provenance(context,key) for key in ids}
    paths=(INV+'research/spark_completion_event_preflight.py',
           INV+'scripts/check_spark_completion_event_preflight.py',
           INV+'decisions/SparkCompletionSC2EventCompatibility.md',
           INV+'evidence/spark-completion/SC1Adjudication.json',
           INV+'evidence/spark-completion/SC2MechanismChecks.json',
           INV+'research/spark_completion_mechanism.py',
           INV+'research/spark_completion_basins.py',
           'specs/grc-9-v4-spec.md','specs/grc-v4-spec.md',
           'src/pygrc/models/grc_9_v4_expansion.py',
           'src/pygrc/models/grc_9_v4_topology.py')
    return dict(schema='grc9v4-spark-sc2-event-preflight-v1',
                status='proposed_conditional_compatibility_not_event_feasibility',
                sources=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths],
                forensic_traces=traces,preflight=checks(),
                claim_debt_progress=dict(
                    local_claims=[dict(id='SC2-CL-C-EVENT-PREFLIGHT',status='proposed_conditional',
                        statement='A concrete saturated source with a qualified parent and two independent exact resource roles has a literal D11 four-node target and compatible charge under unchanged global wells; no constitutive admission or event execution is proved.'),
                        dict(id='SC2-CL-C-TARGET-STATIONARY',status='proposed_conditional',
                        statement='The actual allocated fourteen-node topology supports an exact charge-20 locally attracting C_OS equilibrium under the proposed site law, with at least two eligible new geometric basins. Entry and a uniform complete descent roster remain unproved.')],
                    organization='SC1 definition remains selected; actual diagnostic parent/footprint and potential target children checked; event realization still open',
                    stability='target-specific local exact bounds supplied; quantified trapping/complete basin roster/numerical lift remain open',
                    nonempty_domain='positive structural and charge preflight; admitted actual event and organized-branch entry remain open',
                    temporal_lifecycle='independent exact resource roles only; native admission/window/replay not executed',
                    nonlinear_site_binding='open_not_admitted'),
                SC1_closed=True,SC2_closed=False,accepted_authority=False,
                native_steps=0,native_events=0,completed_spark=False,debts_closed=[],G4_accepted=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write',action='store_true');group.add_argument('--check',action='store_true')
    args=parser.parse_args();value=build();path=ROOT/OUTPUT
    if args.write:
        with path.open('x') as stream:stream.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    elif json.loads(path.read_bytes())!=value:
        raise ValueError('SC-2 preflight source or exact evidence changed')
    print('PASS: two source roles, both literal D11 chiral targets, exact charge and target-specific bounds; 9 forensic traces. No admitted event or native evolution.')

"""Recompute the bounded SC-2 exact-equation continuation and its controls."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import flint

ROOT=Path(__file__).resolve().parents[4]
INV='implementation/investigations/grc9v4-constitutive-design/'
OUTPUT=INV+'evidence/spark-completion/SC2Continuation.json'
PREDECESSOR=INV+'evidence/spark-completion/SC2EventPreflight.json'
sys.path.insert(0,str(ROOT/INV/'research'))
from spark_completion_continuation import checks


def build():
    paths=(PREDECESSOR,INV+'research/spark_completion_os_reference.py',
           INV+'research/spark_completion_continuation.py',INV+'research/spark_completion_basins.py',
           INV+'scripts/check_spark_completion_continuation.py',
           INV+'decisions/SparkCompletionSC2Continuation.md',
           INV+'evidence/spark-completion/SC1Adjudication.json',
           'src/pygrc/models/grc_v4_candidate_c.py','src/pygrc/models/grc_v4_geometry.py',
           'src/pygrc/models/grc_v4_realizations.py','src/pygrc/models/grc_v4_step.py',
           'specs/grc-v4-spec.md','specs/grc-9-v4-spec.md')
    predecessor=json.loads((ROOT/PREDECESSOR).read_bytes())
    # Validate the consumed preflight's own bindings; typed authority wrappers
    # remain in that record, without reclassifying their dispositions here.
    for source in predecessor['sources']:
        if hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest()!=source['sha256']:
            raise ValueError('preflight source changed: '+source['path'])
    return dict(schema='grc9v4-spark-sc2-continuation-v1',
        status='research_finite_continuation_pass_organized_entry_not_obtained',
        arithmetic=dict(python_flint=flint.__version__,target='exact_real_equations',
                        native_rounding_conformance=False,automatic_fallback=False),
        sources=[dict(path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in paths],
        checks=checks(predecessor['preflight']),
        claim_debt_progress=dict(local_claims=[
            dict(id='SC2-CL-N-STRICT-SPLIT',status='proposed_bounded_negative',
                 statement='Original four source/target reads fail the newly declared exact 1e-11 split control; this does not exclude all tolerances or change the conditional equilibrium proof.'),
            dict(id='SC2-CL-C-FINITE-CONTINUATION',status='proposed_conditional',
                 statement='The explicit mobility/duration companion has 128 rigorously enclosed positive exact-equation steps per transferred role, with split admission and certified classifications on both chiral charts; no organizing gain is observed.'),
            dict(id='SC2-CL-N-ALTERNATE-BRANCH',status='proposed_bounded_negative',
                 statement='Both endpoint enclosures lie in an alternative well box with no qualified geometric basins throughout the box. No physical trapping or infinite-time exclusion is proved.')],
            organization='SC1 definition selected; no completed child gain in the finite run',
            stability='organized equilibrium remains conditional; no quantitative physical trap supplied',
            nonempty_domain='finite exact-equation continuation demonstrated; completed-spark source/event/entry remains open',
            numerical_lift='Arb encloses exact recurrences only; native rounded charge/diagnostic agreement remains open',
            nonlinear_site_binding='proposed_not_admitted'),
        SC1_closed=True,SC2_closed=False,accepted_authority=False,native_steps=0,
        native_events=0,completed_spark=False,debts_closed=[],G4_accepted=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true');mode.add_argument('--check',action='store_true')
    args=parser.parse_args();value=build();path=ROOT/OUTPUT
    if args.write:
        with path.open('x') as stream:stream.write(json.dumps(value,indent=2)+'\n')
    elif json.loads(path.read_bytes())!=value:
        raise ValueError('SC-2 continuation source or recomputed evidence changed')
    print('PASS: exact rational controls; 2 x 128 enclosed companion steps; both chiral classifiers. No organized entry, native event or completion.')

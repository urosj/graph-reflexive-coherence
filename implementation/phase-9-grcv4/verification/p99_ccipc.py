"""Seventh-realization lifecycle, compatibility and public execution evidence."""

import argparse
from copy import deepcopy
import json
import lzma
from pathlib import Path
import time
import unittest

import p984d_ccipc as storage
from p992_compatibility import seal as evidence_seal
import p984b_runtime as base_runtime
check_bindings = base_runtime.check_bindings
import p9_ccipc_integration_compute as compute

b = storage.b
SELF = b.HERE + "p99_ccipc.py"
BASE = "implementation/phase-9-grcv4/tranche-9/"
GROUPS = {"9.1b":"CCIPCLifecycle", "9.2":"CCIPCCompatibility", "9.4a":"CCIPCCrossing",
          "9.4b":"CCIPCPublic", "9.5":"CCIPCConflict"}
COUNTS = {"9.1b":6,"9.2":4,"9.4a":4,"9.4b":5,"9.5":3}


def filename(checkpoint):
    b.require(checkpoint in GROUPS,"unknown C_CI_PC integration checkpoint")
    return BASE + "P9-" + checkpoint + "-CCIPC.json.xz"


def run(checkpoint):
    from tests.models import test_grc_9_v4_ccipc_integration as test
    path=filename(checkpoint)
    b.require(not (b.ROOT/path).exists(),"refuse overwrite")
    cls=getattr(test,GROUPS[checkpoint])
    preflight=storage.read(compute.PREFLIGHT)
    b.check_digest(preflight);b.check_bindings(preflight['source_bindings'])
    b.require(preflight['outcome']=='passed' and preflight['native_checkpoint_byte_parity'], 'integration compute preflight')
    collectors={"9.1b":test.lifecycle.OBSERVATIONS,"9.2":test.legacy.EVIDENCE,
                "9.4a":test.crossing.EVIDENCE,"9.4b":test.public.EVIDENCE,"9.5":test.conflict.EVIDENCE}
    collectors[checkpoint].clear()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(cls)
    roster=[x.id() for x in suite]
    sources=set((b.ROOT/"src").rglob("*.py")) | {Path(__file__).resolve(),Path(test.__file__).resolve()}
    sources|={Path(m.__file__).resolve() for m in (test.source,test.lifecycle,test.legacy,test.crossing,test.public,test.conflict)}
    sources|=set((b.ROOT/"src/pygrc/models/grc_v4_assets").glob("*.json"))
    paths={p.relative_to(b.ROOT).as_posix() for p in sources}
    paths|={"specs/grc-9-v4-spec.md",storage.r.INPUTS,"tests/models/test_grc_9_v4_lifecycle.py"}
    paths|={compute.SELF,compute.PREFLIGHT,b.HERE+'p984h_validation_reuse.py',
            b.HERE+'p9_cpc_covariance_compute.py',b.HERE+'p9_cpc_wire_reuse.py',b.HERE+'p984h_cpc.py'}
    refs=b.bind(paths)
    start=time.monotonic()
    with compute.worker() as policy:
        result=unittest.TextTestRunner(verbosity=2).run(suite)
    b.require(result.wasSuccessful() and not result.skipped and result.testsRun==COUNTS[checkpoint],"incomplete C_CI_PC integration tests")
    b.check_bindings(refs)
    evidence=deepcopy(collectors[checkpoint])
    if checkpoint=="9.1b":evidence=evidence["C_CI_PC"]
    # Legacy comparison evidence includes legitimate IEEE negative zeros.
    # Use the established compatibility evidence encoding, preserving them.
    value=evidence_seal(dict(schema="p99-ccipc-execution-v1",family="C_CI_PC",checkpoint=checkpoint,
        outcome="passed",tests=roster,tests_run=result.testsRun,failures=0,errors=0,skips=0,
        elapsed_seconds=time.monotonic()-start,source_bindings=refs,evidence=evidence,compute_policy=policy,
        exact_backend="flint",numerical_policy="legacy_exact_v1",native_runtime_executed=True,
        user_accepted=False,aggregate_closed=False,full_GRC9V4_conformance=False,
        optional_completion="unselected",tranche8_large_prerequisites="separate_required_evidence"))
    check(checkpoint,value)
    with (b.ROOT/path).open("xb") as stream:stream.write(lzma.compress(json.dumps(value,separators=(",",":"),allow_nan=False).encode()+b"\n"))
    return dict(checkpoint=checkpoint,tests=result.testsRun,outcome="passed_pending_acceptance")


def check(checkpoint,value=None):
    value=storage.read(filename(checkpoint)) if value is None else value
    b.require(value==evidence_seal(value),"C_CI_PC execution digest drift")
    check_bindings(value["source_bindings"])
    b.require(value["schema"]=="p99-ccipc-execution-v1" and value["family"]=="C_CI_PC"
        and value["checkpoint"]==checkpoint and value["outcome"]=="passed"
        and value["tests_run"]==COUNTS[checkpoint] and len(value["tests"])==COUNTS[checkpoint]
        and len(set(value["tests"]))==COUNTS[checkpoint] and value["evidence"]
        and all(x.startswith("tests.models.test_grc_9_v4_ccipc_integration."+GROUPS[checkpoint]+".test_") for x in value["tests"])
        and all(value[k]==0 for k in ("failures","errors","skips"))
        and all(value[k] is False for k in ("user_accepted","aggregate_closed","full_GRC9V4_conformance"))
        and value["native_runtime_executed"] is True and value["exact_backend"]=="flint",
        "C_CI_PC integration evidence scope/coverage drift")
    if checkpoint=="9.1b":
        e=value['evidence']
        b.require(e['successful_groups']==7 and e['event_commits']==1 and e['positive_target_steps']==2
            and all(e[k] for k in ('source_beat_then_bound_event','both_roles_distinct','full_reset_restored','exact_replay')),
            'incomplete mandatory lifecycle execution')
    if checkpoint=="9.2":
        b.require(set(value["evidence"])=={"transition","state","observable","lifecycle"},"four compatibility surfaces")
        for surface,row in value["evidence"].items():
            b.require(row["profile_family"]=="C_CI_PC" and row["outcome"]=="passed" and
                row["contract_id"]=="D10.2-EC-DISABLED-C_CI_PC-"+surface.upper(),"wrong compatibility subject")
    if checkpoint=='9.4a':
        e=value['evidence']
        b.require(set(e)=={'excluded_domain','rollback','replay_pressure','roundtrip'}
            and e['roundtrip']['independent_initializer'] is False
            and all(e['roundtrip'][k] for k in ('exact_native_step_and_snapshot',
                'current_reset_independently_admitted','enabled_positive_step')),'crossing coverage')
    if checkpoint=='9.4b':
        e=value['evidence'];migration=e['profile_migration'];scope=e['scope']
        b.require(set(e)=={'profile_migration','scope','branch_crossings','construction','expansion_replay'}
            and migration['target_family']=='C_OS' and all(migration[k] for k in
                ('committed','complete_profile_changed','both_resource_histories_preserved','carrier_loss_receipted','exact_replay',
                 'late_failure_atomic','stale_source_rejected','tampered_state_rejected','negative_duration_rejected'))
            and set(scope['execution_families'])=={'C_OS','C_CI','A_CI','A_PC','A_OS','C_PC','C_CI_PC'}
            and scope['C_CI_PC_basin_migration_rejected'] and scope['whole_publication_unchanged']
            and scope['full_GRC9V4_conformance'] is False,'public migration/scope coverage')
    if checkpoint=='9.5':
        e=value['evidence']['rejection']
        b.require(e['whole_publication_preserved'] and e['successful_history_unchanged']
            and e['no_v4_substitution'] and e['fresh_native_candidate_observed']
            and e['before_snapshot_sha256']==e['after_snapshot_sha256'],'legacy conflict rollback')
    return value


def matrix():
    from p993_matrix import catalog
    from p9_cpc_acceptance import decision
    prior=storage.read(BASE+"P9-9.3-CPCMatrix.json")
    accepted=decision(b.ROOT)
    b.require(accepted is not None,"accepted sixth-realization predecessor required")
    current=check("9.2")
    rows=deepcopy(prior["cells"])
    b.require(len(rows)==40,"full compatibility roster")
    catalog(b.ROOT)
    for row in rows:
        if row["family"]=="C_PC":
            row.update(disposition="bounded_accepted",reason="explicit_C_PC_acceptance",
                acceptance=dict(path="implementation/phase-9-grcv4/tranche-9/P9-CPC-Acceptance.json",record_digest=accepted["record_digest"]))
        if row["family"]!="C_CI_PC":continue
        evidence=current["evidence"][row["surface"]]
        row.update(disposition="passed_pending_acceptance",reason="new_C_CI_PC_native_delegate_execution",
            complete_profile_id=evidence["complete_profile_id"],model_identity=evidence["model_identity"],
            target_spec_version=evidence["target_spec_version"],acceptance=None,
            execution=dict(path=filename("9.2"),record_digest=current["record_digest"],json_pointer="/evidence/"+row["surface"]))
    return b.seal(dict(schema="p993-ccipc-matrix-successor-v1",family="C_CI_PC",cells=rows,
        predecessor_digest=prior["record_digest"],counts=dict(bounded_accepted=24,passed_pending_acceptance=4,unselected_not_executed=12),
        user_accepted=False,aggregate_closed=False,full_GRC9V4_conformance=False))


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("action",choices=("run","check","matrix"))
    p.add_argument("--checkpoint",choices=GROUPS,default="9.1b")
    args=p.parse_args()
    if args.action=="run":print(json.dumps(run(args.checkpoint),indent=2))
    elif args.action=="check":print(json.dumps(dict(checkpoint=args.checkpoint,outcome=check(args.checkpoint)["outcome"])))
    else:b.write_new(BASE+"P9-9.3-CCIPCMatrix.json",matrix())

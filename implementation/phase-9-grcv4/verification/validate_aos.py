"""Final A_OS checks and reproducible, source-bound validation summary."""
import json
from pathlib import Path
import time
import unittest

import p9_aos_review as review

b=review.b
PATH='implementation/phase-9-grcv4/tranche-9/P9-AOS-Validation.json'
SELF=b.HERE+'validate_aos.py'
GROUPS={
    'retained_science':('test_p984d_aos_oracle','test_p984d_aos_runtime','test_p984ef_aos',
        'test_p984g_aos','test_p984gh_aos_native','test_p984h_aos_covariance','test_p984h_validation_reuse'),
    'existing_integration':('tests.models.test_grc_9_v4_contracts','tests.models.test_grc_9_v4_architecture',
        'tests.models.test_grc_9_v4_owner','tests.models.test_grc_9_v4_legacy',
        'tests.models.test_grc_9_v4_crossing','tests.models.test_grc_9_v4'),
    'review_and_surfaces':('test_p9_aos_review','test_p9101c_support_reconciliation'),
}


def suite(names):
    return unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in names)


def run_group(name):
    started=time.monotonic()
    with b.exact_backend(b.ExactBackend.FLINT):
        result=unittest.TextTestRunner(verbosity=2).run(suite(GROUPS[name]))
    b.require(result.wasSuccessful(),'validation group failed: '+name)
    # The pre-existing abstract family suites explicitly skip their base class;
    # concrete suites must run. New scientific and side-tool tests never skip.
    b.require(name=='existing_integration' or not result.skipped,'unexpected validation skip')
    return dict(group=name,modules=list(GROUPS[name]),tests_run=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),
        skipped=[dict(test=str(test),reason=reason) for test,reason in result.skipped],
        seconds=time.monotonic()-started,outcome='passed')


def main():
    b.require(not (b.ROOT/PATH).exists(),'refuse overwrite validation evidence')
    groups=[]
    # Execute the final capture wrapper after source cleanup, including the
    # explicit refusal of unselected A_OS basin migration.
    for checkpoint in review.integration.GROUPS:
        if not (b.ROOT/review.integration.filename(checkpoint)).exists():
            with b.exact_backend(b.ExactBackend.FLINT):review.integration.run(checkpoint)
        review.integration.check(checkpoint)
    matrix=review.integration.BASE+'P9-9.3-AOSMatrix.json'
    if not (b.ROOT/matrix).exists():b.write_new(matrix,review.integration.matrix())
    if not (b.ROOT/review.authority.PATH).exists():
        value=review.authority.build();review.authority.check(value);b.write_new(review.authority.PATH,value)
    groups.append(run_group('retained_science'))
    groups.append(run_group('existing_integration'))
    value=review.build();review.checked(value=value)
    if (b.ROOT/review.PATH).exists():
        b.require(review.checked()==value,'review no longer rebuilds')
    else:b.write_new(review.PATH,value)
    groups.append(run_group('review_and_surfaces'))
    paths={SELF,review.SELF,review.TEST,review.PATH}
    paths|={p.relative_to(b.ROOT).as_posix() for p in (b.ROOT/'src').rglob('*.py')}
    for group in GROUPS.values():
        for name in group:
            module=__import__(name,fromlist=['__file__'])
            paths.add(Path(module.__file__).resolve().relative_to(b.ROOT).as_posix())
    record=b.seal(dict(schema='p9-aos-validation-v1',groups=groups,
        new_integration_tests=sum(review.integration.COUNTS.values()),
        source_bindings=b.bind(paths),review_digest=value['record_digest'],
        exact_backend='flint',outcome='passed',user_accepted=False,aggregate_closed=False))
    b.write_new(PATH,record)
    print(json.dumps(dict(outcome='passed',groups=groups,new_integration_tests=22)),flush=True)


if __name__=='__main__':main()

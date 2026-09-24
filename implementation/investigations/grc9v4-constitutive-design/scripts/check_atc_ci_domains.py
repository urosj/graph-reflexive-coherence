#!/usr/bin/env python3
"""CI-2 rational domain certificate; investigation-only, stdout-only."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = Path('implementation/investigations/grc9v4-constitutive-design')
sys.path.insert(0, str(ROOT/INV/'research'))
import atc_ci_domains as d


def source_bindings(extra=()):
    paths = {Path(__file__).resolve(), ROOT/INV/'decisions/ATCCIDomainsAndReference.md',
        ROOT/INV/'evidence/atc-ci-pc/ATCCIPCAnchorCertificate.json',
        ROOT/INV/'evidence/atc-ci-pc/CI1PC1-IndependentReview.md',
        ROOT/INV/'evidence/atc-ci-successor/CI2CI3-IndependentReview.md',
        ROOT/INV/'evidence/atc-ci-successor/CI3-DerivedWitness-IndependentReview.md',
        ROOT/INV/'decisions/ATCSectorStateDomain.md',
        ROOT/INV/'decisions/ATCSectorChannelsAndRequests.md', *extra}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT/INV) and path.suffix == '.py':
                paths.add(path)
    return [dict(path=p.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            for p in sorted(paths)]


def run():
    a = d.anchor.a
    bounds = d.domain_bounds()
    # Recheck finite incidence/WLS identities, not any OS numerical campaign.
    algebra = a.mathref.algebra_checks()
    value = a.encode(dict(schema='grcv4_atc_ci2_domains_v1',
        status='independent_review_pass_scientifically_closed_pending_scoped_adjudication',
        scientific_acceptance=True, graph_admitted=False, native_ATC_executed=False, ATC2_closed=False,
        evidence=dict(bounds=bounds, algebra=algebra),
        claim_updates=[dict(claim_id='ATC-CI-DOMAIN-02', claim_class='conditional',
            profile_scope=['A_CI'], predecessor_handles=['ATC-CI-CHAIN-01'],
            debt_refs=['ATC7-DB-'+n for n in ('02','03','04','05','06','07','08','12','14','15','16','19','26','28')],
            local_debt_discharge=False, native_authority=False,
            still_open='CI3 independent reference/representation; review and DB24/source admission; wider graphs, formation and aggregate ATC2')]))
    value['source_bindings'] = source_bindings()
    value['record_digest'] = a.digest(value)
    return value


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))

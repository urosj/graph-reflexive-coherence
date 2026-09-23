"""PC-2 support-restriction control, explicitly partially lossy.

Research only. No target dynamics are used to choose the map. The additional
constitutive axiom is nearest admissible history with no invented bridge
memory, measured in the declared symmetric-star Frobenius norm. This remains
a valid option, but its selection was superseded by the relational-lift
candidate on the exact decorated domain. POLICY names this control only.
"""
from fractions import Fraction as F
import atc_ci_pc_anchor as r

POLICY = 'pc_star_restriction_partial_loss_v1'
RESET = 'pc_whole_carrier_loss_zero_v1'


def supported(edges,i,j):
    return bool(set(edges[i]) & set(edges[j]))


def restrict(values,source_edges,target_edges,lineage):
    """Pi_target(E Z E^T), where lineage[i]=(target edge, orientation sign).

    Generic linear-algebra kernel for covariance pressure. The scientific
    event wrapper below fixes the reviewed star-to-double-star operation.
    """
    n,m=len(source_edges),len(target_edges)
    r.require(len(values)==n and all(len(row)==n for row in values),'source carrier dimensions')
    r.require(len(lineage)==n and all(type(j) is int and 0<=j<m and s in (-1,1)
                                    for j,s in lineage),'complete signed edge lineage')
    r.require(len({j for j,_ in lineage})==n,'injective surviving-edge lineage')
    def zero(x): return x.lo==x.hi==0 if isinstance(x,r.I) else x==0
    def equal(x,y): return r.same(x,y) if isinstance(x,r.I) else x==y
    r.require(all(equal(values[i][j],values[j][i]) for i in range(n) for j in range(n)),
              'symmetric source history')
    r.require(all(zero(values[i][j]) for i in range(n) for j in range(n)
                  if not supported(source_edges,i,j)), 'source history outside star support')
    z=values[0][0]*0
    embedded=[[z for _ in range(m)] for _ in range(m)]
    for i,(u,si) in enumerate(lineage):
        for j,(v,sj) in enumerate(lineage): embedded[u][v]=si*sj*values[i][j]
    kept=tuple(tuple(x if supported(target_edges,i,j) else z for j,x in enumerate(row))
               for i,row in enumerate(embedded))
    dropped=tuple(tuple(z if supported(target_edges,i,j) else x for j,x in enumerate(row))
                  for i,row in enumerate(embedded))
    return kept,dropped,tuple(map(tuple,embedded))


def event_carrier(carrier,policy=POLICY):
    r.require(type(carrier) is r.Carrier and carrier.graph=='paired_source','admitted paired source carrier')
    r.require(policy in (POLICY,RESET),'explicit known carrier-event policy')
    kept,dropped,embedded=restrict(carrier.values,r.p.SOURCE,r.p.TARGET,tuple((i,1) for i in range(4)))
    if policy==RESET:
        kept=tuple(tuple(r.I(0) for _ in range(5)) for _ in range(5));dropped=embedded
    target=r.Carrier('paired_target',kept,policy+':'+carrier.basis,token=r._DOMAIN_TOKEN)
    flat=tuple(x for row in dropped for x in row)
    proved=any(x.lo>0 or x.hi<0 for x in flat)
    absent=all(x.lo==x.hi==0 for x in flat)
    receipt=dict(policy_id=policy,channel='carrier',
        disposition='partial_transport_explicit_loss' if policy==POLICY else 'whole_carrier_reset_explicit_loss',
        source_graph='paired_source',target_graph='paired_target',
        source_carrier=carrier.values,source_digest=r.a.digest(r.a.encode(carrier.values)),
        target_carrier=target.values,target_digest=r.a.digest(r.a.encode(target.values)),
        discarded_carrier=dropped,discarded_digest=r.a.digest(r.a.encode(dropped)),
        source_norm_upper=r.norm_upper(x for row in carrier.values for x in row),
        target_norm_upper=r.norm_upper(x for row in kept for x in row),
        discarded_norm_squared=r.p.norm2(flat),
        information_loss='proved_nonzero' if proved else 'exactly_zero' if absent else 'not_excluded',
        map_is_lossless=False,new_bridge_carrier='exact_zero',
        W_disposition='separate channel: old edges exact lineage, new bridge W=1',
        target_dynamic_restoration_claimed=False,native_authority=False)
    return target,receipt

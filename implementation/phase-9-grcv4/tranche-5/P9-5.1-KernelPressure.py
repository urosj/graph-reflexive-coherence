"""Independent audit of verbatim AST-extracted P9-5.1 numerical kernels.

This is NOT the repository's 38-method suite or a test of its schema, profile,
package, verifier, or lifecycle integration. The uploaded function/method bodies
are executed unchanged; lightweight graph/coordinate carriers supply only their
numeric inputs. SymPy provides an independent exact matrix-inverse oracle.
"""
from __future__ import annotations
import ast, dataclasses, hashlib, json, math, random, types
from fractions import Fraction
from pathlib import Path
import sympy as sp
import mpmath as mp

import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, default=None,
                    help='Path to grc_v4_candidate_a.py (no package import is performed).')
parser.add_argument('--output', type=Path, default=Path('P9-5.1-AuditPressure.json'))
args=parser.parse_args()
if args.source is None:
    candidates=(Path('src/pygrc/models/grc_v4_candidate_a.py'),
                Path('grc_v4_candidate_a.py'),
                Path(__file__).resolve().parent/'grc_v4_candidate_a.py')
    SOURCE=next((path for path in candidates if path.is_file()),None)
    if SOURCE is None:
        parser.error('Supply --source or run from the repository root.')
else:
    SOURCE=args.source
if not SOURCE.is_file():
    parser.error(f'Source does not exist: {SOURCE}')
TREE=ast.parse(SOURCE.read_text())
class NonfiniteGeometryError(ValueError): pass

def _computed(value):
    if not math.isfinite(value): raise NonfiniteGeometryError('nonfinite numerical result')
    return 0.0 if value == 0 else value

def _number(value):
    if type(value) not in (int,float) or not math.isfinite(value): raise ValueError('invalid number')
    return float(value)

def _vector(values, positive=False, nonnegative=False):
    result=tuple(_number(v) for v in values)
    if positive and any(v<=0 for v in result): raise ValueError('not positive')
    if nonnegative and any(v<0 for v in result): raise ValueError('negative')
    return result

@dataclasses.dataclass(frozen=True)
class Edge:
    edge_id:str
    tail_node_id:int
    head_node_id:int
@dataclasses.dataclass(frozen=True)
class Graph:
    live_node_ids:tuple
    oriented_edges:tuple
    def node_index(self,node): return self.live_node_ids.index(node)
@dataclasses.dataclass(frozen=True)
class VertexScalar:
    graph:Graph
    values:tuple
@dataclasses.dataclass(frozen=True)
class PhysicalFlux:
    graph:Graph
    values:tuple

def _require_coordinates(value,kind,graph):
    assert type(value) is kind and value.graph==graph

selected=[]
for node in TREE.body:
    if isinstance(node,ast.FunctionDef) and node.name in {'_finite_fraction','_solve_spd','_conductance'}:
        selected.append(node)
    if isinstance(node,ast.ClassDef) and node.name=='CandidateADifferentialReference':
        selected.extend(n for n in node.body if isinstance(n,ast.FunctionDef) and n.name=='rebuild')
module=ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')],level=0)]+selected,type_ignores=[])
ns=dict(globals())
exec(compile(ast.fix_missing_locations(module),str(SOURCE),'exec'),ns)
solve=ns['_solve_spd']; rebuild=ns['rebuild']; conductance=ns['_conductance']

rng=random.Random(951900)
counts={}; failures=[]
def record(name,ok,detail=None):
    counts[name]=counts.get(name,0)+1
    if not ok: failures.append({'category':name,'detail':detail})
def F(x): return Fraction(x)
def S(x): return sp.Rational(F(x).numerator,F(x).denominator)
def R(x): return F(int(sp.numer(x)))/int(sp.denom(x))

# Independent inverse vs source's elimination, including dimensions > 2.
for k in range(90):
    d=1+k%6
    X=sp.Matrix([[sp.Rational(rng.randrange(-5,6),4) for _ in range(d)] for _ in range(d+2)])
    ridge=sp.Rational(1,2**(k%9))
    A=X.T*X+ridge*sp.eye(d)
    b=sp.Matrix([sp.Rational(rng.randrange(-20,21),8) for _ in range(d)])
    got=solve([[R(A[i,j]) for j in range(d)] for i in range(d)],[R(x) for x in b])
    expected=tuple(float(R(x)) for x in A.inv()*b)
    record('exact_SPD_inverse',got==expected,{'case':k,'dimension':d})

# WLS graph kernels vs independently assembled incidence-style local design.
for k in range(48):
    n=1+k%7; d=1+k%4
    edges=tuple(Edge(str(e),rng.randrange(n),rng.randrange(n)) for e in range(2*n))
    graph=Graph(tuple(range(n)),edges)
    positions=tuple(tuple(rng.randrange(-8,9)/4 for _ in range(d)) for _ in range(n))
    weights={e.edge_id:rng.randrange(1,9)/4 for e in edges}
    ridge=2.0**-(k%6)
    C=VertexScalar(graph,tuple(rng.randrange(0,21)/4 for _ in range(n)))
    back=types.SimpleNamespace(graph=graph,dimension=d,positions=positions,reference_weights=weights,regularization=ridge)
    got=rebuild(back,C)
    expected=[]
    for i in range(n):
        rows=[]; ww=[]; dc=[]
        for e in edges:
            if e.tail_node_id==i or e.head_node_id==i:
                j=e.head_node_id if e.tail_node_id==i else e.tail_node_id
                rows.append([S(positions[j][l])-S(positions[i][l]) for l in range(d)])
                ww.append(S(weights[e.edge_id])); dc.append(S(C.values[j])-S(C.values[i]))
        if rows:
            X=sp.Matrix(rows); W=sp.diag(*ww)
            normal=X.T*W*X+S(ridge)*sp.eye(d)
            target=normal.inv()*X.T*W*sp.Matrix(dc)
            expected.append(tuple(float(R(x)) for x in target))
        else: expected.append((0.0,)*d)
    record('multigraph_WLS',got==tuple(expected),{'case':k})

# Exact loop/parallel/isolated witness.
g=Graph((0,1,2),(Edge('a',0,1),Edge('b',1,0),Edge('loop',0,0)))
b=types.SimpleNamespace(graph=g,dimension=1,positions=((0.0,),(1.0,),(8.0,)),reference_weights={'a':1.0,'b':3.0,'loop':1e308},regularization=1.0)
c=VertexScalar(g,(1.0,3.0,9.0)); D=rebuild(b,c)
record('loop_parallel_isolate',D==((1.6,),(1.6,),(0.0,)))
p=types.SimpleNamespace(alpha=0.0,beta=1.0,gamma=1.0,W_floor=1e-12)
w=conductance(g,p,c,D,PhysicalFlux(g,(0.5,-1.0,2.0)))
record('loop_parallel_conductance',w==tuple(math.exp(v) for v in (-0.125,-0.5,-2.0)))

# Independent mp exp on EXACT BINARY64 ROUNDED exponent; this is the declared
# two-stage arithmetic, not RN(exp(exact rational exponent)) generally.
mp.mp.dps=160
for k in range(96):
    graph=Graph((0,1),(Edge('e',0,1),))
    C=VertexScalar(graph,(rng.randrange(0,20)/4,rng.randrange(0,20)/4))
    Ds=tuple(tuple(rng.randrange(-8,9)/4 for _ in range(3)) for _ in range(2))
    J=PhysicalFlux(graph,(rng.randrange(-12,13)/4,))
    p=types.SimpleNamespace(alpha=rng.randrange(-3,4)/4,beta=rng.randrange(-3,4)/4,gamma=rng.randrange(-3,4)/4,W_floor=2.0**-(k%40))
    E=-(F(p.alpha)*(F(C.values[0])+F(C.values[1]))+F(p.beta)*sum((F(a)-F(b))**2 for a,b in zip(*Ds))+F(p.gamma)*F(J.values[0])**2)/2
    er=F(float(E)); exact_exp=mp.exp(mp.mpf(er.numerator)/er.denominator)
    expected=max(p.W_floor,float(exact_exp)); got=conductance(graph,p,C,Ds,J)[0]
    record('conductance_rounded_exponent_oracle',abs(got-expected)<=math.ulp(expected),{'case':k,'got':got,'expected':expected})

# Range and cancellation probes, including huge exact sums and subnormal floors.
g=Graph((0,1),(Edge('e',0,1),)); Ds=((0.,),(0.,))
for floor in (5e-324,1e-12,1.0,2.0,1e308):
    p=types.SimpleNamespace(alpha=1.0,beta=0.0,gamma=0.0,W_floor=floor)
    for exponent in (-1001.,-1000.,-746.,-745.,-744.,0.):
        v=-exponent
        got=conductance(g,p,VertexScalar(g,(v,v)),Ds,PhysicalFlux(g,(0.,)))[0]
        expected=max(floor,float(mp.exp(exponent)))
        record('floor_boundaries',got==expected,{'floor':floor,'exponent':exponent})
p=types.SimpleNamespace(alpha=1.0,beta=0.0,gamma=-2.0,W_floor=1e-12)
c=math.ldexp(1.,1000); j=math.ldexp(1.,500)
record('large_signed_cancellation',conductance(g,p,VertexScalar(g,(c,c)),Ds,PhysicalFlux(g,(j,)))==(1.,))

# Domain probes make the actual overflow/underflow policy explicit.
try:
    ns['_finite_fraction'](F(1e308)**2)
    record('gradient_overflow',False)
except NonfiniteGeometryError: record('gradient_overflow',True)
underflow_value=ns['_finite_fraction'](F(5e-324)/4)
record('gradient_underflow_observation',underflow_value==0.0)

# A high-exponent example to distinguish 4-ulp local tests from a global accuracy claim.
p=types.SimpleNamespace(alpha=-0.1,beta=0.,gamma=0.,W_floor=1e-12)
C=VertexScalar(g,(7001.,7001.)); E=F(0.1)*7001
value=conductance(g,p,C,Ds,PhysicalFlux(g,(0.,)))[0]
mathematical=float(mp.exp(mp.mpf(E.numerator)/E.denominator))
rounding_example={'exact_exponent':str(E),'rounded_exponent':float(E),'kernel':value,'RN_exp_exact_exponent':mathematical,'ulp_distance':abs(value-mathematical)/math.ulp(mathematical)}

result={'scope':__doc__,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'kernel_bodies':[n.name for n in selected],'seed':951900,'python':__import__('sys').version,'sympy':sp.__version__,'mpmath':mp.__version__,'case_counts':counts,'total_cases':sum(counts.values()),'failures':failures,'gradient_underflow_result':underflow_value,'rounded_exponent_accuracy_example':rounding_example,'not_executed':['repository 38-method suite','verify_p951_initialization.py','profile/codec/schema/lifecycle integration']}
# Concrete whole-WLS underflow and explicit-flux dependence: observations, not
# additional conformance claims or failing tests of the declared numeric policy.
b=types.SimpleNamespace(graph=g,dimension=1,positions=((0.,),(1.,)),reference_weights={'e':1.},regularization=4.)
result['whole_WLS_underflow_observation']={
    'C':[0.,5e-324], 'positions':[[0.],[1.]], 'reference_weight':1., 'ridge':4.,
    'exact_each':'(minimum_positive_binary64)/5',
    'computed':rebuild(b,VertexScalar(g,(0.,5e-324)))}
p=types.SimpleNamespace(alpha=0.,beta=0.,gamma=1.,W_floor=1e-12)
result['explicit_reference_flux_dependence']={
    str(j):conductance(g,p,VertexScalar(g,(1.,3.)),((0.,),(0.,)),PhysicalFlux(g,(j,)))[0]
    for j in (0.,1.)}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

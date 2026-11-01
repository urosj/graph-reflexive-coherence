"""Recheck the spark manuscript's corrected admission and stationary arguments.

Exact FLINT algebra and a 256-bit Arb domain enclosure; no trajectory runs,
certificate regeneration, authority changes or writes to the repository.
"""
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

from flint import arb, ctx, fmpq, fmpq_mat

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
sys.path[:0] = [str(ROOT / 'src'), str(INV / 'research'),
               str(INV / 'evidence/spark-completion/review/constructive-candidate')]
from spark_completion_a_ci import ACIReference, global_root_domain
from spark_completion_a_os import AOSReference, graph_constants
from spark_completion_os_reference import COSReference
from spark_completion_positive import fixture


def norm(matrix):
    return max(sum(abs(F(str(matrix[i, j]))) for j in range(matrix.ncols()))
               for i in range(matrix.nrows()))


def positive_definite(matrix):
    """Exact symmetric elimination: every LDL pivot must be positive."""
    for k in range(matrix.nrows()):
        pivot = matrix[k, k]
        assert pivot > 0, 'nonpositive spectral witness pivot'
        for i in range(k + 1, matrix.nrows()):
            for j in range(i, matrix.nrows()):
                value = matrix[i, j] - matrix[i, k] * matrix[k, j] / pivot
                matrix[i, j] = value
                matrix[j, i] = value


def check():
    source, _, targets = fixture()
    target = targets['1']['graph']
    # Both chiral charts have identical equations, including endpoint rows.
    assert graph_constants(json.dumps(target, sort_keys=True)) == graph_constants(
        json.dumps(targets['-1']['graph'], sort_keys=True))
    base = INV / 'evidence/spark-completion/applicability'
    declaration = json.loads((base / 'CCIPCDeclaration.json').read_text())
    assert declaration['domain']['Z_frobenius_radius'] == '1/128'
    estimates = []
    for name, graph in [('source', source), ('target', target)]:
        model = COSReference(graph, 'rational')
        B, Le = model.B, model.Le
        a = norm((fmpq(3, 4) * model.I + Le).inv())
        lap, incidence = norm(Le), norm(B)
        star, radius = F(max(map(sum, model.overlap)), 8), F(1, 32)
        for carrier in (F(1, 128), F(1, 64)):
            z = F(isqrt(model.m - 1) + 1) * carrier / 2
            h = z + star * radius**2
            assert h < 1 and a * h * lap < 1
            inverse, resolvent = 1 / (1 - h), a / (1 - a * h * lap)
            j = F(2, 1024) * (incidence * F(4, 64) + 6) + lap * h * F(4, 65536)
            y = resolvent * j
            image = inverse * y / 2
            rate = inverse * (resolvent * (lap * F(4, 65536) + lap * y) / 2 + image)
            rate *= 2 * star * radius
            if carrier == F(1, 128):
                limit = F('0.063351') if name == 'source' else F('0.019589')
                assert image < radius and rate < limit
            elif name == 'source':
                assert image > radius, 'the larger-radius self-map estimate changed'
            estimates.append(dict(graph=name, carrier_radius=str(carrier),
                                  image_bound=str(image), contraction=str(rate),
                                  self_map=image < radius))

        # Charge-zero coordinates span the nonconstant spectrum. This proves
        # lambda_2(B B^T) > 1/28 without floating-point eigendecomposition.
        E = fmpq_mat([[int(i == j) if i < model.n - 1 else -1
                       for j in range(model.n - 1)] for i in range(model.n)])
        identity = fmpq_mat([[int(i == j) for j in range(model.n)]
                             for i in range(model.n)])
        positive_definite(E.transpose() * (B * B.transpose() - fmpq(1, 28) * identity) * E)
        assert F(127, 128) * F(1, 28) > F(1, 64)
        if name == 'target':
            # The incorrectly printed radius admits a concrete counterexample
            # to the quoted H >= (255/256) I, even at a zero-flat root.
            C = model.vector({node: '7/5' for node in model.nodes})
            Z = model.matrix(model.m, model.m)
            Z[0, 0] = fmpq(-1, 64)
            H = model.I + Z / 2
            read = model.read(C, H, eta=fmpq(1, 1024))
            assert all(x == 0 for key in ('baseline', 'current', 'causal_flat')
                       for x in read[key].entries())
            assert H[0, 0] == fmpq(127, 128) < fmpq(255, 256)

    aos = json.loads((base / 'AOSResearchProgress.json').read_text())['proof']
    aci = json.loads((base / 'ACIResearchProgress.json').read_text())['proof']
    domain = json.loads((base / 'earlier-closure/AOSAnisotropicDomain.json').read_text())
    assert aos['center'] == aci['center'] and aos['logW_center'] == aci['logW_center']
    assert ACIReference.read is AOSReference.read
    nodes = target['live_node_ids']
    n, m = len(nodes), len(target['edges'])
    d = n - 1 + m
    assert domain['relative_dimension'] == d == 30
    E = fmpq_mat([[int(i == j) if i < n - 1 else -int(j < n - 1)
                   if i == n - 1 else int(j == i - 1)
                   for j in range(d)] for i in range(n + m)])
    T = fmpq_mat([[fmpq(x) for x in row] for row in domain['basis']])
    radii = list(map(fmpq, domain['axis_radii']))
    D = fmpq_mat([[radii[i] if i == j else 0 for j in range(d)] for i in range(d)])
    S = E * T * D
    widths = [sum(abs(S[i, j]) for j in range(d)) for i in range(n + m)]
    with ctx.workprec(256):
        C = [arb(fmpq(aos['center'][node]), widths[i]) for i, node in enumerate(nodes)]
        W = [arb(fmpq(value), widths[n + i]).exp()
             for i, value in enumerate(aos['logW_center'])]
        assert all(0 < x < 4 for x in C)
        assert all(arb(fmpq(99, 100)) < x < arb(fmpq(101, 100)) for x in W)
    auxiliary = global_root_domain(json.dumps(target, sort_keys=True))
    assert auxiliary == aci['root_domain']
    assert F(auxiliary['image_bound']) < F('0.00004041') < F(1, 32)
    assert F(auxiliary['contraction']) < F('0.00000229') < 1

    # diag(4*tau/5, 4*tau/5): operator admission need not imply a
    # Frobenius certificate. These are the exact squared ratios to tau.
    assert F(16, 25) < 1 < F(32, 25)
    paths = [INV / 'drafts/spark-completion/Proposal.md', INV / 'drafts/2026-11-GRC-V4.md']
    proposal, paper = [path.read_text() for path in paths]
    appendix = paper.split('## Appendix H.', 1)[1]
    equations = re.findall(r'\$\$(.*?)\$\$', proposal, re.S)
    assert equations == re.findall(r'\$\$(.*?)\$\$', appendix, re.S)
    return dict(status='passed_spark_publication_corrections',
                composite_estimator=estimates, larger_radius_Hodge_counterexample=True,
                nonconstant_spectral_lower='>1/28', both_chiral_equations_equal=True,
                operator_Frobenius_distinction=True,
                AOS_full_domain_inside_shared_read_chart=True,
                AOS_auxiliary_image_bound=auxiliary['image_bound'],
                AOS_auxiliary_contraction=auxiliary['contraction'],
                matching_display_equations=len(equations),
                documents=[dict(path=str(path.relative_to(ROOT)),
                                sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in paths],
                physical_campaigns_run=0, scientific_authorities_changed=False,
                limits='Checks the corrected auxiliary arguments, not a regeneration of every full-state certificate.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', required=True, action='store_true')
    parser.parse_args()
    print(json.dumps(check(), indent=2))

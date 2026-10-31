"""Basin observations at the connected Lipschitz section, not an instantaneous root.

The recorded chain is observed during the one native read. Existing independent
unreduced edge equations certify that chain; retained checks never call section().
"""
from dataclasses import replace
from fractions import Fraction as Q

import p9101a_basin_oracle as common
import p9_crg2b_runtime as runtime
from pygrc.models.grc_v4_geometry import GeometryStageInputs

require = common.require
capture_chains = runtime.capture_chains


def summary(inputs, record):
    cert, incidence, _ = runtime.data(inputs)
    fixed = Q(record['independent_certificate']['fixed_H_errors']['J'])
    error = Q(record['error_upper'])
    # A_H bounds the base displacement's H dependence. The existing theorem
    # supplies its current factor through A_H = dt ||B|| J_H.
    jh = Q(cert['bounds']['A_H']) / (Q(str(runtime.proof.DT)) * Q(str(runtime.proof.norm(incidence))))
    total = fixed + jh * error
    return dict(current_error_upper=str(fixed), geometry_residual_upper=str(max(Q(row['geometry_residual']) for row in record['independent_certificate']['section']['levels'])),
        represented_nonzero=sum(j != 0 for j in record['J']),
        certified_fixed_geometry_signs=sum(abs(Q(j)) > fixed for j in record['J']),
        exact_root_signs_claimed=False, C1_claimed=False,
        section_error_upper=str(error), section_current_error_upper=str(total),
        section_resolved_sign_count=sum(abs(Q(j)) > total for j in record['J']),
        error_scope='fixed_H_current_plus_separate_Lipschitz_section_bound',
        section_record=record)


def capture(read, point, chain):
    record = runtime.read_record(read, point, chain)
    return summary(read.inputs, record)


def validate(selected, equation, *, numerics=False):
    inputs = GeometryStageInputs.from_payload(selected['recipe']['inputs'])
    record = equation['section_record']
    runtime.check_read(inputs, record, numerics=numerics)
    require(inputs.stage == 'pre_read' and inputs.dt == 0, 'section diagnostic stage')
    require(selected['recipe'] == dict(numerics=runtime.native_completion.APPROXIMATION,
            inputs=inputs.to_payload(), differential_reference=None), 'section completion recipe')
    from pygrc.models.grc_v4_geometry import GRCV4Geometry, OneFormHodge
    geom = GRCV4Geometry(inputs.geometry.reference, OneFormHodge(inputs.geometry.reference.graph,
                         tuple(map(tuple, record['H']))))
    expected = replace(inputs, geometry=geom, stage='rg2b_section').to_payload()
    require(selected['selected_inputs'] == expected
        and selected['H1_form'] == [[float(x).hex() for x in row] for row in record['H']]
        and selected['current'] == [float(x).hex() for x in record['J']]
        and selected['section_identity'] == record['identity']
        and selected['certificate'] == record['chain']['native_global_bounds']
        and all(selected[k] == record[k] for k in ('levels','evaluations','error_upper','enclosure')),
        'full section/chain/query/certificate mismatch')
    require(equation == summary(inputs, record), 'section error scope or bound drift')
    return equation

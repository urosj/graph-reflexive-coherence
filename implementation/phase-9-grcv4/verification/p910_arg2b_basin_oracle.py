"""A_RG2b basin: joint C/Y section, fixed-row backend, and separate error budgets.

Reuse the accepted independent edge-space chain proof, including represented
Y=512 log W query error. No native section is rerun by retained validation.
"""
from dataclasses import replace
from fractions import Fraction as Q

import p9101a_basin_oracle as common
import p9_arg2b_runtime as runtime
from pygrc.models.grc_v4_geometry import GeometryStageInputs, GRCV4Geometry, OneFormHodge

require = common.require
capture_chains = runtime.capture_chains


def hypotheses(inputs):
    ref = inputs.geometry.reference
    p = ref.profile.params_resolved
    require(ref.profile.identity_payload.profile_family_id == 'A_RG2b', 'A section family')
    expected = dict(eta=1,kappa_c=1,W_floor=.5,alpha=2**-24,beta=2**-24,gamma=2**-24,
                    kappa_Ah=.5,chi_A=1/16,zeta_A=.5,tau_A=1)
    require(all(getattr(p.candidate,k) == v for k,v in expected.items())
            and p.geometry.kappa_H == .5
            and all(w == 1 for w in ref.edge_weights.values())
            and all(v == 0 for row in ref.K4_base for v in row), 'independent A coefficients/reference')
    require(inputs.context.contract_id == 'constant_zero_context_v1'
            and inputs.context.value.to_dict() == {}, 'independent A zero context')
    require(p.realization.extension_evaluator_id == runtime.native_completion.EXTENSION
            and p.realization.containment_certificate_id == runtime.native_completion.CONTAINMENT
            and p.realization.approximation_policy_id == runtime.native_completion.APPROXIMATION
            and p.realization.error_tolerance == 2**-48 and p.realization.iteration_limit == 148,
            'independent A connected completion policy')
    require(inputs.current.W_A is not None and inputs.current.Z_4 is None, 'A history without carrier')


def summary(inputs, record):
    hypotheses(inputs)
    fixed = Q(record['independent_certificate']['fixed_H_errors']['J'])
    sc = record['independent_certificate']['section']
    # Independent edge and native factored certificates can have slightly
    # different outward widths. Retain both; conservatively use their maximum.
    error = max(Q(record['error_upper']), Q(sc['section_error_upper']))
    bounds, _ = runtime.proof.global_bounds()
    total = fixed + Q(str(bounds['J_H'])) * error
    return dict(current_error_upper=str(fixed),
        geometry_residual_upper=str(max(Q(row['geometry_residual']) for row in sc['levels'])),
        represented_nonzero=sum(j != 0 for j in record['J']),
        certified_fixed_geometry_signs=sum(abs(Q(j)) > fixed for j in record['J']),
        exact_root_signs_claimed=False, C1_claimed=False,
        section_error_upper=str(error), native_section_error_upper=record['error_upper'],
        independent_section_error_upper=sc['section_error_upper'],
        input_log_coordinate_error_upper=sc['input_coordinate_error'],
        input_section_error_upper=sc['input_section_error'],
        section_current_error_upper=str(total),
        section_resolved_sign_count=sum(abs(Q(j)) > total for j in record['J']),
        error_scope='fixed_H_current_plus_separate_joint_C_Y_Lipschitz_section_bound',
        section_record=record)


def capture(read, point, chain):
    hypotheses(read.inputs)
    from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
    # The selected native point was captured under this explicit execution policy.
    with exact_backend(ExactBackend.FLINT):
        record = runtime.read_record(read, point, chain)
    return summary(read.inputs, record)


def validate(selected, equation, *, numerics=False):
    inputs = GeometryStageInputs.from_payload(selected['recipe']['inputs'])
    hypotheses(inputs)
    record = equation['section_record']
    runtime.check_read(inputs, record, numerics=numerics)
    require(inputs.stage == 'pre_read' and inputs.dt == 0, 'section diagnostic stage')
    backend = runtime.r.backend(inputs)
    require(selected['recipe'] == dict(numerics=runtime.native_completion.APPROXIMATION,
            inputs=inputs.to_payload(), differential_reference=backend.to_payload()),
            'A section completion/backend recipe')
    geom = GRCV4Geometry(inputs.geometry.reference, OneFormHodge(inputs.geometry.reference.graph,
                         tuple(map(tuple, record['H']))))
    expected = replace(inputs, geometry=geom, stage='rg2b_section').to_payload()
    require(selected['selected_inputs'] == expected
        and selected['H1_form'] == [[float(x).hex() for x in row] for row in record['H']]
        and selected['current'] == [float(x).hex() for x in record['J']]
        and selected['section_identity'] == record['identity']
        and selected['certificate'] == record['chain']['native_global_bounds']
        and all(selected[k] == record[k] for k in ('levels','evaluations','error_upper','enclosure')),
        'full A section/chain/query/certificate mismatch')
    require(equation == summary(inputs, record), 'A section error scope or bound drift')
    return equation

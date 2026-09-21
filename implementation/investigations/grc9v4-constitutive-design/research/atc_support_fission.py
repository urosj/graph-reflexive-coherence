"""Checked successor interface for the reviewed fixed research construction.

The original model/driver remain byte-identical for the independently reviewed
execution. New callers use this interface when consuming the full F2 record.
"""
from fractions import Fraction as F

import atc_support as model


def checked_fixed_fission(state, prescription):
    if (type(state) is not model.State or state.graph != model.SOURCE_GRAPH
            or state.C != (1., 3., 1.)
            or type(prescription) is not dict
            or set(prescription) != {'vertex', 'blocks', 'shares', 'allocated_current'}):
        raise model.ResearchDomainError('expected complete fixed-fixture F2 prescription')
    expected = [str(F(model.rounded(F(state.C[1])/2)))]*2
    allocated = prescription['allocated_current']
    if (type(allocated) is not list or len(allocated) != 2
            or any(type(x) is not str for x in allocated) or allocated != expected):
        raise model.ResearchDomainError('F2 allocated_current differs from recomputed allocation')
    return model.fixed_fission(state, prescription)

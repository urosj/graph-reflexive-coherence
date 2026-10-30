"""Carry the explicitly selected charge successor through spawned workers.

Only harness bindings and exact Fraction-to-FLINT threshold conversion change.
No root, producer, tolerance, arithmetic policy or admission is replaced.
"""
from contextlib import contextmanager
from fractions import Fraction
from unittest.mock import patch
import p9_acipc_large_charge as charge
n=charge.n
SELF=n.b.HERE+'p9_acipc_execution_scope.py'


@contextmanager
def science_scope():
    def exact(value):
        return n.g.q(str(value)) if isinstance(value,Fraction) else n.g.q(value)
    with charge.context(),patch.object(n,'q',exact):yield


def child_in_scope(pipe,function,args):
    with science_scope():
        n.b.require(n.INPUTS==charge.NATIVE and n.companion.INPUTS==charge.INPUTS,
                    'spawned successor binding absent')
        function(pipe,*args)


@contextmanager
def execution_scope():
    capped=n.process_budget.capped
    def guarded(function,args,seconds):
        return capped(child_in_scope,(function,args),seconds)
    with science_scope(),patch.object(n.process_budget,'capped',guarded):yield

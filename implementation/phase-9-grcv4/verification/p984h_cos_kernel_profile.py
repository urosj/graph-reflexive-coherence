"""Cold C_OS kernel attribution; diagnostic instrumentation, not a campaign.

Compile the installed functions' AST with timing-only context managers around
statements. No expression, branch, loop body, return or exception is replaced.
Instrument only outer statements (plus rounded_solve's precision context), not
individual scalar operations. Full retained read parity is mandatory.
"""
import ast
from collections import defaultdict
from contextlib import ExitStack, contextmanager
import inspect
import json
import lzma
import os
import signal
import sys
import textwrap
import time
from dataclasses import replace
from unittest.mock import patch

import p984h_cos_solve_reuse as previous

probe = previous.probe
run = probe.run
SELF = run.HERE + 'p984h_cos_kernel_profile.py'
OUTPUT = run.BASE + 'P9-8.4h-COSKernelProfile.json.xz'


class Timers:
    def __init__(self):
        self.counters = defaultdict(lambda: dict(calls=0, inclusive_seconds=0., exclusive_seconds=0.))
        self.stack = []

    @contextmanager
    def measure(self, label):
        entry = [time.perf_counter(), 0.]
        self.stack.append(entry)
        try:
            yield
        finally:
            elapsed = time.perf_counter() - entry[0]
            self.stack.pop()
            row = self.counters[label]
            row['calls'] += 1
            row['inclusive_seconds'] += elapsed
            row['exclusive_seconds'] += elapsed - entry[1]
            if self.stack:
                self.stack[-1][1] += elapsed


def instrument(fn, timers, *, precision_body=False):
    source = textwrap.dedent(inspect.getsource(fn))
    tree = ast.parse(source)
    definition = tree.body[0]
    run.require(isinstance(definition, ast.FunctionDef) and not definition.decorator_list,
                'diagnostic requires undecorated function')
    label = fn.__module__.split('.')[-1] + '.' + fn.__qualname__

    def wrap(statement):
        caption = ast.get_source_segment(source, statement).splitlines()[0].strip()
        name = f'{label}:L{statement.lineno}:{caption}'
        if precision_body and isinstance(statement, ast.With):
            statement.body = [wrap(child) for child in statement.body]
        return ast.With(items=[ast.withitem(context_expr=ast.Call(
            func=ast.Name(id='_kernel_timer', ctx=ast.Load()),
            args=[ast.Constant(name)], keywords=[]))], body=[statement])

    definition.body = [statement if isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Constant)
        and isinstance(statement.value.value, str) else wrap(statement)
        for statement in definition.body]
    ast.fix_missing_locations(tree)
    namespace = dict(fn.__globals__, _kernel_timer=timers.measure)
    exec(compile(tree, '<timed-installed-kernel>', 'exec'), namespace)
    return namespace[fn.__name__]


@contextmanager
def timing(timers):
    targets = [(probe.matrix, name) for name in
               ('exact_matrix', 'binary64_matrix', 'inverse', 'inertia')]
    targets += [(probe.fm, 'matmul')]
    targets += [(probe.cert, name) for name in ('condition_bound', 'positive_definite')]
    targets += [(probe.geometry, '_capture_stage_inputs')]

    def wrapper(fn, label):
        def call(*args, **kwargs):
            with timers.measure(label):
                return fn(*args, **kwargs)
        return call

    replacements = {id(getattr(m, n)): (getattr(m, n), wrapper(getattr(m, n),
                    m.__name__.split('.')[-1] + '.' + n)) for m, n in targets}
    original = probe.cert.rounded_solve
    replacements[id(original)] = (original, instrument(original, timers, precision_body=True))
    with ExitStack() as patches:
        for name, module in list(sys.modules.items()):
            if not name.startswith('pygrc.models.') or module is None:
                continue
            for attr, value in list(vars(module).items()):
                pair = replacements.get(id(value))
                if pair is not None and value is pair[0]:
                    patches.enter_context(patch.object(module, attr, pair[1]))
        for cls in (probe.candidate._CandidateCAlgebra, probe.candidate.CandidateCSelector):
            patches.enter_context(patch.object(cls, '__post_init__', instrument(cls.__post_init__, timers)))
        yield


def main():
    run.require(not (run.ROOT / OUTPUT).exists(), 'refuse overwrite')
    run.require(all(os.environ.get(k) == '1' for k in
                    ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS')), 'single thread')
    baseline = json.loads(lzma.decompress((run.ROOT / probe.OUTPUT).read_bytes()))
    run.require(baseline == run.seal(baseline), 'baseline identity')
    with run.oracle.exact_backend(run.oracle.ExactBackend.FLINT), run.oracle.numerical_policy(run.oracle.NumericalPolicy.CERTIFIED_ARB_256):
        saved = run.read('prefix')
        run.require(saved == run.seal(saved) and saved['record_digest'] == baseline['prefix_digest'], 'prefix identity')
        before = replace(run.state(saved['execution']['state']).inputs, dt=1.)
        run.require(run.digest(before.to_payload()) == baseline['input_digest'], 'same read input')
        bindings = {p: run.oracle.sha(p) for p in
                    {SELF, previous.SELF, probe.SELF, probe.OUTPUT, *baseline['source_bindings']}}
        timers = Timers()
        def expired(*_):
            raise TimeoutError('600-second diagnostic cap; no fallback')
        signal.signal(signal.SIGALRM, expired)
        signal.alarm(600)
        started = time.perf_counter()
        with timing(timers), run.matrix_operation():
            passed = probe.CandidateCOSPass(before)
        elapsed = time.perf_counter() - started
        signal.alarm(0)
        observed = previous.view(passed)
        run.require(observed == {k: baseline[k] for k in previous.FIELDS}, 'full read parity')
        run.require(bindings == {p: run.oracle.sha(p) for p in bindings}, 'source changed during probe')
        result = run.seal(dict(schema='p984h-cos-kernel-profile-v1', source_bindings=bindings,
            baseline_record_digest=baseline['record_digest'], input_digest=baseline['input_digest'],
            backend='flint', numerical_policy='certified_arb_256_weighted_v1',
            scope='cold_source_current_read_with_AST_timing_not_event_or_step',
            elapsed_seconds=elapsed, counters=dict(timers.counters),
            uninstrumented_seconds=elapsed - sum(t['exclusive_seconds'] for t in timers.counters.values()),
            scientific_view_digest=run.digest(observed), baseline_parity=True,
            native_events=0, native_steps=0))
        raw = json.dumps(result, indent=2, allow_nan=False).encode() + b'\n'
        with (run.ROOT / OUTPUT).open('xb') as stream:
            stream.write(lzma.compress(raw))
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

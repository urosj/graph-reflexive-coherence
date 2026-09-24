#!/usr/bin/env python3
"""Read-only pressure for the proposed support fixture's native bridge.

This does NOT install a potential or simulate the multiwell law. Matching
zero-potential controls pass; the proposed new ID must fail at each old owner.
Print a new record to stdout without replacing any retained evidence.
"""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]

PROPOSED_ID = 'research_atc_sup_mw_site_derivative_v1'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def run():
    from pygrc.models.grc_v4 import GRCV4
    from pygrc.models.grc_v4_candidate_a import CandidateACurrent
    from pygrc.models.grc_v4_codec import V4SchemaError
    from pygrc.models.grc_v4_geometry import GRCV4Graph, OrientedEdge
    from pygrc.models.grc_v4_initializer import CandidateAReferencePass, HISTORY_POLICY
    from pygrc.models.grc_v4_lifecycle import _crossing_declaration, _CrossingDeclarationError
    from tests.models.test_grc_v4_candidate_a import current_fixture
    from tests.models.test_grc_v4_migration import changed_reference

    predecessor_path = REFS / 'ATCSupportFixtureCertificate.json'
    predecessor = json.loads(predecessor_path.read_text())
    assert predecessor['record_digest'] == sha(canonical(
        {k: v for k, v in predecessor.items() if k != 'record_digest'}))
    for binding in predecessor['source_bindings']:
        assert sha((ROOT / binding['path']).read_bytes()) == binding['sha256'], binding['path']

    def rejected(operation, error_type, message=None):
        try:
            operation()
        except error_type as exc:
            if message is not None:
                assert str(exc) == message, str(exc)
            return dict(error_type=type(exc).__name__, outcome='rejected')
        raise AssertionError('proposed unimplemented potential was silently admitted')

    rows = []
    eps = 2**-12
    for label, graph, C, reset_C in (
        ('source', GRCV4Graph(('a', 'b', 'c'), (
            OrientedEdge('ab', 'a', 'b'), OrientedEdge('bc', 'b', 'c'))),
            (1., 3., 1.), (1.+eps, 3.-2*eps, 1.+eps)),
        ('target', GRCV4Graph(('a', 'c', 'v0', 'v1'), (
            OrientedEdge('ab', 'a', 'v0'), OrientedEdge('bc', 'v1', 'c'),
            OrientedEdge('connector', 'v0', 'v1'))),
            (1., 1., 1.5, 1.5), (1.+eps, 1.+eps, 1.5-eps, 1.5-eps)),
    ):
        inputs, backend = current_fixture(graph=graph, C=C,
            W=(1.,)*len(graph.live_edge_ids), dt=2**-6, kappa_c=2**-10,
            kappa_Ah=0., chi_A=0., zeta_A=0.,
            changes={'lifecycle': {'history_policy_id': HISTORY_POLICY}})
        inputs = replace(inputs, reset=replace(inputs.reset, C=reset_C))
        assert inputs.current != inputs.reset and sum(C) == sum(reset_C) == 5
        old = inputs.geometry.reference
        new = changed_reference(old, 'candidate', site_potential_id=PROPOSED_ID)
        assert new.profile.complete_profile_id != old.profile.complete_profile_id
        proposed = replace(inputs, geometry=new.geometry())
        GRCV4(inputs, differential_reference=backend)  # Positive admission control.
        owner_result = rejected(lambda: GRCV4(proposed, differential_reference=backend),
                                ValueError, 'unimplemented A current/profile declaration')
        _crossing_declaration(old)
        crossing_result = rejected(lambda: _crossing_declaration(new),
            _CrossingDeclarationError, 'unsupported A potential declaration')
        roles = []
        for role in ('current', 'reset'):
            state = getattr(inputs, role)
            CandidateACurrent(replace(inputs, current=state), backend)
            positive_init = CandidateAReferencePass(old, backend, state.C, role)
            assert positive_init.W_A_init == (1.,)*len(graph.live_edge_ids)
            current_result = rejected(
                lambda: CandidateACurrent(replace(proposed, current=state), backend),
                ValueError, 'unimplemented A current/profile declaration')
            initializer_result = rejected(
                lambda: CandidateAReferencePass(new, backend, state.C, role), V4SchemaError,
                "initializer target_reference: 'quadratic_site_potential_zero_derivative_v1' was expected")
            roles.append(dict(role=role, C=state.C, zero_potential_control='passed',
                              proposed_current=current_result, proposed_initializer=initializer_result))
        rows.append(dict(graph_role=label, graph=graph.to_payload(),
            old_complete_profile_id=old.profile.complete_profile_id,
            proposed_complete_profile_id=new.profile.complete_profile_id,
            positive_owner='admitted_zero_potential_control_only',
            proposed_owner=owner_result, proposed_crossing=crossing_result, roles=roles))

    paths = {Path(__file__).resolve(), predecessor_path,
        ROOT / 'src/pygrc/models/grc_v4_assets/grc-v4-a-initializer-schema.json'}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT) and '/.venv/' not in str(path) and path.suffix == '.py':
                paths.add(path)
    record = dict(schema='grcv4_atc_support_native_boundary_probe_v1', status='passed',
        interpretation='existing owners correctly reject a new unimplemented potential; bridge remains open',
        python=platform.python_version(), proposed_site_potential_id=PROPOSED_ID,
        support_certificate_digest=predecessor['record_digest'], fixtures=rows,
        native_multiwell_admissions=0, native_steps=0, native_events=0,
        production_changes=False, monkeypatches=False, scientific_acceptance=False,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes()))
                         for p in sorted(paths)])
    record['record_digest'] = sha(canonical(record))
    return record


if __name__ == '__main__':
    print(json.dumps(run(), separators=(',', ':'), ensure_ascii=True, allow_nan=False))

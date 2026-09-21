#!/usr/bin/env python3
"""Bounded V4-native information probe, not an event law or derivative claim.

Read two retained ATC-2 source fixtures, a homogeneous zero-current control,
and four charge-preserving perturbations each. No step, event or acceptance.
Stdout only; never overwrite the reviewed evidence.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
INV = ROOT / 'implementation/investigations/grc9v4-constitutive-design'
REFS = INV / 'evidence/autonomous-topology-change'
sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
from pygrc.models.grc_v4 import GRCV4
from pygrc.models.grc_v4_candidate_a import CandidateADifferentialReference
from pygrc.models.grc_v4_geometry import GeometryStageInputs


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run():
    pressure_path = REFS / 'ATC2PressureResults.json'
    pressure = json.loads(pressure_path.read_text())
    assert sha(canonical({k: v for k, v in pressure.items() if k != 'record_digest'})) == pressure['record_digest']
    # Refuse source drift before constructing a fresh experimental subject.
    for binding in pressure['source_bindings']:
        assert sha((ROOT / binding['path']).read_bytes()) == binding['sha256'], binding['path']
    helper_path = INV / 'scripts/verify_atc2_candidates.py'
    spec = importlib.util.spec_from_file_location('atc2_research_subject', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)  # no run() or unittest execution on import
    rows = []
    delta = F(1, 64)  # fixed experimental amplitude, not an accepted law constant
    for candidate, homogeneous_control in (('A', False), ('C', False), ('A', True)):
        source = next(c for c in pressure['evidence']['native_supplied_event_cases']
                      if c['candidate'] == candidate and c['law'] == 'merge')
        before = GeometryStageInputs.from_payload(source['source'])
        backend = None if source['backend'] is None else CandidateADifferentialReference.from_payload(source['backend'])
        if homogeneous_control:
            # Separate declared control, not a mutation/repair of the reviewed
            # source. Both roles and their shared charge are independently valid.
            before = replace(before, current=replace(before.current, C=(1., 1., 1.)),
                             reset=replace(before.reset, C=(1., 1., 1.)), Q_target=3.)
        graph = before.geometry.reference.graph
        assert graph.live_node_ids == ('a', 'b', 'c')
        owner = GRCV4(before, differential_reference=backend)
        snapshot = owner.snapshot()
        base = helper.native_read(before, backend)
        base_witness = helper.witness(base)
        if homogeneous_control:
            assert all(x == 0 for x in base_witness['J'])
        base_decision = helper.birth(graph, base_witness['H'])
        probes = []
        # Both neighbors of the unique degree-two vertex, both signs. Enumeration
        # is not a physical winner selection or a universal perturbation frame.
        for neighbor in (0, 2):
            for sign in (-1, 1):
                resources = list(before.current.C)
                resources[1] = float(F(resources[1]) + sign * delta)
                resources[neighbor] = float(F(resources[neighbor]) - sign * delta)
                assert sum(map(F, resources)) == sum(map(F, before.current.C))
                changed = replace(before, current=replace(before.current, C=tuple(resources)))
                assert changed.reset == before.reset
                assert changed.current.W_A == before.current.W_A
                assert changed.current.Z_4 == before.current.Z_4
                assert changed.geometry.reference == before.geometry.reference
                admitted = GRCV4(changed, differential_reference=backend)
                before_read = admitted.snapshot()
                point = helper.native_read(changed, backend)
                observed = helper.witness(point)
                difference = [str(F(x) - F(y)) for x, y in zip(observed['J'], base_witness['J'], strict=True)]
                assert any(F(x) != 0 for x in difference)
                assert observed['H'] == base_witness['H']
                decision = helper.birth(graph, observed['H'])
                assert decision == base_decision
                assert admitted.snapshot() == before_read
                assert owner.snapshot() == snapshot
                probes.append(dict(neighbor=graph.live_node_ids[neighbor], sign=sign,
                    amplitude=str(delta), resources=resources, witness=observed,
                    exact_represented_current_difference=difference,
                    source_admitted=True, birth_decision=decision,
                    publication_unchanged=True))
        if candidate == 'A':
            assert base_decision['outcome'] == 'no_event'
            assert all(base_witness['H'][i][j] == 0 for i in range(2) for j in range(2) if i != j)
        rows.append(dict(family=before.geometry.reference.profile.identity_payload.profile_family_id,
            source=before.to_payload(), backend=source['backend'], base_witness=base_witness,
            homogeneous_zero_current_control=homogeneous_control,
            base_birth_decision=base_decision, probes=probes,
            source_snapshot_digest=sha(canonical(snapshot)), publication_unchanged=True))

    # Typed authority boundaries, not raw-string promotion or new ATC nodes.
    side = INV / 'tools/exploratory-side-tool'
    sys.path.insert(0, str(side / 'tool/src'))
    from grcv4_explorer.a_initializer import load_current_forensic_context
    from grcv4_explorer.forensic import contract_provenance, debt_lifecycle
    context = load_current_forensic_context(ROOT, side)
    intake = json.loads((INV / 'evidence/autonomous-topology-change/ATCSourceIntake.json').read_text())
    assert sha(canonical(context.nodes)) == intake['forensic_context']['current_nodes_digest']
    assert sha(canonical(context.propagation_edges)) == intake['forensic_context']['propagation_edges_digest']
    traces = []
    for operation, query in (
        ('contract_provenance', {'contract_id': 'D11-C-EC-C-J0-DERIVATIVE'}),
        ('contract_provenance', {'contract_id': 'D10.2-EC-PARENT-CORE-STRUCTURAL-CHARGE-PROJECTOR'}),
        ('debt_lifecycle', {'debt_id': 'GTRS-RG-DEBT-C1-SECTION-REGULARITY'}),
    ):
        fn = {'contract_provenance': contract_provenance, 'debt_lifecycle': debt_lifecycle}[operation]
        traces.append(dict(operation=operation, query=query, result=fn(context, **query)))

    paths = {Path(__file__).resolve(), pressure_path, INV / 'evidence/autonomous-topology-change/ATCSourceIntake.json'}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(ROOT) and '/.venv/' not in str(path) and path.suffix == '.py':
                paths.add(path)
    paths.add(helper_path)
    for trace in traces:
        for row in trace['result']['rows']:
            paths.add(ROOT / row['source_ref']['path'])
    import numpy as np
    result = dict(schema='grcv4_atc_capability_information_probe_v1', status='passed',
        scientific_status='exploratory_information_availability_not_a_topology_law',
        predecessor_pressure_record_digest=pressure['record_digest'],
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        environment=dict(python=platform.python_version(), numpy=np.__version__),
        recipe=dict(current_resource_probe_amplitude=str(delta),
            fixed=['graph', 'reference', 'complete_profile', 'context', 'W_A', 'Z_4', 'reset', 'charge_target'],
            samples='both signs of center-to-neighbor charge redistribution on each retained three-node path',
            stage='unchanged_ATC_K0_native_present_read',
            values='represented finite differences, no limit or division claiming a derivative'),
        fixtures=rows, source_admissions=15, present_reads=15, finite_perturbations=12,
        evidence_ceiling='finite current response beyond Hodge-only score; also present at homogeneous zero-current control, hence not a refinement-necessity certificate',
        not_established=['refinement_necessity', 'missing_edge_necessity', 'generator_or_partition',
            'all_ten_applicability', 'RG_probe_admissibility', 'classical_derivative',
            'trigger_onset', 'native_ATC', 'scientific_acceptance'],
        ordinary_steps=0, topology_events=0, production_changes=False,
        forensic_queries=traces, forensic_graph_unchanged=True,
        source_bindings=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes())) for p in sorted(paths)])
    result['record_digest'] = sha(canonical(result))
    return result


if __name__ == '__main__':
    print(json.dumps(run(), separators=(',', ':'), ensure_ascii=True, allow_nan=False))

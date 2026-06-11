#!/usr/bin/env python3
"""Phase 3 Smoke Tests: Weighted Backend, Port Backend, Determinism, Stub Path."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from pygrc.core.storage import WeightedGraphBackend, PortGraphBackend
from pygrc.core.serialization import (
    snapshot_to_json,
    snapshot_from_json,
    save_snapshot,
    load_snapshot,
    restore_weighted_graph,
    restore_port_graph,
    export_weighted_topology,
    export_port_topology,
    build_snapshot_metadata,
    build_standard_snapshot,
)
from pygrc.core.digests import digest_snapshot
from pygrc.models._base import BaseFamilyStub
from pygrc.core import GRCParams, CapabilityProfile

PASS = 0
FAIL = 0

def test(name, condition, details=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  OK {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}")
        if details:
            print(f"     Detail: {details}")

print("\n1. Weighted Backend Smoke Tests")
print("-" * 40)
w = WeightedGraphBackend()

# add/remove nodes and edges
n1 = w.add_node({"label": "A"})
n2 = w.add_node({"label": "B"})
test("W-Add Nodes", len(tuple(w.iter_live_node_ids())) == 2, f"got {tuple(w.iter_live_node_ids())}")
e1 = w.add_edge(n1, n2, {"weight": 1.0, "label": "link"})
test("W-Add Edge", len(tuple(w.iter_live_edge_ids())) == 1, f"got {tuple(w.iter_live_edge_ids())}")
w.remove_node(n1)
test("W-Remove Node (cascade)", len(tuple(w.iter_live_node_ids())) == 1 and len(tuple(w.iter_live_edge_ids())) == 0)
n3 = w.add_node({"label": "C"})
n4 = w.add_node({"label": "D"})
e2 = w.add_edge(n3, n4, {"weight": 2.5})
# n2 is still alive, plus n3 and n4 = 3 nodes
test("W-Rebuild after cascade", len(tuple(w.iter_live_node_ids())) == 3, f"got {tuple(w.iter_live_node_ids())}")

# export topology
topo = export_weighted_topology(w)
test("W-Export Topology", isinstance(topo, dict) and "nodes" in topo and "edges" in topo)
test("W-Topo Node Count", len(topo["nodes"]) == 3, f"got {len(topo['nodes'])}")
test("W-Topo Edge Count", len(topo["edges"]) == 1)

# snapshot save/load
metadata = build_snapshot_metadata(
    model_family="weighted",
    step_index=0,
    params={},
    resolved_params={},
    params_hash="test",
    capabilities=set(),
    next_node_id=w.next_node_id,
    next_edge_id=w.next_edge_id,
)
snap = build_standard_snapshot(metadata=metadata, topology=topo)
json_str = snapshot_to_json(snap)
loaded_snap = snapshot_from_json(json_str)
test("W-Snapshot Roundtrip", loaded_snap["metadata"]["model_family"] == "weighted")
test("W-Snapshot Node Count", len(loaded_snap["topology"]["nodes"]) == 3, f"got {len(loaded_snap['topology']['nodes'])}")
test("W-Snapshot Edge Count", len(loaded_snap["topology"]["edges"]) == 1)

# restore backend from snapshot
w2 = restore_weighted_graph(loaded_snap["topology"], loaded_snap["metadata"])
test("W-Restore Node Count", len(tuple(w2.iter_live_node_ids())) == 3)
test("W-Restore Edge Count", len(tuple(w2.iter_live_edge_ids())) == 1)
test("W-Restore Payloads", w2.node_payload(n3) == {"label": "C"})

print("\n2. Port Backend Smoke Tests")
print("-" * 40)
p = PortGraphBackend()

# connect/rewire/remove edges
n10 = p.add_node({"label": "NodeX"})
e10 = p.connect_ports(n10, 0, n10, 1)
test("P-Connect Ports", len(tuple(p.iter_live_edge_ids())) == 1)
p.rewire_edge(e10, n10, 1, n10, 2)
test("P-Rewire Edge", len(tuple(p.iter_live_edge_ids())) == 1)
# After rewire: e10 connects (n10,1)->(n10,2). Slot 0 freed, slot 1 and 2 occupied.
test("P-Occupancy Invariant", not p.port_is_occupied(n10, 0) and p.port_is_occupied(n10, 1) and p.port_is_occupied(n10, 2))
p.remove_edge(e10)
test("P-Remove Edge", len(tuple(p.iter_live_edge_ids())) == 0)
test("P-Occupancy Cleared", not p.port_is_occupied(n10, 2))

# verify occupancy invariants
e11 = p.connect_ports(n10, 0, n10, 3)
test("P-Multi Connect", len(tuple(p.iter_live_edge_ids())) == 1)
e12 = p.connect_ports(n10, 1, n10, 4)
test("P-Second Connect", len(tuple(p.iter_live_edge_ids())) == 2)
occupied_count = sum(1 for s in range(9) if p.port_is_occupied(n10, s))
# Slots 0,1,3,4 occupied = 4
test("P-Occupancy Counts", occupied_count == 4, f"got {occupied_count}")

# export topology
p_topo = export_port_topology(p)
test("P-Export Topology", isinstance(p_topo, dict) and "nodes" in p_topo and "edges" in p_topo)
test("P-Topo Edge Count", len(p_topo["edges"]) == 2)
test("P-Topo Port Structure", "port_structure" in p_topo)

# snapshot save/load
metadata = build_snapshot_metadata(
    model_family="port",
    step_index=0,
    params={},
    resolved_params={},
    params_hash="test",
    capabilities=set(),
    next_node_id=p.next_node_id,
    next_edge_id=p.next_edge_id,
)
p_snap = build_standard_snapshot(metadata=metadata, topology=p_topo)
p_json = snapshot_to_json(p_snap)
p_loaded = snapshot_from_json(p_json)
test("P-Snapshot Roundtrip", len(p_loaded["topology"]["edges"]) == 2)
test("P-Snapshot Port Structure", "port_structure" in p_loaded["topology"])

# restore backend from snapshot
p2 = restore_port_graph(p_loaded["topology"], p_loaded["metadata"])
test("P-Restore Edge Count", len(tuple(p2.iter_live_edge_ids())) == 2)
p2_occupied = sum(1 for s in range(9) if p2.port_is_occupied(n10, s))
test("P-Restore Occupancy", p2_occupied == 4, f"got {p2_occupied}")

print("\n3. Determinism Smoke Tests")
print("-" * 40)
# same constructed graph -> identical snapshot_to_json
w_det = WeightedGraphBackend()
n_a = w_det.add_node({"a": 1})
n_b = w_det.add_node({"b": 2})
w_det.add_edge(n_a, n_b, {"w": 0.5})
topo_det = export_weighted_topology(w_det)
metadata_det = build_snapshot_metadata(
    model_family="weighted", step_index=0, params={}, resolved_params={},
    params_hash="test", capabilities=set(),
    next_node_id=w_det.next_node_id, next_edge_id=w_det.next_edge_id,
)
snap_det = build_standard_snapshot(metadata=metadata_det, topology=topo_det)
json1 = snapshot_to_json(snap_det)
json2 = snapshot_to_json(snap_det)
test("D-Identical Snapshots", json1 == json2)

# identical snapshot -> identical digest
d1 = digest_snapshot(json1)
d2 = digest_snapshot(json2)
test("D-Identical Digests", d1 == d2 and len(d1) == 64)

# cross-family determinism
p_det = PortGraphBackend()
n_c = p_det.add_node({"x": 1})
p_det.connect_ports(n_c, 0, n_c, 1)
p_topo_det = export_port_topology(p_det)
metadata_p_det = build_snapshot_metadata(
    model_family="port", step_index=0, params={}, resolved_params={},
    params_hash="test", capabilities=set(),
    next_node_id=p_det.next_node_id, next_edge_id=p_det.next_edge_id,
)
snap_p_det = build_standard_snapshot(metadata=metadata_p_det, topology=p_topo_det)
p_json_det = snapshot_to_json(snap_p_det)
p_json_det_2 = snapshot_to_json(snap_p_det)
test("D-Port Identical Snapshots", p_json_det == p_json_det_2)
test("D-Port Identical Digests", digest_snapshot(p_json_det) == digest_snapshot(p_json_det_2))

print("\n4. Stub Path Smoke Tests")
print("-" * 40)

# BaseFamilyStub requires CAPABILITY_PROFILE. Create a minimal test profile.
_TEST_CAP_PROFILE = CapabilityProfile(
    family="BASE",
    required=frozenset(),
    optional=frozenset(),
    forbidden=frozenset(),
)

class TestStub(BaseFamilyStub):
    MODEL_FAMILY = "BASE"
    CAPABILITY_PROFILE = _TEST_CAP_PROFILE

stub = TestStub(params=GRCParams.from_mapping({"dt": 0.1, "k": 1}), state=None)

# stub save() / load() through the shared serializer
with tempfile.TemporaryDirectory() as tmpdir:
    fpath = Path(tmpdir) / "stub_snap.json"
    stub.save(str(fpath))
    test("Stub-File Created", fpath.exists())
    
    loaded_stub = TestStub.load(str(fpath))
    test("Stub-Load Success", isinstance(loaded_stub, TestStub))
    test("Stub-Params Match", dict(loaded_stub.get_params().raw_config) == {"dt": 0.1, "k": 1})
    test("Stub-Family Match", loaded_stub.MODEL_FAMILY == "BASE")
    
    # Verify state was preserved
    test("Stub-State StepIndex Match", loaded_stub.get_state().step_index == stub.get_state().step_index)

print("\n" + "=" * 40)
print(f"Results: {PASS} passed, {FAIL} failed")
if FAIL > 0:
    sys.exit(1)
else:
    print("All smoke tests passed. OK")

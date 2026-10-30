"""Native represented-flow diagnostics from one fresh, bound realization read.

The pure wire validator proves graph/operand consistency, not native freshness.
Only capture() obtains operands from admitted C/W/Z. Diagnostics never feed a
writer, spark predicate, admission threshold or physical identity transport.
"""

from dataclasses import dataclass, replace
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from importlib.resources import files
import json
import math

from .grc_9_v4_identity import POLICY_ID, has_basin
from .grc_9_v4_topology import GRC9V4PostbeatRows
from .grc_v4_codec import RELEASE_ID, canonical_json_bytes
from .grc_v4_state import FrozenJSONMap

SCHEMA = "grc9v4-basin-observation-v1"
EVALUATOR = "grc9v4-native-fresh-basin-capture-v1"
_SCHEMA_SHA = "24ec17bdbaa289d4e3b7a83621f641026481da7e39d1d2fc0f798a78a940d591"


def digest(value):
    return sha256(canonical_json_bytes(value)).hexdigest()


@lru_cache(maxsize=4)
def _validator(kind):
    from jsonschema import Draft202012Validator

    raw = (
        files("pygrc.models.grc_v4_assets")
        .joinpath("grc-9-v4-basin-interface-schema.json")
        .read_bytes()
    )
    if sha256(raw).hexdigest() != _SCHEMA_SHA:
        raise ValueError("basin schema asset differs from accepted contract")
    schema = json.loads(raw)
    return Draft202012Validator({"$ref": "#/$defs/" + kind, "$defs": schema["$defs"]})


def typed_node(node):
    if type(node) not in (int, str) or (type(node) is int and abs(node) > 2**53 - 1):
        raise ValueError("normalized int/string node required")
    if type(node) is str:
        node.encode("utf-8")
    return {"kind": "int" if type(node) is int else "str", "value": node}


def node_key(node):
    # JCS key ordering is fixed by these ASCII field names; compare UTF-8 bytes.
    return (0 if type(node) is int else 1, canonical_json_bytes(typed_node(node)))


def _node(value):
    node = value["value"]
    if typed_node(node) != value:
        raise ValueError("typed node identity mismatch")
    return node


def hex_number(value):
    if type(value) is not str:
        raise ValueError("lossless binary64 hex required")
    number = float.fromhex(value)
    if not math.isfinite(number) or number.hex() != value:
        raise ValueError("finite canonical binary64 hex required")
    return number


def _hex(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("nonfinite native basin operand")
    return value.hex()


def _classification(witness, graph_digest):
    """Iterative SCC/terminal propagation, without strongest-edge selection."""
    vertices = [_node(row["node"]) for row in witness["rows"]]
    if len(set(vertices)) != len(vertices) or vertices != sorted(
        vertices, key=node_key
    ):
        raise ValueError("duplicate or noncanonical witness node order")
    adjacency = {v: set() for v in vertices}
    reverse = {v: set() for v in vertices}
    edge_ids = set()
    for edge in witness["edges"]:
        u, v = _node(edge["tail"]), _node(edge["head"])
        if edge["edge_id"] in edge_ids or u not in adjacency or v not in adjacency:
            raise ValueError("duplicate edge or missing endpoint")
        edge_ids.add(edge["edge_id"])
        current = hex_number(edge["current"])
        if current < 0:
            u, v = v, u
        if current != 0:
            adjacency[u].add(v)
            reverse[v].add(u)
    seen, order = set(), []
    for start in vertices:
        stack = [(start, False)]
        while stack:
            v, exiting = stack.pop()
            if exiting:
                order.append(v)
            elif v not in seen:
                seen.add(v)
                stack.append((v, True))
                stack.extend((w, False) for w in adjacency[v] if w not in seen)
    owner, components = {}, []
    for start in reversed(order):
        if start in owner:
            continue
        pending, members = [start], set()
        while pending:
            v = pending.pop()
            if v in members or v in owner:
                continue
            members.add(v)
            pending.extend(reverse[v])
        members = tuple(sorted(members, key=node_key))
        components.append(members)
        owner.update((v, members) for v in members)
    components.sort(key=lambda s: tuple(map(node_key, s)))
    indices = {s: i for i, s in enumerate(components)}
    own = {v: indices[owner[v]] for v in vertices}
    outgoing = [set() for _ in components]
    incoming = [set() for _ in components]
    for u in vertices:
        for v in adjacency[u]:
            if own[u] != own[v]:
                outgoing[own[u]].add(own[v])
                incoming[own[v]].add(own[u])
    cyclic = [len(s) > 1 or s[0] in adjacency[s[0]] for s in components]
    kinds = [
        None
        if outgoing[i]
        else "recirculating"
        if cyclic[i]
        else "sink"
        if incoming[i]
        else "quiescent"
        for i in range(len(components))
    ]
    targets = [{i} if not outgoing[i] else set() for i in range(len(components))]
    counts = [len(s) for s in outgoing]
    ready = [i for i, count in enumerate(counts) if not count]
    while ready:
        i = ready.pop()
        for parent in incoming[i]:
            targets[parent].update(targets[i])
            counts[parent] -= 1
            if not counts[parent]:
                ready.append(parent)
    gradient_tolerance = hex_number(witness["gradient_tolerance"])
    hessian_tolerance = hex_number(witness["hessian_tolerance"])
    if gradient_tolerance <= 0 or hessian_tolerance <= 0:
        raise ValueError("strictly positive seed thresholds required")
    nodes, regions = [], {}
    for v, row in zip(vertices, witness["rows"], strict=True):
        gradient = tuple(map(hex_number, row["gradient"]))
        diagonal = tuple(map(hex_number, row["signed_hessian_diagonal"]))
        tuple(map(hex_number, row["row_net_flux"]))
        if any(d != witness["hessian_sign"] * g for d, g in zip(diagonal, gradient)):
            raise ValueError("signed Hessian differs from fixed-row diagonal")
        seed = (
            sum(Fraction(x) ** 2 for x in gradient) < Fraction(gradient_tolerance) ** 2
            and min(diagonal) > hessian_tolerance
        )
        terminal = sorted(targets[own[v]])
        status = "ambiguous" if len(terminal) > 1 else kinds[terminal[0]]
        sink = components[terminal[0]][0] if status == "sink" else None
        label = (
            None
            if sink is None
            else "grc9v4-flow-basin-sha256:"
            + digest(
                dict(
                    policy_id=POLICY_ID,
                    graph_digest=graph_digest,
                    sink_node_id=typed_node(sink),
                )
            )
        )
        nodes.append(
            dict(
                node=typed_node(v),
                component_ref=own[v],
                reachable_terminals=terminal,
                status=status,
                assigned_sink=None if sink is None else typed_node(sink),
                basin_id=label,
                seed=seed,
            )
        )
        if sink is not None:
            region = regions.setdefault(
                sink,
                dict(
                    sink_node_id=typed_node(sink),
                    basin_id=label,
                    members=[],
                    seed_members=[],
                ),
            )
            region["members"].append(typed_node(v))
            if seed:
                region["seed_members"].append(typed_node(v))
    return dict(
        components=[
            dict(
                component_ref=i,
                members=list(map(typed_node, s)),
                cyclic=cyclic[i],
                is_terminal=not outgoing[i],
                terminal_kind=kinds[i],
            )
            for i, s in enumerate(components)
        ],
        nodes=nodes,
        regions=[regions[v] for v in sorted(regions, key=node_key)],
    )


def observation(binding, witness):
    """Pure construction from declared operands; never a native read/admission."""
    binding, witness = (
        FrozenJSONMap(binding).to_dict(),
        FrozenJSONMap(witness).to_dict(),
    )
    _validator("binding").validate(binding)
    _validator("witness").validate(witness)
    core = dict(
        schema_version=SCHEMA,
        policy_id=POLICY_ID,
        binding=binding,
        operand_digest=digest(witness),
    )
    return {
        **core,
        "observation_digest": digest(core),
        "witness": witness,
        **_classification(witness, binding["graph_digest"]),
    }


def validate_observation(value, graph, *, binding=None, witness=None):
    """Closed shape, exact graph coverage and semantic recomputation.

    Supplying an authenticated binding/witness additionally checks native
    provenance. A standalone graph-consistent record does not prove freshness.
    """
    value = FrozenJSONMap(value).to_dict()
    _validator("observation").validate(value)
    supplied = value["witness"]
    expected_edges = [
        (e.edge_id, typed_node(e.tail.node_id), typed_node(e.head.node_id))
        for e in graph.edges
    ]
    actual_edges = [(e["edge_id"], e["tail"], e["head"]) for e in supplied["edges"]]
    if actual_edges != expected_edges or [r["node"] for r in supplied["rows"]] != [
        typed_node(v) for v in sorted(graph.live_node_ids, key=node_key)
    ]:
        raise ValueError("incomplete or reordered basin graph coverage")
    if (
        value["binding"]["graph_digest"] != graph.graph_digest
        or value["binding"]["orientation_identity"] != graph.orientation_identity
    ):
        raise ValueError("basin graph/orientation binding mismatch")
    if binding is not None and value["binding"] != binding:
        raise ValueError("basin capture/state/role binding mismatch")
    if witness is not None and supplied != witness:
        raise ValueError("basin witness differs from fresh captured native read")
    if value != observation(value["binding"], supplied):
        raise ValueError("basin digests or derived collections differ from operands")
    return FrozenJSONMap(value)


def identity_projection(value):
    return [
        dict(node=n["node"], basin_id=n["basin_id"])
        for n in value["nodes"]
        if n["basin_id"] is not None
    ]


@dataclass(frozen=True, slots=True)
class _Capture:
    inputs: object
    read: object
    point: object
    charge: object
    rows: GRC9V4PostbeatRows
    summaries: tuple
    observation: FrozenJSONMap


def _read_once(inputs, backend):
    identity = inputs.geometry.reference.profile.identity_payload
    realization = identity.realization
    if realization == "OS":
        if identity.candidate == "A":
            from .grc_v4_candidate_a import CandidateACurrent

            read = point = CandidateACurrent(inputs, backend)
        else:
            from .grc_v4_candidate_c import CandidateCCurrent

            read = point = CandidateCCurrent(inputs)
    elif realization in ("CI", "CI+PC"):
        from .grc_v4_ci import CandidateCIRoot

        read = CandidateCIRoot(inputs, backend)
        point = read.selected.point
    elif realization == "PC":
        from .grc_v4_pc import CandidatePCRead

        read = CandidatePCRead(inputs, backend)
        point = read.point
    else:
        raise ValueError("basin native capture is outside selected execution scope")
    return read, point


def capture(state, role):
    """One direct fresh native read for this role; no ordinary writer is run."""
    from . import grc_v4_lifecycle as generic
    from .grc_9_v4_lifecycle import family_implementation
    from .grc_v4_geometry import VertexScalar
    from .grc_v4_certification import current_numerical_policy
    from .grc_v4_exact import current_exact_backend

    if not has_basin(state.specialization) or state.FAMILY not in (
        "C_OS",
        "C_CI",
        "A_CI",
        "A_PC",
        "A_OS",
        "C_PC",
        "C_CI_PC",
    ):
        raise ValueError("explicit supported basin successor required")
    if role not in ("current", "reset"):
        raise ValueError("explicit basin role required")
    authority = getattr(state.inputs, role)
    inputs = generic._fresh_geometry(
        replace(
            state.inputs,
            current=authority,
            reset=authority,
            dt=0.0,
            stage="pre_read",
            evaluation_index=0,
            trial_current=None,
        )
    )
    ref = inputs.geometry.reference
    charge = generic._resource_charge(
        inputs, VertexScalar(ref.graph, authority.C), "admission"
    )
    read, point = _read_once(
        inputs, family_implementation(state).differential_backend(state)
    )
    # A substituted old current/root cannot pass merely because J happens to agree.
    if read.inputs != inputs or point.inputs.current != authority:
        raise ValueError("native basin read does not belong to captured role inputs")
    root = dict(
        recipe=point.to_payload(),
        current=list(map(_hex, point.current.values)),
        H1_form=[
            [_hex(x) for x in r] for r in point.inputs.geometry.one_form_hodge.matrix
        ],
    )
    certificate = None
    if ref.profile.identity_payload.realization in ("CI", "CI+PC"):
        selected = read.selected
        if (
            selected.point is not point
            or selected.inputs != point.inputs
            or selected.inputs.trial_current != point.current
        ):
            raise ValueError("inconsistent joint CI root capture")
        root.update(
            recipe=read.to_payload(),
            evaluations=read.evaluations,
            selected_inputs=selected.inputs.to_payload(),
            generated_H1=[
                [_hex(x) for x in r] for r in selected.generated.one_form_hodge.matrix
            ],
            residual_squared=str(selected.residual_squared),
            certificate=read.certificate.bounds.to_dict(),
        )
        certificate = "grc9v4-basin-joint-root-sha256:" + digest(root)
    elif ref.profile.identity_payload.realization == "PC":
        root["certificate"] = read.certificate.bounds.to_dict()
        certificate = "grc9v4-basin-pc-read-sha256:" + digest(root)
    rows = GRC9V4PostbeatRows(
        ref.graph.port_graph,
        ref.profile,
        authority,
        point.current.values,
        inputs.step_index,
        state.specialization.identity_payload["hessian_sign"],
    )
    summaries = rows.evaluate()
    spark = state.specialization.resolved["spark"]
    witness = dict(
        edges=[
            dict(
                edge_id=e.edge_id,
                tail=typed_node(e.tail.node_id),
                head=typed_node(e.head.node_id),
                current=_hex(j),
            )
            for e, j in zip(rows.port_graph.edges, point.current.values, strict=True)
        ],
        rows=[
            dict(
                node=typed_node(r.node_id),
                gradient=list(map(_hex, r.gradient)),
                signed_hessian_diagonal=[
                    _hex(r.signed_hessian[i][i]) for i in range(3)
                ],
                row_net_flux=list(map(_hex, r.net_flux)),
            )
            for r in sorted(summaries, key=lambda r: node_key(r.node_id))
        ],
        gradient_tolerance=_hex(spark["gradient_tolerance"]),
        hessian_tolerance=_hex(spark["basin_hessian_tolerance"]),
        hessian_sign=rows.hessian_sign,
    )
    binding = dict(
        role=role,
        role_state_digest=digest(
            state.scientific_payload if role == "current" else state.reset_payload
        ),
        profile_id=ref.profile.complete_profile_id,
        model_identity=state.model_identity,
        graph_digest=ref.graph.graph_digest,
        orientation_identity=ref.graph.orientation_identity,
        context_contract_id=inputs.context.contract_id,
        context_value_digest=digest(inputs.context.value.to_dict()),
        numerical_policy_id=current_numerical_policy().value,
        scalar_backend_id=current_exact_backend().value,
        evaluator_id=EVALUATOR,
        release_id=RELEASE_ID,
        stage="fresh_poststate_readmission",
        root_certificate_binding=certificate,
        read_identity="grc9v4-basin-read-sha256:" + digest(root),
    )
    value = validate_observation(
        observation(binding, witness), rows.port_graph, binding=binding, witness=witness
    )
    return _Capture(inputs, read, point, charge, rows, summaries, value)


def capture_pair(state):
    return capture(state, "current"), capture(state, "reset")


def checkpoint_extension(pair, mode):
    if mode not in ("state_only", "exact_observation"):
        raise ValueError("explicit basin replay mode required")
    value = dict(
        schema_version="grc9v4-basin-checkpoint-extension-v1",
        policy_id=POLICY_ID,
        replay_mode=mode,
        current_observation=None,
        reset_observation=None,
    )
    if mode == "exact_observation":
        for role, captured in zip(("current", "reset"), pair, strict=True):
            value[role + "_observation"] = captured.observation.to_dict()
    _validator("checkpoint_extension").validate(value)
    return value


def validate_checkpoint(value, pair, graph):
    value = FrozenJSONMap(value).to_dict()
    _validator("checkpoint_extension").validate(value)
    if value["replay_mode"] == "exact_observation":
        for role, captured in zip(("current", "reset"), pair, strict=True):
            expected = captured.observation.to_dict()
            validate_observation(
                value[role + "_observation"],
                graph,
                binding=expected["binding"],
                witness=expected["witness"],
            )
    return value["replay_mode"]

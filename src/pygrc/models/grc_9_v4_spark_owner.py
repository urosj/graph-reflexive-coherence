"""Pure native spark preparation and the public owner's atomic publication.

An accounting scope is one process-local publication authority shared by forks
and restored checkpoints. Its immutable root owns branches, occurrence claims
and canonical child registrations together. The locator below carries no gain
counter. Cross-process/global uniqueness requires an external accounting owner
and is not claimed. Checkpoint replay validates mathematics without live credit.
"""

from dataclasses import dataclass, replace
from threading import RLock
from uuid import uuid4

from .grc_9_v4_completion import classify, descendants
from .grc_9_v4_completion_certificate import CompletionCertificate
from .grc_9_v4_completion_codec import digest, node, validate
from .grc_9_v4_spark_contracts import (
    GRC9V4SparkConfiguration,
    SparkReceipt,
    SparkReference,
    SparkResult,
)
from .grc_v4_codec import payload_identity
from .grc_v4_exact import ExactBackend
from .grc_v4_geometry import GRCV4Graph
from .grc_v4_spark import quartic_kernel
from .grc_v4_spark_carrier import exact_state, carrier_pairs
from .grc_v4_spark_state import (
    flint_operation,
    rational,
)
from .grc_v4_state import FrozenJSONMap


@dataclass(frozen=True, slots=True)
class CompletionPublication:
    event: FrozenJSONMap | None = None
    certificates: tuple = ()
    observations: tuple = ()
    evidence: FrozenJSONMap | None = None
    objects: tuple = ()
    reason: str = "no committed event"

    def to_payload(self):
        return {
            "event": None if self.event is None else self.event.to_dict(),
            "certificates": [c.to_payload() for c in self.certificates],
            "observations": [o.to_dict() for o in self.observations],
            "evidence": None if self.evidence is None else self.evidence.to_dict(),
            "objects": [o.to_dict() for o in self.objects],
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class ScopePublication:
    branches: tuple = ()
    claims: tuple = ()
    children: tuple = ()
    admitted: tuple = ()


class AccountingScope:
    def __init__(self, origin, initial):
        self.origin = origin
        self.initial = FrozenJSONMap(initial)
        self.lock = RLock()
        self.published = ScopePublication()


_SCOPES = {}
_SCOPES_LOCK = RLock()


def enabled(owner):
    return getattr(owner, "_spark_scope", None) is not None


def kernel(config):
    return quartic_kernel(config.reference.graph, config.reference.profile)


def admit(config):
    k = kernel(config)
    k.readmission(config.current)
    k.readmission(config.reset)


def initialize(owner, config, *, origin=None, register=True):
    from .grc_9_v4_crossing import _Publication

    if type(config) is not GRC9V4SparkConfiguration:
        raise TypeError("exact v3 configuration required")
    admit(config)
    scope = AccountingScope(origin or uuid4().hex, config.to_payload())
    owner._spark_scope, owner._spark_branch = scope, uuid4().hex
    owner._lock = scope.lock
    owner._backend, owner._policy = ExactBackend.FLINT, config.reference.profile.NUMERICS
    owner._initial = config.to_payload()
    p = _Publication(
        "enabled_spark_v4",
        config,
        config.reference,
        config.specialization,
        completion=CompletionPublication(),
    )
    scope.published = ScopePublication(
        branches=((owner._spark_branch, p),), admitted=((publication_id(p), p),)
    )
    if register:
        with _SCOPES_LOCK:
            if scope.origin in _SCOPES:
                raise ValueError("accounting origin already exists")
            _SCOPES[scope.origin] = scope
    return owner


def endpoints(p):
    config = p.owner
    return {
        "state_digest": config.scientific_digest,
        "reset_digest": "grcv4-reset-sha256:" + digest(config.reset.to_payload()),
        "authoritative_digest": "grcv4-authoritative-sha256:"
        + digest(config.current.to_payload()),
        "model_identity": config.model_identity,
        "graph_digest": config.reference.graph.graph_digest,
    }


def publication_payload(p):
    return {
        "configuration": p.owner.to_payload(),
        "completion": p.completion.to_payload(),
        "receipts": [r.to_payload() for r in p.receipts],
        "journal": [x.to_dict() for x in p.journal],
    }


def publication_id(p):
    return digest(publication_payload(p))


def _receipt(before, after, action, kind="operation", evidence=None):
    return SparkReceipt(
        FrozenJSONMap(
            {
                "schema_version": "grc9v4-native-spark-receipt-v1",
                "kind": kind,
                "source": before.owner.scientific_digest,
                "target": after.owner.scientific_digest,
                "parent": None
                if not before.receipts
                else before.receipts[-1].receipt_id,
                "action": action,
                "evidence": evidence,
            }
        )
    )


def _put(objects, value):
    ref = {
        "path": "implementation/native-spark/objects/" + digest(value) + ".json",
        "sha256": digest(value),
    }
    row = FrozenJSONMap({"reference": ref, "value": value})
    if row not in objects:
        objects.append(row)
    return ref


def _capture(payload):
    return exact_state(payload)


def _curve_membership(certificate,state):
    from .grc_9_v4_completion_crg2b import membership_details
    value=membership_details(certificate,state)
    return {'membership_measure':'squared_curve_P_distance_over_radius_squared',
        'curve_parameter':value['parameter'],'parameter_selection':value['method']}


def progress(owner, before, after, receipt, step):
    cp, config = after.completion, after.owner
    if cp.event is None or config.policy is None or cp.evidence is not None:
        return after, 0
    event = cp.event.to_dict()
    if event["occurrence"] in {
        c["occurrence"] for c in owner._spark_scope.published.claims
    }:
        return replace(
            after,
            completion=replace(
                cp, observations=(), reason="occurrence already consumed"
            ),
        ), 0
    cert = next(
        (c for c in cp.certificates if c.operands["binding"]["role"] == "current"), None
    )
    if cert is None:
        return replace(
            after,
            completion=replace(
                cp, observations=(), reason="no admitted current certificate"
            ),
        ), 0
    cert.require_binding(
        kernel(config), config.policy, "current", config.current.charge
    )
    member, norm = cert.membership(config.current)
    if not member:
        return replace(
            after,
            completion=replace(
                cp, observations=(), reason="outside certificate domain"
            ),
        ), 0
    source = classify(_capture(event["source"]), config.policy)
    target = classify(config.current, config.policy)
    match = descendants(source, event["expanded"], event["module"], target)
    if match["local_gain"] < 1 or not match["new_anchors"]:
        return replace(
            after,
            completion=replace(
                cp, observations=(), reason="no additional geometric child"
            ),
        ), 0
    roster = [
        {"anchor": node(a), "members": [node(x) for x in b]}
        for a, b in match["children"]
    ]
    objects = list(cp.objects)
    obs = {
        "role": "current",
        "receipt": _put(objects, receipt.to_payload()),
        "step_index": config.step_index,
        "time": config.time,
        "duration": step.duration,
        "state": _put(objects, config.current.to_payload()),
        "read": _put(
            objects,
            {
                "final_current": list(step.final_current),
                "reference_current": list(step.reference_current),
            },
        ),
        "operands": _put(objects, cert.operands.to_dict()),
        "diagnostic_certificate": _put(
            objects,
            {
                "membership_norm": norm,
                **(_curve_membership(cert,config.current) if config.reference.profile.FAMILY == "C_RG2b" else {}),
                **({"membership_measure": "squared_max_C_logW_carrier_product_upper"} if config.reference.profile.FAMILY in ("A_PC", "A_CI_PC") else {}),
                **({"membership_measure": "squared_max_product_norm"} if config.reference.profile.FAMILY in ("C_PC", "C_CI_PC") else {}),
                **({"membership_measure": "outward_C_logW_chart_infinity_upper"} if config.reference.profile.FAMILY in ("A_OS", "A_CI") else {}),
                "actual": target.to_payload(),
                "arithmetic_error": "0",
            },
        ),
        "descendants": roster,
    }
    observations = cp.observations
    if observations and (
        observations[-1]["step_index"] + 1 != config.step_index
        or rational(config.time) - rational(observations[-1]["time"])
        != rational(step.duration)
        or observations[-1]["descendants"] != FrozenJSONMap(obs)["descendants"]
    ):
        observations = ()
    observations += (FrozenJSONMap(obs),)
    elapsed = rational(config.time) - rational(observations[0]["time"])
    if len(observations) - 1 < config.policy.minimum_beats or elapsed < rational(
        config.policy.minimum_elapsed
    ):
        return replace(
            after,
            completion=replace(
                cp,
                observations=observations,
                objects=tuple(objects),
                reason="positive window pending",
            ),
        ), 0
    proof = cert.proof.to_dict()
    evidence = {
        "schema_version": "grc9v4-child-completion-evidence-v2",
        "policy_digest": config.policy.policy_digest,
        "event_lineage_id": event["occurrence"],
        "decision": "completed",
        "source_capture": _put(objects, event["source_capture"]),
        "event_receipt": _put(objects, event["receipt"]),
        "parent": {
            "anchor": node(match["parent_anchor"]),
            "members": [node(x) for x in match["parent"]],
        },
        "expanded_vertex": node(event["expanded"]),
        "target_profile_id": config.reference.profile.complete_profile_id,
        "target_graph_id": config.reference.graph.graph_digest,
        "lineage": _put(objects, event),
        "proof": {
            "certificate": _put(objects, cert.to_payload()),
            "equation_binding": _put(objects, cert.operands["binding"].to_dict()),
            "state_channels": list(cert.operands["binding"]["state_channels"]),
            "constraints": _put(objects, {"charge": config.current.charge}),
            "domain": _put(
                objects,
                {k: v for k, v in cert.operands.to_dict().items() if k in ("S", "U", "carrier_radius", "carrier_pairs", "carrier_center", "logW_center", "curve", "radius", "parameter_decay", "subdivision_depth")},
            ),
            "center": _put(objects, ({"C": list(cert.operands["center"]), "logW": list(cert.operands["logW_center"]), "Z_4": [list(r) for r in cert.operands["carrier_center"]]} if config.reference.profile.FAMILY in ("A_PC", "A_CI_PC") else {"C": list(cert.operands["center"]), "logW": list(cert.operands["logW_center"])} if config.reference.profile.FAMILY in ("A_OS", "A_CI") else {"C": list(cert.operands["center"]), "Z_4": cert.operands.to_dict()["carrier_center"]} if config.reference.profile.FAMILY in ("C_PC", "C_CI_PC") else list(cert.operands["center"]))),
            "norm_id": ("full_charge_tangent_curve_P_metric_v1" if config.reference.profile.FAMILY == "C_RG2b" else "full_C_logW_chart_scaled_carrier_frobenius_v1" if config.reference.profile.FAMILY in ("A_PC", "A_CI_PC") else "full_C_logW_chart_infinity_v1" if config.reference.profile.FAMILY in ("A_OS", "A_CI") else "full_charge_chart_scaled_carrier_frobenius_v1" if config.reference.profile.FAMILY in ("C_PC", "C_CI_PC") else "full_charge_chart_infinity_v1"),
            "q": proof["q"],
            "image_margin": proof["image_margin"],
            "numerical_policy_id": config.reference.profile.NUMERICS,
            "full_step_error": proof["full_step_error"],
            "full_step_certificate": _put(objects, proof),
            "constraint_certificate": _put(
                objects,
                {
                    "exact_charge_preserved": True,
                    "method": "incidence_column_sums_zero",
                },
            ),
            "diagnostic_certificate": _put(objects, proof["geometry"]),
        },
        "observations": [o.to_dict() for o in observations],
        "local_gain": match["local_gain"],
        "new_child_anchors": [node(x) for x in match["new_anchors"]],
    }
    validate(evidence)
    cp = replace(
        cp,
        observations=observations,
        evidence=FrozenJSONMap(evidence),
        objects=tuple(objects),
        reason="completed",
    )
    return replace(after, completion=cp), match["local_gain"]


def publish(owner, before, after, emitted, action):
    """Called only by the existing public owner's _publish transaction boundary."""
    scope, root = owner._spark_scope, owner._spark_scope.published
    if owner._published is not before or not emitted:
        raise RuntimeError("stale or empty native publication")
    ids = [r.receipt_id for r in before.receipts + emitted]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate receipt")
    for r in emitted:
        p = r.identity_payload
        if (
            p["source"] != before.owner.scientific_digest
            or p["target"] != after.owner.scientific_digest
            or p["parent"]
            != (None if not before.receipts else before.receipts[-1].receipt_id)
        ):
            raise ValueError("native receipt endpoints/ancestry mismatch")
    following = replace(
        after,
        receipts=before.receipts + emitted,
        journal=before.journal + (FrozenJSONMap(action),),
    )
    claims, children = root.claims, root.children
    evidence = after.completion.evidence
    if evidence is not None and before.completion.evidence is None:
        occurrence = evidence["event_lineage_id"]
        if occurrence in {c["occurrence"] for c in claims}:
            raise ValueError("occurrence already consumed at publication")
        if len(emitted) != 2 or emitted[-1].identity_payload["kind"] != "completion":
            raise ValueError("completion requires its atomic receipt")
        claim = FrozenJSONMap(
            {
                "occurrence": occurrence,
                "evidence_digest": digest(evidence.to_dict()),
                "receipt": emitted[-1].to_payload(),
                "local_gain": evidence["local_gain"],
                "objects": [o.to_dict() for o in after.completion.objects],
            }
        )
        claims += (claim,)
        children += tuple(
            FrozenJSONMap(
                {
                    "occurrence": occurrence,
                    "anchor": a.to_dict(),
                    "completion_receipt": emitted[-1].receipt_id,
                }
            )
            for a in evidence["new_child_anchors"]
        )
    branches = tuple(
        (key, following if key == owner._spark_branch else p)
        for key, p in root.branches
    )
    # All expensive verification, evidence validation and prospective records
    # precede this single assignment. A late failure leaves all branches intact.
    scope.published = ScopePublication(
        branches,
        claims,
        children,
        root.admitted + ((publication_id(following), following),),
    )


@flint_operation
def transact(owner, action):
    with owner._lock:
        before = owner._published
        try:
            # Explicit delivery IDs identify an operation in this branch's
            # successful ancestry. Failed attempts remain retryable. Ordinary
            # step() calls have no delivery ID and represent new physical beats.
            operation_id = _operation_id(action)
            if operation_id is not None and any(
                _operation_id(previous) == operation_id for previous in before.journal
            ):
                raise ValueError("operation id already committed in this branch")
            after, step = prepare(owner, before, action)
            receipt = _receipt(before, after, action)
            gain = 0
            if step is not None:
                after, gain = progress(owner, before, after, receipt, step)
            if action["kind"] == "expand":
                event = after.completion.event.to_dict()
                event["receipt"] = receipt.to_payload()
                event["occurrence"] = digest(
                    {
                        "origin": owner._spark_scope.origin,
                        "receipt": receipt.receipt_id,
                        "ancestry": [r.receipt_id for r in before.receipts],
                    }
                )
                after = replace(
                    after,
                    completion=replace(after.completion, event=FrozenJSONMap(event)),
                )
            emitted = (receipt,)
            if gain:
                emitted += (
                    _receipt(
                        before,
                        after,
                        action,
                        "completion",
                        after.completion.evidence.to_dict(),
                    ),
                )
            owner._publish(before, after, emitted, action)
            return SparkResult(True, emitted, local_gain=gain)
        except (ValueError, TypeError, ArithmeticError, RuntimeError) as error:
            return SparkResult(False, reason=str(error))


def _operation_id(action):
    if action.get("kind") == "expand":
        return action["request"].get("operation_id")
    return action.get("operation_id")


def _invalidate(cp, reason, *, certificates=False):
    return CompletionPublication(
        certificates=() if certificates else cp.certificates, reason=reason
    )


def prepare(owner, before, action):
    config, cp = before.owner, before.completion
    kind = action["kind"]
    step = None
    if kind == "step":
        if (
            set(action)
            not in ({"kind", "duration"}, {"kind", "duration", "operation_id"})
            or rational(action["duration"]) <= 0
        ):
            raise ValueError(
                "positive ordinary duration required; inspection earns no time"
            )
        if "operation_id" in action and (
            type(action["operation_id"]) is not str or not action["operation_id"]
        ):
            raise ValueError("nonempty operation id required")
        step = kernel(config).step(config.current, action["duration"])
        config = replace(
            config,
            current=step.after,
            step_index=config.step_index + 1,
            time=str(rational(config.time) + rational(step.duration)),
        )
    elif kind in ("reset", "rebase"):
        if set(action) != {"kind"}:
            raise ValueError("closed reset/rebase action required")
        config = (
            replace(config, current=config.reset, step_index=0, time="0")
            if kind == "reset"
            else replace(config, reset=config.current)
        )
        admit(config)
        cp = _invalidate(cp, kind + " invalidated event window")
    elif kind == "certificates":
        if set(action) != {"kind", "certificates"} or config.policy is None:
            raise ValueError("explicit active policy and certificate pair required")
        certificates = tuple(
            CompletionCertificate.from_payload(c) for c in action["certificates"]
        )
        if tuple(c.operands["binding"]["role"] for c in certificates) != (
            "current",
            "reset",
        ):
            raise ValueError("ordered current/reset certificate pair required")
        for role, cert in zip(("current", "reset"), certificates):
            cert.require_binding(
                kernel(config), config.policy, role, getattr(config, role).charge
            )
        cp = replace(
            cp,
            certificates=certificates,
            observations=(),
            objects=() if cp.evidence is None else cp.objects,
            reason="certificate replacement restarted window",
        )
    elif kind == "migrate":
        if set(action) != {"kind", "configuration"}:
            raise ValueError("closed exact migration required")
        target = GRC9V4SparkConfiguration.from_payload(action["configuration"])
        if (
            target.current != config.current
            or target.reset != config.reset
            or (target.step_index, target.time) != (config.step_index, config.time)
        ):
            raise ValueError(
                "migration cannot replace resources, topology, reset or clock"
            )
        admit(target)
        config, cp = (
            target,
            _invalidate(
                cp,
                "profile/policy/reference migration invalidated event",
                certificates=True,
            ),
        )
    elif kind == "expand":
        config, cp = expansion(owner, before, action)
    else:
        raise ValueError("unsupported exact lifecycle action")
    return replace(
        before,
        owner=config,
        reference=config.reference,
        specialization=config.specialization,
        completion=cp,
    ), step


def profile_template(config):
    if config.reference.profile.FAMILY in ("A_OS", "A_CI", "A_PC", "A_CI_PC"):
        return "grcv4-profile-template-sha256:" + digest(dict(
            schema_version="grc9v4-exact-" + config.reference.profile.FAMILY.replace("_", "").lower() + "-profile-template-v1",
            source_profile=config.reference.profile.complete_profile_id,
            policy="preserve_quartic_A_law_rebuild_exact_fixed_rows_unit_reference_v1"))
    return "grcv4-profile-template-sha256:" + digest(
        {
            "schema_version": "grc9v4-exact-cos-profile-template-v1",
            "source_profile": config.reference.profile.complete_profile_id,
            "policy": "preserve_quartic_law_rebuild_unit_graph_maps_v1",
        }
    )


def expansion(owner, before, action):
    from .grc_9_v4_expansion import (
        GRC9ExpansionPolicy,
        GRC9V4ExpansionPlan,
        GRC9V4ExpansionRequestInput,
    )
    from .grc_v4_profile import resolve_profile

    config = before.owner
    if set(action) != {"kind", "request"} or config.policy is None:
        raise ValueError("closed expansion with active completion policy required")
    request = GRC9V4ExpansionRequestInput.from_payload(action["request"])
    if not before.journal or before.journal[-1]["kind"] != "step":
        raise ValueError("expansion requires actual fresh committed source beat")
    if (
        request.target_profile_template_id != profile_template(config)
        or request.target_specialization_id != config.specialization.specialization_id
    ):
        raise ValueError("target law/specialization mismatch")
    aos = config.reference.profile.FAMILY in ("A_OS", "A_CI", "A_PC", "A_CI_PC")
    apc = config.reference.profile.FAMILY in ("A_PC", "A_CI_PC")
    expected_distribution = (5/2048,1021/1024,1/2048) if config.reference.profile.FAMILY == "C_RG2b" else (1/128,63/64,1/128) if aos else (1/64,31/32,1/64)
    if request.target_effective_degree != 9 or request.resource_distribution != expected_distribution:
        raise ValueError("bounded exact accepted allocation required")
    carrier_event, conductance_event = None, None
    if apc:
        from .grc_9_v4_spark_apc_event import history_policy, capture
        if request.history_policy != history_policy(config):
            raise ValueError("A_PC requires W lineage and explicit whole-carrier loss")
        conductance_event, carrier_event = capture(config, kernel(config))
    elif aos:
        from .grc_9_v4_spark_conductance_event import history_policy, capture
        if request.history_policy != history_policy(config):
            raise ValueError("A_OS event requires both exact histories and old-edge conductance lineage")
        conductance_event = capture(config, kernel(config))
    elif config.reference.profile.FAMILY in ("C_PC", "C_CI_PC"):
        from .grc_9_v4_spark_carrier_event import history_policy, capture
        if request.history_policy != history_policy(config):
            raise ValueError("PC event requires exact both-role archive and explicit whole-carrier loss policy")
        carrier_event = capture(config, kernel(config))
    else:
        for channel in ("candidate", "carrier"):
            h = request.history_policy[channel]
            expected = (
                ("candidate_c_rederive_no_history_v1", "rederived")
                if channel == "candidate"
                else ("carrier_not_applicable_v1", "not_applicable")
            )
            if (
                (h["policy_id"], h["disposition"]) != expected
                or h["source_history_digest"] is not None
                or h["target_initializer_id"] is not None
                or h["information_loss"] != "none"
            ):
                raise ValueError("quartic C event has no independent history")
    policy = GRC9ExpansionPolicy.from_payload(
        config.specialization.resolved["expansion"].to_dict()
    )
    if policy.bond_seed != 1:
        raise ValueError("unit internal reference seed required")
    plan = GRC9V4ExpansionPlan(
        config.reference.graph.port_graph, config.scientific_digest, request, policy
    )
    source = classify(config.current, config.policy)
    row = next(r for r in source.rows if r["node_id"] == request.source_node_id)
    spark = config.specialization.resolved["spark"]
    # Specialization thresholds are frozen binary64 declarations. Compare their
    # exact represented values, never decimal-string approximations.
    from .grc_v4_exact import exact_number

    if (
        not rational(row["gradient_squared"])
        < exact_number(spark["gradient_tolerance"]) ** 2
    ):
        raise ValueError("fresh source gradient predicate rejected")
    if not rational(row["minimum_signed_gradient"]) < exact_number(
        spark["spark_hessian_tolerance"]
    ):
        raise ValueError("fresh hybrid source Hessian predicate rejected")
    parent = [(a, b) for a, b in source.basins if request.source_node_id in b]
    if len(parent) != 1:
        raise ValueError("source lacks unique qualified parent")
    graph = GRCV4Graph.from_port_graph(plan.target_graph)
    shares = dict(zip(plan.module_node_ids, ("0", "5/2048", "1021/1024", "1/2048") if config.reference.profile.FAMILY == "C_RG2b" else ("0", "1/128", "63/64", "1/128") if aos else ("0", "1/64", "31/32", "1/64")))
    transfer = tuple(
        tuple(
            shares.get(x, "0") if old == request.source_node_id else str(int(x == old))
            for old in config.reference.graph.live_node_ids
        )
        for x in graph.live_node_ids
    )
    if apc:
        from .grc_9_v4_spark_apc_event import target as apc_target
        current, reset = (apc_target(getattr(config, role), graph, transfer) for role in ("current", "reset"))
        conductance_event.update(new_edge_ids=sorted(set(graph.live_edge_ids)-set(config.reference.graph.live_edge_ids)),
                                 target_edge_ids=list(graph.live_edge_ids), new_edge_seed="1")
        carrier_event.update(target_carrier_pairs=[list(x) for x in carrier_pairs(graph)],
            target_all_dense_entries_zero=True, target_dense_entries=len(graph.oriented_edges)**2)
    elif conductance_event is not None:
        from .grc_9_v4_spark_conductance_event import target as conductance_target
        current, reset = (conductance_target(getattr(config, role), graph, transfer) for role in ("current", "reset"))
        conductance_event.update(new_edge_ids=sorted(set(graph.live_edge_ids)-set(config.reference.graph.live_edge_ids)),
                                 target_edge_ids=list(graph.live_edge_ids), new_edge_seed="1")
    elif carrier_event is not None:
        from .grc_9_v4_spark_carrier_event import target as carrier_target
        current, reset = (carrier_target(getattr(config, role), graph, transfer) for role in ("current", "reset"))
        carrier_event.update(target_carrier_pairs=[list(x) for x in carrier_pairs(graph)],
            target_all_dense_entries_zero=True, target_dense_entries=len(graph.oriented_edges)**2)
    else:
        current, reset = config.current.transfer(graph, transfer), config.reset.transfer(graph, transfer)
    old = config.reference.profile
    p, identity = (
        old.baseline.params_resolved.to_payload(),
        old.baseline.identity_payload.to_payload(),
    )
    weights, m = {e: 1 for e in graph.live_edge_ids}, len(graph.live_edge_ids)
    if aos:
        from .grc_v4_spark_conductance import descriptor_identity
        p["candidate"]["descriptor_backend_id"] = descriptor_identity(graph)
    else:
        p["candidate"].update(
            W_C_tr=weights,
            W_C_tr_content_digest=payload_identity(
                "wctr_identity_payload",
                {"schema_version": "grcv4-wctr-identity-v1", "W_C_tr": weights},
            ),
        )
    p["geometry"].update(
        K4_base_digest=payload_identity(
            "k4_identity_payload",
            {
                "schema_version": "grcv4-k4-identity-v1",
                "K4_base": [[0] * m for _ in range(m)],
            },
        ),
        reference_hodge_digest=payload_identity(
            "reference_hodge_identity_payload",
            {
                "schema_version": "grcv4-reference-hodge-identity-v1",
                "edge_weights": weights,
            },
        ),
    )
    identity["params_hash"] = payload_identity("resolved_params", p)
    reference = SparkReference(
        graph, type(old)(resolve_profile(p, identity), old.site)
    )
    target = replace(config, reference=reference, current=current, reset=reset)
    admit(target)
    event = {
        "event_id": plan.event_id,
        "source": config.current.to_payload(),
        "source_capture": source.to_payload(),
        "expanded": request.source_node_id,
        "module": list(plan.module_node_ids),
        "transfer": [list(r) for r in transfer],
        "source_receipt": before.receipts[-1].to_payload(),
        "target_graph": graph.graph_digest,
    }
    if carrier_event is not None:
        event["carrier_history"] = carrier_event
    if conductance_event is not None:
        event["conductance_history"] = conductance_event
    return target, CompletionPublication(
        event=FrozenJSONMap(event), reason="event committed; certificate required"
    )


def observation(owner):
    p, root = owner._published, owner._spark_scope.published
    cp, config = p.completion, p.owner
    membership = {}
    for certificate in cp.certificates:
        role = certificate.operands["binding"]["role"]
        if config.policy is None:
            continue
        certificate.require_binding(
            kernel(config), config.policy, role, getattr(config, role).charge
        )
        inside, norm = certificate.membership(getattr(config, role))
        membership[role] = {
            "inside": inside,
            "norm": norm,
            "certificate_id": certificate.certificate_id,
        }
    event_id = "no-event" if cp.event is None else cp.event["occurrence"]
    evidence = (
        cp.evidence.to_dict()
        if cp.evidence is not None
        else {
            "schema_version": "grc9v4-child-completion-evidence-v2",
            "policy_digest": digest(None)
            if config.policy is None
            else config.policy.policy_digest,
            "event_lineage_id": event_id,
            "decision": "not_applicable" if cp.event is None else "pending",
            "reason": cp.reason,
        }
    )
    validate(evidence)
    return {
        "membership": membership,
        "evidence": evidence,
        "window_observations": len(cp.observations),
        "consumed_occurrences": [c.to_dict() for c in root.claims],
        "children": [c.to_dict() for c in root.children],
        "accounting_origin": owner._spark_scope.origin,
        "accounting_scope": "process_shared_publication_v1",
        "native_source_to_completion_accepted": False,
    }


def evidence_object(owner, reference):
    """Resolve a checkpoint object, including evidence retained after reset."""
    if type(reference) is not dict or set(reference) != {"path", "sha256"}:
        raise ValueError("closed evidence reference required")
    expected = "implementation/native-spark/objects/" + reference["sha256"] + ".json"
    if reference["path"] != expected:
        raise ValueError("unknown evidence object namespace")
    with owner._lock:
        objects = list(owner._published.completion.objects)
        for claim in owner._spark_scope.published.claims:
            objects.extend(claim["objects"])
        for row in objects:
            if row["reference"].to_dict() == reference:
                value = row.to_dict()["value"]
                if digest(value) != reference["sha256"]:
                    raise ValueError("evidence object digest mismatch")
                return value
    raise ValueError("unavailable evidence object")


def snapshot(owner):
    with owner._lock:
        root = owner._spark_scope.published
        return {
            "descriptor_version": "grc9v4-native-spark-owner-v3",
            "initial": owner._initial,
            "origin": owner._spark_scope.origin,
            "publication": publication_payload(owner._published),
            "accounting": {
                "claims": [c.to_dict() for c in root.claims],
                "children": [c.to_dict() for c in root.children],
            },
        }


def restore(owner_type, value):
    if (
        set(value)
        != {"descriptor_version", "initial", "origin", "publication", "accounting"}
        or value["descriptor_version"] != "grc9v4-native-spark-owner-v3"
    ):
        raise ValueError("closed native checkpoint successor required")
    origin = value["origin"]
    if (
        type(origin) is not str
        or len(origin) != 32
        or any(x not in "0123456789abcdef" for x in origin)
    ):
        raise ValueError("invalid accounting origin")
    config = GRC9V4SparkConfiguration.from_payload(value["initial"])
    with _SCOPES_LOCK:
        scope = _SCOPES.get(origin)
    p = None
    if scope is not None:
        with scope.lock:
            if scope.initial != FrozenJSONMap(value["initial"]):
                raise ValueError("checkpoint origin/initial configuration mismatch")
            publication_digest = digest(value["publication"])
            p = next(
                (
                    p
                    for key, p in scope.published.admitted
                    if key == publication_digest
                ),
                None,
            )
    if p is None:
        replay = initialize(
            owner_type.__new__(owner_type), config, origin=origin, register=False
        )
        for action in value["publication"]["journal"]:
            result = transact(replay, action)
            if not result.committed:
                raise ValueError("checkpoint replay rejected: " + str(result.reason))
        if publication_payload(replay._published) != value["publication"]:
            raise ValueError("checkpoint differs from exact scientific replay")
        p = replay._published
        # Detached replay may establish only its own claims, never those of a
        # different fork absent the live shared accounting authority.
        if scope is None and snapshot(replay)["accounting"] != value["accounting"]:
            raise ValueError("checkpoint accounting needs its shared authority")
    with _SCOPES_LOCK:
        scope = _SCOPES.get(origin)
        if scope is None:
            scope = replay._spark_scope
            _SCOPES[origin] = scope
    with scope.lock:
        root = scope.published
        for key in ("claims", "children"):
            if set(value["accounting"]) != {"claims", "children"} or any(
                FrozenJSONMap(x) not in getattr(root, key)
                for x in value["accounting"][key]
            ):
                raise ValueError("checkpoint contains unreconciled accounting records")
        owner = owner_type.__new__(owner_type)
        owner._spark_scope, owner._spark_branch = scope, uuid4().hex
        owner._lock, owner._initial = scope.lock, config.to_payload()
        owner._backend, owner._policy = ExactBackend.FLINT, config.reference.profile.NUMERICS
        scope.published = replace(
            root, branches=root.branches + ((owner._spark_branch, p),)
        )
    return owner

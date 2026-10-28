"""Explicit same-graph branch crossings for the four bounded GRC9V4 families.

Legacy integers are a lossless ordered-coordinate encoding of the port owner.
Native state bytes retain signed zero. Local disabled identity envelopes bind
those exact bytes without pretending they are a generic V4 authoritative tuple.
This internal receiver is not public capability discovery (P9-9.4b).
"""

from copy import deepcopy
from dataclasses import asdict, dataclass, field, replace
import hashlib
import json
import math
from threading import RLock

from . import grc_9_v4_owner as enabled
from . import grc_v4_lifecycle as generic
from .grc_9_v3 import GRC9V3
from .grc_9_v3_runtime import compute_base_conductance
from .grc_9_v4_legacy import (
    GRC9V4LegacyDelegate,
    LegacyDelegateBinding,
    TARGET_VERSION,
    LegacyExpansionTargetUndefined,
)
from .grc_v4_codec import canonical_json_bytes, payload_identity
from .grc_v4_exact import exact_number, exact_backend
from .grc_v4_certification import numerical_policy
from .grc_v4_geometry import GRCV4ReferenceGeometry
from .grc_v4_migration import history_digest
from .grc_v4_state import FrozenJSONMap, GRCV4AuthoritativeState, GRCV4LifecycleResult
from .grc_v4_step import (
    make_commit_receipts,
    FailureReceipt,
    FailureReceiptIdentityPayload,
    GRCV4Failure,
)


def _bytes(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()


def _digest(prefix, value):
    return prefix + "-sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _native_digest(value):
    return "grc9v4-legacy-bytes-sha256:" + hashlib.sha256(_bytes(value)).hexdigest()


def _charge(C):
    return float(sum((exact_number(x) for x in C), exact_number()))


@dataclass(frozen=True, slots=True)
class GRC9V4BranchRequest:
    operation_id: str
    source_lifecycle_digest: str
    direction: str
    declaration: FrozenJSONMap

    def __post_init__(self):
        if (
            type(self.operation_id) is not str
            or not self.operation_id
            or type(self.source_lifecycle_digest) is not str
        ):
            raise ValueError("explicit operation and source lifecycle required")
        if self.direction not in ("disable", "enable"):
            raise ValueError("unknown branch crossing")
        object.__setattr__(self, "declaration", FrozenJSONMap(self.declaration))
        keys = (
            {
                "legacy_config",
                "current_incoming_weights",
                "reset_incoming_weights",
                "current_incoming_flux",
                "reset_incoming_flux",
            }
            if self.direction == "disable"
            else {"target_reference"}
        )
        if set(self.declaration) != keys:
            raise ValueError("closed direction-specific declaration required")

    def to_payload(self):
        return dict(
            operation_id=self.operation_id,
            source_lifecycle_digest=self.source_lifecycle_digest,
            direction=self.direction,
            declaration=self.declaration.to_dict(),
        )

    @classmethod
    def from_payload(cls, value):
        if type(value) is not dict or set(value) != {
            "operation_id",
            "source_lifecycle_digest",
            "direction",
            "declaration",
        }:
            raise ValueError("closed branch request required")
        return cls(**value)


def _graph(reference):
    return reference.graph.port_graph


def _native_config(reference, C, weights, flux, config, clock):
    graph = _graph(reference)
    nodes = graph.live_node_ids
    edges = graph.edges
    if (
        len(weights) != len(edges)
        or len(flux) != len(edges)
        or any(
            type(x) not in (int, float) or not math.isfinite(x) or x <= 0
            for x in weights
        )
        or any(type(x) not in (int, float) or not math.isfinite(x) for x in flux)
    ):
        raise ValueError(
            "complete positive incoming weights and complete flux required"
        )
    if "state" in config:
        raise ValueError("caller cannot supply resource/state projection")
    node_index = {node: i for i, node in enumerate(nodes)}
    topology = []
    ports = {}
    incidence = {str(i): [] for i in range(len(nodes))}
    for i, edge in enumerate(edges):
        u, v = node_index[edge.tail.node_id], node_index[edge.head.node_id]
        pu, pv = edge.tail.port, edge.head.port
        sign = 1
        if u > v:
            u, v, pu, pv = v, u, pv, pu
            sign = -1
        topology.append(
            dict(
                edge_id=i,
                endpoint_a=dict(node_id=u, slot=pu - 1),
                endpoint_b=dict(node_id=v, slot=pv - 1),
                payload={},
            )
        )
        ports[str(i)] = dict(
            node_u=u,
            port_u=pu,
            node_v=v,
            port_v=pv,
            conductance=weights[i],
            flux_uv=sign * flux[i],
        )
        incidence[str(u)].append(i)
        incidence[str(v)].append(i)
    return dict(
        config,
        state=dict(
            topology=dict(
                nodes=[dict(node_id=i, payload={}) for i in range(len(nodes))],
                edges=topology,
                incidence=incidence,
                port_structure={},
            ),
            nodes={
                str(i): dict(coherence=c, basin_mass=c, basin_id=i)
                for i, c in enumerate(C)
            },
            port_edges=ports,
            step_index=clock[0],
            time=clock[1],
            budget_target=_charge(C),
        ),
    )


def _project_role(reference, state, weights, flux, config, clock):
    native = GRC9V3.from_config(
        _native_config(reference, state.C, weights, flux, config, clock)
    )
    modes = native.get_params().constitutive_semantic_modes
    if any(
        modes[k] != v
        for k, v in dict(
            frame_mode="fixed_port_chart",
            hessian_backend="row_basis_diagonal",
            curvature_backend="none",
            quadrature_mode="unit_measure",
        ).items()
    ):
        raise ValueError(
            "exact fixed-row curvature-disabled unit-measure stage required"
        )
    # Native pre-flux ordering, then fresh identity. No ordinary step is taken.
    native.rebuild_differential_state()
    native.rebuild_transport_state()
    native.rebuild_differential_state()
    native.rebuild_identity_state()
    return native


def _same_coordinates(reference, delegate):
    graph = _graph(reference)
    state = delegate.get_state()
    if set(state.nodes) != set(range(len(graph.live_node_ids))) or set(
        state.port_edges
    ) != set(range(len(graph.edges))):
        raise ValueError("same-graph crossing cannot guess missing/new lineage")
    index = {node: i for i, node in enumerate(graph.live_node_ids)}
    for i, e in enumerate(graph.edges):
        p = state.port_edges[i]
        endpoints = sorted(
            ((index[e.tail.node_id], e.tail.port), (index[e.head.node_id], e.head.port))
        )
        if (p.node_u, p.port_u, p.node_v, p.port_v) != (*endpoints[0], *endpoints[1]):
            raise ValueError("legacy port/orientation coordinates changed")
    delegate._validate_state(state)
    return tuple(state.nodes[i].coherence for i in range(len(graph.live_node_ids)))


def _reset_delegate(delegate):
    snapshot = delegate.snapshot()["reset_baseline"]["snapshot"]
    if snapshot is None:
        raise ValueError("missing native reset baseline")
    return GRC9V3._from_snapshot(snapshot, restore_reset_baseline=False)


def _return_role(reference, native, role):
    C = _same_coordinates(reference, native)
    if any(x < 0 for x in C):
        raise ValueError("negative target resource")
    profile = reference.profile
    W = None
    Z = None
    initialization = None
    if profile.identity_payload.candidate == "A":
        # I_A^GRC9V3: actual incoming native weights/flux; fresh target-C rows;
        # target A alpha/beta/gamma; exact legacy floor and binary64 arithmetic.
        probe = GRC9V3(params=native.get_params(), state=deepcopy(native.get_state()))
        probe.rebuild_differential_state()
        params = profile.params_resolved.candidate
        evolution = dict(
            probe.get_params().evolution,
            alpha=params.alpha,
            beta=params.beta,
            gamma=params.gamma,
        )
        incoming = tuple(
            probe.get_state().port_edges[i].flux_uv
            for i in range(len(reference.graph.live_edge_ids))
        )
        gradients = tuple(
            tuple(probe.get_state().nodes[i].gradient_row_basis) for i in range(len(C))
        )
        compute_base_conductance(
            probe.get_state(),
            evolution=evolution,
            modes=probe.get_params().constitutive_semantic_modes,
        )
        W = tuple(
            probe.get_state().base_conductance[i]
            for i in range(len(reference.graph.live_edge_ids))
        )
        initialization = dict(
            role=role,
            policy="exact_grc9v3_base_conductance_v1",
            incoming_flux=incoming,
            gradient=gradients,
            W_A_init=W,
        )
    if profile.identity_payload.realization == "PC":
        # Structural carrier is the flattened complete K4 coordinate matrix.
        Z = (0.0,) * (len(reference.K4_base) ** 2)
    return GRCV4AuthoritativeState(C, W, Z), initialization


@dataclass(frozen=True, slots=True)
class _Publication:
    branch: str
    owner: object
    reference: GRCV4ReferenceGeometry
    specialization: object
    receipts: tuple = ()
    journal: tuple = ()
    artifacts: enabled.events.GRC9V4EventArtifacts = field(
        default_factory=enabled.events.GRC9V4EventArtifacts
    )
    entry_receipt: object = None

    @property
    def archives(self):
        return self.artifacts.archives

    @property
    def initializations(self):
        return self.artifacts.reference_currents


class GRC9V4BranchOperation:
    """Sole branch publication, receipt ledger and mixed action journal.

    P9-9.4a admits explicit same-graph crossings and ordinary/reset operations.
    Changed legacy topology needs a declared new coordinate/reference map; this
    receiver rejects it rather than silently discarding lineage.
    """

    def __init__(self, owner):
        if type(owner) is not enabled.GRC9V4EnabledOperation:
            raise TypeError("admitted bounded enabled owner required")
        seed = owner.export_seed()
        self._initial = seed.checkpoint
        self._backend = seed.exact_backend
        self._policy = seed.numerical_policy
        self._published = _Publication(
            "enabled_v4",
            seed.branch,
            seed.branch.state.inputs.geometry.reference,
            seed.branch.state.specialization,
            seed.receipts,
        )
        self._lock = RLock()

    @property
    def branch(self):
        return self._published.branch

    @property
    def receipts(self):
        return self._published.receipts

    @property
    def state(self):
        p = self._published
        if p.branch == "enabled_v4":
            return p.owner.state
        return dict(
            branch=p.branch,
            delegate=p.owner.snapshot(),
            target_spec_version=TARGET_VERSION,
            entry_receipt=p.entry_receipt,
        )

    @staticmethod
    def _endpoints(p):
        if p.branch == "enabled_v4":
            state = p.owner.state
            authority = payload_identity(
                "authoritative_state_identity_payload",
                dict(
                    schema_version="grcv4-authoritative-state-identity-v1",
                    authoritative=state.inputs.scientific_state_preimage[
                        "authoritative"
                    ],
                ),
            )
            return dict(
                state_digest=state.scientific_digest,
                reset_digest=state.reset_digest,
                authoritative_digest=authority,
                model_identity=state.model_identity,
                graph_digest=p.reference.graph.graph_digest,
            )
        snap = p.owner.snapshot()
        binding = p.owner.binding
        body = dict(
            schema_version="grc9v4-disabled-scientific-envelope-v1",
            model_identity=binding.model_identity,
            graph_digest=p.reference.graph.graph_digest,
            legacy_bytes_digest=_native_digest(snap),
        )
        return dict(
            state_digest=_digest("grcv4-state", body),
            reset_digest=_digest(
                "grcv4-reset",
                dict(
                    schema_version="grc9v4-disabled-reset-envelope-v1",
                    model_identity=binding.model_identity,
                    legacy_bytes_digest=_native_digest(snap["reset_baseline"]),
                ),
            ),
            authoritative_digest=_digest("grcv4-authoritative", body),
            model_identity=binding.model_identity,
            graph_digest=p.reference.graph.graph_digest,
        )

    @property
    def lifecycle_digest(self):
        p = self._published
        return payload_identity(
            "lifecycle_envelope_payload",
            dict(
                schema_version="grcv4-lifecycle-envelope-v1",
                scientific_state_digest=self._endpoints(p)["state_digest"],
                receipt_ids=[r.receipt_id for r in p.receipts],
            ),
        )

    def _failure(self, before, operation_id, stage, code, message):
        state = self._endpoints(before)["state_digest"]
        life = self.lifecycle_digest
        identity = FailureReceiptIdentityPayload(
            "grcv4-failure-receipt-v1", operation_id, stage, code, state, state
        )
        receipt = FailureReceipt(
            "grcv4-failure-receipt-envelope-v1",
            payload_identity("failure_receipt_identity_payload", identity.to_payload()),
            identity,
        )
        detail = GRCV4Failure(
            stage, None, code, str(message), state, state, life, life, receipt
        )
        return GRCV4LifecycleResult("rejected", False, None, detail, (receipt,))

    @staticmethod
    def _history(p):
        if p.branch != "enabled_v4":
            return dict(candidate=None, carrier=None)
        return {
            s: history_digest(p.owner.state.inputs, s) for s in ("candidate", "carrier")
        }

    def _receipts(self, before, after, operation_id, kind):
        old, new = self._history(before), self._history(after)
        channels = {}
        history = {}
        losses = []
        crossing = kind == "migrate"
        for s in ("candidate", "carrier"):
            loss = (
                (s + "_history_loss")
                if old[s] is not None and new[s] is None
                else "none"
            )
            disposition = (
                "explicit_loss"
                if loss != "none"
                else "target_initializer"
                if old[s] is None and new[s] is not None
                else "exact_transport"
                if old[s]
                else "not_applicable"
            )
            if loss != "none":
                losses.append(loss)
            channels[s] = dict(
                schema_version="grcv4-history-channel-policy-v1",
                subject=s,
                policy_id="grc9v4_exact_delegate_crossing_v1"
                if crossing
                else "grc9v4_branch_lifecycle_v1",
                disposition=disposition,
                source_history_digest=old[s],
                target_initializer_id=(
                    "exact_grc9v3_base_conductance_v1"
                    if s == "candidate"
                    else "canonical_zero_carrier_v1"
                )
                if disposition == "target_initializer"
                else None,
                information_loss=loss,
            )
            history[s] = dict(
                subject=s,
                disposition=disposition,
                source_history_digest=old[s],
                target_history_digest=new[s],
                information_loss=loss,
            )
        if crossing:
            if after.branch == "disabled_grc9v3":
                losses.append("v4_surface_projection")
            losses.append("whole_state_delegate_crossing")
        _, refs = generic._receipt_context(before.reference)
        refs["history_bundle_digest"] = payload_identity(
            "history_bundle_identity_payload",
            dict(
                schema_version="grcv4-history-bundle-identity-v1",
                history_bundle=dict(
                    schema_version="grcv4-history-bundle-policy-v1", **channels
                ),
            ),
        )
        core = dict(
            operation_id=operation_id,
            **refs,
            actual_charge_delta=float(
                self._resource_charge(after) - self._resource_charge(before)
            ),
            information_losses=losses,
            disposition="committed",
            parent_receipt_ids=[]
            if not before.receipts
            else [generic._previous_primary(before.receipts)],
        )
        for role, p in (("source", before), ("target", after)):
            core.update({role + "_" + k: v for k, v in self._endpoints(p).items()})
        if crossing:
            primary = dict(
                schema_version="grcv4-profile-migration-receipt-v1",
                core=core,
                history=dict(
                    schema_version="grcv4-history-bundle-receipt-v1", **history
                ),
            )
        elif kind == "reset":
            primary = dict(
                schema_version="grcv4-reset-receipt-v1",
                core=core,
                reset_baseline_digest=self._endpoints(before)["reset_digest"],
            )
        else:
            primary = dict(schema_version="grcv4-step-commit-receipt-v1", core=core)
        payloads = [
            primary,
            *[
                dict(
                    schema_version="grcv4-history-disposition-receipt-v1",
                    core=core,
                    subject=s,
                    history_disposition=history[s]["disposition"],
                    information_loss=history[s]["information_loss"],
                )
                for s in ("candidate", "carrier")
            ],
        ]
        if crossing:
            payloads.append(
                dict(
                    schema_version="grc9v4-legacy-compatibility-receipt-v1",
                    core=core,
                    target_spec_version=TARGET_VERSION,
                    compatibility_surfaces=[
                        "transition",
                        "state",
                        "observable",
                        "lifecycle",
                    ],
                )
            )
        clock = self._clock(after)
        return make_commit_receipts(
            payloads,
            operation_id=operation_id,
            source_state_digest=core["source_state_digest"],
            target_state_digest=core["target_state_digest"],
            target_step_index=clock[0],
            target_time=clock[1],
        )[1]

    @staticmethod
    def _clock(p):
        state = (
            p.owner.state.inputs if p.branch == "enabled_v4" else p.owner.get_state()
        )
        return state.step_index, state.time

    @staticmethod
    def _resource_charge(p):
        values = (
            p.owner.state.inputs.current.C
            if p.branch == "enabled_v4"
            else tuple(
                p.owner.get_state().nodes[i].coherence
                for i in range(len(p.reference.graph.live_node_ids))
            )
        )
        # Subtract exact represented sums before rounding the receipt scalar.
        return sum((exact_number(x) for x in values), exact_number())

    def _publish(self, before, after, emitted, action):
        if self._published is not before:
            raise RuntimeError("publication changed during transaction")
        if not emitted or len({r.receipt_id for r in before.receipts + emitted}) != len(
            before.receipts + emitted
        ):
            raise ValueError("duplicate receipt lineage")
        for r in emitted:
            core = r.identity_payload["core"]
            for role, p in (("source", before), ("target", after)):
                if any(
                    core[role + "_" + k] != v for k, v in self._endpoints(p).items()
                ):
                    raise ValueError("receipt endpoint mismatch")
            expected = (
                []
                if not before.receipts
                else [generic._previous_primary(before.receipts)]
            )
            if list(core["parent_receipt_ids"]) != expected:
                raise ValueError("invalid receipt parent")
        following = replace(
            after,
            receipts=before.receipts + emitted,
            journal=before.journal + (FrozenJSONMap(action),),
        )
        following.artifacts.require_extension_of(before.artifacts)
        self._published = following

    def migrate(self, request):
        if type(request) is not GRC9V4BranchRequest:
            raise TypeError("typed crossing request required")
        with self._lock, exact_backend(self._backend), numerical_policy(self._policy):
            before = self._published
            if request.source_lifecycle_digest != self.lifecycle_digest:
                return self._failure(
                    before,
                    request.operation_id,
                    "admission",
                    "invalid_migration",
                    "stale source lifecycle",
                )
            if (request.direction == "disable") != (before.branch == "enabled_v4"):
                return self._failure(
                    before,
                    request.operation_id,
                    "admission",
                    "invalid_migration",
                    "wrong source branch",
                )
            try:
                after = (
                    self._disable(before, request)
                    if request.direction == "disable"
                    else self._enable(before, request)
                )
            except ValueError as exc:
                return self._failure(
                    before,
                    request.operation_id,
                    "target_readmission",
                    "target_readmission_failure",
                    exc,
                )
            emitted = self._receipts(before, after, request.operation_id, "migrate")
            if after.branch == "disabled_grc9v3":
                after = replace(after, entry_receipt=emitted[-1])
            self._publish(
                before,
                after,
                emitted,
                dict(kind="migrate", request=request.to_payload()),
            )
            return GRCV4LifecycleResult(
                "committed", True, emitted[0].commit_id, None, emitted
            )

    def _disable(self, before, request):
        inputs = before.owner.state.inputs
        ref = before.reference
        d = request.declaration
        if (
            ref.profile.params_resolved.common.measure_profile_id
            != "unit_vertex_measure_v1"
        ):
            raise ValueError("unit-measure crossing required")
        native = []
        for role in ("current", "reset"):
            native.append(
                _project_role(
                    ref,
                    getattr(inputs, role),
                    d[role + "_incoming_weights"],
                    d[role + "_incoming_flux"],
                    d["legacy_config"].to_dict(),
                    self._clock(before),
                )
            )
        snapshot = native[0].snapshot()
        snapshot["reset_baseline"]["snapshot"] = native[1]._snapshot_payload(
            reset_baseline=None
        )
        owner = GRC9V4LegacyDelegate(
            LegacyDelegateBinding(ref.profile, before.specialization), snapshot
        )
        _same_coordinates(ref, owner._delegate)
        _same_coordinates(ref, _reset_delegate(owner._delegate))
        archive = FrozenJSONMap(
            dict(
                source_state_digest=before.owner.state.scientific_digest,
                current=asdict(inputs.current),
                reset=asdict(inputs.reset),
                history_digests=self._history(before),
            )
        )
        return replace(
            before,
            branch="disabled_grc9v3",
            owner=owner,
            artifacts=replace(before.artifacts, archives=before.archives + (archive,)),
        )

    def _enable(self, before, request):
        ref = GRCV4ReferenceGeometry.from_payload(
            request.declaration["target_reference"].to_dict()
        )
        if (
            ref.graph != before.reference.graph
            or ref.context != before.reference.context
        ):
            raise ValueError("crossing requires the exact declared same graph/context")
        family = ref.profile.identity_payload.profile_family_id
        if family not in enabled._OWNERS:
            raise ValueError("unselected target family")
        native = before.owner._delegate
        reset = _reset_delegate(native)
        current, ci = _return_role(ref, native, "current")
        baseline, ri = _return_role(ref, reset, "reset")
        from .grc_v4_geometry import GeometryStageInputs

        inputs = GeometryStageInputs(
            ref.geometry(),
            ref.context,
            current,
            baseline,
            request.operation_id,
            _charge(current.C),
            (),
            *self._clock(before),
            0,
            "pre_read",
            0,
            None,
        )
        inputs = generic._fresh_geometry(inputs)
        state = enabled._OWNERS[family].STATE(inputs, before.specialization)
        owner = enabled.GRC9V4EnabledBranch.admit(
            state
        )  # Native independent current/reset admission.
        notes = tuple(FrozenJSONMap(v) for v in (ci, ri) if v is not None)
        return replace(
            before,
            branch="enabled_v4",
            owner=owner,
            reference=ref,
            artifacts=replace(
                before.artifacts, reference_currents=before.initializations + notes
            ),
            entry_receipt=None,
        )

    @staticmethod
    def _prepare_enabled(before, kind, request=None):
        if (
            before.branch != "enabled_v4"
            or type(before.owner) is not enabled.GRC9V4EnabledBranch
        ):
            raise ValueError("enabled action requires the immutable enabled branch")
        context = enabled.GRC9V4EnabledContext(
            before.owner.state, before.receipts, before.artifacts
        )
        transition = enabled.prepare_enabled(context, kind, request)
        if (
            type(transition) is not enabled.GRC9V4EnabledTransition
            or transition.source != context
        ):
            raise ValueError("prepared enabled action differs from branch source")
        return transition

    @staticmethod
    def _enabled_target(before, transition):
        return replace(
            before,
            owner=enabled.GRC9V4EnabledBranch(transition.state),
            reference=transition.state.inputs.geometry.reference,
            receipts=before.receipts + transition.result.emitted_receipts,
            artifacts=transition.artifacts,
        )

    def _enabled_action(self, kind, request=None):
        with self._lock, exact_backend(self._backend), numerical_policy(self._policy):
            before = self._published
            transition = self._prepare_enabled(before, kind, request)
            if transition.result.committed:
                action = {"kind": "enabled_" + kind}
                if request is not None:
                    action["request"] = request.to_payload()
                self._publish(
                    before,
                    self._enabled_target(before, transition),
                    transition.result.emitted_receipts,
                    action,
                )
            return transition.result

    def step_enabled(self, request):
        return self._enabled_action("step", request)

    def reset_enabled(self):
        return self._enabled_action("reset")

    def legacy_operation(self, operation_id, kind="step"):
        if type(operation_id) is not str or not operation_id:
            raise ValueError("explicit operation identity required")
        if kind not in ("step", "reset"):
            raise ValueError("bounded native operation required")
        with self._lock:
            before = self._published
            if before.branch != "disabled_grc9v3":
                raise ValueError("legacy operation on enabled branch")
            owner = before.owner.duplicate()
            try:
                result = getattr(owner, kind)()
                _same_coordinates(before.reference, owner._delegate)
            except LegacyExpansionTargetUndefined as exc:
                return self._failure(
                    before, operation_id, "target_readmission", exc.code, exc
                )
            except ValueError as exc:
                return self._failure(
                    before,
                    operation_id,
                    "target_readmission",
                    "target_readmission_failure",
                    exc,
                )
            after = replace(before, owner=owner)
            emitted = self._receipts(before, after, operation_id, kind)
            self._publish(
                before,
                after,
                emitted,
                dict(kind="legacy_" + kind, operation_id=operation_id),
            )
            return result

    def snapshot(self):
        with self._lock:
            p = self._published
            return _bytes(
                dict(
                    descriptor_version="grc9v4-branch-crossing-checkpoint-v1",
                    initial=json.loads(self._initial),
                    branch=p.branch,
                    state=p.owner.state.to_payload()
                    if p.branch == "enabled_v4"
                    else p.owner.checkpoint(),
                    receipts=[r.to_payload() for r in p.receipts],
                    journal=[a.to_dict() for a in p.journal],
                    archives=[a.to_dict() for a in p.archives],
                    initializations=[a.to_dict() for a in p.initializations],
                    lifecycle_digest=self.lifecycle_digest,
                )
            )

    @classmethod
    def from_state(cls, raw):
        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate snapshot key")
                result[key] = value
            return result

        data = json.loads(raw, object_pairs_hook=unique)
        if (
            set(data)
            != {
                "descriptor_version",
                "initial",
                "branch",
                "state",
                "receipts",
                "journal",
                "archives",
                "initializations",
                "lifecycle_digest",
            }
            or data["descriptor_version"] != "grc9v4-branch-crossing-checkpoint-v1"
        ):
            raise ValueError("closed crossing snapshot required")
        owner = cls(
            enabled.GRC9V4EnabledOperation.from_state(
                canonical_json_bytes(data["initial"])
            )
        )
        from .grc_v4 import GRCV4StepRequestInput

        for action in data["journal"]:
            if action.get("kind") == "migrate" and set(action) == {"kind", "request"}:
                result = owner.migrate(
                    GRC9V4BranchRequest.from_payload(action["request"])
                )
            elif action.get("kind") == "enabled_step" and set(action) == {
                "kind",
                "request",
            }:
                result = owner.step_enabled(
                    GRCV4StepRequestInput.from_payload(action["request"])
                )
            elif action == {"kind": "enabled_reset"}:
                result = owner.reset_enabled()
            elif action.get("kind") in ("legacy_step", "legacy_reset") and set(
                action
            ) == {"kind", "operation_id"}:
                result = owner.legacy_operation(
                    action["operation_id"], action["kind"][7:]
                )
            else:
                raise ValueError("unknown crossing journal action")
            if hasattr(result, "committed") and not result.committed:
                raise ValueError("retained crossing failed replay")
        if owner.snapshot() != _bytes(data):
            raise ValueError("crossing replay mismatch")
        return owner

    def duplicate(self):
        return type(self).from_state(self.snapshot())

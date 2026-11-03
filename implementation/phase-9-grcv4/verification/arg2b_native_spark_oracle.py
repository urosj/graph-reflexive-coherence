"""Independent joint inverse-chain, conductance-writer and physical-step audit."""

import importlib.util
import json
import sys
from functools import lru_cache
from pathlib import Path

from crg2b_native_spark_oracle import decoded, encoded, need, norm, vector
from flint import arb, arb_mat, ctx, fmpq, fmpq_mat

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_codec import canonical_json_bytes, decode_canonical_json
from pygrc.models.grc_v4_spark_conductance import ExactConductanceState
from pygrc.models.grc_v4_spark_state import round_flux
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "implementation/investigations/grc9v4-constitutive-design/research"
sys.path[:0] = [
    str(RESEARCH),
    str(RESEARCH.parent / "evidence/spark-completion/review/constructive-candidate"),
]
spec = importlib.util.spec_from_file_location(
    "arg2b_independent_depth24", RESEARCH / "spark_completion_a_rg2b.py"
)
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)
reference.DEPTH = 24
reference.PRECISION = 768
reference.PROPOSAL_BITS = 384
reference.SWEEPS = 12
original_domain = reference.global_domain
target_chart = dict(reference.TARGET_CHART)


@lru_cache(maxsize=8)
def domain(key):
    g = json.loads(key)
    nodes = g["live_node_ids"]
    if len(nodes) == 15:
        core = next(n for n in nodes if n.endswith("/core"))
        prefix = core.rsplit("/", 1)[0]
        chart = {
            prefix + k[len("sc2-positive-module") :]
            if k.startswith("sc2-positive-module/")
            else k: v
            for k, v in target_chart.items()
        }
    else:
        chart = target_chart
    old = reference.TARGET_CHART
    try:
        reference.TARGET_CHART = chart
        return original_domain(key)
    finally:
        reference.TARGET_CHART = old


reference.global_domain = domain


def model(graph):
    return reference.ARG2bReference(graph)


@lru_cache(maxsize=8)
def fresh(graph_bytes, state_bytes):
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        state = ExactConductanceState.from_canonical_bytes(state_bytes)
        m = model(json.loads(graph_bytes))
        W = vector(state.W_A)
        X = m.pack(vector(state.C), arb_mat([[x.log()] for x in W.entries()]))
        scale = 2**384
        qs = [x.mid().fmpq() for x in X.entries()]
        point = arb_mat(
            [[fmpq((q.numerator * scale) // q.denominator, scale)] for q in qs]
        )
        s = m.section(point)
        error = (s["error"] + arb(fmpq(1, 256)) * norm(X - point)).upper()
        H = arb_mat(m.m, m.m)
        for i in range(m.m):
            for j in range(i, m.m):
                if m.overlap[i][j]:
                    H[i, j] = H[j, i] = arb(s["proposal"][i, j].fmpq(), error.fmpq())
        return FrozenJSONMap(
            {
                "H": encoded(H),
                "selected": {
                    k: encoded(v) for k, v in m.read(vector(state.C), W, H).items()
                },
            }
        )


@lru_cache(maxsize=8)
def _proof(graph_bytes, profile_bytes, state_bytes, witness_bytes, precision):
    with _ARB_CONTEXT_LOCK, ctx.workprec(precision):
        graph, profile = json.loads(graph_bytes), json.loads(profile_bytes)
        state = ExactConductanceState.from_canonical_bytes(state_bytes)
        w = FrozenJSONMap(decode_canonical_json(witness_bytes))
        need(
            w["graph"].to_dict() == graph
            and w["profile"].to_dict() == profile
            and w["state"].to_dict() == state.to_payload(),
            "externally captured full C/W subject",
        )
        need(
            w["precision_bits"] == 256
            and w["numerical_policy_id"]
            == "spark_arg2b_arb256_section16_current192_flux128_conductance192_v1"
            and w["physical_state"] == ("C", "W_A")
            and w["section_coordinates"] == "C_then_64_logW"
            and w["writer_in_inverse"]
            and not w["section_C1_claimed"],
            "joint policy and complete physical state",
        )
        m = model(graph)
        rho = fmpq(1, 1024)
        L = fmpq(1, 256)
        for key, value in m.domain.items():
            if key not in ("schema", "selector", "section_tail"):
                need(
                    w["completion"][key] == FrozenJSONMap({"v": value})["v"],
                    "frozen joint domain: " + key,
                )
        W = vector(state.W_A)
        X = m.pack(vector(state.C), arb_mat([[x.log()] for x in W.entries()]))
        Xprev = vector(w["query_proposal"])
        Hprev = decoded(w["proposal"])
        proposal = Hprev
        shift = norm(X - Xprev)
        need(shift <= arb(fmpq(w["query_shift"][1])), "whole C/logW input displacement")
        need(len(w["chain"]) == 16, "complete native joint chain")
        need(
            Hprev == Hprev.transpose() and norm(Hprev - m.I) < arb(rho),
            "query proposal geometry",
        )
        residuals = []
        rxmax = arb(0)
        rhmax = arb(0)
        pairs = [(i, j) for i in range(m.m) for j in range(i, m.m) if m.overlap[i][j]]
        for row in w["chain"]:
            need(
                len(row["X"]) == m.d and len(row["H"]) == len(pairs),
                "complete joint inverse coordinates",
            )
            Xi = vector(row["X"])
            H = arb_mat(m.m, m.m)
            for (i, j), v in zip(pairs, row["H"], strict=True):
                H[i, j] = H[j, i] = arb(fmpq(v))
            need(norm(H - m.I) < arb(rho), "inverse geometry SPD/star ball")
            read = m.lag(Xi, H, retract=True)
            rx = norm(Xi + read["increment"] - Xprev)
            rh = norm(read["geometry"] - Hprev)
            need(
                rx <= arb(fmpq(row["state_residual"][1]))
                and rh <= arb(fmpq(row["geometry_residual"][1])),
                "independent full writer/inverse residual",
            )
            residuals.append((rh + L * rx).upper())
            rxmax = max(rxmax, rx)
            rhmax = max(rhmax, rh)
            Xprev, Hprev = Xi, H
        need(Hprev == m.I, "identity terminal")
        q, V = (
            fmpq(m.domain["graph_transform_contraction"]),
            fmpq(m.domain["section_value_radius"]),
        )
        tail = arb(q**16 * V)
        residual = (rhmax + L * rxmax) / (1 - q)
        need(
            fmpq(w["completion"]["section_tail"]) == q**16 * V, "native completion tail"
        )
        need(
            tail <= arb(fmpq(w["section_tail"][1]))
            and residual <= arb(fmpq(w["residual_error"][1]))
            and residual + tail + L * shift <= arb(fmpq(w["section_error"][1])),
            "joint residual/tail/full shift error",
        )
        error = arb(V)
        for r in reversed(residuals):
            error = r + q * error
        error = (error + L * shift).upper().fmpq()
        H = arb_mat(m.m, m.m)
        for i in range(m.m):
            for j in range(i, m.m):
                if m.overlap[i][j]:
                    H[i, j] = H[j, i] = arb(proposal[i, j].fmpq(), error)
        need(norm(H - m.I) < arb(rho), "proved infinite section geometry")
        selected = m.read(vector(state.C), W, H)
        for key, value in selected.items():
            actual = decoded(w["selected"][key])
            need(
                all(
                    a.overlaps(b)
                    for a, b in zip(actual.entries(), value.entries(), strict=True)
                ),
                "independent selected tuple: " + key,
            )
        published = decoded(w["geometry"])
        need(
            all(
                a.contains(b)
                for a, b in zip(published.entries(), H.entries(), strict=True)
            ),
            "published section enclosure",
        )
        need(
            all(x.rad() < arb(fmpq(1, 2**192)) for x in selected["current"].entries()),
            "independent current192",
        )
        return FrozenJSONMap(
            {
                "H": encoded(H),
                "selected": {k: encoded(v) for k, v in selected.items()},
                "checks": {
                    "finite_levels": 16,
                    "full_writer_in_inverse": True,
                    "full_input_shift": True,
                    "truncation_tail": True,
                    "level_weighted_residuals": True,
                    "section_C1_claimed": False,
                },
            }
        )


def proof_read(graph, profile, state, witness):
    return _proof(
        canonical_json_bytes(graph),
        canonical_json_bytes(profile),
        state.to_canonical_bytes(),
        canonical_json_bytes(witness.to_dict()),
        768,
    )


def verify_step(config, before, step, *, fresh_check=False):
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        graph = config.reference.graph.to_payload()
        profile = config.reference.profile.to_payload()
        need(
            step.before == before
            and step.profile_id == config.reference.profile.complete_profile_id
            and step.duration == "16",
            "captured public physical subject",
        )
        incoming = proof_read(graph, profile, before, step.section)
        returned = proof_read(graph, profile, step.after, step.restart_section)
        J = decoded(incoming["selected"]["current"])
        m = model(graph)
        need(
            all(
                round_flux(x.lower().fmpq()) == round_flux(x.upper().fmpq()) == fmpq(v)
                for x, v in zip(J.entries(), step.flux, strict=True)
            ),
            "unique independently rounded flux",
        )
        exact = fmpq_mat([[fmpq(c)] for c in before.C]) - 16 * fmpq_mat(
            [[x.fmpq() for x in r] for r in m.B.tolist()]
        ) * fmpq_mat([[fmpq(v)] for v in step.flux])
        need(
            tuple(map(str, exact.entries())) == step.after.C
            and sum(exact.entries()) == 21,
            "exact charge and incidence",
        )
        ideal = vector(before.C) - 16 * m.B * J
        need(
            all(
                abs(a - b) <= arb(fmpq(e))
                for a, b, e in zip(
                    (vector(step.after.C) - ideal).entries(),
                    [arb(0)] * m.n,
                    step.componentwise_error_bounds,
                    strict=True,
                )
            ),
            "full represented C error",
        )
        W = vector(before.W_A)
        L = arb_mat([[x.log()] for x in W.entries()])
        exponent, _ = m.exponent(vector(step.after.C), W, J)
        nextL = m.decay * L + (1 - m.decay) * exponent
        weights = m.exp(nextL)
        for key, value in (
            ("exponent", exponent),
            ("ideal", weights),
            ("selected_current", J),
        ):
            need(
                all(
                    a.overlaps(b)
                    for a, b in zip(
                        decoded(step.writer[key]).entries(),
                        value.entries(),
                        strict=True,
                    )
                ),
                "writer operand: " + key,
            )
        need(
            tuple(step.writer["incoming_W"]) == before.W_A, "incoming W writer history"
        )
        for w, mid, idealW in zip(
            step.after.W_A, step.writer["midpoint"], weights.entries(), strict=True
        ):
            need(
                fmpq(w) == round_flux(fmpq(mid) * 2**64) / 2**64,
                "represented W rounding",
            )
            need(
                abs(arb(fmpq(w)).log() - idealW.log())
                <= arb(fmpq(step.log_conductance_component_error)),
                "whole log-W error",
            )
        H = decoded(incoming["H"])
        final = m.read(vector(step.after.C), W, H)["current"]
        ref = m.read(vector(step.after.C), vector(step.after.W_A), m.I)["current"]
        for rows, value in ((step.final_current, final), (step.reference_current, ref)):
            need(
                all(
                    arb((fmpq(a) + fmpq(b)) / 2, (fmpq(b) - fmpq(a)) / 2).overlaps(x)
                    for (a, b), x in zip(rows, value.entries(), strict=True)
                ),
                "held-H/reference diagnostic",
            )
        if fresh_check:
            for state, witness, proved in (
                (before, step.section, incoming),
                (step.after, step.restart_section, returned),
            ):
                independent = fresh(
                    canonical_json_bytes(graph), state.to_canonical_bytes()
                )
                for key in ("current", "causal_flat"):
                    need(
                        all(
                            a.overlaps(b)
                            for a, b in zip(
                                decoded(independent["selected"][key]).entries(),
                                decoded(proved["selected"][key]).entries(),
                                strict=True,
                            )
                        ),
                        "fresh depth24 section",
                    )
        return {
            "incoming": incoming["checks"].to_dict(),
            "returned": returned["checks"].to_dict(),
            "fresh_depth24": fresh_check,
            "full_C_logW_error": True,
            "exact_charge": True,
            "duration": "16",
        }

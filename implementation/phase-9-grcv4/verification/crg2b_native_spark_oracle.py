"""Independent higher-precision C_RG2b section, literal similarity and chain audit.

The scientific reference runs in its own module namespace with a depth-40 chain
and Arb768. Its memoized comparisons are keyed by complete exact subjects;
complete witness proofs are reused only for byte-identical subjects and evidence.
"""

import importlib.util
import json
import sys
from functools import lru_cache
from pathlib import Path

from flint import arb, arb_mat, ctx, fmpq, fmpq_mat

from pygrc.models.grc_v4_certification import _ARB_CONTEXT_LOCK
from pygrc.models.grc_v4_state import FrozenJSONMap

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "implementation/investigations/grc9v4-constitutive-design/research"
sys.path[:0] = [
    str(RESEARCH),
    str(RESEARCH.parent / "evidence/spark-completion/review/constructive-candidate"),
]
spec = importlib.util.spec_from_file_location(
    "crg2b_independent_depth40", RESEARCH / "spark_completion_c_rg2b.py"
)
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)
reference.DEPTH = 40
reference.PROPOSAL_BITS = 512
reference.PRECISION = 768
reference.SWEEPS = 10


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def vector(values):
    return arb_mat([[fmpq(x)] for x in values])


def norm(M):
    return arb(
        max(
            sum(abs(M[i, j]).upper().fmpq() for j in range(M.ncols()))
            for i in range(M.nrows())
        )
    )


def bounds(x):
    return [str(x.lower().fmpq()), str(x.upper().fmpq())]


def encoded(M):
    return [[bounds(M[i, j]) for j in range(M.ncols())] for i in range(M.nrows())]


def decoded(rows):
    return arb_mat(
        [
            [arb((fmpq(a) + fmpq(b)) / 2, (fmpq(b) - fmpq(a)) / 2) for a, b in row]
            for row in rows
        ]
    )


def encloses(rows, M):
    return all(
        fmpq(rows[i][j][0]) <= M[i, j].lower().fmpq()
        and M[i, j].upper().fmpq() <= fmpq(rows[i][j][1])
        for i in range(M.nrows())
        for j in range(M.ncols())
    )


def model(graph):
    return reference.CRG2bReference(graph)


@lru_cache(maxsize=8)
def selected(graph_bytes, values):
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        m = model(json.loads(graph_bytes))
        C = vector(values)
        scale = 2**512
        q = [x.mid().fmpq() for x in C.entries()]
        point = arb_mat(
            [[fmpq((x.numerator * scale) // x.denominator, scale)] for x in q]
        )
        section = m.section(point)
        e = (section["error"] + arb(fmpq(1, 256)) * norm(C - point)).upper()
        H = arb_mat(m.m, m.m)
        for i in range(m.m):
            for j in range(i, m.m):
                if m.overlap[i][j]:
                    H[i, j] = arb(section["proposal"][i, j].fmpq(), e.fmpq())
                    H[j, i] = H[i, j]
        current, flat = m.direct_similarity_read(C, H, m.q(1, 1024))
        return FrozenJSONMap(
            {"H": encoded(H), "J": encoded(current), "flat": encoded(flat)}
        )


def _audit_read_uncached(graph, profile, state, witness):
    """Rebuild every native level using a different physical current solve."""
    need(
        witness["graph"].to_dict() == graph
        and witness["profile"].to_dict() == profile
        and witness["state"].to_dict() == state.to_payload(),
        "section witness subject binding",
    )
    need(
        witness["precision_bits"] == 256
        and witness["physical_state"] == ("C",)
        and not witness["section_C1_claimed"],
        "section policy/physical state",
    )
    m = model(graph)
    C = vector(state.C)
    Xprev = vector(witness["query_proposal"])
    Hprev = decoded(witness["proposal"])
    rho = fmpq(1, 1024)
    L = fmpq(1, 256)
    shift = norm(C - Xprev)
    need(shift <= arb(fmpq(witness["query_shift"][1])), "whole-input query shift")
    maxima = [arb(0), arb(0)]
    level_residuals = []
    chain = witness["chain"]
    need(len(chain) == 32, "complete finite-chain depth")
    for i, row in enumerate(chain):
        X = vector(row["X"])
        H = arb_mat(m.m, m.m)
        pairs = [(j, k) for j in range(m.m) for k in range(j, m.m) if m.overlap[j][k]]
        need(len(row["H"]) == len(pairs), "complete symmetric star geometry")
        for (j, k), x in zip(pairs, row["H"], strict=True):
            H[j, k] = H[k, j] = arb(fmpq(x))
        need(norm(H - m.I) < arb(rho), "finite-chain geometry domain")
        clipped = m.clip(X)
        J, flat = m.direct_similarity_read(clipped, H, m.q(1, 1024))
        generated = m.geometry(flat)
        rx = norm(X - 8 * m.B * J - Xprev)
        rh = norm(Hprev - generated)
        for idx, (actual, label) in enumerate(
            ((rx, "state_residual"), (rh, "geometry_residual"))
        ):
            need(
                actual <= arb(fmpq(row[label][1])),
                "independent chain residual: " + label,
            )
            maxima[idx] = max(maxima[idx], actual)
        level_residuals.append((rh + L * rx).upper())
        Xprev, Hprev = X, H
    need(Hprev == m.I, "identity terminal section boundary")
    q = fmpq(m.domain["graph_transform_contraction"])
    V = fmpq(m.domain["section_value_radius"])
    tail = arb(q**32 * V)
    residual = (maxima[1] + L * maxima[0]) / (1 - q)
    need(
        tail <= arb(fmpq(witness["section_tail"][1]))
        and residual <= arb(fmpq(witness["residual_error"][1])),
        "finite-chain tail or residual error",
    )
    need(
        residual + tail + L * shift <= arb(fmpq(witness["section_error"][1])),
        "full section enclosure error",
    )
    H = decoded(witness["geometry"])
    proposal = decoded(witness["proposal"])
    error = fmpq(witness["section_error"][1])
    for i in range(m.m):
        for j in range(m.m):
            need(
                H[i, j] == H[j, i] if H[i, j].rad() == 0 else H[i, j].overlaps(H[j, i]),
                "symmetric section enclosure",
            )
            if not m.overlap[i][j]:
                need(H[i, j] == 0, "section support")
            else:
                need(
                    H[i, j].contains(arb(proposal[i, j].fmpq(), error)),
                    "claimed section error not enclosed by H",
                )
    J, flat = m.direct_similarity_read(C, H, m.q(1, 1024))
    # The two interval solves differ in enclosure width, so compare their
    # midpoint tuples and require overlap in addition to a fresh tighter root.
    need(
        all(
            x.overlaps(y)
            for x, y in zip(
                J.entries(), decoded(witness["current"]).entries(), strict=True
            )
        ),
        "literal similarity current disagrees",
    )
    need(
        all(
            x.overlaps(y)
            for x, y in zip(
                flat.entries(), decoded(witness["flat"]).entries(), strict=True
            )
        ),
        "literal similarity flat disagrees",
    )
    baseline = -m.q(1, 1024) * m.Bt * (m.B * H * m.Bt * C / 64 - m.site(C))
    need(
        all(
            x.overlaps(y)
            for x, y in zip(
                baseline.entries(), decoded(witness["baseline"]).entries(), strict=True
            )
        ),
        "both physical H consumers",
    )
    # Independently reconstruct the section enclosure from the verified chain.
    # The frozen graph-transform theorem bounds the exact infinite section by
    # these residuals plus q^32 V and the complete input displacement. No new
    # inverse-chain solve is needed to establish this enclosure.
    # Backward residual propagation is sharper than repeating the worst
    # level at every depth: E_(i-1) <= rh_i + L*rx_i + q*E_i, E_N <= V.
    # It uses the same global inverse/section inequalities and includes the
    # whole tail; no finite level or physical direction is omitted.
    weighted = arb(V)
    for level in reversed(level_residuals):
        weighted = level + q * weighted
    independent_error = (weighted + L * shift).upper().fmpq()
    proved_H = arb_mat(m.m, m.m)
    for i in range(m.m):
        for j in range(i, m.m):
            if m.overlap[i][j]:
                proved_H[i, j] = proved_H[j, i] = arb(
                    proposal[i, j].fmpq(), independent_error
                )
    need(norm(proved_H - m.I) < arb(rho), "independently proved section domain")
    proved_J, proved_flat = m.direct_similarity_read(C, proved_H, m.q(1, 1024))
    need(
        all(x.rad() < arb(fmpq(1, 2**160)) for x in proved_J.entries()),
        "independent current enclosure exceeds fixed policy",
    )
    return {
        "checks": {
            "finite_levels": 32,
            "all_inverse_and_geometry_residuals": True,
            "full_input_shift": True,
            "truncation_tail": True,
            "literal_similarity": True,
            "proof_derived_section": True,
            "level_weighted_residuals": True,
            "section_C1_claimed": False,
        },
        "H": encoded(proved_H),
        "J": encoded(proved_J),
        "flat": encoded(proved_flat),
    }


@lru_cache(maxsize=8)
def _audited_read(graph_bytes, profile_bytes, state_bytes, witness_bytes, precision):
    from pygrc.models.grc_v4_spark_state import ExactResources

    need(precision == 768, "independent audit precision")
    return FrozenJSONMap(
        _audit_read_uncached(
            json.loads(graph_bytes),
            json.loads(profile_bytes),
            ExactResources.from_canonical_bytes(state_bytes),
            FrozenJSONMap(json.loads(witness_bytes)),
        )
    )


def proof_read(graph, profile, state, witness):
    """Reuse only a proved byte-identical complete witness and exact subject."""
    from pygrc.models.grc_v4_codec import canonical_json_bytes

    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        return _audited_read(
            canonical_json_bytes(graph),
            canonical_json_bytes(profile),
            state.to_canonical_bytes(),
            canonical_json_bytes(witness.to_dict()),
            ctx.prec,
        )


def audit_read(graph, profile, state, witness, *, fresh=True):
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        proved = proof_read(graph, profile, state, witness)
        if fresh:
            exact = selected(
                json.dumps(graph, sort_keys=True, separators=(",", ":")), tuple(state.C)
            )
            for native, key in (("geometry", "H"), ("current", "J"), ("flat", "flat")):
                need(
                    encloses(witness[native], decoded(exact[key])),
                    "fresh depth40 enclosure: " + native,
                )
                need(
                    all(
                        x.overlaps(y)
                        for x, y in zip(
                            decoded(proved[key]).entries(),
                            decoded(exact[key]).entries(),
                            strict=True,
                        )
                    ),
                    "proof-derived section disagrees with fresh depth40 solve",
                )
        return dict(proved["checks"].to_dict(), fresh_depth40=fresh)


def verify_step(step, *, fresh=True, diagnostic_overlap=False):
    with _ARB_CONTEXT_LOCK, ctx.workprec(768):
        graph = step.before.graph.to_payload()
        profile = step.section["profile"].to_dict()
        m = model(graph)
        first = audit_read(graph, profile, step.before, step.section, fresh=fresh)
        second = audit_read(
            graph, profile, step.after, step.restart_section, fresh=fresh
        )
        C = vector(step.before.C)
        after = vector(step.after.C)
        reference_root = proof_read(graph, profile, step.before, step.section)
        ideal = C - 8 * m.B * decoded(reference_root["J"])
        need(
            step.duration == "8"
            and step.before.charge == step.after.charge
            and sum(map(fmpq, step.after.C)) == fmpq(step.after.charge),
            "exact charge/duration",
        )
        need(
            all(
                abs(arb(fmpq(value)) - ideal[i, 0]) < arb(fmpq(error))
                for i, (value, error) in enumerate(
                    zip(step.after.C, step.componentwise_error_bounds, strict=True)
                )
            ),
            "complete represented resource error",
        )
        incidence = fmpq_mat(
            [
                [
                    int(e["tail"]["node_id"] == n) - int(e["head"]["node_id"] == n)
                    for e in graph["edges"]
                ]
                for n in graph["live_node_ids"]
            ]
        )
        need(
            fmpq_mat([[fmpq(x)] for x in step.after.C])
            == fmpq_mat([[fmpq(x)] for x in step.before.C])
            - 8 * incidence * fmpq_mat([[fmpq(x)] for x in step.flux]),
            "exact incidence law",
        )
        held, _ = m.direct_similarity_read(
            after, decoded(reference_root["H"]), m.q(1, 1024)
        )
        if diagnostic_overlap:
            # Independent interval expressions can enclose the same current
            # without nesting (notably at an almost stationary center). This
            # is a diagnostic comparison, not certification of the stored box.
            # Keep the existing current160 bound as an additional discriminator.
            actual = decoded([[x] for x in step.final_current])
            need(
                all(
                    a.overlaps(b) and abs(a - b) < arb(fmpq(1, 2**160))
                    for a, b in zip(actual.entries(), held.entries(), strict=True)
                ),
                "held diagnostic overlap/current160 consistency",
            )
        else:
            need(
                encloses([[x] for x in step.final_current], held),
                "held section poststate diagnostic",
            )
        ref, _ = m.direct_similarity_read(after, m.I, m.q(1, 1024))
        need(
            all(
                x.contains(fmpq(v))
                for x, v in zip(ref.entries(), step.reference_current, strict=True)
            ),
            "fixed reference poststate diagnostic",
        )
        result = {
            "independent_precision_bits": 768,
            "incoming": first,
            "returned": second,
            "full_step_error": True,
            "exact_incidence": True,
            "exact_charge": True,
            "poststate_diagnostics": True,
            "physical_state": ["C"],
        }
        if diagnostic_overlap:
            result["held_diagnostic_check"] = (
                "independent_overlap_and_current160_difference; not stored-box recertification"
            )
        return result

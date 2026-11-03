"""Bind the native spark contract map and small arithmetic checks; no trajectories."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
import lzma
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
INV = "implementation/investigations/grc9v4-constitutive-design/"
EVIDENCE = INV + "evidence/spark-completion/"
EARLY = EVIDENCE + "applicability/earlier-closure/"
HERE = "implementation/phase-9-grcv4/"
DOCUMENT = HERE + "tranche-9/P9-9.1a.1-NativeSparkContract.md"
RECORD = HERE + "tranche-9/P9-9.1a.1-Verification.json"
SCRIPT = HERE + "verification/p991a1_native_spark_contract.py"
# Family, manifest suffix, obligation code, independent state channels.
FAMILIES = (
    ("C_OS", "", "", ["C"]),
    ("C_CI", "-applicability", "CCI", ["C"]),
    ("C_PC", "-pc", "CPC", ["C", "Z"]),
    ("C_CI_PC", "-ci-pc", "CCIPC", ["C", "Z"]),
    ("A_OS", "-a-os", "AOS", ["C", "W"]),
    ("A_CI", "-a-ci", "ACI", ["C", "W"]),
    ("A_PC", "-a-pc", "APC", ["C", "W", "Z"]),
    ("A_CI_PC", "-a-ci-pc", "ACIPC", ["C", "W", "Z"]),
    ("C_RG2b", "-c-rg2b", "CRG2B", ["C"]),
    ("A_RG2b", "-a-rg2b", "ARG2B", ["C", "W"]),
)
NATIVE = (
    "grc_v4_profile", "grc_v4_codec", "grc_v4_state", "grc_v4_geometry",
    "grc_v4_transport", "grc_v4_step", "grc_v4_candidate_c",
    "grc_v4_candidate_a", "grc_v4_realizations", "grc_v4_ci", "grc_v4_pc",
    "grc_v4_numerics", "grc_v4_certification", "grc_v4_lifecycle",
    "grc_9_v4_identity", "grc_9_v4_contracts", "grc_9_v4_lifecycle",
    "grc_9_v4_owner", "grc_9_v4_expansion", "grc_9_v4_crossing",
    "grc_9_v4_api_lifecycle", "grc_9_v4_basin", "grc_9_v4",
    "grc_9_v4_crg2b_connected", "grc_9_v4_arg2b_connected",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False).encode()).hexdigest()


def sealed(value):
    body = {k: v for k, v in value.items() if k != "record_digest"}
    return dict(body, record_digest=digest(body))


def path(name):
    target = (ROOT / name).resolve()
    need(not Path(name).is_absolute() and target.is_relative_to(ROOT),
         "source path escapes repository")
    return target


def sha(name):
    return hashlib.sha256(path(name).read_bytes()).hexdigest()


def read(name):
    raw = path(name).read_bytes()
    return json.loads(lzma.decompress(raw) if name.endswith(".xz") else raw)


def obligations(value):
    result = set()
    if isinstance(value, dict):
        identifier = value.get("obligation_id")
        if isinstance(identifier, str) and "-VO-NATIVE-" in identifier:
            need(value.get("status") in ("pending", "pending_forward") and
                 value.get("destination") == "P9-9.1a", "native obligation disposition drift")
            result.add(identifier)
        for child in value.values():
            result.update(obligations(child))
    elif isinstance(value, list):
        for child in value:
            result.update(obligations(child))
    return result


def authority_map(sources):
    rows, all_obligations = [], set()
    for family, suffix, code, channels in FAMILIES:
        name = "specs/grc-9-v4-spark-completion" + suffix + "-source-manifest.json"
        manifest = read(name)
        need(manifest["native_support_added"] == [] and
             manifest["native_implementation_destination"] == "P9-9.1a",
             "research manifest cannot grant native support")
        sources.add(name)
        found = set()
        for item in manifest["chain"]:
            need(sha(item["path"]) == item["sha256"], "authority chain drift: " + item["path"])
            sources.add(item["path"])
            if item["stage"] == "authority":
                found.update(obligations(read(item["path"])))
        prefix = "SC-" + (code + "-" if code else "") + "VO-NATIVE-"
        expected = {prefix + "NUMERICS", prefix + "LIFECYCLE"}
        need(expected <= found, "missing native family obligations: " + family)
        all_obligations.update(expected)
        rows.append(dict(family=family, source_manifest=name, contract_ids=manifest["contract_ids"],
                         state_channels=channels, native_obligations=sorted(expected),
                         native_support=False, implementation_status="not_started"))
    name = "specs/grc-9-v4-spark-completion-earlier-source-manifest.json"
    manifest = read(name); sources.add(name)
    need(manifest["native_support_added"] == [], "earlier adoption grants no native support")
    found = set()
    for item in manifest["chain"]:
        need(sha(item["path"]) == item["sha256"], "earlier chain drift: " + item["path"])
        sources.add(item["path"])
        if item["stage"] == "authority":
            found.update(obligations(read(item["path"])))
    expected = {f"SC-EARLY-{code}-VO-NATIVE-{kind}"
                for code in ("COS", "CCI", "CPC", "CCIPC", "AOS")
                for kind in ("NUMERICS", "LIFECYCLE")}
    need(found == expected, "earlier endpoint obligation population changed")
    all_obligations.update(found)
    need(len(all_obligations) == 30, "wrong native obligation population")
    return dict(families=rows, earlier_endpoint_obligations=sorted(found),
                native_obligation_count=len(all_obligations))


def continuity_probe():
    from pygrc.models.grc_v4_geometry import (
        GRCV4Graph, OrientedEdge, GRCV4Differential, VertexScalar, PhysicalFlux)
    from pygrc.models.grc_v4_transport import provisional_continuity, ChargeEvaluation
    from pygrc.models.grc_v4_profile import list_supported_profiles, get_supported_profile
    from pygrc.models.grc_v4_numerics import ExactBackend, exact_backend

    with exact_backend(ExactBackend.FLINT):
        profile = next(p for p in map(get_supported_profile, sorted(list_supported_profiles()))
                       if p.identity_payload.profile_family_id == "C_OS")
        graph = GRCV4Graph(("a", "b"), (OrientedEdge("e", "a", "b"),))
        before = VertexScalar(graph, (1.0, 2.0))
        after = provisional_continuity(before, PhysicalFlux(graph, (2.0**-53,)), 1.0,
                                      differential=GRCV4Differential(graph, profile.params_resolved.common))
        charge = ChargeEvaluation(after, 3.0, profile)
        drift = sum(map(Fraction, after.values)) - 3
        need(after.values == (1.0 - 2.0**-53, 2.0) and drift == -Fraction(1, 2**53),
             "native continuity counterexample changed")
        need(charge.actual == 3 and charge.residual == 0 and charge.admitted,
             "native diagnostic counterexample changed")
        return dict(input_C=["1", "2"], duration="1", prescribed_edge_current="1/9007199254740992",
                    output_C=[str(Fraction(x)) for x in after.values],
                    rounded_charge=charge.actual, reported_residual=charge.residual,
                    tolerance_admitted=charge.admitted, exact_charge_drift=str(drift),
                    scope="prescribed-current continuity kernel, not a selected C_OS solver or trajectory")


def certificate_budget(sources):
    from flint import fmpq, fmpq_mat
    declaration_name = EARLY + "CEarlierDomain.json"
    proof_name = EARLY + "CEarlierProofs.json"
    sources.update((declaration_name, proof_name, EVIDENCE + "SC2SourceBeat.json.xz"))
    declaration, proofs = read(declaration_name), read(proof_name)
    need(sealed(declaration) == declaration and sealed(proofs) == proofs, "certificate record digest")
    proof = proofs["proofs"]["C_OS"]
    need(proofs["domain_digest"] == declaration["record_digest"] == proof["domain_digest"],
         "certificate/domain mismatch")
    d, n = declaration["resource_dimension"], 15
    need(d == n - 1, "wrong charge-tangent dimension")
    T = fmpq_mat([[fmpq(x) for x in row] for row in declaration["basis"]])
    r = list(map(fmpq, declaration["axis_radii"]))
    need(T.nrows() == T.ncols() == len(r) == d and min(r) > 0, "invalid domain basis/radii")
    diag = lambda values: fmpq_mat([[values[i] if i == j else 0 for j in range(d)] for i in range(d)])
    E = fmpq_mat([[int(i == j) if i < d else -1 for j in range(d)] for i in range(n)])
    R = fmpq_mat([[int(i == j) for j in range(n)] for i in range(d)])
    S = E * T * diag(r)
    U = diag([1/x for x in r]) * T.inv() * R
    need(U * S == diag([1] * d), "invalid chart left inverse")
    need(all(sum(S[i, j] for i in range(n)) == 0 for j in range(d)), "chart not charge tangent")
    need(sum(fmpq(x) for x in declaration["center"].values()) == 21, "center charge")
    norm = max(sum(abs(U[i, j]) for j in range(n)) for i in range(d))
    margin = fmpq(proof["strict_image_margin"][0])
    need(0 < fmpq(proof["contraction"][1]) < 1 and margin > 0, "trap bounds")
    prepared = read(EVIDENCE + "SC2SourceBeat.json.xz")["checks"]["prepared"]
    input_rounding = {}
    for role in ("current", "reset"):
        exact = [Fraction(x) for x in prepared[role + "_prestate"].values()]
        need(sum(exact) == 21, "source charge")
        input_rounding[role] = str(sum(Fraction(float(x)) for x in exact) - 21)
    need(input_rounding == {"current": str(Fraction(1, 2**50)), "reset": "0"}, "input rounding changed")
    return dict(resource_dimension=d, U_S_identity=True, S_exactly_charge_tangent=True,
                center_charge="21", chart_infinity_norm=str(norm), image_margin_lower=str(margin),
                sufficient_tangent_componentwise_error_strictly_below=str(margin/norm),
                approximate_threshold_for_display=float(margin/norm),
                native_full_step_error_proved=False, diagnostic_agreement_proved=False,
                source_binary64_exact_charge_drift=input_rounding)


def run():
    import flint

    sources = {DOCUMENT, SCRIPT, "specs/grc-v4-numerical-policy.md"}
    sources.update("src/pygrc/models/" + name + ".py" for name in NATIVE)
    mapped = authority_map(sources)
    probe = continuity_probe()
    budget = certificate_budget(sources)
    for module in tuple(sys.modules.values()):
        filename = getattr(module, "__file__", None)
        if filename:
            module_path = Path(filename).resolve()
            if module_path.is_relative_to(ROOT / "src/pygrc") and module_path.suffix == ".py":
                sources.add(str(module_path.relative_to(ROOT)))
    return dict(authority_map=mapped, continuity_probe=probe, certificate_budget=budget,
                execution_environment=dict(python=sys.version.split()[0], python_flint=flint.__version__,
                                           backend="FLINT", arithmetic="binary64 kernel / exact fmpq certificate algebra"),
                source_bindings=[dict(path=name, sha256=sha(name)) for name in sorted(sources)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = path(RECORD)
    if args.write:
        need(not target.exists(), "refusing to overwrite retained contract checks")
        start = time.monotonic()
        result = run()
        value = sealed(dict(schema="p9-native-spark-contract-map-v1", leaf="P9-9.1a.1",
                            status="mapping_complete_pending_review", user_accepted=False,
                            baseline_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                            native_steps=0, native_events=0, native_completion_support=False,
                            hierarchy_support=False, numerical_campaigns=0,
                            kernel_probe_calls=1, validation_wall_seconds=time.monotonic()-start,
                            **result))
        target.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n")
    else:
        value = read(RECORD)
        need(sealed(value) == value, "contract-map record digest")
        need(value["schema"] == "p9-native-spark-contract-map-v1" and value["leaf"] == "P9-9.1a.1"
             and value["status"] == "mapping_complete_pending_review" and not value["user_accepted"]
             and value["native_steps"] == value["native_events"] == value["numerical_campaigns"] == 0
             and not value["native_completion_support"] and not value["hierarchy_support"],
             "contract-map scope drift")
        for item in value["source_bindings"]:
            need(sha(item["path"]) == item["sha256"], "contract-map source drift: " + item["path"])
        result = run()
        need(all(value[key] == item for key, item in result.items()), "contract-map result changed")
    print(json.dumps(dict(status="P991A1_NATIVE_SPARK_CONTRACT_PASS", families=10,
                          native_obligations=value["authority_map"]["native_obligation_count"],
                          native_steps=0, numerical_campaigns=0,
                          source_bindings=len(value["source_bindings"]),
                          recorded_validation_seconds=value["validation_wall_seconds"])))


if __name__ == "__main__":
    main()

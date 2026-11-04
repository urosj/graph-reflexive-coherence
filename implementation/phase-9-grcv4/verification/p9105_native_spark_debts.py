"""Reconcile accepted spark research and native evidence; no numerical execution."""

import argparse
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import subprocess

import p991a7_support as support

ROOT = support.ROOT
INV = "implementation/investigations/grc9v4-constitutive-design/"
BASE = "implementation/phase-9-grcv4/tranche-10/"
LEDGER = INV + "evidence/spark-completion/native/ClaimDebtLedger.json"
DECISION = INV + "decisions/SparkCompletionNativeDebtReconciliation.md"
EARLY = INV + "decisions/spark-completion-earlier/Authority.json"
EARLY_MANIFEST = "specs/grc-9-v4-spark-completion-earlier-source-manifest.json"
INHERITED = INV + "decisions/D10DebtClaimTransformationLedger.json"
RESEARCH_LEDGER = (
    INV
    + "evidence/spark-completion/applicability/earlier-closure/EarlierSC3ClaimDebtLedger.json"
)
REGRESSION = BASE + "P9-10.3-NativeSpark-Regressions.json"
REGRESSION_ACCEPTANCE = BASE + "P9-10.3-NativeSpark-Acceptance.json"
PUBLICATION_ACCEPTANCE = BASE + "P9-10.4-NativeSpark-Acceptance.json"
BASELINE = "215509f4"
FAMILIES = tuple(row[0] for row in support.ROSTER)
HIERARCHY = "SC-VO-HIERARCHY-EVOLUTION"
EXCLUSIONS = [
    "arbitrary graphs, profiles, contexts, durations or initial states",
    "general autonomous topology selection or universal spark formation",
    "hierarchy evolution beyond atomic new-child occurrence records",
    "distributed exactly-once accounting across disconnected processes",
    "C1 regularity of RG2b sections or classical section spectra",
    "numeric abundance, mechanism necessity, or independent child subsystems",
    "full GRC9V4 conformance or P9-G4 acceptance",
]
need, seal = support.need, support.seal


def ref(root, path, pointer=None):
    need(
        not Path(path).is_absolute() and ".." not in Path(path).parts,
        "nonportable reference",
    )
    result = dict(
        path=path, sha256=sha256((Path(root) / path).read_bytes()).hexdigest()
    )
    if pointer is not None:
        result["json_pointer"] = pointer
    return result


@lru_cache(maxsize=256)
def baseline_bytes(root, path):
    return subprocess.check_output(["git", "show", BASELINE + ":" + path], cwd=root)


def frozen(root, path):
    raw = (Path(root) / path).read_bytes()
    need(
        raw == baseline_bytes(str(Path(root).resolve()), path),
        "accepted source changed: " + path,
    )
    return json.loads(raw)


def _scientific_sources(root, evidence):
    manifest = frozen(root, evidence["source_manifest"])
    source = next(r["path"] for r in manifest["chain"] if r["stage"] == "authority")
    value = frozen(root, source)
    acceptance = frozen(root, value["acceptance"]["path"])
    need(
        acceptance["status"] == "accepted_bounded_scientific_completion",
        "research acceptance absent",
    )
    return source, value, manifest


def build(root=ROOT, *, checked_support=None):
    root = Path(root).resolve()
    native = support.checked(root) if checked_support is None else checked_support
    need(native == frozen(root, support.RECORD), "not the accepted native population")
    regression = frozen(root, REGRESSION)
    decision = frozen(root, REGRESSION_ACCEPTANCE)
    publication = frozen(root, PUBLICATION_ACCEPTANCE)
    need(
        decision["user_accepted"] is True
        and decision["execution_record_digest"] == regression["record_digest"]
        and regression["tests_run"] == 28
        and all(r["status"] == "passed" for r in regression["regressions"]),
        "integration evidence is not accepted",
    )
    need(
        publication["user_accepted"] is True
        and publication["families"] == list(FAMILIES),
        "workflow publication is not accepted",
    )
    early = frozen(root, EARLY)
    need(
        early["status"] == "accepted_bounded_scientific", "earlier endpoints unaccepted"
    )
    frozen(root, early["acceptance"]["path"])
    early_manifest = frozen(root, EARLY_MANIFEST)
    inherited = frozen(root, INHERITED)
    frozen(root, RESEARCH_LEDGER)
    claims, debts, obligations, families = [], [], [], []
    sources = {
        support.RECORD,
        REGRESSION,
        REGRESSION_ACCEPTANCE,
        PUBLICATION_ACCEPTANCE,
        EARLY,
        EARLY_MANIFEST,
        early["acceptance"]["path"],
        RESEARCH_LEDGER,
        INHERITED,
        "specs/grc-9-v4-native-spark-lifecycle.md",
    }
    for source in early_manifest["chain"]:
        sources.add(source["path"])
        need(
            ref(root, source["path"])["sha256"] == source["sha256"],
            "earlier endpoint propagation changed",
        )
    subjects = {r["family"]: r for r in native["families"]}
    for evidence in native["evidence"]:
        family = evidence["family"]
        path, authority, manifest = _scientific_sources(root, evidence)
        sources.update(
            (path, evidence["source_manifest"], authority["acceptance"]["path"])
        )
        for s in manifest["chain"]:
            sources.add(s["path"])
            need(
                ref(root, s["path"])["sha256"] == s["sha256"],
                "research propagation changed",
            )
        vo_map = {
            r["obligation_id"]: (i, r, path)
            for i, r in enumerate(authority["verification_obligations"])
        }
        vo_map.update(
            {
                r["obligation_id"]: (i, r, EARLY)
                for i, r in enumerate(early["verification_obligations"])
                if r["family"] == family
            }
        )
        need(
            set(vo_map) == set(evidence["native_obligations"]),
            "missing or extra family obligation",
        )
        family_claims = []
        for i, claim in enumerate(authority["claims"]):
            family_claims.append(claim["claim_id"])
            claims.append(
                dict(
                    claim_id=claim["claim_id"],
                    family=family,
                    scientific_claim=claim,
                    source_ref=ref(root, path, f"/claims/{i}"),
                    native_evidence_relation="bounded_conformance_not_backward_scientific_support",
                )
            )
        for identifier in evidence["native_obligations"]:
            i, old, source = vo_map[identifier]
            split = "hierarchy" in old.get("obligation", "").lower()
            obligations.append(
                dict(
                    obligation_id=identifier,
                    family=family,
                    predecessor=old,
                    source_ref=ref(root, source, f"/verification_obligations/{i}"),
                    disposition="split_bounded_native_discharged_hierarchy_retained"
                    if split
                    else "resolved_bounded_native",
                    native_portion_discharged=True,
                    evidence_family=family,
                    residual_obligation_ids=[HIERARCHY] if split else [],
                    resolved_scope=(
                        "Exact selected source/target, both-role full represented map and charge/diagnostic certification."
                        if identifier.endswith("NUMERICS")
                        else "Actual source/event, both-role transfer, positive current window, reset comparison with zero gain, "
                        "atomic occurrence/new-child accounting, invalidation, rollback and replay within the shared publication authority."
                    ),
                )
            )
        for i, debt in enumerate(authority["debts"]):
            identifier = debt["debt_id"]
            is_aggregate = identifier.startswith("SC-DEBT-")
            relevant = debt.get(
                "verification_obligation_ids", [debt.get("verification_obligation")]
            )
            relevant = [x for x in relevant if x]
            hierarchy = identifier in (
                "SC-DEBT-ORGANIZATION",
                "SC-DEBT-TEMPORAL-LIFECYCLE",
            ) or any(
                o["obligation_id"] in relevant and o["residual_obligation_ids"]
                for o in obligations
            )
            debts.append(
                dict(
                    debt_id=identifier,
                    predecessor_status=debt["status"],
                    predecessor=ref(root, path, f"/debts/{i}"),
                    origin_ledger=debt["origin_ledger"],
                    disposition="partially_resolved_bounded_native"
                    if hierarchy
                    else "resolved_bounded_scientific_and_native",
                    resolved_scope=debt.get("resolved_scope", debt.get("scope")),
                    native_resolution="Accepted numerical and lifecycle evidence now realizes the selected scientific contract at the listed exact subjects.",
                    evidence_families=list(FAMILIES) if is_aggregate else [family],
                    verification_obligation_ids=relevant,
                    successor_claim_ids=debt["successor_claim_ids"],
                    residual_obligation_ids=[HIERARCHY] if hierarchy else [],
                    broader_scope_exclusions=EXCLUSIONS,
                )
            )
            sources.add(debt["origin_ledger"])
        families.append(
            dict(
                family=family,
                scientific_authority=ref(root, path),
                scientific_acceptance=authority["acceptance"],
                propagation_manifest=ref(root, evidence["source_manifest"]),
                scientific_claim_ids=family_claims,
                adopted_endpoint_successor=(
                    dict(
                        authority=ref(root, EARLY),
                        acceptance=early["acceptance"],
                        propagation_manifest=ref(root, EARLY_MANIFEST),
                        endpoint=next(
                            e for e in early["endpoints"] if e["family"] == family
                        ),
                        contract_ids=[
                            r["equation_contract_id"]
                            for r in early["contracts"]
                            if r["equation_contract_id"]
                            in set(
                                k
                                for o in early["verification_obligations"]
                                if o["family"] == family
                                for k in o["contract_ids"]
                            )
                        ],
                    )
                    if family in early["scope"]["adopted_earlier_endpoints"]
                    else None
                ),
                contract_ids=evidence["contract_ids"],
                native_obligation_ids=evidence["native_obligations"],
                state_channels=evidence["state_channels"],
                native_evidence=evidence,
                exact_subject=subjects[family],
                numerical_basis="Accepted full-map represented-error, exact charge and actual predicate certificates; not a solver residual or a successful orbit alone.",
                lifecycle_basis="Accepted family full current/reset campaigns and complete cold replay, plus shared P9-10.3 lifecycle and all-ten persistence/identity regressions.",
                limitations=(
                    "Unique Lipschitz section; no C1 section claim."
                    if "RG2b" in family
                    else "Full selected joint-root error included; no fixed-geometry or overlap substitute."
                    if "CI" in family
                    else "Selected staged map and all physical writers are included."
                ),
            )
        )
    for debt in debts:
        if debt["debt_id"].startswith("SC-DEBT-"):
            kind = (
                "NUMERICS"
                if debt["debt_id"] in ("SC-DEBT-STABILITY", "SC-DEBT-NONEMPTY-DOMAIN")
                else "LIFECYCLE"
            )
            debt["contributing_obligation_ids"] = [
                o["obligation_id"]
                for o in obligations
                if o["obligation_id"].endswith(kind)
            ]
    for i, claim in enumerate(early["claims"]):
        claims.append(
            dict(
                claim_id=claim["claim_id"],
                scientific_claim=claim,
                source_ref=ref(root, EARLY, f"/claims/{i}"),
                family=claim["family"],
                native_evidence_relation="adopted_endpoint_conformance_no_new_birth",
            )
        )
    inherited_rows = [
        dict(
            debt_id=r["debt_id"],
            source_ref=ref(root, INHERITED, f"/debt_transformations/{i}"),
            predecessor_transformation=r["transformation"],
            successor_claim_ids=r["successor_claim_ids"],
            verification_obligation=r["verification_obligation"],
            disposition="unchanged_by_native_spark_campaigns",
            reason="The spark contracts do not prove the broader inherited statement; preserve its existing authority and activation condition.",
            activation_condition=r.get("activation_condition"),
        )
        for i, r in enumerate(inherited["debt_transformations"])
    ]
    residual = dict(
        obligation_id=HIERARCHY,
        status="deferred_not_discharged",
        destination="P9-10.6 support boundary; separate future hierarchy implementation",
        split_from=[
            r["obligation_id"] for r in obligations if r["residual_obligation_ids"]
        ],
        already_supported="Atomic insertion of canonical new-child records together with one consumed event occurrence.",
        remaining="Broader hierarchy tracking/evolution is not enabled or validated by these campaigns.",
        source_ref=ref(root, "specs/grc-9-v4-native-spark-lifecycle.md"),
    )
    need(
        len(obligations) == 30
        and len({o["obligation_id"] for o in obligations}) == 30
        and len(families) == 10
        and len(debts) == 14,
        "incomplete ledger reconciliation",
    )
    for path in sorted(sources):
        frozen(root, path) if path.endswith(".json") else need(
            (root / path).read_bytes() == baseline_bytes(str(root), path),
            "changed accepted document: " + path,
        )
    return seal(
        dict(
            schema="grc9v4-native-spark-claim-debt-ledger-v1",
            date="2026-11-04",
            leaf="P9-10.5",
            status="reconciled_bounded_native_pending_acceptance",
            reconciliation_user_accepted=False,
            basis="Existing separately accepted scientific and native results; user directed scoped discharge, not new scientific authority.",
            predecessor_ledger=ref(root, RESEARCH_LEDGER),
            scientific_claims=claims,
            debts=debts,
            verification_obligations=obligations,
            families=families,
            inherited_debts=inherited_rows,
            residual_obligations=[residual],
            inherited_non_spark_scope=dict(
                abundance="Unchanged: completion gain does not define numeric abundance.",
                ATC="Unchanged: nine-port completion does not close general autonomous topology-change debts.",
                basin_diagnostic="Preserve its separate scientific/native acceptances; geometric child completion does not redefine represented-flow basins.",
            ),
            accepted_native_support=ref(root, support.RECORD),
            integration_acceptance=ref(root, REGRESSION_ACCEPTANCE),
            publication_acceptance=ref(root, PUBLICATION_ACCEPTANCE),
            source_refs=[ref(root, p) for p in sorted(sources)],
            counts=dict(
                families=10,
                original_native_obligations=30,
                native_portions_discharged=30,
                fully_scoped_native_resolutions=26,
                split_with_hierarchy_residual=4,
                spark_debt_transformations=14,
                inherited_debts_preserved=len(inherited_rows),
            ),
            scope=dict(
                exact_declarations_and_certificate_domains=True,
                new_scientific_claims=[],
                historical_claim_classes_preserved=True,
                historical_records_unchanged=True,
                native_support_added=[],
                new_numerical_trajectories=0,
                hierarchy_support=False,
                full_GRC9V4_conformance=False,
                G4_accepted=False,
                exclusions=EXCLUSIONS,
            ),
            reconciliation_sources=[
                ref(root, p)
                for p in (
                    DECISION,
                    "implementation/phase-9-grcv4/verification/p9105_native_spark_debts.py",
                    "implementation/phase-9-grcv4/verification/test_p9105_native_spark_debts.py",
                )
            ],
            next_work="Review P9-10.5 reconciliation, then P9-10.6 reviewed support/residuals/handoff and explicit G4 decision.",
        )
    )


def validate(value, expected):
    need(value == seal(value), "unsealed native debt ledger")
    need(
        value == expected,
        "native debt disposition, authority, exact subject or residual changed",
    )
    return value


def checked(root=ROOT):
    root = Path(root).resolve()
    return validate(json.loads((root / LEDGER).read_bytes()), build(root))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prepare", action="store_true")
    args = ap.parse_args()
    if args.prepare:
        value = build()
        destination = ROOT / LEDGER
        need(not destination.exists(), "refuse to overwrite a retained ledger")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(value, indent=2) + "\n")
    else:
        value = checked()
    print("P9105_NATIVE_DEBTS_PASS", json.dumps(value["counts"]), "native_rerun=false")

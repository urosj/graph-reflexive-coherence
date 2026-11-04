"""Final bounded support disposition; authenticate decisions, never run trajectories."""

import json
from hashlib import sha256
from pathlib import Path
import subprocess

from p9105_native_spark_epoch import seal

ROOT = Path(__file__).resolve().parents[3]
BASELINE = "33eecf24"
BASE = "implementation/phase-9-grcv4/"
INV = "implementation/investigations/grc9v4-constitutive-design/"
RECORD = BASE + "tranche-10/P9-10.6-ReleaseDisposition.json"
FAMILIES = sorted(f"{c}_{r}" for c in ("A", "C") for r in ("OS", "CI", "PC", "CI_PC", "RG2b"))
SOURCES = (
    BASE + "tranche-7/ProfileG2Registry.json",
    BASE + "tranche-7/P9-7.7-AggregateAcceptance.json",
    BASE + "tranche-7/P9-7.8-G3Acceptance.json",
    BASE + "tranche-9/P9-Tranches8-9-AllTenAcceptance.json",
    BASE + "tranche-9/P9-9.1a.7-Support.json",
    BASE + "tranche-10/P9-10.1a-NativeAcceptance.json",
    *(BASE + "tranche-10/" + name + "-Acceptance.json" for name in (
        "P9-10.1b", "P9-10.1c", "P9-10.2",
        "P9-10-AOS", "P9-10-CPC", "P9-10-CCIPC", "P9-10-ACIPC",
        "P9-10-CRG2b", "P9-10-ARG2b", "P9-10.3", "P9-10.4",
        "P9-10.3-NativeSpark", "P9-10.4-NativeSpark", "P9-10.5-NativeSpark",
    )),
    INV + "evidence/spark-completion/native/ClaimDebtLedger.json",
)


def build(root=ROOT):
    root = Path(root)
    refs = []
    for path in SOURCES:
        raw = (root / path).read_bytes()
        original = subprocess.check_output(["git", "show", BASELINE + ":" + path], cwd=root)
        if raw != original:
            raise ValueError("accepted release source changed: " + path)
        value = json.loads(raw)
        refs.append(dict(path=path, sha256=sha256(raw).hexdigest(), record_digest=value.get("record_digest")))
    return seal(dict(
        schema="p9106-bounded-release-disposition-v1",
        date="2026-11-04",
        status="bounded_support_and_acceptance_recorded_G4_pending",
        acceptance_basis="User requested final support and acceptance under P9-10.6; explicitly reserved G4 as its own decision.",
        user_accepted=True, P9_10_6_closed=True,
        tranche10_work_complete_at_declared_scope=True,
        Phase9_closed=False, G4_accepted=False,
        G4_disposition="pending_separate_explicit_review_and_decision",
        full_GRC9V4_conformance=False,
        families=FAMILIES, pending_families_within_declared_scopes=[],
        support_sets={
            "generic": dict(source=SOURCES[0], scope="registry exact accepted G2 declarations; G3 admits their specialization"),
            "specialization_and_lifecycle": dict(source=SOURCES[3], scope="all ten individually accepted Tranche 8-9 source/target identities and finite domains"),
            "disabled_compatibility": dict(source=SOURCES[3], accepted_source_cells=40, scope="source-model cells only; exact expanded-target compatibility uses separate P9-10.1b/c subjects"),
            "basins_and_conservation": dict(sources=list(SOURCES[5:15]), scope="exact first-four v2 targets and six later family targets; independent rows/classification and saved replay/charge evidence"),
            "native_spark_completion": dict(source=SOURCES[4], exact_declarations=20, scope="ten explicit optional source/target policies, both-role certificates, actual entry, two-positive-step windows and cold replay; not arbitrary members of a family"),
        },
        acceptance_chain=dict(ordinary_regressions=SOURCES[15], ordinary_examples=SOURCES[16], native_regressions=SOURCES[17], native_examples=SOURCES[18], native_debt_reconciliation=SOURCES[19]),
        residuals=dict(
            native_obligations=30, native_portions_discharged=30,
            fully_scoped_native_resolutions=26, split_with_hierarchy_residual=4,
            hierarchy_obligation="SC-VO-HIERARCHY-EVOLUTION",
            hierarchy_disposition="deferred_separately_authorized_future_work",
            spark_debt_transformations=14, inherited_D10_transformations_preserved=29,
            ledger=SOURCES[20],
        ),
        retained_limits=[
            "Exact declarations, graphs, contexts, histories, horizons and certificate domains only; support sets are distinct and not interchangeable.",
            "Historical pending fields remain unchanged; the cited later decisions supply current acceptance and debt dispositions.",
            "CI fixed-geometry current bounds are not exact joint-root claims or uniform trajectory enclosures; retain certificate and resolution limits.",
            "Carrier-effect margins remain pointwise; nonzero stored Z alone does not prove an effect above numerical error.",
            "RG2b uses accepted Lipschitz sections; C1 regularity and classical section spectra remain unresolved.",
            "Canonical mechanical expansion is supported; general autonomous topology selection and arbitrary-graph fission are not granted.",
            "Completed spark is the selected geometric organization convention, not a new independent subsystem or multiple full-state attractors.",
            "Atomic new-child insertion and local occurrence accounting are supported; broader hierarchy evolution and distributed exactly-once are not.",
            "No numeric abundance, universal formation claim, or silent legacy fallback for optional exact spark policies.",
            "Original excluded cases and deferred large diagnostics remain exclusions and unexecuted diagnostics, not passing evidence.",
        ],
        new_support=[], new_scientific_authority=[], new_numerical_trajectories=0,
        original_evidence_relabelled=False,
        verification_mode="accepted_record_identity_and_scope_only_no_numerical_rerun",
        next_action="Separate P9-G4 release review/decision against these bounded support sets; no new implementation or campaign authorized.",
        source_refs=refs,
    ))


def validate(value, expected):
    if value != expected:
        raise ValueError("release disposition or accepted source binding changed")
    return value


def checked(root=ROOT):
    return validate(json.loads((Path(root) / RECORD).read_bytes()), build(root))


if __name__ == "__main__":
    value = checked()
    print(json.dumps(dict(status=value["status"], families=len(value["families"]), G4_accepted=False, native_rerun=False)))

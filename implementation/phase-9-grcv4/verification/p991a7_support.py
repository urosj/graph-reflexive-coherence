"""Reconcile accepted native campaigns; never execute a numerical trajectory."""

import argparse
import importlib
import json
import lzma
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "implementation/phase-9-grcv4/tranche-9/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/"
sys.path[:0] = [str(ROOT / "src"), str(ROOT / (SIDE + "tool/src"))]
from pygrc.models.grc_9_v4_completion_codec import digest  # noqa: E402
from pygrc.models.grc_9_v4_spark_contracts import GRC9V4SparkConfiguration  # noqa: E402
from pygrc.models.grc_9_v4_spark_support import declaration  # noqa: E402

ASSET = "src/pygrc/models/grc_v4_assets/grc-9-v4-native-spark-support.json"
RECORD = BASE + "P9-9.1a.7-Support.json"
RUNTIME = ("src/pygrc/models/grc_9_v4.py", "src/pygrc/models/grc_9_v4_spark_support.py")
AUTHORITY = BASE + "P9-9.1a.1-Verification.json"
ROSTER = (
    ("C_OS", "", "1ec198b2"),
    ("C_CI", "CCI", "88a1c6b1"),
    ("C_PC", "CPC", "31d1aba7"),
    ("C_CI_PC", "CCIPC", "e2cfad85"),
    ("A_OS", "AOS", "4587185f"),
    ("A_CI", "ACI", "5b92524c"),
    ("A_PC", "APC", "10277f05"),
    ("A_CI_PC", "ACIPC", "7252dd6d"),
    ("C_RG2b", "CRG2b", "528736b9"),
    ("A_RG2b", "ARG2b", "528736b9"),
)
# Fixed retained campaign files, not values supplied by discovery or callers.
CAMPAIGN_PINS = {
    "C_OS": "84292e50ce6df37f1a64d38776facc78dffaed62afab67777773a69b57489e31",
    "C_CI": "45fc8f7a30f0cc27826e56d94da37c0e5e8496dc9b790edfc02c9d7b8899f8f5",
    "C_PC": "00890de9b5fb1c16ca530a694307717ce56e8f59da5dc9b5254d1201b7ba8ca6",
    "C_CI_PC": "48e625099afd4a4137a1dd010e83b2bd1cf1104f76835b3c7f332d29d9568676",
    "A_OS": "52104272715a612a6880f21d2e01bf607721dc26047699ae8bcd6ec549733c80",
    "A_CI": "4c879e99606f87652c463a16d598853f3f836771a55be2d915ec399e1de539e3",
    "A_PC": "03de8725555b9be65b0b0f0fb6f36912a52c4100cbec3d8d0339f8d741eeaf3b",
    "A_CI_PC": "23e899d1e6e72f0aa61d32ce62f5b098852bdd97094044286640c185674d1903",
    "C_RG2b": "f84ac243ea09a53986b23c487513c49014c390917e653cafe8ce780b20c23a49",
    "A_RG2b": "94823f115876c5593318c5a881d8356c4e998630668d9c1938c14d740b341ab3",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path):
    raw = path.read_bytes()
    return json.loads(lzma.decompress(raw) if path.suffix == ".xz" else raw)


def prefix(tag):
    return BASE + ("P9-9.1a.6-" + tag + ".5" if tag else "P9-9.1a.5")


def inputs(root, tag):
    with lzma.open(root / (prefix(tag) + "-inputs.jsonl.xz"), "rt") as stream:
        value = json.loads(next(stream))
        need(not stream.read().strip(), "unexpected additional campaign input")
    return value


def seal(value):
    return {
        **value,
        "record_digest": digest(
            {k: v for k, v in value.items() if k != "record_digest"}
        ),
    }


def _build(root=ROOT, *, history=False):
    root = Path(root)
    authority = load(root / AUTHORITY)["authority_map"]
    family_authority = {r["family"]: r for r in authority["families"]}
    families, evidence, sources = [], [], []
    for family, tag, commit in ROSTER:
        path = prefix(tag) + "-Campaign.json" + ("" if "RG2b" in family else ".xz")
        raw = (root / path).read_bytes()
        need(
            sha256(raw).hexdigest() == CAMPAIGN_PINS[family],
            "changed campaign: " + family,
        )
        v = load(root / path)
        need(
            v["native_endpoint_verified"] is True
            and v["native_completion_support"] is False
            and v["user_accepted"] is False
            and v["full_trajectory_runs"] == 2
            and v["physical_supporting_tail_steps"] == 0,
            "changed historical scope",
        )
        roles = {
            role: {
                k: v["roles"][role][k]
                for k in ("entry", "completion", "target_steps", "local_gain")
            }
            for role in ("current", "reset")
        }
        need(
            roles["current"]["local_gain"] == 1
            and roles["reset"]["local_gain"] == 0
            and all(
                r["completion"] - r["entry"] == 2
                and r["completion"] == r["target_steps"]
                for r in roles.values()
            ),
            "endpoint/window/gain mismatch",
        )
        review = prefix(tag) + "-Review.md"
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=root, check=True
        )
        review_raw = subprocess.check_output(
            ["git", "show", commit + ":" + review], cwd=root
        )
        current_review = subprocess.check_output(
            ["git", "show", "528736b9:" + review], cwd=root
        )
        need(
            (root / review).read_bytes() == current_review,
            "changed reviewed campaign documentation",
        )
        data = inputs(root, tag)
        subjects = []
        for role in ("source", "target"):
            config = GRC9V4SparkConfiguration.from_payload(
                data[role + "_configuration"]
            )
            need(
                config.reference.profile.FAMILY == family
                and str(config.current.charge) == v["exact_charge"]
                and config.policy.step_duration == v["duration"],
                "wrong declaration subject",
            )
            subjects.append(
                dict(
                    role=role,
                    declaration_digest=declaration(config),
                    model_identity=config.model_identity,
                    complete_profile_id=config.reference.profile.complete_profile_id,
                    graph_digest=config.reference.graph.graph_digest,
                    charge=str(config.current.charge),
                )
            )
        certificate_ids = [digest(c) for c in data["certificates"]]
        if "certificate_ids" in v:
            need(certificate_ids == v["certificate_ids"], "wrong target certificates")
        row = dict(
            family=family,
            campaign_record_digest=v["record_digest"],
            numerical_policy=config.reference.profile.NUMERICS,
            duration=v["duration"],
            subjects=subjects,
            certificate_ids=certificate_ids,
            roles=roles,
        )
        families.append(row)
        a = family_authority[family]
        native = list(a["native_obligations"])
        earlytag = "COS" if not tag else tag
        native += [
            n
            for n in authority["earlier_endpoint_obligations"]
            if n.startswith("SC-EARLY-" + earlytag + "-")
        ]
        evidence.append(
            dict(
                family=family,
                campaign={"path": path, "sha256": CAMPAIGN_PINS[family]},
                accepted_commit=commit,
                accepted_review={
                    "path": review,
                    "sha256": sha256(review_raw).hexdigest(),
                },
                current_review={
                    "path": review,
                    "sha256": sha256(current_review).hexdigest(),
                },
                input={
                    "path": prefix(tag) + "-inputs.jsonl.xz",
                    "sha256": sha256(
                        (root / (prefix(tag) + "-inputs.jsonl.xz")).read_bytes()
                    ).hexdigest(),
                },
                source_manifest=a["source_manifest"],
                contract_ids=a["contract_ids"],
                state_channels=a["state_channels"],
                native_obligations=native,
                obligation_disposition="native_evidence_complete_for_P9_10_5_adjudication",
            )
        )
        sources.extend(v["source_bindings"])
        # C_OS has an accepted lossless compact successor for two obsolete streams.
        if tag:
            sources.extend(v["streams"])
        else:
            from p991a5_native_spark_compact import checked_manifest

            checked_manifest(root)
            sources.extend(
                r
                for r in v["streams"]
                if not r["path"].endswith(("-current.jsonl.xz", "-reset.jsonl.xz"))
            )
        if history:
            module = (
                "spark_native_campaign"
                if not tag
                else "spark_native_" + tag.lower() + "_campaign"
            )
            if "RG2b" in family:
                from grcv4_explorer.spark_native_rg2b_campaign import checked_record

                checked_record(root, family)
            else:
                importlib.import_module("grcv4_explorer." + module).checked_record(root)
    # Validate the common source history once, then authenticate all finite edges.
    from p991a5_native_spark_compact_epoch import validated_history

    versions = validated_history(root)
    seen = set()
    for ref in sources:
        path, expected = ref["path"], ref["sha256"]
        if (path, expected) in seen:
            continue
        seen.add((path, expected))
        need(
            not Path(path).is_absolute()
            and (root / path).resolve().is_relative_to(root.resolve()),
            "nonportable binding",
        )
        from p991a6_cpc_evidence_epoch import CHANGED, PREFIXES, evidence_bytes

        raw = (
            evidence_bytes(root, path)
            if path in CHANGED or path in PREFIXES
            else (root / path).read_bytes()
        )
        need(
            sha256(raw).hexdigest() == expected or expected in versions.get(path, {}),
            "changed source/evidence: " + path,
        )
    roster = dict(schema="grc9v4-native-spark-support-v1", families=families)
    result = seal(
        dict(
            schema="phase9-native-spark-support-reconciliation-v1",
            leaf="P9-9.1a.7",
            status="bounded_native_support_reconciled",
            family_campaigns_accepted=True,
            reconciliation_user_accepted=True,
            native_completion_support=True,
            completion_support_scope="exact_declarations_and_certificate_domains",
            hierarchy_tracking=False,
            general_ATC=False,
            full_GRC9V4_conformance=False,
            G4_accepted=False,
            new_numerical_trajectories=0,
            historical_execution_flags_preserved=True,
            evidence=evidence,
            families=families,
            runtime_bindings=[
                {"path": p, "sha256": sha256((root / p).read_bytes()).hexdigest()}
                for p in RUNTIME
            ],
            native_obligation_count=sum(len(r["native_obligations"]) for r in evidence),
            next_tasks=[
                "P9-10.3-NATIVE-SPARK",
                "P9-10.4-NATIVE-SPARK",
                "P9-10.5",
                "P9-10.6",
            ],
        )
    )
    need(
        len({r["family"] for r in families}) == 10
        and result["native_obligation_count"] == 30,
        "incomplete reconciliation",
    )
    return roster, result


def build(root=ROOT, *, history=False):
    from p991a5_native_spark_compact_epoch import history_snapshot

    with history_snapshot(root):
        return _build(root, history=history)


def checked(root=ROOT, *, history=False):
    roster, result = build(root, history=history)
    need(
        load(Path(root) / ASSET) == roster,
        "runtime roster differs from accepted subjects",
    )
    need(load(Path(root) / RECORD) == result, "changed reconciliation scope/evidence")
    from pygrc.models.grc_9_v4_spark_support import registry

    need(registry() == roster, "packaged runtime support mismatch")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument(
        "--history",
        action="store_true",
        help="also check each original side-tool campaign reader",
    )
    args = ap.parse_args()
    if args.prepare:
        roster, value = build(history=args.history)
        (ROOT / ASSET).write_text(json.dumps(roster, indent=2) + "\n")
        module = ROOT / "src/pygrc/models/grc_9_v4_spark_support.py"
        text = module.read_text()
        import re

        module.write_text(
            re.sub(
                r'ASSET_SHA256 = "[^"]+"',
                'ASSET_SHA256 = "'
                + sha256((ROOT / ASSET).read_bytes()).hexdigest()
                + '"',
                text,
            )
        )
        value["runtime_bindings"] = [
            {"path": p, "sha256": sha256((ROOT / p).read_bytes()).hexdigest()}
            for p in RUNTIME
        ]
        value = seal(value)
        (ROOT / RECORD).write_text(json.dumps(value, indent=2) + "\n")
    else:
        value = checked(history=args.history)
    print("P991A7_SUPPORT_PASS families=10 native_obligations=30 native_rerun=false")

"""Additive initializer contract package; the predecessor package stays byte-exact."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from pygrc.models.grc_v4_codec import canonical_json_bytes

ACCEPTED_SPEC_COMMIT = "f7962e4"
SCHEMA = "specs/grc-v4-a-initializer-schema.json"
RELEASE = "specs/grc-v4-a-initializer-release.json"
ASSETS = "src/pygrc/models/grc_v4_assets/"
BUILDER = "implementation/phase-9-grcv4/verification/build_p972a_initializer_release.py"
INV = "implementation/investigations/grc9v4-constitutive-design/"


def build():
    from verify_p972a_proposal import SPECIFICATION_BINDINGS, BASE, PROPOSAL, PAPER
    for name, digest in SPECIFICATION_BINDINGS.items():
        raw = (ROOT / name).read_bytes()
        if sha256(raw).hexdigest() != digest or raw != subprocess.check_output(
                ["git", "show", ACCEPTED_SPEC_COMMIT + ":" + name], cwd=ROOT):
            raise ValueError("accepted initializer spec changed: " + name)
    sources = set(SPECIFICATION_BINDINGS) | {PROPOSAL, PAPER, BUILDER,
        "specs/grc-v4-contract-schema.json",
        INV + "decisions/P9CandidateAInitializerReferencePassProposal.md",
        INV + "decisions/P9CandidateAInitializerReferencePassAuthority.json",
        INV + "tools/exploratory-side-tool/records/P972aInitializerAdmission.json"}
    predecessor = json.loads(subprocess.check_output(
        ["git", "show", BASE + ":specs/grc-v4-specification-release.json"], cwd=ROOT))
    policy = json.loads((ROOT / SCHEMA).read_text())["$defs"]["static_policy"]["const"]
    payload = dict(schema_version="grcv4-a-initializer-release-identity-v1",
                   predecessor_release_id=predecessor["release_id"],
                   accepted_specification_commit=subprocess.check_output(
                       ["git", "rev-parse", ACCEPTED_SPEC_COMMIT], cwd=ROOT, text=True).strip(),
                   artifact_bindings=[dict(path=n, sha256=sha256((ROOT / n).read_bytes()).hexdigest()) for n in sorted(sources)],
                   static_policy=policy,
                   static_policy_digest="grcv4-a-initializer-policy-sha256:" + sha256(canonical_json_bytes(policy)).hexdigest(),
                   snapshot_layout_id="pygrc-generic-initializer-migration-snapshot-v1",
                   migration_receipt_schema="grcv4-profile-migration-receipt-v2")
    manifest = dict(schema_version="grcv4-a-initializer-release-v1",
                    release_id="grcv4-spec-release-sha256:" + sha256(canonical_json_bytes(payload)).hexdigest(),
                    release_identity_payload=payload,
                    claim_ceiling="Accepted optional initializer contract package, not runtime evidence or aggregate/G2/G3 acceptance.")
    data = (json.dumps(manifest, indent=2) + "\n").encode()
    return {RELEASE: data, ASSETS + Path(RELEASE).name: data,
            ASSETS + Path(SCHEMA).name: (ROOT / SCHEMA).read_bytes()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    for name, raw in build().items():
        if (ROOT / name).read_bytes() != raw:
            raise ValueError("initializer release output drift: " + name)
    print("P972A_INITIALIZER_RELEASE_PASS")

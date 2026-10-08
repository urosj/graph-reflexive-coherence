"""Read-only Tranche 8 evidence index; never implementation permission or a rerun.

The committed checkpoint pins existing acceptance, not a new acceptance ledger.
Historical mutable handoffs are read from Git; immutable retained evidence must
still match on disk. Missing ignored copies may be restored from lossless archives.
Numerical checkers are exposed only by explicit CLI action.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from copy import deepcopy

from tranche8_validation import ACTIVE, validation_session

ROOT = Path(__file__).resolve().parents[3]
PHASE = "implementation/phase-9-grcv4/"
BASE = PHASE + "tranche-8/"
HERE = PHASE + "verification/"
SIDE = "implementation/investigations/grc9v4-constitutive-design/tools/exploratory-side-tool/"
ASSET = SIDE + "tool/phase9-web/tranche8-evidence.js"
CHECKPOINT = "dbfcd311b8ee67ad9a5d8ea0f38670d88b8d57b1"
# Preregistration pins confer neither numerical evidence nor acceptance.
BOUNDARY_CONTRACT_SOURCES = {
    BASE + "P9-8.4c-BoundaryContract.json": "c7a142d0691cce9a3e7807bc58c1f6d10481772e26103a7210b81a1f69bcf8d9",
    BASE + "P9-8.4c-BoundaryReview.md": "d13fa1298d0d10526bb89fd43499a346da480ec04da11df064e383c5f8750895",
}
BOUNDARY_MECHANICAL_SOURCES = {
    BASE + "P9-8.4c-MechanicalChecks.json": "bfca9935d05b5fb793406765e10e48a1652ec7e203ea40deb93590d0f6cc3c1a",
    BASE + "P9-8.4c-MechanicalReview.md": "df80ed367b159007fc8552f85e5f4fa0276e3e786305077718de6395a310d598",
}
# Boundary execution pins do not confer scoped user acceptance.
BOUNDARY_COS_SOURCES = {
    BASE + "P9-8.4c-COSCases.json": "78d0e3e10e47742114f30e129dc62dce3683cbd1dcde1bae9062c644b293a754",
    BASE + "P9-8.4c-COSResults.json": "5da7e5d80188774a8403e079265c55a27d109fd31ab0136c99dcaa5e7d78b329",
    BASE + "P9-8.4c-COSReview.md": "66ff1d9a0e829cc0fb2349e1bc7e182236cc0e0196db5496af61e4201f067af9"
}

# New A oracle scope remains separate from numerical runtime acceptance.
BOUNDARY_AOS_ORACLE_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSOracleInputs.json": "d6c4c325474d7de8f601fe7a098e90e6027b152826cb9aadda0c9177ee2ed049",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSOracleResults.json": "33b1c41fd3a5764d8317cf2233e19762222e98c5b38301cdd3c91b7a8121b500",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSOracleReview.md": "ac3b85a497a4828eb6c5dbf3ebe4683b833050790952d03b9022fef55c5c1ecf"
}
BOUNDARY_AOS_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSCases.json": "6c3c9e24351fcd7b42c65f0b8e54758a13291bcf94cd5d980921f0a12309879b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSResults.json": "ac2918f910ff07f7f57301d45ce5b043d206bb2436d650adddc93ebeb4832f4c",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-AOSRuntimeReview.md": "26849e5d563dcd9f68de0168fab9e1946d38f19f643c6e46aef8d8bdc46aeab9"
}
BOUNDARY_CCI_PREPARATION_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCIPreparationInputs.json": "da8f99df3a1ef69317b72161e3e20f35130b62c80bc55a60dcbf0da78d625592",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCIPreparationResults.json": "53afccc62c76594a80e5640e40c2abb8289db39ffd756250ca63f2551747d25e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCIPreparationReview.md": "4a394abc0e8026a5a5ce739557b3ecc7d053ee0da00d36ca3ef98ec4db00992b"
}

BOUNDARY_CCI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCICases.json": "ba21a1f7e47f4fc8ce79b1fe5ca03b78027195b219997df6853cdfa390e5985e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCIResults.json": "f4edf55cee5bb408e29998b5c04416893df0b562653de57a76a9d58b6e350957",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-CCIRuntimeReview.md": "3707b3f42692eb76f31ea86ee573de0b13078fb4f386cb8f1c9ddb829bdd1fa7"
}

BOUNDARY_ACI_ORACLE_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACIOracleInputs.json": "6eae65792850f173b7463cf0bc5d96a801c08e8777bda5028d8fd8a413b8809f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACIOracleResults.json": "52d43cda43359691f18cbeb1287489a730b6271c2982741a36a5d7f14b62d905",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACIOracleReview.md": "ca4f78d414b5f751219b103a34bbbeb5fe716e5e936450d19ee7b3276ed1043c"
}

BOUNDARY_ACI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACICases.json": "d68172e494d2882a678b473894f3823af80edb34c7fbe2deddabaef48f9eec47",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACIResults.json": "add9d33980c2e548632da35f121735b8ba1453e27875c8cc59a3a1f2710fffb8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4c-ACIRuntimeReview.md": "b83315cc8715b8ef8c6fd09bed32e3108abd50f48b4f1c86bbb1b54fea3512af"
}

# C_PC boundary execution and separate scoped acceptance have exact pins.
BOUNDARY_CPC_SOURCES = {
    BASE + "P9-8.4c-CPCCases.json": "efea21c39271508f9b85b5147659613662e11d614fbb2d3dbc571f16e2350616",
    BASE + "P9-8.4c-CPCResults.json": "d281d25dad72d00a3ae1ad4aa40e7489a48ea7065fe6091edcf5ca23505b8f85",
    BASE + "P9-8.4c-CPCRuntimeReview.md": "bdca0a46d77e33189bf7ad1d9f557cea3097cbeee1cd1dc736a77e8bfd6dcbca",
}

# A_PC boundary execution and separate scoped acceptance have exact pins.
BOUNDARY_APC_SOURCES = {
    BASE + "P9-8.4c-APCCases.json": "cf12a1d35d0a8489eb16345f414dc3ef445dfbfcf013828c0c73f18a02eb301c",
    BASE + "P9-8.4c-APCResults.json": "6eb4ded39b423ac35b8ee276eaa2a399b566b2716ce9810ec93f37cc3cd74038",
    BASE + "P9-8.4c-APCRuntimeReview.md": "cefe1d6e94b81c6797e8f5828ff9e6d78c2daa1f1c347a52ecaf5efebabd8c15",
}

# C_CI+PC boundary execution is separate from scoped user acceptance.
BOUNDARY_CCIPC_SOURCES = {
    BASE + "P9-8.4c-CCIPCCases.json": "7641e8bd06a3e617c72a2892f4a9a1eba1c0eda3ba96fd02a1fa2775e13beb74",
    BASE + "P9-8.4c-CCIPCResults.json": "a1963f2b54f66ca49b6ede03add0fe3fda41ad6a1b1b6065cd1437b3fbf8252a",
    BASE + "P9-8.4c-CCIPCRuntimeReview.md": "8e57b3f67cba32062e538d126cc353072d0adf9789f96b7e63bea0182cb2fa4a",
}

# A_CI+PC execution and separate scoped acceptance have exact source pins.
BOUNDARY_ACIPC_SOURCES = {
    BASE + "P9-8.4c-ACIPCCases.json": "60508ea1e13b7b924972a01c0ab743670c06380760fea6b2123c00a0aca04db2",
    BASE + "P9-8.4c-ACIPCResults.json": "24210e42fb52a25cf5c6c0e89bf377dbb0911ed9ace14018d1e5fe16348f4ef3",
    BASE + "P9-8.4c-ACIPCRuntimeReview.md": "5a65669e68aca9073f58d6d85103e955e39db0b4b79e39c54ba88818b6fd559d",
}

# A_RG2b execution and separate scoped user acceptance have exact source pins.
ACCEPTED_ARG2B_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ARG2bCases.json": "cecede14b568698ea5c2500e07123838ef2e344519e509d5f79abfb7e0f48a08",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ARG2bResults.json": "d23a612386ea7d1966b09f159d996b306d240b11cc1f8fb2cc692dce5572564b",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ARG2bRuntimeReview.md": "9692b616a09a3c764cede9b109d3fbcb6fe849844c383dc97f84a9fe6e89f295",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ARG2bNumericalRecheck.json": "871a82f8040d989fbbc6587dc4bf656dae9d3ad136b5addb36b14b1ef7b22dfe"
}
# C_RG2b passing execution remains separate from user acceptance.
ACCEPTED_CRG2B_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CRG2bCases.json": "59b97d15e3e29b6dab6e23714c18137d7236a302283be56a78e34226c8bf5fe1",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CRG2bResults.json": "b0ffbbdcac92732738401306c4d53365c370eaf393e0cbedc9f7369a46e9baea",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CRG2bRuntimeReview.md": "40beb6140f4b5581ab6156b5b68a5a4451e2229deead8800fa48b9e84daf86f7",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CRG2bNumericalRecheck.json": "b823638b97a2cd2e59c2ce63a96b4f20d85b1d56bc6f4a7c6524d8aaa4061e06"
}
# A_CI_PC execution and separate scoped user acceptance have exact source pins.
ACCEPTED_ACIPC_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIPCCases.json": "a768952d08ec38f9c034f904ec73569de21fc0cb32d755633c8a1860007ade15",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIPCResults.json": "a1f5da445f6fbce1d17d98a872ab7558477083dea9b288af9a409c540c06f194",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIPCRuntimeReview.md": "210865b79e318b126f8385078954fae5e3e897abde74c973495f8ef3840f226e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIPCNumericalRecheck.json": "75cd7300811f5c869fb761afb407f73bba208f3e6492e38609f78549449150cb"
}
# C_CI_PC execution and separate scoped user acceptance have exact source pins.
ACCEPTED_CCIPC_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIPCCases.json": "0c489a674c35cad9c3f5a64f3fe970414fadf950a7c2aa378ef740f3b3a6978f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIPCResults.json": "6ae474557161f9d9e6d3c5d350b023f2742eeb1cafa8c24733c39beafe132db2",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIPCRuntimeReview.md": "5d3cd84eb1a6c2b91ab9326818cdd7d372088d160bf87d25131683ab39919e3e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIPCNumericalRecheck.json": "99e1156bbec61a6a5f311c7912021f88fcb0d2af9f9171bb9781395c7753f52d"
}
# A_PC execution and separate scoped user acceptance have exact source pins.
ACCEPTED_APC_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-APCCases.json": "b0f2b8eb1718c23579f208573eec1e9e463c6b740beeaf68b925ec2728c91163",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-APCResults.json": "cd37259572c53dfec62f9fbf30fe0fb043add1d2d34c1d2f126dfa0deb06b4bc",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-APCRuntimeReview.md": "5e8f762b3a323980eac6255be62030793aa68502a3b5f6a7e1d83296a3238b56"
}
# C_PC execution and separate scoped user acceptance have exact source pins.
ACCEPTED_CPC_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CPCCases.json": "c23e2a9a2a9d653f433316a57e7b7d3c1c3de557d7d8d507f136d6310ad4271e",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CPCResults.json": "9ca4dae9633e8d91154c8f5f1a9a4454f3dd5a3e83456edb5a27cf5664bc080a",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CPCRuntimeReview.md": "4343ca0bc237f1627c2a8a7a724f04b4174b5bc69fc95c6aab3a3cfa1f0f1d27",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CPCScientificPressure.json": "59d0ed4fd9351e783e71e0a462ff0f8df669524871ecf4f1f0b88d9f4a7a4a2e"
}
# Exact C_CI execution/review pins. The review records the separate scoped
# user acceptance; raw execution retains its original unaccepted flags.
ACCEPTED_CCI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCICases.json": "473bf8252a1b6e5b02816e261686f53e3c39c927bf957dbae87ef7f705802a85",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIResults.json": "8b6648142a4cf5c863cd4b4ebc6849fcf6b2329401e2ade1bfc2eb2bea2b69a6",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCICompletionCases.json": "23d05f40ab6fceba84a5257c0dea7ff03de1ff057946380e5dcbc3e42008876d",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCICompletionResults.json": "b7bdb1f848e3b904a6ff9cb99df37882227ea8cc562bbe00a7387a9f2860631f",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-CCIRuntimeReview.md": "fbf40e6e109fbbc9c7bad9492807a770a3e2fab7db2d734f3767631517dce679"
}
HANDOFF = "implementation/Phase-9-GRCV4-Handoff.md"
ACCEPTED_ACI_SOURCES = {
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACICases.json": "c3a5dd33e640c2f73dbc97373f27c21b53d98bf967aef524d7a84baaf7e671d8",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIResults.json": "01a86bde6105776ecd955e3f3583925c5ec1edbe03a17cb09d9c454e09a43100",
    "implementation/phase-9-grcv4/tranche-8/P9-8.4b-ACIRuntimeReview.md": "db5e7ef7529bd2412df49f7db6f1b153d1787737f9e19118f54a4ff07cb84003"
}
PLAN = "implementation/Phase-9-GRCV4-ImplementationPlan.md"
FAMILIES = tuple(c + "_" + r for c in ("A", "C") for r in ("OS", "CI", "PC", "CI_PC", "RG2b"))
PROFILE_RECORDS = {
    "A_OS": ("A.2-AOS", "A.1-AOS"),
    "A_CI": ("A.2-ACI", "A.1-ACI"),
    "A_PC": ("A.2-APC", "A.1-APC"),
    "A_CI_PC": ("A.2-ACIPC", "A.1-ACIPC"),
    "A_RG2b": ("A.2-ARG2b", "A.1-ARG2b"),
    "C_CI": ("C-CI", None),
    "C_CI_PC": ("C-CI-PC", None),
    "C_RG2b": ("C-RG2b", None),
}
MECHANICS = (
    ("P9-8.0", "Accepted R1–R10 bounded feasibility, not native execution", "p9-81e-exact-backend-correction-and-p9-80-audit"),
    ("P9-8.1", "Accepted shared mechanics parent", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1a", "Fixed chart and immutable port graph", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1b", "Fixed-row differential and stage-specific weight bridge", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1c", "Fresh mechanical candidate trigger, not a completed spark", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1d", "Column coarse-graining and Split", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.1e", "Exact-backend correction", "p9-81-shared-mechanics-parent-acceptance"),
    ("P9-8.2", "Pure allocator: 17 frozen vectors, three transforms; no event commit", "p9-82-pure-expansion-allocator"),
)
CHILDREN = {
    "a": "Coverage and comparison contracts",
    "b": "All-ten frozen expansion counterparts",
    "c": "Capacity and phase boundaries",
    "d": "Deeper recursive runtime expansion",
    "e": "Ordering, relabeling and signed-edge covariance",
    "f": "Chart rotation and reflection/chirality covariance",
    "g": "Larger-graph admission and independent oracles",
    "h": "Larger-graph runtime and covariance",
    "i": "Coverage reconciliation, side-tool catch-up and handoff",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


class Sources:
    def __init__(self, root):
        self.root, self.refs, self.values = Path(root).resolve(), {}, {}
        self.decoded = {}
        git(self.root, "merge-base", "--is-ancestor", CHECKPOINT, "HEAD")

    def current_bytes(self, name):
        snapshot = ACTIVE.get()
        if snapshot is not None:
            require(snapshot.root == self.root, "snapshot root mismatch")
            return snapshot.raw(name)
        return (self.root / name).read_bytes()

    def raw(self, name, *, historical=False):
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "repository-relative source required")
        if name not in self.values:
            path = self.root / name
            require(not path.is_symlink() and path.resolve().is_relative_to(self.root), "unsafe source path")
            boundary_pins = {**BOUNDARY_ACIPC_SOURCES, **BOUNDARY_CONTRACT_SOURCES, **BOUNDARY_MECHANICAL_SOURCES, **BOUNDARY_COS_SOURCES, **BOUNDARY_AOS_ORACLE_SOURCES, **BOUNDARY_AOS_SOURCES, **BOUNDARY_CCI_PREPARATION_SOURCES, **BOUNDARY_CCI_SOURCES, **BOUNDARY_ACI_ORACLE_SOURCES, **BOUNDARY_ACI_SOURCES, **BOUNDARY_CPC_SOURCES, **BOUNDARY_APC_SOURCES, **BOUNDARY_CCIPC_SOURCES}
            if name in boundary_pins:
                require(not historical, "preregistration is not a historical acceptance")
                frozen = self.current_bytes(name)
                require(hashlib.sha256(frozen).hexdigest() == boundary_pins[name], "boundary preregistration/mechanical source drift")
                self.values[name] = frozen
                self.refs[name] = dict(path=name, sha256=boundary_pins[name], revision=None,
                    basis=("pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_ACIPC_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_CCIPC_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_APC_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_CPC_SOURCES else
                        "pinned_accepted_independent_oracle_not_runtime_acceptance" if name in BOUNDARY_ACI_ORACLE_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_ACI_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_CCI_SOURCES else
                        "pinned_target_preparation_not_native_campaign_or_acceptance" if name in BOUNDARY_CCI_PREPARATION_SOURCES else
                        "pinned_accepted_independent_oracle_not_runtime_acceptance" if name in BOUNDARY_AOS_ORACLE_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_AOS_SOURCES else
                        "pinned_boundary_execution_with_scoped_acceptance" if name in BOUNDARY_COS_SOURCES else
                        "pinned_accepted_mechanical_evidence_not_numerical" if name in BOUNDARY_MECHANICAL_SOURCES else "pinned_preregistration_not_runtime_acceptance"))
                return frozen
            pins = {**ACCEPTED_ARG2B_SOURCES, **ACCEPTED_CCI_SOURCES, **ACCEPTED_ACI_SOURCES, **ACCEPTED_CPC_SOURCES, **ACCEPTED_APC_SOURCES, **ACCEPTED_CCIPC_SOURCES, **ACCEPTED_ACIPC_SOURCES, **ACCEPTED_CRG2B_SOURCES}
            if name in pins:
                require(not historical, "current pinned evidence is not a historical Git snapshot")
                frozen = self.current_bytes(name)
                family = "A_RG2b" if name in ACCEPTED_ARG2B_SOURCES else "C_RG2b" if name in ACCEPTED_CRG2B_SOURCES else "A_CI_PC" if name in ACCEPTED_ACIPC_SOURCES else "C_CI_PC" if name in ACCEPTED_CCIPC_SOURCES else "A_PC" if name in ACCEPTED_APC_SOURCES else "C_PC" if name in ACCEPTED_CPC_SOURCES else "A_CI" if name in ACCEPTED_ACI_SOURCES else "C_CI"
                require(hashlib.sha256(frozen).hexdigest() == pins[name],
                        "accepted " + family + " source drift: " + name)
                self.values[name] = frozen
                self.refs[name] = dict(path=name, sha256=pins[name], revision=None,
                    basis="pinned_execution_with_separate_scoped_user_acceptance")
                return frozen
            frozen = git(self.root, "show", CHECKPOINT + ":" + name)
            require(historical or self.current_bytes(name) == frozen, "Tranche 8 retained source drift: " + name)
            self.values[name] = frozen
            self.refs[name] = dict(path=name, sha256=hashlib.sha256(frozen).hexdigest(),
                                   revision=CHECKPOINT, basis="historical_git" if historical else "current_equals_accepted_checkpoint")
        return self.values[name]

    def read(self, name):
        if name not in self.decoded:
            self.decoded[name] = json.loads(self.raw(name))
        return deepcopy(self.decoded[name])

    def ref(self, name, *, historical=False, anchor=None):
        self.raw(name, historical=historical)
        return {**self.refs[name], **({"anchor": anchor} if anchor else {})}


def build(root=ROOT):
    import phase9_implementation_policy as policy
    policy.restore_packed_evidence(root)
    with validation_session(root=root):
        return _build(root)


def _build(root):
    import phase9_implementation_policy as policy
    sources = Sources(root)
    handoff = sources.ref(HANDOFF, historical=True)
    sources.ref(PLAN, historical=True)
    coverage_path = BASE + "P9-8.4a-Coverage.json"
    coverage = sources.read(coverage_path)
    families = coverage["families"]
    require(set(families) == set(FAMILIES), "all-ten prerequisite population drift")
    mechanics = [dict(work_id=i, status="accepted_bounded", scope=label,
                       acceptance={**handoff, "anchor": anchor}, numerical_conformance_inferred=False)
                 for i, label, anchor in MECHANICS]
    mechanics[0]["acceptance"] = sources.ref(BASE + "P9-8.0-AggregateReview.md")
    profiles = []
    for family in FAMILIES:
        row = families[family]
        evidence = [sources.ref(r["path"]) for r in row["evidence"]]
        review = {**handoff, "anchor": {"C_OS": "p9-83c-os-native-event-integration", "C_PC": "p9-83c-pc-whole-carrier-event-integration"}.get(family)}
        oracle = None
        if family in PROFILE_RECORDS:
            runtime_name, oracle_name = PROFILE_RECORDS[family]
            stem = BASE + "P9-8.3" + runtime_name
            validation = sources.read(stem + "-Validation.json")
            require("acceptance" in validation, "missing recorded runtime decision: " + family)
            evidence.append(sources.ref(stem + "-Validation.json"))
            review = sources.ref(stem + "-RuntimeReview.md")
            if oracle_name:
                oracle_stem = BASE + "P9-8.3" + oracle_name
                oracle = dict(status="accepted_bounded", evidence=sources.ref(oracle_stem + "-Oracle.json"),
                              review=sources.ref(oracle_stem + "-OracleReview.md"))
                if family != "A_OS":
                    oracle["acceptance"] = sources.ref(oracle_stem + "-Acceptance.json")
        profiles.append(dict(family=family, work_id="P9-8.3[" + family + "]",
            status="accepted_bounded", review=review, evidence=evidence,
            independent_A_oracle=oracle, subject_bindings=row["subject_bindings"],
            baseline=sources.ref(row["baseline_data"]["path"]),
            schedule=row["baseline_schedule"], comparison_budget=row["comparison_budget"],
            scope=row["reusable_scope"], prerequisites=row["prerequisites"],
            claim_traces=row["retained_claim_traces"], claim_trace_scope=row["claim_trace_scope"],
            claim_trace_pointer="/families/" + family + "/retained_claim_traces",
            claim_trace_record=sources.ref(coverage_path),
            historical_source_bindings="Original validation source identities remain in the pinned record; later code is not retroactively certified by this view.",
            public_support_added=False))
    closeout_name = BASE + "P9-8.3-CloseoutValidation.json"
    closeout = sources.read(closeout_name)
    large = []
    for family in FAMILIES:
        row = closeout["examples"][family]
        large.append(dict(family=family, configuration=sources.ref(row["path"]),
                          numerical_report=sources.ref(row["numerical_report"]),
                          outcomes=row["outcomes"], runtime_accepted=False,
                          next_owners=["P9-8.4g[" + family + "]", "P9-8.4h[" + family + "]"]))

    cells = {r["id"]: r for r in coverage["coverage_cells"] if r["owner"] == "P9-8.4b" and r["applicable"]}
    require(len(cells) == 322, "8.4b required population drift")
    covered, runs = set(), []
    for family, tag, expected_pass, expected_failure in (("C_OS", "COS", 14, 2), ("C_OS", "COSPhaseOne", 2, 0), ("A_OS", "AOS", 16, 0)):
        input_name, result_name = (BASE + "P9-8.4b-" + tag + n + ".json" for n in ("Cases", "Results"))
        inputs, result = sources.read(input_name), sources.read(result_name)
        require(result["manifest_digest"] == inputs["record_digest"], "runtime manifest link drift")
        require(result["user_accepted"] is False and result["aggregate_closed"] is False, "execution flags rewritten")
        cases = []
        for case in result["cases"]:
            ids = case["coverage_binding"]["cell_ids"]
            require(len(ids) == 2 and all(i in cells and cells[i]["family"] == family for i in ids), "foreign runtime coverage")
            passed = case["outcome"] == "passed_named_case"
            require(not passed or case["event_committed"] is True, "success without event")
            if passed:
                require(not covered.intersection(ids), "duplicate success credit")
                covered.update(ids)
            cases.append(dict(case_id=case["case_id"], cells=ids, case_passed=passed,
                              event_committed=case["event_committed"], outcome=case["outcome"], first_failure=case["first_failure"]))
        require(sum(c["case_passed"] for c in cases) == expected_pass and len(cases) - expected_pass == expected_failure,
                "retained case disposition drift")
        review_name = BASE + ("P9-8.4b-AOSRuntimeReview.md" if family == "A_OS" else "P9-8.4b-RuntimeReview.md")
        require("## Scoped user acceptance" in sources.raw(review_name).decode(), "missing scoped runtime acceptance")
        runs.append(dict(family=family, inputs=sources.ref(input_name), results=sources.ref(result_name),
                         record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
                         passed_cases=expected_pass, incomplete_cases=expected_failure, cases=cases,
                         status="accepted_bounded"))
    pending_cells = set()
    if ACCEPTED_CCI_SOURCES:
        input_name, result_name = (BASE + "P9-8.4b-CCICompletion" + n + ".json" for n in ("Cases", "Results"))
        inputs, result = sources.read(input_name), sources.read(result_name)
        require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True,
                "accepted C_CI execution binding drift")
        require(result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted C_CI authority widened")
        require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "C_CI case roster drift")
        pending_cases = []
        for case, row in zip(inputs["cases"], result["cases"], strict=True):
            ids = row["coverage_binding"]["cell_ids"]
            require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                    and all(i in cells and cells[i]["family"] == "C_CI" for i in ids), "C_CI foreign coverage")
            passed = row["outcome"] == "passed_named_case"
            require(row["case_passed"] == passed and (not passed or
                    row["event_committed"] is True and row["first_failure"] is None), "C_CI false case success")
            if passed:
                require(not pending_cells.intersection(ids), "duplicate C_CI cell")
                pending_cells.update(ids)
            pending_cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
                event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
        for ref in inputs["source_bindings"]:
            require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                    "accepted C_CI execution source drift: " + ref["path"])
        original_name = BASE + "P9-8.4b-CCIResults.json"
        original = sources.read(original_name)
        sources.ref(BASE + "P9-8.4b-CCICases.json")
        require(result["cases"][:8] == original["cases"][:8]
                and result["shared"] == original["shared"]
                and result["execution_partition"]["predecessor_record_digest"] == original["record_digest"],
                "C_CI retained execution reuse drift")
        failures = [dict(case_id=r["case_id"], event_committed=r["event_committed"],
                         case_passed=r["case_passed"], first_failure=r["first_failure"])
                    for r in original["cases"] if not r["case_passed"]]
        runs.append(dict(family="C_CI", inputs=sources.ref(input_name), results=sources.ref(result_name),
            record_digest=result["record_digest"],
            acceptance=sources.ref(BASE + "P9-8.4b-CCIRuntimeReview.md", anchor="scoped-user-acceptance"),
            review=sources.ref(BASE + "P9-8.4b-CCIRuntimeReview.md"),
            passed_cases=sum(c["case_passed"] for c in pending_cases),
            incomplete_cases=sum(not c["case_passed"] for c in pending_cases),
            cases=pending_cases, status="accepted_bounded",
            execution_partition=result["execution_partition"],
            original_attempt=dict(results=sources.ref(original_name), failures=failures)))
        require(len(pending_cells) == 32 and len(pending_cases) == 16, "accepted C_CI coverage drift")
        covered.update(pending_cells)
        pending_cells.clear()
    if ACCEPTED_ACI_SOURCES:
        input_name, result_name = (BASE + "P9-8.4b-ACI" + n + ".json" for n in ("Cases", "Results"))
        inputs, result = sources.read(input_name), sources.read(result_name)
        require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
                and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted A_CI execution/scope drift")
        require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted A_CI case roster drift")
        cases = []
        for case, row in zip(inputs["cases"], result["cases"], strict=True):
            ids = row["coverage_binding"]["cell_ids"]
            require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                    and all(i in cells and cells[i]["family"] == "A_CI" for i in ids), "accepted A_CI foreign coverage")
            passed = row["outcome"] == "passed_named_case"
            require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                    and row["first_failure"] is None), "accepted A_CI false success")
            if passed:
                require(not pending_cells.intersection(ids), "duplicate A_CI cell")
                pending_cells.update(ids)
            cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
                event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
        for ref in inputs["source_bindings"]:
            require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                    "accepted A_CI execution source drift: " + ref["path"])
        review_name = BASE + "P9-8.4b-ACIRuntimeReview.md"
        require("## Scoped user acceptance" in sources.raw(review_name).decode(), "missing scoped A_CI acceptance")
        runs.append(dict(family="A_CI", inputs=sources.ref(input_name), results=sources.ref(result_name),
            record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
            review=sources.ref(review_name),
            passed_cases=sum(c["case_passed"] for c in cases), incomplete_cases=sum(not c["case_passed"] for c in cases),
            cases=cases, status="accepted_bounded"))
        require(len(pending_cells) == 32 and len(cases) == 16, "accepted A_CI coverage drift")
        covered.update(pending_cells)
        pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-CPC" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted C_PC execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted C_PC roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "C_PC" for i in ids), "accepted C_PC foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted C_PC false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate C_PC credit")
            pending_cells.update(ids)
        cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
            event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted C_PC execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-CPCRuntimeReview.md"
    require("## Scoped user acceptance" in sources.raw(review_name).decode(), "missing scoped C_PC acceptance")
    runs.append(dict(family="C_PC", inputs=sources.ref(input_name), results=sources.ref(result_name),
        record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
        review=sources.ref(review_name),
        signed_stage_pressure=sources.ref(BASE + "P9-8.4b-CPCScientificPressure.json"),
        passed_cases=sum(c["case_passed"] for c in cases), incomplete_cases=sum(not c["case_passed"] for c in cases),
        cases=cases, status="accepted_bounded"))
    require(len(pending_cells) == 34 and len(cases) == 17, "accepted C_PC coverage drift")
    pressure = sources.read(BASE + "P9-8.4b-CPCScientificPressure.json")
    require(pressure["runtime_digest"] == result["record_digest"]
            and pressure["manifest_digest"] == inputs["record_digest"] and len(pressure["reads"]) == 1125
            and pressure["user_accepted"] is False and pressure["native_trajectories_rerun"] is False,
            "C_PC signed stage pressure binding drift")
    for ref in pressure["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "C_PC signed stage pressure source drift: " + ref["path"])
    runs[-1]["pc_claim_restrictions"] = pressure["claim_restrictions"]
    runs[-1]["claim_source"] = sources.ref(
        "implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json")
    covered.update(pending_cells)
    pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-APC" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted A_PC execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted A_PC roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "A_PC" for i in ids), "accepted A_PC foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted A_PC false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate A_PC credit")
            pending_cells.update(ids)
        cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
            event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted A_PC execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-APCRuntimeReview.md"
    require("## Scoped user acceptance" in sources.raw(review_name).decode(), "A_PC separate acceptance missing")
    runs.append(dict(family="A_PC", inputs=sources.ref(input_name), results=sources.ref(result_name),
        record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
        review=sources.ref(review_name),
        stage_evidence=dict(signed_read_certificates=3 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"]),
            target_beats=sum(len(r["continuation"]) for r in result["cases"]),
            fresh_final_reads=sum(len(r["final_reads"]) for r in result["cases"]),
            entry_W_Z_effects=sum(len(e) for r in result["cases"] for e in r["entry_effects"].values()),
            minimum_W_Z_effect_margin=min(e["minimum_margin_ratio"] for r in result["cases"] for v in r["entry_effects"].values() for e in v.values()),
            independent_source_chart=inputs["independent_source_chart"],
            resource_recipe=inputs["resource_recipe"]),
        pc_claim_restrictions=inputs["scientific_contracts"]["claim_restrictions"],
        claim_source=sources.ref("implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"),
        passed_cases=sum(c["case_passed"] for c in cases), incomplete_cases=sum(not c["case_passed"] for c in cases),
        cases=cases, status="accepted_bounded"))
    require(len(pending_cells) == 32 and len(cases) == 16, "accepted A_PC coverage drift")
    covered.update(pending_cells)
    pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-CCIPC" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted C_CI_PC execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted C_CI_PC roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "C_CI_PC" for i in ids), "accepted C_CI_PC foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted C_CI_PC false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate C_CI_PC credit")
            pending_cells.update(ids)
        cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
            event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted C_CI_PC execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-CCIPCRuntimeReview.md"
    require("## Scoped user acceptance" in sources.raw(review_name).decode(), "C_CI_PC separate acceptance missing")
    runs.append(dict(family="C_CI_PC", inputs=sources.ref(input_name), results=sources.ref(result_name),
        record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
        review=sources.ref(review_name),
        stage_evidence=dict(signed_read_certificates=3 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"]),
            target_beats=sum(len(r["continuation"]) for r in result["cases"]),
            fresh_final_reads=sum(len(r["final_reads"]) for r in result["cases"]),
            same_root_writer_effects=sum(len(r["writer_effects"]) for r in result["cases"]),
            final_root_effects=sum(len(v) for r in result["cases"] for v in r["final_effects"].values()),
            minimum_effect_margin=min(e["minimum_margin_ratio"] for r in result["cases"]
                for e in [*r["writer_effects"].values(), *[e for v in r["final_effects"].values() for e in v.values()]]),
            independent_source_chart=inputs["independent_source_chart"],
            independent_target_charts={c["case_id"]:c["independent_target_chart"] for c in inputs["cases"]}),
        stage_evidence_label="Signed reads, composite roots and carrier effects",
        pc_claim_restrictions=inputs["scientific_contracts"]["claim_restrictions"],
        claim_source=sources.ref("implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"),
        passed_cases=sum(c["case_passed"] for c in cases), incomplete_cases=sum(not c["case_passed"] for c in cases),
        cases=cases, status="accepted_bounded"))
    require(len(pending_cells) == 32 and len(cases) == 16, "accepted C_CI_PC coverage drift")
    recheck_name = BASE + "P9-8.4b-CCIPCNumericalRecheck.json"
    recheck = sources.read(recheck_name)
    require(recheck["manifest_digest"] == inputs["record_digest"]
            and recheck["runtime_digest"] == result["record_digest"]
            and recheck["cases_passed"] == 16 and recheck["successful_history_cells"] == 32
            and recheck["interval_equations_recomputed"] is True
            and recheck["native_entry_points_disabled"] is True
            and recheck["native_trajectories_rerun"] is False
            and recheck["user_accepted"] is False and recheck["aggregate_closed"] is False,
            "C_CI_PC numerical recheck binding/scope drift")
    for ref in recheck["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "C_CI_PC numerical recheck source drift: " + ref["path"])
    runs[-1]["numerical_recheck"] = sources.ref(recheck_name)
    covered.update(pending_cells)
    pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-ACIPC" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted A_CI_PC execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted A_CI_PC roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "A_CI_PC" for i in ids), "accepted A_CI_PC foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted A_CI_PC false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate A_CI_PC credit")
            pending_cells.update(ids)
        cases.append(dict(case_id=row["case_id"], cells=ids, case_passed=passed,
            event_committed=row["event_committed"], outcome=row["outcome"], first_failure=row["first_failure"]))
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted A_CI_PC execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-ACIPCRuntimeReview.md"
    require("## Scoped user acceptance" in sources.raw(review_name).decode(), "A_CI_PC separate acceptance missing")
    runs.append(dict(family="A_CI_PC", inputs=sources.ref(input_name), results=sources.ref(result_name),
        record_digest=result["record_digest"], acceptance=sources.ref(review_name, anchor="scoped-user-acceptance"),
        review=sources.ref(review_name),
        stage_evidence=dict(signed_read_certificates=3 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"]),
            target_beats=sum(len(r["continuation"]) for r in result["cases"]),
            fresh_final_reads=sum(len(r["final_reads"]) for r in result["cases"]),
            entry_W_Z_effects=sum(len(v) for r in result["cases"] for v in r["entry_effects"].values()),
            source_old_Z_effects=sum(len(v) for v in result["shared"]["source_history_effects"].values()),
            final_root_effects=sum(len(v) for r in result["cases"] for v in r["final_effects"].values()),
            minimum_effect_margin=min(e["minimum_margin_ratio"] for e in
                [*[e for v in result["shared"]["source_history_effects"].values() for e in v.values()],
                 *[e for r in result["cases"] for section in ("entry_effects", "final_effects") for v in r[section].values() for e in v.values()]]),
            independent_source_chart=inputs["independent_source_chart"],
            independent_target_charts={c["case_id"]:c["independent_whole_chart"] for c in inputs["cases"]}),
        stage_evidence_label="Signed joint roots and separate W/Z consumers",
        pc_claim_restrictions=inputs["scientific_contracts"]["claim_restrictions"],
        claim_source=sources.ref("implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"),
        passed_cases=sum(c["case_passed"] for c in cases), incomplete_cases=sum(not c["case_passed"] for c in cases),
        cases=cases, status="accepted_bounded"))
    require(len(pending_cells) == 32 and len(cases) == 16, "accepted A_CI_PC coverage drift")
    recheck_name = BASE + "P9-8.4b-ACIPCNumericalRecheck.json"
    recheck = sources.read(recheck_name)
    require(recheck["manifest_digest"] == inputs["record_digest"]
            and recheck["runtime_digest"] == result["record_digest"]
            and recheck["cases_passed"] == 16 and recheck["successful_history_cells"] == 32
            and recheck["interval_equations_recomputed"] is True
            and recheck["native_entry_points_disabled"] is True
            and recheck["native_trajectories_rerun"] is False
            and recheck["user_accepted"] is False and recheck["aggregate_closed"] is False,
            "A_CI_PC numerical recheck binding/scope drift")
    for ref in recheck["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "A_CI_PC numerical recheck source drift: " + ref["path"])
    runs[-1]["numerical_recheck"] = sources.ref(recheck_name)
    covered.update(pending_cells)
    pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-CRG2b" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted C_RG2b execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted C_RG2b roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "C_RG2b" for i in ids), "accepted C_RG2b foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted C_RG2b false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate C_RG2b credit")
            pending_cells.update(ids)
        cases.append({"case_id": row["case_id"], "cells": ids, "case_passed": passed,
            "event_committed": row["event_committed"], "outcome": row["outcome"], "first_failure": row["first_failure"]})
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted C_RG2b execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-CRG2bRuntimeReview.md"
    require(b"## Scoped user acceptance" in sources.raw(review_name), "missing C_RG2b scoped acceptance")
    runs.append({"family": "C_RG2b", "inputs": sources.ref(input_name), "results": sources.ref(result_name),
        "record_digest": result["record_digest"], "acceptance": sources.ref(review_name, anchor="scoped-user-acceptance"),
        "review": sources.ref(review_name),
        "stage_evidence": {"signed_read_certificates": 5 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"]),
            "inverse_level_residuals": 6*(5 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"])),
            "ordinary_bridges": 1 + sum(len(r["continuation"]) for r in result["cases"]),
            "target_beats": sum(len(r["continuation"]) for r in result["cases"]),
            "fresh_final_reads": sum(len(r["final_reads"]) for r in result["cases"]),
            "source_controls": sum(len(v) for v in result["shared"]["source_effects"].values()),
            "entry_controls": sum(len(v) for r in result["cases"] for v in r["entry_effects"].values()),
            "final_controls": sum(len(v) for r in result["cases"] for v in r["final_effects"].values()),
            "minimum_effect_margin": min(e["minimum_margin_ratio"] for e in
                [*[e for v in result["shared"]["source_effects"].values() for e in v.values()],
                 *[e for r in result["cases"] for section in ("entry_effects", "final_effects") for v in r[section].values() for e in v.values()]]),
            "independent_source_chart": inputs["independent_source_chart"],
            "independent_global_proof": inputs["independent_global_proof"],
            "independent_target_charts": {r["case_id"]:r["executed_case"]["independent_graph_chart"] for r in result["cases"]}},
        "stage_evidence_label": "Signed inverse chains, complete section errors and lagged invariance",
        "rg_claim_restrictions": inputs["scientific_contracts"]["claim_restrictions"],
        "claim_source": sources.ref("implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"),
        "passed_cases": sum(c["case_passed"] for c in cases), "incomplete_cases": sum(not c["case_passed"] for c in cases),
        "cases": cases, "status": "accepted_bounded"})
    require(len(pending_cells) == 32 and len(cases) == 16, "accepted C_RG2b coverage drift")
    recheck_name = BASE + "P9-8.4b-CRG2bNumericalRecheck.json"
    recheck = sources.read(recheck_name)
    require(recheck["manifest_digest"] == inputs["record_digest"]
            and recheck["runtime_digest"] == result["record_digest"]
            and recheck["cases_passed"] == 16 and recheck["successful_history_cells"] == 32
            and recheck["interval_equations_recomputed"] is True
            and recheck["native_entry_points_disabled"] is True
            and recheck["native_trajectories_rerun"] is False
            and recheck["user_accepted"] is False and recheck["aggregate_closed"] is False,
            "C_RG2b numerical recheck binding/scope drift")
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    shared_digest = hashlib.sha256(canonical_json_bytes(result["shared"])).hexdigest()
    require(len(recheck["cases"]) == len(result["cases"])
            and all(check["case_id"] == row["case_id"]
                    and check["case_digest"] == hashlib.sha256(canonical_json_bytes(row)).hexdigest()
                    and check["shared_digest"] == shared_digest
                    and check["successful_history_cells"] == 2
                    and check["interval_equations_recomputed"] is True
                    and check["native_trajectories_rerun"] is False
                    for check, row in zip(recheck["cases"], result["cases"], strict=True)),
            "C_RG2b completed numerical cases drift")
    for ref in recheck["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "C_RG2b numerical recheck source drift: " + ref["path"])
    runs[-1]["numerical_recheck"] = sources.ref(recheck_name)
    covered.update(pending_cells)
    pending_cells.clear()
    input_name, result_name = (BASE + "P9-8.4b-ARG2b" + n + ".json" for n in ("Cases", "Results"))
    inputs, result = sources.read(input_name), sources.read(result_name)
    require(result["manifest_digest"] == inputs["record_digest"] and result["native_runtime_executed"] is True
            and result["user_accepted"] is False and result["aggregate_closed"] is False, "accepted A_RG2b execution/scope drift")
    require([r["case_id"] for r in result["cases"]] == [r["case_id"] for r in inputs["cases"]], "accepted A_RG2b roster drift")
    cases = []
    for case, row in zip(inputs["cases"], result["cases"], strict=True):
        ids = row["coverage_binding"]["cell_ids"]
        require(row["coverage_binding"] == case["coverage_binding"] and len(ids) == 2
                and all(i in cells and cells[i]["family"] == "A_RG2b" for i in ids), "accepted A_RG2b foreign coverage")
        passed = row["outcome"] == "passed_named_case"
        require(row["case_passed"] == passed and (not passed or row["event_committed"] is True
                and row["first_failure"] is None), "accepted A_RG2b false success")
        if passed:
            require(not pending_cells.intersection(ids) and not covered.intersection(ids), "duplicate A_RG2b credit")
            pending_cells.update(ids)
        cases.append({"case_id": row["case_id"], "cells": ids, "case_passed": passed,
            "event_committed": row["event_committed"], "outcome": row["outcome"], "first_failure": row["first_failure"]})
    for ref in inputs["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "accepted A_RG2b execution source drift: " + ref["path"])
    review_name = BASE + "P9-8.4b-ARG2bRuntimeReview.md"
    require(b"## Scoped user acceptance" in sources.raw(review_name), "missing A_RG2b scoped acceptance")
    runs.append({"family": "A_RG2b", "inputs": sources.ref(input_name), "results": sources.ref(result_name),
        "record_digest": result["record_digest"], "acceptance": sources.ref(review_name, anchor="scoped-user-acceptance"),
        "review": sources.ref(review_name),
        "stage_evidence": {"signed_read_certificates": 5 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"]),
            "inverse_level_residuals": 4*(5 + sum(4 + 3*len(r["continuation"]) + len(r["final_reads"]) for r in result["cases"])),
            "ordinary_bridges": 1 + sum(len(r["continuation"]) for r in result["cases"]),
            "target_beats": sum(len(r["continuation"]) for r in result["cases"]),
            "fresh_final_reads": sum(len(r["final_reads"]) for r in result["cases"]),
            "writer_controls": sum(len(v) for r in result["cases"] for v in r["writer_effects"].values()),
            "source_controls": sum(len(v) for v in result["shared"]["source_effects"].values()),
            "entry_controls": sum(len(v) for r in result["cases"] for v in r["entry_effects"].values()),
            "final_controls": sum(len(v) for r in result["cases"] for v in r["final_effects"].values()),
            "minimum_effect_margin": min(e["minimum_margin_ratio"] for e in
                [*[e for v in result["shared"]["source_effects"].values() for e in v.values()],
                 *[e for r in result["cases"] for section in ("entry_effects", "final_effects", "writer_effects") for v in r[section].values() for e in v.values()]]),
            "independent_source_chart": inputs["independent_source_chart"],
            "independent_global_proof": inputs["independent_global_proof"],
            "independent_target_charts": {r["case_id"]:r["executed_case"]["independent_graph_chart"] for r in result["cases"]}},
        "stage_evidence_label": "Signed C/Y chains, W lineage and composed writer controls",
        "rg_claim_restrictions": inputs["scientific_contracts"]["claim_restrictions"],
        "claim_source": sources.ref("implementation/investigations/grc9v4-constitutive-design/decisions/D10NormativeClaimTopology.json"),
        "passed_cases": sum(c["case_passed"] for c in cases), "incomplete_cases": sum(not c["case_passed"] for c in cases),
        "cases": cases, "status": "accepted_bounded"})
    require(len(pending_cells) == 32 and len(cases) == 16, "accepted A_RG2b coverage drift")
    recheck_name = BASE + "P9-8.4b-ARG2bNumericalRecheck.json"
    recheck = sources.read(recheck_name)
    require(recheck["manifest_digest"] == inputs["record_digest"]
            and recheck["runtime_digest"] == result["record_digest"]
            and recheck["cases_passed"] == 16 and recheck["successful_history_cells"] == 32
            and recheck["interval_equations_recomputed"] is True
            and recheck["native_entry_points_disabled"] is True
            and recheck["native_trajectories_rerun"] is False
            and recheck["user_accepted"] is False and recheck["aggregate_closed"] is False,
            "A_RG2b numerical recheck binding/scope drift")
    from pygrc.models.grc_v4_codec import canonical_json_bytes
    shared_digest = hashlib.sha256(canonical_json_bytes(result["shared"])).hexdigest()
    require(len(recheck["cases"]) == len(result["cases"])
            and all(check["case_id"] == row["case_id"]
                    and check["case_digest"] == hashlib.sha256(canonical_json_bytes(row)).hexdigest()
                    and check["shared_digest"] == shared_digest
                    and check["successful_history_cells"] == 2
                    and check["interval_equations_recomputed"] is True
                    and check["native_trajectories_rerun"] is False
                    for check, row in zip(recheck["cases"], result["cases"], strict=True)),
            "A_RG2b completed numerical cases drift")
    for ref in recheck["source_bindings"]:
        require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                "A_RG2b numerical recheck source drift: " + ref["path"])
    runs[-1]["numerical_recheck"] = sources.ref(recheck_name)
    covered.update(pending_cells)
    pending_cells.clear()
    rows = []
    for family in FAMILIES:
        required = sorted(i for i, r in cells.items() if r["family"] == family)
        accepted = sorted(set(required) & covered)
        rows.append(dict(family=family, required_cells=len(required), accepted_cells=len(accepted),
                         executed_pending_cells=len(set(required) & pending_cells),
                         pending_cells=len(required) - len(accepted), required_cell_ids=required,
                         accepted_cell_ids=accepted, status="accepted_bounded" if len(accepted) == len(required)
                         else "executed_pending_review_and_acceptance" if set(required) <= pending_cells else "pending"))
    b_complete = len(covered) == len(cells)
    children = [dict(work_id="P9-8.4" + key, title=title,
                     status="accepted_inventory_not_execution" if key == "a" else
                     ("accepted_bounded" if b_complete else "partial") if key == "b" else "pending",
                     accepted=key == "a" or key == "b" and b_complete) for key, title in CHILDREN.items()]
    # Retain the exact claim/spec/paper associations without promoting their statuses.
    mapping = coverage["scientific_claim_mapping"]
    sources.ref(mapping["paper"]["path"])
    sources.ref(mapping["side_tool_source"])
    for name in ("specs/grc-9-v4-spec.md", "specs/grc-v4-spec.md"):
        sources.ref(name)
    sources.ref(BASE + "P9-8.4a-CoverageReview.md")
    supplements = [sources.ref(BASE + "P9-8.4b-" + name) for name in (
        "AOSOracleInputs.json", "AOSOracleResults.json", "AOSOracleReview.md", "AOSScientificPressure.json")]
    sources.ref(BASE + "P9-8.3-GraphConfigurationGuide.md")
    sources.ref(BASE + "P9-8.3-CatalogValidation.json")
    sources.ref("examples/grcv4/configurations.json")
    # Protect all current transitive inputs of the active 8.4 campaigns without
    # pretending the historical 8.3 validations describe today's source bytes.
    for tag in ("COS", "COSPhaseOne", "AOS"):
        for ref in sources.read(BASE + "P9-8.4b-" + tag + "Cases.json")["source_bindings"]:
            require(hashlib.sha256((sources.root / ref["path"]).read_bytes()).hexdigest() == ref["sha256"],
                    "8.4 execution source drift: " + ref["path"])
    scope = sorted(policy.runtime_targets(policy.recorded_acceptance(sources.root)), key=lambda r: r["path"])
    work = sources.read(policy.WORK)
    work_paths = {r["path"] for r in work["entries"]}
    ready, owners = policy.leaf_permissions(sources.root)
    import prepare_p984c_boundaries as boundary
    boundary_contract = sources.read(boundary.OUTPUT)
    boundary.validate(boundary_contract, sources.root)
    import test_p984c_mechanics as mechanics_checks
    mechanics_result = sources.read(mechanics_checks.RESULT)
    mechanics_checks.check(mechanics_result)
    require("## Scoped user acceptance" in sources.raw(mechanics_checks.REVIEW).decode(), "missing shared mechanics decision")
    require("## Scoped user acceptance" in sources.raw(boundary.REVIEW).decode(), "missing boundary contract decision")
    boundary_view = dict(record=sources.ref(boundary.OUTPUT), review=sources.ref(boundary.REVIEW),
        contract_accepted=True, acceptance_scope="matrix_and_budgets_only_not_numerical_history_cells",
        acceptance=sources.ref(boundary.REVIEW, anchor="scoped-user-acceptance"),
        mechanics=dict(record=sources.ref(mechanics_checks.RESULT), review=sources.ref(mechanics_checks.REVIEW),
            status="accepted_shared_mechanics", acceptance=sources.ref(mechanics_checks.REVIEW, anchor="scoped-user-acceptance"), observations=mechanics_result["observations"],
            test_methods=mechanics_result["tests_passed"], scope=mechanics_result["scope"],
            tests_rerun=False, numerical_history_credit=0, committed_events=0),
        record_digest=boundary_contract["record_digest"], disposition=boundary_contract["disposition"],
        counts=boundary_contract["counts"], layouts=boundary_contract["layouts"],
        families=boundary_contract["families"], schedule=boundary_contract["schedule"],
        retention=boundary_contract["retention"], prerequisites=boundary_contract["prerequisites"],
        native_runtime_executed=False, user_accepted=False)
    import p984c_cos as boundary_cos
    cos_summary = boundary_cos.status(sources.read(boundary_cos.INPUTS), sources.read(boundary_cos.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_cos.REVIEW).decode(), "missing C_OS boundary acceptance")
    require(cos_summary["passed_cases"] == 30 and cos_summary["exact_reuse_cases"] == 2, "incomplete C_OS boundary acceptance")
    cos_summary["accepted_cells"] = 64
    boundary_view["family_results"] = [dict(**cos_summary,
        status="accepted_bounded", required_cells=64, passing_pending_cells=0,
        acceptance=sources.ref(boundary_cos.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_cos.INPUTS), results=sources.ref(boundary_cos.RESULTS),
        review=sources.ref(boundary_cos.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-COSResults.json"),
        comparison_scope="bounded_dense_crosscheck_not_rigorous_full_error_or_effect_separation")]
    import p984c_aos_oracle as boundary_aos
    aos_summary = boundary_aos.validate(sources.read(boundary_aos.INPUTS), sources.read(boundary_aos.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_aos.REVIEW).decode(), "missing A_OS boundary oracle acceptance")
    boundary_view["oracle_preparations"] = [dict(**aos_summary, family="A_OS",
        status="accepted_oracle_scope", oracle_scope_accepted=True, native_steps=0,
        acceptance=sources.ref(boundary_aos.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_aos.INPUTS), results=sources.ref(boundary_aos.RESULTS),
        review=sources.ref(boundary_aos.REVIEW),
        scope="saved_entry_full_formula_bounds_not_native_admission_or_uniform_trajectory_bound")]
    import p984c_aos_runtime as boundary_aos_runtime
    import p984c_aci_oracle as boundary_aci_oracle
    aci_oracle = boundary_aci_oracle.status(sources.read(boundary_aci_oracle.INPUTS), sources.read(boundary_aci_oracle.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_aci_oracle.REVIEW).decode()
        and aci_oracle["passed_cases"] == 30, "missing or incomplete A_CI oracle acceptance")
    boundary_view["oracle_preparations"].append(dict(**aci_oracle,
        oracle_cases_passed=aci_oracle["passed_cases"] + aci_oracle["exact_accepted_target_reuses"],
        oracle_cases_required=aci_oracle["cases_required"], exact_reuse_cases=aci_oracle["exact_accepted_target_reuses"],
        status="accepted_oracle_scope", oracle_scope_accepted=True,
        acceptance=sources.ref(boundary_aci_oracle.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_aci_oracle.INPUTS),
        results=sources.ref(boundary_aci_oracle.RESULTS), review=sources.ref(boundary_aci_oracle.REVIEW),
        scope="independent_joint_root_C_W_readback_and_domain_expectations_plus_exact_accepted_D45_targets_not_native_execution"))
    native_aos = boundary_aos_runtime.status(sources.read(boundary_aos_runtime.INPUTS), sources.read(boundary_aos_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_aos_runtime.REVIEW).decode(), "missing A_OS boundary native acceptance")
    require(native_aos["successful_history_cells"] == 64, "incomplete A_OS boundary acceptance")
    native_aos["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_aos,
        status="accepted_bounded", required_cells=64, passing_pending_cells=0,
        acceptance=sources.ref(boundary_aos_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_aos_runtime.INPUTS), results=sources.ref(boundary_aos_runtime.RESULTS),
        review=sources.ref(boundary_aos_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-AOSResults.json"),
        comparison_scope="actual_saved_entry_full_formula_intervals_and_native_consumer_checks_not_uniform_trajectory_bound"))
    import p984c_cci_preparation as cci_preparation
    cci_ready = cci_preparation.status(sources.read(cci_preparation.INPUTS), sources.read(cci_preparation.RESULTS))
    preparation_status = "prepared_scope_only" if cci_ready["passed_cases"] + cci_ready["exact_reuse_cases"] == cci_ready["cases_required"] else "incomplete_preparation"
    boundary_view["target_preparations"] = [dict(**cci_ready, status=preparation_status,
        inputs=sources.ref(cci_preparation.INPUTS), results=sources.ref(cci_preparation.RESULTS),
        review=sources.ref(cci_preparation.REVIEW),
        scope="entry_joint_root_certificates_and_nominal_predictions_not_native_event_or_continuation")]
    import p984c_cci_runtime as boundary_cci_runtime
    native_cci = boundary_cci_runtime.status(sources.read(boundary_cci_runtime.INPUTS), sources.read(boundary_cci_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_cci_runtime.REVIEW).decode(), "missing C_CI boundary acceptance")
    require(native_cci["successful_history_cells"] == 64, "incomplete C_CI boundary acceptance")
    native_cci["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_cci,
        status="accepted_bounded", required_cells=64, passing_pending_cells=0,
        acceptance=sources.ref(boundary_cci_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_cci_runtime.INPUTS), results=sources.ref(boundary_cci_runtime.RESULTS),
        review=sources.ref(boundary_cci_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-CCICompletionResults.json"),
        comparison_scope="actual_entry_joint_root_full_formula_intervals_and_native_whole_ball_admission_not_uniform_trajectory_bound"))
    import p984c_aci_runtime as boundary_aci_runtime
    native_aci = boundary_aci_runtime.status(sources.read(boundary_aci_runtime.INPUTS), sources.read(boundary_aci_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_aci_runtime.REVIEW).decode(), "missing A_CI boundary acceptance")
    require(native_aci["successful_history_cells"] == 64, "incomplete A_CI boundary acceptance")
    native_aci["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_aci,
        status="accepted_bounded", required_cells=64, passing_pending_cells=0,
        acceptance=sources.ref(boundary_aci_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_aci_runtime.INPUTS), results=sources.ref(boundary_aci_runtime.RESULTS),
        review=sources.ref(boundary_aci_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-ACIResults.json"),
        comparison_scope="actual_entry_joint_root_readback_W_writer_restart_and_whole_ball_checks_not_uniform_trajectory_bound"))
    import p984c_cpc_runtime as boundary_cpc_runtime
    native_cpc = boundary_cpc_runtime.status(sources.read(boundary_cpc_runtime.INPUTS), sources.read(boundary_cpc_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_cpc_runtime.REVIEW).decode()
            and native_cpc["successful_history_cells"] == 64, "C_PC acceptance scope drift")
    native_cpc["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_cpc,
        status="accepted_bounded", required_cells=64,
        passing_pending_cells=0, acceptance=sources.ref(boundary_cpc_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_cpc_runtime.INPUTS), results=sources.ref(boundary_cpc_runtime.RESULTS),
        review=sources.ref(boundary_cpc_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-CPCResults.json"),
        comparison_scope="pointwise_full_formula_signed_readback_whole_carrier_reset_and_single_writer_checks_not_uniform_trajectory_bound"))
    import p984c_apc_runtime as boundary_apc_runtime
    native_apc = boundary_apc_runtime.status(sources.read(boundary_apc_runtime.INPUTS), sources.read(boundary_apc_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_apc_runtime.REVIEW).decode()
            and native_apc["successful_history_cells"] == 64, "A_PC acceptance scope drift")
    native_apc["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_apc,
        status="accepted_bounded", required_cells=64,
        passing_pending_cells=0, acceptance=sources.ref(boundary_apc_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_apc_runtime.INPUTS), results=sources.ref(boundary_apc_runtime.RESULTS),
        review=sources.ref(boundary_apc_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-APCResults.json"),
        comparison_scope="pointwise_fixed_row_signed_readback_exact_W_lineage_and_separate_W_Z_writers_not_uniform_trajectory_bound"))
    import p984c_ccipc_runtime as boundary_ccipc_runtime
    native_ccipc = boundary_ccipc_runtime.status(sources.read(boundary_ccipc_runtime.INPUTS), sources.read(boundary_ccipc_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_ccipc_runtime.REVIEW).decode()
            and native_ccipc["successful_history_cells"] == 64, "C_CI_PC acceptance scope drift")
    native_ccipc["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_ccipc,
        status="accepted_bounded", required_cells=64,
        passing_pending_cells=0, acceptance=sources.ref(boundary_ccipc_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_ccipc_runtime.INPUTS), results=sources.ref(boundary_ccipc_runtime.RESULTS),
        review=sources.ref(boundary_ccipc_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-CCIPCResults.json"),
        comparison_scope="pointwise_full_joint_root_signed_readback_fixed_old_Z_same_source_writer_and_strict_composite_slack_not_uniform_trajectory_bound"))
    import p984c_acipc_runtime as boundary_acipc_runtime
    native_acipc = boundary_acipc_runtime.status(sources.read(boundary_acipc_runtime.INPUTS), sources.read(boundary_acipc_runtime.RESULTS))
    require("## Scoped user acceptance" in sources.raw(boundary_acipc_runtime.REVIEW).decode()
            and native_acipc["successful_history_cells"] == 64, "A_CI_PC acceptance scope drift")
    native_acipc["accepted_cells"] = 64
    boundary_view["family_results"].append(dict(**native_acipc,
        status="accepted_bounded", required_cells=64,
        passing_pending_cells=0, acceptance=sources.ref(boundary_acipc_runtime.REVIEW, anchor="scoped-user-acceptance"),
        inputs=sources.ref(boundary_acipc_runtime.INPUTS), results=sources.ref(boundary_acipc_runtime.RESULTS),
        review=sources.ref(boundary_acipc_runtime.REVIEW),
        reuse_evidence=sources.ref(BASE + "P9-8.4b-ACIPCResults.json"),
        comparison_scope="pointwise_full_joint_root_signed_readback_exact_W_lineage_fixed_old_Z_same_source_W_Z_writers_and_strict_composite_slack_not_uniform_trajectory_bound"))
    value = dict(schema="phase9_tranche8_evidence_v1", output_class="retained_implementation_evidence_not_forensic_authority",
        checkpoint=CHECKPOINT, mechanics=mechanics, profiles=profiles,
        runtime_scope_snapshot=scope,
        registered_runtime_paths=sorted(r["path"] for r in scope if r["path"] in work_paths),
        dependency_ready_snapshot=ready,
        permitted_paths_snapshot=sorted(r["path"] for r in scope if
            (r["requires_gate"] == "P9-G1" or r["path"] in work_paths) and set(ready) & owners[r["path"]]),
        runtime_scope_note="Display roster only; current policy must independently authenticate permission, dependency readiness and work bindings.",
        configuration=dict(status="accepted_preparation_not_large_runtime", review=sources.ref(closeout_name),
                           outcome_counts=closeout["outcome_counts"], families=large, catalog_size=42),
        coverage=dict(record=sources.ref(coverage_path), children=children, families=rows, runs=runs,
                      oracle_and_pressure=supplements, boundary_contract=boundary_view,
                      required_cells=322, accepted_cells=len(covered), pending_cells=len(cells) - len(covered),
                      executed_pending_cells=len(pending_cells),
                      aggregate_closed=False, other_vector_cells=60, larger_history_cells=20),
        scientific_claim_mapping=mapping,
        verification=dict(level="pinned_sources_and_retained_structure", native_trajectories_rerun=False,
                          interval_equations_recomputed=False, historical_8_3_source_bindings_revalidated_against_current_code=False),
        future=dict(P9_8_5="pending_full_atomicity_campaign", P9_8_6="pending_conformance_review",
                    tranche_9="pending_public_lifecycle_and_compatibility", disabled_cells_pending=40,
                    new_public_support=[], general_ATC_inferred=False, arbitrary_graph_support=False),
        source_refs=sorted(sources.refs.values(), key=lambda r: r["path"]))
    value["view_digest"] = digest(value)
    return value


def browser_source(value):
    return "// Generated from checked retained Tranche 8 evidence; not new authority.\nexport const TRANCHE8_EVIDENCE = " + json.dumps(value, indent=2, ensure_ascii=False) + ";\n"


def checked(root=ROOT):
    value = build(root)
    require((Path(root) / ASSET).read_text() == browser_source(value), "Tranche 8 browser evidence drift")
    return value


BOUNDARY_RUNTIME = {"C_OS": "p984c_cos", "A_OS": "p984c_aos_runtime",
    "C_CI": "p984c_cci_runtime", "A_CI": "p984c_aci_runtime", "C_PC": "p984c_cpc_runtime", "A_PC": "p984c_apc_runtime", "C_CI_PC": "p984c_ccipc_runtime", "A_CI_PC": "p984c_acipc_runtime"}


def family_status(root, family):
    """Selected 8.4c family only; not full-index or current-boundary validity."""
    import importlib
    import phase9_implementation_policy as policy
    require(family in BOUNDARY_RUNTIME, "boundary evidence unavailable for this family")
    policy.restore_packed_evidence(root)
    name = BOUNDARY_RUNTIME[family]
    with validation_session((name,), root=root):
        module = importlib.import_module(name)
        sources = Sources(root)
        summary = module.status(sources.read(module.INPUTS), sources.read(module.RESULTS))
        review = sources.raw(module.REVIEW).decode()
        cells = 2 * (summary["passed_cases"] + summary["exact_reuse_cases"])
        require(cells == 64, "incomplete boundary scope")
        require("## Scoped user acceptance" in review, "missing scoped acceptance")
        summary.update(accepted_cells=cells, status="accepted_bounded", passing_pending_cells=0,
            acceptance=sources.ref(module.REVIEW, anchor="scoped-user-acceptance"))
        summary.update(inputs=sources.ref(module.INPUTS), results=sources.ref(module.RESULTS))
        return dict(schema="phase9_tranche8_family_status_v1", family=family, checkpoint="8.4c",
            scope="selected_family_only_not_full_index_or_execution_permission",
            native=summary, source_refs=sorted(sources.refs.values(), key=lambda r: r["path"]),
            other_families_checked=False, native_trajectories_rerun=False)


def next_work(value):
    c = value["coverage"]
    boundary_summary = " ".join(
        f"8.4c {r['family']}: {r['accepted_cells']}/{r['required_cells']} accepted history cells; {r['passing_pending_cells']} passing cells pending acceptance."
        for r in c["boundary_contract"]["family_results"])
    oracle_summary = " ".join(
        f"{r['family']} boundary oracle: {r['oracle_cases_passed']}/{r['oracle_cases_required']} target expectations available; oracle scope {'accepted' if r['oracle_scope_accepted'] else 'pending review'}, no runtime acceptance follows from the oracle."
        for r in c["boundary_contract"]["oracle_preparations"])
    preparation_summary = " ".join(
        f"{r['family']} target preparation: {r['passed_cases'] + r['exact_reuse_cases']}/{r['cases_required']} cases; native event/continuation evidence and acceptance reported separately."
        for r in c["boundary_contract"]["target_preparations"])
    return (f"Tranche 8: shared 8.1 mechanics and 8.2 allocator accepted; all ten 8.3 bounded profile integrations accepted. "
            f"8.4b has {c['accepted_cells']}/{c['required_cells']} accepted history cells; {c['pending_cells']} remain. "
            f"{c['executed_pending_cells']} additional cells have passing execution evidence awaiting review/acceptance. "
            f"{boundary_summary} {oracle_summary} {preparation_summary} 8.4c–i and 8.5/8.6 remain open. Larger-graph preparation is not runtime acceptance; "
            "public lifecycle and forty disabled cells remain Tranche 9 work. No new support or execution permission follows from this view.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("status", "check", "verify-retained"), default="status", nargs="?")
    parser.add_argument("--family", choices=("A_OS", "C_OS", "C_CI", "A_CI", "C_PC", "A_PC", "C_CI_PC", "A_CI_PC", "C_RG2b", "A_RG2b"))
    parser.add_argument("--recheck-numerics", action="store_true")
    parser.add_argument("--checkpoint", choices=("8.4b", "8.4c"), default="8.4b")
    parser.add_argument("--oracle", action="store_true", help="check A_OS or A_CI 8.4c independent oracle scope, not native execution")
    parser.add_argument("--preparation", action="store_true", help="check C_CI 8.4c target preparation, not a native campaign")
    args = parser.parse_args()
    if args.action != "verify-retained":
        if args.family:
            require(args.action == "status" and args.checkpoint == "8.4c"
                and not args.recheck_numerics and not args.oracle and not args.preparation,
                "family status requires the 8.4c checkpoint without numerical options")
            print(json.dumps(family_status(ROOT, args.family), indent=2))
            return
        value = checked()
        require(not args.family and not args.recheck_numerics and not args.oracle and not args.preparation and args.checkpoint == "8.4b", "numerical/checker options require verify-retained")
        print(json.dumps(value if args.action == "status" else dict(status="passed", view_digest=value["view_digest"],
              level=value["verification"]["level"], accepted_cells=value["coverage"]["accepted_cells"], native_trajectories_rerun=False), indent=2))
        return
    require(args.family is not None, "select one completed family explicitly")
    if args.checkpoint != "8.4c":
        checked()  # Keep historical .b dispatch unchanged in this bounded refactor.
    require(not args.oracle or (args.family in ("A_OS", "A_CI") and args.checkpoint == "8.4c"), "oracle selection requires A_OS/A_CI boundary checkpoint")
    require(not args.preparation or (args.family == "C_CI" and args.checkpoint == "8.4c"), "preparation selection requires C_CI boundary checkpoint")
    if args.checkpoint == "8.4c":
        require(args.family in BOUNDARY_RUNTIME, "boundary evidence unavailable for this family")
        if args.family in ("C_PC", "A_PC", "C_CI_PC", "A_CI_PC"):
            commands = [[sys.executable, str(ROOT / HERE / (BOUNDARY_RUNTIME[args.family] + ".py")), "--check-retained",
                *(["--recheck-numerics"] if args.recheck_numerics else [])]]
        elif args.family == "A_CI":
            script = "p984c_aci_oracle.py" if args.oracle else "p984c_aci_runtime.py"
            commands = [[sys.executable, str(ROOT / HERE / script), "--check-retained",
                *(["--recheck-numerics"] if args.recheck_numerics else [])]]
        elif args.family == "C_CI":
            script = "p984c_cci_preparation.py" if args.preparation else "p984c_cci_runtime.py"
            commands = [[sys.executable, str(ROOT / HERE / script), "--check-retained",
                *(["--recheck-numerics"] if args.recheck_numerics else [])]]
        elif args.family == "C_OS":
            require(not args.recheck_numerics, "C_OS checker already recomputes dense comparisons")
            commands = [[sys.executable, str(ROOT / HERE / "p984c_cos.py"), "--check"]]
        else:
            script = "p984c_aos_oracle.py" if args.oracle else "p984c_aos_runtime.py"
            commands = [[sys.executable, str(ROOT / HERE / script), "--check-retained",
                *(["--recheck-numerics"] if args.recheck_numerics else [])]]
    elif args.family == "C_OS":
        require(not args.recheck_numerics, "C_OS retained checker always recomputes its dense comparisons, not native trajectories")
        commands = [[sys.executable, str(ROOT / HERE / "p984b_cos_successor.py"), "--check-retained", *extra] for extra in (["--original"], [])]
    else:
        script = {"C_CI": "p984b_cci_completion.py", "A_CI": "p984b_aci_runtime.py", "A_OS": "p984b_aos_runtime.py",
                  "C_PC": "p984b_cpc_runtime.py", "A_PC": "p984b_apc_runtime.py", "C_CI_PC": "p984b_ccipc_runtime.py", "A_CI_PC": "p984b_acipc_runtime.py", "C_RG2b": "p984b_crg2b_runtime.py", "A_RG2b": "p984b_arg2b_runtime.py"}[args.family]
        commands = [[sys.executable, str(ROOT / HERE / script), "--check-retained",
                     *(["--recheck-numerics"] if args.recheck_numerics else [])]]
        if args.family == "C_PC":
            commands.append([sys.executable, str(ROOT / HERE / "p984b_cpc_pressure.py"), "--check-retained",
                             *(["--recheck-numerics"] if args.recheck_numerics else [])])
    for command in commands:
        if args.checkpoint == "8.4c":
            command.insert(1, str(ROOT / HERE / "tranche8_retained.py"))
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()

"""Exact source epochs for the P9-9.4b transition/dispatch refactor.

Historical execution is authenticated against its committed source, never
relabeled as execution of the successor. Fresh 9.4b runs bind the current bytes
and compare event and mixed-checkpoint outputs against the predecessor.
"""

import hashlib
from pathlib import Path
import subprocess

SOURCES = {
    "implementation/phase-9-grcv4/verification/p984i_first_group.py": {
        "current_sha256": "5fead6195a172fac902afce65f6859ed9ae07f4f6083d036a0c4bfa00dd12f43",
        "predecessors": {
            "c489355c1655e404000865507d0d62dd96178a5cc3f8d227de2ac5dac37fbfbe": "7b16696a"
        },
    },
    "implementation/phase-9-grcv4/verification/p985_status.py": {
        "current_sha256": "d7c6eede2274f41820c1daef8efc7531096d32ffc995c46c669d0da988699c76",
        "predecessors": {
            "527f54fcb0f10112d7fbe0eb627905a0e059137daeb6b5596c88598131c232ba": "7b16696a"
        },
    },
    "implementation/phase-9-grcv4/verification/phase9_specialization_acceptance.py": {
        "current_sha256": "de53604c10b6d8a350b77e8331efea486963757014f195eb274c04508ebbe052",
        "predecessors": {
            "ee6f37a7b3caf25977209f4a886ccc93227c2d0af5db7584ab9d0e4ca6141feb": "a04095f8"
        },
    },
    "src/pygrc/models/grc_9_v4_crossing.py": {
        "current_sha256": "b75e3a5a18dce61dbc783212d30478c324973276d7a748934df4155d23008bb9",
        "predecessors": {
            "1a4470de4942c86b82ad96498977567789891038080594e97a3646ecb02eb639": "7b16696a"
        },
    },
    "src/pygrc/models/grc_9_v4_lifecycle.py": {
        "current_sha256": "7ca7e1bcef9646d5f891e5cd1cc23925b93bbfde91778121c2f45604e4228f25",
        "predecessors": {
            "c19670def351aaeb63f9331df1c817b7c82a4570dd6c8772645bbdb35460247c": "7b16696a"
        },
    },
    "src/pygrc/models/grc_9_v4_owner.py": {
        "current_sha256": "82f36656f0923aff56b2e9d5590f6f420f9209ed42eea4dddda50fe01f11a5f7",
        "predecessors": {
            "64f2dadde0b2902444ea4b0dd10d139acda3f69053844d1d7e427231db254563": "b894c95d",
            "a90bdcd3cc5d8ffd84e7f909f811b74b53f29b2b6ff94ef6a80356f62b3f0748": "7b16696a",
        },
    },
}


# P9-10.1a: exact document and provenance-reader epochs only. This does not
# relabel any old execution as a basin-successor run or change runtime code.
SOURCES.update({
    "specs/README.md": {
        "current_sha256": "1effe5b7af0209cc871d905e268c44a54e885d65446969a954cb41bb243d6964",
        "predecessors": {"1fb3b0009b52879a0cf083a1d5ecfe4c78dc061c1c8532a12c5684b8b89e8f66": "1275bd1f"}
    },
    "implementation/investigations/grc9v4-constitutive-design/drafts/2026-09-GRC-V4.md": {
        "current_sha256": "dd538ba5f731808d9cb8d95337a36fe2cb8ddfacece90c0f3001399381f63768",
        "predecessors": {
            "6060e28698c07068f91a5e40d5335d1cf8ae2c4292baf3a7c817a36f1ede57a9": "1275bd1f"
        }
    },
    "implementation/investigations/grc9v4-constitutive-design/drafts/GRCV4-proposal.md": {
        "current_sha256": "86cb2b0019ee4c1bdcc59f8a7c0b8de1c9c991527c3be6b210deffaa09ad4552",
        "predecessors": {
            "09c080fd835d096372cff6204e42ddf0baba2b2da674fee905c7b5df2c83ed84": "1275bd1f"
        }
    },
    "implementation/phase-9-grcv4/verification/verify_p972a_proposal.py": {
        "current_sha256": "73b0cc8ec0af7d5df319688d8323e8e034d5e46bf999cf8a3c5e139aca64d96d",
        "predecessors": {
            "8bfd11a5d77b159b34fc79cbd222c8bdc633114ae4a6c16ea96fd2374a50a15d": "1275bd1f"
        }
    },
    "implementation/phase-9-grcv4/verification/build_p972b_contract.py": {
        "current_sha256": "6fe7529b4e41c29fd2357cb55ada76c8328e53f9dfd1e1cb2d85503c310fedc8",
        "predecessors": {
            "618a9e241eeebd8e861178ba344a1c4a8cb2d1fa0db3845c1752ae84ea73013e": "1275bd1f"
        }
    },
    "implementation/phase-9-grcv4/verification/build_p972b_event_release.py": {
        "current_sha256": "d8b1ce09dd62363ae326a763a2a8764bb790d2dff25eed501e175623d4463f69",
        "predecessors": {
            "747723629729808d89302802072739138ce82eb8f4e4ad4abb1e86cfd9b18882": "1275bd1f"
        }
    }
})

def historical_source(root, name, expected):
    row = SOURCES.get(name)
    if row is None or expected not in row["predecessors"]:
        return None
    root = Path(root).resolve()
    current = (root / name).read_bytes()
    if hashlib.sha256(current).hexdigest() != row["current_sha256"]:
        return None
    original = subprocess.check_output(
        ["git", "show", row["predecessors"][expected] + ":" + name], cwd=root
    )
    return expected if hashlib.sha256(original).hexdigest() == expected else None

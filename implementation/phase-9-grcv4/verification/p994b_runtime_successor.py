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

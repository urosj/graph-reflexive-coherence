"""Historical execution inputs across the additive public package export.

Execution records stay unchanged. Runtime successors are the exact
new lazy GRC9V4 export and the separately pinned transition/dispatch refactor. The two readers below are verification context, whose
original bytes remain retrievable at the accepted predecessor. Current reader
bytes are bound by the phase maintenance roster, not presented as old execution.
"""

import hashlib
from pathlib import Path
import subprocess

BASELINE = "7b16696a"
EXPORT = "src/pygrc/models/__init__.py"
READERS = {
    "implementation/phase-9-grcv4/verification/p992_compatibility.py",
    "implementation/phase-9-grcv4/verification/p994a_crossings.py",
}
ADDITION = """    if name == "GRC9V4":
        from .grc_9_v4 import GRC9V4
        return GRC9V4
"""


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def execution_sha(root, name, expected):
    root = Path(root).resolve()
    path = (root / name).resolve()
    if Path(name).is_absolute() or not path.is_relative_to(root):
        raise ValueError("nonportable execution source")
    raw = path.read_bytes()
    actual = sha(raw)
    if actual == expected:
        return actual
    from p994b_runtime_successor import historical_source
    historical = historical_source(root, name, expected)
    if historical is not None:
        return historical
    if name not in READERS and name != EXPORT:
        return actual
    old = subprocess.check_output(["git", "show", BASELINE + ":" + name], cwd=root)
    if sha(old) != expected:
        return actual
    if name == EXPORT:
        old_text = old.decode()
        marker = "    raise AttributeError(name)\n"
        if (
            old_text.count(marker) != 1
            or raw != old_text.replace(marker, ADDITION + marker).encode()
        ):
            return actual
    return expected

"""Historical research bindings are not assertions about successor production.

Only changed src/ files may resolve against this explicit pre-integration commit.
All other measured scripts/inputs must still match their retained bytes locally.
This authenticates original evidence; it gives no conformance credit to new code.
"""

import hashlib
import subprocess

BASELINE = "5b9836358af2873e524e6ceae7256639e8a6bbce"


def research_source_digest(root, path):
    content = (root / path).read_bytes()
    if path.startswith("src/"):
        content = subprocess.run(
            ["git", "show", BASELINE + ":" + path],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
    return hashlib.sha256(content).hexdigest()

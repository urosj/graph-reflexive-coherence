"""Small, explicit public configurations extracted from accepted native runs.

No test helpers, private owners, solver imports or parameter search are used.
Loading a declaration is separate from constructing/admitting a runtime model.
"""
import hashlib
import json
from pathlib import Path

from pygrc.models.grc_9_v4 import GRC9V4Configuration

ROOT = Path(__file__).resolve().parents[2]
PATH = Path(__file__).with_name("fixtures.json")
FAMILIES = ("C_OS", "C_CI", "A_CI", "A_PC", "A_OS", "C_PC", "C_CI_PC",
            "A_CI_PC", "C_RG2b", "A_RG2b")


def fixture(family):
    raw = PATH.read_bytes()
    expected = PATH.with_suffix(".sha256").read_text().split()[0]
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("example fixture content changed; review and repin it")
    return json.loads(raw)["families"][family]


def configuration(family="C_OS"):
    """A fresh typed configuration; constructing it does not restore lineage."""
    return GRC9V4Configuration.from_payload(fixture(family)["configuration"])

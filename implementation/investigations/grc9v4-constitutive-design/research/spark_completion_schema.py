"""SC-3 design-envelope pressure checks, NOT native admission or proof verification.

A passing envelope has consistent fields; its referenced theorems, actual state
inclusion, lineage, equation binding and certificates still require validation.
"""
from fractions import Fraction
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]
SCHEMA = ROOT / "specs/grc-9-v4-spark-completion-schema.json"
RATIONAL_FIELDS = {"c0", "a", "mu", "epsilon_gradient", "epsilon_Hessian",
    "minimum_resource", "contrast", "minimum_elapsed", "step_duration", "time",
    "duration", "q", "image_margin", "full_step_error"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def node_key(node):
    return node["kind"], node["value"]


def validate_structure(value, *, policy=None):
    """Validate closed shape and local arithmetic only; never return admission."""
    Draft202012Validator(json.loads(SCHEMA.read_text())).validate(value)

    def walk(obj):
        if isinstance(obj, list):
            for item in obj:
                walk(item)
        elif isinstance(obj, dict):
            if set(obj) == {"path", "sha256"}:
                p = Path(obj["path"])
                need(not p.is_absolute() and ".." not in p.parts and str(p) == obj["path"],
                     "noncanonical repository reference")
            for key, item in obj.items():
                if key in RATIONAL_FIELDS:
                    f = Fraction(item)
                    need(str(f) == item, "noncanonical rational: " + key)
                walk(item)
            if "members" in obj:
                members = [node_key(n) for n in obj["members"]]
                need(members == sorted(set(members)) and node_key(obj["anchor"]) in members,
                     "duplicate/unsorted basin members or absent anchor")
    walk(value)
    kind = value["schema_version"]
    if kind == "grcv4-homogeneous-quartic-site-v1":
        need(Fraction(value["c0"]) > Fraction(value["a"]) > 0 and Fraction(value["mu"]) > 0,
             "site domain requires c0 > a > 0, mu > 0")
    elif kind == "grc9v4-child-completion-policy-v2":
        need(all(Fraction(value[k]) > 0 for k in RATIONAL_FIELDS & value.keys()),
             "completion thresholds and durations must be positive")
    elif value["decision"] == "completed":
        need(policy is not None, "completed envelope requires its static policy")
        validate_structure(policy)
        # All policy fields are ASCII; this is also the selected JCS preimage.
        import hashlib
        policy_digest = hashlib.sha256(json.dumps(policy, sort_keys=True,
            separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
        need(value["policy_digest"] == policy_digest, "wrong policy identity")
        proof = value["proof"]
        need("C" in proof["state_channels"], "resource coordinate omitted")
        need(0 <= Fraction(proof["q"]) < 1, "not a contraction bound")
        need(0 <= Fraction(proof["full_step_error"]) < Fraction(proof["image_margin"]),
             "full-step error does not fit strict image margin")
        need(proof["numerical_policy_id"] == policy["numerical_policy_id"], "numerical policy mismatch")
        observations = value["observations"]
        need(len(observations) >= policy["minimum_beats"], "short positive window")
        dt = Fraction(policy["step_duration"])
        need(len(observations)*dt >= Fraction(policy["minimum_elapsed"]), "short elapsed window")
        for i, obs in enumerate(observations):
            need(Fraction(obs["time"]) > 0 and Fraction(obs["duration"]) == dt, "invalid positive clock")
            if i:
                old = observations[i-1]
                need(obs["step_index"] == old["step_index"]+1 and
                     Fraction(obs["time"])-Fraction(old["time"]) == dt, "nonconsecutive window")
                need(obs["receipt"] != old["receipt"], "replayed occurrence is not a new beat")
                need(obs["descendants"] == old["descendants"], "changed certified domain roster")
            basins = obs["descendants"]
            anchors = [node_key(b["anchor"]) for b in basins]
            members = [node_key(n) for b in basins for n in b["members"]]
            need(anchors == sorted(set(anchors)) and len(members) == len(set(members)),
                 "noncanonical or overlapping descendants")
            need(len(basins)-1 == value["local_gain"], "wrong local gain")
        new = [node_key(n) for n in value["new_child_anchors"]]
        need(new == sorted(set(new)) and set(new) <= set(anchors) and
             node_key(value["parent"]["anchor"]) not in new, "invalid new child roster")
    return "structure_only_not_scientific_or_native_admission"

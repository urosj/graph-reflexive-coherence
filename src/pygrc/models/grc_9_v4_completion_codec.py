"""Explicit optional SC-3 schema asset; validation is never proof admission."""

import json
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from importlib.resources import files

from .grc_v4_codec import canonical_json_bytes
from .grc_v4_spark_state import NUMERICAL_POLICY, rational
from .grc_v4_state import FrozenJSONMap

SCHEMA_SHA256 = "7caad31be98abf29911a9438b166effcb487e4adbf7c78c8c3e0f8ca2069ed52"


@lru_cache(maxsize=1)
def _validator():
    from jsonschema import Draft202012Validator

    raw = (
        files("pygrc.models.grc_v4_assets")
        .joinpath("grc-9-v4-spark-completion-schema.json")
        .read_bytes()
    )
    if sha256(raw).hexdigest() != SCHEMA_SHA256:
        raise ValueError("optional completion schema asset changed")
    return Draft202012Validator(json.loads(raw))


def validate(value):
    data = FrozenJSONMap(value).to_dict()
    _validator().validate(data)
    return data


def digest(value):
    return sha256(canonical_json_bytes(value)).hexdigest()


def node(value):
    if type(value) not in (str, int) or type(value) is int and abs(value) > 2**53 - 1:
        raise ValueError("typed safe node identity required")
    return {"kind": "str" if type(value) is str else "int", "value": value}


@dataclass(frozen=True, slots=True)
class CompletionPolicy:
    landscape_sign: int = -1
    epsilon_gradient: str = "4"
    epsilon_Hessian: str = "1/4"
    minimum_resource: str = "1/2"
    contrast: str = "1/2"
    minimum_beats: int = 2
    minimum_elapsed: str = "64"
    step_duration: str = "32"

    def __post_init__(self):
        validate(self.to_payload())
        if type(self.landscape_sign) is not int or type(self.minimum_beats) is not int:
            raise ValueError("integer sign and window required")
        if (
            min(
                map(
                    rational,
                    (
                        self.epsilon_gradient,
                        self.epsilon_Hessian,
                        self.minimum_resource,
                        self.contrast,
                        self.minimum_elapsed,
                        self.step_duration,
                    ),
                )
            )
            <= 0
        ):
            raise ValueError("positive exact completion thresholds required")
        if self.minimum_beats < 1:
            raise ValueError("positive completion window required")

    def to_payload(self):
        return {
            "schema_version": "grc9v4-child-completion-policy-v2",
            "policy_id": "grc9v4-certified-geometric-child-basins-v1",
            "landscape_sign": self.landscape_sign,
            "epsilon_gradient": self.epsilon_gradient,
            "epsilon_Hessian": self.epsilon_Hessian,
            "minimum_resource": self.minimum_resource,
            "contrast": self.contrast,
            "minimum_beats": self.minimum_beats,
            "minimum_elapsed": self.minimum_elapsed,
            "step_duration": self.step_duration,
            "trap_policy_id": "full_physical_map_strict_contraction_v1",
            "numerical_policy_id": NUMERICAL_POLICY,
        }

    @property
    def policy_digest(self):
        return digest(self.to_payload())

    @classmethod
    def from_payload(cls, value):
        data = validate(value)
        result = cls(**{k: data[k] for k in cls.__dataclass_fields__})
        if result.to_payload() != data:
            raise ValueError("unsupported completion policy binding")
        return result

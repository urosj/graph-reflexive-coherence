"""Closed dispatch for explicitly implemented native quartic families."""

from .grc_v4_spark_state import QuarticCCIPCProfile, QuarticCCIProfile, QuarticCOSProfile, QuarticCPCProfile
from .grc_v4_spark_adaptive_carrier import QuarticAPCProfile
from .grc_v4_spark_conductance import QuarticAOSProfile, QuarticACIProfile


def quartic_profile(value):
    family = value["identity_payload"]["profile_family_id"]
    types = {"C_OS": QuarticCOSProfile, "C_CI": QuarticCCIProfile, "C_PC": QuarticCPCProfile, "C_CI_PC": QuarticCCIPCProfile, "A_OS": QuarticAOSProfile, "A_CI": QuarticACIProfile, "A_PC": QuarticAPCProfile}
    if family not in types:
        raise ValueError("unimplemented native quartic family")
    return types[family].from_payload(value)


def quartic_kernel(graph, profile):
    from .grc_v4_spark_apc import SparkAPCKernel
    from .grc_v4_spark_aos import SparkAOSKernel
    from .grc_v4_spark_aci import SparkACIKernel
    from .grc_v4_spark_ccipc import SparkCCIPCKernel
    from .grc_v4_spark_cpc import SparkCPCKernel
    from .grc_v4_spark_cci import SparkCCIKernel
    from .grc_v4_spark_cos import SparkCOSKernel

    types = {QuarticCOSProfile: SparkCOSKernel, QuarticCCIProfile: SparkCCIKernel, QuarticCPCProfile: SparkCPCKernel, QuarticCCIPCProfile: SparkCCIPCKernel, QuarticAOSProfile: SparkAOSKernel, QuarticACIProfile: SparkACIKernel, QuarticAPCProfile: SparkAPCKernel}
    if type(profile) not in types:
        raise TypeError("explicit supported quartic profile required")
    return types[type(profile)](graph, profile)

"""PyGRC package bootstrap.

Public import policy for the source-installable research workspace:

- Prefer the package facades listed in ``PUBLIC_API_SURFACES``.
- ``pygrc.discovery`` and ``pygrc.cli`` are importable research/tooling
  surfaces, but they are not root-facade exports.
- Direct deep imports from implementation modules are considered unstable
  unless they are used by an example, spec, or reference guide.
"""

from . import core, integrations, landscapes, models, telemetry, utils, visualization

PUBLIC_API_SURFACES: dict[str, str] = {
    "pygrc.core": "shared model interfaces, params, graph backends, events, snapshots",
    "pygrc.models": "runtime model families, states, lowering adapters",
    "pygrc.landscapes": "landscape seeds, validation, GRCL/PDE bridges, inference",
    "pygrc.telemetry": "artifact capture, contracts, reports, replay helpers",
    "pygrc.visualization": "artifact-driven plot and graph rendering helpers",
    "pygrc.integrations": "adapter-boundary contracts for host/tool interop",
}

RESEARCH_TOOLING_SURFACES: dict[str, str] = {
    "pygrc.discovery": "hypothesis catalogs, mechanism ledgers, review artifacts",
    "pygrc.cli": "local command-line entry points and wrappers",
}

__all__ = [
    "PUBLIC_API_SURFACES",
    "RESEARCH_TOOLING_SURFACES",
    "core",
    "integrations",
    "landscapes",
    "models",
    "telemetry",
    "utils",
    "visualization",
]

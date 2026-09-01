"""Read-only source admission for the GRCv4 exploratory side tool."""

from .bundle import build_source_bundle
from .discovery import discover_sources

__all__ = ["build_source_bundle", "discover_sources"]

"""Shared exception types for PyGRC."""

from __future__ import annotations


class GRCError(Exception):
    """Base exception for PyGRC contract and runtime failures."""


class InvalidParamsError(GRCError):
    """Raised when parameter construction or validation fails."""


class UnsupportedCapabilityError(GRCError):
    """Raised when a caller requests a capability a model does not support."""


class SnapshotCompatibilityError(GRCError):
    """Raised when snapshot loading or restoration is incompatible."""


class InvalidStateTransitionError(GRCError):
    """Raised when a contract-level state transition is invalid."""


class InvalidLandscapeSeedError(GRCError):
    """Raised when a normalized landscape seed is structurally invalid."""


class LandscapeTranslationEquivalenceError(GRCError):
    """Raised when a translated landscape seed breaks source-level invariants."""

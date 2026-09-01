"""Fail-closed errors for source discovery and admission."""


class SourceAdmissionError(RuntimeError):
    """An admitted source failed identity, schema, or reference validation."""


class SourceEvolutionError(SourceAdmissionError):
    """The observed repository inventory differs from the admitted snapshot."""


class GraphInvariantError(RuntimeError):
    """The derived graph violates its source or authority contract."""


class MutationValidationError(RuntimeError):
    """A structural counterfactual is outside the admitted mutation algebra."""


class ScenarioValidationError(RuntimeError):
    """A serialized scenario is stale, malformed, or not precomputed."""


class RippleCompilationError(RuntimeError):
    """A counterfactual result cannot be compiled into a bounded ripple row."""

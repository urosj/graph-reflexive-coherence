"""Fail-closed errors for source discovery and admission."""


class SourceAdmissionError(RuntimeError):
    """An admitted source failed identity, schema, or reference validation."""


class SourceEvolutionError(SourceAdmissionError):
    """The observed repository inventory differs from the admitted snapshot."""

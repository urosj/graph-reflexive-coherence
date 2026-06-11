"""Additional import coverage for the Phase 1 contract modules."""

from __future__ import annotations

import unittest


class ModuleImportContractTest(unittest.TestCase):
    """Verify that the common-contract modules import cleanly as a set."""

    def test_core_contract_modules_import(self) -> None:
        import pygrc.core.backends
        import pygrc.core.capabilities
        import pygrc.core.digests
        import pygrc.core.errors
        import pygrc.core.events
        import pygrc.core.graph
        import pygrc.core.ids
        import pygrc.core.interfaces
        import pygrc.core.mutations
        import pygrc.core.observables
        import pygrc.core.params
        import pygrc.core.serialization
        import pygrc.core.storage
        import pygrc.core.types

        self.assertIsNotNone(pygrc.core.backends)
        self.assertIsNotNone(pygrc.core.capabilities)
        self.assertIsNotNone(pygrc.core.digests)
        self.assertIsNotNone(pygrc.core.errors)
        self.assertIsNotNone(pygrc.core.events)
        self.assertIsNotNone(pygrc.core.graph)
        self.assertIsNotNone(pygrc.core.ids)
        self.assertIsNotNone(pygrc.core.interfaces)
        self.assertIsNotNone(pygrc.core.mutations)
        self.assertIsNotNone(pygrc.core.observables)
        self.assertIsNotNone(pygrc.core.params)
        self.assertIsNotNone(pygrc.core.serialization)
        self.assertIsNotNone(pygrc.core.storage)
        self.assertIsNotNone(pygrc.core.types)

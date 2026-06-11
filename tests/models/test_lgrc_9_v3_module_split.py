"""Smoke tests for the LGRC9V3 ownership-module split."""

from __future__ import annotations

import unittest

from pygrc.models import LGRC9V3
from pygrc.models import lgrc_9_v3 as legacy
from pygrc.models.lgrc_9_v3_contract import validate_lgrc9v3_causal_modes
from pygrc.models.lgrc_9_v3_identity import (
    evaluate_lgrc9v3_proper_time_identity_persistence,
)
from pygrc.models.lgrc_9_v3_packets import (
    LGRC9V3PacketRecord,
    build_lgrc9v3_packet_ledger,
)
from pygrc.models.lgrc_9_v3_timing import annotate_lgrc9v3_causal_history
from pygrc.models.lgrc_9_v3_topology import (
    transport_lgrc9v3_packets_through_refinement,
)


class LGRC9V3ModuleSplitTest(unittest.TestCase):
    """Validate legacy and direct split-module import compatibility."""

    def test_legacy_facade_reexports_runtime_and_split_symbols(self) -> None:
        self.assertIs(legacy.LGRC9V3, LGRC9V3)
        self.assertIs(legacy.LGRC9V3PacketRecord, LGRC9V3PacketRecord)
        self.assertIs(
            legacy.validate_lgrc9v3_causal_modes,
            validate_lgrc9v3_causal_modes,
        )

    def test_direct_split_module_imports_are_callable(self) -> None:
        self.assertTrue(callable(validate_lgrc9v3_causal_modes))
        self.assertTrue(callable(build_lgrc9v3_packet_ledger))
        self.assertTrue(callable(transport_lgrc9v3_packets_through_refinement))
        self.assertTrue(callable(evaluate_lgrc9v3_proper_time_identity_persistence))
        self.assertTrue(callable(annotate_lgrc9v3_causal_history))


if __name__ == "__main__":
    unittest.main()

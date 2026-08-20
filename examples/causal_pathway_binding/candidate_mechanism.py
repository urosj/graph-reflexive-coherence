"""Executable mechanism used only by the unregistered-candidate example."""

from __future__ import annotations

from typing import Any


def packet_schedule_to_snapshot(schedule_result: Any) -> Any:
    """Carry the exact packet-schedule result across the experimental cut."""

    return schedule_result

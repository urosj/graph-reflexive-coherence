"""Load and validate a normalized landscape seed.

What this example does:
    Ensures the example seed exists, loads it from YAML, validates it, and
    prints source-side content.

Why it is needed:
    Loading a seed is still source-side. It proves the document is well formed;
    it does not prove any runtime event.
"""

from __future__ import annotations

import json
from typing import Any

from define_seed import SEED_PATH, save_example_seed
from pygrc.landscapes import load_landscape_seed, validate_landscape_seed


def load_example_seed() -> Any:
    """Load the saved example seed, creating it first if needed."""

    if not SEED_PATH.exists():
        save_example_seed()
    seed = load_landscape_seed(SEED_PATH)
    validate_landscape_seed(seed)
    return seed


def _summary(seed: Any) -> dict[str, Any]:
    return {
        "path": str(SEED_PATH),
        "name": seed.meta.name,
        "source_domain": seed.meta.source_domain,
        "translation_mode": seed.meta.translation_mode,
        "primitive_count": len(seed.primitives),
        "primitives": [
            {
                "id": primitive.id,
                "type": primitive.type,
                "has_grcl9v3_extension": "grcl9v3" in primitive.extensions,
            }
            for primitive in seed.primitives
        ],
        "transport_intent": [
            {
                "id": intent.id,
                "mode": intent.mode,
                "sources": intent.sources,
                "targets": intent.targets,
                "carrier_id": intent.carrier_id,
            }
            for intent in seed.transport_intent
        ],
        "top_level_extensions": sorted(seed.extensions),
    }


def main() -> None:
    seed = load_example_seed()
    print("Loaded landscape seed")
    print(json.dumps(_summary(seed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Retain the three small C fixtures that lack complete JSON state pairs.

Discovery never imports fixtures or executes numerical work. This explicit
maintenance command reconstructs the accepted source fixtures and pure target
transfers; it does not add a new event or acceptance claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import replace
from pathlib import Path

from pygrc.models import grc_9_v4_expansion as expansion
from pygrc.models.grc_v4_exact import ExactBackend, exact_backend
from pygrc.models.grc_v4_pc import carrier_geometry

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "implementation/phase-9-grcv4/tranche-8/P9-8.3-CatalogSmallCInputs.json"


def build():
    from tests.models.test_grc_9_v4_crg2b import construction, fixture
    from tests.models.test_grc_9_v4_lifecycle import (
        native_cos_fixture,
        native_cpc_fixture,
    )

    states = {}
    for family, make in (
        ("C_OS", native_cos_fixture),
        ("C_PC", native_cpc_fixture),
        ("C_RG2b", fixture),
    ):
        with exact_backend(ExactBackend.FLINT):
            source, request, *_ = make()
            ref = source.inputs.geometry.reference
            if family == "C_RG2b":
                transfer = construction(source, request)
            else:
                plan = expansion.GRC9V4ExpansionPlan(
                    ref.graph.port_graph,
                    source.scientific_digest,
                    request,
                    expansion.GRC9ExpansionPolicy.from_payload(
                        source.specialization.resolved["expansion"]
                    ),
                )
                extra = (
                    (source.inputs.current, source.inputs.reset)
                    if family == "C_PC"
                    else ()
                )
                transfer = getattr(
                    expansion, "GRC9V4" + family.replace("_", "") + "Expansion"
                )(plan, ref, *extra)
            inputs = replace(
                source.inputs,
                geometry=transfer.target.geometry(),
                current=transfer.transfer(source.inputs.current),
                reset=transfer.transfer(source.inputs.reset),
            )
            if family == "C_PC":
                inputs = replace(
                    inputs, geometry=carrier_geometry(inputs, inputs.current)
                )
            target = type(source)(inputs, source.specialization)
            states[family] = {
                "source": source.to_payload(),
                "target": target.to_payload(),
                "request": request.to_payload(),
            }
        print(f"{family}: retained source fixture and pure target transfer", flush=True)
    paths = [
        Path(__file__).relative_to(ROOT),
        Path("tests/models/test_grc_9_v4_lifecycle.py"),
        Path("tests/models/test_grc_9_v4_crg2b.py"),
    ]
    paths += sorted(
        p.relative_to(ROOT) for p in (ROOT / "src/pygrc/models").glob("grc*v4*.py")
    )
    return {
        "schema": "p983-catalog-small-c-inputs-v1",
        "states": states,
        "scope": "existing_fixture_and_pure_transfer; no_new_acceptance",
        "source_bindings": [
            {
                "path": str(p),
                "sha256": hashlib.sha256((ROOT / p).read_bytes()).hexdigest(),
            }
            for p in paths
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.write:
        OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    elif json.loads(OUTPUT.read_text()) != result:
        raise SystemExit("Small C catalog inputs differ; inspect before regenerating")


if __name__ == "__main__":
    main()

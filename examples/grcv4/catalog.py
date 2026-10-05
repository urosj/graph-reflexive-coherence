"""Browse, compare and select retained GRC V4 graph configurations.

Standard-library-only checkout tool. Reading a catalog never imports a model,
executes a fixture, runs admission or changes supported profiles.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = "examples/grcv4/configurations.json"
FAMILIES = tuple(f"{c}_{r}" for c in "AC" for r in ("OS", "CI", "PC", "CI_PC", "RG2b"))
STATUSES = (
    "bounded-runtime",
    "measured-run",
    "certificate-passed",
    "read-passed",
    "rejected",
    "incomplete",
    "mixed",
    "stale",
)


class CatalogError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise CatalogError(message)


def encoded(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def json_read(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def constant(value):
        raise CatalogError(f"nonfinite JSON number: {value}")

    def finite(value):
        number = float(value)
        require(math.isfinite(number), "nonfinite JSON number")
        return number

    return json.loads(
        raw, object_pairs_hook=pairs, parse_constant=constant, parse_float=finite
    )


def numeric_identity(value):
    """JSON numbers 1 and 1.0 agree; booleans retain their separate type."""
    if type(value) is float and value.is_integer():
        return int(value)
    if isinstance(value, list):
        return [numeric_identity(v) for v in value]
    if isinstance(value, dict):
        return {k: numeric_identity(v) for k, v in value.items()}
    return value


def pointer(data, path):
    require(path == "" or path.startswith("/"), "invalid JSON pointer")
    for part in path.split("/")[1:]:
        key = part.replace("~1", "/").replace("~0", "~")
        data = data[int(key)] if isinstance(data, list) else data[key]
    return data


def graph_summary(graph):
    nodes = graph["live_node_ids"]
    keys = [encoded(numeric_identity(n)) for n in nodes]
    require(len(set(keys)) == len(keys), "duplicate graph node")
    adjacent, degree = {k: set() for k in keys}, dict.fromkeys(keys, 0)
    edges = graph.get("edges", graph.get("oriented_edges"))
    require(isinstance(edges, list), "graph has no edge list")
    for edge in edges:
        tail = edge["tail"]["node_id"] if "tail" in edge else edge["tail_node_id"]
        head = edge["head"]["node_id"] if "head" in edge else edge["head_node_id"]
        u, v = encoded(numeric_identity(tail)), encoded(numeric_identity(head))
        require(u in adjacent and v in adjacent, "edge references absent node")
        adjacent[u].add(v)
        adjacent[v].add(u)
        degree[u] += 1
        degree[v] += 1
    remaining, components = set(keys), 0
    while remaining:
        stack = [remaining.pop()]
        components += 1
        while stack:
            fresh = adjacent[stack.pop()] & remaining
            remaining -= fresh
            stack.extend(fresh)
    return {
        "vertices": len(nodes),
        "edges": len(edges),
        "components": components,
        "cycle_rank": len(edges) - len(nodes) + components,
        "maximum_degree": max(degree.values(), default=0),
    }


def parameter_summary(profile):
    params = profile["params_resolved"]
    realization = params["realization"]
    summary = {
        "kappa_H": params["geometry"]["kappa_H"],
        "carrier_radius": realization.get("radius"),
        "resource_chart": realization.get("source_envelope_id"),
        "geometry_domain": realization.get("contraction_domain_id"),
        "selector_cutoff": params["candidate"].get("Lambda_C"),
        "tolerance": realization.get("tolerance", realization.get("error_tolerance")),
        "completion": realization.get("containment_certificate_id"),
        "carrier_norm": realization.get("carrier_norm_id"),
        "norms": {k: v for k, v in realization.items() if "norm" in k},
    }
    chart = realization.get("source_envelope_id", "").split(":")
    if len(chart) == 4 and chart[0] == "pc_compact_base_chart_v1":
        summary.update(
            zip(
                ("resource_radius", "weight_lower", "weight_upper"),
                map(float.fromhex, chart[1:]),
                strict=True,
            )
        )
    domain = realization.get("contraction_domain_id", "").split(":")
    if len(domain) == 2 and domain[0] == "ci_reference_frobenius_ball_v1":
        summary["geometry_radius"] = float.fromhex(domain[1])
    return summary


class Catalog:
    def __init__(self, path=DEFAULT, root=ROOT):
        self.root = Path(root).resolve()
        self.path = self.relative(path)
        data = json_read((self.root / self.path).read_bytes())
        require(
            data["schema"] == "grc-configuration-catalog-v1", "unknown catalog schema"
        )
        self.entries = {}
        for item in data["entries"]:
            name = item["id"]
            require(
                re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name),
                "invalid configuration ID",
            )
            require(name not in self.entries, f"duplicate configuration ID: {name}")
            require(item["family"] in FAMILIES, f"unknown family: {item['family']}")
            require(item["model"] in {"GRC9V4", "GRCV4"}, "unknown model")
            require(
                item["format"]
                in {
                    "prepared-native",
                    "native-states",
                    "native-oracle",
                    "generic-report",
                    "generic-inputs",
                },
                "unknown data adapter",
            )
            require(
                item["format"].startswith("generic-") == (item["model"] == "GRCV4"),
                "model/data adapter mismatch",
            )
            self.entries[name] = item

    def relative(self, path):
        path = Path(path)
        require(
            not path.is_absolute() and ".." not in path.parts,
            "catalog paths must be relative to the repository",
        )
        resolved = (self.root / path).resolve()
        require(
            resolved.is_relative_to(self.root), "catalog path escapes the repository"
        )
        return path.as_posix()

    def artifact(self, ref, *, parse=False):
        path = self.relative(ref["path"])
        raw = (self.root / path).read_bytes()
        require(
            hashlib.sha256(raw).hexdigest() == ref["sha256"],
            f"artifact changed: {path}; review and refresh its catalog binding",
        )
        return json_read(raw) if parse else None

    def entry(self, name):
        if name not in self.entries:
            hints = difflib.get_close_matches(name, self.entries, n=3)
            raise CatalogError(
                f"unknown configuration {name!r}"
                + (f"; try: {', '.join(hints)}" if hints else "; use list")
            )
        return self.entries[name]

    def inspect(self, name):
        item = self.entry(name)
        data = self.artifact(item["data"], parse=True)
        for ref in item["evidence"]:
            self.artifact(ref)
        configurations = {}
        for side, path in item["sides"].items():
            require(side in {"source", "target"}, "unknown graph side")
            value = pointer(data, path)
            if item["format"] == "prepared-native":
                config = {
                    "graph": value["graph"],
                    "profile": value["profile"],
                    "roles": value["roles"],
                    "specialization": data["specialization"],
                    "reference_recipe": data["reference_recipe"],
                    "scientific_digest": value["scientific_digest"],
                    "reset_digest": value["reset_digest"],
                    "model_identity": value["model_identity"],
                    "ordinary_dt": data["selected_configuration"]["ordinary_dt"],
                }
            elif item["format"] == "native-states":
                inputs = value["inputs"]
                config = {
                    "graph": inputs["reference"]["graph"],
                    "profile": inputs["reference"]["profile"],
                    "inputs": inputs,
                    "specialization": value["specialization"],
                    "roles": {r: inputs[r] for r in ("current", "reset")},
                    "scientific_digest": value["scientific_digest"],
                    "reset_digest": value["reset_digest"],
                    "model_identity": value["model_identity"],
                }
                dt = (
                    data.get("numerical_observations", {})
                    .get("initial_inputs", {})
                    .get("dt")
                )
                if dt is not None:
                    config["ordinary_dt"] = dt
            elif item["format"] == "generic-inputs":
                config = {
                    "graph": value["reference"]["graph"],
                    "profile": value["reference"]["profile"],
                    "inputs": value,
                    "roles": {r: value[r] for r in ("current", "reset")},
                    "ordinary_dt": data["dt"],
                    "differential_reference": data["differential_reference"],
                }
            elif item["format"] == "native-oracle":
                roles = (
                    {r: value[r] for r in ("current", "reset")}
                    if side == "source"
                    else {
                        r: value["roles"][r]["authoritative"]
                        for r in ("current", "reset")
                    }
                )
                config = {
                    "graph": value["port_graph"],
                    "profile": value["reference"]["profile"],
                    "reference": value["reference"],
                    "roles": roles,
                    "ordinary_dt": data["numerical_scope"]["dt"],
                    "specialization": data["specialization"],
                    "scientific_digest": value["scientific_digest"],
                    "reset_digest": value["reset_digest"],
                    "model_identity": value["model_identity"],
                }
            else:
                realization = item["family"][2:].replace("_", "+")
                run = data["runs"][realization][0]
                config = {
                    "graph": data["graph"],
                    "profile": data["declarations"][realization],
                    "roles": {
                        "current": {
                            "C": run["C_before"],
                            "W_A": run["W_before"],
                            "Z_4": run["Z_before"],
                        }
                    },
                    "ordinary_dt": data["dt"],
                    "reference_hodge": data["H_reference"],
                    "K4_base": data["K4_base"],
                    "edge_weights": data["edge_weights"],
                    "differential_reference": data["differential_reference"],
                }
            require(
                config["profile"]["identity_payload"]["profile_family_id"]
                == item["family"],
                "profile family mismatch",
            )
            config["graph_summary"] = graph_summary(config["graph"])
            config["parameters"] = parameter_summary(config["profile"])
            configurations[side] = config
        require("source" in configurations, "configuration has no source graph")
        status, outcomes = item.get("recorded_status"), None
        if item["format"] == "prepared-native":
            require(
                item["acceptance"] == "not_accepted",
                "prepared inputs cannot claim runtime acceptance",
            )
            report = self.artifact(item["admission"], parse=True)
            require(
                report["family"] == item["family"]
                and report["prepared_digest"] == data["record_digest"],
                "numerical report belongs to a different configuration",
            )
            require(
                report["physical_steps"] == report["events_committed"] == 0,
                "unexpected probe execution scope",
            )
            outcomes = {s: report[s] for s in ("source", "target")}
            require(
                all(set(roles) == {"current", "reset"} for roles in outcomes.values()),
                "probe must record both histories on both graphs",
            )
            values = {
                r["status"] for roles in outcomes.values() for r in roles.values()
            }
            require(
                values <= {"passed", "rejected", "incomplete"},
                "unknown numerical outcome",
            )
            status = next(iter(values)) if len(values) == 1 else "mixed"
            if status == "passed":
                status = (
                    "read-passed"
                    if item["family"].endswith("OS")
                    else "certificate-passed"
                )
        require(status in STATUSES, "unknown evidence status")
        return {
            "id": name,
            "title": item["title"],
            "model": item["model"],
            "family": item["family"],
            "scenario": item["scenario"],
            "status": status,
            "acceptance": item["acceptance"],
            "notes": item["notes"],
            "commands": item.get("commands", []),
            "evidence": item["evidence"],
            "data": item["data"],
            "configurations": configurations,
            "numerical_outcomes": outcomes,
        }

    def rows(self):
        result = []
        for name in sorted(self.entries):
            try:
                row = self.inspect(name)
                row["parameters"] = {
                    s: c["parameters"] for s, c in row["configurations"].items()
                }
                row["profile_ids"] = {
                    s: c["profile"]["complete_profile_id"]
                    for s, c in row["configurations"].items()
                }
                row["graphs"] = {
                    s: c["graph_summary"] for s, c in row.pop("configurations").items()
                }
                row.pop("numerical_outcomes")
            except (
                ValueError,
                OSError,
                KeyError,
                TypeError,
                IndexError,
                OverflowError,
            ) as exc:
                item = self.entry(name)
                row = {
                    k: item[k] for k in ("id", "title", "model", "family", "scenario")
                }
                row.update(status="stale", error=str(exc), graphs={})
            result.append(row)
        return result

    def selection(self, name, side):
        item = self.inspect(name)
        require(side in item["configurations"], f"{name} has no {side} configuration")
        config = item.pop("configurations")[side]
        result = {
            "schema": "grc-configuration-selection-v1",
            "catalog": self.path,
            "entry_digest": digest(self.entry(name)),
            "side": side,
            "configuration": config,
            "recorded_evidence": item,
            "purpose": "pinned_selection_only; numerical_admission_and_execution_are_separate",
        }
        result["selection_digest"] = digest(result)
        return deepcopy(result)

    def verify_selection(self, saved):
        require(
            saved["schema"] == "grc-configuration-selection-v1",
            "unknown selection schema",
        )
        expected = self.selection(saved["recorded_evidence"]["id"], saved["side"])
        require(
            encoded(saved) == encoded(expected),
            "selection changed or its configuration/evidence drifted; inspect and select again",
        )
        return {
            "status": "unchanged",
            "id": saved["recorded_evidence"]["id"],
            "side": saved["side"],
            "selection_digest": saved["selection_digest"],
        }


def comparable(record, side):
    require(side in record["configurations"], f"{record['id']} has no {side}")
    config = record["configurations"][side]
    values = {
        "model": record["model"],
        "family": record["family"],
        "evidence": record["status"],
        "acceptance": record["acceptance"],
        "graph": config["graph_summary"],
        "graph_content": digest(numeric_identity(config["graph"])),
        "history_content": digest(numeric_identity(config["roles"])),
        "profile_id": config["profile"]["complete_profile_id"],
        "parameters": deepcopy(config["profile"]["params_resolved"]),
        "decoded_bounds": config["parameters"],
        "ordinary_dt": config.get("ordinary_dt"),
    }
    # Per-edge maps can contain hundreds of different labels. Keep a binding and
    # count in the comparison; show/select --json retains the complete mapping.
    weights = values["parameters"]["candidate"].get("W_C_tr")
    if isinstance(weights, dict):
        values["parameters"]["candidate"]["W_C_tr"] = {
            "edge_count": len(weights),
            "content_digest": digest(numeric_identity(weights)),
        }
    flat = {}

    def visit(value, path):
        if isinstance(value, dict) and value:
            for key, child in value.items():
                visit(child, path + "." + key if path else key)
        else:
            flat[path] = value

    visit(values, "")
    return flat


def compare(records, side):
    values = [comparable(record, side) for record in records]
    result = []
    for key in sorted(set().union(*values)):
        cells = [{"present": key in value, "value": value.get(key)} for value in values]
        if len({encoded(numeric_identity(cell)) for cell in cells}) > 1:
            result.append(
                {
                    "field": key,
                    "values": dict(zip((r["id"] for r in records), cells, strict=True)),
                }
            )
    return {
        "side": side,
        "configurations": [r["id"] for r in records],
        "differences": result,
    }


def table(headers, rows):
    strings = [[str(cell) for cell in row] for row in [headers, *rows]]
    widths = [max(len(row[i]) for row in strings) for i in range(len(headers))]
    return "\n".join(
        "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip()
        for row in strings
    )


def short(value, limit=42):
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def human_show(record, side):
    require(side in record["configurations"], f"configuration has no {side}")
    value = record["configurations"][side]
    g = value["graph_summary"]
    lines = [
        f"{record['id']} — {record['title']}",
        f"{record['model']} / {record['family']} / {side}",
        f"Graph: {g['vertices']} vertices, {g['edges']} edges, {g['components']} components, cycle rank {g['cycle_rank']}, maximum degree {g['maximum_degree']}",
        f"Evidence: {record['status']}; review: {record['acceptance']}",
        "Profile: " + value["profile"]["complete_profile_id"],
        "Parameters:",
    ]
    hidden = set()
    if "resource_radius" in value["parameters"]:
        hidden.add("resource_chart")
    if "geometry_radius" in value["parameters"]:
        hidden.add("geometry_domain")
    lines += [
        f"  {k}: {v}"
        for k, v in value["parameters"].items()
        if v is not None and k not in hidden
    ]
    if value.get("ordinary_dt") is not None:
        lines.append(f"  ordinary_dt: {value['ordinary_dt']}")
    lines += [
        "Notes:",
        *("  " + text for text in record["notes"]),
        "Files:",
        "  " + record["data"]["path"],
        *("  " + ref["path"] for ref in record["evidence"]),
    ]
    if record["numerical_outcomes"]:
        lines.append("Numerical probes (both histories):")
        for graph_side, roles in record["numerical_outcomes"].items():
            for role, result in roles.items():
                lines.append(
                    f"  {graph_side}/{role}: {result['status']} — {result['owner']}"
                    + (f"; {result['reason']}" if "reason" in result else "")
                )
    lines += [
        "Reproduction commands (not executed by this tool):",
        *("  " + c for c in record["commands"]),
    ]
    return "\n".join(lines)


def family(value):
    normalized = value.upper().replace("+", "_").replace("RG2B", "RG2b")
    if normalized not in FAMILIES:
        raise argparse.ArgumentTypeError("unknown family; e.g. A_OS, C_CI+PC or A_RG2b")
    return normalized


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog",
        help="repository-relative inventory JSON; default is the shipped catalog, or the saved selection's catalog",
    )
    sub = parser.add_subparsers(dest="action", required=True)
    listing = sub.add_parser(
        "list", help="list available records without running numerical code"
    )
    listing.add_argument("--family", type=family)
    listing.add_argument("--model", choices=("GRCV4", "GRC9V4"))
    listing.add_argument("--scenario")
    listing.add_argument("--status", choices=STATUSES)
    listing.add_argument(
        "--kappa-h", type=float, help="exact recorded coupling on the selected side"
    )
    listing.add_argument("--min-vertices", type=int)
    listing.add_argument("--max-vertices", type=int)
    listing.add_argument("--min-edges", type=int)
    listing.add_argument("--max-edges", type=int)
    show = sub.add_parser(
        "show", help="inspect parameters, graph and recorded evidence"
    )
    show.add_argument("id")
    comparing = sub.add_parser(
        "compare", help="compare graph, parameter and evidence differences"
    )
    comparing.add_argument("ids", nargs="+")
    select = sub.add_parser(
        "select", help="export a pinned choice; does not execute it"
    )
    select.add_argument("id")
    select.add_argument(
        "--output",
        type=Path,
        help="new JSON file; default is stdout, existing files are preserved",
    )
    verify = sub.add_parser(
        "verify-selection", help="check a saved choice against the current artifacts"
    )
    verify.add_argument("path", type=Path)
    for command in (listing, show, comparing, select):
        command.add_argument(
            "--side",
            choices=("source", "target"),
            default="source",
            help="selected graph side; size filters apply to this side",
        )
    for command in (listing, show, comparing, verify):
        command.add_argument(
            "--json", action="store_true", help="machine-readable output"
        )
    args = parser.parse_args(argv)
    try:
        saved = (
            json_read(args.path.read_bytes())
            if args.action == "verify-selection"
            else None
        )
        catalog = Catalog(
            args.catalog or (saved["catalog"] if saved is not None else DEFAULT)
        )
        if args.action == "list":
            require(
                args.kappa_h is None or math.isfinite(args.kappa_h),
                "coupling filter must be finite",
            )
            for metric in ("vertices", "edges"):
                lo, hi = getattr(args, "min_" + metric), getattr(args, "max_" + metric)
                require(
                    (lo is None or lo >= 0) and (hi is None or hi >= 0),
                    "size filters must be nonnegative",
                )
                require(lo is None or hi is None or lo <= hi, "minimum exceeds maximum")
            rows = []
            for row in catalog.rows():
                if any(
                    getattr(args, key) and getattr(args, key) != row[key]
                    for key in ("family", "model", "scenario", "status")
                ):
                    continue
                graph = row["graphs"].get(args.side)
                if graph is None and row["status"] != "stale":
                    continue
                if (
                    args.kappa_h is not None
                    and row.get("parameters", {}).get(args.side, {}).get("kappa_H")
                    != args.kappa_h
                ):
                    continue
                fits = True
                for metric in ("vertices", "edges"):
                    lo, hi = (
                        getattr(args, "min_" + metric),
                        getattr(args, "max_" + metric),
                    )
                    if lo is not None or hi is not None:
                        fits &= (
                            graph is not None
                            and (lo is None or graph[metric] >= lo)
                            and (hi is None or graph[metric] <= hi)
                        )
                if fits:
                    rows.append(row)
            if args.json:
                print(json.dumps(rows, indent=2, allow_nan=False))
            else:
                print(
                    table(
                        [
                            "ID",
                            "MODEL",
                            "SOURCE V/E",
                            "TARGET V/E",
                            "KAPPA_H",
                            "R",
                            "M",
                            "EVIDENCE",
                        ],
                        [
                            [
                                r["id"],
                                r["model"],
                                *(
                                    f"{r['graphs'][s]['vertices']}/{r['graphs'][s]['edges']}"
                                    if s in r["graphs"]
                                    else "—"
                                    for s in ("source", "target")
                                ),
                                *(
                                    r.get("parameters", {}).get(args.side, {}).get(k)
                                    if r.get("parameters", {}).get(args.side, {}).get(k)
                                    is not None
                                    else "—"
                                    for k in (
                                        "kappa_H",
                                        "carrier_radius",
                                        "resource_radius",
                                    )
                                ),
                                r["status"],
                            ]
                            for r in rows
                        ],
                    )
                )
                print(
                    f"\n{len(rows)} configurations. Evidence is recorded scope; selecting does not run admission."
                )
                print(
                    f"Parameters shown for {args.side}: R = carrier radius, M = resource bound; — = not declared."
                )
                for row in rows:
                    if "error" in row:
                        print(f"{row['id']}: {row['error']}")
        elif args.action == "show":
            record = catalog.inspect(args.id)
            require(
                args.side in record["configurations"],
                f"configuration has no {args.side}",
            )
            if args.json:
                record["selected_side"] = args.side
            print(
                json.dumps(record, indent=2, allow_nan=False)
                if args.json
                else human_show(record, args.side)
            )
        elif args.action == "compare":
            require(
                len(args.ids) >= 2 and len(set(args.ids)) == len(args.ids),
                "compare needs at least two distinct IDs",
            )
            result = compare([catalog.inspect(name) for name in args.ids], args.side)
            if args.json:
                print(json.dumps(result, indent=2, allow_nan=False))
            else:
                print(
                    table(
                        ["DIFFERENCE", *args.ids],
                        [
                            [
                                r["field"],
                                *(
                                    short(r["values"][name]["value"])
                                    if r["values"][name]["present"]
                                    else "<absent>"
                                    for name in args.ids
                                ),
                            ]
                            for r in result["differences"]
                        ],
                    )
                )
                print(
                    "\nLong values are abbreviated; --json retains every difference in full."
                )
        elif args.action == "select":
            text = (
                json.dumps(
                    catalog.selection(args.id, args.side), indent=2, allow_nan=False
                )
                + "\n"
            )
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                with args.output.open("x") as stream:
                    stream.write(text)
                print(
                    f"Selected {args.id} ({args.side}) -> {args.output}; use verify-selection to check it later."
                )
            else:
                print(text, end="")
        else:
            result = catalog.verify_selection(saved)
            print(
                json.dumps(result, indent=2)
                if args.json
                else f"Unchanged: {result['id']} ({result['side']}); selection/evidence match."
            )
    except (ValueError, OSError, KeyError, TypeError, IndexError, OverflowError) as exc:
        parser.exit(2, f"catalog: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

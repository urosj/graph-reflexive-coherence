#!/usr/bin/env python3
"""Read-only Phase 9 verification panel on a separate local surface."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit, parse_qs

TOOL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL / "src"))
from grcv4_explorer.paths import repository_root  # noqa: E402
from grcv4_explorer.phase9_verification import verification_status  # noqa: E402
from grcv4_explorer.phase9_verification import pressure_projection  # noqa: E402
from grcv4_explorer.receipt_parents import parent_authority  # noqa: E402
from grcv4_explorer.abundance import abundance_authority  # noqa: E402
from grcv4_explorer.a_initializer import initializer_authority  # noqa: E402
from grcv4_explorer.basin import basin_authority, basin_source  # noqa: E402
from grcv4_explorer.basin_native import basin_native_status, basin_native_source
from grcv4_explorer.target_compatibility import target_compatibility_status, target_compatibility_source
from grcv4_explorer.tranche10_support import tranche10_support_status, tranche10_support_source
from grcv4_explorer.aos import aos_status, aos_source
from grcv4_explorer.cpc import cpc_status, cpc_source
from grcv4_explorer.ccipc import ccipc_status, ccipc_source
from grcv4_explorer.acipc import acipc_status, acipc_source
from grcv4_explorer.crg2b import crg2b_status, crg2b_source
from grcv4_explorer.arg2b import arg2b_status, arg2b_source
from grcv4_explorer.tranche8 import tranche8_status, tranche8_source  # noqa: E402
from grcv4_explorer.tranche8_end import tranche8_end_reviews, tranche8_end_source


from grcv4_explorer.tranche9 import (tranche9_status, tranche9_source,
    tranche9_compatibility_status, tranche9_compatibility_source,
    tranche9_crossing_status, tranche9_crossing_source, tranche9_public_status, tranche9_public_source,
    tranche9_conflict_status, tranche9_conflict_source,
    tranche9_support_status, tranche9_support_source)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urlsplit(self.path)
        if request.path in {"/api/aos", "/api/aos/source", "/api/cpc", "/api/cpc/source", "/api/ccipc", "/api/ccipc/source", "/api/acipc", "/api/acipc/source", "/api/crg2b", "/api/crg2b/source", "/api/arg2b", "/api/arg2b/source"}:
            views = {"aos": (aos_status, aos_source), "cpc": (cpc_status, cpc_source), "ccipc": (ccipc_status, ccipc_source), "acipc": (acipc_status, acipc_source), "crg2b": (crg2b_status, crg2b_source), "arg2b": (arg2b_status, arg2b_source)}
            view, source = views[request.path.split("/")[2]]
            try:
                query = parse_qs(request.query, strict_parsing=True, keep_blank_values=True)
                root = repository_root()
                if request.path.endswith("/source"):
                    if set(query) != {"path"} or len(query["path"]) != 1:
                        raise KeyError("one indexed source path required")
                    content, ref = source(root, query["path"][0])
                else:
                    if query:
                        raise KeyError("Realization evidence has fixed scope")
                    content = json.dumps(view(root)).encode()
                self.send_response(200)
                if request.path.endswith("/source"):
                    self.send_header("X-Evidence-SHA256", ref["sha256"])
            except KeyError as error:
                self.send_response(404)
                content = json.dumps({"error": str(error)}).encode()
            except Exception as error:
                self.send_response(503)
                content = json.dumps({"error": str(error)}).encode()
            self.send_header("Content-Type", "application/octet-stream" if request.path.endswith("/source") else "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if request.path in {"/api/tranche10/targets", "/api/tranche10/targets/source", "/api/tranche10/support", "/api/tranche10/support/source"}:
            try:
                query = parse_qs(request.query, strict_parsing=True)
                root = repository_root()
                if request.path.endswith("/source"):
                    if set(query) != {"path"} or len(query["path"]) != 1:
                        raise KeyError("one indexed source path required")
                    source = tranche10_support_source if "/support/" in request.path else target_compatibility_source
                    content, ref = source(root, query["path"][0])
                else:
                    if query:
                        raise KeyError("expanded-target evidence has fixed scope")
                    view = tranche10_support_status if request.path.endswith("support") else target_compatibility_status
                    content = json.dumps(view(root)).encode()
                self.send_response(200)
                if request.path.endswith("/source"):
                    self.send_header("X-Evidence-SHA256", ref["sha256"])
            except KeyError as error:
                self.send_response(404)
                content = json.dumps({"error": str(error)}).encode()
            except Exception as error:
                self.send_response(503)
                content = json.dumps({"error": str(error)}).encode()
            self.send_header("Content-Type", "application/octet-stream" if request.path.endswith("/source") else "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if request.path in {"/api/basin", "/api/basin/source", "/api/basin/native", "/api/basin/native/source"}:
            try:
                query = parse_qs(request.query, strict_parsing=True)
                root = repository_root()
                if request.path in {"/api/basin", "/api/basin/native"}:
                    if query:
                        raise KeyError("basin authority has fixed scope")
                    content = json.dumps(basin_native_status(root) if request.path.endswith("native") else basin_authority(root, TOOL.parent)).encode()
                else:
                    if set(query) != {"path"} or len(query["path"]) != 1:
                        raise KeyError("one indexed source path required")
                    content, ref = basin_native_source(root, query["path"][0]) if "/native/" in request.path else basin_source(root, TOOL.parent, query["path"][0])
                self.send_response(200)
                if request.path.endswith("/source"):
                    self.send_header("X-Evidence-SHA256", ref["sha256"])
            except KeyError as error:
                self.send_response(404)
                content = json.dumps({"error": str(error)}).encode()
            except Exception as error:
                self.send_response(503)
                content = json.dumps({"error": str(error)}).encode()
            self.send_header("Content-Type", "application/octet-stream" if request.path.endswith("/source") else "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if request.path in {"/api/tranche9", "/api/tranche9/source", "/api/tranche9/compatibility", "/api/tranche9/compatibility/source", "/api/tranche9/crossings", "/api/tranche9/crossings/source", "/api/tranche9/public", "/api/tranche9/public/source", "/api/tranche9/conflict", "/api/tranche9/conflict/source", "/api/tranche9/support", "/api/tranche9/support/source"}:
            try:
                query = parse_qs(request.query, strict_parsing=True)
                if request.path in {"/api/tranche9", "/api/tranche9/compatibility", "/api/tranche9/crossings", "/api/tranche9/public", "/api/tranche9/conflict", "/api/tranche9/support"}:
                    if query: raise KeyError("Tranche 9 has a fixed four-family scope")
                    view = tranche9_support_status if request.path.endswith("support") else tranche9_conflict_status if request.path.endswith("conflict") else tranche9_public_status if request.path.endswith("public") else tranche9_crossing_status if request.path.endswith("crossings") else tranche9_compatibility_status if request.path.endswith("compatibility") else tranche9_status
                    content = json.dumps(view(repository_root())).encode()
                else:
                    if set(query) != {"path"} or len(query["path"]) != 1:
                        raise KeyError("one indexed source path required")
                    source = tranche9_support_source if "/support/" in request.path else tranche9_conflict_source if "/conflict/" in request.path else tranche9_public_source if "/public/" in request.path else tranche9_crossing_source if "/crossings/" in request.path else tranche9_compatibility_source if "/compatibility/" in request.path else tranche9_source
                    content, ref = source(repository_root(), query["path"][0])
                self.send_response(200)
                if request.path.endswith("/source"):
                    self.send_header("X-Evidence-SHA256", ref["sha256"])
            except KeyError as error:
                self.send_response(404)
                content = json.dumps({"error": str(error)}).encode()
            except Exception as error:
                self.send_response(503)
                content = json.dumps({"error": str(error), "evidence_state": "unavailable_not_admitted"}).encode()
            self.send_header("Content-Type", "application/octet-stream" if request.path.endswith("/source") else "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if request.path in {"/api/tranche8", "/api/tranche8/source", "/api/tranche8/end", "/api/tranche8/end/source"}:
            content_type = "application/json"
            try:
                query = parse_qs(request.query, strict_parsing=True)
                selected = {}
                if "family" in query or "checkpoint" in query:
                    if any(len(query.get(k, [])) != 1 for k in ("family", "checkpoint")):
                        raise KeyError("one family and checkpoint required")
                    selected = {k: query.pop(k)[0] for k in ("family", "checkpoint")}
                if request.path in {"/api/tranche8", "/api/tranche8/end"}:
                    if query:
                        raise KeyError("unknown Tranche 8 status arguments")
                    if request.path.endswith('/end'):
                        if selected:raise KeyError('final reviews have a fixed four-family scope')
                        value=tranche8_end_reviews(repository_root())
                    else:value=tranche8_status(repository_root(), **selected)
                    content = json.dumps(value, ensure_ascii=False).encode()
                else:
                    if set(query) != {"path"} or len(query["path"]) != 1:
                        raise KeyError("one indexed repository-relative path required")
                    if request.path == '/api/tranche8/end/source':
                        if selected:raise KeyError('final reviews have a fixed four-family scope')
                        content,ref=tranche8_end_source(repository_root(),query['path'][0])
                    else:content, ref = tranche8_source(repository_root(), query["path"][0], **selected)
                    content_type = "text/plain; charset=utf-8"
                self.send_response(200)
                if request.path.endswith("/source"):
                    self.send_header("X-Evidence-SHA256", ref["sha256"])
                    self.send_header("X-Evidence-Revision", ref["revision"])
            except KeyError as error:
                content = json.dumps({"error": str(error)}).encode()
                self.send_response(404)
            except Exception as error:
                content = json.dumps({"error": str(error), "evidence_state": "unavailable_not_admitted"}).encode()
                self.send_response(503)
            self.send_header("Content-Type", content_type)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if self.path in {"/api/receipt-parents", "/api/abundance", "/api/a-initializer"}:
            try:
                query = {"/api/abundance": abundance_authority,
                         "/api/receipt-parents": parent_authority,
                         "/api/a-initializer": initializer_authority}[self.path]
                content = json.dumps(query(repository_root(), TOOL.parent)).encode()
                self.send_response(200)
            except Exception:
                content = b'{"error":"Authority unavailable; no historical fallback or conformance inferred."}'
                self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if request.path == "/api/probe":
            try:
                query = parse_qs(request.query, strict_parsing=True)
                if set(query) != {"case_id"} or len(query["case_id"]) != 1:
                    raise KeyError("one exact case_id required")
                content = json.dumps(
                    pressure_projection(repository_root(), query["case_id"][0]),
                    ensure_ascii=False,
                ).encode()
                self.send_response(200)
            except KeyError as error:
                content = json.dumps({"error": str(error)}).encode()
                self.send_response(404)
            except Exception as error:
                content = json.dumps(
                    {"error": str(error), "evidence_state": "unavailable_not_admitted"}
                ).encode()
                self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if self.path == "/api/status":
            try:
                content = json.dumps(
                    verification_status(repository_root()), ensure_ascii=False
                ).encode()
                self.send_response(200)
            except Exception:
                content = b'{"current_boundary":"failed_closed","error":"Status unavailable; use the CLI for diagnostics."}'
                self.send_response(503)
            self.send_header("Content-Type", "application/json")
        elif self.path in {"/", "/verification.js", "/g2-registry.js", "/aggregate-review.js", "/specialization-review.js", "/tranche8-evidence.js", "/tranche8-apc-evidence.js", "/tranche8-handoff.js", "/tranche8-lifecycle.js", "/tranche8-conformance.js", "/tranche8-end.js", "/tranche8.js", "/tranche9.js", "/basin.js", "/target-compatibility.js", "/tranche10-support.js", "/aos.js", "/cpc.js", "/ccipc.js", "/acipc.js", "/crg2b.js", "/arg2b.js", "/verification.css"}:
            name = "index.html" if self.path == "/" else self.path[1:]
            content = (TOOL / "phase9-web" / name).read_bytes()
            self.send_response(200)
            self.send_header(
                "Content-Type",
                {
                    "index.html": "text/html; charset=utf-8",
                    "verification.js": "text/javascript",
                    "g2-registry.js": "text/javascript",
                    "aggregate-review.js": "text/javascript",
                    "specialization-review.js": "text/javascript",
                    "tranche8-evidence.js": "text/javascript",
                    "tranche8-apc-evidence.js": "text/javascript",
                    "tranche8-handoff.js": "text/javascript",
                    "tranche8-lifecycle.js": "text/javascript",
                    "tranche8-conformance.js": "text/javascript",
                    "tranche8-end.js": "text/javascript",
                    "tranche9.js": "text/javascript",
                    "basin.js": "text/javascript",
                    "target-compatibility.js": "text/javascript",
                    "tranche10-support.js": "text/javascript",
                    "aos.js": "text/javascript",
                    "cpc.js": "text/javascript",
                    "ccipc.js": "text/javascript",
                    "acipc.js": "text/javascript",
                    "crg2b.js": "text/javascript",
                    "arg2b.js": "text/javascript",
                    "tranche8.js": "text/javascript",
                    "verification.css": "text/css",
                }[name],
            )
        else:
            self.send_error(404)
            return
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        self.send_error(405, "Read-only verification surface")

    def log_message(self, *args):
        pass


def main():
    if Path(sys.prefix).resolve() != (repository_root() / ".venv").resolve():
        raise RuntimeError("use the existing repository .venv")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=4174)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(
        f"PHASE9_VERIFICATION_SERVE http://127.0.0.1:{server.server_port} read_only=true",
        flush=True,
    )
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

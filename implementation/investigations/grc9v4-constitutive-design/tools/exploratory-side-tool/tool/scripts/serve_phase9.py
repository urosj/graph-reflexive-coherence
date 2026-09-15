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


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urlsplit(self.path)
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
        elif self.path in {"/", "/verification.js", "/g2-registry.js", "/aggregate-review.js", "/specialization-review.js", "/verification.css"}:
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

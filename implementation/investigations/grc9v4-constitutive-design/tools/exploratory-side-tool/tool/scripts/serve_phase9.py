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
from grcv4_explorer.spark_completion import spark_completion_authority, spark_completion_source
from grcv4_explorer.spark_applicability import spark_applicability_authority, spark_applicability_source
from grcv4_explorer.spark_research import spark_research_status, spark_research_source
from grcv4_explorer.spark_cipc_research import spark_cipc_research_status, spark_cipc_research_source
from grcv4_explorer.spark_cipc import spark_cipc_authority, spark_cipc_source
from grcv4_explorer.spark_aci import spark_aci_authority, spark_aci_source
from grcv4_explorer.spark_apc import spark_apc_authority, spark_apc_source
from grcv4_explorer.spark_acipc import spark_acipc_authority, spark_acipc_source
from grcv4_explorer.spark_crg2b import spark_crg2b_authority, spark_crg2b_source
from grcv4_explorer.spark_arg2b import spark_arg2b_authority, spark_arg2b_source
from grcv4_explorer.spark_earlier_accepted import spark_earlier_authority, spark_earlier_source
from grcv4_explorer.spark_publication import spark_publication_source
from grcv4_explorer.spark_native_cos import native_cos_numerics, native_cos_numerics_source
from grcv4_explorer.spark_native_lifecycle import native_lifecycle, native_lifecycle_source
from grcv4_explorer.spark_native_cci_pressure import native_cci_pressure, native_cci_pressure_source
from grcv4_explorer.spark_native_cci_campaign import native_cci_campaign, native_cci_campaign_source
from grcv4_explorer.spark_native_cpc_pressure import native_cpc_pressure, native_cpc_pressure_source
from grcv4_explorer.spark_native_cpc_campaign import native_cpc_campaign, native_cpc_campaign_source
from grcv4_explorer.spark_native_ccipc_campaign import native_ccipc_campaign, native_ccipc_campaign_source
from grcv4_explorer.spark_native_ccipc_pressure import native_ccipc_pressure, native_ccipc_pressure_source
from grcv4_explorer.spark_native_ccipc import native_ccipc, native_ccipc_source
from grcv4_explorer.spark_native_aci_campaign import native_aci_campaign, native_aci_campaign_source
from grcv4_explorer.spark_native_apc_campaign import native_apc_campaign, native_apc_campaign_source
from grcv4_explorer.spark_native_aos_campaign import native_aos_campaign, native_aos_campaign_source
from grcv4_explorer.spark_native_aci_pressure import native_aci_pressure, native_aci_pressure_source
from grcv4_explorer.spark_native_aci import native_aci, native_aci_source
from grcv4_explorer.spark_native_apc import native_apc, native_apc_source
from grcv4_explorer.spark_native_arg2b_pressure import native_arg2b_pressure, native_arg2b_pressure_source
from grcv4_explorer.spark_native_arg2b import native_arg2b, native_arg2b_source
from grcv4_explorer.spark_native_rg2b_campaign import native_rg2b_campaign, native_rg2b_campaign_source
from grcv4_explorer.spark_native_crg2b import native_crg2b, native_crg2b_source
from grcv4_explorer.spark_native_acipc import native_acipc, native_acipc_source
from grcv4_explorer.spark_native_acipc_campaign import native_acipc_campaign, native_acipc_campaign_source
from grcv4_explorer.spark_native_crg2b_pressure import native_crg2b_pressure, native_crg2b_pressure_source
from grcv4_explorer.spark_native_acipc_pressure import native_acipc_pressure, native_acipc_pressure_source
from grcv4_explorer.spark_native_apc_pressure import native_apc_pressure, native_apc_pressure_source
from grcv4_explorer.spark_native_aos import native_aos, native_aos_source
from grcv4_explorer.spark_native_aos_pressure import native_aos_pressure, native_aos_pressure_source
from grcv4_explorer.spark_native_cpc import native_cpc, native_cpc_source
from grcv4_explorer.spark_native_cci import native_cci, native_cci_source
from grcv4_explorer.spark_native_preflight import native_preflight, native_preflight_source
from grcv4_explorer.spark_native_campaign import native_campaign, native_campaign_source
from grcv4_explorer.spark_earlier_c import spark_earlier_c_status, spark_earlier_c_source
from grcv4_explorer.spark_arg2b_research import spark_arg2b_research_status, spark_arg2b_research_source
from grcv4_explorer.spark_crg2b_research import spark_crg2b_research_status, spark_crg2b_research_source
from grcv4_explorer.spark_acipc_research import spark_acipc_research_status, spark_acipc_research_source
from grcv4_explorer.spark_apc_research import spark_apc_research_status, spark_apc_research_source
from grcv4_explorer.spark_aci_research import spark_aci_research_status, spark_aci_research_source
from grcv4_explorer.spark_aos import spark_aos_authority, spark_aos_source
from grcv4_explorer.spark_aos_earlier import spark_aos_earlier_status, spark_aos_earlier_source
from grcv4_explorer.spark_aos_research import spark_aos_research_status, spark_aos_research_source
from grcv4_explorer.spark_pc import spark_pc_authority, spark_pc_source
from grcv4_explorer.basin_native import basin_native_status, basin_native_source
from grcv4_explorer.target_compatibility import target_compatibility_status, target_compatibility_source
from grcv4_explorer.tranche10_support import tranche10_support_status, tranche10_support_source
from grcv4_explorer.tranche10_examples import tranche10_examples_status, tranche10_examples_source
from grcv4_explorer.tranche10_regressions import tranche10_regressions_status, tranche10_regressions_source
from grcv4_explorer.tranche10_verification import tranche10_verification_status, tranche10_verification_source
from grcv4_explorer.tranche10_families import family_basin_status, family_basin_source
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
        if request.path in {"/api/tranche10/families", "/api/tranche10/families/source"}:
            try:
                query = parse_qs(request.query, strict_parsing=True, keep_blank_values=True)
                source = request.path.endswith("/source")
                if set(query) != ({"family", "path"} if source else {"family"}) or any(len(v) != 1 for v in query.values()):
                    raise KeyError("one explicit family and indexed source path required")
                if source:
                    content, ref = family_basin_source(repository_root(), query["path"][0], query["family"][0])
                else:
                    content = json.dumps(family_basin_status(repository_root(), query["family"][0])).encode()
                self.send_response(200)
                if source:
                    self.send_header("X-Evidence-SHA256", ref["sha256"])
            except KeyError as error:
                self.send_response(404); content = json.dumps({"error": str(error)}).encode()
            except Exception as error:
                self.send_response(503); content = json.dumps({"error": str(error)}).encode()
            self.send_header("Content-Type", "application/octet-stream" if request.path.endswith("/source") else "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers(); self.wfile.write(content)
            return
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
        if request.path in {"/api/tranche10/targets", "/api/tranche10/targets/source", "/api/tranche10/support", "/api/tranche10/support/source", "/api/tranche10/verification", "/api/tranche10/verification/source", "/api/tranche10/regressions", "/api/tranche10/regressions/source", "/api/tranche10/examples", "/api/tranche10/examples/source"}:
            try:
                query = parse_qs(request.query, strict_parsing=True)
                root = repository_root()
                if request.path.endswith("/source"):
                    if set(query) != {"path"} or len(query["path"]) != 1:
                        raise KeyError("one indexed source path required")
                    source = {"targets": target_compatibility_source, "support": tranche10_support_source,
                              "verification": tranche10_verification_source, "regressions": tranche10_regressions_source, "examples": tranche10_examples_source}[request.path.split("/")[3]]
                    content, ref = source(root, query["path"][0])
                else:
                    if query:
                        raise KeyError("expanded-target evidence has fixed scope")
                    view = {"targets": target_compatibility_status, "support": tranche10_support_status,
                            "verification": tranche10_verification_status, "regressions": tranche10_regressions_status, "examples": tranche10_examples_status}[request.path.split("/")[3]]
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
        if request.path == "/api/native-spark/c-os/campaign/compact/source":
            try:
                if request.query:
                    raise ValueError("compact evidence has fixed scope")
                from grcv4_explorer.spark_native_campaign import native_campaign_compact_source
                content = native_campaign_compact_source(repository_root())
                self.send_response(200)
            except (ValueError, OSError) as exc:
                self.send_response(503)
                content = json.dumps({"error": str(exc)}).encode()
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if request.path in {"/api/native-spark/c-rg2b/campaign", "/api/native-spark/c-rg2b/campaign/source", "/api/native-spark/a-rg2b/campaign", "/api/native-spark/a-rg2b/campaign/source"}:
            try:
                if request.query:
                    raise ValueError("fixed RG2b campaign scope")
                family = "C_RG2b" if "/c-rg2b/" in request.path else "A_RG2b"
                root = repository_root()
                content = (native_rg2b_campaign_source(root, family) if request.path.endswith("/source")
                           else json.dumps(native_rg2b_campaign(root, family)).encode())
                self.send_response(200)
            except Exception as error:
                self.send_response(503)
                content = json.dumps({"error": str(error), "evidence_state": "unavailable_not_admitted"}).encode()
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if request.path in {"/api/native-spark/a-rg2b/pressure", "/api/native-spark/a-rg2b/pressure/source", "/api/native-spark/a-rg2b/preflight", "/api/native-spark/a-rg2b/preflight/source", "/api/native-spark/c-rg2b/pressure", "/api/native-spark/c-rg2b/pressure/source", "/api/native-spark/c-rg2b/preflight", "/api/native-spark/c-rg2b/preflight/source", "/api/native-spark/a-ci-pc/campaign", "/api/native-spark/a-ci-pc/campaign/source", "/api/native-spark/a-ci-pc/pressure", "/api/native-spark/a-ci-pc/pressure/source", "/api/native-spark/a-ci-pc/preflight", "/api/native-spark/a-ci-pc/preflight/source", "/api/native-spark/a-pc/campaign", "/api/native-spark/a-pc/campaign/source", "/api/native-spark/a-pc/pressure", "/api/native-spark/a-pc/pressure/source", "/api/native-spark/a-pc/preflight", "/api/native-spark/a-pc/preflight/source", "/api/native-spark/a-ci/campaign", "/api/native-spark/a-ci/campaign/source", "/api/native-spark/a-ci/pressure", "/api/native-spark/a-ci/pressure/source", "/api/native-spark/a-ci/preflight", "/api/native-spark/a-ci/preflight/source", "/api/native-spark/a-os/campaign", "/api/native-spark/a-os/campaign/source", "/api/native-spark/a-os/pressure", "/api/native-spark/a-os/pressure/source", "/api/native-spark/a-os/preflight", "/api/native-spark/a-os/preflight/source", "/api/native-spark/c-ci-pc/campaign", "/api/native-spark/c-ci-pc/campaign/source", "/api/native-spark/c-ci-pc/pressure", "/api/native-spark/c-ci-pc/pressure/source", "/api/native-spark/c-ci-pc/preflight", "/api/native-spark/c-ci-pc/preflight/source", "/api/native-spark/c-pc/campaign", "/api/native-spark/c-pc/campaign/source", "/api/native-spark/c-pc/pressure", "/api/native-spark/c-pc/pressure/source", "/api/native-spark/c-pc/preflight", "/api/native-spark/c-pc/preflight/source", "/api/native-spark/c-ci/campaign", "/api/native-spark/c-ci/campaign/source", "/api/native-spark/c-ci/pressure", "/api/native-spark/c-ci/pressure/source", "/api/native-spark/c-ci/preflight", "/api/native-spark/c-ci/preflight/source", "/api/native-spark/c-os/numerical-bridge", "/api/native-spark/c-os/numerical-bridge/source",
                            "/api/native-spark/c-os/lifecycle", "/api/native-spark/c-os/lifecycle/source",
                            "/api/native-spark/c-os/preflight", "/api/native-spark/c-os/preflight/source",
                            "/api/native-spark/c-os/campaign", "/api/native-spark/c-os/campaign/source"}:
            try:
                if request.query:
                    raise ValueError("native numerical evidence has fixed scope")
                root = repository_root()
                source, projection = ((native_arg2b_pressure_source, native_arg2b_pressure) if "/a-rg2b/pressure" in request.path
                                      else (native_arg2b_source, native_arg2b) if "/a-rg2b/" in request.path
                                      else (native_crg2b_pressure_source, native_crg2b_pressure) if "/c-rg2b/pressure" in request.path
                                      else (native_crg2b_source, native_crg2b) if "/c-rg2b/" in request.path
                                      else (native_acipc_campaign_source, native_acipc_campaign) if "/a-ci-pc/campaign" in request.path
                                      else (native_acipc_pressure_source, native_acipc_pressure) if "/a-ci-pc/pressure" in request.path
                                      else (native_acipc_source, native_acipc) if "/a-ci-pc/" in request.path
                                      else (native_apc_pressure_source, native_apc_pressure) if "/a-pc/pressure" in request.path
                                      else (native_apc_campaign_source, native_apc_campaign) if "/a-pc/campaign" in request.path
                                      else (native_apc_source, native_apc) if "/a-pc/" in request.path
                                      else (native_aci_campaign_source, native_aci_campaign) if "/a-ci/campaign" in request.path
                                      else (native_aos_campaign_source, native_aos_campaign) if "/a-os/campaign" in request.path
                                      else (native_aos_pressure_source, native_aos_pressure) if "/a-os/pressure" in request.path
                                      else (native_aos_source, native_aos) if "/a-os/" in request.path
                                      else (native_aci_pressure_source, native_aci_pressure) if "/a-ci/pressure" in request.path
                                      else (native_aci_source, native_aci) if "/a-ci/" in request.path
                                      else (native_ccipc_pressure_source, native_ccipc_pressure) if "/c-ci-pc/pressure" in request.path
                                      else (native_ccipc_campaign_source, native_ccipc_campaign) if "/c-ci-pc/campaign" in request.path
                                      else (native_ccipc_source, native_ccipc) if "/c-ci-pc/" in request.path
                                      else (native_cpc_campaign_source, native_cpc_campaign) if "/c-pc/campaign" in request.path
                                      else (native_cpc_pressure_source, native_cpc_pressure) if "/c-pc/pressure" in request.path
                                      else (native_cpc_source, native_cpc) if "/c-pc/" in request.path
                                      else (native_cci_campaign_source, native_cci_campaign) if "/c-ci/campaign" in request.path
                                      else (native_cci_pressure_source, native_cci_pressure) if "/c-ci/pressure" in request.path
                                      else (native_cci_source, native_cci) if "/c-ci/" in request.path
                                      else (native_campaign_source, native_campaign) if "/campaign" in request.path
                                      else (native_preflight_source, native_preflight) if "/preflight" in request.path
                                      else (native_lifecycle_source, native_lifecycle) if "/lifecycle" in request.path
                                      else (native_cos_numerics_source, native_cos_numerics))
                content = source(root) if request.path.endswith("/source") else json.dumps(projection(root)).encode()
                self.send_response(200)
            except Exception as error:
                self.send_response(503)
                content = json.dumps({"error": str(error), "evidence_state": "unavailable_not_admitted"}).encode()
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if request.path in {"/api/spark-completion", "/api/spark-completion/source",
                            "/api/spark-completion/publication/source",
                            "/api/spark-completion/applicability", "/api/spark-completion/applicability/source",
                            "/api/spark-completion/applicability/research", "/api/spark-completion/applicability/research/source",
                            "/api/spark-completion/applicability/ci-pc", "/api/spark-completion/applicability/ci-pc/source",
                            "/api/spark-completion/applicability/ci-pc/research", "/api/spark-completion/applicability/ci-pc/research/source",
                            "/api/spark-completion/applicability/a-ci", "/api/spark-completion/applicability/a-ci/source",
                            "/api/spark-completion/applicability/a-pc", "/api/spark-completion/applicability/a-pc/source",
                            "/api/spark-completion/applicability/a-ci-pc", "/api/spark-completion/applicability/a-ci-pc/source",
                            "/api/spark-completion/applicability/c-rg2b", "/api/spark-completion/applicability/c-rg2b/source",
                            "/api/spark-completion/applicability/a-rg2b", "/api/spark-completion/applicability/a-rg2b/source",
                            "/api/spark-completion/applicability/earlier-accepted", "/api/spark-completion/applicability/earlier-accepted/source",
                            "/api/spark-completion/applicability/earlier-c", "/api/spark-completion/applicability/earlier-c/source",
                            "/api/spark-completion/applicability/a-rg2b/research", "/api/spark-completion/applicability/a-rg2b/research/source",
                            "/api/spark-completion/applicability/c-rg2b/research", "/api/spark-completion/applicability/c-rg2b/research/source",
                            "/api/spark-completion/applicability/a-ci-pc/research", "/api/spark-completion/applicability/a-ci-pc/research/source",
                            "/api/spark-completion/applicability/a-pc/research", "/api/spark-completion/applicability/a-pc/research/source",
                            "/api/spark-completion/applicability/a-ci/research", "/api/spark-completion/applicability/a-ci/research/source",
                            "/api/spark-completion/applicability/a-os", "/api/spark-completion/applicability/a-os/source",
                            "/api/spark-completion/applicability/a-os/earlier", "/api/spark-completion/applicability/a-os/earlier/source",
                            "/api/spark-completion/applicability/a-os/research", "/api/spark-completion/applicability/a-os/research/source",
                            "/api/spark-completion/applicability/pc", "/api/spark-completion/applicability/pc/source"}:
            try:
                query = parse_qs(request.query, strict_parsing=True)
                root = repository_root()
                applicability = request.path.startswith("/api/spark-completion/applicability")
                authority_reader = spark_applicability_authority if applicability else spark_completion_authority
                source_reader = spark_applicability_source if applicability else spark_completion_source
                if request.path == "/api/spark-completion/publication/source":
                    source_reader = spark_publication_source
                if request.path in {"/api/spark-completion/applicability/earlier-accepted", "/api/spark-completion/applicability/earlier-accepted/source"}:
                    authority_reader, source_reader = spark_earlier_authority, spark_earlier_source
                if request.path.startswith("/api/spark-completion/applicability/research"):
                    authority_reader, source_reader = spark_research_status, spark_research_source
                if request.path.startswith("/api/spark-completion/applicability/pc"):
                    authority_reader, source_reader = spark_pc_authority, spark_pc_source
                if request.path in {"/api/spark-completion/applicability/ci-pc", "/api/spark-completion/applicability/ci-pc/source"}:
                    authority_reader, source_reader = spark_cipc_authority, spark_cipc_source
                if request.path.startswith("/api/spark-completion/applicability/ci-pc/research"):
                    authority_reader, source_reader = spark_cipc_research_status, spark_cipc_research_source
                if request.path in {"/api/spark-completion/applicability/a-os", "/api/spark-completion/applicability/a-os/source"}:
                    authority_reader, source_reader = spark_aos_authority, spark_aos_source
                if request.path.startswith("/api/spark-completion/applicability/a-os/research"):
                    authority_reader, source_reader = spark_aos_research_status, spark_aos_research_source
                if request.path.startswith("/api/spark-completion/applicability/a-os/earlier"):
                    authority_reader, source_reader = spark_aos_earlier_status, spark_aos_earlier_source
                if request.path in {"/api/spark-completion/applicability/a-ci", "/api/spark-completion/applicability/a-ci/source"}:
                    authority_reader, source_reader = spark_aci_authority, spark_aci_source
                if request.path.startswith("/api/spark-completion/applicability/a-ci/research"):
                    authority_reader, source_reader = spark_aci_research_status, spark_aci_research_source
                if request.path in {"/api/spark-completion/applicability/a-pc", "/api/spark-completion/applicability/a-pc/source"}:
                    authority_reader, source_reader = spark_apc_authority, spark_apc_source
                if request.path.startswith("/api/spark-completion/applicability/a-pc/research"):
                    authority_reader, source_reader = spark_apc_research_status, spark_apc_research_source
                if request.path in {"/api/spark-completion/applicability/a-ci-pc", "/api/spark-completion/applicability/a-ci-pc/source"}:
                    authority_reader, source_reader = spark_acipc_authority, spark_acipc_source
                if request.path.startswith("/api/spark-completion/applicability/a-ci-pc/research"):
                    authority_reader, source_reader = spark_acipc_research_status, spark_acipc_research_source
                if request.path in {"/api/spark-completion/applicability/c-rg2b", "/api/spark-completion/applicability/c-rg2b/source"}:
                    authority_reader, source_reader = spark_crg2b_authority, spark_crg2b_source
                if request.path.startswith("/api/spark-completion/applicability/c-rg2b/research"):
                    authority_reader, source_reader = spark_crg2b_research_status, spark_crg2b_research_source
                if request.path in {"/api/spark-completion/applicability/a-rg2b", "/api/spark-completion/applicability/a-rg2b/source"}:
                    authority_reader, source_reader = spark_arg2b_authority, spark_arg2b_source
                if request.path in {"/api/spark-completion/applicability/earlier-c", "/api/spark-completion/applicability/earlier-c/source"}:
                    authority_reader, source_reader = spark_earlier_c_status, spark_earlier_c_source
                if request.path.startswith("/api/spark-completion/applicability/a-rg2b/research"):
                    authority_reader, source_reader = spark_arg2b_research_status, spark_arg2b_research_source
                if not request.path.endswith("/source"):
                    if query:
                        raise KeyError("spark-completion authority has fixed scope")
                    content = json.dumps(authority_reader(root, TOOL.parent)).encode()
                else:
                    if set(query) != {"path"} or len(query["path"]) != 1:
                        raise KeyError("one indexed source path required")
                    content, ref = source_reader(root, TOOL.parent, query["path"][0])
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
        elif self.path in {"/", "/verification.js", "/g2-registry.js", "/aggregate-review.js", "/specialization-review.js", "/tranche8-evidence.js", "/tranche8-apc-evidence.js", "/tranche8-handoff.js", "/tranche8-lifecycle.js", "/tranche8-conformance.js", "/tranche8-end.js", "/tranche8.js", "/tranche9.js", "/basin.js", "/spark-completion.js", "/spark-applicability.js", "/spark-research.js", "/spark-pc.js", "/spark-cipc.js", "/spark-cipc-research.js", "/spark-aos-research.js", "/spark-aos.js", "/spark-aos-earlier.js", "/spark-aci-research.js", "/spark-apc-research.js", "/spark-acipc-research.js", "/spark-crg2b-research.js", "/spark-native-cos.js", "/spark-native-lifecycle.js", "/spark-native-preflight.js", "/spark-native-cpc.js", "/spark-native-ccipc.js", "/spark-native-aos.js", "/spark-native-acipc.js", "/spark-native-crg2b.js", "/spark-native-arg2b.js", "/spark-native-apc.js", "/spark-native-aci.js", "/spark-native-apc-campaign.js", "/spark-native-acipc-campaign.js", "/spark-native-rg2b-campaign.js", "/spark-native-aci-campaign.js", "/spark-native-aos-campaign.js", "/spark-native-ccipc-campaign.js", "/spark-native-cpc-campaign.js", "/spark-native-cci.js", "/spark-native-cci-campaign.js", "/spark-native-campaign.js", "/spark-earlier-accepted.js", "/spark-earlier-c.js", "/spark-arg2b-research.js", "/spark-arg2b.js", "/spark-crg2b.js", "/spark-acipc.js", "/spark-apc.js", "/spark-aci.js", "/target-compatibility.js", "/tranche10-support.js", "/tranche10-regressions.js", "/tranche10-examples.js", "/tranche10-verification.js", "/tranche10-families.js", "/aos.js", "/cpc.js", "/ccipc.js", "/acipc.js", "/crg2b.js", "/arg2b.js", "/verification.css"}:
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
                    "spark-completion.js": "text/javascript",
                    "spark-applicability.js": "text/javascript",
                    "spark-research.js": "text/javascript",
                    "spark-pc.js": "text/javascript",
                    "spark-cipc.js": "text/javascript",
                    "spark-cipc-research.js": "text/javascript",
                    "spark-aos-research.js": "text/javascript",
                    "spark-aos.js": "text/javascript",
                    "spark-aos-earlier.js": "text/javascript",
                    "spark-aci-research.js": "text/javascript",
                    "spark-apc-research.js": "text/javascript",
                    "spark-acipc-research.js": "text/javascript",
                    "spark-crg2b-research.js": "text/javascript",
                    "spark-native-cos.js": "text/javascript",
                    "spark-native-lifecycle.js": "text/javascript",
                    "spark-native-preflight.js": "text/javascript",
                    "spark-native-cpc.js": "text/javascript",
                    "spark-native-ccipc.js": "text/javascript",
                    "spark-native-acipc.js": "text/javascript",
                    "spark-native-crg2b.js": "text/javascript",
                    "spark-native-arg2b.js": "text/javascript",
                    "spark-native-apc.js": "text/javascript",
                    "spark-native-aci.js": "text/javascript",
                    "spark-native-aos.js": "text/javascript",
                    "spark-native-apc-campaign.js": "text/javascript",
                    "spark-native-acipc-campaign.js": "text/javascript",
                    "spark-native-rg2b-campaign.js": "text/javascript",
                    "spark-native-aci-campaign.js": "text/javascript",
                    "spark-native-aos-campaign.js": "text/javascript",
                    "spark-native-ccipc-campaign.js": "text/javascript",
                    "spark-native-cpc-campaign.js": "text/javascript",
                    "spark-native-cci.js": "text/javascript",
                    "spark-native-cci-campaign.js": "text/javascript",
                    "spark-native-campaign.js": "text/javascript",
                    "spark-earlier-accepted.js": "text/javascript",
                    "spark-earlier-c.js": "text/javascript",
                    "spark-arg2b-research.js": "text/javascript",
                    "spark-arg2b.js": "text/javascript",
                    "spark-crg2b.js": "text/javascript",
                    "spark-acipc.js": "text/javascript",
                    "spark-apc.js": "text/javascript",
                    "spark-aci.js": "text/javascript",
                    "target-compatibility.js": "text/javascript",
                    "tranche10-support.js": "text/javascript",
                    "tranche10-regressions.js": "text/javascript",
                    "tranche10-examples.js": "text/javascript",
                    "tranche10-verification.js": "text/javascript",
                    "tranche10-families.js": "text/javascript",
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

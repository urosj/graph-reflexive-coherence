#!/usr/bin/env python3
"""Check A construction/dynamics claim boundaries without granting lifecycle credit."""

import argparse
import ast
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from fractions import Fraction
import io
import decimal
import importlib.metadata
import platform
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import tempfile
import unittest
from unittest.mock import patch

import phase9_implementation_policy as p
import verify_p951_initialization as prior
import verify_p948b_review as c_review

ROOT = p.ROOT
SCRIPT = p.HERE + "verify_p954_claims.py"
RECORD = p.PHASE + "tranche-5/P9-5.4-ExecutionRecord.json"
REVIEW = p.PHASE + "tranche-5/P9-5.4-Review.md"
AUDIT = p.PHASE + "tranche-5/P9-5.4-AuditFollowup.json"
PREDECESSOR = p.PHASE + "tranche-5/P9-5.3-AuditFollowup.json"
SUBJECT = "5a3e674"
PAPER = p.INV + "drafts/2026-09-GRC-V4.md"
CONTRACTS = (
    "D10.2-EC-PARENT-L-A-INITIALIZER-GRC",
    "D10.2-EC-PARENT-L-A-INITIALIZER-GRC9V3",
    "D10.2-EC-PARENT-A-RETAINED-WRITER",
    "D10.2-EC-PARENT-A-WRITER-TARGET",
    "D10.2-EC-PARENT-L-ATOMICITY",
    "D10.2-EC-PARENT-L-SNAPSHOT-RESET",
    "D10.2-EC-PARENT-SPEC-CLAIM-CEILINGS",
)
# These are implementation-review dispositions, not new forensic claim nodes,
# scientific laws, a runtime classifier or a replacement for source authority.
CLAIMS = {
    "initialization_values": {
        "status": "verified_bounded",
        "basis": "P9-5.1: rebuild target differentials and positive current/reset W from explicit target resource/reference-flux operands.",
        "ceiling": "Supplied flux value/role and positive authority do not authenticate its origin, current regularity, lifecycle admission or formation.",
    },
    "retained_authority_and_writer": {
        "status": "verified_bounded",
        "basis": "P9-5.2: direct W-dependent current, typed Read-Back and one provisional final-C log writer; incoming W supplies the consumed stages.",
        "ceiling": "A legal write or causal W sensitivity alone is not attributable native formation, post-input retention, native release or a live commit.",
    },
    "os_numerical_step": {
        "status": "verified_bounded",
        "basis": "P9-5.3: one predictor/corrector, exact split admission, continuity/write and both post-writer current admissions, with provisional outputs.",
        "ceiling": "Whole live-publication rollback, receipts, snapshot/reset and profile G2 remain separate obligations.",
    },
    "initializer_reference_current_origin": {
        "status": "pending",
        "requires": "Bind an admitted reference-current source to the actual target graph/profile/context/resource stage for current and reset; exclude discarded-history dependence; reject a forged role, omitted flux or fabricated zero seed.",
        "owner": "A target-initialization integration in P9-7.2a/P9-7.2b-A_OS; not discharged by a local value constructor or ordinary retained-state step.",
    },
    "whole_target_lifecycle": {
        "status": "pending",
        "requires": "Readmit current and reset separately; validate current/geometry/domain, charge and serializer; record direction-specific loss; publish graph/state/reset/ledger atomically or preserve the entire prestate on failure.",
        "owner": "A_OS children of P9-7.1 through P9-7.6, including reset-only and both post-writer singularity witnesses.",
    },
    "source_history_preservation": {
        "status": "excluded_by_history_free_policy",
        "requires": "A separately admitted history-transport map and direction-specific evidence would be needed for a preserving crossing. Equal numeric W, stable edge IDs or reset arrays cannot supply provenance.",
        "owner": "P9-7.2a/P9-7.2b/P9-7.3-A_OS; history-free crossings must report loss/no fabrication, including reset.",
    },
    "native_formation": {
        "status": "pending",
        "requires": "Attributable ordinary-writer activity that leaves a declared neutral/instantaneous baseline under the complete profile's formation contract; initialized nonneutral values or a nonzero write alone do not suffice.",
        "owner": "Separate profile-scoped scientific evidence; P9-5.4 does not select a formation experiment or criterion.",
    },
    "post_input_retention": {
        "status": "pending",
        "requires": "Qualifying formed content remains causally available after the forming driver is absent; all maintaining inputs/state must be declared. Persistence under continued forcing or a slow rate alone is insufficient.",
        "owner": "Separate profile-scoped scientific evidence under paper section 5.2.",
    },
    "native_release": {
        "status": "pending",
        "requires": "Native bounded attributable return/removal under the declared writer with accounting and lifecycle provenance; reset, history drop, or neutrality from a moving instantaneous reference is insufficient.",
        "owner": "Separate profile-scoped scientific evidence under paper sections 5.2 and 5.5; administrative loss remains a lifecycle operation.",
    },
    "structural_formation_or_branch": {
        "status": "pending",
        "requires": "Declared constrained criticality/domain and branch evidence; retained formation, initialized nonneutrality, a single snapshot or a nearby runtime trajectory cannot establish it.",
        "owner": "Separate analysis evidence under paper section 13.1.",
    },
    "A_OS_conformance": {
        "status": "pending",
        "requires": "Applicable profile-specific lifecycle and complete fixture product, followed by explicit P9-7.7-A_OS/G2 acceptance. Accepted C_OS singleton evidence cannot be transferred to A.",
        "owner": "P9-7.7-A_OS and P9-G2[A_OS]; G3 remains a separate entry.",
    },
    "exact_GRC9V3_initialization": {
        "status": "excluded_from_generic_initializer",
        "requires": "A deliberately selected exact GRC9V3 specialization binding and its independent compatibility evidence; generic WLS construction or numerical agreement is insufficient.",
        "owner": "Specialization/compatibility owners after their required entries, not P9-5.4.",
    },
}
TESTS = (
    [
        "tests.models.test_grc_v4_candidate_a.CandidateAInitializationTests." + name
        for name in (
            "test_current_and_reset_rebuild_separately",
            "test_reset_only_failure_does_not_change_current_or_reference",
            "test_missing_reference_current_is_not_a_zero_seed",
            "test_same_value_initialization_does_not_claim_formation_or_history",
            "test_roundtrip_rebuilds_and_rejects_cached_outputs_or_claim_promotions",
            "test_inputs_outputs_detach_and_no_runtime_support_is_advertised",
        )
    ]
    + [
        "tests.models.test_grc_v4_candidate_a.CandidateACurrentWriterTests." + name
        for name in (
            "test_explicit_gate_and_structural_gain_controls_preserve_direct_history",
            "test_writer_roundtrip_recomputes_outputs_and_rejects_claim_promotions",
        )
    ]
    + [
        "tests.models.test_grc_v4_realizations.CandidateAOSIntegrationTests." + name
        for name in (
            "test_positive_writer_singularity_rejects_after_successful_current",
            "test_reference_restart_can_fail_after_consumed_geometry_admission",
        )
    ]
)


class ClaimBoundaryTests(unittest.TestCase):
    def test_positive_initialization_can_leave_only_reset_current_singular(self):
        from pygrc.models.grc_v4_candidate_a import (
            CandidateAInitialization,
            CandidateACurrent,
            CandidateAStageError,
        )
        from pygrc.models.grc_v4_geometry import VertexScalar, PhysicalFlux
        from pygrc.models.grc_v4_step import (
            ProvisionalCandidateAOSStep,
            ResourceBoundaryError,
        )
        from tests.models.test_grc_v4_candidate_a import current_fixture

        inputs, backend = current_fixture(
            C=(0.0, 0.0),
            W=(1.0,),
            dt=0.0,
            gamma=-2 * math.log(2),
            chi_A=1.0,
            zeta_A=3.0,
        )
        ref = inputs.geometry.reference
        pair = CandidateAInitialization.construct(
            ref,
            backend,
            current_C=VertexScalar(ref.graph, (0.0, 0.0)),
            current_reference_current=PhysicalFlux(ref.graph, (0.0,)),
            reset_C=VertexScalar(ref.graph, (0.0, 0.0)),
            reset_reference_current=PhysicalFlux(ref.graph, (1.0,)),
        )
        # The exponent contribution is -gamma * J_ref**2 / 2; J_ref=1 gives W_reset=2.
        self.assertEqual(pair.current.authority.state.W_A, (1.0,))
        self.assertEqual(pair.reset.authority.state.W_A, (2.0,))
        before = pair.to_payload()
        target = replace(
            inputs,
            current=pair.current.authority.state,
            reset=pair.reset.authority.state,
        )
        self.assertEqual(CandidateACurrent(target, backend).current.values, (0.0,))
        # At C=0 the current's instantaneous reference is 1. Reset has
        # q=(2-1)/(2+1)=1/3 and 1-zeta*chi*q=0, despite positive mobility.
        self.assertEqual(1 - 3 * Fraction(2 - 1, 2 + 1), 0)
        with self.assertRaises(ResourceBoundaryError) as caught:
            ProvisionalCandidateAOSStep(target, backend)
        self.assertEqual(caught.exception.stage, "pre_read_reconstruction")
        self.assertIsInstance(caught.exception.__cause__, CandidateAStageError)
        self.assertEqual(caught.exception.__cause__.disposition, "singular")
        self.assertEqual(pair.to_payload(), before)
        self.assertFalse(before["lifecycle_committed"])
        # These explicit flux operands have no authenticated target-source
        # certificate. This is a partial-constructor counterexample, not a
        # claimed lawful completed migration or proof of live-owner rollback.

    def test_zero_current_writer_and_initializer_can_return_identical_values(self):
        from pygrc.models.grc_v4_candidate_a import (
            CandidateAInitializationStage,
            CandidateAInitialization,
        )
        from pygrc.models.grc_v4_geometry import VertexScalar, PhysicalFlux
        from pygrc.models.grc_v4_step import ProvisionalCandidateAOSStep
        from tests.models.test_grc_v4_candidate_a import current_fixture

        inputs, backend = current_fixture(
            C=(0.0, 0.0),
            W=(4.0,),
            dt=math.log(2),
            tau_A=1.0,
            gamma=-2 * math.log(2),
            chi_A=0.0,
            zeta_A=1.0,
        )
        step = ProvisionalCandidateAOSStep(inputs, backend)
        self.assertEqual(step.os_pass.corrector.current.values, (0.0,))
        self.assertEqual(step.writer.W_drv_A, (1.0,))
        # Independent multiplicative half-interpolation: sqrt(4*1)=2.
        self.assertEqual(step.next_inputs.current.W_A, (2.0,))
        self.assertEqual(step.next_inputs.current.C, inputs.current.C)
        self.assertEqual(step.next_inputs.reset, inputs.reset)
        ref = inputs.geometry.reference
        plus = CandidateAInitializationStage(
            ref,
            backend,
            VertexScalar(ref.graph, (0.0, 0.0)),
            PhysicalFlux(ref.graph, (1.0,)),
        )
        minus = CandidateAInitializationStage(
            ref,
            backend,
            VertexScalar(ref.graph, (0.0, 0.0)),
            PhysicalFlux(ref.graph, (-1.0,)),
        )
        self.assertEqual(plus.authority.state, step.next_inputs.current)
        self.assertEqual(plus.authority.state, minus.authority.state)
        self.assertNotEqual(plus.identity, minus.identity)
        pair = CandidateAInitialization(plus, minus).to_payload()
        self.assertFalse(pair["source_history_preserved"])
        self.assertFalse(pair["native_formation_claimed"])
        self.assertFalse(pair["lifecycle_committed"])
        # Same graph/profile/C/W, three input histories. Equal values neither
        # authenticate provenance nor turn an initialization into formation.
        # Zero present current and read-off also did not freeze the writer.

    def test_neutral_contrast_from_reference_motion_is_not_a_retained_write(self):
        from pygrc.models.grc_v4_candidate_a import CandidateACurrent
        from tests.models.test_grc_v4_candidate_a import current_fixture

        inputs, backend = current_fixture(
            C=(1.0, 1.0), W=(2.0,), gamma=-2 * math.log(2)
        )
        original = CandidateACurrent(inputs, backend)
        changed = CandidateACurrent(
            replace(
                inputs, current=replace(inputs.current, C=(2.0, 1.0)), Q_target=3.0
            ),
            backend,
        )
        self.assertEqual(original.W_hat_A, (1.0,))
        self.assertEqual(changed.W_hat_A, (2.0,))
        self.assertEqual(original.contrast_exact, (Fraction(1, 3),))
        self.assertEqual(changed.contrast_exact, (Fraction(),))
        self.assertEqual(original.authority.state.W_A, changed.authority.state.W_A)
        # This compares declared fixed-stage states with different C/charge;
        # no transition or release experiment is claimed between them.


def suite():
    result = unittest.defaultTestLoader.loadTestsFromNames(TESTS)
    result.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(ClaimBoundaryTests)
    )
    return result


def source_queries():
    sys.path.insert(0, str(ROOT / p.SIDE / "tool/src"))
    from grcv4_explorer.forensic import load_forensic_context, contract_provenance

    context = load_forensic_context(ROOT, ROOT / p.SIDE)
    traces = [contract_provenance(context, key) for key in CONTRACTS]
    result = []
    for trace in traces:
        row = trace["rows"][0]
        p.require(
            row["payload"]["support_disposition"] == "indeterminate_requires_review",
            "source support changed; scientific review required",
        )
        result.append(
            {
                "contract_id": trace["query"]["contract_id"],
                "trace_digest": trace["trace_digest"],
                "source_ref": row["source_ref"],
                "normative_contract": row["payload"]["contract"]["attributes"][
                    "normative_equation_or_contract"
                ],
                "support_disposition": row["payload"]["support_disposition"],
            }
        )
    return {
        "source_bundle_digest": context.source_bundle_digest,
        "graph_digest": context.graph_digest,
        "contracts": result,
    }


def sources():
    return {
        **prior.source_bindings(),
        **{
            name: p.sha((ROOT / name).read_bytes())
            for name in (
                SCRIPT,
                PAPER,
                "specs/grc-v4-spec.md",
                p.PHASE + "tranche-1/P9-1.4-SupportAndDependencies.json",
            )
        },
    }


def run_tests():
    tests = suite()
    ids = [test.id() for test in prior.leaves(tests)]
    p.require(len(ids) == len(set(ids)) == 13, "changed claim-pressure roster")
    before = {
        path.relative_to(ROOT).as_posix(): p.sha(path.read_bytes())
        for folder in ("src", "tests")
        for path in (ROOT / folder).rglob("*.py")
    }
    before.update(sources())
    output = io.StringIO()
    start = time.monotonic()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(tests)
    print(output.getvalue(), end="")
    p.require(
        result.wasSuccessful()
        and result.testsRun == 13
        and not result.skipped
        and not result.expectedFailures,
        "claim pressure failed",
    )
    bindings = sources()
    p.require(
        all(before.get(k) == v for k, v in bindings.items()), "execution source drift"
    )
    return {
        "tests_run": result.testsRun,
        "failures": 0,
        "errors": 0,
        "skips": 0,
        "executed_ids": ids,
        "elapsed_seconds": round(time.monotonic() - start, 3),
    }, bindings


def capture():
    p.require(not (ROOT / RECORD).exists(), "preserve retained execution")
    p.accepted_a_os(ROOT)
    queries = source_queries()
    result, bindings = run_tests()
    record = {
        "schema": "phase9_leaf_execution_record_v1",
        "iteration_id": "P9-5.4",
        "status": "implemented_verified_pending_independent_audit_and_user_acceptance",
        "release_id": p.ABUNDANCE_RELEASE_ID,
        "source_git_base": p.git(ROOT, "rev-parse", "HEAD").decode().strip(),
        "authority": "User accepted and committed P9-5.3, then explicitly requested P9-5.4.",
        "accepted_predecessor": {
            "commit": SUBJECT,
            "path": PREDECESSOR,
            "record_digest": p.read(ROOT / PREDECESSOR)["record_digest"],
        },
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "command": [".venv/bin/python", SCRIPT, "--capture"],
        "reconstruction_command": [".venv/bin/python", SCRIPT, "--test"],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "libmpdec": decimal.__libmpdec_version__,
            "dependencies": {
                name: importlib.metadata.version(name)
                for name in ("numpy", "jsonschema", "rfc8785")
            },
        },
        "environment_scope": "Observed execution environment; dependency lock and all loaded scientific modules are bound below.",
        "source_bindings": bindings,
        "runtime_result": result,
        "source_review": queries,
        "claim_separation": CLAIMS,
        "claim_ceiling": "Construction, ordinary retained dynamics and claim separation are bounded numerical/review work. No authenticated initializer reference origin, live A lifecycle, formed-state/retention/release/branch evidence, exact GRC9V3 compatibility, A_OS G2 or G3 is granted.",
        "accepted_generic_runtime_support": [],
        "admitted_specialization_support_sets": [],
        "G2_accepted": False,
        "G3_accepted": False,
        "reconstruction": "Use the Git checkout matching these bindings, provision root .venv from uv.lock, and run reconstruction_command. Source authority and prior numerical executions remain at their Git subjects; no source archive or external input is needed.",
    }
    record["record_digest"] = p.digest_record(record)
    (ROOT / RECORD).write_text(json.dumps(record, indent=2) + "\n")
    print("P954_CLAIM_CAPTURE_PASS tests=" + str(result["tests_run"]))


def audit_source_projection(record):
    """Recover the audited documents; comments do not require a numerical rerun."""
    followup = p.read(ROOT / AUDIT)
    p.require(
        followup["record_digest"] == p.digest_record(followup)
        and followup["original_execution_sha256"]
        == p.sha((ROOT / RECORD).read_bytes()),
        "changed audit follow-up or original execution",
    )
    for name, digest in followup["audit_inputs"].items():
        p.require(
            p.sha(p.safe_path(ROOT, name).read_bytes()) == digest,
            "changed independent audit input: " + name,
        )
    bindings = followup["source_delta"]["bindings"]
    p.require(set(bindings) == {SCRIPT, REVIEW}, "unexpected audit correction scope")
    with tempfile.TemporaryDirectory(prefix="p954-audited-source-") as directory:
        target = Path(directory)
        for name, item in bindings.items():
            current = (ROOT / name).read_bytes()
            p.require(
                p.sha(current) == item["corrected_sha256"],
                "changed audit correction: " + name,
            )
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(current)
        result = subprocess.run(
            ["git", "apply", "--reverse", "-"],
            cwd=target,
            input=followup["source_delta"]["patch"],
            text=True,
            capture_output=True,
        )
        p.require(
            result.returncode == 0,
            "audit source delta does not reconstruct: " + result.stderr,
        )
        for name, item in bindings.items():
            p.require(
                p.sha((target / name).read_bytes()) == item["original_sha256"],
                "different audited source: " + name,
            )
        p.require(
            bindings[SCRIPT]["original_sha256"] == record["source_bindings"][SCRIPT],
            "different audited verifier",
        )
        original, current = (
            ast.parse((target / SCRIPT).read_bytes()),
            ast.parse((ROOT / SCRIPT).read_bytes()),
        )
        for name in (
            "ClaimBoundaryTests",
            "suite",
            "source_queries",
            "sources",
            "run_tests",
            "capture",
        ):

            def definition(tree):
                return next(
                    node
                    for node in tree.body
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef))
                    and node.name == name
                )

            p.require(
                ast.dump(definition(original)) == ast.dump(definition(current)),
                "audit correction changed captured scientific body: " + name,
            )
    return bindings[SCRIPT]["corrected_sha256"]


def audit_pressure():
    """Small fresh runtime checks against the supplied independent equations."""
    from pygrc.models.grc_v4_candidate_a import (
        CandidateAInitializationStage,
        CandidateACurrent,
    )
    from pygrc.models.grc_v4_geometry import VertexScalar, PhysicalFlux
    from tests.models.test_grc_v4_candidate_a import current_fixture

    external = p.read(ROOT / (p.PHASE + "tranche-5/P9-5.4-AuditChecks.json"))
    inputs, backend = current_fixture(C=(0.0, 0.0), W=(2.0,), gamma=-2 * math.log(2))
    ref = inputs.geometry.reference
    currents = []
    p.require(
        [row["J"] for row in external["squared_vs_absolute_current_probe"]]
        == [0, 1, -1, 0.5, -0.5, 2, -2],
        "changed audit current roster",
    )
    for row in external["squared_vs_absolute_current_probe"]:
        j = row["J"]
        actual = CandidateAInitializationStage(
            ref,
            backend,
            VertexScalar(ref.graph, (0.0, 0.0)),
            PhysicalFlux(ref.graph, (j,)),
        ).authority.state.W_A[0]
        p.require(
            abs(actual - row["squared_law"]) <= math.ulp(row["squared_law"]),
            "non-unit squared-current law differs",
        )
        if abs(j) not in (0, 1):
            p.require(
                abs(actual - row["absolute_value_substitution"])
                > 100 * math.ulp(actual),
                "absolute-value substitution survived",
            )
        currents.append({"J": j, "W_A": actual})
    inputs, backend = current_fixture(C=(1.5, 1.5), W=(2.0,), gamma=-2 * math.log(2))
    original = CandidateACurrent(inputs, backend)
    changed = CandidateACurrent(
        replace(inputs, current=replace(inputs.current, C=(2.0, 1.0))), backend
    )
    p.require(
        sum(inputs.current.C) == sum(changed.inputs.current.C) == inputs.Q_target == 3,
        "matched-charge comparison drift",
    )
    p.require(
        original.W_hat_A == (1.0,)
        and changed.W_hat_A == (2.0,)
        and original.contrast_exact == (Fraction(1, 3),)
        and changed.contrast_exact == (Fraction(),)
        and original.authority.state.W_A == changed.authority.state.W_A == (2.0,),
        "matched-charge fixed-state equations differ",
    )
    return {
        "status": "passed",
        "current_cases": currents,
        "same_charge_comparison": {
            "C": [[1.5, 1.5], [2.0, 1.0]],
            "Q": 3.0,
            "W_A": 2.0,
            "W_hat": [1.0, 2.0],
            "q": ["1/3", "0"],
            "scope": "Two supplied fixed-stage states; no transition, formation or native release evidence.",
        },
    }


def check():
    record = p.read(ROOT / RECORD)
    p.require(
        record["record_digest"] == p.digest_record(record), "changed execution record"
    )
    p.require(record["claim_separation"] == CLAIMS, "changed reviewed claim separation")
    p.require(
        record["source_review"] == source_queries(), "changed source contract review"
    )
    corrected_script = audit_source_projection(record)
    for name, digest in record["source_bindings"].items():
        if name == SCRIPT:
            digest = corrected_script
        p.require(
            p.sha(p.safe_path(ROOT, name).read_bytes()) == digest,
            "changed reviewed source: " + name,
        )
    p.require(
        [test.id() for test in prior.leaves(suite())]
        == record["runtime_result"]["executed_ids"],
        "changed test roster",
    )
    # Every scientific byte captured in accepted P9-5.3 remains unchanged.
    predecessor = p.read(ROOT / PREDECESSOR)
    p.require(
        (ROOT / PREDECESSOR).read_bytes()
        == p.git(ROOT, "show", SUBJECT + ":" + PREDECESSOR),
        "changed accepted predecessor",
    )
    for name, digest in predecessor["source_bindings"].items():
        p.require(
            p.sha((ROOT / name).read_bytes()) == digest,
            "changed accepted scientific source: " + name,
        )
    ready, _ = p.leaf_permissions(ROOT)
    p.require(
        len(ready) == 34
        and "P9-5.4" in ready
        and "P9-7.1-A_OS" not in ready
        and "P9-G2[A_OS]" not in ready,
        "claim completion promoted lifecycle permission",
    )
    controls = []
    with patch.object(
        p, "accepted_a_os", side_effect=ValueError("missing P9-5.3 acceptance")
    ):
        try:
            p.leaf_permissions(ROOT)
        except ValueError as exc:
            p.require(
                str(exc) == "missing P9-5.3 acceptance", "wrong dependency rejection"
            )
        else:
            raise ValueError("ignored accepted numerical dependency")
    controls.append("missing_accepted_P9_5_3")
    original_read = p.read
    work = p.read(ROOT / p.WORK)
    for label, path, leaf in (
        ("future_A_lifecycle", "src/pygrc/models/grc_v4_lifecycle.py", "P9-7.1-A_OS"),
        (
            "claims_leaf_cannot_own_candidate_numerics",
            "src/pygrc/models/grc_v4_candidate_a.py",
            "P9-5.4",
        ),
    ):
        changed = deepcopy(work)
        next(row for row in changed["entries"] if row["path"] == path)[
            "iteration_id"
        ] = leaf
        changed["record_digest"] = p.digest_record(changed)
        with patch.object(
            p,
            "read",
            side_effect=lambda path: (
                changed if Path(path) == ROOT / p.WORK else original_read(path)
            ),
        ):
            try:
                p.work_entries(ROOT, p.acceptance(ROOT))
            except ValueError as exc:
                p.require(
                    "entry dependencies" in str(exc)
                    or "different owning leaf" in str(exc)
                    or (
                        label == "future_A_lifecycle"
                        and str(exc) == "unregistered work iteration"
                    ),
                    "wrong claim-owner rejection",
                )
            else:
                raise ValueError("claim leaf granted runtime authority")
        controls.append(label)
    reuse = c_review.capture_reuse()
    boundary = p.current_boundary(ROOT)
    sys.path.insert(0, str(ROOT / p.SCRIPTS))
    from test_phase9_g1_surfaces import status_only_check, acceptance_status_check

    status_only_check(ROOT)
    acceptance_status_check(ROOT)
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / p.SCRIPTS / "run_phase9_notebook.py"),
            "--status-only",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    p.require(result.returncode == 0, result.stdout + result.stderr)
    p.require(p.current_boundary(ROOT) == boundary, "publication changed during check")
    return {
        "status": "passed",
        "iteration_id": "P9-5.4",
        "reused_tests": 13,
        "preserved_predecessor_source_bindings": len(predecessor["source_bindings"]),
        "entry_controls": controls,
        "reviewed_claim_boundaries": len(CLAIMS),
        "C_capture_original_subject": reuse["original_subject"],
        "API_notebook_browser_status": "passed",
        "scientific_tests_rerun": 0,
        "A_OS_G2_accepted": False,
        "G3_accepted": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--capture", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--test", action="store_true")
    group.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    if args.capture:
        capture()
    elif args.check:
        print(json.dumps(check()))
    elif args.audit:
        print(json.dumps(audit_pressure()))
    else:
        run_tests()

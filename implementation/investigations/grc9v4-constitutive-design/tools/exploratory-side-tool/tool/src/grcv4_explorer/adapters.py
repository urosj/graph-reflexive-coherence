"""Schema-specific, read-only adapters for the admitted D0-D10.2 bundle."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from .canonical import digest, file_sha256, load_json_object, record_digest
from .errors import SourceAdmissionError


SPECIALIZED_ADAPTERS = {
    "D10NormativeClaimTopology.json": "d10_claim_topology_v2",
    "D10DebtClaimTransformationLedger.json": "d10_debt_claim_ledger_v2",
    "D10SpecificationAuthorizationProfile.json": "d10_authorization_profile_v2",
    "D10_2FullSubstrateProvenanceAndPromotionAudit.json": "d10_2_provenance_v1",
    "D9CompleteStepAndLifecycleContract.json": "d9_complete_step_v1",
    "D9ProfileStateLifecycleRegistry.json": "d9_profile_registry_v1",
    "D9LifecycleCoverageMatrix.json": "d9_lifecycle_matrix_v1",
    "D9ResidualDebtLedger.json": "d9_residual_debt_v1",
}

ADMITTED_SCHEMAS = {
    "D0TargetInheritanceAndClaimCeiling.json": "grc9v4_constitutive_design_decision_v1",
    "D1RetainedRepresentationOntologyAndCandidateAdmission.json": "1.0",
    "D2FormationRetentionReleaseAndWriteInterface.json": "1.0",
    "D3ContinuationRequirementsAndStructuralDomain.json": "1.0",
    "D4GeometryMobilityAndTopologyOwnership.json": "grc9v4-constitutive-design-decision-v1",
    "D5DirectionalReadBack.json": "grc9v4-constitutive-design-decision-v1",
    "D6TotalCurrentClosure.json": "grc9v4_constitutive_decision_v1",
    "D7ClosedWriteReadLoop.json": "grc9v4_constitutive_decision_v1",
    "D4v2CandidateGeometryAndCarrierCompletion.json": "grc9v4_constitutive_decision_v1",
    "D5v2DirectionalReadBackCompletion.json": "grc9v4_constitutive_decision_v1",
    "D6v2UpdatedTotalCurrentClosure.json": "grc9v4-constitutive-design-decision-v1",
    "D7v2CandidateTransitionComparativeAdmission.json": "1.0",
    "D7GGlobalMetricAndStructuralCultivationClosure.json": "1.0",
    "D7Gv2GeometryParametricClosureAndFinalization.json": "GRC9V4-CD-D7G-v2.5",
    "D7GPostv2GraphHodgeTypeCorrection.json": "GRC9V4-CD-CORRECTION-v1.0",
    "D8ABranchAppropriateStructuralTargetExtraction.json": "GRC9V4-CD-D8A-v1.0",
    "GeometryTemporalRealizationSuccessorCoupledImplicit.json": "grc9v4_geometry_temporal_realization_successor_coupled_implicit_v1",
    "D8BCoupledArchitectureLocalContinuationAnalysis.json": "grc9v4_d8b_coupled_architecture_local_continuation_analysis_v1",
    "GeometryTemporalRealizationSuccessorOperatorSplit.json": "grc9v4-constitutive-design-decision-v1",
    "GeometryTemporalRealizationSuccessorReconstructedGeometry.json": "grc9v4-constitutive-design-decision-v1",
    "GeometryTemporalRealizationSuccessorPersistentCarrier.json": "grc9v4_geometry_temporal_realization_successor_persistent_carrier_v1",
    "GeometryTemporalRealizationComparativeSynthesis.json": "grc9v4_geometry_temporal_realization_comparative_synthesis_v1",
    "GeometryTemporalRealizationHybridCoupledPersistentCarrier.json": "grc9v4_geometry_temporal_realization_hybrid_coupled_persistent_carrier_v1",
    "D9CompleteStepAndLifecycleContract.json": "grc9v4_constitutive_design_D9_complete_step_and_lifecycle_v1",
    "D9ProfileStateLifecycleRegistry.json": "grc9v4_d9_profile_state_lifecycle_registry_v1",
    "D9LifecycleCoverageMatrix.json": "grc9v4_d9_lifecycle_coverage_matrix_v1",
    "D9ResidualDebtLedger.json": "grc9v4_d9_residual_debt_ledger_v1",
    "D10DesignSynthesisAndSpecWritingDecision.json": "grc9v4_constitutive_design_d10_v2",
    "D10NormativeClaimTopology.json": "grc9v4_d10_claim_topology_v2",
    "D10DebtClaimTransformationLedger.json": "grc9v4_d10_debt_claim_transformation_v2",
    "D10SpecificationAuthorizationProfile.json": "grc9v4_d10_specification_authorization_profile_v2",
    "D10_1PreliminarySubstrateProvenance.json": "filename_admitted_legacy_schema",
    "D10_2FullSubstrateProvenanceAndPromotionAudit.json": "grc9v4_d10_2_full_provenance_v1",
}


@dataclass(frozen=True)
class SourceDocument:
    """One admitted source plus its normalized adapter projection."""

    filename: str
    path: Path
    data: dict[str, Any]
    admission: dict[str, Any]
    adapter_kind: str
    record_identifier: str
    schema_identifier: str
    digest_field: str
    semantic_index: dict[str, Any]

    @property
    def declared_digest(self) -> str:
        return cast(str, self.data[self.digest_field])

    def manifest_row(self) -> dict[str, Any]:
        return {
            "source_id": self.admission["source_id"],
            "path": self.admission["path"],
            "filename": self.filename,
            "adapter_kind": self.adapter_kind,
            "schema_identifier": self.schema_identifier,
            "record_identifier": self.record_identifier,
            "gate_id": self.data.get("gate_id"),
            "status": self.data["status"],
            "digest_field": self.digest_field,
            "canonical_digest": self.declared_digest,
            "file_sha256": self.admission["file_sha256"],
            "predecessor_record_id": self.data.get("predecessor_record_id"),
            "predecessor_decision_digest": self.data.get("predecessor_decision_digest"),
            "semantic_index": self.semantic_index,
        }


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise SourceAdmissionError(f"missing string field: {label}")
    return value


def _string_ids(rows: Any, key: str, label: str) -> list[str]:
    if not isinstance(rows, list):
        raise SourceAdmissionError(f"missing list field: {label}")
    result: list[str] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise SourceAdmissionError(f"non-object row: {label}/{index}")
        result.append(_require_string(row.get(key), f"{label}/{index}/{key}"))
    return result


def _index(ids: list[str]) -> dict[str, Any]:
    return {
        "count": len(ids),
        "ids": ids,
        "ids_digest": digest(ids),
    }


def _semantic_index(filename: str, data: dict[str, Any]) -> dict[str, Any]:
    if filename == "D10NormativeClaimTopology.json":
        current = _string_ids(data.get("claims"), "claim_id", "claims")
        historical = _string_ids(
            data.get("historical_claim_nodes"),
            "claim_id",
            "historical_claim_nodes",
        )
        edges = data.get("claim_debt_edges")
        if not isinstance(edges, list):
            raise SourceAdmissionError("claim_debt_edges is not a list")
        return {
            "current_claims": _index(current),
            "historical_claims": _index(historical),
            "claim_debt_edge_count": len(edges),
        }
    if filename == "D10DebtClaimTransformationLedger.json":
        debts = _string_ids(
            data.get("debt_transformations"), "debt_id", "debt_transformations"
        )
        obligations = _string_ids(
            data.get("verification_obligations"),
            "obligation_id",
            "verification_obligations",
        )
        return {
            "debt_transformations": _index(debts),
            "verification_obligations": _index(obligations),
        }
    if filename == "D10_2FullSubstrateProvenanceAndPromotionAudit.json":
        objects = _string_ids(
            data.get("normatively_load_bearing_objects"),
            "object_id",
            "normatively_load_bearing_objects",
        )
        contracts = _string_ids(
            data.get("normative_equation_contract_registry"),
            "equation_contract_id",
            "normative_equation_contract_registry",
        )
        return {
            "parent_objects": _index(objects),
            "equation_contracts": _index(contracts),
        }
    if filename == "D9ProfileStateLifecycleRegistry.json":
        profiles = _string_ids(data.get("profiles"), "profile_id", "profiles")
        migrations = _string_ids(
            data.get("migration_classes"), "migration_id", "migration_classes"
        )
        return {
            "profiles": _index(profiles),
            "migration_classes": _index(migrations),
        }
    if filename == "D9LifecycleCoverageMatrix.json":
        profiles = _string_ids(data.get("rows"), "profile_id", "rows")
        columns = data.get("columns")
        if not isinstance(columns, list) or not all(
            isinstance(item, str) for item in columns
        ):
            raise SourceAdmissionError("D9 lifecycle columns are malformed")
        return {
            "profile_rows": _index(profiles),
            "operation_columns": _index(cast(list[str], columns)),
        }
    if filename == "D9ResidualDebtLedger.json":
        obligations = _string_ids(
            data.get("post_spec_verification_obligations"),
            "obligation_id",
            "post_spec_verification_obligations",
        )
        debts = _string_ids(data.get("current_debts"), "debt_id", "current_debts")
        return {
            "current_debts": _index(debts),
            "post_spec_verification_obligations": _index(obligations),
        }
    if filename == "D10SpecificationAuthorizationProfile.json":
        fields = (
            "normative_common_claim_ids",
            "optional_profile_claim_ids",
            "conditional_claim_ids",
            "open_claim_ids",
            "negative_claim_ids",
        )
        result: dict[str, Any] = {}
        for field in fields:
            values = data.get(field)
            if not isinstance(values, list) or not all(
                isinstance(item, str) for item in values
            ):
                raise SourceAdmissionError(f"authorization field malformed: {field}")
            result[field] = _index(cast(list[str], values))
        return result
    return {
        "record_identifier": (
            data.get("record_id") or data.get("artifact_id") or data.get("gate_id")
        ),
        "predecessor_declared": "predecessor_decision_digest" in data,
    }


def adapt_source(repo_root: Path, admission: dict[str, Any]) -> SourceDocument:
    relative = _require_string(admission.get("path"), "admission/path")
    path = repo_root / relative
    if not path.is_file():
        raise SourceAdmissionError(f"admitted source missing: {relative}")
    expected_sha = _require_string(
        admission.get("file_sha256"), "admission/file_sha256"
    )
    if file_sha256(path) != expected_sha:
        raise SourceAdmissionError(f"admitted source SHA mismatch: {relative}")
    data = load_json_object(path)
    expected_status = _require_string(
        admission.get("expected_status"), "admission/expected_status"
    )
    if data.get("status") != expected_status:
        raise SourceAdmissionError(f"admitted source status mismatch: {relative}")
    digest_field = _require_string(
        admission.get("canonical_digest_field"),
        "admission/canonical_digest_field",
    )
    declared = _require_string(data.get(digest_field), f"{relative}/{digest_field}")
    if declared != admission.get("canonical_digest"):
        raise SourceAdmissionError(f"admitted source digest changed: {relative}")
    if declared != record_digest(data, digest_field):
        raise SourceAdmissionError(f"canonical source digest mismatch: {relative}")
    identifier = data.get("record_id") or data.get("artifact_id")
    record_identifier = _require_string(identifier, f"{relative}/record_identifier")
    schema = data.get("schema_version") or data.get("record_type")
    schema_identifier = _require_string(
        schema or "filename_admitted_legacy_schema",
        f"{relative}/schema_identifier",
    )
    admitted_schema = ADMITTED_SCHEMAS.get(path.name)
    if admitted_schema is None or schema_identifier != admitted_schema:
        raise SourceAdmissionError(f"source schema is not admitted: {relative}")
    return SourceDocument(
        filename=path.name,
        path=path,
        data=data,
        admission=admission,
        adapter_kind=SPECIALIZED_ADAPTERS.get(
            path.name, "accepted_decision_lineage_v1"
        ),
        record_identifier=record_identifier,
        schema_identifier=schema_identifier,
        digest_field=digest_field,
        semantic_index=_semantic_index(path.name, data),
    )

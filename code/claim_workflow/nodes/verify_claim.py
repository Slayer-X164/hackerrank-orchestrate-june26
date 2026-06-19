"""Verify Claim node.

This node is where the core decision logic will live: comparing the parsed
claim against the image findings and evidence sufficiency result. The current
version is a structured placeholder.
"""

from __future__ import annotations

from ..state import ClaimWorkflowState, VerificationDecision


def verify_claim_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Attach a deterministic verification decision to the shared state."""

    parsed_claim = state.get("parsed_claim")
    evidence = state.get("evidence_assessment")
    analyses = state.get("image_analyses", [])
    primary_analysis = next((analysis for analysis in analyses if analysis.supports_claim), None)

    issue_type = (
        primary_analysis.visible_issue_type
        if primary_analysis and primary_analysis.visible_issue_type
        else parsed_claim.claimed_issue
        if parsed_claim and parsed_claim.claimed_issue
        else "unknown"
    )
    object_part = (
        primary_analysis.visible_object_part
        if primary_analysis and primary_analysis.visible_object_part
        else parsed_claim.claimed_object_part
        if parsed_claim and parsed_claim.claimed_object_part
        else "unknown"
    )
    supporting_image_ids = evidence.supporting_image_ids if evidence else []
    evidence_standard_met = evidence.evidence_standard_met if evidence else False
    claim_status = "supported" if evidence_standard_met else "not_enough_information"
    severity = (
        primary_analysis.visible_severity
        if primary_analysis and primary_analysis.visible_severity
        else "unknown"
    )

    state["verification_decision"] = VerificationDecision(
        issue_type=issue_type,
        object_part=object_part,
        claim_status=claim_status,
        claim_status_justification=(
            "Deterministic mock workflow found at least one supporting image."
            if evidence_standard_met
            else "Deterministic mock workflow could not confirm the claim from the available images."
        ),
        supporting_image_ids=supporting_image_ids,
        severity=severity,
        claim_conflict_score=0.0 if evidence_standard_met else 0.5,
    )
    state["trace"].append(
        "verify_claim: produced deterministic status, issue, part, and severity"
    )
    return state

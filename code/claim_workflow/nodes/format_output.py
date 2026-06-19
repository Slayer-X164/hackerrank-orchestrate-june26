"""Format Output node.

This node converts the workflow's intermediate objects into the final CSV-ready
schema expected by the challenge evaluator.
"""

from __future__ import annotations

from ..state import ClaimWorkflowState


def format_output_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Build a CSV-ready output dictionary from the shared state."""

    claim_record = state["claim_record"]
    evidence = state.get("evidence_assessment")
    risk = state.get("risk_assessment")
    decision = state.get("verification_decision")

    state["formatted_output"] = {
        "user_id": claim_record.user_id,
        "image_paths": ";".join(claim_record.image_paths),
        "user_claim": claim_record.user_claim,
        "claim_object": claim_record.claim_object,
        "evidence_standard_met": (
            str(evidence.evidence_standard_met).lower() if evidence else "false"
        ),
        "evidence_standard_met_reason": (
            evidence.rationale if evidence else "Evidence assessment unavailable."
        ),
        "risk_flags": (
            ";".join(risk.risk_flags) if risk and risk.risk_flags else "none"
        ),
        "issue_type": decision.issue_type if decision else "unknown",
        "object_part": decision.object_part if decision else "unknown",
        "claim_status": (
            decision.claim_status if decision else "not_enough_information"
        ),
        "claim_status_justification": (
            decision.claim_status_justification
            if decision
            else "Claim verification unavailable."
        ),
        "supporting_image_ids": (
            ";".join(decision.supporting_image_ids)
            if decision and decision.supporting_image_ids
            else "none"
        ),
        "valid_image": str(evidence.valid_image).lower() if evidence else "false",
        "severity": decision.severity if decision else "unknown",
    }
    state["trace"].append("format_output: built CSV-ready output payload")
    return state

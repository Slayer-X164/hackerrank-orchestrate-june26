"""Verify Claim node.

This node is where the core decision logic will live: comparing the parsed
claim against the image findings and evidence sufficiency result. The current
version is a structured placeholder.
"""

from __future__ import annotations

from ..state import ClaimWorkflowState, VerificationDecision


def verify_claim_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Attach a placeholder verification decision to the shared state."""

    state["verification_decision"] = VerificationDecision(
        issue_type="unknown",
        object_part="unknown",
        claim_status="not_enough_information",
        claim_status_justification=(
            "Stub verification only. Final claim verification logic has not "
            "been implemented yet."
        ),
        supporting_image_ids=[],
        severity="unknown",
    )
    state["trace"].append("verify_claim: attached placeholder decision")
    return state

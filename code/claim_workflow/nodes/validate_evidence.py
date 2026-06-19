"""Validate Evidence node.

This node compares the image set against the minimum evidence requirements. The
stub currently records a pending assessment so the graph structure is ready
before the evidence policy is fully implemented.
"""

from __future__ import annotations

from ..state import ClaimWorkflowState, EvidenceAssessment


def validate_evidence_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Attach a placeholder evidence assessment to the shared state."""

    state["evidence_assessment"] = EvidenceAssessment(
        evidence_standard_met=False,
        valid_image=False,
        unmet_requirements=["Evidence validation logic not implemented yet."],
        rationale=(
            "Stub evidence assessment only. This node should later enforce the "
            "rules from dataset/evidence_requirements.csv."
        ),
    )
    state["trace"].append(
        "validate_evidence: attached placeholder evidence requirement result"
    )
    return state

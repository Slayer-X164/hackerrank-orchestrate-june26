"""Validate Evidence node.

This node compares the image set against the minimum evidence requirements. The
stub currently records a pending assessment so the graph structure is ready
before the evidence policy is fully implemented.
"""

from __future__ import annotations

from ..state import ClaimWorkflowState, EvidenceAssessment


def validate_evidence_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Attach a deterministic evidence assessment to the shared state."""

    analyses = state.get("image_analyses", [])
    applied_requirement_ids = [
        requirement.requirement_id for requirement in state["evidence_requirements"]
    ]
    supporting_image_ids = [
        analysis.image_id
        for analysis in analyses
        if analysis.supports_claim and analysis.is_usable
    ]
    visible_and_clear = any(
        analysis.claimed_part_visible and analysis.claimed_part_clear
        for analysis in analyses
    )
    evidence_standard_met = bool(supporting_image_ids) and visible_and_clear
    valid_image = any(analysis.is_usable for analysis in analyses)
    failed_requirement_ids = [] if evidence_standard_met else applied_requirement_ids
    unmet_requirements = (
        []
        if evidence_standard_met
        else ["No mock image satisfied the claimed-part visibility requirement."]
    )

    state["evidence_assessment"] = EvidenceAssessment(
        evidence_standard_met_reason=(
            "At least one mock image clearly shows the claimed part."
            if evidence_standard_met
            else "No mock image clearly shows the claimed part."
        ),
        evidence_standard_met=evidence_standard_met,
        valid_image=valid_image,
        unmet_requirements=unmet_requirements,
        applied_requirement_ids=applied_requirement_ids,
        satisfied_requirement_ids=[] if not evidence_standard_met else applied_requirement_ids,
        failed_requirement_ids=failed_requirement_ids,
        supporting_image_ids=supporting_image_ids,
        rationale=(
            "Deterministic mock evidence validation completed using preloaded "
            "requirements and per-image placeholder findings."
        ),
    )
    state["trace"].append(
        "validate_evidence: computed deterministic evidence sufficiency and rule attribution"
    )
    return state

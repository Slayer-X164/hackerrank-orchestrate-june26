"""Verify Claim node.

This node is where the core decision logic will live: comparing the parsed
claim against the image findings and evidence sufficiency result. The current
version is a structured placeholder.
"""

from __future__ import annotations

from ..state import ClaimWorkflowState, VerificationDecision


def verify_claim_node(
    state: ClaimWorkflowState,
) -> ClaimWorkflowState:

    findings = state["aggregated_image_findings"]

    damage_types = [
        issue
        for issue in findings.visible_issue_types
        if issue not in ["none", "unknown"]
    ]

    # evidence quality
    if findings.usable_image_count == 0:
        claim_status = "not_enough_information"

    elif damage_types:
        claim_status = "supported"

    elif findings.visible_issue_types == ["none"]:
        claim_status = "contradicted"

    else:
        claim_status = "not_enough_information"

    issue_type = damage_types[0] if damage_types else "unknown"

    object_part = findings.visible_parts[0] if findings.visible_parts else "unknown"

    if claim_status == "supported":
        justification = f"Visible {issue_type} detected on {object_part}."
    elif claim_status == "contradicted":
        justification = "Claimed area is visible but no damage was detected."
    else:
        justification = "Submitted images do not provide enough evidence."

    confidence = findings.highest_confidence
    if claim_status == "supported":
        conflict_score = 0.0
    elif claim_status == "contradicted":
        conflict_score = 1.0
    else:
        conflict_score = 0.5
        
    state["verification_decision"] = VerificationDecision(
        issue_type=issue_type,
        object_part=object_part,
        claim_status=claim_status,
        claim_status_justification=justification,
        supporting_image_ids=findings.supporting_image_ids,
        severity=("medium" if claim_status == "supported" else "unknown"),
        claim_conflict_score=(conflict_score),
    )

    state["trace"].append(f"verify_claim: status={claim_status}")
    print("\n=== DECISION ===")
    print(state["verification_decision"])
    return state

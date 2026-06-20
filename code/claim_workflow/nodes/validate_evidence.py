from ..state import ClaimWorkflowState, EvidenceAssessment


def validate_evidence_node(
    state: ClaimWorkflowState,
) -> ClaimWorkflowState:

    analyses = state.get("image_analyses", [])

    applied_requirement_ids = [
        requirement.requirement_id
        for requirement in state["evidence_requirements"]
    ]

    valid_image = any(
        analysis.is_usable
        for analysis in analyses
    )

    visible_and_clear = any(
        analysis.claimed_part_visible
        and analysis.claimed_part_clear
        for analysis in analyses
    )

    supporting_image_ids = [
        analysis.image_id
        for analysis in analyses
        if (
            analysis.claimed_part_visible
            and analysis.claimed_part_clear
        )
    ]

    evidence_standard_met = (
        valid_image
        and visible_and_clear
    )

    if evidence_standard_met:
        unmet_requirements = []
        failed_requirement_ids = []

        reason = (
            "At least one image clearly shows the claimed object part."
        )

    else:
        unmet_requirements = [
            "Claimed object part is not clearly visible."
        ]

        failed_requirement_ids = applied_requirement_ids

        reason = (
            "No image clearly shows the claimed object part."
        )

    state["evidence_assessment"] = (
        EvidenceAssessment(
            evidence_standard_met=evidence_standard_met,
            evidence_standard_met_reason=reason,
            valid_image=valid_image,
            unmet_requirements=unmet_requirements,
            applied_requirement_ids=applied_requirement_ids,
            satisfied_requirement_ids=(
                applied_requirement_ids
                if evidence_standard_met
                else []
            ),
            failed_requirement_ids=failed_requirement_ids,
            supporting_image_ids=supporting_image_ids,
            rationale=(
                "Evidence sufficiency was determined using "
                "claimed-part visibility and image clarity."
            ),
        )
    )

    state["trace"].append(
        f"validate_evidence: "
        f"evidence_standard_met={evidence_standard_met}"
    )

    return state
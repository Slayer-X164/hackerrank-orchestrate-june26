from claim_workflow.state import ClaimWorkflowState

def format_output_node(
    state: ClaimWorkflowState,
) -> ClaimWorkflowState:

    claim = state["claim_record"]
    verification = state["verification_decision"]
    evidence = state["evidence_assessment"]
    risk = state["risk_assessment"]

    state["formatted_output"] = {

        "user_id":
            claim.user_id,

        "image_paths":
            ";".join(claim.image_paths),

        "user_claim":
            claim.user_claim,

        "claim_object":
            claim.claim_object,

        "evidence_standard_met":
            str(evidence.evidence_standard_met).lower(),

        "evidence_standard_met_reason":
            evidence.evidence_standard_met_reason,

        "risk_flags":
            ";".join(risk.risk_flags),

        "issue_type":
            verification.issue_type,

        "object_part":
            verification.object_part,

        "claim_status":
            verification.claim_status,

        "claim_status_justification":
            verification.claim_status_justification,

        "supporting_image_ids":
            ";".join(
                verification.supporting_image_ids
            ) or "none",

        "valid_image":
            str(evidence.valid_image).lower(),

        "severity":
            verification.severity,
    }

    return state
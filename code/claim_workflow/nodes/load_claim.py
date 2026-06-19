"""Load Claim node.

This node performs deterministic preprocessing only. It normalizes the raw
claim row into a lightweight parsed structure and prepares the shared state for
downstream multimodal analysis.
"""

from __future__ import annotations

from ..state import ClaimWorkflowState, ParsedClaim


def load_claim_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Prepare the claim payload for downstream nodes.

    This stub intentionally avoids any LLM usage for now. Later, this is the
    right place to add a structured extraction step using `langchain-openrouter`
    with `openrouter/openai/gpt-oss-120b:free`.
    """

    claim_record = state["claim_record"]
    parsed_claim = ParsedClaim(
        claim_summary=claim_record.user_claim,
        claimed_issue=None,
        claimed_object_part=None,
        severity_hint=None,
    )
    state["parsed_claim"] = parsed_claim
    state["trace"].append("load_claim: normalized raw claim into shared state")
    return state

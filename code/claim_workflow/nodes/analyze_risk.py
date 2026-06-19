"""Analyze Risk node.

This node combines user-history signals and image-review signals into final
risk flags. The current stub keeps the interface stable without making policy
decisions yet.
"""

from __future__ import annotations

from typing import cast

from ..state import ClaimWorkflowState, RiskAssessment, RiskFlag


def analyze_risk_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Attach a deterministic risk assessment to the shared state."""

    history_flags: list[str] = []
    if state["user_history"]:
        raw_flags = str(state["user_history"].get("history_flags", "none"))
        if raw_flags != "none":
            history_flags = raw_flags.split(";")

    image_quality_flags = {
        flag
        for analysis in state.get("image_analyses", [])
        for flag in (analysis.quality_flags or [])
    }
    combined_flags = list(dict.fromkeys([*history_flags, *sorted(image_quality_flags)]))
    risk_flags = cast(list[RiskFlag], combined_flags or ["none"])
    state["risk_assessment"] = RiskAssessment(
        risk_flags=risk_flags,
        rationale=(
            "Deterministic mock risk assessment merged history flags with any "
            "image quality flags."
        ),
        risk_justification=(
            "Risk flags were derived from preloaded user history and mock "
            "image-analysis quality signals."
        ),
    )
    state["trace"].append(
        "analyze_risk: merged deterministic history and image-derived risk flags"
    )
    return state

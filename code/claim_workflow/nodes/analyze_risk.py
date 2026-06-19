"""Analyze Risk node.

This node combines user-history signals and image-review signals into final
risk flags. The current stub keeps the interface stable without making policy
decisions yet.
"""

from __future__ import annotations

from typing import cast

from ..state import ClaimWorkflowState, RiskAssessment, RiskFlag


def analyze_risk_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Attach a placeholder risk assessment to the shared state."""

    history_flags: list[str] = []
    if state["user_history"]:
        raw_flags = str(state["user_history"].get("history_flags", "none"))
        if raw_flags != "none":
            history_flags = raw_flags.split(";")

    risk_flags = cast(list[RiskFlag], history_flags or ["none"])
    state["risk_assessment"] = RiskAssessment(
        risk_flags=risk_flags,
        rationale=(
            "Stub risk assessment only. This node should later merge history "
            "signals with image-derived review risks."
        ),
    )
    state["trace"].append("analyze_risk: attached placeholder risk assessment")
    return state

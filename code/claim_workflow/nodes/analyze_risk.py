from typing import cast

from ..state import (
    ClaimWorkflowState,
    RiskAssessment,
    RiskFlag,
)

def analyze_risk_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Attach a deterministic risk assessment to the shared state."""

    history_flags: list[str] = []

    history = state.get("user_history")

    if history:
        raw_flags = history.history_flags

        if raw_flags != "none":
            history_flags = [
                flag.strip()
                for flag in raw_flags.split(";")
                if flag.strip()
            ]

    image_quality_flags = {
        flag
        for analysis in state.get("image_analyses", [])
        for flag in (analysis.quality_flags or [])
    }

    combined_flags = list(
        dict.fromkeys(
            [
                *history_flags,
                *sorted(image_quality_flags),
            ]
        )
    )

    risk_flags = cast(
        list[RiskFlag],
        combined_flags or ["none"],
    )

    state["risk_assessment"] = RiskAssessment(
        risk_flags=risk_flags,
        rationale=(
            "Deterministic mock risk assessment merged history flags "
            "with image quality signals."
        ),
        risk_justification=(
            "Risk flags were derived from user history and "
            "image-analysis findings."
        ),
    )

    state["trace"].append(
        "analyze_risk: merged history and image-derived risk flags"
    )

    return state
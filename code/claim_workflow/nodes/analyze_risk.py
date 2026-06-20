from typing import cast

from ..state import (
    ClaimWorkflowState,
    RiskAssessment,
    RiskFlag,
)

from typing import cast

from ..state import (
    ClaimWorkflowState,
    RiskAssessment,
    RiskFlag,
)


def analyze_risk_node(
    state: ClaimWorkflowState,
) -> ClaimWorkflowState:

    risk_flags: set[str] = set()

    history = state.get("user_history")

    if history:

        if history.history_flags != "none":
            risk_flags.update(
                flag.strip()
                for flag in history.history_flags.split(";")
                if flag.strip()
            )

        if history.last_90_days_claim_count >= 3:
            risk_flags.add("user_history_risk")

        if history.rejected_claim >= 2:
            risk_flags.add("user_history_risk")

    for analysis in state.get("image_analyses", []):

        for flag in analysis.quality_flags or []:

            if flag != "none":
                risk_flags.add(flag)

    final_flags = sorted(risk_flags)

    if not final_flags:
        final_flags = ["none"]

    state["risk_assessment"] = RiskAssessment(
        risk_flags=cast(
            list[RiskFlag],
            final_flags,
        ),
        rationale=(
            "Risk assessment derived from user claim history "
            "and image quality indicators."
        ),
        risk_justification=(
            "Flags reflect historical claim behavior and "
            "image-review findings."
        ),
    )

    state["trace"].append(
        f"analyze_risk: {','.join(final_flags)}"
    )

    return state
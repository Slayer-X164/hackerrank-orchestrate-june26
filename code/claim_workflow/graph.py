"""LangGraph assembly for the claim verification workflow."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from .nodes.analyze_images import analyze_images_node
from .nodes.analyze_risk import analyze_risk_node
from .nodes.format_output import format_output_node
from .nodes.load_claim import load_claim_node
from .nodes.validate_evidence import validate_evidence_node
from .nodes.verify_claim import verify_claim_node
from .state import ClaimWorkflowState


def build_claim_verification_graph() -> Any:
    """Build the claim verification workflow.

    The graph uses one shared state object and a fixed linear sequence that
    matches the requested architecture:

    1. Load Claim
    2. Analyze Images
    3. Validate Evidence
    4. Analyze Risk
    5. Verify Claim
    6. Format Output

    Returns:
        A compiled LangGraph workflow ready to be invoked with a
        `ClaimWorkflowState`.
    """

    graph = StateGraph(ClaimWorkflowState)

    graph.add_node("load_claim", load_claim_node)
    graph.add_node("analyze_images", analyze_images_node)
    graph.add_node("validate_evidence", validate_evidence_node)
    graph.add_node("analyze_risk", analyze_risk_node)
    graph.add_node("verify_claim", verify_claim_node)
    graph.add_node("format_output", format_output_node)

    graph.add_edge(START, "load_claim")
    graph.add_edge("load_claim", "analyze_images")
    graph.add_edge("analyze_images", "validate_evidence")
    graph.add_edge("validate_evidence", "analyze_risk")
    graph.add_edge("analyze_risk", "verify_claim")
    graph.add_edge("verify_claim", "format_output")
    graph.add_edge("format_output", END)

    return graph.compile()

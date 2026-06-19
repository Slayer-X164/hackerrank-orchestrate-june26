from langgraph.graph import StateGraph, START, END

from .state import ClaimWorkflowState
from .nodes.load_claim import load_claim_node
from .nodes.analyze_images import analyze_images_node
from .nodes.validate_evidence import validate_evidence_node
from .nodes.analyze_risk import analyze_risk_node
from .nodes.verify_claim import verify_claim_node
from .nodes.format_output import format_output_node


def build_claim_verification_graph():
    builder = StateGraph(ClaimWorkflowState)

    builder.add_node("load_claim", load_claim_node)
    builder.add_node("analyze_images", analyze_images_node)
    builder.add_node("validate_evidence", validate_evidence_node)
    builder.add_node("analyze_risk", analyze_risk_node)
    builder.add_node("verify_claim", verify_claim_node)
    builder.add_node("format_output", format_output_node)

    builder.add_edge(START, "load_claim")
    builder.add_edge("load_claim", "analyze_images")
    builder.add_edge("analyze_images", "validate_evidence")
    builder.add_edge("validate_evidence", "analyze_risk")
    builder.add_edge("analyze_risk", "verify_claim")
    builder.add_edge("verify_claim", "format_output")
    builder.add_edge("format_output", END)

    return builder.compile()
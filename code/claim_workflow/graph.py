"""LangGraph assembly for the claim verification workflow."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from langgraph.graph import END, START, StateGraph
except ImportError:
    START = "__start__"
    END = "__end__"

    class _CompiledStateGraph:
        """Minimal fallback executor when `langgraph` is unavailable."""

        def __init__(
            self,
            nodes: dict[str, Callable[[Any], Any]],
            edges: dict[str, str],
        ) -> None:
            self._nodes = nodes
            self._edges = edges

        def invoke(self, state: Any) -> Any:
            """Execute the linear graph from START to END."""

            current = self._edges[START]
            while current != END:
                state = self._nodes[current](state)
                current = self._edges[current]
            return state

    class StateGraph:
        """Tiny subset of the LangGraph API used by this project."""

        def __init__(self, _state_type: Any) -> None:
            self._nodes: dict[str, Callable[[Any], Any]] = {}
            self._edges: dict[str, str] = {}

        def add_node(self, name: str, fn: Callable[[Any], Any]) -> None:
            self._nodes[name] = fn

        def add_edge(self, source: str, target: str) -> None:
            self._edges[source] = target

        def compile(self) -> _CompiledStateGraph:
            return _CompiledStateGraph(self._nodes, self._edges)

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

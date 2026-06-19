"""Entry point for the claim verification workflow scaffold.

This file currently exposes the LangGraph workflow builder and shared-state
helpers without running end-to-end prediction logic. It exists so the project
has a stable, documented entry point while the node implementations are still
being filled in.
"""

from claim_workflow import (
    ClaimWorkflowState,
    build_claim_verification_graph,
    create_initial_state,
)

__all__ = [
    "ClaimWorkflowState",
    "build_claim_verification_graph",
    "create_initial_state",
]

"""Analyze Images node.

This node is reserved for per-image visual inspection. The current version is a
stub that builds the expected state shape without performing any model calls.
"""

from __future__ import annotations

from ..state import ClaimWorkflowState, ImageAnalysis


def analyze_images_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Create placeholder per-image analysis entries.

    Later, this node should call the configured vision-capable model through
    `langchain-openrouter` and produce structured findings for each submitted
    image independently.
    """

    analyses = [
        ImageAnalysis(
            image_path=image_path,
            image_id=image_id,
            notes="Stub analysis only; visual model call not implemented yet.",
        )
        for image_path, image_id in zip(
            state["claim_record"].image_paths,
            state["image_ids"],
            strict=True,
        )
    ]
    state["image_analyses"] = analyses
    state["trace"].append(
        "analyze_images: created placeholder per-image analysis records"
    )
    return state

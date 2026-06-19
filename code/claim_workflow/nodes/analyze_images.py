"""Analyze Images node.

This node is reserved for per-image visual inspection. The current version is a
stub that builds the expected state shape without performing any model calls.
"""

from __future__ import annotations

from ..state import ClaimWorkflowState, ImageAnalysis


def _analysis_for_image(
    state: ClaimWorkflowState, image_path: str, image_id: str, index: int
) -> ImageAnalysis:
    claim_record = state["claim_record"]
    parsed_claim = state.get("parsed_claim")
    claimed_issue = parsed_claim.claimed_issue if parsed_claim else None
    claimed_object_part = parsed_claim.claimed_object_part if parsed_claim else None

    is_primary = index == 0
    quality_flags = [] if is_primary else ["blurry_image"]
    provides_context = len(state["image_ids"]) > 1 and not is_primary
    relevance_score = max(0.4, 0.95 - (index * 0.2))

    return ImageAnalysis(
        image_path=image_path,
        image_id=image_id,
        visible_object=claim_record.claim_object,
        visible_object_part=claimed_object_part or "unknown",
        visible_issue_type=claimed_issue or "unknown",
        visible_severity=parsed_claim.severity_hint or "medium" if parsed_claim else "medium",
        quality_flags=quality_flags,
        relevance_flags=[],
        trust_flags=[],
        is_usable=True,
        is_relevant=True,
        claimed_part_visible=is_primary,
        claimed_part_clear=is_primary,
        provides_context=provides_context,
        correct_orientation=True,
        notes=(
            "Deterministic mock image analysis generated without reading image bytes."
        ),
        confidence=relevance_score,
        supports_claim=is_primary,
        contradicts_claim=False,
        relevance_score=relevance_score,
        selection_rationale=(
            "Primary image selected as best evidence in deterministic mock flow."
            if is_primary
            else "Secondary image retained as contextual evidence only."
        ),
    )


def analyze_images_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Create deterministic per-image mock analysis entries."""

    analyses = [
        _analysis_for_image(state, image_path, image_id, index)
        for index, (image_path, image_id) in enumerate(
            zip(state["claim_record"].image_paths, state["image_ids"], strict=True)
        )
    ]
    state["image_analyses"] = analyses
    state["trace"].append(
        "analyze_images: populated deterministic per-image mock findings"
    )
    return state

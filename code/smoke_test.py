"""Smoke test for deterministic claim workflow execution."""

from __future__ import annotations

from pprint import pprint

from claim_workflow.graph import build_claim_verification_graph
from claim_workflow.state import ClaimRecord, EvidenceRequirement, create_initial_state


def main() -> None:
    """Build and execute the graph with a deterministic dummy claim."""

    graph = build_claim_verification_graph()
    state = create_initial_state(
        claim_id="dummy-claim-001",
        repo_root=".",
        dataset_root="./dataset",
        claim_record=ClaimRecord(
            user_id="user_demo",
            image_paths=[
                "images/test/case_demo/img_1.jpg",
                "images/test/case_demo/img_2.jpg",
            ],
            user_claim="Customer reports a crack on the laptop screen.",
            claim_object="laptop",
        ),
        user_history={
            "user_id": "user_demo",
            "history_flags": "manual_review_required",
            "history_summary": "Demo user with prior review-required claims.",
        },
        evidence_requirements=[
            EvidenceRequirement(
                requirement_id="REQ_GENERAL_OBJECT_PART",
                claim_object="all",
                applies_to="general claim review",
                minimum_image_evidence=(
                    "The claimed object and relevant part should be visible clearly enough to inspect."
                ),
            ),
            EvidenceRequirement(
                requirement_id="REQ_LAPTOP_SCREEN_KEYBOARD_TRACKPAD",
                claim_object="laptop",
                applies_to="screen, keyboard, or trackpad",
                minimum_image_evidence=(
                    "The claimed laptop screen area should be visible clearly enough to inspect cracks."
                ),
            ),
        ],
    )
    final_state = graph.invoke(state)
    pprint(final_state)


if __name__ == "__main__":
    main()

"""Run a small subset of claims and generate test_output.csv."""

from __future__ import annotations

import csv
from pathlib import Path

from claim_workflow import (
    build_claim_verification_graph,
    create_initial_state,
)

from data.loaders import (
    load_claims,
    load_user_history,
    load_evidence_requirements,
)


OUTPUT_COLUMNS = [
    "user_id",
    "image_paths",
    "user_claim",
    "claim_object",
    "evidence_standard_met",
    "evidence_standard_met_reason",
    "risk_flags",
    "issue_type",
    "object_part",
    "claim_status",
    "claim_status_justification",
    "supporting_image_ids",
    "valid_image",
    "severity",
]


def main() -> int:

    repo_root = Path(__file__).resolve().parent.parent
    dataset_root = repo_root / "dataset"

    print("Loading dataset...")

    claims = load_claims(str(dataset_root))

    # only test first x claims
    claims = claims[:2]

    history_map = load_user_history(str(dataset_root))
    requirements = load_evidence_requirements(str(dataset_root))

    graph = build_claim_verification_graph()

    rows: list[dict[str, str]] = []

    print(f"Testing {len(claims)} claims")

    for index, claim in enumerate(claims, start=1):

        print(
            f"[{index}/{len(claims)}] Processing "
            f"user={claim.user_id}"
        )

        try:
            state = create_initial_state(
                claim_id=f"test-{index}",
                repo_root=str(repo_root),
                dataset_root=str(dataset_root),
                claim_record=claim,
                user_history=history_map.get(claim.user_id),
                evidence_requirements=requirements,
            )

            result = graph.invoke(state)

            rows.append(
                result["formatted_output"]
            )

        except Exception as exc:
            print(
                f"Failed claim {index}: {exc}"
            )

    output_file = repo_root / "test_output.csv"

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(rows)

    print()
    print("=" * 50)
    print(f"Generated: {output_file}")
    print(f"Rows written: {len(rows)}")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
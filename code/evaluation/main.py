# code/evaluation/main.py

from pathlib import Path

from data.loaders import (
    load_claims,
    load_user_history,
    load_evidence_requirements
)

from claim_workflow.graph import build_claim_verification_graph
from claim_workflow.state import create_initial_state
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)

def evaluate():

    dataset_root = "./dataset"

    claims = load_claims(
        Path(dataset_root) / "sample_claims.csv"
    )

    history_map = load_user_history(
        dataset_root
    )

    requirements = load_evidence_requirements(
        dataset_root
    )

    graph = build_claim_verification_graph()

    total = 0

    correct_status = 0
    correct_issue = 0
    correct_part = 0
    correct_severity = 0

    print("\n===== RUNNING EVALUATION =====\n")

    for idx, claim in enumerate(claims):

        state = create_initial_state(
            claim_id=f"sample-{idx}",
            repo_root=".",
            dataset_root=dataset_root,
            claim_record=claim,
            user_history=history_map.get(
                claim.user_id
            ),
            evidence_requirements=requirements,
        )

        result = graph.invoke(state)

        predicted = result["formatted_output"]

        total += 1

        #
        # Ground-truth labels from sample_claims.csv
        #
        expected_status = claim.claim_status
        expected_issue = claim.issue_type
        expected_part = claim.object_part
        expected_severity = claim.severity

        #
        # Compare predictions
        #
        if (
            predicted["claim_status"]
            == expected_status
        ):
            correct_status += 1

        if (
            predicted["issue_type"]
            == expected_issue
        ):
            correct_issue += 1

        if (
            predicted["object_part"]
            == expected_part
        ):
            correct_part += 1

        if (
            predicted["severity"]
            == expected_severity
        ):
            correct_severity += 1

    print("\n===== RESULTS =====\n")

    status_acc = (
        correct_status / total
        if total
        else 0
    )

    issue_acc = (
        correct_issue / total
        if total
        else 0
    )

    part_acc = (
        correct_part / total
        if total
        else 0
    )

    severity_acc = (
        correct_severity / total
        if total
        else 0
    )

    overall_correct = (
        correct_status
        + correct_issue
        + correct_part
        + correct_severity
    )

    overall_total = total * 4

    overall_acc = (
        overall_correct / overall_total
        if overall_total
        else 0
    )

    print(
        f"Claim Status Accuracy : "
        f"{status_acc:.2%}"
    )

    print(
        f"Issue Type Accuracy   : "
        f"{issue_acc:.2%}"
    )

    print(
        f"Object Part Accuracy  : "
        f"{part_acc:.2%}"
    )

    print(
        f"Severity Accuracy     : "
        f"{severity_acc:.2%}"
    )

    print(
        f"\nOverall Accuracy      : "
        f"{overall_acc:.2%}"
    )


if __name__ == "__main__":
    evaluate()
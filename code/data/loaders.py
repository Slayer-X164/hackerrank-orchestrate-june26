from pathlib import Path
import csv

from claim_workflow.state import ClaimRecord, UserHistory, EvidenceRequirement



def load_claims(dataset_root: str):
    claims_path = Path(dataset_root) / "claims.csv"

    claims: list[ClaimRecord] = []

    with open(claims_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            claims.append(
                ClaimRecord(
                    user_id=row["user_id"],
                    image_paths=[
                      path.strip() for path in row["image_paths"].split(";") if path.strip()
                    ],
                    user_claim=row["user_claim"],
                    claim_object=row["claim_object"],
                )
            )
        return claims


def load_user_history(dataset_root: str) -> dict[str, UserHistory]:
    path = Path(dataset_root) / "user_history.csv"

    history = {}

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            record = UserHistory(
                user_id=row["user_id"],
                past_claim_count=int(row["past_claim_count"]),
                accept_claim=int(row["accept_claim"]),
                manual_review_claim=int(row["manual_review_claim"]),
                rejected_claim=int(row["rejected_claim"]),
                last_90_days_claim_count=int(
                    row["last_90_days_claim_count"]
                ),
                history_flags=row["history_flags"],
                history_summary=row["history_summary"],
            )

            history[record.user_id] = record

    return history

def load_evidence_requirements(dataset_root: str) -> list[EvidenceRequirement]:
  path = Path(dataset_root) / "evidence_requirements.csv"
  requirements = []

  with open(path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
      requirements.append(
                EvidenceRequirement(
                    requirement_id=row["requirement_id"],
                    claim_object=row["claim_object"],
                    applies_to=row["applies_to"],
                    minimum_image_evidence=row[
                        "minimum_image_evidence"
                    ],
                )
            )
  return requirements


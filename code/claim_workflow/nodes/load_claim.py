from __future__ import annotations

from ..state import (
    ClaimWorkflowState,
    IssueType,
    ObjectPart,
    ParsedClaim,
)

ISSUE_KEYWORDS: list[tuple[str, IssueType]] = [
    ("dent", "dent"),
    ("scratch", "scratch"),
    ("crack", "crack"),
    ("shatter", "glass_shatter"),
    ("broken", "broken_part"),
    ("missing", "missing_part"),    
    ("torn", "torn_packaging"),
    ("crushed", "crushed_packaging"),
    ("water", "water_damage"),
    ("liquid", "water_damage"),
    ("spill", "water_damage"),
    ("stain", "stain"),
]

OBJECT_PART_KEYWORDS: list[tuple[str, ObjectPart]] = [
    # car
    ("rear bumper", "rear_bumper"),
    ("front bumper", "front_bumper"),
    ("bumper", "front_bumper"),
    ("windshield", "windshield"),
    ("mirror", "side_mirror"),
    ("headlight", "headlight"),
    ("taillight", "taillight"),
    ("fender", "fender"),
    ("quarter panel", "quarter_panel"),
    ("door", "door"),
    ("hood", "hood"),

    # laptop
    ("screen", "screen"),
    ("keyboard", "keyboard"),
    ("trackpad", "trackpad"),
    ("hinge", "hinge"),
    ("lid", "lid"),
    ("corner", "corner"),
    ("port", "port"),
    ("base", "base"),

    # package
    ("package corner", "package_corner"),
    ("corner of the package", "package_corner"),
    ("package side", "package_side"),
    ("seal", "seal"),
    ("label", "label"),
    ("contents", "contents"),
    ("item", "item"),
    ("box", "box"),
]

SEVERITY_KEYWORDS = [
    ("severe", "high"),
    ("major", "high"),
    ("significant", "high"),
    ("bad", "medium"),
    ("moderate", "medium"),
    ("small", "low"),
    ("minor", "low"),
    ("light", "low"),
]


def _match_issue(text: str) -> IssueType | None:
    for keyword, issue in ISSUE_KEYWORDS:
        if keyword in text:
            return issue
    return None


def _match_object_part(text: str) -> ObjectPart | None:
    for keyword, part in OBJECT_PART_KEYWORDS:
        if keyword in text:
            return part
    return None


def _match_severity_hint(text: str) -> str | None:
    for keyword, severity in SEVERITY_KEYWORDS:
        if keyword in text:
            return severity
    return None


def load_claim_node(
    state: ClaimWorkflowState,
) -> ClaimWorkflowState:

    claim_record = state["claim_record"]

    normalized_claim = (
        claim_record.user_claim
        .lower()
        .strip()
    )

    claimed_issue = _match_issue(
        normalized_claim
    )

    claimed_object_part = _match_object_part(
        normalized_claim
    )

    severity_hint = _match_severity_hint(
        normalized_claim
    )

    state["parsed_claim"] = ParsedClaim(
        claim_summary=claim_record.user_claim,
        claimed_issue=claimed_issue,
        claimed_object_part=claimed_object_part,
        severity_hint=severity_hint,
    )

    state["trace"].append(
        (
            "load_claim: "
            f"issue={claimed_issue}, "
            f"part={claimed_object_part}, "
            f"severity={severity_hint}"
        )
    )

    return state
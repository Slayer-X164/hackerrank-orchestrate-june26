"""Shared state definitions for the claim verification workflow.

This module defines the single state object that is passed through every
LangGraph node. The workflow is intentionally designed around one shared state
so that each step can read earlier findings and append its own outputs without
introducing side channels.

Model calls are intentionally not implemented yet. The state includes the
future model configuration needed for `langchain-openrouter` with the free
`gpt-oss-120b` route so the rest of the workflow can be wired now and filled in
later.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypedDict

from typing_extensions import NotRequired

ClaimObject = Literal["car", "laptop", "package"]
RequirementClaimObject = ClaimObject | Literal["all"]
ClaimStatus = Literal["supported", "contradicted", "not_enough_information"]
IssueType = Literal[
    "dent",
    "scratch",
    "crack",
    "glass_shatter",
    "broken_part",
    "missing_part",
    "torn_packaging",
    "crushed_packaging",
    "water_damage",
    "stain",
    "none",
    "unknown",
]
Severity = Literal["none", "low", "medium", "high", "unknown"]
RiskFlag = Literal[
    "none",
    "blurry_image",
    "cropped_or_obstructed",
    "low_light_or_glare",
    "wrong_angle",
    "wrong_object",
    "wrong_object_part",
    "damage_not_visible",
    "claim_mismatch",
    "possible_manipulation",
    "non_original_image",
    "text_instruction_present",
    "user_history_risk",
    "manual_review_required",
]
CarObjectPart = Literal[
    "front_bumper",
    "rear_bumper",
    "door",
    "hood",
    "windshield",
    "side_mirror",
    "headlight",
    "taillight",
    "fender",
    "quarter_panel",
    "body",
    "unknown",
]
LaptopObjectPart = Literal[
    "screen",
    "keyboard",
    "trackpad",
    "hinge",
    "lid",
    "corner",
    "port",
    "base",
    "body",
    "unknown",
]
PackageObjectPart = Literal[
    "box",
    "package_corner",
    "package_side",
    "seal",
    "label",
    "contents",
    "item",
    "unknown",
]
ObjectPart = CarObjectPart | LaptopObjectPart | PackageObjectPart
WorkflowNodeName = Literal[
    "load_claim",
    "analyze_images",
    "validate_evidence",
    "analyze_risk",
    "verify_claim",
    "format_output",
]


@dataclass(slots=True)
class WorkflowModelConfig:
    """Static model settings for future LLM and VLM integration."""

    provider: str = "langchain-openrouter"
    model_name: str = "openai/gpt-oss-120b:free"
    temperature: float = 0.0


@dataclass(slots=True)
class ClaimRecord:
    """Raw claim row loaded from a CSV source."""

    user_id: str
    image_paths: list[str]
    user_claim: str
    claim_object: ClaimObject


@dataclass(slots=True)
class ParsedClaim:
    """Structured interpretation of the user conversation."""

    claim_summary: str
    claimed_issue_text: str | None = None
    claimed_object_part_text: str | None = None
    claimed_issue: IssueType | None = None
    claimed_object_part: ObjectPart | None = None
    severity_hint: str | None = None


@dataclass(slots=True)
class ImageAnalysis:
    """Per-image analysis container produced by the image-analysis node."""

    image_path: str
    image_id: str
    visible_object: ClaimObject | None = None
    visible_object_part: ObjectPart | None = None
    visible_issue_type: IssueType | None = None
    visible_severity: Severity | None = None
    quality_flags: list[RiskFlag] | None = None
    relevance_flags: list[RiskFlag] | None = None
    trust_flags: list[RiskFlag] | None = None
    is_usable: bool = True
    is_relevant: bool | None = None
    claimed_part_visible: bool | None = None
    claimed_part_clear: bool | None = None
    provides_context: bool | None = None
    correct_orientation: bool | None = None
    notes: str | None = None
    confidence: float | None = None
    supports_claim: bool | None = None
    contradicts_claim: bool | None = None
    relevance_score: float | None = None
    selection_rationale: str | None = None


@dataclass(slots=True)
class EvidenceAssessment:
    """Result of comparing observed evidence against the minimum requirements."""

    evidence_standard_met_reason: str
    evidence_standard_met: bool
    valid_image: bool
    unmet_requirements: list[str]
    applied_requirement_ids: list[str]
    satisfied_requirement_ids: list[str]
    failed_requirement_ids: list[str]
    supporting_image_ids: list[str]
    rationale: str


@dataclass(slots=True)
class RiskAssessment:
    """Risk findings derived from user history and image metadata."""

    risk_flags: list[RiskFlag]
    rationale: str
    risk_justification: str


@dataclass(slots=True)
class VerificationDecision:
    """Final structured decision before output formatting."""

    issue_type: IssueType
    object_part: ObjectPart
    claim_status: ClaimStatus
    claim_status_justification: str
    supporting_image_ids: list[str]
    severity: Severity
    claim_conflict_score: float | None = None


@dataclass(slots=True)
class EvidenceRequirement:
    """Normalized evidence requirement row from the dataset."""

    requirement_id: str
    claim_object: RequirementClaimObject
    applies_to: str
    minimum_image_evidence: str


class ClaimWorkflowState(TypedDict):
    """Single shared workflow state passed across all LangGraph nodes."""

    claim_id: str
    repo_root: str
    dataset_root: str
    model_config: WorkflowModelConfig
    claim_record: ClaimRecord
    user_history: dict[str, Any] | None
    evidence_requirements: list[EvidenceRequirement]
    image_ids: list[str]
    parsed_claim: NotRequired[ParsedClaim]
    image_analyses: NotRequired[list[ImageAnalysis]]
    evidence_assessment: NotRequired[EvidenceAssessment]
    risk_assessment: NotRequired[RiskAssessment]
    verification_decision: NotRequired[VerificationDecision]
    formatted_output: NotRequired[dict[str, str]]
    trace: list[str]
    errors: list[str]


def create_initial_state(
    *,
    claim_id: str,
    repo_root: str,
    dataset_root: str,
    claim_record: ClaimRecord,
    user_history: dict[str, Any] | None = None,
    evidence_requirements: list[EvidenceRequirement] | None = None,
    model_config: WorkflowModelConfig | None = None,
) -> ClaimWorkflowState:
    """Create the shared state object used by every workflow node.

    Args:
        claim_id: Stable claim identifier used for tracing and logs.
        repo_root: Absolute path to the repository root.
        dataset_root: Absolute path to the dataset directory.
        claim_record: Raw claim row that the workflow will evaluate.
        user_history: Optional user history row already looked up by `user_id`.
        evidence_requirements: Optional preloaded evidence rules.
        model_config: Optional override for future model integration.

    Returns:
        A fully initialized shared state dictionary that LangGraph nodes can
        mutate incrementally.
    """

    image_ids = [Path(path).stem for path in claim_record.image_paths]
    return ClaimWorkflowState(
        claim_id=claim_id,
        repo_root=repo_root,
        dataset_root=dataset_root,
        model_config=model_config or WorkflowModelConfig(),
        claim_record=claim_record,
        user_history=user_history,
        evidence_requirements=evidence_requirements or [],
        image_ids=image_ids,
        trace=[],
        errors=[],
    )

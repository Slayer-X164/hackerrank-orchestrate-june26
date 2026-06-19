import os
from ..state import (
    ClaimWorkflowState,
    ImageAnalysis,
    ClaimObject,
    ObjectPart,
    IssueType,
    Severity,
    RiskFlag,
)
from pathlib import Path
import base64
from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv
from typing import get_args
import json
from pprint import pprint

load_dotenv()


def analyze_single_image(
    state: ClaimWorkflowState,
    image_path: str,
    image_id: str,
    index: int,
) -> ImageAnalysis:
    claim_record = state["claim_record"]
    print("Analyzing:", image_path)
    image_file = Path(state["dataset_root"]) / image_path

    with open(image_file, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    llm = ChatOpenRouter(
        model="nvidia/nemotron-nano-12b-v2-vl:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
        temperature=0,
    )

    prompt = f"""
You are an insurance evidence reviewer.

Claim Object:
{claim_record.claim_object}

Claim Conversation:
{claim_record.user_claim}

Analyze ONLY the provided image.

Return ONLY valid JSON.

Rules:

visible_object must be exactly one of:
{list(get_args(ClaimObject))}

visible_object_part must be exactly one of:
{list(get_args(ObjectPart))}

visible_issue_type must be exactly one of:
{list(get_args(IssueType))}

visible_severity must be exactly one of:
{list(get_args(Severity))}

quality_flags may contain zero or more of:
{list(get_args(RiskFlag))}

JSON schema:

{{
  "visible_object": "",
  "visible_object_part": "",
  "visible_issue_type": "",
  "visible_severity": "",

  "claimed_part_visible": true | false,
  "claimed_part_clear": true | false,


  "quality_flags": [
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
],

  "confidence": 0.10 - 0.99,

  "notes": " example -> Visible scratch on front bumper."
}}
"""
    try:
        response = llm.invoke(
            [
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                        },
                    ],
                },
            ]
        )

        # print("RAW RESPONSE:")
        # pprint(response.content)
        content = response.content.strip()

        if content.startswith("```"):
            content = content.split("\n", 1)[1]

        if content.endswith("```"):
            content = content.rsplit("```", 1)[0]

        content = content.strip()
        pprint(f"passed content {content}")
        result = json.loads(content)
    except Exception as e:
        print("something went wrong image json ", e)

        result = {
            "visible_object": claim_record.claim_object,
            "visible_object_part": "unknown",
            "visible_issue_type": "unknown",
            "visible_severity": "unknown",
            "quality_flags": ["manual_review_required"],
            "claimed_part_visible": False,
            "claimed_part_clear": False,
            "confidence": 0.0,
            "notes": f"JSON parse failure: {e}",
        }
    return ImageAnalysis(
        image_path=image_path,
        image_id=image_id,
        visible_object=result.get("visible_object"),
        visible_object_part=result.get(
            "visible_object_part",
            "unknown",
        ),
        visible_issue_type=result.get(
            "visible_issue_type",
            "unknown",
        ),
        visible_severity=result.get(
            "visible_severity",
            "unknown",
        ),
        quality_flags=result.get(
            "quality_flags",
            [],
        ),
        relevance_flags=[],
        trust_flags=[],
        claimed_part_visible=result.get(
            "claimed_part_visible",
            False,
        ),
        claimed_part_clear=result.get(
            "claimed_part_clear",
            False,
        ),

        provides_context=index > 0,
        correct_orientation=True,
        notes=result.get("notes"),
        confidence=float(result.get("confidence", 0.0)),
        relevance_score=float(result.get("confidence", 0.0)),
        selection_rationale=("Selected by vision model analysis."),
    )

def aggregate_image_findings(image_analyis: ImageAnalysis) -> ClaimWorkflowState:
    ...

def analyze_images_node(state: ClaimWorkflowState) -> ClaimWorkflowState:

    analyses = [
        analyze_single_image(state, image_path, image_id, index)
        for index, (image_path, image_id) in enumerate(
            zip(state["claim_record"].image_paths, state["image_ids"], strict=True)
        )
    ]
    state["image_analyses"] = analyses
    state["trace"].append(
        "analyze_images: populated deterministic per-image mock findings"
    )
    return state

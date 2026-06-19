# Dataset Analysis

## Overview

This document summarizes the task specification in [problem_statement.md](/home/slayer/Desktop/hackerrank-orchestrate-june26/problem_statement.md), the labeled development set in [dataset/sample_claims.csv](/home/slayer/Desktop/hackerrank-orchestrate-june26/dataset/sample_claims.csv), user metadata in [dataset/user_history.csv](/home/slayer/Desktop/hackerrank-orchestrate-june26/dataset/user_history.csv), and evidence rules in [dataset/evidence_requirements.csv](/home/slayer/Desktop/hackerrank-orchestrate-june26/dataset/evidence_requirements.csv).

The task is a multimodal claim-verification problem over three object types:

- `car`
- `laptop`
- `package`

The system must use images as the primary source of truth, while using the chat transcript to identify the claimed issue and object part, evidence requirements to determine reviewability, and user history to add risk context.

## Dataset Inventory

- `problem_statement.md`: specification for inputs, outputs, allowed values, and evaluation expectations.
- `dataset/sample_claims.csv`: 20 labeled examples with both inputs and expected outputs.
- `dataset/user_history.csv`: 47 user-level history rows.
- `dataset/evidence_requirements.csv`: 10 evidence requirement rules.

## 1. Complete Schema Of Every Dataset

### 1.1 Task-Level Input Schema From `problem_statement.md`

The production input file `dataset/claims.csv` is described as having one row per claim with these columns:

| Column | Type | Description | Notes |
|---|---|---|---|
| `user_id` | string | User identifier | Join key into `user_history.csv` |
| `image_paths` | string | One or more image paths separated by semicolons | Image IDs are filenames without extension |
| `user_claim` | string | Chat transcript describing the issue | May be long, mixed-language, and conversational |
| `claim_object` | enum string | Claimed object type | One of `car`, `laptop`, `package` |

### 1.2 Output Schema From `problem_statement.md`

The required `output.csv` columns are:

| Column | Type | Description | Notes |
|---|---|---|---|
| `user_id` | string | Copied from input | Identity field |
| `image_paths` | string | Copied from input | Semicolon-delimited |
| `user_claim` | string | Copied from input | Original conversation |
| `claim_object` | enum string | Copied from input | `car`, `laptop`, `package` |
| `evidence_standard_met` | boolean-like string | Whether images are sufficient to evaluate | Uses literal `true` or `false` |
| `evidence_standard_met_reason` | string | Short reason for evidence sufficiency | Should be image-grounded |
| `risk_flags` | semicolon-delimited string | Risk indicators or `none` | May include multiple flags |
| `issue_type` | enum string | Visible issue category | `none` means no visible issue; `unknown` means indeterminate |
| `object_part` | enum string | Relevant part of object | Enum depends on `claim_object` |
| `claim_status` | enum string | Final claim decision | `supported`, `contradicted`, `not_enough_information` |
| `claim_status_justification` | string | Concise image-grounded explanation | May mention risk context secondarily |
| `supporting_image_ids` | semicolon-delimited string | Supporting image IDs or `none` | Can be subset of uploaded images |
| `valid_image` | boolean-like string | Whether image set is usable for automated review | Uses literal `true` or `false` |
| `severity` | enum string | Estimated damage severity | `none`, `low`, `medium`, `high`, `unknown` |

### 1.3 `dataset/sample_claims.csv`

This is a labeled training and evaluation-style dataset. It contains the complete input fields plus the complete expected output fields.

| Column | Type | Observed / Allowed Values | Description |
|---|---|---|---|
| `user_id` | string | `user_001` ... `user_034` in sample | User identifier |
| `image_paths` | string | One or two image paths in sample | Semicolon-delimited image list |
| `user_claim` | string | Natural-language support conversation | Contains English and Hinglish examples |
| `claim_object` | enum string | `car`, `laptop`, `package` | Object category |
| `evidence_standard_met` | boolean-like string | `true`, `false` | Whether evidence suffices for evaluation |
| `evidence_standard_met_reason` | string | Free text | Reason tied to visibility and coverage |
| `risk_flags` | semicolon-delimited string | `none` or one/more risk flags | Additive review/risk signals |
| `issue_type` | enum string | See full allowed set below | Visible issue classification |
| `object_part` | enum string | Object-specific part label | Claimed or observed part |
| `claim_status` | enum string | `supported`, `contradicted`, `not_enough_information` | Final claim outcome |
| `claim_status_justification` | string | Free text | Image-based rationale |
| `supporting_image_ids` | semicolon-delimited string | `img_1`, `img_2`, `img_1;img_2`, or `none` | Images supporting the decision |
| `valid_image` | boolean-like string | `true`, `false` | Whether image set is usable |
| `severity` | enum string | `none`, `low`, `medium`, `high`, `unknown` | Estimated issue severity |

Observed structure by object in the sample set:

- Cars: 8 rows
- Laptops: 6 rows
- Packages: 6 rows

Observed pattern distribution in the sample set:

- Supported: common across all three objects
- Contradicted: present for all three objects
- Not enough information: present for car and package in sample
- Multi-image reasoning: several rows require choosing a single best image from the set
- Mixed-language conversation: at least car and package samples contain Hinglish

### 1.4 `dataset/user_history.csv`

This is a user-level enrichment table keyed by `user_id`.

| Column | Type | Observed Values | Description |
|---|---|---|---|
| `user_id` | string | `user_001` ... `user_047` | Primary key for join |
| `past_claim_count` | integer-like string | `0` to `14` observed | Total historical claim count |
| `accept_claim` | integer-like string | `0` to `4` observed | Number of accepted claims |
| `manual_review_claim` | integer-like string | `0` to `4` observed | Number sent to manual review |
| `rejected_claim` | integer-like string | `0` to `7` observed | Number rejected |
| `last_90_days_claim_count` | integer-like string | `0` to `9` observed | Recency/frequency signal |
| `history_flags` | semicolon-delimited string | `none`, `user_history_risk`, `manual_review_required`, or both | Precomputed risk metadata |
| `history_summary` | string | Free text summary | Describes prior patterns and failure modes |

Important semantics:

- User history is supportive context, not ground truth.
- Some summaries reference repeated image similarity, authenticity concerns, side confusion, screenshots, wrong object evidence, or severity exaggeration.
- `history_flags` overlaps with allowed output `risk_flags`, suggesting the system may pass through or map this context into final output.

### 1.5 `dataset/evidence_requirements.csv`

This table defines minimum evidence quality and visibility rules.

| Column | Type | Observed Values | Description |
|---|---|---|---|
| `requirement_id` | string | 10 unique IDs | Stable rule identifier |
| `claim_object` | enum string | `all`, `car`, `laptop`, `package` | Scope of requirement |
| `applies_to` | string | Issue family description | Human-readable applicability |
| `minimum_image_evidence` | string | Free text rule | Operational reviewability rule |

Requirement coverage:

- General requirements for all claims:
  - object part visibility
  - multi-image handling
  - reviewability
- Car-specific requirements:
  - body panels for dents/scratches
  - glass/light/mirror for cracks or broken parts
  - enough context when side/orientation/identity matters
- Laptop-specific requirements:
  - screen/keyboard/trackpad visibility
  - hinge/lid/corner/body/base/port context
- Package-specific requirements:
  - exterior damage
  - label or stain review
  - contents visibility for missing-item claims

## 2. All Possible Output Labels And Values

### 2.1 `claim_status`

- `supported`
- `contradicted`
- `not_enough_information`

Interpretation:

- `supported`: images visually support the claim.
- `contradicted`: images are sufficient, but what is visible does not match the claim.
- `not_enough_information`: images do not allow reliable evaluation of the claim.

### 2.2 `issue_type`

- `dent`
- `scratch`
- `crack`
- `glass_shatter`
- `broken_part`
- `missing_part`
- `torn_packaging`
- `crushed_packaging`
- `water_damage`
- `stain`
- `none`
- `unknown`

Interpretation:

- `none`: relevant part is visible and no issue is present.
- `unknown`: issue cannot be determined from the evidence.

### 2.3 `object_part` Values By Object Type

Car:

- `front_bumper`
- `rear_bumper`
- `door`
- `hood`
- `windshield`
- `side_mirror`
- `headlight`
- `taillight`
- `fender`
- `quarter_panel`
- `body`
- `unknown`

Laptop:

- `screen`
- `keyboard`
- `trackpad`
- `hinge`
- `lid`
- `corner`
- `port`
- `base`
- `body`
- `unknown`

Package:

- `box`
- `package_corner`
- `package_side`
- `seal`
- `label`
- `contents`
- `item`
- `unknown`

### 2.4 `risk_flags`

Allowed values:

- `none`
- `blurry_image`
- `cropped_or_obstructed`
- `low_light_or_glare`
- `wrong_angle`
- `wrong_object`
- `wrong_object_part`
- `damage_not_visible`
- `claim_mismatch`
- `possible_manipulation`
- `non_original_image`
- `text_instruction_present`
- `user_history_risk`
- `manual_review_required`

Observed sample usage:

- `none`
- `claim_mismatch`
- `user_history_risk`
- `manual_review_required`
- `wrong_angle`
- `damage_not_visible`
- `blurry_image`
- `non_original_image`
- `cropped_or_obstructed`
- `wrong_object`
- `text_instruction_present`

Not yet observed in sample but still allowed:

- `low_light_or_glare`
- `wrong_object_part`
- `possible_manipulation`

### 2.5 `severity`

- `none`
- `low`
- `medium`
- `high`
- `unknown`

Observed semantics:

- `none`: visible area contradicts a physical-damage claim and no damage is seen.
- `unknown`: evidence is insufficient to assess severity.
- `low`/`medium`/`high`: visual severity of the observed issue, not necessarily the user's claimed severity.

### 2.6 Boolean-Like Fields

`evidence_standard_met`:

- `true`
- `false`

`valid_image`:

- `true`
- `false`

Important distinction:

- `evidence_standard_met=false` means the image set is insufficient for the specific claim evaluation.
- `valid_image=false` means the image set is not usable or not trustworthy enough for automated review.
- These fields are related but not identical.

Observed combinations in sample:

- `evidence_standard_met=true`, `valid_image=true`
- `evidence_standard_met=false`, `valid_image=true`
- `evidence_standard_met=false`, `valid_image=false`
- `evidence_standard_met=true`, `valid_image=false`

That last combination is especially important: a claim can still be evaluable even if the image has authenticity or originality concerns, as seen in a contradicted row with `non_original_image`.

### 2.7 `supporting_image_ids`

Allowed pattern:

- One or more image IDs such as `img_1`
- Multiple IDs separated by semicolons such as `img_1;img_2`
- `none`

Observed semantics:

- For `supported`, it points to the best evidence image(s).
- For `contradicted`, it can point to the image(s) that contradict the claim.
- For `not_enough_information`, it may be `none`.

## 3. Relationships Between Claims, Images, History, And Evidence Requirements

### 3.1 Core Entity Relationship

One claim row connects four information sources:

1. Claim row:
   - provides `user_id`, `image_paths`, `user_claim`, `claim_object`
2. Images:
   - provide the primary visual evidence
3. User history:
   - adds risk and review context through `user_id`
4. Evidence requirements:
   - determine whether submitted images satisfy minimum reviewability standards for the claim type and issue family

### 3.2 Functional Dependency Flow

Recommended reasoning order:

1. Parse the conversation to extract:
   - object type confirmation
   - claimed issue type
   - claimed object part
   - severity cues
   - whether the claim is about exterior, contents, or a side-specific component
2. Split and inspect images independently.
3. Determine whether any image satisfies the relevant evidence requirement.
4. Identify visible object, part, issue, and severity.
5. Compare visual evidence to the claim text.
6. Add non-visual risk context from user history.
7. Produce final structured outputs and a concise justification.

### 3.3 Claim To Image Relationship

- One claim may have one or multiple images.
- Multiple images are not interchangeable; each must be assessed separately.
- A single best image may drive the decision, even when others are blurry or contextual only.
- Some rows require combining context from one image and detail from another.

Examples from the sample set:

- One image provides context, another provides the close-up proof.
- One image is blurry but another is sufficient.
- The only image shows the wrong part, producing `not_enough_information`.

### 3.4 Claim To History Relationship

- `user_id` is a left-join key into `user_history.csv`.
- History does not change the visible issue, part, or severity directly.
- History can add:
  - `user_history_risk`
  - `manual_review_required`
  - suspicion around originality, exaggeration, repeated patterns, or wrong-object claims

Observed behavior in sample:

- Clear visual support can still coexist with `user_history_risk`.
- A contradicted or insufficient case often adds `manual_review_required` when history is concerning.
- Low-risk users often receive `risk_flags=none` when the images are straightforward.

### 3.5 Claim To Evidence Requirement Relationship

The evidence requirements act like minimum reviewability gates:

- General rules apply to every claim.
- Object-specific rules refine what must be visible.
- Certain issue families require different context:
  - car scratches/dents require a surface angle
  - glass/light/mirror claims require direct visibility of cracks or missing parts
  - package contents claims require an opened package and visible contents area
  - laptop hinge/body claims require enough context to identify the exact component

### 3.6 Interaction Between `evidence_standard_met`, `claim_status`, And `valid_image`

These are separate judgments:

- `evidence_standard_met` asks: can we evaluate the claim?
- `claim_status` asks: what does the evidence say?
- `valid_image` asks: is the image set usable for automated review?

Observed behavior:

- If the wrong part is shown, `evidence_standard_met=false`, `claim_status=not_enough_information`, `valid_image=true`.
- If authenticity or non-originality is suspected, `valid_image=false` may occur even when the claim is contradicted confidently.
- If package contents are obscured, both `evidence_standard_met=false` and `valid_image=false` may occur.

## 4. Potential Edge Cases

### 4.1 Conversation Parsing Edge Cases

- Long conversations where the claim appears late in the transcript
- The user initially describes the wrong area, then corrects it
- Mixed-language text such as Hindi-English code switching
- Ambiguous severity language like "pretty bad" without a precise issue type
- Claims about one part while the image shows another

### 4.2 Image Evidence Edge Cases

- One image is blurry, another is usable
- Full-view image lacks detail, close-up lacks context
- Cropped images hide the claimed part
- Wrong angle prevents assessing dents/scratches
- Glare or low light obscures damage
- Submitted image shows the wrong object category entirely
- Submitted image shows the right object but wrong part
- Image contains text overlays or instructions that should not affect damage assessment
- Non-original images, screenshots, or manipulated images

### 4.3 Labeling Edge Cases

- `issue_type=none` versus `issue_type=unknown`
- `claim_status=contradicted` versus `not_enough_information`
- `valid_image=false` even when there is enough evidence to contradict the claim
- Supporting image IDs in contradiction cases
- Multiple simultaneous risk flags and their ordering

### 4.4 Object-Specific Edge Cases

Cars:

- Left/right or front/rear confusion
- Headlight versus bumper or fender ambiguity
- Severe frontal damage image submitted for a hood scratch claim
- Mirror damage where only alignment, not fracture, is visible

Laptops:

- Cosmetic versus functional claims when no visible physical damage appears
- Screen crack versus reflection artifact
- Hinge damage versus lid/body seam issue
- Trackpad complaint with no visible damage

Packages:

- Missing contents claim without visible expected contents
- Torn seal versus normal packaging folds
- Water damage versus printing/stain artifact
- Box damage claim with an image of a different object

### 4.5 Dataset Coverage Edge Cases

- Users in `claims.csv` may be absent from `user_history.csv`
- Future test rows may use allowed labels not observed in sample
- The sample set may not contain every possible object-part and issue-type combination
- Some evidence rules such as `possible_manipulation` are allowed but not directly demonstrated in the sample

## 5. Recommended Architecture

### 5.1 High-Level Design

A robust solution should be modular and deterministic where possible:

1. Input loader
   - read claims, history, and evidence rules
   - normalize paths and delimiters
2. Claim parser
   - extract claimed issue, part, severity hints, and object details from `user_claim`
3. Image analyzer
   - inspect each image independently
   - return object identity, visible parts, visible issue, visibility/quality flags, and trust signals
4. Evidence-rule matcher
   - choose applicable rules by `claim_object` and issue family
   - determine whether minimum evidence is met
5. Decision engine
   - compare textual claim against visual evidence
   - decide `supported`, `contradicted`, or `not_enough_information`
6. Risk enricher
   - join user history
   - add `user_history_risk` and `manual_review_required` when appropriate
7. Output formatter
   - emit normalized enums and justifications
8. Evaluation pipeline
   - run on `sample_claims.csv`
   - compare against expected outputs

### 5.2 Recommended Internal Data Model

Per claim, structure the reasoning around normalized intermediate objects:

- `claim_parse`
  - extracted claim object
  - claimed issue type
  - claimed part
  - issue family
  - claim text summary
- `image_result[]`
  - image ID
  - detected object type
  - visible parts
  - detected issue type
  - evidence quality flags
  - trust flags
  - severity estimate
  - whether it supports, contradicts, or is irrelevant
- `history_context`
  - matched history row
  - derived risk flags
  - summarized history risk
- `decision`
  - evidence sufficiency
  - final status
  - selected supporting IDs
  - final justification

### 5.3 Recommended Decision Policy

Use a staged policy:

1. Verify object relevance.
2. Verify part visibility and issue-family-specific evidence rules.
3. Identify best image or image subset.
4. Decide whether visible evidence:
   - matches the claim
   - contradicts the claim
   - is insufficient
5. Add risk flags without overriding strong visual evidence.

### 5.4 Why This Architecture Fits The Dataset

- The sample labels repeatedly separate evidence sufficiency from claim truth.
- Multi-image rows need per-image scoring, not naive concatenation.
- User history affects review risk, not core visual classification.
- Evidence rules map naturally to a gating layer before final classification.

## 6. Risks And Ambiguities In The Dataset

### 6.1 Specification Ambiguities

- No explicit rule defines how to order multiple `risk_flags`.
- The spec says use the closest matching allowed value, which leaves room for interpretation when issue type is borderline.
- `valid_image` is underdefined compared with `evidence_standard_met`; the sample set becomes the main source of truth for how to separate them.
- There is no explicit ontology linking every conversational phrase to an `issue_type` or `object_part`.

### 6.2 Sample Label Ambiguities

- Some contradiction cases are based on mismatch between claimed issue and visible issue, not just absence of damage.
- `severity` seems to represent visible damage severity, but contradiction rows with the wrong object still receive a severity value such as `low`; this may reflect the visible object's condition rather than the claimed object's condition.
- A row can be `contradicted` with `valid_image=false`, implying the system may still use evidence while distrustfully flagging it.

### 6.3 Generalization Risks

- The sample size is small, especially per label combination.
- Not all allowed risk flags or issue types are demonstrated.
- Real test rows may have more images, noisier text, or unseen combinations.
- Distribution shift is likely for image quality, object viewpoint, and missing-history scenarios.

### 6.4 Operational Risks

- Vision models may overfit to prompt wording and become nondeterministic.
- OCR-like text inside images may distract the model unless explicitly ignored.
- Cost can rise quickly if every image is passed through multiple model stages.
- Repeated claims with similar images may call for image hashing or duplicate detection, but that is not guaranteed by the starter spec alone.

## 7. Candidate Solution Strategies

### Strategy 1: End-To-End VLM Structured Extraction

Approach:

- Give the claim text, image(s), and allowed labels to a vision-language model.
- Ask for fully structured JSON covering all required fields.

Pros:

- Fastest to implement
- Handles multimodal reasoning in one place
- Can naturally connect conversation text and images
- Flexible for mixed-language transcripts

Cons:

- Harder to make deterministic
- More prone to label drift and schema violations
- May blur evidence sufficiency, trust, and claim-status distinctions
- More expensive if run monolithically on every row

Best fit:

- Strong baseline or hackathon-first prototype

### Strategy 2: Modular Pipeline With Rule-Based Gating Plus VLM

Approach:

- Parse conversation and user history with lightweight deterministic logic or text LLM.
- Run per-image VLM analysis for object, part, damage, and quality.
- Apply evidence requirements and decision rules in code.

Pros:

- Best alignment with the dataset structure
- Easier to debug and evaluate component errors
- More deterministic and controllable
- Separates visual truth from policy logic
- Makes it easier to add manual-review and risk rules cleanly

Cons:

- Higher implementation complexity
- Requires careful schema design for intermediate outputs
- Still depends on VLM quality for core visual interpretation

Best fit:

- Most balanced final architecture for quality and reproducibility

### Strategy 3: Two-Stage Cascade With Cheap Filter Then Expensive Review

Approach:

- Use a small/cheap model or heuristic layer first for object validation, image quality, and obvious mismatches.
- Escalate only uncertain or promising rows to a stronger VLM.

Pros:

- Better cost control
- Faster runtime on clear-cut rows
- Good for larger test sets or stricter operational analysis

Cons:

- Risk of early-stage false negatives
- Requires threshold calibration
- More moving parts and harder evaluation

Best fit:

- Production-leaning system where cost and latency matter

### Strategy 4: Retrieval-Assisted Prompting From Sample Exemplars

Approach:

- Retrieve the most similar sample claims by object, issue family, and risk pattern.
- Feed a few examples into a VLM/LLM prompt before predicting the current row.

Pros:

- Can improve label consistency on a small ontology
- Useful for rare combinations or subtle distinctions like contradiction versus insufficiency
- Leverages sample annotations directly

Cons:

- Sample set is small, so retrieval coverage is limited
- Risks overfitting to development examples
- More prompt complexity and token cost

Best fit:

- Secondary enhancement on top of a modular pipeline, not as the sole approach

## Recommended Final Direction

The strongest overall direction is Strategy 2, optionally enhanced with parts of Strategy 3 and Strategy 4.

Recommended combination:

- Base pipeline: modular rule-driven architecture
- Visual core: per-image VLM analysis
- Decision layer: deterministic mapping from evidence outputs to final labels
- Optional optimization: cheap first-pass image validity and object checks
- Optional consistency boost: exemplar retrieval only for ambiguous rows

Why this is the best fit:

- It matches the task instruction that images are the primary truth source.
- It respects the separate roles of claim text, evidence rules, and history.
- It gives the cleanest path to reproducible evaluation on `sample_claims.csv`.
- It reduces the risk of a single monolithic prompt collapsing multiple label decisions together.

## Key Practical Findings

- `sample_claims.csv` is not just a label file; it encodes the intended policy for sufficiency, contradiction, risk, and trust.
- `user_history.csv` should enrich `risk_flags`, not dominate `claim_status`.
- `evidence_requirements.csv` is best treated as an explicit reviewability gate before final classification.
- The most important modeling distinction is between:
  - "the image shows no such damage"
  - "the image shows the wrong thing"
  - "the image is not sufficient to tell"
- Multi-image reasoning matters. The system should score images independently and then aggregate.

# Claim Verification Workflow

## Architecture

Claim
→ Load Claim
→ Analyze Images
→ Aggregate Findings
→ Validate Evidence
→ Analyze Risk
→ Verify Claim
→ Format Output

## Tech Stack

* Python
* LangGraph
* LangChain
* OpenRouter
* Vision Language Models

## Running

Generate predictions:

```bash
python3 code/main.py
```

Run evaluation:

```bash
python3 code/evaluation/main.py
```

## Output

The workflow generates:

* output.csv

containing predictions for all claims in dataset/claims.csv.

## Key Features

* Multi-image claim processing
* Structured image analysis
* Evidence validation
* Risk assessment
* Claim verification
* CSV output generation

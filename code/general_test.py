from data.loaders import load_claims, load_user_history, load_evidence_requirements
from pprint import pprint
from claim_workflow.state import create_initial_state
from claim_workflow.graph import build_claim_verification_graph
claims = load_claims("./dataset")
history_map = load_user_history("./dataset")
requirements = load_evidence_requirements("./dataset")

claim = claims[0]

state = create_initial_state(
    claim_id="sample-001",
    repo_root=".",
    dataset_root="./dataset",
    claim_record=claim,
    user_history=history_map.get(claim.user_id),
    evidence_requirements=requirements,
)

graph = build_claim_verification_graph()

result = graph.invoke(state)

pprint(result["formatted_output"])
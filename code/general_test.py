from data.loaders import load_claims, load_user_history, load_evidence_requirements
from pprint import pprint
from claim_workflow.state import create_initial_state
from claim_workflow.graph import build_claim_verification_graph
from claim_workflow.nodes.analyze_images import analyze_single_image

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

analysis = analyze_single_image(
    state,
    claim.image_paths[0],
    "img_1",
    0,
)

print(analysis)

# graph = build_claim_verification_graph()

# result = graph.invoke(state)

# pprint(result["formatted_output"])




# from langchain_openrouter import ChatOpenRouter
# import os
# from dotenv import load_dotenv
# load_dotenv()
# llm = ChatOpenRouter(
#     model="nvidia/nemotron-nano-12b-v2-vl:free",
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.environ["OPENROUTER_API_KEY"],
# )

# response = llm.invoke("Say hello")

# print(response.content)
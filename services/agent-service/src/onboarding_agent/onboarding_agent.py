import os
from ..rag.rag import query_knowledgebase
from typing import List, Tuple
# from autogen import AssistantAgent, UserProxyAgent


# groq_api_key = os.environ['API_KEY']

# config_list = [{
#     "model": "llama-3.3-70b-versatile",
#     "api_key": groq_api_key,
#     "api_type": "groq"
# }]



def onboarding_agent(query: str, history: List[Tuple[str, str]]) -> str:

    response = query_knowledgebase(query)

    return response['answer']
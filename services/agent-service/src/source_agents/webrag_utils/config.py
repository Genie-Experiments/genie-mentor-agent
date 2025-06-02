import os
from dotenv import load_dotenv

load_dotenv()

def get_env_variable(var_name: str, cast_type=None, required: bool = True):
    value = os.getenv(var_name)
    if required and value is None:
        raise ValueError(f"{var_name} is not set in the environment variables.")
    return cast_type(value) if cast_type and value is not None else value

GROQ_API_KEY = get_env_variable("WEBRAG_GROQ_API_KEY")
GOOGLE_API_KEY = get_env_variable("WEBRAG_GOOGLE_API_KEY")
GOOGLE_CX = get_env_variable("WEBRAG_GOOGLE_CX")
OPENAI_API_KEY = get_env_variable("WEBRAG_OPENAI_API_KEY")
EMBED_DEFAULT_MODEL = get_env_variable("WEBRAG_EMBED_DEFAULT_MODEL")
MAX_GENERAL_RESULTS = get_env_variable("WEBRAG_MAX_GENERAL_RESULTS", cast_type=int)
MAX_VIDEO_RESULTS = get_env_variable("WEBRAG_MAX_VIDEO_RESULTS", cast_type=int)
LLM_DEFAULT_MODEL = get_env_variable("WEBRAG_LLM_DEFAULT_MODEL")
TOP_K_URLS = get_env_variable("WEBRAG_TOP_K_URLS", cast_type=int)
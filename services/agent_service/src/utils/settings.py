import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = Field(..., description="API key for Groq LLM service")
    OPENAI_API_KEY: str = Field(..., description="API key for OpenAI services")

    # MCP Gateway Settings
    NOTION_MCP_TOKEN: Optional[str] = Field(
        None, description="Token for Notion MCP Gateway"
    )
    GITHUB_MCP_TOKEN: str = Field(..., description="Token for GitHub MCP Gateway")
    NOTION_API_KEY: str = Field(..., description="API key for Notion service")

    # Server Settings
    HOST: str = Field(default="0.0.0.0", description="Host address for the server")
    PORT: int = Field(default=8000, description="Port number for the server")
    BACKEND_URL: str = Field(
        default="http://127.0.0.1:8001", description="Backend service URL"
    )

    # Database Settings
    DATABASE_URL: str = Field(
        default="sqlite:///./memory.db", description="Database connection URL"
    )
    CHROMA_DB_PATH: str = Field(
        default="services/knowledge-base-chroma-index/chroma_db",
        description="Path to Chroma database",
    )

    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Logging format",
    )

    # Model Settings
    DEFAULT_MODEL: str = Field(
        default="meta-llama/llama-4-scout-17b-16e-instruct",
        description="Default LLM model to use",
    )
    
    # WebRAG Settings
    WEBRAG_LLM_DEFAULT_MODEL: str = Field(
        default="llama-3.3-70b-versatile", description="Default LLM model for WebRAG"
    )
    WEBRAG_EMBED_DEFAULT_MODEL: str = Field(
        default="text-embedding-ada-002",
        description="Default embedding model for WebRAG",
    )
    GOOGLE_SERVICE_ACCOUNT_FILE: str = Field(
        ..., description="Path to the Google service account JSON file"
    )
    KB_PROCESSED_FILES: str = Field(
        ..., description="Path to the file tracking already processed KB documents"
    )
    KB_DATA_STORAGE_DRIVE_ID: str = Field(
        ..., description="Path to the google drive where KB documents are stored"
    )
    WEBRAG_OPENAI_API_KEY: str = Field(..., description="OpenAI API key for WebRAG")
    WEBRAG_GROQ_API_KEY: str = Field(..., description="Groq API key for WebRAG")
    WEBRAG_GOOGLE_API_KEY: str = Field(..., description="Google API key for WebRAG")
    WEBRAG_GOOGLE_CX: str = Field(..., description="Google Custom Search Engine ID")
    WEBRAG_MAX_SEARCH_RESULTS: int = Field(
        default=10, description="Maximum number of search results"
    )
    WEBRAG_MAX_VIDEO_RESULTS: int = Field(
        default=5, description="Maximum number of video results"
    )
    WEBRAG_MAX_GENERAL_RESULTS: int = Field(
        default=5, description="Maximum number of general results"
    )
    WEBRAG_TOP_K: int = Field(
        default=3, description="Number of top results to consider"
    )

    # Cache Settings
    CACHE_TTL: int = Field(default=3600, description="Cache time-to-live in seconds")

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(
        default=100, description="Number of requests allowed per time window"
    )
    RATE_LIMIT_WINDOW: int = Field(
        default=3600, description="Time window for rate limiting in seconds"
    )

    # Session Settings
    SESSION_TIMEOUT: int = Field(default=1800, description="Session timeout in seconds")

    # CORS Settings
    CORS_ORIGINS: list[str] = Field(default=["*"], description="Allowed CORS origins")

    # Feature Flags
    ENABLE_EVALUATION: bool = Field(default=True, description="Enable evaluation agent")
    ENABLE_EDITING: bool = Field(default=True, description="Enable editing agent")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    This ensures we only load environment variables once.
    """
    return Settings()


# Create a global settings instance
settings = get_settings()

# Export commonly used settings as module-level variables
# API Keys
GROQ_API_KEY = settings.GROQ_API_KEY
OPENAI_API_KEY = settings.OPENAI_API_KEY
NOTION_MCP_TOKEN = settings.NOTION_MCP_TOKEN
GITHUB_MCP_TOKEN = settings.GITHUB_MCP_TOKEN
NOTION_API_KEY = settings.NOTION_API_KEY

# Server Settings
HOST = settings.HOST
PORT = settings.PORT
BACKEND_URL = settings.BACKEND_URL

# Database Settings
DATABASE_URL = settings.DATABASE_URL
CHROMA_DB_PATH = settings.CHROMA_DB_PATH

# Logging Settings
LOG_LEVEL = settings.LOG_LEVEL
LOG_FORMAT = settings.LOG_FORMAT

# Model Settings
DEFAULT_MODEL = settings.DEFAULT_MODEL

# WebRAG Settings
WEBRAG_LLM_DEFAULT_MODEL = settings.WEBRAG_LLM_DEFAULT_MODEL
WEBRAG_EMBED_DEFAULT_MODEL = settings.WEBRAG_EMBED_DEFAULT_MODEL
WEBRAG_OPENAI_API_KEY = settings.WEBRAG_OPENAI_API_KEY
WEBRAG_GROQ_API_KEY = settings.WEBRAG_GROQ_API_KEY
WEBRAG_GOOGLE_API_KEY = settings.WEBRAG_GOOGLE_API_KEY
WEBRAG_GOOGLE_CX = settings.WEBRAG_GOOGLE_CX
WEBRAG_MAX_SEARCH_RESULTS = settings.WEBRAG_MAX_SEARCH_RESULTS
WEBRAG_MAX_VIDEO_RESULTS = settings.WEBRAG_MAX_VIDEO_RESULTS
WEBRAG_MAX_GENERAL_RESULTS = settings.WEBRAG_MAX_GENERAL_RESULTS
WEBRAG_TOP_K = settings.WEBRAG_TOP_K

# Cache Settings
CACHE_TTL = settings.CACHE_TTL

# Rate Limiting
RATE_LIMIT_REQUESTS = settings.RATE_LIMIT_REQUESTS
RATE_LIMIT_WINDOW = settings.RATE_LIMIT_WINDOW

# Session Settings
SESSION_TIMEOUT = settings.SESSION_TIMEOUT

# CORS Settings
CORS_ORIGINS = settings.CORS_ORIGINS

# Feature Flags
ENABLE_EVALUATION = settings.ENABLE_EVALUATION
ENABLE_EDITING = settings.ENABLE_EDITING


GOOGLE_SERVICE_ACCOUNT_FILE = settings.GOOGLE_SERVICE_ACCOUNT_FILE
KB_PROCESSED_FILES = settings.KB_PROCESSED_FILES
KB_DATA_STORAGE_DRIVE_ID= settings.KB_DATA_STORAGE_DRIVE_ID
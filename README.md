# Genie Mentor Agent

Genie Mentor Agent is a platform designed to automate the onboarding and continuous learning of developers within an organization. By leveraging AI agents, the system aims to:

- Guide new team members through structured learning tracks
- Answer questions about internal documentation and processes
- Track user progress and knowledge gaps
- Reduce dependency on existing team members for onboarding
- Provide proactive reminders and personalized learning experiences

## Implementation Plan

For a comprehensive overview of the project, including architecture, workflows, and implementation steps, please see the [Implementation Plan](implementation-plan.md).

## Project Structure

- **frontend/**: ReactJS application for user interfaces
- **services/**: Backend microservices (FastAPI)
- **infrastructure/**: Docker and AWS configuration files
- **docs/**: Additional documentation

## Documentation

- [System Architecture](docs/architecture/system-architecture.md): Detailed overview of the system architecture and components
- [Services Overview](docs/services/services-overview.md): Description of each microservice and its responsibilities
- [API Documentation](docs/api/api-documentation.md): Comprehensive guide to the APIs exposed by the platform


## Core Features

- Learning Bot for guided course completion
- Onboarding Bot for Q&A about internal documentation
- Admin dashboard for managing users and knowledgebases
- Integration with TalentLMS and document sources (Wiki, Google Drive)
- Retrieval-augmented generation (RAG) for accurate answers with citations

## Running the System Locally

To run the Genie Mentor Agent system, follow these steps:

1. **Environment Variables**: The system relies on environment variables, which are expected to be present in a `.env`
```ini
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
GROQ_API_KEY_PLANNER=your-groq-api-key
GROQ_API_KEY_PLANNER_REFINER=your-groq-api-key
GROQ_API_KEY_KB=your-groq-api-key
GROQ_API_KEY_EXECUTOR=your-groq-api-key
GROQ_API_KEY_EVAL=your-groq-api-key
GROQ_API_KEY_EDITOR=your-groq-api-key
USE_OPENAI="false"
DATABASE_URL="sqlite:///./memory.db"
CHROMA_DB_PATH="/app/genie-kbdocs-v1/chroma_db"
BACKEND_URL=http://127.0.0.1:8000 # for local development
NOTION_API_KEY=your-notion-api-key
WEBRAG_LLM_DEFAULT_MODEL=llama-3.3-70b-versatile
WEBRAG_MAX_SEARCH_RESULTS=10
WEBRAG_OPENAI_API_KEY=your-openai-api-key
WEBRAG_GROQ_API_KEY=your-groq-api-key
WEBRAG_GOOGLE_API_KEY=your-google-api-key
WEBRAG_GOOGLE_CX=your-google-cx
WEBRAG_MAX_VIDEO_RESULTS=5
WEBRAG_MAX_GENERAL_RESULTS=5
WEBRAG_TOP_K=3
WEBRAG_EMBED_DEFAULT_MODEL=text-embedding-ada-002
GITHUB_MCP_TOKEN=your-github-token
GOOGLE_SERVICE_ACCOUNT_FILE="/app/secrets/promising-keep-file-here.json"
KB_PROCESSED_FILES="/app/ingestion_state/KB_processed_files_history.txt"
KB_DATA_STORAGE_DRIVE_ID=your-drive-id
```
2.  **Build & Start Docker Images**: Navigate to the root of the project and build the Docker images using the following command:
    ```bash
    DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 docker-compose up -d --build
    ```
3.  **Verify Services**: Make sure all services are running correctly. You can check the status of the containers with:
    ```bash
    docker ps
    ```
    
4. **Access Data Ingestion API**: The data ingestion API will be accessible at `http://localhost:8003/docs`,
    Ingest PDFs store in google drive using via `http://localhost:8003/docs#/default/ingest_from_drive_api_trigger_ingestion_post`

    Note: In case of any errors, see logs of `data-ingestion-service`

5. **Access Backend API**: The backend API will be accessible at `http://localhost:8000/docs`, where you can find the OpenAPI documentation and interact with the API endpoints.|

6. **Access Frontend**: http://localhost:3001/

---/app/
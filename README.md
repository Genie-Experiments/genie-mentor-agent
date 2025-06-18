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

## Running the System

To run the Genie Mentor Agent system, follow these steps:

1.  **Environment Variables**: The system relies on environment variables, which are expected to be present in a `.env` file at the root of the project. Please ensure this file is configured with the necessary variables for your setup. Refer to the [Environment Variables Setup](#environment-variables-setup) section for details.

2.  **Build Docker Images**: Navigate to the root of the project and build the Docker images using the following command:
    ```bash
    docker-compose build
    ```

3.  **Start Services**: Once the images are built, you can start all the services using Docker Compose:
    ```bash
    docker compose up
    ```

4.  **Access Backend API**: The backend API will be accessible at `http://127.0.0.1:8000/docs`, where you can find the OpenAPI documentation and interact with the API endpoints.

---

## Environment Variables Setup

The system uses environment variables for configuration and sensitive information (like API keys). These variables are loaded from a `.env` file in the project's root directory.

**Important:** The `.env` file should **never** be committed to version control (e.g., Git) as it often contains sensitive data. A `.env.example` file is provided to guide you on the required variables.

To set up your `.env` file:

1.  **Create the `.env` file**: Copy the example environment file to create your own:
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file**: Open the newly created `.env` file and replace the placeholder values with your actual configurations.

Here's an example of common variables you might need to configure in your `.env` file (your actual variables may vary based on the services used):

```ini
GROQ_API_KEY=your-groq-api-key
CHROMA_DB_PATH=/path/to/chroma_db
OPENAI_API_KEY=your-openai-api-key
NOTION_API_KEY=your-notion-api-key
NOTION_API_TOKEN=your-notion-api-token
GITHUB_MCP_TOKEN=your-github-token
DATABASE_URL="sqlite:///./memory.db"
BACKEND_URL="http://127.0.0.1:8000"
WEBRAG_LLM_DEFAULT_MODEL="llama-3.3-70b-versatile"
WEBRAG_MAX_SEARCH_RESULTS=10
WEBRAG_OPENAI_API_KEY=your-openai-api-key
WEBRAG_GROQ_API_KEY=your-groq-api-key
WEBRAG_GOOGLE_API_KEY=your-google-api-key
WEBRAG_GOOGLE_CX=your-google-cx
WEBRAG_MAX_VIDEO_RESULTS=5
WEBRAG_MAX_GENERAL_RESULTS=5
WEBRAG_TOP_K_URLS=3
WEBRAG_EMBED_DEFAULT_MODEL="text-embedding-ada-002"
WEBRAG_TOP_K=3
```
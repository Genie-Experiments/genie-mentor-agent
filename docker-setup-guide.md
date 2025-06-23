# Genie Mentor Agent Setup Guide for New Developers

Welcome to the Genie Mentor Agent project! This guide will help you set up the entire system using Docker

## Project Overview

Genie Mentor Agent is a system consisting of multiple services:

- Frontend (React + TypeScript + Vite)
- Agent Service (Python)
- Data Ingestion Service (Python)
- Integration Services
- Gateway Services for Notion and GitHub

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- 
## Quick Start with Docker

To get the entire system running with minimal configuration:

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd genie-mentor-agent
   ```

2. **Create an .env file:**

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file to include necessary API keys and configuration values.

3. **Launch the entire system:**

   ```bash
   docker-compose up -d
   ```

   This will build and start all services defined in the main docker-compose.yml file, including the frontend.

4. **Access the application:**
   - Frontend: http://localhost:3001
   - Agent Service API: http://localhost:8000
   - Data Ingestion Service: http://localhost:8003

## Frontend Development

For frontend development specifically:

1. **Run only the frontend in development mode:**

   ```bash
   cd frontend-js
   docker-compose -f docker-compose.dev.yml up
   ```

   This will start the frontend with hot-reloading at http://localhost:3001.

2. **Build the frontend for production:**
   ```bash
   cd frontend-js
   docker build -t genie-mentor-frontend .
   ```

## Working with Individual Services

### Agent Service

```bash
docker-compose up -d agent-service
```

### Data Ingestion Service

```bash
docker-compose up -d data-ingestion-service
```

### Gateway Services

```bash
docker-compose up -d notion-mcp-gateway github-mcp-gateway
```

## Development Workflow

1. **Make changes to the code** in your local environment
2. **Test in development mode** with hot-reloading
3. **Build and test in production mode** before committing
4. **Push changes** to the repository

## Troubleshooting

### Docker Issues

- **Containers not starting:** Check logs with `docker-compose logs [service-name]`
- **Port conflicts:** Verify no other services are using the configured ports
  - If you see an error like `Bind for 0.0.0.0:PORT failed: port is already allocated`, it means another process is using that port
  - To fix this, edit the docker-compose.yml file and change the host port (the first number in the port mapping)
  - For example, change `"8000:8000"` to `"8080:8000"` to map the container's port 8000 to host port 8080
  - Then access the service at the new port (e.g., http://localhost:8080 instead of http://localhost:8000)
- **Volume mount issues:** Ensure paths in docker-compose files are correct

### Frontend Issues

- **Dependencies not installing:** Run `docker-compose build --no-cache frontend`
- **Network errors:** Check if backend services are running and accessible

## Architecture Overview

- **Frontend:** React application serving the user interface
- **Agent Service:** Core business logic and AI agent functionality
- **Data Ingestion Service:** Handles importing and processing external data
- **Integration Service:** Connects with external systems and APIs
- **Gateway Services:** Protocol adaptation for external services

## Additional Resources

- Check the `/docs` directory for detailed documentation
- See `git-standards.md` for contributing guidelines
- Review `implementation-plan.md` for project roadmap

## Getting Help

If you encounter issues not covered in this guide:

1. Check existing documentation in the `docs/` directory
2. Ask team members for assistance
3. Create an issue in the project repository

Welcome to the team, and happy coding!

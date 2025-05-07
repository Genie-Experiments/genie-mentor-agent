# Genie Mentor Agent: System Architecture

## Overview

The Genie Mentor Agent platform is implemented as a set of microservices that communicate with each other through well-defined APIs. This architecture provides scalability, flexibility, and allows for independent development and deployment of components.

## Architecture Diagram

```mermaid
flowchart TD
    %% Subgraph: Frontend
    subgraph Frontend["Frontend (ReactJS + Vite + MUI/Tailwind)"]
        FE_Admin["Admin Dashboard"]
        FE_Instructor["Instructor Dashboard"]
        FE_User["User Portal"]
        LearningBotUI["Learning Bot UI (or Slackbot, platform selects one)"]
        OnboardingBotUI["Onboarding Bot UI (or Slackbot, platform selects one)"]
    end
    style Frontend fill:#e3f2fd,stroke:#2196f3,stroke-width:2px

    %% Subgraph: Backend
    subgraph Backend["Backend (FastAPI)"]
        BE["API Gateway"]
        AuthService["Auth Service"]
        UserService["User Management Service"]
        KBService["Knowledgebase Service"]
        BotService["Bot Assignment Service"]
        AgentService["Agent Orchestration Service"]
        TalentLMSService["TalentLMS Integration Service"]
    end
    style Backend fill:#fffde7,stroke:#fbc02d,stroke-width:2px

    %% Subgraph: Agents
    subgraph Agents["Agents & Memory"]
        AGENTS["Agent Service"]
        LearningBot["Learning Bot"]
        OnboardingBot["Onboarding Bot"]
        RAG["RAG Pipeline"]
        Memory["Agentic Memory"]
    end
    style Agents fill:#e8f5e9,stroke:#43a047,stroke-width:2px

    %% Subgraph: Data
    subgraph Data["Data Layer"]
        PG["Postgres"]
        VEC["PGVector"]
    end
    style Data fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px

    %% Subgraph: Cloud
    subgraph Cloud["Cloud Storage"]
        WikiDocs["Wiki Docs (Notion/Confluence/etc.)"]
        GDRIVE["Google Drive"]
    end
    style Cloud fill:#e1f5fe,stroke:#0277bd,stroke-width:2px

    %% Subgraph: MCP
    subgraph MCP["MCP Servers"]
        MCP_WIKI["MCP Server - Wiki Docs"]
        MCP_GDRIVE["MCP Server - Google Drive"]
    end
    style MCP fill:#fce4ec,stroke:#d81b60,stroke-width:2px

    %% Flows
    FE_Admin -- UI --> BE
    FE_Instructor -- UI --> BE
    FE_User -- UI --> BE
    LearningBotUI -- Conversational UI/Slackbot --> BE
    OnboardingBotUI -- Conversational UI/Slackbot --> BE

    BE -- Auth --> AuthService
    BE -- User Management --> UserService
    BE -- Knowledgebase --> KBService
    BE -- Bot Assignment --> BotService
    BE -- Agent Orchestration --> AgentService
    BE -- TalentLMS Sync --> TalentLMSService

    TalentLMSService -- Progress/Assessments --> LearningBot

    AgentService -- Start/Resume --> AGENTS
    AGENTS -- Guides/Progress --> LearningBot
    AGENTS -- Q&A --> OnboardingBot
    OnboardingBot -- RAG Query --> RAG
    RAG -- Retrieve --> Memory
    LearningBot -- Progress/Assessment --> Memory
    OnboardingBot -- Conv/Pref Memory --> Memory
    Memory -- Store/Fetch --> VEC
    VEC -- Vector Data --> PG
    UserService -- DB Ops --> PG
    KBService -- DB Ops --> PG
    BotService -- DB Ops --> PG
    AgentService -- DB Ops --> PG

    KBService -- MCP Config --> MCP_WIKI
    KBService -- MCP Config --> MCP_GDRIVE
    MCP_WIKI -- List/Fetch Docs --> WikiDocs
    MCP_GDRIVE -- List/Fetch Docs --> GDRIVE
    MCP_WIKI -- Index Docs --> KBService
    MCP_GDRIVE -- Index Docs --> KBService
```

## Microservices

1. **API Gateway**
   - Single entry point for frontend and external clients
   - Routes requests to appropriate services
   - Handles authentication and authorization
   - Provides API documentation and discovery

2. **Bot Service**
   - Implements the core agent orchestration
   - Contains both Learning Bot and Onboarding Bot implementations
   - Uses LangGraph for agent workflows
   - Consumes Memory Service for state management
   - Communicates with Data Ingestion Service for document retrieval

3. **Memory Service**
   - Manages all forms of agentic memory
   - Implements LangMem for conversation, learning progress, and preference memory
   - Provides memory persistence and retrieval
   - Optimizes memory context for agent consumption

4. **Data Ingestion Service**
   - Manages document sources via MCP connectors
   - Handles document processing, chunking, and embedding
   - Maintains vector store for semantic search
   - Implements RAG query pipeline
   - Provides admin tools for knowledgebase management

5. **Integration Service**
   - Integrates with TalentLMS for course and progress synchronization
   - Provides Slack connectors for bot delivery
   - Implements webhooks for external system notifications

## Inter-Service Communication

- **REST APIs**: For synchronous request/response patterns
- **Message Queue**: RabbitMQ for asynchronous event-driven communication
- **Service Discovery**: Using container orchestration service discovery mechanisms

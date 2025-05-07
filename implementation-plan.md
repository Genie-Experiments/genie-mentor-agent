# Genie Mentor Agent: Implementation Plan

> **Purpose**: This document provides a comprehensive and explainable roadmap for building the Genie Mentor Agent platform. It is designed to be easily understood by anyone—technical or non-technical—who wants to grasp the goals, architecture, workflows, and implementation steps for this AI-powered developer onboarding and learning solution.

---

## Overview

**Genie Mentor Agent** is a platform designed to automate the onboarding and continuous learning of developers within an organization. By leveraging AI agents, the system aims to:
- Guide new team members through structured learning tracks.
- Answer questions about internal documentation and processes.
- Track user progress and knowledge gaps.
- Reduce dependency on existing team members for onboarding.
- Provide proactive reminders and personalized learning experiences.

The platform targets three main user groups: admins, instructors, and learners. It integrates with tools like TalentLMS and supports knowledgebase sources such as Wiki Docs (Notion/Confluence) and Google Drive.

---

## Core Features & User Roles

### User Roles

| Role         | Permissions                                                                                  |
|--------------|---------------------------------------------------------------------------------------------|
| **Admin**    | Full platform control: manage users, instructors, knowledgebases, configs, MCP integration   |
| **Instructor** | Create/manage users, assign courses, manage knowledgebases (optional, configurable)         |
| **User**     | Access assigned bots, interact with learning tracks or knowledgebase, track their progress   |

Admins and instructors are responsible for setting up user accounts, assigning learning tracks or bots, and configuring the knowledgebase. Users (learners) interact with the bots to complete their onboarding or learning journey.

### Bot Types

- **Learning Bot**
  - Accessible as either a Slackbot or a custom conversational UI within the User Portal (the platform will select one approach based on feasibility and user needs).
  - Guides users through assigned learning tracks/courses.
  - Integrates with TalentLMS: frequently syncs user progress, assignments, and quiz results from TalentLMS to keep the learning state up to date.
  - Displays real-time progress, reminders, and actionable learning tasks in the UI.
  - Maintains user learning memory (progress, assessments, interaction history).

- **Onboarding Bot**
  - Accessible as either a Slackbot or a custom conversational UI within the User Portal (the platform will select one approach based on feasibility and user needs).
  - Conversational Q&A agent for internal docs (RAG over knowledgebase).
  - Provides accurate, referenced answers from internal documentation.
  - Maintains per-conversation memory and user preference memory for a personalized experience.

---

## System Architecture

**Frontend:** Built with ReactJS, Vite, and MUI/Tailwind for a modern, responsive user experience.  
**Backend:** Powered by FastAPI (Python) for robust and scalable API development.  
**Agents:** Uses Autogen for agent orchestration and retrieval-augmented generation (RAG).  
**Database:** Postgres + PGVector for structured and vectorized storage.  
**Cloud:** Integrates with Wiki Docs (Notion/Confluence), Google Drive, and AWS for storage and compute.  
**API Management:** AWS API Gateway for secure and scalable API management.
**Knowledgebase Sources:** Context is provided to the AI via MCP servers, which standardize access to various document sources.

**Detailed System Architecture :**

```mermaid
flowchart TD
    %% Subgraph: Frontend
    subgraph Frontend["Frontend (ReactJS + Vite + MUI/Tailwind)"]
        FE_Admin["Admin/Instructor Dashboard"]
        FE_User["User Panel"]
    end
    style Frontend fill:#e3f2fd,stroke:#2196f3,stroke-width:2px

    %% Subgraph: AWS
    subgraph AWS["AWS Services"]
        APIGW["AWS API Gateway"]
        AuthService["Cognito / IAM"]
    end
    style AWS fill:#FF9900,stroke:#232F3E,stroke-width:2px

    %% Subgraph: Services
    subgraph Services["Microservices (FastAPI)"]
        AgentService["Agent Service"]
        DataIngestionService["Data Ingestion Service"]
        IntegrationService["Integration Service"]
    end
    style Services fill:#fffde7,stroke:#fbc02d,stroke-width:2px

    %% Subgraph: Agents
    subgraph Agents["Autogen Components"]
        LearningBot["Learning Bot (Autogen)"]
        OnboardingBot["Onboarding Bot (Autogen)"]
        Memory["Memory Store"]
    end
    style Agents fill:#e8f5e9,stroke:#43a047,stroke-width:2px

    %% Subgraph: RAG
    subgraph RAG["RAG Pipeline"]
        Retriever["Document Retriever"]
        VectorStore["Vector Store"]
        Generator["Response Generator"]
    end
    style RAG fill:#fce4ec,stroke:#d81b60,stroke-width:2px

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
        TalentLMS["TalentLMS"]
    end
    style Cloud fill:#e1f5fe,stroke:#0277bd,stroke-width:2px

    %% Subgraph: MCP
    subgraph MCP["MCP Servers"]
        MCP_WIKI["MCP Server - Wiki Docs"]
        MCP_GDRIVE["MCP Server - Google Drive"]
    end
    style MCP fill:#fce4ec,stroke:#d81b60,stroke-width:2px

    %% Flows
    FE_Admin -- UI --> APIGW
    FE_User -- UI --> APIGW

    APIGW -- Auth --> AuthService
    APIGW -- Routes To --> AgentService
    APIGW -- Routes To --> DataIngestionService
    APIGW -- Routes To --> IntegrationService

    AgentService -- Implements --> OnboardingBot
    AgentService -- Implements --> LearningBot
    
    %% RAG Pipeline Flow
    OnboardingBot -- User Query --> Retriever
    Retriever -- Search --> VectorStore
    VectorStore -- Relevant Docs --> Generator
    Generator -- Generate Response --> OnboardingBot
    
    RAG -- Retrieve --> Memory
    OnboardingBot -- Conv/Pref Memory --> Memory
    LearningBot -- Progress/Assessment --> Memory

    IntegrationService -- TalentLMS Integration --> TalentLMS
    TalentLMS -- Course Data --> LearningBot

    DataIngestionService -- Manages --> RAG
    AgentService -- Manages --> Memory
    
    Memory -- Store/Fetch --> VEC
    VectorStore -- Vector Embeddings --> VEC
    VEC -- Vector Data --> PG
    AgentService -- DB Ops --> PG
    DataIngestionService -- DB Ops --> PG
    IntegrationService -- DB Ops --> PG

    DataIngestionService -- MCP Config --> MCP_WIKI
    DataIngestionService -- MCP Config --> MCP_GDRIVE
    MCP_WIKI -- List/Fetch Docs --> WikiDocs
    MCP_GDRIVE -- List/Fetch Docs --> GDRIVE
    MCP_WIKI -- Index Docs --> DataIngestionService
    MCP_GDRIVE -- Index Docs --> DataIngestionService

    %% Styling for key services
    classDef service fill:#fffde7,stroke:#fbc02d,stroke-width:2px,font-weight:bold;
    class AgentService,DataIngestionService,IntegrationService service;
    classDef agent fill:#e8f5e9,stroke:#43a047,stroke-width:2px,font-weight:bold;
    class LearningBot,OnboardingBot,Memory agent;
    classDef rag fill:#fce4ec,stroke:#d81b60,stroke-width:2px,font-weight:bold;
    class Retriever,VectorStore,Generator rag;
    classDef db fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px;
    class PG,VEC db;
    classDef cloud fill:#e1f5fe,stroke:#0277bd,stroke-width:2px;
    class WikiDocs,GDRIVE,TalentLMS cloud;
    classDef mcp fill:#fce4ec,stroke:#d81b60,stroke-width:2px;
    class MCP_WIKI,MCP_GDRIVE mcp;
    classDef aws fill:#FF9900,stroke:#232F3E,stroke-width:2px,font-weight:bold;
    class APIGW,AuthService aws;
```

---

## Detailed Component Breakdown

This section explains the main building blocks of the Genie Mentor Agent platform, focusing on what each part does and how they work together.

### 1. **Frontend (ReactJS + Vite + MUI/Tailwind)**
- **Admin/Instructor Dashboard:** Allows admins to manage users, instructors, knowledgebases, and platform configurations.
- **User Panel:** Where learners interact with bots, view their learning progress, and access conversation history and preferences.
- **Bot UIs:** Custom conversational interfaces for Learning Bot and Onboarding Bot, if not using Slack.

### 2. **Backend (FastAPI)**
- **Auth Service:** Handles authentication and role-based access control (RBAC) for all users.
- **Agent Service:** Implements both the Learning Bot and Onboarding Bot using Autogen, manages conversation memory, and handles agent orchestration.
- **Data Ingestion Service:** Handles document processing, chunking, embedding, and RAG query pipeline.
- **Integration Service:** Provides Slack connectors for bot delivery, TalentLMS integration, and webhook endpoints for external system notifications.

### 3. **Agent Service (Autogen)**
- **Learning Bot Agent:** Guides users through structured learning tracks, tracks progress, and manages learning memory.
- **Onboarding Bot Agent:** Answers user questions using retrieval-augmented generation (RAG) over the knowledgebase, and maintains conversation and preference memory.
- **Memory Store:** Integrated within the Agent Service, uses Postgres and PGVector for storing learning progress, conversation, and preference memory.
- **RAG Integration:** Connects with the Data Ingestion Service to retrieve relevant documents and generate answers with citations.

### 4. **Database (Postgres + PGVector)**
- **User/Role Tables:** Store user profiles, roles, and assignments.
- **Learning Progress:** Tracks user advancement through courses, quizzes, and assignments.
- **Knowledgebase Metadata:** Stores information about document sources, MCP configs, and indexing status.
- **Agent Memory:** Vector store for all agentic memory (progress, conversation, preferences).

### 5. **Cloud & MCP Integration**
- **Wiki Docs (Notion/Confluence/etc.):** Main storage for internal documentation and knowledgebase content.
- **Google Drive:** Alternative document source for knowledgebase.
- **MCP Servers:** Standardize access to external sources, making it easy to add new document repositories.
- **Admin configures MCP endpoints via dashboard:** Ensures secure and flexible integration.

---

## User Workflows

This section illustrates the main user journeys and system flows so that anyone can understand how the platform operates in practice. For each diagram below, a step-by-step textual description is provided to make the workflow clear even without visual aids.

### 1. **User Onboarding & Bot Assignment Flow**

**Textual Workflow Description:**
1. **Admin or Instructor creates a new user** in the platform, specifying their role (admin, instructor, or user).
2. **Admin or Instructor assigns the Onboarding Bot** to the new user.
3. **Platform sends a welcome notification** to the user, inviting them to log in.
4. **User logs in** and sees the Onboarding Bot has been assigned to them.
5. **User interacts with the Onboarding Bot UI or Slackbot** for Q&A about internal documentation, receiving referenced answers.
6. **All conversations and preferences are updated** in the platform for future sessions and reporting.

```mermaid
sequenceDiagram
    participant A as Admin/Instructor 🧑‍💼
    participant P as Platform 🖥️
    participant U as User 👤
    participant B as OnboardingBot UI/Slackbot 🤖

    A->>P: Create User (with role)
    A->>P: Assign Onboarding Bot and Knowledgebase
    P->>U: Send Welcome Email/Notification
    U->>P: Login
    P->>U: Show Assigned Bot
    U->>B: Start Conversation
    B->>U: Q&A, Provide References
    B->>P: Update Conversation & Preferences

```

### 2. **Agentic Memory & RAG Retrieval Flow**

**Textual Workflow Description:**
1. **User initiates a query** (question or request) for the Onboarding Bot.
2. **Onboarding Bot receives the query** along with the user's conversation ID.
3. **Bot retrieves user preferences and conversation memory** to personalize the response.
4. **Bot uses the RAG (Retrieval-Augmented Generation) pipeline** to search the knowledgebase for relevant documents.
5. **Relevant documents are retrieved and ranked** using vector search.
6. **Bot generates an answer** using the retrieved documents, providing citations for transparency.
7. **Bot responds to the user** with the answer and references.
8. **All conversation and preference memory is updated** for future context and personalization.

```mermaid
flowchart LR
    %% User Session
    UQ["User Query"]:::user
    ConvID["Conversation ID"]:::user

    %% OnboardingBot
    OB["Onboarding Bot"]:::bot
    PrefMem["User Preferences Memory"]:::memory
    ConvMem["Conversation Memory 1"]:::memory
    ConvMem2["Conversation Memory N"]:::memory

    %% RAG
    Retriever["Retriever (Autogen)"]:::rag
    KB["Knowledgebase"]:::db
    Docs["Indexed Documents"]:::db
    Citations["Citations"]:::db

    UQ --> OB
    ConvID --> ConvMem
    ConvID --> ConvMem2
    OB -- Uses --> PrefMem
    OB -- Uses --> ConvMem
    OB -- Uses --> ConvMem2
    OB -- Query --> Retriever
    Retriever -- Vector Search --> KB
    KB -- Returns --> Docs
    Docs -- Provide --> OB
    OB -- Responds with Answer & Citations --> UQ
    OB -- Updates --> ConvMem
    OB -- Updates --> ConvMem2
    OB -- Updates --> PrefMem

    classDef user fill:#e3f2fd,stroke:#1976d2,stroke-width:2px;
    classDef bot fill:#e8f5e9,stroke:#43a047,stroke-width:2px;
    classDef memory fill:#fffde7,stroke:#fbc02d,stroke-width:2px;
    classDef rag fill:#fce4ec,stroke:#d81b60,stroke-width:2px;
    classDef db fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px;
```

### 3. **Knowledgebase Creation & Document Ingestion**

**Textual Workflow Description:**
1. **Admin or Instructor creates a new knowledgebase** in the platform, specifying the MCP server and document source (e.g., Wiki Docs or Google Drive).
2. **Platform connects to the MCP server** and authenticates the connection.
3. **MCP server fetches a list of documents** from the external source.
4. **MCP server returns document metadata** to the platform.
5. **Platform indexes the documents** so they can be used for retrieval-augmented Q&A.
6. **Knowledgebase is marked as ready** and can be used by the Onboarding Bot to answer user questions.

```mermaid
sequenceDiagram
    participant Admin/Instructor as <b style="color:#1976d2;">Admin/Instructor</b>
    participant Platform as <b style="color:#fbc02d;">Platform</b>
    participant MCP_WIKI as <b style="color:#d81b60;">MCP_Server_WikiDocs</b>
    participant ExternalWiki as <b style="color:#0277bd;">Wiki Docs (Notion/Confluence/etc.)</b>
    participant KB as <b style="color:#8e24aa;">Knowledgebase</b>

    Admin/Instructor->>Platform: Create Knowledgebase, Provide MCP Config
    Platform->>MCP_WIKI: Connect & Authenticate
    MCP_WIKI->>ExternalWiki: List/Fetch Documents
    MCP_WIKI->>Platform: Return Document Metadata
    Platform->>KB: Index Documents for RAG
    KB->>Platform: Ready for Q&A
```

---

## Developer Getting Started Guide

This section provides developers with specific tasks and instructions to begin implementing the Genie Mentor Agent platform. Each task includes implementation guidance, recommended approaches, and links to relevant resources.

### 1. Setting Up Development Environment

Before starting implementation, ensure your development environment includes:

- Python 3.9+ for backend/agent development
- Node.js 18+ for frontend development
- PostgreSQL 13+ with pgvector extension
- Docker for containerization
- Docker Compose for local development
- AWS CLI configured with appropriate permissions

**Microservices Repository Structure:**
```
genie-mentor-bot/
├── services/                     # Contains all microservices
│   ├── bot-service/              # Bot Service for agent orchestration
│   │   ├── src/
│   │   │   ├── agents/           # Agent implementations
│   │   │   │   ├── learning/     # Learning Bot implementation
│   │   │   │   └── onboarding/   # Onboarding Bot implementation
│   │   │   ├── llm/              # LLM integrations
│   │   │   ├── routes/           # API routes
│   │   │   └── main.py           # Service entry point
│   │   ├── Dockerfile
│   │   └── requirements.txt      # Python dependencies
│   │
│   ├── data-ingestion-service/   # Document/Knowledge Ingestion Service
│   │   ├── src/
│   │   │   ├── connectors/       # Document source connectors
│   │   │   │   ├── mcp/          # MCP client implementation
│   │   │   │   ├── wiki/         # Wiki connectors
│   │   │   │   └── drive/        # Google Drive connector
│   │   │   ├── indexing/         # Document processing & indexing
│   │   │   ├── routes/           # API routes
│   │   │   └── main.py           # Service entry point
│   │   ├── Dockerfile
│   │   └── requirements.txt      # Python dependencies
│   │
│   ├── integration-service/      # External integrations service
│   │   ├── src/
│   │   │   ├── talentlms/        # TalentLMS integration
│   │   │   ├── slack/            # Slack integration
│   │   │   ├── routes/           # API routes
│   │   │   └── main.py           # Service entry point
│   │   ├── Dockerfile
│   │   └── requirements.txt      # Python dependencies
│   │
│   └── shared-lib/               # Shared libraries and utilities
│       ├── src/
│       │   ├── db/               # Database utilities
│       │   ├── models/           # Shared data models
│       │   ├── messaging/        # Inter-service messaging
│       │   └── utils/            # Common utilities
│       └── requirements.txt      # Python dependencies
│
├── frontend/                     # React application (unchanged)
│   ├── src/
│   │   ├── components/           # UI components
│   │   ├── pages/                # Page layouts
│   │   ├── services/             # API clients
│   │   └── contexts/             # State management
│   ├── public/                   # Static assets
│   └── package.json              # Node dependencies
│
├── infrastructure/               # Infrastructure configurations
│   ├── docker-compose.yml        # Local development setup
│   ├── aws/                      # AWS configurations
│   │   ├── api-gateway/          # API Gateway configurations
│   │   ├── cognito/              # Cognito user pool configurations
│   │   └── cloudformation/       # CloudFormation templates
│   └── terraform/                # Infrastructure as Code
│
└── docs/                         # Documentation
    ├── architecture/             # Architecture diagrams
    ├── api/                      # API documentation
    └── services/                 # Service-specific documentation
```

### 2. Microservices Architecture Overview

The Genie Mentor Agent platform is implemented as a set of microservices that communicate with each other through well-defined APIs. This architecture provides scalability, flexibility, and allows for independent development and deployment of components.

#### Key Services:

1. **AWS API Gateway**
   - Single entry point for frontend and external clients
   - Routes requests to appropriate backend services
   - Handles authentication and authorization via AWS Cognito
   - Provides API documentation and discovery
   - Manages API keys and usage plans

2. **Agent Service**
   - Implements the core agent orchestration
   - Contains both Learning Bot and Onboarding Bot implementations
   - Uses Autogen for agent workflows
   - Manages conversation memory and preference memory
   - Communicates with Data Ingestion Service for document retrieval

3. **Data Ingestion Service**
   - Manages document sources via MCP connectors
   - Handles document processing, chunking, and embedding
   - Maintains vector store for semantic search
   - Implements RAG query pipeline
   - Provides admin tools for knowledgebase management

4. **Integration Service**
   - Integrates with TalentLMS for course and progress synchronization
   - Provides Slack connectors for bot delivery
   - Implements webhooks for external system notifications

#### Inter-Service Communication:

- **REST APIs**: For synchronous request/response patterns
- **Future Enhancement**: Message Queue (RabbitMQ) for asynchronous event-driven communication (to be implemented in later phases)
- **Simple Service Discovery**: Direct service URLs configured via environment variables

### 3. Agent Implementation Tasks

The initial agent implementation will focus on the Onboarding Bot using Autogen:

#### Service-Specific Tasks:

**Agent Service Implementation**

**Task 2.5: Implement service API endpoints**
- Create RESTful API endpoints for onboarding bot interactions
- Implement basic authentication
- Set up direct communication with Data Ingestion Service
- Build health checks and monitoring

```python
# Example Agent Service API implementation to be used as a reference
from fastapi import FastAPI, Depends, HTTPException
from .agents.autogen.onboarding.agent import OnboardingBotAgent
from .auth import get_current_user
from .clients.data_client import DataIngestionServiceClient

app = FastAPI(title="Agent Service", description="Agent orchestration service for Genie Mentor Agent")

async def get_data_client():
    return DataIngestionServiceClient(base_url="http://data-ingestion-service:8082")

@app.post("/api/onboarding-bot/interact")
async def onboarding_bot_interact(
    request: BotRequest,
    current_user = Depends(get_current_user),
    data_client = Depends(get_data_client)
):
    agent = OnboardingBotAgent(
        llm=get_llm_instance(),
        tools=get_learning_tools(),
        data_client=data_client
    )
    
    response = await agent.invoke(
        user_input=request.message,
        user_id=current_user.id,
        conversation_id=request.conversation_id
    )
    
    return {"response": response}
```

**Data Ingestion Service Implementation**

**Task 2.6: Implement Data Ingestion Service API**
- Create document source management endpoints
- Implement document indexing API
- Build vector search endpoints
- Create MCP configuration management

```python
# Example Data Ingestion Service API implementation
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from .connectors.mcp import MCPClient
from .connectors.wiki import NotionConnector
from .connectors.drive import GoogleDriveConnector
from .indexing import DocumentIndexer
from .auth import validate_service_token

app = FastAPI(title="Data Ingestion Service", description="Document ingestion and RAG for Genie Mentor Agent")

# Dependency injection
def get_document_indexer():
    return DocumentIndexer(connection_string="postgresql://user:pass@postgres:5432/vectordb")

# Document source endpoints
@app.post("/api/sources")
async def create_document_source(
    source: DocumentSource,
    auth = Depends(validate_service_token)
):
    # Create document source configuration
    # Store in database
    return {"id": "generated-id", "status": "created"}

# Document indexing endpoints
@app.post("/api/sources/{source_id}/sync")
async def sync_document_source(
    source_id: str,
    auth = Depends(validate_service_token),
    indexer = Depends(get_document_indexer)
):
    # Get source config from database
    source = await get_source_by_id(source_id)
    
    # Create appropriate connector
    if source.type == "notion":
        connector = NotionConnector(api_key=source.config.api_key, database_id=source.config.database_id)
    elif source.type == "google_drive":
        connector = GoogleDriveConnector(credentials_file=source.config.credentials_path, folder_id=source.config.folder_id)
    elif source.type == "mcp":
        connector = MCPClient(endpoint=source.config.endpoint, auth_config=source.config.auth)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported source type: {source.type}")
    
    # Sync documents
    result = await connector.sync_documents(indexer)
    return {"status": "success", "documents_processed": result.count}

# Vector search endpoints
@app.post("/api/search")
async def semantic_search(
    query: SearchQuery,
    auth = Depends(validate_service_token),
    indexer = Depends(get_document_indexer)
):
    vector_store = indexer.get_vectorstore()
    results = await vector_store.asimilarity_search(
        query=query.text,
        k=query.limit or 5,
        filter=query.filters
    )
    return {
        "results": [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            } for doc in results
        ]
    }
```

### 4. Service Integration and Communication

**Task 4.1: Set up inter-service communication**
- Implement REST clients for service-to-service calls
- Set up direct service URLs via environment variables
- Create service discovery mechanism

```python
# Example REST client for inter-service communication
import aiohttp
from typing import Dict, Any, Optional

class ServiceClient:
    def __init__(self, base_url: str, service_token: Optional[str] = None):
        self.base_url = base_url
        self.service_token = service_token
    
    async def _get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.service_token:
            headers["Authorization"] = f"Bearer {self.service_token}"
        return headers
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}{path}",
                headers=await self._get_headers(),
                params=params
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    async def post(self, path: str, data: Dict[str, Any]):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}{path}",
                headers=await self._get_headers(),
                json=data
            ) as response:
                response.raise_for_status()
                return await response.json()
```

```python
# Example message queue integration (using RabbitMQ)
import aio_pika
from typing import Dict, Any, Callable, Awaitable
import json

class MessageQueue:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
        self.channel = None
    
    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.connection_string)
        self.channel = await self.connection.channel()
    
    async def publish(self, exchange: str, routing_key: str, message: Dict[str, Any]):
        if not self.channel:
            await self.connect()
        
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=routing_key
        )
    
    async def subscribe(self, queue: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        if not self.channel:
            await self.connect()
        
        queue_obj = await self.channel.declare_queue(queue, durable=True)
        
        async def process_message(message):
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    await callback(data)
                except Exception as e:
                    # Log exception
                    print(f"Error processing message: {e}")
        
        await queue_obj.consume(process_message)
```

### 5. Local Development and Deployment

**Task 5.1: Set up local development environment**
- Create Docker Compose configuration
- Configure service networking
- Set up shared database

```yaml
# Example docker-compose.yml for local development
version: '3.8'

services:
  api-gateway:
    build: ./services/api-gateway
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/geniebot
      - AGENT_SERVICE_URL=http://agent-service:8081
      - DATA_SERVICE_URL=http://data-ingestion-service:8082
      - INTEGRATION_SERVICE_URL=http://integration-service:8083
    depends_on:
      - postgres
      - agent-service
      - data-ingestion-service
      - integration-service

  agent-service:
    build: ./services/agent-service
    ports:
      - "8081:8081"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/geniebot
      - DATA_SERVICE_URL=http://data-ingestion-service:8082
      - RABBITMQ_URL=amqp://rabbitmq:5672
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - rabbitmq
      - data-ingestion-service

  data-ingestion-service:
    build: ./services/data-ingestion-service
    ports:
      - "8082:8082"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/geniebot
      - RABBITMQ_URL=amqp://rabbitmq:5672
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - rabbitmq

  integration-service:
    build: ./services/integration-service
    ports:
      - "8083:8083"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/geniebot
      - RABBITMQ_URL=amqp://rabbitmq:5672
      - TALENTLMS_API_KEY=${TALENTLMS_API_KEY}
      - TALENTLMS_DOMAIN=${TALENTLMS_DOMAIN}
    depends_on:
      - postgres
      - rabbitmq

  postgres:
    image: ankane/pgvector:latest
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=geniebot
    volumes:
      - postgres-data:/var/lib/postgresql/data

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq

volumes:
  postgres-data:
  rabbitmq-data:
```

### 6. Implementation Timeline and Dependencies

For successful implementation of the microservices architecture, follow this recommended task ordering:

1. **Week 1: Foundation & Core Services**
   - Set up microservices repository structure
   - Implement shared libraries
   - Create database schemas
   - Build Agent Service core functionality
   - Set up Docker Compose environment
   - Configure AWS API Gateway and Cognito

2. **Week 2: Agent & Data Services**
   - Implement Data Ingestion Service
   - Create RAG pipeline
   - Implement agent memory

3. **Week 3: Integration & Testing**
   - Build Integration Service
   - Implement TalentLMS integration
   - Create Slack integration
   - Implement end-to-end testing
   - Integrate services with AWS API Gateway

4. **Week 4: Frontend & Deployment**
   - Build Admin Dashboard
   - Implement User Panel
   - Create frontend integration
   - Set up CI/CD pipeline
   - Deploy to production environment

### 7. Best Practices for Microservices Implementation

- **Service Boundaries**: Clearly define each service's responsibility and minimize dependencies
- **API Contracts**: Create well-documented API contracts between services
- **Authentication**: Implement both user-facing and service-to-service authentication
- **Error Handling**: Build robust error handling and retry mechanisms for service communication
- **Logging & Monitoring**: Implement centralized logging and monitoring for all services
- **Containerization**: Use Docker for consistent environments and deployments
- **Database Access**: Each service should only access its own database tables/schemas
- **Testing**: Create unit tests, integration tests, and end-to-end tests for microservices communication
- **Documentation**: Maintain up-to-date API documentation for all services

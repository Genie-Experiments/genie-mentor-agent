# Genie Mentor Agent: Services Overview

## Overview

This document provides a detailed overview of each microservice in the Genie Mentor Agent platform, including their responsibilities, dependencies, and implementation details.

## API Gateway Service

The API Gateway serves as the single entry point for all client requests, routing them to the appropriate backend services.

### Responsibilities:
- Authentication and authorization
- Request routing
- API documentation
- Cross-Origin Resource Sharing (CORS) handling

### Implementation Details:
- Built with FastAPI
- JWT-based authentication
- Role-based access control (RBAC)
- Swagger/OpenAPI documentation

## Bot Service

The Bot Service implements the core agent orchestration for both the Learning Bot and Onboarding Bot.

### Responsibilities:
- Learning Bot implementation
- Onboarding Bot implementation
- Agent workflow orchestration
- Tool integration

### Implementation Details:
- Uses Autogen for agent workflows
- Integrates with Memory Service for state management
- Communicates with Data Ingestion Service for document retrieval
- Implements agent tools and actions

## Memory Service

The Memory Service manages all forms of agentic memory for the Genie Mentor Agent platform.

### Responsibilities:
- Conversation memory management
- Learning progress tracking
- User preference storage
- Memory context optimization

### Implementation Details:
- Uses Postgres and PGVector for memory storage
- Provides memory persistence and retrieval APIs
- Optimizes memory context for agent consumption

## Data Ingestion Service

The Data Ingestion Service manages document sources, processing, and retrieval for the Genie Mentor Agent platform.

### Responsibilities:
- Document source management
- Document processing and chunking
- Vector embedding generation
- RAG query pipeline
- Knowledgebase management

### Implementation Details:
- Integrates with MCP servers for document access
- Uses Autogen for document processing
- Implements vector search using PGVector
- Provides RAG query APIs

## Integration Service

The Integration Service handles external system integrations for the Genie Mentor Agent platform.

### Responsibilities:
- TalentLMS integration
- Slack integration
- Webhook handling
- Event notification

### Implementation Details:
- Implements TalentLMS API client
- Provides Slack Bot integration
- Uses direct API calls for service communication
- Future Enhancement: RabbitMQ for asynchronous event handling (to be implemented in later phases)
- Implements webhook endpoints for external notifications

## Shared Library

The Shared Library provides common utilities and models used across all services.

### Components:
- Database utilities
- Shared data models
- Inter-service messaging
- Common utilities

### Implementation Details:
- Reusable database connection utilities
- Pydantic models for data validation
- RabbitMQ client for messaging
- Utility functions for common operations

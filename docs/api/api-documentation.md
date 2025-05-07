# Genie Mentor Agent: API Documentation

## Overview

This document provides a comprehensive guide to the APIs exposed by the Genie Mentor Agent platform. Each service exposes its own set of RESTful APIs that can be consumed by other services or external clients.

## API Gateway Endpoints

### Authentication

- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout

### User Management

- `GET /api/users` - List all users
- `GET /api/users/{user_id}` - Get user details
- `POST /api/users` - Create a new user
- `PUT /api/users/{user_id}` - Update user details
- `DELETE /api/users/{user_id}` - Delete a user

### Agent Assignment

- `GET /api/agents` - List all available agents
- `GET /api/users/{user_id}/agents` - List agents assigned to a user
- `POST /api/users/{user_id}/agents` - Assign an agent to a user
- `DELETE /api/users/{user_id}/agents/{agent_id}` - Unassign an agent from a user

### Knowledgebase Management

- `GET /api/knowledgebases` - List all knowledgebases
- `GET /api/knowledgebases/{kb_id}` - Get knowledgebase details
- `POST /api/knowledgebases` - Create a new knowledgebase
- `PUT /api/knowledgebases/{kb_id}` - Update knowledgebase details
- `DELETE /api/knowledgebases/{kb_id}` - Delete a knowledgebase

## Agent Service Endpoints

### Learning Agent

- `POST /api/agent/learning/interact` - Interact with the Learning Agent
- `GET /api/agent/learning/progress/{user_id}` - Get user learning progress
- `POST /api/agent/learning/reminders/{user_id}` - Set learning reminders

### Onboarding Agent

- `POST /api/agent/onboarding/interact` - Interact with the Onboarding Agent
- `GET /api/agent/onboarding/history/{user_id}` - Get conversation history

## Memory Service Endpoints

### Conversation Memory

- `POST /api/memory/conversation` - Create conversation memory
- `GET /api/memory/conversation/{conversation_id}` - Get conversation memory
- `PUT /api/memory/conversation/{conversation_id}` - Update conversation memory

### Learning Progress

- `POST /api/memory/learning` - Update learning progress
- `GET /api/memory/learning/{user_id}/{course_id}` - Get learning progress

### User Preferences

- `POST /api/memory/preferences` - Create user preferences
- `GET /api/memory/preferences/{user_id}` - Get user preferences
- `PUT /api/memory/preferences/{user_id}` - Update user preferences

## Data Ingestion Service Endpoints

### Document Management

- `POST /api/documents` - Upload a document
- `GET /api/documents/{document_id}` - Get document details
- `DELETE /api/documents/{document_id}` - Delete a document

### RAG Queries

- `POST /api/rag/query` - Query the knowledgebase using RAG

### MCP Configuration

- `POST /api/mcp/config` - Configure MCP connection
- `GET /api/mcp/config/{config_id}` - Get MCP configuration
- `PUT /api/mcp/config/{config_id}` - Update MCP configuration
- `DELETE /api/mcp/config/{config_id}` - Delete MCP configuration

## Integration Service Endpoints

### TalentLMS Integration

- `POST /api/integrations/talentlms/sync` - Sync with TalentLMS
- `GET /api/integrations/talentlms/courses` - Get courses from TalentLMS
- `GET /api/integrations/talentlms/users/{user_id}/progress` - Get user progress from TalentLMS

### Slack Integration

- `POST /api/integrations/slack/message` - Send a message to Slack
- `POST /api/integrations/slack/webhook` - Receive webhook from Slack

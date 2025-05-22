# Multi-Agent Query System Implementation Details

This document outlines the implementation details for our multi-agent system designed to answer queries using two data sources:
1. Ingested knowledgebase containing PPTX files from our experiments demo
2. MCP Notion server with live data from our documentation

## System Overview

The system follows a pipeline architecture with four specialized agents:

1. **Planner Agent**
2. **Refiner Agent**
3. **RAG/Query Agent**
4. **Evaluation Agent**

Each agent will be implemented independently by different team members, with clear input/output interfaces to ensure seamless integration.

## Agent Specifications

### 1. Planner Agent

**Responsibility**: Evaluate user intent and determine which source(s) to use for answering the query.

**Input**:
- User query (string)

**Output**:
- Query plan (JSON object) containing:
  - `user_query`: Original user query
  - `query_intent`: Identified intent of the query
  - `data_sources`: Array of required data sources (`["knowledgebase"]`, `["notion"]`, or `["knowledgebase", "notion"]`)
  - `query_components`: Breaking down complex queries into sub-queries if needed
  - `execution_order`: DAG representation of query execution flow

**Implementation Details**:
- Use NLP techniques to classify query intent
- Implement a decision tree to determine appropriate data sources
- Create DAG structure for complex queries requiring multiple sources
- Handle edge cases where intent is ambiguous

**Example Output**:
```json
{
  "user_query": "What are the latest experiment results for Project ABC?",
  "query_intent": "retrieve_experiment_results",
  "data_sources": ["knowledgebase", "notion"],
  "query_components": [
    {"id": "q1", "sub_query": "experiment results Project Alpha", "source": "knowledgebase"},
    {"id": "q2", "sub_query": "latest updates Project Alpha", "source": "notion"}
  ],
  "execution_order": {
    "nodes": ["q1", "q2"],
    "edges": [],
    "aggregation": "combine_and_summarize"
  }
}
```

### 2. Refiner Agent

**Responsibility**: Review and optimize the query plan from the Planner Agent.

**Input**:
- Query plan from Planner Agent (JSON object)

**Output**:
- Refined query plan (JSON object) with the same structure as input
- Feedback message explaining refinements (if any)

**Implementation Details**:
- Check for redundancies in data source selection
- Optimize execution order in the query DAG
- Validate that all required fields are present in the plan
- Suggest additional sub-queries if plan seems incomplete
- Return the original plan if no refinements are needed

**Example Output**:
```json
{
  "refined_plan": {
    "user_query": "What are the latest experiment results for Project Alpha?",
    "query_intent": "retrieve_experiment_results",
    "data_sources": ["knowledgebase", "notion"],
    "query_components": [
      {"id": "q1", "sub_query": "experiment results Project Alpha", "source": "knowledgebase"},
      {"id": "q2", "sub_query": "latest updates Project Alpha", "source": "notion"}
    ],
    "execution_order": {
      "nodes": ["q1", "q2"],
      "edges": [],
      "aggregation": "prioritize_recent_data"
    }
  },
  "feedback": "Changed aggregation strategy to prioritize recent data since user is asking for 'latest' results."
}
```

### 3. RAG/Query Agent

**Responsibility**: Execute the query plan by retrieving information from specified sources and formulating a comprehensive answer.

**Input**:
- Refined query plan (JSON object)

**Output**:
- Query response (JSON object) containing:
  - `answer`: Formulated answer based on retrieved information
  - `sources`: List of sources used to generate the answer
  - `confidence_score`: Confidence level in the answer (0-1)

**Implementation Details**:
- Implement connectors for both knowledgebase and Notion data sources
- For knowledgebase: Use embedding-based retrieval to find relevant content from PPTX files
- For Notion: Implement MCP server API client to query documentation
- Follow the execution order specified in the DAG
- Implement various aggregation strategies for combining results
- Handle errors and timeouts gracefully

**Knowledgebase Connector**:
- Use vector database to store and query embeddings of PPTX content
- Implement semantic search functionality
- Return relevant chunks with metadata

**Notion Connector**:
- Authenticate with MCP server
- Implement pagination for large result sets
- Cache frequently accessed documentation when possible

**Example Output**:
```json
{
  "answer": "Project Alpha's latest experiment results from March 2025 show a 27% improvement in performance metrics. According to recent Notion updates, the team is preparing a follow-up experiment scheduled for next month.",
  "sources": [
    {"type": "knowledgebase", "file": "Project_Alpha_Results_2025.pptx", "slide": 12},
    {"type": "notion", "page_id": "abc123", "last_updated": "2025-05-01"}
  ],
  "confidence_score": 0.87
}
```

### 4. Evaluation Agent (Optional)

**Responsibility**: Evaluate and refine the answer from the RAG/Query Agent to ensure it meets user requirements.

**Input**:
- Query response from RAG/Query Agent (JSON object)
- Original user query (string)

**Output**:
- Final response (JSON object) containing:
  - `final_answer`: Formatted answer ready for user consumption
  - `evaluation_metrics`: Metrics used to evaluate the answer quality
  - `improvement_notes`: Notes on how the answer was improved (if applicable)

**Implementation Details**:
- Compare the answer against the original user query for relevance
- Check for completeness of the answer
- Improve formatting for better readability
- Add citations and references where appropriate
- Implement different output formats based on content type
- Flag answers for human review if confidence is below threshold

**Example Output**:
```json
{
  "final_answer": "# Project Alpha: Latest Results\n\nAccording to the March 2025 experiments, Project Alpha has achieved a **27% improvement** in performance metrics.\n\nThe team is currently preparing a follow-up experiment scheduled for June 2025.\n\n*Sources: Project Alpha Results presentation (Slide 12), Notion documentation (updated May 1, 2025)*",
  "evaluation_metrics": {
    "relevance_score": 0.92,
    "completeness_score": 0.85,
    "formatting_score": 0.95
  },
  "improvement_notes": "Added formatting for readability and included source citations."
}
```

## Runtime Architecture

To integrate these agents into a cohesive system, we'll implement using AutoGen Core following the Actor model architecture:

1. **Agent Implementation**:
   - Each agent will be subclassed from `RoutedAgent` from AutoGen Core
   - Agents will have unique identifiers of type `AgentId` and metadata of type `AgentMetadata`
   - Define message handlers using the `@message_handler()` decorator for each message type the agent needs to process

2. **Message-Based Communication**:
   - Define custom message types using dataclasses for structured communication between agents
   - Implement specific message handlers for different query tasks (planning, refining, retrieval, evaluation)
   - Use typed messages to ensure type safety and enable proper message routing

3. **Agent Runtime Management**:
   - Use `SingleThreadedAgentRuntime` for local development and testing
   - Manage agent lifecycle through the runtime rather than directly instantiating agents
   - Implement subscription mechanisms for agent communication using topics

4. **Data Source Integration**:
   - Create custom message types for knowledgebase and Notion data retrieval operations
   - Implement specialized agents that handle data source interactions
   - Use asynchronous message handling for non-blocking data retrieval operations

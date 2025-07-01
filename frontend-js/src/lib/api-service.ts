/* eslint-disable @typescript-eslint/no-explicit-any */
// Service for communicating with the backend API
const DEFAULT_BACKEND = "http://127.0.0.1:8000";

// Main response structure
export type ApiResponse = {
  trace_info: TraceInfo;
};

export interface TraceInfo { // Exporting TraceInfo
  start_time: number;
  user_query: string;
  planner_agent: PlannerAgent[];
  planner_refiner_agent: PlannerRefinerAgent[];
  executor_agent: ExecutorAgent;
  evaluation_agent: EvaluationAgent[];
  editor_agent: EditorAgent[];
  errors: any[]; // Can be refined if error structure is known
  total_time: number;
  evaluation_skipped: boolean;
  skip_reason: string | null;
  final_answer: string;
  session_id: string;
}

// Planner Agent
export interface PlannerAgent { // Exporting PlannerAgent
  plan: Plan;
  execution_time_ms: number;
  retry_count: number;
  llm_usage?: LLMUsage;
}

export interface Plan { // Exporting Plan
  user_query: string;
  query_intent: string;
  data_sources: string[];
  query_components: QueryComponent[];
  execution_order: ExecutionOrder;
  think: Think;
}

export interface QueryComponent { // Exporting QueryComponent
  id: string;
  sub_query: string;
  source: string;
}

export interface ExecutionOrder { // Exporting ExecutionOrder
  nodes: string[];
  edges: any[]; // Using 'any' for now
  aggregation: string;
}

export interface Think { // Exporting Think
  query_analysis: string;
  sub_query_reasoning: string;
  source_selection: string;
  execution_strategy: string;
}

// Planner Refiner Agent
export interface PlannerRefinerAgent { // Exporting PlannerRefinerAgent
  execution_time_ms: number;
  refinement_required: string;
  feedback_summary: string;
  feedback_reasoning: string[];
  error: any | null;
  llm_usage?: LLMUsage;
}

// Executor Agent (Handles both success and error cases)
export interface ExecutorAgent { // Exporting ExecutorAgent
  error: any | null;
  executor_answer?: string;
  all_documents?: string[];
  documents_by_source?: DocumentsBySource;
  metadata_by_source?: MetadataBySource;
  llm_usage?: LLMUsage;
  execution_time_ms?: number;
}

// Data Sources (Handles any combination of sources)
export interface DocumentsBySource { // Exporting DocumentsBySource
  knowledgebase?: string[];
  github?: string[];
  notion?: string[];
  websearch?: string[];
}

export interface MetadataBySource { // Exporting MetadataBySource
  knowledgebase?: KnowledgebaseMetadata[];
  github?: GitHubMetadata[];
  notion?: NotionMetadata[];
  websearch?: WebsearchMetadata[];
}

// --- Concrete Metadata Types ---
export interface KnowledgebaseMetadata { // Exporting KnowledgebaseMetadata
  title: string;
  source: string;
  page: number;
  document_title: string | null;
}

export interface WebsearchMetadata { // Exporting WebsearchMetadata
  title: string;
  url: string;
  description: string;
}

// --- Placeholder Metadata Types ---
export interface GitHubMetadata { // Exporting GitHubMetadata
  // Defined structure from GitHub integration
  repo_links: string[];
  repo_names: string[];
}

export interface NotionMetadata { // Exporting NotionMetadata
  // Defined structure from Notion integration
  doc_links: string[];
  doc_names: string[];
}

// LLM Usage data
export interface LLMUsage {
  model: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}

// Evaluation Agent
export interface EvaluationAgent { // Exporting EvaluationAgent
  evaluation_history: EvaluationHistory;
  attempt: number;
  llm_usage?: LLMUsage;
  execution_time_ms?: number;
}

export interface EvaluationHistory { // Exporting EvaluationHistory
  score: number;
  reasoning: string;
  error: any | null;
}

// Editor Agent
export interface EditorAgent { // Exporting EditorAgent
  editor_history: EditorHistory;
  attempt: number;
}

export interface EditorHistory { // Exporting EditorHistory
  answer: string;
  error: any | null;
  skipped: boolean;
}

/**
 * Send a query to the backend and return the response
 * @param query The user query to send to the backend
 * @param sessionId The session ID to associate with the query
 * @returns The API response as a JSON object
 */
export async function callBackend(query: string, sessionId: string = "123"): Promise<ApiResponse> {
  const endpoint = `${DEFAULT_BACKEND}/1/agent_service`;
  
  try {
    // Use the same query parameters format as the Streamlit app
    const url = new URL(endpoint);
    url.searchParams.append('query', query);
    url.searchParams.append('session_id', sessionId);

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new Error(`Server responded with ${response.status}: ${errorText}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling backend:', error);
    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
      throw new Error('Could not connect to the server. Please check your network connection or server status.');
    }
    throw error;
  }
}

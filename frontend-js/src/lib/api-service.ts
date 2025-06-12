/* eslint-disable @typescript-eslint/no-explicit-any */
// Service for communicating with the backend API
const DEFAULT_BACKEND = "http://127.0.0.1:8000";

// Create a type for the API response based on the Streamlit app
export interface ApiResponse {
  trace_info?: {
    planner_agent?: any[];
    planner_refiner_agent?: any[];
    executor_agent?: {
      combined_answer_of_sources?: string;
      metadata_by_source?: Record<string, any[]>;
    };
    evaluation_agent?: any[];
    editor_agent?: any[];
    final_answer?: string;
    total_time?: string;
  };
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
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling backend:', error);
    throw error;
  }
}

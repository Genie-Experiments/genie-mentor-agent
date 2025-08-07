// Types for the enhanced knowledge base response structure
import type { DocumentsBySource, MetadataBySource, LLMUsage } from '@/lib/api-service';

export interface KnowledgeBaseResponse {
  trace_info: {
    executor_agent: ExecutorAgentEnhanced;
    final_answer: string;
  };
}

export interface ExecutorAgentEnhanced {
  trace: TraceHop[];
  num_hops: number;
  // Keep compatibility with existing ExecutorAgent
  error?: unknown | null;
  executor_answer?: string;
  all_documents?: string[];
  documents_by_source?: DocumentsBySource;
  metadata_by_source?: MetadataBySource;
  llm_usage?: LLMUsage;
  execution_time_ms?: number;
}

// Support multiple evaluator agents with knowledge base traces
export interface EvaluatorAgentEnhanced {
  trace?: TraceHop[];
  num_hops?: number;
  // Common evaluator agent properties
  evaluation_result?: string;
  evaluation_score?: number | string;
  evaluation_history?: unknown[];
  attempt?: number;
  llm_usage?: LLMUsage;
  execution_time_ms?: number;
  error?: unknown | null;
  // Additional properties
  [key: string]: unknown;
}

export interface TraceHop {
  hop: number | "final";
  sub_questions?: SubQuestion[];
  generator?: string; // For final hop
  global_memory?: string[];
  local_memory?: LocalMemoryItem[];
  reasoner_output?: ReasonerOutput;
}

export interface SubQuestion {
  sub_question: string;
  retrieved_docs: RetrievedDocument[];
  global_summary: string;
  local_summary: string;
}

export interface RetrievedDocument {
  content: string;
  metadata: DocumentMetadata;
}

export interface DocumentMetadata {
  section?: string;
  page?: number;
  source: string;
}

export interface LocalMemoryItem {
  sub_question: string;
  response: string;
}

export interface ReasonerOutput {
  sufficient: boolean;
  required_documents: string[];
  documents_in_context: string[];
  reasoning: string;
  next_sub_questions: string[];
}

// UI Component Props for Research Tab Integration
export interface KnowledgeBaseDisplayProps {
  executorAgent: ExecutorAgentEnhanced;
  finalAnswer?: string;
  onViewDetails?: (agent: ExecutorAgentEnhanced) => void;
}

export interface EvaluatorKnowledgeBaseProps {
  evaluators: EvaluatorAgentEnhanced[];
  onViewDetails?: (evaluator: EvaluatorAgentEnhanced) => void;
}

export interface TraceDisplayProps {
  trace: TraceHop[];
  numHops: number;
  agentType: 'executor' | 'evaluator';
  agentIndex?: number;
}

export interface HopCardProps {
  hop: TraceHop;
  isExpanded: boolean;
  onToggle: () => void;
  hopIndex?: number;
}

export interface SubQuestionCardProps {
  subQuestion: SubQuestion;
  isExpanded: boolean;
  onToggle: () => void;
  questionIndex?: number;
}

export interface DocumentCardProps {
  document: RetrievedDocument;
  index: number;
}

export interface ReasonerOutputCardProps {
  reasonerOutput: ReasonerOutput;
}

export interface MemoryDisplayProps {
  globalMemory?: string[];
  localMemory?: LocalMemoryItem[];
}

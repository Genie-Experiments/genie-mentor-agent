import type {
  TraceInfo,
  PlannerAgent,
  PlannerRefinerAgent,
  ExecutorAgent,
  EvaluationAgent,
  LLMUsage,
} from '@/lib/api-service';

export interface ResearchTabProps {
  traceInfo: TraceInfo;
}

export interface LLMUsageDisplayProps {
  llmUsage?: LLMUsage;
  executionTimeMs?: number;
}

export interface KeyValueRowProps {
  keyText: string;
  value?: string | number | null | string[];
  showBatch?: boolean;
  index?: number;
}

export interface AgentSectionProps {
  title: string;
  agents: (PlannerAgent | PlannerRefinerAgent | ExecutorAgent | EvaluationAgent)[];
  onViewDetails?: (agent: PlannerAgent | PlannerRefinerAgent | ExecutorAgent | EvaluationAgent) => void;
  viewDetailsText?: string;
}

export interface PlannerAgentSectionProps {
  planners: PlannerAgent[];
  onViewDetails: (planner: PlannerAgent) => void;
}

export interface RefinerAgentSectionProps {
  refiners: PlannerRefinerAgent[];
}

export interface ExecutorAgentSectionProps {
  executor: ExecutorAgent;
  onViewDetails: (executor: ExecutorAgent) => void;
}

export interface EvaluatorAgentSectionProps {
  evaluators: EvaluationAgent[];
  onViewDetails: (evaluator: EvaluationAgent) => void;
}

export interface QueryComponentProps {
  components: Array<{
    id: string;
    sub_query: string;
    source: string;
  }>;
}

export interface ViewDetailsButtonProps {
  onClick: () => void;
  text: string;
}

export interface SeparatorProps {
  style?: React.CSSProperties;
}

export interface ResearchModalState {
  plannerVisible: boolean;
  plannerContent: string;
  executorVisible: boolean;
  executorContent: string;
  evaluatorVisible: boolean;
  evaluatorContent: string;
}

export interface UseResearchModalsReturn {
  modalState: ResearchModalState;
  openPlannerModal: (planner: PlannerAgent) => void;
  closePlannerModal: () => void;
  openExecutorModal: (executor: ExecutorAgent) => void;
  closeExecutorModal: () => void;
  openEvaluatorModal: (evaluator: EvaluationAgent) => void;
  closeEvaluatorModal: () => void;
}

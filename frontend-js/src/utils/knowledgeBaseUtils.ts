import type { ExecutorAgent } from '@/lib/api-service';
import type { ExecutorAgentEnhanced, EvaluatorAgentEnhanced } from '@/types/knowledgeBaseTypes';

/**
 * Utility function to check if the response contains knowledge base data
 */
export const isKnowledgeBaseResponse = (
  executorAgent: ExecutorAgent | ExecutorAgentEnhanced
): executorAgent is ExecutorAgentEnhanced => {
  const enhanced = executorAgent as ExecutorAgentEnhanced;
  return !!(enhanced.trace && enhanced.num_hops);
};

/**
 * Utility function to check if evaluator has knowledge base data
 */
export const isEvaluatorKnowledgeBase = (
  evaluator: EvaluatorAgentEnhanced
): boolean => {
  return !!(evaluator.trace && evaluator.num_hops);
};

/**
 * Utility function to check if the response should show the simplified answer view
 */
export const shouldShowKnowledgeBaseView = (
  executorAgent: ExecutorAgent | ExecutorAgentEnhanced
): boolean => {
  return isKnowledgeBaseResponse(executorAgent);
};

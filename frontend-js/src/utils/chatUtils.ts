import { v4 as uuidv4 } from 'uuid';
import type { ApiResponse } from '../lib/api-service';
import type { ConversationItem } from '@/types/chatTypes';
import { ERROR_MESSAGES } from '@/constant/chatTheme';

/**
 * Generates a unique ID for conversation items
 */
export const generateId = (): string => {
  return uuidv4();
};

/**
 * Creates a new conversation item
 */
export const createConversationItem = (question: string): ConversationItem => ({
  id: generateId(),
  question: question.trim(),
  isLoading: true,
  error: null,
  timestamp: new Date(),
});

/**
 * Extracts error message from API response
 */
export const extractErrorMessage = (response: ApiResponse): string => {
  return response.user_message || 
         response.message || 
         ERROR_MESSAGES.default;
};

/**
 * Checks if the response should show simplified answer
 */
export const shouldShowSimplifiedAnswer = (response: ApiResponse): boolean => {
  const traceInfo = response.trace_info;
  
  // Check for greeting detection
  if (traceInfo.skip_reason?.includes('Greeting detected')) {
    return true;
  }
  
  // Check if all agents are null/empty
  const hasNoAgents = !traceInfo.planner_agent &&
    !traceInfo.executor_agent &&
    (!traceInfo.evaluation_agent || traceInfo.evaluation_agent.length === 0) &&
    (!traceInfo.editor_agent || traceInfo.editor_agent.length === 0);
    
  return hasNoAgents;
};

/**
 * Updates a conversation item at a specific index
 */
export const updateConversationItem = (
  items: ConversationItem[], 
  index: number, 
  updates: Partial<ConversationItem>
): ConversationItem[] => {
  if (index < 0 || index >= items.length) {
    return items;
  }
  
  const updatedItems = [...items];
  updatedItems[index] = { ...updatedItems[index], ...updates };
  return updatedItems;
};

/**
 * Validates if a question is valid for processing
 */
export const isValidQuestion = (question: string): boolean => {
  return Boolean(question && question.trim() !== '');
};

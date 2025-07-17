import { useEffect, useCallback } from 'react';
import { useChatState } from './useChatState';
import { useApiCall } from './useApiCall';
import { isValidQuestion } from '../utils/chatUtils';
import type { ChatProps } from '@/types/chatTypes';

export interface UseChatReturn {
  state: ReturnType<typeof useChatState>['state'];
  isProcessing: boolean;
}

export const useChat = ({ 
  question, 
  questionId = 0, 
  onLoadingStateChange 
}: ChatProps): UseChatReturn => {
  const { state, addQuestion, updateResponse, updateError } = useChatState();
  const { callApi } = useApiCall();
  
  const isProcessing = state.isLoading;

  useEffect(() => {
    if (onLoadingStateChange) {
      onLoadingStateChange(isProcessing);
    }
  }, [isProcessing, onLoadingStateChange]);
  
  const processQuestion = useCallback(async (questionText: string) => {
    if (!isValidQuestion(questionText)) return;
    addQuestion(questionText);
    
    try {
      const response = await callApi(questionText);
      updateResponse(response);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      updateError(errorMessage);
    }
  }, [addQuestion, callApi, updateResponse, updateError]);
  
  useEffect(() => {
    if (isValidQuestion(question)) {
      processQuestion(question);
    }
  }, [question, questionId, processQuestion]);
  
  return {
    state,
    isProcessing,
  };
};

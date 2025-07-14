import { useCallback, useRef } from 'react';
import { callBackend } from '../lib/api-service';
import type { ApiResponse } from '../lib/api-service';
import { ERROR_MESSAGES } from '@/constant/chatTheme';

export interface UseApiCallReturn {
  callApi: (question: string) => Promise<ApiResponse>;
  cancelRequest: () => void;
}

export const useApiCall = (): UseApiCallReturn => {
  const abortControllerRef = useRef<AbortController | null>(null);
  
  const callApi = useCallback(async (question: string): Promise<ApiResponse> => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    
    try {
      const response = await callBackend(question);
      return response;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request was cancelled');
      }
      
      console.error('API call failed:', error);
      throw new Error(ERROR_MESSAGES.networkError);
    } finally {
      abortControllerRef.current = null;
    }
  }, []);
  
  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);
  
  return {
    callApi,
    cancelRequest,
  };
};

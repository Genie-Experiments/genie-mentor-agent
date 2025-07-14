import { useReducer, useCallback } from 'react';
import { createConversationItem, updateConversationItem, extractErrorMessage } from '../utils/chatUtils';
import type { ApiResponse } from '../lib/api-service';
import type { ChatAction, ChatState } from '@/types/chatTypes';

const initialState: ChatState = {
  conversationHistory: [],
  isLoading: false,
  error: null,
  apiResponse: null,
};

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_QUESTION': {
      if (!action.payload?.question) return state;
      
      const newItem = createConversationItem(action.payload.question);
      return {
        ...state,
        conversationHistory: [...state.conversationHistory, newItem],
        isLoading: true,
        error: null,
        apiResponse: null,
      };
    }
    
    case 'UPDATE_RESPONSE': {
      if (!action.payload?.response) return state;
      
      const response = action.payload.response;
      const lastIndex = state.conversationHistory.length - 1;
      
      if (lastIndex < 0) return state;
      
      let updatedHistory;
      if (response.error === true) {
        const errorMessage = extractErrorMessage(response);
        updatedHistory = updateConversationItem(state.conversationHistory, lastIndex, {
          isLoading: false,
          error: errorMessage,
          apiResponse: response,
        });
      } else {
        updatedHistory = updateConversationItem(state.conversationHistory, lastIndex, {
          answer: response.trace_info.final_answer,
          apiResponse: response,
          isLoading: false,
          error: null,
        });
      }
      
      return {
        ...state,
        conversationHistory: updatedHistory,
        isLoading: false,
        apiResponse: response,
      };
    }
    
    case 'UPDATE_ERROR': {
      if (!action.payload?.error) return state;
      
      const lastIndex = state.conversationHistory.length - 1;
      let updatedHistory = state.conversationHistory;
      
      if (lastIndex >= 0) {
        updatedHistory = updateConversationItem(state.conversationHistory, lastIndex, {
          isLoading: false,
          error: action.payload.error,
        });
      }
      
      return {
        ...state,
        conversationHistory: updatedHistory,
        isLoading: false,
        error: action.payload.error,
      };
    }
    
    case 'SET_LOADING': {
      return {
        ...state,
        isLoading: action.payload?.isLoading ?? false,
      };
    }
    
    case 'RESET_STATE': {
      return initialState;
    }
    
    default:
      return state;
  }
}

export interface UseChatStateReturn {
  state: ChatState;
  addQuestion: (question: string) => void;
  updateResponse: (response: ApiResponse) => void;
  updateError: (error: string) => void;
  setLoading: (isLoading: boolean) => void;
  resetState: () => void;
}

export const useChatState = (): UseChatStateReturn => {
  const [state, dispatch] = useReducer(chatReducer, initialState);
  
  const addQuestion = useCallback((question: string) => {
    dispatch({ type: 'ADD_QUESTION', payload: { question } });
  }, []);
  
  const updateResponse = useCallback((response: ApiResponse) => {
    dispatch({ type: 'UPDATE_RESPONSE', payload: { response } });
  }, []);
  
  const updateError = useCallback((error: string) => {
    dispatch({ type: 'UPDATE_ERROR', payload: { error } });
  }, []);
  
  const setLoading = useCallback((isLoading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: { isLoading } });
  }, []);
  
  const resetState = useCallback(() => {
    dispatch({ type: 'RESET_STATE' });
  }, []);
  
  return {
    state,
    addQuestion,
    updateResponse,
    updateError,
    setLoading,
    resetState,
  };
};

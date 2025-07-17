import type { ApiResponse } from "@/lib/api-service";


export interface ConversationItem {
  id: string;
  question: string;
  answer?: string;
  apiResponse?: ApiResponse;
  isLoading: boolean;
  error: string | null;
  timestamp: Date;
}

export interface ChatState {
  conversationHistory: ConversationItem[];
  isLoading: boolean;
  error: string | null;
  apiResponse: ApiResponse | null;
}

export interface ChatProps {
  question: string;
  questionId?: number;
  onLoadingStateChange?: (isLoading: boolean) => void;
}

export interface MessageItemProps {
  item: ConversationItem;
  index: number;
}

export interface ErrorDisplayProps {
  error: string;
  className?: string;
}

export interface LoadingIndicatorProps {
  message?: string;
  className?: string;
}

export type ChatActionType = 
  | 'ADD_QUESTION'
  | 'UPDATE_RESPONSE'
  | 'UPDATE_ERROR'
  | 'SET_LOADING'
  | 'RESET_STATE';

export interface ChatAction {
  type: ChatActionType;
  payload?: {
    question?: string;
    questionId?: number;
    response?: ApiResponse;
    error?: string;
    conversationItem?: ConversationItem;
    isLoading?: boolean;
  };
}

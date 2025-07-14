import React, { useRef } from 'react';
import { useChat } from '../../hooks/useChat';
import { useAutoScroll } from '../../hooks/useAutoScroll';
import { ChatContainer, ConversationHistory, LoadingIndicator, ErrorDisplay } from './components';
import './components/scroll-behavior.css';
import type { ChatProps } from '@/types/chatTypes';

const Chat: React.FC<ChatProps> = ({ question, questionId = 0, onLoadingStateChange }) => {
  const chatAreaRef = useRef<HTMLDivElement>(null);
  const { state, isProcessing } = useChat({ question, questionId, onLoadingStateChange });

  useAutoScroll(chatAreaRef, [state.conversationHistory, isProcessing, state.apiResponse]);

  const hasConversations = state.conversationHistory.length > 0;
  const showGlobalError = state.error && !state.apiResponse && !hasConversations;
  const showGlobalLoading = isProcessing && !hasConversations;

  return (
    <ChatContainer chatAreaRef={chatAreaRef}>
      <ConversationHistory conversations={state.conversationHistory} />
      {showGlobalLoading && <LoadingIndicator />}
      {showGlobalError && state.error && <ErrorDisplay error={state.error} />}
    </ChatContainer>
  );
};

export default Chat;

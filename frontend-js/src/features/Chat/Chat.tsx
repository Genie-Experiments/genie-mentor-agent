import React, { useState, useRef, useEffect } from 'react';
import { callBackend } from '../../lib/api-service';
import type { ApiResponse } from '../../lib/api-service';
import { TabsContainer, QuestionBadge, AnswerTab, ResearchTab, SourcesTab } from './components';
import './components/scroll-behavior.css';
import { useAutoScroll } from './hooks/useAutoScroll';

interface ChatProps {
  question: string;
  questionId?: number; // Add an optional identifier to track question changes
  onLoadingStateChange?: (isLoading: boolean) => void;
}

interface ConversationItem {
  question: string;
  answer?: string;
  apiResponse?: ApiResponse;
  isLoading?: boolean;
  error?: string | null;
}

const Chat: React.FC<ChatProps> = ({ question, questionId = 0, onLoadingStateChange }) => {
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationHistory, setConversationHistory] = useState<ConversationItem[]>([]);
  const chatAreaRef = useRef<HTMLDivElement>(null);

  // Use our custom auto-scroll hook to ensure scrolling happens even when cursor is not in chat area
  useAutoScroll(chatAreaRef, [conversationHistory, isLoading, apiResponse]);

  // Update parent component's loading state when our loading state changes
  useEffect(() => {
    if (onLoadingStateChange) {
      onLoadingStateChange(isLoading);
    }
  }, [isLoading, onLoadingStateChange]);

  // Process a new question when it arrives
  useEffect(() => {
    if (question && question.trim() !== '') {
      // Add the new question to conversation history
      const newConversationItem: ConversationItem = {
        question: question,
        isLoading: true,
        error: null,
      };

      setConversationHistory((prev) => [...prev, newConversationItem]);
      setIsLoading(true);
      setError(null);
      setApiResponse(null);

      // Start the API call
      const fetchResponse = async () => {
        try {
          const responseData = await callBackend(question);
          setApiResponse(responseData);
          // Update the last conversation item with the response
          setConversationHistory((prev) => {
            const updated = [...prev];
            const lastIndex = updated.length - 1;

            if (lastIndex >= 0) {
              updated[lastIndex] = {
                ...updated[lastIndex],
                answer: responseData.trace_info.final_answer,
                apiResponse: responseData,
                isLoading: false,
                error: null,
              };
            }

            return updated;
          });
        } catch (err) {
          setError('Failed to fetch response from the backend.');
          console.error(err);

          // Update conversation with error
          setConversationHistory((prev) => {
            const updated = [...prev];
            const lastIndex = updated.length - 1;

            if (lastIndex >= 0) {
              updated[lastIndex] = {
                ...updated[lastIndex],
                isLoading: false,
                error: 'Failed to fetch response from the backend.',
              };
            }

            return updated;
          });
        }

        setIsLoading(false);
      };

      fetchResponse();
    }
  }, [question, questionId]); // Add questionId to dependencies to react to the same question text being asked again
  return (
    <div className="flex w-full justify-center">
      {' '}
      <div
        ref={chatAreaRef}
        className="auto-scroll-chat flex w-full max-w-[760px] flex-col items-start px-4 pt-8"
        style={{
          maxHeight: 'calc(100vh - 150px)',
        }}
      >
        {/* Display conversation history */}
        <div className="w-full">
          {conversationHistory.map((item, index) => (
            <div key={index} className="mb-10">
              {/* Question section */}
              <QuestionBadge
                question={item.question}
                isLoading={item.isLoading || false}
                error={item.error || null}
              />

              {/* Answer section with tabs if we have a response */}
              {item.apiResponse && (
                <div className="mt-6">
                  <TabsContainer
                    defaultValue="answer"
                    answerContent={
                      <AnswerTab
                        finalAnswer={item.apiResponse.trace_info.final_answer}
                        executorAgent={item.apiResponse.trace_info.executor_agent}
                      />
                    }
                    sourcesContent={
                      <SourcesTab executorAgent={item.apiResponse.trace_info.executor_agent} />
                    }
                    traceContent={<ResearchTab traceInfo={item.apiResponse.trace_info} />}
                  />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Current question loading indicator */}
        {isLoading && !conversationHistory.length && (
          <div className="my-4 flex w-full items-center justify-center">
            <div className="mr-2 h-5 w-5 animate-spin rounded-full border-2 border-[#00A599] border-t-transparent"></div>
            <span className="font-['Inter'] text-[16px] text-[#002835]">Processing...</span>
          </div>
        )}

        {/* Global error message */}
        {error && !apiResponse && !conversationHistory.length && (
          <div className="mt-4 w-full rounded-lg border border-red-200 bg-red-50 p-3 text-red-600">
            {error}
          </div>
        )}
        {/* Add some bottom spacing for the last item */}
        {conversationHistory.length > 0 && (
          <div className="w-full py-8">{/* Empty div for spacing */}</div>
        )}
      </div>
    </div>
  );
};

export default Chat;

import React, { useState, useRef, useEffect } from 'react';
import { callBackend } from '../../lib/api-service';
import type { ApiResponse } from '../../lib/api-service';
import { TabsContainer, QuestionBadge, AnswerTab, ResearchTab, SourcesTab } from './components';

interface ChatProps {
  question: string;
}

const Chat: React.FC<ChatProps> = ({ question }) => {
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (question) {
      const fetchResponse = async () => {
        setIsLoading(true);
        setError(null);
        setApiResponse(null);
        try {
          const responseData = await callBackend(question);
          setApiResponse(responseData);
          if (chatAreaRef.current) {
            chatAreaRef.current.scrollTop = 0;
          }
        } catch (err) {
          setError('Failed to fetch response from the backend.');
          console.error(err);
        }
        setIsLoading(false);
      };
      fetchResponse();
    }
  }, [question]);

  return (
    <div className="flex w-full justify-center">
      <div className="flex w-full max-w-[760px] flex-col items-start px-4 pt-8">
        {question && (
          <QuestionBadge
            question={question}
            isLoading={isLoading && !apiResponse}
            error={error && !apiResponse ? error : null}
          />
        )}
        {isLoading && !apiResponse && <p className="mt-4">Loading response...</p>}
        {error && !apiResponse && <p className="mt-4 text-red-500">{error}</p>}{' '}
        {apiResponse && (
          <>
            <TabsContainer
              defaultValue="answer"
              answerContent={
                <AnswerTab
                  finalAnswer={apiResponse.trace_info.final_answer}
                  executorAgent={apiResponse.trace_info.executor_agent}
                />
              }
              sourcesContent={<SourcesTab executorAgent={apiResponse.trace_info.executor_agent} />}
              traceContent={<ResearchTab traceInfo={apiResponse.trace_info} />}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default Chat;

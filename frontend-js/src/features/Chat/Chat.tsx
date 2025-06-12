import React, { useState, useRef, useEffect } from 'react';
import { mockAgentResponses } from '../../mocks/api-response';
import { callBackend } from '../../lib/api-service';
import { 
  TabsContainer, 
  QuestionBadge, 
  AnswerTab, 
  ResearchTab, 
  SourcesTab, 
  ResponseList 
} from './components';

const TABS = ['Answer', 'Research', 'Sources'];

interface ChatProps {
  onQuestionSubmit: (question: string) => void;
  question: string;
}

const Chat: React.FC<ChatProps> = ({ onQuestionSubmit, question }) => {  const [showBadge, setShowBadge] = useState(true);
  const [responses, setResponses] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (responses.length > 0) {
      setShowBadge(true);
      if (chatAreaRef.current) {
        chatAreaRef.current.scrollTop = 0;
      }
    }
  }, [responses]);

  useEffect(() => {
    if (question && question.trim() !== '') {
      setShowBadge(true);
      setIsLoading(true);
      setError(null);
      
      callBackend(question)
        .then(response => {
          console.log('API Response:', response);
          setResponses((prev) => [
            response.trace_info?.final_answer || `Response to: ${question}`,
            ...prev,
          ]);
        })
        .catch(err => {
          console.error('Error fetching response:', err);
          setError('Failed to get a response. Please try again.');
          setResponses((prev) => [
            'Error: Failed to get a response. Please try again.',
            ...prev,
          ]);
        })
        .finally(() => {
          setIsLoading(false);
        });
      
      onQuestionSubmit(question);
    }
  }, [question, onQuestionSubmit]);return (
    <div className="w-full flex justify-center">
      <div className="max-w-[760px] w-full flex flex-col items-start px-4 pt-8">
        
        {showBadge && <QuestionBadge question={question} isLoading={isLoading} error={error} />}
        <div ref={chatAreaRef} className="w-full flex flex-col"></div>
          <TabsContainer tabs={TABS}>
            {(activeTab) => {
              switch (activeTab) {
                case 'Answer':
                return <AnswerTab finalAnswer={mockAgentResponses.final_answer} />;
              case 'Research':
                return <ResearchTab />;
              case 'Sources':
                return <SourcesTab />;
              default:
                return null;
            }
          }}
        </TabsContainer>
        
        {/* User Responses Section */}
        <ResponseList responses={responses} />
      </div>
    </div>
  );
};

export default Chat;

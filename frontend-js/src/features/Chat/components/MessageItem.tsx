import React from 'react';
import { shouldShowSimplifiedAnswer } from '../../../utils/chatUtils';
import { QuestionBadge, TabsContainer, AnswerTab, ResearchTab, SourcesTab } from './';
import ErrorDisplay from './ErrorDisplay';
import type { MessageItemProps } from '@/types/chatTypes';
import { CHAT_THEME, UI_TEXT } from '@/constant/chatTheme';

const MessageItem: React.FC<MessageItemProps> = ({ item }) => {
  const renderAnswer = () => {
    if (!item.apiResponse || item.error) return null;

    const showSimplified = shouldShowSimplifiedAnswer(item.apiResponse);

    if (showSimplified) {
      return (
        <div className="mt-6">
          <h3
            className="mb-2 uppercase opacity-40"
            style={{
              fontFamily: CHAT_THEME.typography.fontFamily,
              fontSize: CHAT_THEME.typography.fontSize.md,
              fontWeight: CHAT_THEME.typography.fontWeight.medium,
              color: CHAT_THEME.colors.text.primary,
            }}
          >
            {UI_TEXT.answer}
          </h3>
          <div className="whitespace-pre-wrap">{item.apiResponse.trace_info.final_answer}</div>
        </div>
      );
    }

    return (
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
            <SourcesTab executorAgent={item.apiResponse.trace_info.executor_agent || {}} />
          }
          traceContent={<ResearchTab traceInfo={item.apiResponse.trace_info} />}
        />
      </div>
    );
  };

  return (
    <div className="mb-10">
      <QuestionBadge
        question={item.question}
        isLoading={item.isLoading}
        error={null} // Handle errors separately
      />

      {renderAnswer()}

      {item.error && <ErrorDisplay error={item.error} />}
    </div>
  );
};

export default React.memo(MessageItem);

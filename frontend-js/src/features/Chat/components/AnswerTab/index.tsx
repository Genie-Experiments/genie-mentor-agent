import React, { useMemo } from 'react';
import ContextModal from '../ContextModal';
import { TopSourcesSection } from './TopSourcesSection';
import { ContextSection } from './ContextSection';
import { AnswerSection } from './AnswerSection';
import '../markdown-styles.css';
import type { AnswerTabProps } from '@/types/AnswerTabTypes';
import { extractContexts, extractTopSources } from '@/utils/answerTabUtils';
import { useContextModal } from '@/hooks/useContextModal';

const AnswerTab: React.FC<AnswerTabProps> = ({ finalAnswer, executorAgent }) => {
  const { modalState, openModal, closeModal } = useContextModal(executorAgent);

  const topSources = useMemo(() => extractTopSources(executorAgent), [executorAgent]);
  const contexts = useMemo(() => extractContexts(executorAgent), [executorAgent]);

  return (
    <div className="flex w-full flex-col gap-8">
      <TopSourcesSection sources={topSources} />
      <ContextSection contexts={contexts} onContextClick={openModal} />
      <ContextModal
        isVisible={modalState.isVisible}
        title={modalState.title}
        content={modalState.content}
        onClose={closeModal}
      />
      <AnswerSection
        finalAnswer={finalAnswer}
        executorAgent={executorAgent}
        onCitationClick={openModal}
      />
    </div>
  );
};

export default AnswerTab;

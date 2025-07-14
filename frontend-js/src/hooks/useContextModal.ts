import type { ExecutorAgent } from '@/lib/api-service';
import type { ContextModalState } from '@/types/AnswerTabTypes';
import { getContextByIndex } from '@/utils/answerTabUtils';
import { useState, useCallback } from 'react';

/**
 * Hook to manage context modal state and actions
 */
export const useContextModal = (executorAgent?: ExecutorAgent) => {
  const [modalState, setModalState] = useState<ContextModalState>({
    isVisible: false,
    title: '',
    content: '',
  });

  const openModal = useCallback((index: number) => {
    console.log(`Citation clicked: using array index: ${index}`);
    
    const contextData = getContextByIndex(executorAgent, index);
    if (!contextData) return;

    setModalState({
      isVisible: true,
      title: contextData.title,
      content: contextData.content,
    });
  }, [executorAgent]);

  const closeModal = useCallback(() => {
    setModalState(prev => ({
      ...prev,
      isVisible: false,
    }));
  }, []);

  return {
    modalState,
    openModal,
    closeModal,
  };
};

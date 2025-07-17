import { useState } from 'react';
import type { UseSourcesModalReturn, SourcesModalState } from '@/types/SourcesTabTypes';

export const useSourcesModal = (): UseSourcesModalReturn => {
  const [modalState, setModalState] = useState<SourcesModalState>({
    isVisible: false,
    title: '',
    content: '',
  });

  const openModal = (title: string, content: string) => {
    setModalState({
      isVisible: true,
      title,
      content,
    });
  };

  const closeModal = () => {
    setModalState(prev => ({
      ...prev,
      isVisible: false,
    }));
  };

  return {
    modalState,
    openModal,
    closeModal,
  };
};

import { useState } from 'react';
import type {
  PlannerAgent,
  ExecutorAgent,
  EvaluationAgent,
} from '@/lib/api-service';
import type { UseResearchModalsReturn, ResearchModalState } from '@/types/ResearchTabTypes';
import {
  formatPlannerDetailedResponse,
  formatExecutorDetailedResponse,
  formatEvaluatorDetailedResponse,
} from '@/utils/researchTabUtils';

export const useResearchModals = (): UseResearchModalsReturn => {
  const [modalState, setModalState] = useState<ResearchModalState>({
    plannerVisible: false,
    plannerContent: '',
    executorVisible: false,
    executorContent: '',
    evaluatorVisible: false,
    evaluatorContent: '',
  });

  const openPlannerModal = (planner: PlannerAgent) => {
    const content = formatPlannerDetailedResponse(planner);
    setModalState(prev => ({
      ...prev,
      plannerVisible: true,
      plannerContent: content,
    }));
  };

  const closePlannerModal = () => {
    setModalState(prev => ({
      ...prev,
      plannerVisible: false,
    }));
  };

  const openExecutorModal = (executor: ExecutorAgent) => {
    const content = formatExecutorDetailedResponse(executor);
    setModalState(prev => ({
      ...prev,
      executorVisible: true,
      executorContent: content,
    }));
  };

  const closeExecutorModal = () => {
    setModalState(prev => ({
      ...prev,
      executorVisible: false,
    }));
  };

  const openEvaluatorModal = (evaluator: EvaluationAgent) => {
    const content = formatEvaluatorDetailedResponse(evaluator);
    setModalState(prev => ({
      ...prev,
      evaluatorVisible: true,
      evaluatorContent: content,
    }));
  };

  const closeEvaluatorModal = () => {
    setModalState(prev => ({
      ...prev,
      evaluatorVisible: false,
    }));
  };

  return {
    modalState,
    openPlannerModal,
    closePlannerModal,
    openExecutorModal,
    closeExecutorModal,
    openEvaluatorModal,
    closeEvaluatorModal,
  };
};

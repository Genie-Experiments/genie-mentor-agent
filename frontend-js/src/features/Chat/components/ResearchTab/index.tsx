import React from 'react';
import ContextModal from '../ContextModal';
import { PlannerAgentSection } from './PlannerAgentSection';
import { RefinerAgentSection } from './RefinerAgentSection';
import { ExecutorAgentSection } from './ExecutorAgentSection';
import { EvaluatorAgentSection } from './EvaluatorAgentSection';
import { Separator } from './Separator';
import { useResearchModals } from '@/hooks/useResearchModals';
import { MODAL_TITLES } from '@/constant/researchTab';
import type { ResearchTabProps } from '@/types/ResearchTabTypes';

const ResearchTab: React.FC<ResearchTabProps> = ({ traceInfo }) => {
  const {
    modalState,
    openPlannerModal,
    closePlannerModal,
    openExecutorModal,
    closeExecutorModal,
    openEvaluatorModal,
    closeEvaluatorModal,
  } = useResearchModals();

  const hasExecutorAgent = !!traceInfo.executor_agent;
  const hasEvaluationAgents = traceInfo.evaluation_agent && traceInfo.evaluation_agent.length > 0;

  return (
    <div className="flex w-full flex-col gap-4 font-['Inter'] text-[#002835]">
      {/* PLANNER AGENT Section */}
      {traceInfo.planner_agent && traceInfo.planner_agent.length > 0 && (
        <PlannerAgentSection planners={traceInfo.planner_agent} onViewDetails={openPlannerModal} />
      )}

      {/* Query Refinement Agent Section */}
      {traceInfo.planner_refiner_agent && traceInfo.planner_refiner_agent.length > 0 && (
        <RefinerAgentSection refiners={traceInfo.planner_refiner_agent} />
      )}

      {/* Executor Agent Section */}
      {hasExecutorAgent && (
        <ExecutorAgentSection
          executor={traceInfo.executor_agent}
          onViewDetails={openExecutorModal}
        />
      )}

      {/* Separator before Evaluator Agent if executor agents existed */}
      {hasExecutorAgent && hasEvaluationAgents && <Separator />}

      {/* Evaluator Agent Section */}
      {hasEvaluationAgents && (
        <EvaluatorAgentSection
          evaluators={traceInfo.evaluation_agent}
          onViewDetails={openEvaluatorModal}
        />
      )}

      {/* Modals */}
      <ContextModal
        isVisible={modalState.plannerVisible}
        title={MODAL_TITLES.PLANNER}
        content={modalState.plannerContent}
        onClose={closePlannerModal}
        isHtml={true}
      />

      <ContextModal
        isVisible={modalState.executorVisible}
        title={MODAL_TITLES.EXECUTOR}
        content={modalState.executorContent}
        onClose={closeExecutorModal}
        isHtml={true}
      />

      <ContextModal
        isVisible={modalState.evaluatorVisible}
        title={MODAL_TITLES.EVALUATOR}
        content={modalState.evaluatorContent}
        onClose={closeEvaluatorModal}
        isHtml={true}
      />
    </div>
  );
};

export default ResearchTab;

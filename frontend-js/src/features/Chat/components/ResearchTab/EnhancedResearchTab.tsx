import React from 'react';
import ContextModal from '../ContextModal';
import { PlannerAgentSection } from './PlannerAgentSection';
import { RefinerAgentSection } from './RefinerAgentSection';
import { EnhancedExecutorAgentSection } from './EnhancedExecutorAgentSection';
import { KnowledgeBaseAgentSection } from './KnowledgeBaseAgentSection';
import { DetailedEvaluatorAgentSection } from './DetailedEvaluatorAgentSection';
import { Separator } from './Separator';
import { useResearchModals } from '@/hooks/useResearchModals';
import { MODAL_TITLES } from '@/constant/researchTab';
import { isKnowledgeBaseResponse } from '@/utils/knowledgeBaseUtils';
import type { ResearchTabProps } from '@/types/ResearchTabTypes';
import type { ExecutorAgentEnhanced, EvaluatorAgentEnhanced } from '@/types/knowledgeBaseTypes';

const EnhancedResearchTab: React.FC<ResearchTabProps> = ({ traceInfo }) => {
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

  // Check if executor has knowledge base
  const executorHasKB =
    hasExecutorAgent && isKnowledgeBaseResponse(traceInfo.executor_agent as ExecutorAgentEnhanced);

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

      {/* Knowledge Base Agent Section (dedicated section for knowledge base research) */}
      {executorHasKB && (
        <KnowledgeBaseAgentSection
          knowledgeBaseAgent={traceInfo.executor_agent as ExecutorAgentEnhanced}
          onViewDetails={(agent) => openExecutorModal(agent as any)}
        />
      )}

      {/* Regular Executor Agent Section (for non-knowledge base executors) */}
      {hasExecutorAgent && !executorHasKB && (
        <EnhancedExecutorAgentSection
          executor={traceInfo.executor_agent}
          onViewDetails={openExecutorModal}
        />
      )}

      {/* Separator before Evaluator Agents if executor agents existed */}
      {hasExecutorAgent && hasEvaluationAgents && <Separator />}

      {/* Detailed Evaluator Agents with Knowledge Base and Attempt Support */}
      {hasEvaluationAgents && (
        <DetailedEvaluatorAgentSection
          evaluators={traceInfo.evaluation_agent as unknown as EvaluatorAgentEnhanced[]}
          onViewDetails={(evaluator) => {
            // @ts-expect-error - Type conversion for modal compatibility
            openEvaluatorModal(evaluator);
          }}
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
        title={executorHasKB ? 'Knowledge Base Research Details' : MODAL_TITLES.EXECUTOR}
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

export default EnhancedResearchTab;

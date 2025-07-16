import React from 'react';
import type { EvaluatorAgentSectionProps } from '@/types/ResearchTabTypes';
import { LLMUsageDisplay } from './LLMUsageDisplay';
import { KeyValueRow } from './KeyValueRow';
import { ViewDetailsButton } from './ViewDetailsButton';
import { RESEARCH_STYLES, SECTION_TITLES, FIELD_LABELS } from '@/constant/researchTab';
import { extractEvaluatorLLMUsage } from '@/utils/researchTabUtils';

export const EvaluatorAgentSection: React.FC<EvaluatorAgentSectionProps> = ({
  evaluators,
  onViewDetails,
}) => {
  if (!evaluators || evaluators.length === 0) return null;

  return (
    <>
      <div style={RESEARCH_STYLES.sectionTitle}>{SECTION_TITLES.EVALUATOR_AGENT}</div>
      {evaluators.map((evaluator, index) => (
        <div key={index} style={{ marginBottom: '11px' }}>
          {(() => {
            const llmUsage = extractEvaluatorLLMUsage(evaluator);
            return llmUsage ? (
              <LLMUsageDisplay
                llmUsage={llmUsage}
                executionTimeMs={evaluator.execution_time_ms || 0}
              />
            ) : null;
          })()}
          <KeyValueRow keyText={FIELD_LABELS.EVALUATION_ATTEMPT} value={evaluator.attempt} />
          <KeyValueRow keyText={FIELD_LABELS.SCORE} value={evaluator.evaluation_history.score} />
          {evaluator.evaluation_history.error && (
            <KeyValueRow keyText={FIELD_LABELS.ERROR} value="Yes" />
          )}
        </div>
      ))}
      <ViewDetailsButton
        onClick={() => onViewDetails(evaluators[0])}
        text="View Reasoning Details"
      />
    </>
  );
};

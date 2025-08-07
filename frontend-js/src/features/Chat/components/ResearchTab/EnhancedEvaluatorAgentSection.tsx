import React from 'react';
import { LLMUsageDisplay } from './LLMUsageDisplay';
import { KeyValueRow } from './KeyValueRow';
import { ViewDetailsButton } from './ViewDetailsButton';
import { RESEARCH_STYLES, SECTION_TITLES } from '@/constant/researchTab';
import { isEvaluatorKnowledgeBase } from '@/utils/knowledgeBaseUtils';
import type { EvaluatorKnowledgeBaseProps } from '@/types/knowledgeBaseTypes';

export const EnhancedEvaluatorAgentSection: React.FC<EvaluatorKnowledgeBaseProps> = ({
  evaluators,
  onViewDetails,
}) => {
  return (
    <React.Fragment>
      <div style={RESEARCH_STYLES.sectionTitle}>{SECTION_TITLES.EVALUATOR_AGENT}</div>

      {evaluators.map((evaluator, index) => {
        const hasKnowledgeBase = isEvaluatorKnowledgeBase(evaluator);

        return (
          <div key={index} style={{ marginBottom: index < evaluators.length - 1 ? '24px' : '0' }}>
            {/* Evaluator Header */}
            <div
              style={{
                ...RESEARCH_STYLES.key,
                marginBottom: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <span>Evaluator Agent #{index + 1}</span>
              {hasKnowledgeBase && (
                <span
                  style={{
                    fontSize: '12px',
                    backgroundColor: '#E0F2FE',
                    color: '#0369A1',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontWeight: 500,
                  }}
                >
                  Knowledge Base
                </span>
              )}
            </div>

            {/* LLM Usage if available */}
            {evaluator.llm_usage && (
              <LLMUsageDisplay
                llmUsage={evaluator.llm_usage}
                executionTimeMs={evaluator.execution_time_ms || 0}
              />
            )}

            {/* Knowledge Base Trace Display */}
            {hasKnowledgeBase && evaluator.trace && (
              <div style={{ marginBottom: '16px' }}>
                <div
                  style={{
                    padding: '16px',
                    backgroundColor: '#F8FAFC',
                    borderRadius: '8px',
                    border: '1px solid #E2E8F0',
                    fontFamily: 'Inter, sans-serif',
                    fontSize: '14px',
                    color: '#64748B',
                  }}
                >
                  Knowledge base trace with {evaluator.num_hops || 0} research hops completed.
                  <div style={{ marginTop: '8px', fontSize: '12px', fontStyle: 'italic' }}>
                    Detailed trace visualization will be available soon.
                  </div>
                </div>
              </div>
            )}

            {/* Evaluator-specific Information */}
            <div style={{ marginBottom: '11px' }}>
              {evaluator.evaluation_result && (
                <KeyValueRow keyText="Evaluation Result" value={evaluator.evaluation_result} />
              )}

              {evaluator.evaluation_score && (
                <KeyValueRow keyText="Evaluation Score" value={evaluator.evaluation_score} />
              )}

              {hasKnowledgeBase && evaluator.num_hops && (
                <KeyValueRow
                  keyText="Research Hops"
                  value={`${evaluator.num_hops} hops completed`}
                />
              )}

              {Boolean(evaluator.error) && <KeyValueRow keyText="Error" value="Error occurred" />}
            </div>

            {/* View Details Button */}
            <ViewDetailsButton
              onClick={() => onViewDetails?.(evaluator)}
              text={
                hasKnowledgeBase
                  ? `View Evaluator #${index + 1} Knowledge Base Details`
                  : `View Evaluator #${index + 1} Details`
              }
            />
          </div>
        );
      })}
    </React.Fragment>
  );
};

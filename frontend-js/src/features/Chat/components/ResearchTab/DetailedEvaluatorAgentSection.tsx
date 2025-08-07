import React from 'react';
import { LLMUsageDisplay } from './LLMUsageDisplay';
import { KeyValueRow } from './KeyValueRow';
import { ViewDetailsButton } from './ViewDetailsButton';
import { RESEARCH_STYLES, SECTION_TITLES, FIELD_LABELS } from '@/constant/researchTab';
import { isEvaluatorKnowledgeBase } from '@/utils/knowledgeBaseUtils';
import type { EvaluatorAgentEnhanced } from '@/types/knowledgeBaseTypes';
import type { LLMUsage } from '@/lib/api-service';

interface DetailedEvaluatorAgentSectionProps {
  evaluators: EvaluatorAgentEnhanced[];
  onViewDetails?: (agent: EvaluatorAgentEnhanced) => void;
}

export const DetailedEvaluatorAgentSection: React.FC<DetailedEvaluatorAgentSectionProps> = ({
  evaluators,
  onViewDetails,
}) => {
  if (!evaluators || evaluators.length === 0) return null;

  return (
    <React.Fragment>
      <div style={RESEARCH_STYLES.sectionTitle}>{SECTION_TITLES.EVALUATOR_AGENT}</div>
      
      {evaluators.map((evaluator, evaluatorIndex) => {
        const hasKnowledgeBase = isEvaluatorKnowledgeBase(evaluator);
        
        // Get LLM usage from evaluation_history
        const historyObj = evaluator.evaluation_history as unknown as Record<string, unknown>;
        const llmUsage = historyObj?.llm_usage as LLMUsage;
        
        return (
          <div key={evaluatorIndex} style={{ marginBottom: '16px' }}>
            {/* Evaluator Label */}
            <div style={{
              ...RESEARCH_STYLES.key,
              marginBottom: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span>Evaluator Agent #{evaluatorIndex + 1}</span>
              {hasKnowledgeBase && (
                <span style={{
                  fontSize: '12px',
                  backgroundColor: '#E0F2FE',
                  color: '#0369A1',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  fontWeight: 500
                }}>
                  Knowledge Base
                </span>
              )}
            </div>

            {/* LLM Usage Display */}
            {llmUsage && (
              <div style={{ marginBottom: '8px' }}>
                <LLMUsageDisplay
                  llmUsage={llmUsage}
                  executionTimeMs={evaluator.execution_time_ms || 0}
                />
              </div>
            )}

            {/* Basic Evaluator Info */}
            {evaluator.evaluation_result && (
              <KeyValueRow 
                keyText="Evaluation Result" 
                value={evaluator.evaluation_result} 
              />
            )}
            
            {evaluator.evaluation_score && (
              <KeyValueRow 
                keyText="Evaluation Score" 
                value={evaluator.evaluation_score} 
              />
            )}

            {hasKnowledgeBase && evaluator.num_hops && (
              <KeyValueRow 
                keyText={FIELD_LABELS.RESEARCH_HOPS} 
                value={`${evaluator.num_hops} hops completed`} 
              />
            )}

            {Boolean(evaluator.error) && (
              <KeyValueRow keyText={FIELD_LABELS.ERROR} value="Error occurred" />
            )}

            {/* View Details Button */}
            <ViewDetailsButton
              onClick={() => onViewDetails?.(evaluator)}
              text={hasKnowledgeBase ? 
                `View Evaluator Agent #${evaluatorIndex + 1} Knowledge Base Details` : 
                `View Evaluator Agent #${evaluatorIndex + 1} Details`
              }
            />
          </div>
        );
      })}
    </React.Fragment>
  );
};

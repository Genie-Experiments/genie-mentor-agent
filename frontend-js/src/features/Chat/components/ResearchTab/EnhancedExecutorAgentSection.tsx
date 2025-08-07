import React from 'react';
import { LLMUsageDisplay } from './LLMUsageDisplay';
import { KeyValueRow } from './KeyValueRow';
import { ViewDetailsButton } from './ViewDetailsButton';
import { RESEARCH_STYLES, SECTION_TITLES, FIELD_LABELS } from '@/constant/researchTab';
import { isKnowledgeBaseResponse } from '@/utils/knowledgeBaseUtils';
import type { ExecutorAgentSectionProps } from '@/types/ResearchTabTypes';
import type { ExecutorAgentEnhanced } from '@/types/knowledgeBaseTypes';
import type { ExecutorAgent } from '@/lib/api-service';

export const EnhancedExecutorAgentSection: React.FC<ExecutorAgentSectionProps> = ({
  executor,
  onViewDetails,
}) => {
  const enhancedExecutor = executor as ExecutorAgentEnhanced;
  const hasKnowledgeBase = isKnowledgeBaseResponse(enhancedExecutor);

  return (
    <React.Fragment>
      <div style={RESEARCH_STYLES.sectionTitle}>{SECTION_TITLES.EXECUTOR_AGENT}</div>

      <LLMUsageDisplay
        llmUsage={enhancedExecutor.llm_usage}
        executionTimeMs={enhancedExecutor.execution_time_ms || 0}
      />

      {/* Knowledge Base Trace Display */}
      {hasKnowledgeBase && enhancedExecutor.trace && (
        <div style={{ marginBottom: '20px' }}>
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
            Knowledge base trace with {enhancedExecutor.num_hops || 0} research hops completed.
            <div style={{ marginTop: '8px', fontSize: '12px', fontStyle: 'italic' }}>
              Detailed trace visualization will be available soon.
            </div>
          </div>
        </div>
      )}

      <div style={{ marginBottom: '11px' }}>
        {enhancedExecutor.executor_answer && (
          <KeyValueRow
            keyText={FIELD_LABELS.COMBINED_ANSWER}
            value={enhancedExecutor.executor_answer}
          />
        )}

        {hasKnowledgeBase && enhancedExecutor.num_hops && (
          <KeyValueRow
            keyText="Research Hops"
            value={`${enhancedExecutor.num_hops} hops completed`}
          />
        )}

        {Boolean(enhancedExecutor.error) && (
          <KeyValueRow keyText={FIELD_LABELS.ERROR} value="Error occurred" />
        )}
      </div>

      <ViewDetailsButton
        onClick={() => onViewDetails(enhancedExecutor as ExecutorAgent)}
        text={
          hasKnowledgeBase
            ? 'View Knowledge Base Research Details'
            : 'View Executor Agent Detailed Response'
        }
      />
    </React.Fragment>
  );
};

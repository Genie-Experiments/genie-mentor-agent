import React from 'react';
import type { ExecutorAgentSectionProps } from '@/types/ResearchTabTypes';
import { LLMUsageDisplay } from './LLMUsageDisplay';
import { KeyValueRow } from './KeyValueRow';
import { ViewDetailsButton } from './ViewDetailsButton';
import { RESEARCH_STYLES, SECTION_TITLES, FIELD_LABELS } from '@/constant/researchTab';

export const ExecutorAgentSection: React.FC<ExecutorAgentSectionProps> = ({
  executor,
  onViewDetails,
}) => {
  return (
    <React.Fragment>
      <div style={RESEARCH_STYLES.sectionTitle}>{SECTION_TITLES.EXECUTOR_AGENT}</div>
      <LLMUsageDisplay
        llmUsage={executor.llm_usage}
        executionTimeMs={executor.execution_time_ms || 0}
      />
      <div style={{ marginBottom: '11px' }}>
        {executor.executor_answer && (
          <KeyValueRow keyText={FIELD_LABELS.COMBINED_ANSWER} value={executor.executor_answer} />
        )}
        {executor.error && <KeyValueRow keyText={FIELD_LABELS.ERROR} value="Yes" />}
      </div>
      <ViewDetailsButton
        onClick={() => onViewDetails(executor)}
        text="View Executor Agent Detailed Response"
      />
    </React.Fragment>
  );
};

import React from 'react';
import type { RefinerAgentSectionProps } from '@/types/ResearchTabTypes';
import { LLMUsageDisplay } from './LLMUsageDisplay';
import { KeyValueRow } from './KeyValueRow';
import { Separator } from './Separator';
import { RESEARCH_STYLES, SECTION_TITLES, FIELD_LABELS } from '@/constant/researchTab';
import { formatDisplayValue } from '@/utils/researchTabUtils';

export const RefinerAgentSection: React.FC<RefinerAgentSectionProps> = ({ refiners }) => {
  if (!refiners || refiners.length === 0) return null;

  return (
    <>
      <div style={RESEARCH_STYLES.sectionTitle}>{SECTION_TITLES.QUERY_REFINEMENT}</div>
      {refiners.map((refiner, index) => (
        <div key={index} style={{ marginBottom: '11px' }}>
          <LLMUsageDisplay
            llmUsage={refiner.llm_usage}
            executionTimeMs={refiner.execution_time_ms}
          />
          <KeyValueRow
            keyText={FIELD_LABELS.REFINEMENT_REQUIRED}
            value={formatDisplayValue(refiner.refinement_required)}
          />
          <KeyValueRow keyText={FIELD_LABELS.FEEDBACK_SUMMARY} value={refiner.feedback_summary} />
          <KeyValueRow
            keyText={FIELD_LABELS.FEEDBACK_REASONING}
            value={refiner.feedback_reasoning}
          />
          {refiner.error && <KeyValueRow keyText={FIELD_LABELS.ERROR} value="Yes" />}
        </div>
      ))}
      <Separator />
    </>
  );
};

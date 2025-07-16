import React from 'react';
import type { PlannerAgentSectionProps } from '@/types/ResearchTabTypes';
import { LLMUsageDisplay } from './LLMUsageDisplay';
import { KeyValueRow } from './KeyValueRow';
import { QueryComponents } from './QueryComponents';
import { ViewDetailsButton } from './ViewDetailsButton';
import { Separator } from './Separator';
import { RESEARCH_STYLES, SECTION_TITLES, FIELD_LABELS } from '@/constant/researchTab';

export const PlannerAgentSection: React.FC<PlannerAgentSectionProps> = ({
  planners,
  onViewDetails,
}) => {
  if (!planners || planners.length === 0) return null;

  return (
    <>
      <div style={RESEARCH_STYLES.sectionTitle}>{SECTION_TITLES.PLANNER_AGENT}</div>
      {planners.map((planner, index) => (
        <div key={index} style={{ marginBottom: '11px' }}>
          <LLMUsageDisplay
            llmUsage={planner.llm_usage}
            executionTimeMs={planner.execution_time_ms}
          />
          <KeyValueRow keyText={FIELD_LABELS.QUERY_INTENT} value={planner.plan.query_intent} />
          {planner.plan.query_components.length > 0 && (
            <QueryComponents components={planner.plan.query_components} />
          )}
        </div>
      ))}
      <ViewDetailsButton
        onClick={() => onViewDetails(planners[0])}
        text="View Planner Detailed Response"
      />
      <Separator />
    </>
  );
};

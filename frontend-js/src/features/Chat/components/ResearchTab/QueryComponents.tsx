import React from 'react';
import type { QueryComponentProps } from '@/types/ResearchTabTypes';
import { RESEARCH_STYLES, RESEARCH_CONSTANTS } from '@/constant/researchTab';

export const QueryComponents: React.FC<QueryComponentProps> = ({ components }) => {
  if (!components || components.length === 0) return null;

  return (
    <div style={{ display: 'flex', marginBottom: '11px' }}>
      <div
        style={{
          ...RESEARCH_STYLES.key,
          width: RESEARCH_CONSTANTS.KEY_COLUMN_WIDTH,
          flexShrink: 0,
        }}
      >
        Query Component
      </div>
      <div style={{ width: RESEARCH_CONSTANTS.SPACER_WIDTH, flexShrink: 0 }} />
      <div>
        <div>
          <span style={RESEARCH_STYLES.componentKey}>ID: </span>
          <span style={RESEARCH_STYLES.value}>{components[0].id}</span>
        </div>
        <div>
          <span style={RESEARCH_STYLES.componentKey}>Sub-Query: </span>
          <span style={RESEARCH_STYLES.value}>{components[0].sub_query}</span>
        </div>
        <div>
          <span style={RESEARCH_STYLES.componentKey}>Source: </span>
          <span style={RESEARCH_STYLES.value}>{components[0].source}</span>
        </div>
      </div>
    </div>
  );
};

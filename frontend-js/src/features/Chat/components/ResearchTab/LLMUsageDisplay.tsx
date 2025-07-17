import React from 'react';
import type { LLMUsageDisplayProps } from '@/types/ResearchTabTypes';
import { RESEARCH_STYLES, RESEARCH_CONSTANTS, FIELD_LABELS } from '@/constant/researchTab';

export const LLMUsageDisplay: React.FC<LLMUsageDisplayProps> = ({ llmUsage, executionTimeMs }) => {
  if (!llmUsage) return null;

  const columnStyle: React.CSSProperties = {
    ...RESEARCH_STYLES.column,
    paddingRight: RESEARCH_CONSTANTS.EXECUTION_TIME_PADDING,
    marginRight: RESEARCH_CONSTANTS.EXECUTION_TIME_PADDING,
    minWidth: RESEARCH_CONSTANTS.MIN_COLUMN_WIDTH,
  };

  const largeColumnStyle: React.CSSProperties = {
    ...columnStyle,
    minWidth: RESEARCH_CONSTANTS.LARGE_MIN_COLUMN_WIDTH,
  };

  const lastColumnStyle: React.CSSProperties = {
    ...RESEARCH_STYLES.lastColumn,
    minWidth: RESEARCH_CONSTANTS.MIN_COLUMN_WIDTH,
  };

  return (
    <div style={{ marginTop: '18px', marginBottom: '18px', display: 'flex' }}>
      <div style={columnStyle}>
        <div style={RESEARCH_STYLES.executionTimeValue}>
          <span>{executionTimeMs || 0}</span>
          <span style={{ textTransform: 'lowercase' }}>ms</span>
        </div>
        <div style={RESEARCH_STYLES.label}>{FIELD_LABELS.EXECUTION_TIME}</div>
      </div>

      <div style={largeColumnStyle}>
        <div
          style={{
            ...RESEARCH_STYLES.valueTitle,
            maxWidth: '240px',
            overflow: 'visible',
            whiteSpace: 'normal',
            cursor: 'default',
            wordBreak: 'break-word',
          }}
          title={llmUsage.model}
        >
          {llmUsage.model}
        </div>
        <div style={RESEARCH_STYLES.label}>{FIELD_LABELS.LLM_USED}</div>
      </div>

      <div style={columnStyle}>
        <div style={RESEARCH_STYLES.valueTitle}>
          {String(llmUsage.input_tokens).padStart(2, '0')}
        </div>
        <div style={RESEARCH_STYLES.label}>{FIELD_LABELS.INPUT_TOKENS}</div>
      </div>

      <div style={lastColumnStyle}>
        <div style={RESEARCH_STYLES.valueTitle}>
          {String(llmUsage.output_tokens).padStart(2, '0')}
        </div>
        <div style={RESEARCH_STYLES.label}>{FIELD_LABELS.OUTPUT_TOKENS}</div>
      </div>
    </div>
  );
};

import React from 'react';
import type { KeyValueRowProps } from '@/types/ResearchTabTypes';
import { RESEARCH_STYLES, RESEARCH_CONSTANTS } from '@/constant/researchTab';

export const KeyValueRow: React.FC<KeyValueRowProps> = ({
  keyText,
  value,
  showBatch = false,
  index,
}) => {
  return (
    <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: '11px' }}>
      {/* Number Column */}
      {index !== undefined && (
        <div
          style={{
            ...RESEARCH_STYLES.key,
            width: RESEARCH_CONSTANTS.NUMBER_COLUMN_WIDTH,
            flexShrink: 0,
          }}
        >
          {index + 1}.
        </div>
      )}

      {/* Key Column */}
      <div
        style={{
          ...RESEARCH_STYLES.key,
          width: RESEARCH_CONSTANTS.KEY_COLUMN_WIDTH,
          flexShrink: 0,
        }}
      >
        {keyText}
      </div>

      {/* Spacer Column */}
      <div style={{ width: RESEARCH_CONSTANTS.SPACER_WIDTH, flexShrink: 0 }} />

      {/* Value Column (takes remaining space) */}
      <div style={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
        {value !== undefined && value !== null && (
          <div
            style={
              typeof value === 'string' && !Array.isArray(value)
                ? { ...RESEARCH_STYLES.value, ...RESEARCH_STYLES.truncatedText }
                : RESEARCH_STYLES.value
            }
          >
            {Array.isArray(value) ? value.join(', ') : String(value)}
          </div>
        )}

        {showBatch && value !== undefined && value !== null && !Array.isArray(value) && (
          <div style={{ marginLeft: '4px', ...RESEARCH_STYLES.batch }}>
            <span style={RESEARCH_STYLES.batchText}>Good</span>
          </div>
        )}
      </div>
    </div>
  );
};

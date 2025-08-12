import React from 'react';
import type { EditorAgentSectionProps } from '@/types/ResearchTabTypes';
import { KeyValueRow } from './KeyValueRow';
import { ViewDetailsButton } from './ViewDetailsButton';
import { RESEARCH_STYLES, SECTION_TITLES, FIELD_LABELS } from '@/constant/researchTab';

export const EditorAgentSection: React.FC<EditorAgentSectionProps> = ({
  editors,
  onViewDetails,
}) => {
  if (!editors || editors.length === 0) return null;

  return (
    <>
      <div style={RESEARCH_STYLES.sectionTitle}>{SECTION_TITLES.EDITOR_AGENT}</div>
      {editors.map((editor, index) => (
        <div key={index} style={{ marginBottom: '16px' }}>
          {/* Editor Information */}
          <div style={{ marginBottom: '11px' }}>
            <KeyValueRow keyText={FIELD_LABELS.EDITOR_ATTEMPT} value={editor.attempt} />
            {editor.editor_history.answer && (
              <KeyValueRow 
                keyText={FIELD_LABELS.EDITOR_ANSWER} 
                value={editor.editor_history.answer}
              />
            )}
            {editor.editor_history.skipped && (
              <KeyValueRow keyText={FIELD_LABELS.SKIPPED} value="Yes" />
            )}
            {editor.editor_history.error && (
              <KeyValueRow keyText={FIELD_LABELS.ERROR} value="Yes" />
            )}
          </div>

          {/* View Details Button for each editor */}
          <ViewDetailsButton
            onClick={() => onViewDetails(editor)}
            text={`View Editor Agent Iteration #${editor.attempt} Details`}
          />
        </div>
      ))}
    </>
  );
};

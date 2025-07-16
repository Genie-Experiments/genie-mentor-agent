import React from 'react';
import type { KnowledgeBaseSourceItemProps } from '@/types/SourcesTabTypes';
import { ViewDetailsButton } from './ViewDetailsButton';
import { SOURCES_STYLES, SOURCES_CONSTANTS, SOURCES_FIELD_LABELS } from '@/constant/sourcesTab';
import { getSourceTitle } from '@/utils/sourcesTabUtils';

export const KnowledgeBaseSourceItem: React.FC<KnowledgeBaseSourceItemProps> = ({
  item,
  index,
  onShowDetail,
}) => {
  const title = getSourceTitle(item.title);

  return (
    <li style={SOURCES_STYLES.listItem}>
      <div style={SOURCES_STYLES.itemHeader}>
        <span style={SOURCES_STYLES.itemIndex}>{index + 1}.</span>
        <span style={SOURCES_STYLES.itemTitle}>{title}</span>
      </div>
      <div style={SOURCES_STYLES.itemContent}>
        <div style={{ height: SOURCES_CONSTANTS.VERTICAL_SPACING.LARGE }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          <div style={SOURCES_STYLES.itemDetail}>
            {SOURCES_FIELD_LABELS.SOURCE}: {item.source}
          </div>
          <div style={SOURCES_STYLES.itemDetail}>
            {SOURCES_FIELD_LABELS.PAGE}: {item.page}
          </div>
        </div>
        <div style={{ height: SOURCES_CONSTANTS.VERTICAL_SPACING.LARGE }} />
        <ViewDetailsButton onClick={() => onShowDetail(title, index)} />
      </div>
    </li>
  );
};

import React from 'react';
import type { WebSourceItemProps } from '@/types/SourcesTabTypes';
import { StarIcon } from './StarIcon';
import { SOURCES_STYLES, SOURCES_CONSTANTS } from '@/constant/sourcesTab';
import { getSourceTitle, getSourceDescription } from '@/utils/sourcesTabUtils';

export const WebSourceItem: React.FC<WebSourceItemProps> = ({ item, index }) => {
  const title = getSourceTitle(item.title);
  const description = getSourceDescription(item.description);

  return (
    <li style={SOURCES_STYLES.listItem}>
      <div style={SOURCES_STYLES.itemHeader}>
        <span style={SOURCES_STYLES.itemIndex}>{index + 1}.</span>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: SOURCES_CONSTANTS.HORIZONTAL_SPACING.SMALL,
          }}
        >
          <StarIcon />
          <a href={item.url} target="_blank" rel="noopener noreferrer" style={SOURCES_STYLES.link}>
            {item.url}
          </a>
        </div>
      </div>
      <div style={SOURCES_STYLES.itemContent}>
        <div style={{ height: SOURCES_CONSTANTS.VERTICAL_SPACING.MEDIUM }} />
        <div style={SOURCES_STYLES.itemTitle}>{title}</div>
        <div style={{ height: SOURCES_CONSTANTS.VERTICAL_SPACING.SMALL }} />
        <div style={SOURCES_STYLES.itemDetail}>{description}</div>
      </div>
    </li>
  );
};

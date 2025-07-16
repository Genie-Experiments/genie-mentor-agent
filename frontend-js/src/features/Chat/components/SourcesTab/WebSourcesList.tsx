import React from 'react';
import type { WebsearchMetadata } from '@/lib/api-service';
import { WebSourceItem } from './WebSourceItem';
import { SOURCES_STYLES } from '@/constant/sourcesTab';

interface WebSourcesListProps {
  metadata: WebsearchMetadata[];
}

export const WebSourcesList: React.FC<WebSourcesListProps> = ({ metadata }) => {
  return (
    <ol style={SOURCES_STYLES.listContainer}>
      {metadata.map((item, index) => (
        <WebSourceItem key={index} item={item} index={index} />
      ))}
    </ol>
  );
};

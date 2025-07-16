import React from 'react';
import type { KnowledgebaseMetadata } from '@/lib/api-service';
import { KnowledgeBaseSourceItem } from './KnowledgeBaseSourceItem';
import { SOURCES_STYLES } from '@/constant/sourcesTab';

interface KnowledgeBaseSourcesListProps {
  metadata: KnowledgebaseMetadata[];
  onShowDetail: (title: string, index: number) => void;
}

export const KnowledgeBaseSourcesList: React.FC<KnowledgeBaseSourcesListProps> = ({
  metadata,
  onShowDetail,
}) => {
  return (
    <ol style={SOURCES_STYLES.listContainer}>
      {metadata.map((item, index) => (
        <KnowledgeBaseSourceItem
          key={index}
          item={item}
          index={index}
          onShowDetail={onShowDetail}
        />
      ))}
    </ol>
  );
};

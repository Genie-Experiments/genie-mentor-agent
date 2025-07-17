import React from 'react';
import type { SourceSectionProps } from '@/types/SourcesTabTypes';
import { SOURCES_STYLES } from '@/constant/sourcesTab';

export const SourceSection: React.FC<SourceSectionProps> = ({
  title,
  children,
  showSeparator = false,
}) => {
  return (
    <>
      <div style={SOURCES_STYLES.sectionTitle}>{title}</div>
      {children}
      {showSeparator && <div style={SOURCES_STYLES.separator} />}
    </>
  );
};

import React from 'react';
import type { NoSourcesMessageProps } from '@/types/SourcesTabTypes';
import { SOURCES_STYLES } from '@/constant/sourcesTab';

export const NoSourcesMessage: React.FC<NoSourcesMessageProps> = ({ message }) => {
  return <div style={SOURCES_STYLES.noSourcesMessage}>{message}</div>;
};

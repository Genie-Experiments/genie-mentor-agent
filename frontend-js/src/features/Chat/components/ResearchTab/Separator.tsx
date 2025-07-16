import React from 'react';
import type { SeparatorProps } from '@/types/ResearchTabTypes';
import { RESEARCH_STYLES } from '@/constant/researchTab';

export const Separator: React.FC<SeparatorProps> = ({ style }) => {
  return <div style={{ ...RESEARCH_STYLES.separator, ...style }} />;
};

import React from 'react';
import EnhancedResearchTab from './EnhancedResearchTab';
import type { ResearchTabProps } from '@/types/ResearchTabTypes';

const ResearchTab: React.FC<ResearchTabProps> = ({ traceInfo }) => {
  return <EnhancedResearchTab traceInfo={traceInfo} />;
};

export default ResearchTab;

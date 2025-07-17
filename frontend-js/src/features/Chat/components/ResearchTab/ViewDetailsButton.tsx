import React from 'react';
import type { ViewDetailsButtonProps } from '@/types/ResearchTabTypes';
import { RESEARCH_STYLES } from '@/constant/researchTab';

export const ViewDetailsButton: React.FC<ViewDetailsButtonProps> = ({ onClick, text }) => {
  return (
    <div style={RESEARCH_STYLES.viewDetails} onClick={onClick}>
      {text}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="21"
        height="22"
        viewBox="0 0 21 22"
        fill="none"
        style={{ marginLeft: '8px' }}
      >
        <path
          d="M7.875 16.25L13.125 11L7.875 5.75"
          stroke="#00A599"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
};

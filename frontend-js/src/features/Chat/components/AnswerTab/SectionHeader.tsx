import React from 'react';
import { STYLES } from '@/constant/answerTab';
import type { SectionHeaderProps } from '@/types/AnswerTabTypes';

export const SectionHeader: React.FC<SectionHeaderProps> = ({ title, className = '' }) => (
  <div className={`mb-4 ${className}`} style={STYLES.header}>
    {title}
  </div>
);

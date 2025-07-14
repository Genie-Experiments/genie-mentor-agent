import React from 'react';
import { StarIcon } from './StarIcon';
import { SectionHeader } from './SectionHeader';
import { STYLES } from '@/constant/answerTab';
import type { ContextCard } from '@/types/AnswerTabTypes';

interface ContextSectionProps {
  contexts: ContextCard[];
  onContextClick: (index: number) => void;
}

interface ContextCardComponentProps {
  context: ContextCard;
  index: number;
  onClick: (index: number) => void;
}

const ContextCardComponent: React.FC<ContextCardComponentProps> = ({ context, index, onClick }) => (
  <div
    onClick={() => onClick(index)}
    className={STYLES.card.className}
    style={{ padding: STYLES.card.padding }}
  >
    <div className="flex items-center gap-2">
      <span style={{ width: 16, height: 16, display: 'inline-flex', alignItems: 'center' }}>
        <StarIcon />
      </span>
      <span
        style={{
          ...STYLES.text.secondary,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          maxWidth: 180,
        }}
      >
        {context.title || `Context ${index + 1}`}
      </span>
    </div>
    <div
      style={{
        ...STYLES.text.primary,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
        maxWidth: 200,
        height: '42px',
      }}
    >
      {context.content}
    </div>
  </div>
);

export const ContextSection: React.FC<ContextSectionProps> = React.memo(
  ({ contexts, onContextClick }) => {
    if (contexts.length === 0) return null;

    return (
      <div>
        <SectionHeader title="Context" />
        <div className={STYLES.grid.className} style={STYLES.grid.style}>
          {contexts.map((context, index) => (
            <ContextCardComponent
              key={`context-${index}`}
              context={context}
              index={index}
              onClick={onContextClick}
            />
          ))}
        </div>
      </div>
    );
  }
);

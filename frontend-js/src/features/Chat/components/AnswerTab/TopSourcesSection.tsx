import React from 'react';
import { StarIcon } from './StarIcon';
import { SectionHeader } from './SectionHeader';
import type { SourceCard } from '@/types/AnswerTabTypes';
import { STYLES } from '@/constant/answerTab';
import { truncateUrl } from '@/utils/answerTabUtils';

interface TopSourcesSectionProps {
  sources: SourceCard[];
}

interface SourceCardComponentProps {
  source: SourceCard;
  index: number;
}

const SourceCardComponent: React.FC<SourceCardComponentProps> = ({ source, index }) => (
  <a
    key={index}
    href={source.url}
    target="_blank"
    rel="noopener noreferrer"
    className="flex flex-col items-start justify-center rounded-[8px] border border-[#9CBFBC] bg-white transition-shadow hover:shadow-[0px_12px_21px_0px_#CDE6E5]"
    style={{ padding: STYLES.card.padding, textDecoration: 'none', gap: 0 }}
  >
    <div className="flex items-center gap-2">
      <span style={{ width: 16, height: 16, display: 'inline-flex', alignItems: 'center' }}>
        <StarIcon />
      </span>
      <span style={STYLES.text.secondary}>{truncateUrl(source.url)}</span>
    </div>
    <div style={{ height: '10px' }} />
    <div
      style={{
        ...STYLES.text.title,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
        maxWidth: 200,
        marginBottom: '7px',
      }}
    >
      {source.title}
    </div>
  </a>
);

export const TopSourcesSection: React.FC<TopSourcesSectionProps> = React.memo(({ sources }) => {
  if (sources.length === 0) return null;

  return (
    <div>
      <SectionHeader title="Top sources" />
      <div className={STYLES.grid.className} style={STYLES.grid.style}>
        {sources.map((source, index) => (
          <SourceCardComponent key={`source-${index}`} source={source} index={index} />
        ))}
      </div>
    </div>
  );
});

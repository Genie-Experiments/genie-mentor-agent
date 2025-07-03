import React from 'react';
import Tooltip from '../../../components/ui/Tooltip';
import type { CitationRendererProps } from '../../../lib/types';
import {
  getSourceDisplayName,
  isExternalSource,
  getCitationUrl,
  getExternalSourceUrl,
  processCitationText,
} from '../../../lib/utils';
import { SOURCE_TYPES } from '../../../constant';

const CitationRenderer: React.FC<CitationRendererProps> = ({
  children,
  onCitationClick,
  isMultiSource = false,
  dataSources = [SOURCE_TYPES.KNOWLEDGE_BASE],
  sourceUrls = {},
  onOpenUrl = (url) => window.open(url, '_blank', 'noopener,noreferrer'),
  metadata = {},
}) => {
  console.log(children, 'Children received in CitationRenderer');
  const childrenAsString = React.Children.toArray(children)
    .map((child) => {
      console.log('Processing child:', child);
      if (typeof child === 'string' || typeof child === 'number') {
        return String(child);
      }
      if (React.isValidElement(child)) {
        const props = child.props as { children?: React.ReactNode };
        if (props && props.children) {
          return String(props.children);
        }
      }
      return '';
    })
    .join('');

  const parts = processCitationText(childrenAsString, isMultiSource);

  return (
    <>
      {parts.map((part, index) => {
        if (part.type === 'citation') {
          const sourceName =
            isMultiSource && part.sourceIndex !== undefined
              ? dataSources[part.sourceIndex] || SOURCE_TYPES.KNOWLEDGE_BASE
              : dataSources[0] || SOURCE_TYPES.KNOWLEDGE_BASE;

          return (
            <Tooltip
              key={index}
              content={{
                title: getSourceDisplayName(sourceName),
                subtitle: `Source ${part.originalText || part.docIndex + 1}`,
              }}
              position="top"
            >
              <span
                className={`citation ${isExternalSource(sourceName) ? 'citation-url' : ''}`}
                onClick={() => {
                  if (isExternalSource(sourceName)) {
                    // First try to get URL from metadata if available (for GitHub, Notion, WebSearch)
                    const metadataUrl = getExternalSourceUrl(sourceName, part.docIndex, metadata);

                    // If metadata URL is available, use it
                    if (metadataUrl) {
                      onOpenUrl(metadataUrl);
                      return;
                    }

                    // Otherwise fall back to source URLs map
                    const fallbackUrl = getCitationUrl(sourceName, part.docIndex, sourceUrls);
                    if (fallbackUrl) {
                      onOpenUrl(fallbackUrl);
                      return;
                    }
                  }

                  // If not an external source or no URL found, handle as before
                  if (part.sourceIndex !== undefined) {
                    // Multi-source citation
                    onCitationClick(part.docIndex, part.sourceIndex);
                  } else {
                    // Single-source citation
                    onCitationClick(part.docIndex);
                  }
                }}
              >
                {part.content}
              </span>
            </Tooltip>
          );
        }
        return <React.Fragment key={index}>{part.content}</React.Fragment>;
      })}
    </>
  );
};

export default CitationRenderer;

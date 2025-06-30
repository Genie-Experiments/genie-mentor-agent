import React from 'react';
import Tooltip from '../../../components/ui/Tooltip';

interface CitationRendererProps {
  children: React.ReactNode;
  onCitationClick: (citationIndex: number, sourceIndex?: number) => void;
  isMultiSource?: boolean;
  dataSources?: string[];
  // URL mapping for external sources (key is source type + index)
  sourceUrls?: Record<string, string>;
  // Callback for opening URLs
  onOpenUrl?: (url: string) => void;
}

// Helper function to format source names for display - focused on our four main sources
const getSourceDisplayName = (sourceName: string): string => {
  switch (sourceName.toLowerCase()) {
    case 'knowledgebase':
      return 'Knowledge Base';
    case 'websearch':
      return 'Web Source';
    case 'github':
      return 'GitHub Source';
    case 'notion':
      return 'Notion Doc';
    default:
      // For any other source, capitalize the first letter
      return sourceName.charAt(0).toUpperCase() + sourceName.slice(1);
  }
};

const CitationRenderer: React.FC<CitationRendererProps> = ({
  children,
  onCitationClick,
  isMultiSource = false,
  dataSources = ['knowledgebase'],
  sourceUrls = {},
  onOpenUrl = (url) => window.open(url, '_blank', 'noopener,noreferrer'),
}) => {
  // Convert children to string for processing
  const childrenAsString = React.Children.toArray(children)
    .map((child) => {
      if (typeof child === 'string' || typeof child === 'number') {
        return String(child);
      }
      if (React.isValidElement(child)) {
        // Try to extract text content from React elements
        const props = child.props as { children?: React.ReactNode };
        if (props && props.children) {
          return String(props.children);
        }
      }
      return '';
    })
    .join('');

  // Define types for our text parts
  type TextPart = {
    type: 'text';
    content: string;
  };

  type CitationPart = {
    type: 'citation';
    content: string;
    sourceIndex?: number;
    docIndex: number;
    originalText?: string;
  };

  type Part = TextPart | CitationPart;

  // Process the text to replace citation markers with styled spans
  const processText = () => {
    if (!childrenAsString) return [] as Part[];

    // Choose regex based on whether we have multiple sources or not
    // Updated to handle decimal citations like [3.2]
    const singleSourceRegex = /\[(\d+(?:\.\d+)?)\]/g;
    const multiSourceRegex = /\[([A-Z])\]\[(\d+(?:\.\d+)?)\]/g;

    const regex = isMultiSource ? multiSourceRegex : singleSourceRegex;
    const parts: Part[] = [];
    let lastIndex = 0;
    let match;

    // Find all citation matches and split text around them
    while ((match = regex.exec(childrenAsString)) !== null) {
      // Add text before the citation
      if (match.index > lastIndex) {
        parts.push({ type: 'text', content: childrenAsString.substring(lastIndex, match.index) });
      }

      if (isMultiSource) {
        // For multi-source format: [A][1] or [A][3.2]
        const sourceIndex = match[1].charCodeAt(0) - 65; // Convert A->0, B->1, etc.
        // Parse the citation number and convert to integer (e.g. "3.2" becomes 3)
        const citationNumber = parseInt(match[2], 10);

        // Display the original citation but use integer for processing
        console.log(
          `Found multi-source citation: [${match[1]}][${match[2]}], source: ${sourceIndex}, document: ${citationNumber - 1}`
        );

        parts.push({
          type: 'citation',
          content: match[0], // Keep the original citation format [A][n]
          sourceIndex: sourceIndex,
          docIndex: citationNumber - 1, // Convert to 0-based index for array access
          originalText: match[2], // Keep original text for display purposes
        });
      } else {
        // For single-source format: [1] or [3.2]
        // Parse the citation number and convert to integer (e.g. "3.2" becomes 3)
        const citationNumber = parseInt(match[1], 10);

        // Display the original citation but use integer for processing
        console.log(
          `Found single-source citation: [${match[1]}], parsed as number: ${citationNumber - 1}`
        );

        parts.push({
          type: 'citation',
          content: match[0], // Keep the original citation format [n]
          docIndex: citationNumber - 1, // Convert to 0-based index for array access
          originalText: match[1], // Keep original text for display purposes
        });
      }

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text after last citation
    if (lastIndex < childrenAsString.length) {
      parts.push({ type: 'text', content: childrenAsString.substring(lastIndex) });
    }

    return parts;
  };

  const parts = processText();

  // Debug log to show parsed parts
  console.log('Parsed citation parts:', parts);

  // Helper function to check if source is an external source type that should open URL
  const isExternalSource = (sourceName: string): boolean => {
    const sourceLower = sourceName.toLowerCase();
    return sourceLower === 'websearch' || sourceLower === 'github' || sourceLower === 'notion';
  };

  // Helper function to get URL for a citation - optimized for our four sources
  const getCitationUrl = (sourceName: string, docIndex: number): string | undefined => {
    // Create the exact key in the format sourceName_docIndex
    const key = `${sourceName.toLowerCase()}_${docIndex}`;

    // First try the exact key match
    if (sourceUrls[key]) {
      return sourceUrls[key];
    }

    // Special handling for each source type if exact key not found
    const sourceLower = sourceName.toLowerCase();

    // Find all keys for this source type
    const sourceKeys = Object.keys(sourceUrls).filter((k) => k.startsWith(`${sourceLower}_`));

    if (sourceKeys.length > 0) {
      if (docIndex < sourceKeys.length) {
        // Try to match the index if possible
        const sortedKeys = sourceKeys.sort((a, b) => {
          const aIndex = parseInt(a.split('_')[1], 10);
          const bIndex = parseInt(b.split('_')[1], 10);
          return aIndex - bIndex;
        });
        return sourceUrls[sortedKeys[docIndex]];
      } else {
        // Fallback to the first URL for this source
        return sourceUrls[sourceKeys[0]];
      }
    }

    // If no URL is found, return undefined
    return undefined;
  };

  return (
    <>
      {parts.map((part, index) => {
        if (part.type === 'citation') {
          return (
            <Tooltip
              key={index}
              content={{
                title:
                  isMultiSource && 'sourceIndex' in part && part.sourceIndex !== undefined
                    ? getSourceDisplayName(dataSources[part.sourceIndex] || 'knowledgebase')
                    : getSourceDisplayName(dataSources[0] || 'knowledgebase'),
                subtitle: `Source ${part.originalText || part.docIndex + 1}`,
              }}
              position="top"
            >
              <span
                className={`citation ${
                  isExternalSource(
                    isMultiSource && 'sourceIndex' in part && part.sourceIndex !== undefined
                      ? dataSources[part.sourceIndex] || 'knowledgebase'
                      : dataSources[0] || 'knowledgebase'
                  )
                    ? 'citation-url'
                    : ''
                }`}
                onClick={() => {
                  // Determine the source name for this citation
                  const sourceName =
                    isMultiSource && 'sourceIndex' in part && part.sourceIndex !== undefined
                      ? dataSources[part.sourceIndex] || 'knowledgebase'
                      : dataSources[0] || 'knowledgebase';

                  // Handle each source type appropriately
                  switch (sourceName.toLowerCase()) {
                    case 'websearch':
                    case 'github':
                    case 'notion': {
                      // External sources - open URL if available
                      const url = getCitationUrl(sourceName, part.docIndex);
                      if (url) {
                        console.log(`Opening ${sourceName} URL:`, url);
                        onOpenUrl(url);
                        return;
                      } else {
                        console.warn(`No ${sourceName} URL found for index ${part.docIndex}`);
                      }
                      break;
                    }

                    case 'knowledgebase':
                    default:
                      // Internal source - use context modal
                      console.log(`Opening context modal for ${sourceName}`);
                      break;
                  }

                  // Default behavior - open context modal
                  if ('sourceIndex' in part && part.sourceIndex !== undefined) {
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

import React from 'react';

interface CitationRendererProps {
  children: React.ReactNode;
  onCitationClick: (citationIndex: number) => void;
}

const CitationRenderer: React.FC<CitationRendererProps> = ({ children, onCitationClick }) => {
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

  // Process the text to replace citation markers with styled spans
  const processText = () => {
    if (!childrenAsString) return [];

    // Regular expression to find citation patterns like [1], [2], etc.
    const citationRegex = /\[(\d+)\]/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    // Find all citation matches and split text around them
    while ((match = citationRegex.exec(childrenAsString)) !== null) {
      // Add text before the citation
      if (match.index > lastIndex) {
        parts.push({ type: 'text', content: childrenAsString.substring(lastIndex, match.index) });
      }
      // Add the citation
      const citationNumber = parseInt(match[1], 10);
      console.log(`Found citation: [${match[1]}], parsed as number: ${citationNumber}`);
      parts.push({
        type: 'citation',
        content: match[0], // Keep the original citation format [n]
        index: citationNumber - 1, // Convert to 0-based index for array access
      });

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text after last citation
    if (lastIndex < childrenAsString.length) {
      parts.push({ type: 'text', content: childrenAsString.substring(lastIndex) });
    }

    return parts;
  };

  const parts = processText();

  return (
    <>
      {parts.map((part, index) => {
        if (part.type === 'citation') {
          return (
            <span
              key={index}
              className="citation"
              onClick={() => {
                console.log(`Citation clicked in renderer: ${part.index}`);
                onCitationClick(part.index as number);
              }}
            >
              {part.content}
            </span>
          );
        }
        return <React.Fragment key={index}>{part.content}</React.Fragment>;
      })}
    </>
  );
};

export default CitationRenderer;

import React from 'react';
import useClickOutside from '@/hooks/useClickOutside';

// Import convertMarkdownToHtml from ResearchTab
const convertMarkdownToHtml = (markdown: string): string => {
  if (!markdown) return '';

  const html = markdown
    // Convert headers
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')

    // Convert bold and italic
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    .replace(/_(.*?)_/g, '<em>$1</em>')

    // Convert links
    .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')

    // Convert lists
    .replace(/^\s*\n\* (.*)/gm, '<ul>\n<li>$1</li>\n</ul>')
    .replace(/^\s*\n- (.*)/gm, '<ul>\n<li>$1</li>\n</ul>')
    .replace(/^\s*\n\d+\. (.*)/gm, '<ol>\n<li>$1</li>\n</ol>')

    // Fix lists (multiple items)
    .replace(/<\/ul>\s*\n<ul>/g, '')
    .replace(/<\/ol>\s*\n<ol>/g, '')

    // Convert code blocks
    .replace(/```([^`]*?)```/g, '<pre><code>$1</code></pre>')

    // Convert inline code
    .replace(/`([^`]+?)`/g, '<code>$1</code>')

    // Convert paragraphs (2+ newlines followed by text)
    .replace(/\n\n([^\n]+)\n/g, '<p>$1</p>\n')

    // Convert single line breaks
    .replace(/\n/g, '<br />');

  return html;
};

interface ContextModalProps {
  isVisible: boolean;
  title: string;
  content: string;
  onClose: () => void;
  isHtml?: boolean;
  isMarkdown?: boolean; // New prop to identify markdown content
}

const ContextModal: React.FC<ContextModalProps> = ({
  isVisible,
  title,
  content,
  onClose,
  isHtml = false,
  isMarkdown = false, // Default to false
}) => {
  const modalRef = useClickOutside<HTMLDivElement>({
    onClickOutside: onClose,
    enabled: isVisible,
  });

  if (!isVisible) return null;

  // Convert markdown to HTML if isMarkdown is true
  const processedContent = isMarkdown ? convertMarkdownToHtml(content) : content;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {' '}
      <div
        ref={modalRef}
        className="animate-slide-in-right h-full w-[450px] overflow-auto bg-white shadow-xl"
        style={{
          transition: 'transform 0.3s ease-out',
          borderRadius: '20px 0px 0px 20px',
        }}
      >
        <div
          className="sticky top-0 z-10 flex items-center justify-between bg-white px-[30px] py-[28.5px]"
          style={{ borderBottom: '1px solid #9CBFBC' }}
        >
          <h2
            style={{
              color: '#002835',
              fontFamily: 'Inter',
              fontSize: '18px',
              fontWeight: 600,
            }}
          >
            {title || 'Context Details'}
          </h2>{' '}
          <button onClick={onClose} className="flex cursor-pointer items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="30"
              height="30"
              viewBox="0 0 30 30"
              fill="none"
              className="cursor-pointer"
            >
              <path
                d="M8 23.75L6.25 22L13.25 15L6.25 8L8 6.25L15 13.25L22 6.25L23.75 8L16.75 15L23.75 22L22 23.75L15 16.75L8 23.75Z"
                fill="#1D1B20"
              />
            </svg>
          </button>
        </div>{' '}
        {isHtml || isMarkdown ? (
          <div
            className="markdown-content px-[30px] py-[30px]"
            dangerouslySetInnerHTML={{ __html: processedContent }}
          />
        ) : (
          <div
            className="px-[30px] py-[30px] whitespace-pre-wrap"
            style={{
              color: '#002835',
              fontFamily: 'Inter',
              fontSize: '16px',
              fontStyle: 'normal',
              fontWeight: 400,
              lineHeight: '24px',
            }}
          >
            {content}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContextModal;

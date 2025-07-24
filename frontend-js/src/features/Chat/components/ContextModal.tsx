import React, { useState, useRef, useCallback, useEffect } from 'react';
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
  const [modalWidth, setModalWidth] = useState(450); // Initial width
  const [isResizing, setIsResizing] = useState(false);
  const resizeRef = useRef<HTMLDivElement>(null);
  const modalRef = useClickOutside<HTMLDivElement>({
    onClickOutside: onClose,
    enabled: isVisible && !isResizing, // Disable click outside when resizing
  });

  const MIN_WIDTH = 450;
  const MAX_WIDTH = window.innerWidth * 0.8; // 80% of screen width

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isResizing) return;

      const containerRect = document.body.getBoundingClientRect();
      const newWidth = containerRect.right - e.clientX;

      if (newWidth >= MIN_WIDTH && newWidth <= MAX_WIDTH) {
        setModalWidth(newWidth);
      }
    },
    [isResizing, MAX_WIDTH]
  );

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'ew-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);

  if (!isVisible) return null;

  // Convert markdown to HTML if isMarkdown is true
  const processedContent = isMarkdown ? convertMarkdownToHtml(content) : content;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Resize handle */}
      <div
        ref={resizeRef}
        className="absolute top-0 left-0 z-10 h-full w-1 cursor-ew-resize bg-transparent transition-colors hover:bg-gray-400"
        style={{
          right: `${modalWidth}px`,
        }}
        onMouseDown={handleMouseDown}
      />

      <div
        ref={modalRef}
        className="animate-slide-in-right relative h-full overflow-auto bg-white shadow-xl"
        style={{
          width: `${modalWidth}px`,
          minWidth: `${MIN_WIDTH}px`,
          maxWidth: `${MAX_WIDTH}px`,
          transition: isResizing ? 'none' : 'transform 0.3s ease-out',
          borderRadius: '20px 0px 0px 20px',
        }}
      >
        {/* Resize handle - left border */}
        <div
          className="absolute top-0 left-0 z-10 h-full w-2 cursor-ew-resize bg-transparent transition-colors hover:bg-gray-200"
          onMouseDown={handleMouseDown}
          style={{
            background: isResizing ? 'rgba(156, 191, 188, 0.3)' : 'transparent',
          }}
        />

        <div
          className="sticky top-0 z-10 flex items-center justify-between bg-white px-[30px] py-[28.5px]"
          style={{ borderBottom: '1px solid #9CBFBC' }}
        >
          <h2
            className="truncate pr-4" // Add truncate and padding for responsiveness
            style={{
              color: '#002835',
              fontFamily: 'Inter',
              fontSize: '18px',
              fontWeight: 600,
            }}
          >
            {title || 'Context Details'}
          </h2>
          <button
            onClick={onClose}
            className="flex flex-shrink-0 cursor-pointer items-center justify-center"
          >
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
        </div>

        {isHtml || isMarkdown ? (
          <div
            className="markdown-content px-[30px] py-[30px] break-words" // Add break-words for responsive text
            dangerouslySetInnerHTML={{ __html: processedContent }}
            style={{
              wordBreak: 'break-word', // Ensure long words break properly
              overflowWrap: 'break-word',
            }}
          />
        ) : (
          <div
            className="px-[30px] py-[30px] break-words whitespace-pre-wrap" // Add break-words for responsive text
            style={{
              color: '#002835',
              fontFamily: 'Inter',
              fontSize: '16px',
              fontStyle: 'normal',
              fontWeight: 400,
              lineHeight: '24px',
              wordBreak: 'break-word', // Ensure long words break properly
              overflowWrap: 'break-word',
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

import React, { useState } from 'react';
import { ChevronDown, ChevronRight, FileText, Tag, Hash } from 'lucide-react';
import type { DocumentCardProps } from '@/types/knowledgeBaseTypes';

const DocumentCard: React.FC<DocumentCardProps> = ({ document, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const truncateContent = (content: string, maxLength: number = 200) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
      {/* Document Header */}
      <button
        onClick={toggleExpanded}
        className="flex w-full items-start gap-3 p-3 text-left transition-colors duration-200 hover:bg-gray-50"
      >
        <div className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded bg-emerald-500 text-white">
          <FileText className="h-3 w-3" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-600">
              Doc {index + 1}
            </span>
            {document.metadata.section && (
              <span className="flex items-center gap-1 text-xs text-gray-600">
                <Tag className="h-3 w-3" />
                {document.metadata.section}
              </span>
            )}
            {document.metadata.page && (
              <span className="flex items-center gap-1 text-xs text-gray-600">
                <Hash className="h-3 w-3" />
                Page {document.metadata.page}
              </span>
            )}
          </div>
          <p className="mb-1 text-xs font-medium text-gray-700">
            Source: {document.metadata.source}
          </p>
          <p className="line-clamp-2 text-xs text-gray-600">
            {isExpanded ? document.content : truncateContent(document.content)}
          </p>
        </div>
        <div className="flex-shrink-0">
          {isExpanded ? (
            <ChevronDown className="h-4 w-4 text-gray-400" />
          ) : (
            <ChevronRight className="h-4 w-4 text-gray-400" />
          )}
        </div>
      </button>

      {/* Document Full Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50">
          <div className="p-3">
            <div className="text-xs leading-relaxed whitespace-pre-wrap text-gray-700">
              {document.content}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentCard;

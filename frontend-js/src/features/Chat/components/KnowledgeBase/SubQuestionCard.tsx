import React from 'react';
import { ChevronDown, ChevronRight, HelpCircle, FileText, Globe } from 'lucide-react';
import type { SubQuestionCardProps } from '@/types/knowledgeBaseTypes';
import DocumentCard from './DocumentCard';

const SubQuestionCard: React.FC<SubQuestionCardProps> = ({
  subQuestion,
  isExpanded,
  onToggle,
  questionIndex: _questionIndex,
}) => {
  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-gray-50">
      {/* Sub-Question Header */}
      <button
        onClick={onToggle}
        className="flex w-full items-start gap-3 p-3 text-left transition-colors duration-200 hover:bg-gray-100"
      >
        <div className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-indigo-500 text-white">
          <HelpCircle className="h-3 w-3" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium break-words text-gray-900">
            {subQuestion.sub_question}
          </p>
          <p className="mt-1 text-xs text-gray-600">
            {subQuestion.retrieved_docs.length} documents retrieved
          </p>
        </div>
        <div className="flex-shrink-0">
          {isExpanded ? (
            <ChevronDown className="h-4 w-4 text-gray-500" />
          ) : (
            <ChevronRight className="h-4 w-4 text-gray-500" />
          )}
        </div>
      </button>

      {/* Sub-Question Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-white">
          <div className="space-y-4 p-4">
            {/* Retrieved Documents */}
            {subQuestion.retrieved_docs.length > 0 && (
              <div className="space-y-3">
                <h6 className="flex items-center gap-2 font-medium text-gray-800">
                  <FileText className="h-4 w-4" />
                  Retrieved Documents ({subQuestion.retrieved_docs.length})
                </h6>
                <div className="max-h-60 space-y-2 overflow-y-auto">
                  {subQuestion.retrieved_docs.map((doc, index) => (
                    <DocumentCard key={index} document={doc} index={index} />
                  ))}
                </div>
              </div>
            )}

            {/* Global Summary */}
            <div className="rounded-lg border border-green-200 bg-green-50 p-3">
              <h6 className="mb-2 flex items-center gap-2 font-medium text-green-900">
                <Globe className="h-4 w-4" />
                Global Summary
              </h6>
              <p className="text-sm text-green-800">{subQuestion.global_summary}</p>
            </div>

            {/* Local Summary */}
            <div className="rounded-lg border border-blue-200 bg-blue-50 p-3">
              <h6 className="mb-2 flex items-center gap-2 font-medium text-blue-900">
                <FileText className="h-4 w-4" />
                Local Summary
              </h6>
              <p className="text-sm text-blue-800">{subQuestion.local_summary}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SubQuestionCard;

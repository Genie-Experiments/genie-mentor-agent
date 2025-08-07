import React from 'react';
import { Brain, CheckCircle, XCircle, FileQuestion, ArrowRight } from 'lucide-react';
import type { ReasonerOutputCardProps } from '@/types/knowledgeBaseTypes';

const ReasonerOutputCard: React.FC<ReasonerOutputCardProps> = ({ reasonerOutput }) => {
  return (
    <div className="overflow-hidden rounded-lg border border-amber-200 bg-amber-50">
      {/* Reasoner Header */}
      <div className="border-b border-amber-200 bg-amber-100 p-3">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-amber-700" />
          <h5 className="font-medium text-amber-900">Reasoning Analysis</h5>
          <div className="ml-auto flex items-center gap-2">
            {reasonerOutput.sufficient ? (
              <div className="flex items-center gap-1 text-green-700">
                <CheckCircle className="h-4 w-4" />
                <span className="text-xs font-medium">Sufficient</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 text-red-700">
                <XCircle className="h-4 w-4" />
                <span className="text-xs font-medium">Insufficient</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-4 p-4">
        {/* Reasoning */}
        <div>
          <h6 className="mb-2 font-medium text-amber-900">Reasoning</h6>
          <p className="rounded border border-amber-200 bg-white p-3 text-sm text-amber-800">
            {reasonerOutput.reasoning}
          </p>
        </div>

        {/* Required Documents */}
        {reasonerOutput.required_documents.length > 0 && (
          <div>
            <h6 className="mb-2 flex items-center gap-2 font-medium text-amber-900">
              <FileQuestion className="h-4 w-4" />
              Required Documents
            </h6>
            <div className="space-y-1">
              {reasonerOutput.required_documents.map((doc, index) => (
                <div
                  key={index}
                  className="rounded border border-amber-200 bg-white p-2 text-xs text-amber-800"
                >
                  {doc}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Documents in Context */}
        {reasonerOutput.documents_in_context.length > 0 && (
          <div>
            <h6 className="mb-2 flex items-center gap-2 font-medium text-amber-900">
              <CheckCircle className="h-4 w-4" />
              Documents in Context
            </h6>
            <div className="space-y-1">
              {reasonerOutput.documents_in_context.map((doc, index) => (
                <div
                  key={index}
                  className="rounded border border-green-200 bg-green-50 p-2 text-xs text-green-800"
                >
                  {doc}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Next Sub-Questions */}
        {reasonerOutput.next_sub_questions.length > 0 && (
          <div>
            <h6 className="mb-2 flex items-center gap-2 font-medium text-amber-900">
              <ArrowRight className="h-4 w-4" />
              Next Sub-Questions
            </h6>
            <div className="space-y-2">
              {reasonerOutput.next_sub_questions.map((question, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2 rounded border border-blue-200 bg-blue-50 p-2 text-xs text-blue-800"
                >
                  <span className="flex-shrink-0 font-medium text-blue-600">{index + 1}.</span>
                  <span>{question}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReasonerOutputCard;

import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Brain, Search, FileText, AlertCircle } from 'lucide-react';
import type { HopCardProps } from '@/types/knowledgeBaseTypes';
import SubQuestionCard from './SubQuestionCard';
import ReasonerOutputCard from './ReasonerOutputCard';
import MemoryDisplay from './MemoryDisplay';

const HopCard: React.FC<HopCardProps> = ({ hop, isExpanded, onToggle, hopIndex: _hopIndex }) => {
  const [expandedSubQuestions, setExpandedSubQuestions] = useState<Set<number>>(new Set());

  const toggleSubQuestion = (questionIndex: number) => {
    setExpandedSubQuestions((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(questionIndex)) {
        newSet.delete(questionIndex);
      } else {
        newSet.add(questionIndex);
      }
      return newSet;
    });
  };

  const getHopIcon = () => {
    if (hop.hop === 'final') return <Brain className="h-5 w-5" />;
    return <Search className="h-5 w-5" />;
  };

  const getHopTitle = () => {
    if (hop.hop === 'final') return 'Final Answer Generation';
    return `Research Hop ${hop.hop}`;
  };

  const getHopColor = () => {
    if (hop.hop === 'final') return 'bg-purple-500';
    return 'bg-blue-500';
  };

  const getHopBgColor = () => {
    if (hop.hop === 'final') return 'bg-purple-50 border-purple-200';
    return 'bg-blue-50 border-blue-200';
  };

  return (
    <div
      className={`overflow-hidden rounded-lg border transition-all duration-200 ${getHopBgColor()}`}
    >
      {/* Hop Header */}
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between p-4 text-left transition-colors duration-200 hover:bg-white/50"
      >
        <div className="flex items-center gap-3">
          <div
            className={`flex h-8 w-8 items-center justify-center ${getHopColor()} rounded-full text-white`}
          >
            {getHopIcon()}
          </div>
          <div>
            <h4 className="font-semibold text-gray-900">{getHopTitle()}</h4>
            {hop.sub_questions && (
              <p className="text-sm text-gray-600">
                {hop.sub_questions.length} sub-question{hop.sub_questions.length !== 1 ? 's' : ''}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {hop.reasoner_output && !hop.reasoner_output.sufficient && (
            <AlertCircle className="h-4 w-4 text-amber-500" />
          )}
          {isExpanded ? (
            <ChevronDown className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-500" />
          )}
        </div>
      </button>

      {/* Hop Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-white">
          <div className="space-y-4 p-4">
            {/* Sub-Questions */}
            {hop.sub_questions && hop.sub_questions.length > 0 && (
              <div className="space-y-3">
                <h5 className="flex items-center gap-2 font-medium text-gray-800">
                  <FileText className="h-4 w-4" />
                  Sub-Questions & Research
                </h5>
                {hop.sub_questions.map((subQuestion, index) => (
                  <SubQuestionCard
                    key={index}
                    subQuestion={subQuestion}
                    questionIndex={index}
                    isExpanded={expandedSubQuestions.has(index)}
                    onToggle={() => toggleSubQuestion(index)}
                  />
                ))}
              </div>
            )}

            {/* Final Generator (for final hop) */}
            {hop.generator && (
              <div className="rounded-lg border border-purple-200 bg-purple-50 p-4">
                <h5 className="mb-2 font-medium text-purple-900">Generated Response</h5>
                <div className="text-sm whitespace-pre-wrap text-purple-800">{hop.generator}</div>
              </div>
            )}

            {/* Reasoner Output */}
            {hop.reasoner_output && <ReasonerOutputCard reasonerOutput={hop.reasoner_output} />}

            {/* Memory Display */}
            {(hop.global_memory || hop.local_memory) && (
              <MemoryDisplay globalMemory={hop.global_memory} localMemory={hop.local_memory} />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default HopCard;

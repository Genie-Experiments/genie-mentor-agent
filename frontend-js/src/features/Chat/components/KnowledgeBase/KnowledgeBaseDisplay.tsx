import React, { useState } from 'react';
import { Brain, BookOpen } from 'lucide-react';
import type { KnowledgeBaseDisplayProps } from '@/types/knowledgeBaseTypes';
import HopCard from './HopCard';

const KnowledgeBaseDisplay: React.FC<KnowledgeBaseDisplayProps> = ({
  executorAgent,
  finalAnswer,
}) => {
  const [expandedHops, setExpandedHops] = useState<Set<number>>(new Set([0]));

  const toggleHop = (hopIndex: number) => {
    setExpandedHops((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(hopIndex)) {
        newSet.delete(hopIndex);
      } else {
        newSet.add(hopIndex);
      }
      return newSet;
    });
  };

  return (
    <div className="w-full space-y-4">
      {/* Knowledge Base Header */}
      <div className="flex items-center gap-3 rounded-lg border border-emerald-200 bg-gradient-to-r from-emerald-50 to-teal-50 p-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500">
          <BookOpen className="h-5 w-5 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-emerald-900">Knowledge Base Research</h3>
          <p className="text-sm text-emerald-700">
            {executorAgent.num_hops} research hops completed
          </p>
        </div>
      </div>

      {/* Research Hops */}
      <div className="space-y-3">
        {executorAgent.trace.map((hop, index) => (
          <HopCard
            key={`hop-${index}`}
            hop={hop}
            hopIndex={index}
            isExpanded={expandedHops.has(index)}
            onToggle={() => toggleHop(index)}
          />
        ))}
      </div>

      {/* Final Answer Section */}
      <div className="mt-6 rounded-xl border border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
        <div className="mb-4 flex items-center gap-2">
          <Brain className="h-6 w-6 text-blue-600" />
          <h3 className="text-lg font-semibold text-blue-900">Synthesized Answer</h3>
        </div>
        <div className="prose prose-sm max-w-none text-gray-800">{finalAnswer}</div>
      </div>
    </div>
  );
};

export default KnowledgeBaseDisplay;

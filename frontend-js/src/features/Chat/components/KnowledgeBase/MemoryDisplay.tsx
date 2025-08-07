import React, { useState } from 'react';
import { Brain, Database, ChevronDown, ChevronRight, MemoryStick } from 'lucide-react';
import type { MemoryDisplayProps } from '@/types/knowledgeBaseTypes';

const MemoryDisplay: React.FC<MemoryDisplayProps> = ({ globalMemory, localMemory }) => {
  const [isGlobalExpanded, setIsGlobalExpanded] = useState(false);
  const [isLocalExpanded, setIsLocalExpanded] = useState(false);

  if (!globalMemory?.length && !localMemory?.length) {
    return null;
  }

  return (
    <div className="space-y-3">
      <h5 className="flex items-center gap-2 font-medium text-gray-800">
        <MemoryStick className="h-4 w-4" />
        Memory Systems
      </h5>

      {/* Global Memory */}
      {globalMemory && globalMemory.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-purple-200 bg-purple-50">
          <button
            onClick={() => setIsGlobalExpanded(!isGlobalExpanded)}
            className="flex w-full items-center justify-between p-3 text-left transition-colors duration-200 hover:bg-purple-100"
          >
            <div className="flex items-center gap-2">
              <Brain className="h-4 w-4 text-purple-600" />
              <span className="font-medium text-purple-900">
                Global Memory ({globalMemory.length} entries)
              </span>
            </div>
            {isGlobalExpanded ? (
              <ChevronDown className="h-4 w-4 text-purple-600" />
            ) : (
              <ChevronRight className="h-4 w-4 text-purple-600" />
            )}
          </button>

          {isGlobalExpanded && (
            <div className="border-t border-purple-200 bg-white">
              <div className="space-y-2 p-3">
                {globalMemory.map((entry, index) => (
                  <div key={index} className="rounded border border-purple-200 bg-purple-50 p-2">
                    <div className="mb-1 text-xs font-medium text-purple-600">
                      Entry {index + 1}
                    </div>
                    <div className="text-xs text-purple-800">{entry}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Local Memory */}
      {localMemory && localMemory.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-teal-200 bg-teal-50">
          <button
            onClick={() => setIsLocalExpanded(!isLocalExpanded)}
            className="flex w-full items-center justify-between p-3 text-left transition-colors duration-200 hover:bg-teal-100"
          >
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-teal-600" />
              <span className="font-medium text-teal-900">
                Local Memory ({localMemory.length} entries)
              </span>
            </div>
            {isLocalExpanded ? (
              <ChevronDown className="h-4 w-4 text-teal-600" />
            ) : (
              <ChevronRight className="h-4 w-4 text-teal-600" />
            )}
          </button>

          {isLocalExpanded && (
            <div className="border-t border-teal-200 bg-white">
              <div className="space-y-3 p-3">
                {localMemory.map((entry, index) => (
                  <div key={index} className="rounded border border-teal-200 bg-teal-50 p-3">
                    <div className="mb-2 text-xs font-medium text-teal-600">
                      Q: {entry.sub_question}
                    </div>
                    <div className="rounded border border-teal-200 bg-white p-2 text-xs text-teal-800">
                      A: {entry.response}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MemoryDisplay;

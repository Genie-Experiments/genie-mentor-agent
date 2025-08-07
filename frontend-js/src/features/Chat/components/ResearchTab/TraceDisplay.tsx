import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Search, Brain, FileText } from 'lucide-react';
import { RESEARCH_STYLES } from '@/constant/researchTab';
import type { TraceDisplayProps, TraceHop } from '@/types/knowledgeBaseTypes';

export const TraceDisplay: React.FC<TraceDisplayProps> = ({
  trace,
  numHops,
  agentType,
  agentIndex,
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

  const getHopTitle = (hop: TraceHop) => {
    if (hop.hop === 'final') return 'Final Synthesis';
    return `Research Hop ${hop.hop}`;
  };

  const getHopIcon = (hop: TraceHop) => {
    if (hop.hop === 'final') return <Brain size={14} style={{ color: '#6366F1' }} />;
    return <Search size={14} style={{ color: '#0EA5E9' }} />;
  };

  const agentLabel = agentType === 'executor' ? 'Executor' : `Evaluator ${agentIndex || ''}`;

  return (
    <div style={{ marginBottom: '16px' }}>
      {/* Section Header */}
      <div
        style={{
          ...RESEARCH_STYLES.key,
          marginBottom: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}
      >
        <FileText size={16} style={{ color: '#00A599' }} />
        <span>
          {agentLabel} Knowledge Base Research ({numHops} hops)
        </span>
      </div>

      {/* Trace Hops */}
      <div
        style={{
          border: '1px solid #E5E7EB',
          borderRadius: '6px',
          overflow: 'hidden',
          backgroundColor: '#FAFAFA',
        }}
      >
        {trace.map((hop, index) => (
          <div
            key={index}
            style={{
              borderBottom: index < trace.length - 1 ? '1px solid #E5E7EB' : 'none',
            }}
          >
            {/* Hop Header */}
            <button
              onClick={() => toggleHop(index)}
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: 'transparent',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontSize: '14px',
                fontFamily: 'Inter',
                transition: 'background-color 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#F3F4F6';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {getHopIcon(hop)}
                <span style={{ fontWeight: 500, color: '#374151' }}>{getHopTitle(hop)}</span>
                {hop.sub_questions && (
                  <span style={{ fontSize: '12px', color: '#6B7280' }}>
                    ({hop.sub_questions.length} questions)
                  </span>
                )}
              </div>
              {expandedHops.has(index) ? (
                <ChevronDown size={16} style={{ color: '#6B7280' }} />
              ) : (
                <ChevronRight size={16} style={{ color: '#6B7280' }} />
              )}
            </button>

            {/* Hop Content */}
            {expandedHops.has(index) && (
              <div
                style={{
                  padding: '0 16px 16px 16px',
                  backgroundColor: '#FFFFFF',
                  borderTop: '1px solid #E5E7EB',
                }}
              >
                {/* Sub-questions */}
                {hop.sub_questions && hop.sub_questions.length > 0 && (
                  <div style={{ marginBottom: '12px' }}>
                    <div
                      style={{
                        ...RESEARCH_STYLES.key,
                        fontSize: '13px',
                        marginBottom: '6px',
                      }}
                    >
                      Research Questions:
                    </div>
                    {hop.sub_questions.map((sq, sqIndex) => (
                      <div
                        key={sqIndex}
                        style={{
                          padding: '8px 12px',
                          backgroundColor: '#F8FAFC',
                          border: '1px solid #E2E8F0',
                          borderRadius: '4px',
                          marginBottom: '6px',
                        }}
                      >
                        <div
                          style={{
                            fontSize: '13px',
                            fontWeight: 500,
                            color: '#334155',
                            marginBottom: '4px',
                          }}
                        >
                          Q{sqIndex + 1}: {sq.sub_question}
                        </div>
                        <div
                          style={{
                            fontSize: '12px',
                            color: '#64748B',
                          }}
                        >
                          {sq.retrieved_docs.length} documents retrieved
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Reasoner Output */}
                {hop.reasoner_output && (
                  <div
                    style={{
                      padding: '8px 12px',
                      backgroundColor: hop.reasoner_output.sufficient ? '#F0FDF4' : '#FEF3F2',
                      border: hop.reasoner_output.sufficient
                        ? '1px solid #BBF7D0'
                        : '1px solid #FECACA',
                      borderRadius: '4px',
                      marginBottom: '8px',
                    }}
                  >
                    <div
                      style={{
                        fontSize: '12px',
                        fontWeight: 500,
                        color: hop.reasoner_output.sufficient ? '#166534' : '#991B1B',
                        marginBottom: '4px',
                      }}
                    >
                      Status:{' '}
                      {hop.reasoner_output.sufficient ? 'Sufficient' : 'Needs More Information'}
                    </div>
                    <div
                      style={{
                        fontSize: '12px',
                        color: '#4B5563',
                      }}
                    >
                      {hop.reasoner_output.reasoning}
                    </div>
                  </div>
                )}

                {/* Final Generator */}
                {hop.generator && (
                  <div
                    style={{
                      padding: '8px 12px',
                      backgroundColor: '#F3F4F6',
                      border: '1px solid #D1D5DB',
                      borderRadius: '4px',
                      fontSize: '12px',
                      color: '#374151',
                    }}
                  >
                    <strong>Generated Response:</strong> {hop.generator.substring(0, 200)}...
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

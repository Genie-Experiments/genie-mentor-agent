import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChevronDown, ChevronRight, Database, Search, Brain, AlertCircle } from 'lucide-react';
import { LLMUsageDisplay } from './LLMUsageDisplay';
import { KeyValueRow } from './KeyValueRow';
import { ViewDetailsButton } from './ViewDetailsButton';
import { RESEARCH_STYLES, SECTION_TITLES, FIELD_LABELS } from '@/constant/researchTab';
import type { ExecutorAgentEnhanced } from '@/types/knowledgeBaseTypes';

interface KnowledgeBaseAgentSectionProps {
  knowledgeBaseAgent: ExecutorAgentEnhanced;
  onViewDetails?: (agent: ExecutorAgentEnhanced) => void;
}

export const KnowledgeBaseAgentSection: React.FC<KnowledgeBaseAgentSectionProps> = ({
  knowledgeBaseAgent,
  onViewDetails,
}) => {
  const [expandedHops, setExpandedHops] = useState<Set<number>>(new Set());
  const [expandedContent, setExpandedContent] = useState<Set<string>>(new Set());

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

  const toggleContent = (contentId: string) => {
    setExpandedContent((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(contentId)) {
        newSet.delete(contentId);
      } else {
        newSet.add(contentId);
      }
      return newSet;
    });
  };

  const truncateText = (text: string, maxLength: number = 300) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const renderTruncatedContent = (content: string, contentId: string, maxLength: number = 300) => {
    const isExpanded = expandedContent.has(contentId);
    const shouldTruncate = content.length > maxLength;

    if (!shouldTruncate) return content;

    return (
      <div>
        <div>{isExpanded ? content : truncateText(content, maxLength)}</div>
        <button
          onClick={() => toggleContent(contentId)}
          style={{
            background: 'none',
            border: 'none',
            color: '#3B82F6',
            cursor: 'pointer',
            fontSize: '14px',
            marginTop: '8px',
            padding: '4px 0',
            textDecoration: 'underline',
            fontFamily: 'Inter, sans-serif',
          }}
        >
          {isExpanded ? 'Show less' : 'Show more'}
        </button>
      </div>
    );
  };

  const renderMarkdownContent = (content: string, contentId: string, maxLength: number = 300) => {
    const isExpanded = expandedContent.has(contentId);
    const shouldTruncate = content.length > maxLength;
    const displayContent =
      shouldTruncate && !isExpanded ? truncateText(content, maxLength) : content;

    return (
      <div>
        <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({ children }) => <p style={{ margin: '8px 0' }}>{children}</p>,
              strong: ({ children }) => <strong style={{ fontWeight: 600 }}>{children}</strong>,
              em: ({ children }) => <em style={{ fontStyle: 'italic' }}>{children}</em>,
              ul: ({ children }) => (
                <ul style={{ marginLeft: '16px', marginBottom: '8px' }}>{children}</ul>
              ),
              ol: ({ children }) => (
                <ol style={{ marginLeft: '16px', marginBottom: '8px' }}>{children}</ol>
              ),
              li: ({ children }) => <li style={{ marginBottom: '4px' }}>{children}</li>,
              h1: ({ children }) => (
                <h1 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px' }}>
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '6px' }}>
                  {children}
                </h3>
              ),
              code: ({ children }) => (
                <code
                  style={{
                    backgroundColor: '#F3F4F6',
                    padding: '2px 4px',
                    borderRadius: '3px',
                    fontSize: '13px',
                    fontFamily: 'monospace',
                  }}
                >
                  {children}
                </code>
              ),
              blockquote: ({ children }) => (
                <blockquote
                  style={{
                    borderLeft: '3px solid #D1D5DB',
                    paddingLeft: '12px',
                    margin: '8px 0',
                    fontStyle: 'italic',
                    color: '#6B7280',
                  }}
                >
                  {children}
                </blockquote>
              ),
              table: ({ children }) => (
                <table
                  style={{
                    width: '100%',
                    borderCollapse: 'collapse',
                    margin: '8px 0',
                    fontSize: '13px',
                  }}
                >
                  {children}
                </table>
              ),
              th: ({ children }) => (
                <th
                  style={{
                    border: '1px solid #D1D5DB',
                    padding: '6px 8px',
                    backgroundColor: '#F9FAFB',
                    fontWeight: 600,
                    textAlign: 'left',
                  }}
                >
                  {children}
                </th>
              ),
              td: ({ children }) => (
                <td
                  style={{
                    border: '1px solid #D1D5DB',
                    padding: '6px 8px',
                  }}
                >
                  {children}
                </td>
              ),
            }}
          >
            {displayContent}
          </ReactMarkdown>
        </div>
        {shouldTruncate && (
          <button
            onClick={() => toggleContent(contentId)}
            style={{
              background: 'none',
              border: 'none',
              color: '#3B82F6',
              cursor: 'pointer',
              fontSize: '14px',
              marginTop: '8px',
              padding: '4px 0',
              textDecoration: 'underline',
              fontFamily: 'Inter, sans-serif',
            }}
          >
            {isExpanded ? 'Show less' : 'Show more'}
          </button>
        )}
      </div>
    );
  };

  const renderSubQuestionsList = (
    subQuestions: Array<
      { sub_question?: string; global_summary?: string; local_summary?: string } | string
    >
  ) => {
    return (
      <ol
        style={{
          margin: '8px 0',
          paddingLeft: '20px',
          listStyleType: 'decimal',
        }}
      >
        {subQuestions.map((sq, index) => (
          <li
            key={index}
            style={{
              ...RESEARCH_STYLES.value,
              marginBottom: '4px',
              lineHeight: '1.4',
            }}
          >
            {typeof sq === 'string' ? sq : sq.sub_question || ''}
          </li>
        ))}
      </ol>
    );
  };

  const getHopIcon = (hopNumber: number | 'final') => {
    if (hopNumber === 'final') return <Brain style={{ width: '16px', height: '16px' }} />;
    return <Search style={{ width: '16px', height: '16px' }} />;
  };

  const getHopTitle = (hopNumber: number | 'final') => {
    if (hopNumber === 'final') return 'Final Answer Generation';
    return `Research Hop ${hopNumber}`;
  };

  const getHopStatusColor = (hop: {
    hop: number | 'final';
    reasoner_output?: { sufficient: boolean };
  }) => {
    if (hop.reasoner_output && !hop.reasoner_output.sufficient) {
      return '#F59E0B'; // amber
    }
    if (hop.hop === 'final') {
      return '#8B5CF6'; // purple
    }
    return '#3B82F6'; // blue
  };

  return (
    <React.Fragment>
      <div style={RESEARCH_STYLES.sectionTitle}>{SECTION_TITLES.KNOWLEDGE_BASE_AGENT}</div>

      {/* Agent Overview */}
      <LLMUsageDisplay
        llmUsage={knowledgeBaseAgent.llm_usage}
        executionTimeMs={knowledgeBaseAgent.execution_time_ms || 0}
      />

      {/* Knowledge Base Summary */}
      <div style={{ marginBottom: '16px' }}>
        <KeyValueRow
          keyText={FIELD_LABELS.RESEARCH_HOPS}
          value={`${knowledgeBaseAgent.num_hops || 0} hops completed`}
        />

        {Boolean(knowledgeBaseAgent.error) && (
          <KeyValueRow keyText={FIELD_LABELS.ERROR} value="Error occurred" />
        )}
      </div>

      {/* Research Hops Drawer */}
      {knowledgeBaseAgent.trace && knowledgeBaseAgent.trace.length > 0 && (
        <div style={{ marginBottom: '16px' }}>
          <div
            style={{
              ...RESEARCH_STYLES.key,
              marginBottom: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <Database style={{ width: '16px', height: '16px' }} />
            Research Trace ({
              knowledgeBaseAgent.trace.filter((hop) => hop.hop !== 'final').length
            }{' '}
            hops)
          </div>

          <div
            style={{
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              backgroundColor: '#F9FAFB',
              overflow: 'hidden',
            }}
          >
            {knowledgeBaseAgent.trace
              .filter((hop) => hop.hop !== 'final')
              .map((hop, index) => {
                const isExpanded = expandedHops.has(index);
                const hopStatusColor = getHopStatusColor(hop);
                const filteredTrace = knowledgeBaseAgent.trace.filter((hop) => hop.hop !== 'final');

                return (
                  <div
                    key={index}
                    style={{
                      borderBottom: index < filteredTrace.length - 1 ? '1px solid #E5E7EB' : 'none',
                    }}
                  >
                    {/* Hop Header */}
                    <button
                      onClick={() => toggleHop(index)}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        backgroundColor: isExpanded ? '#FFFFFF' : 'transparent',
                        border: 'none',
                        textAlign: 'left',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        transition: 'background-color 0.2s ease',
                        fontFamily: 'Inter, sans-serif',
                      }}
                      onMouseEnter={(e) => {
                        if (!isExpanded) {
                          e.currentTarget.style.backgroundColor = '#F3F4F6';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!isExpanded) {
                          e.currentTarget.style.backgroundColor = 'transparent';
                        }
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div
                          style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '50%',
                            backgroundColor: hopStatusColor,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#FFFFFF',
                          }}
                        >
                          {getHopIcon(hop.hop)}
                        </div>
                        <div>
                          <div
                            style={{
                              ...RESEARCH_STYLES.value,
                              fontWeight: 500,
                              marginBottom: '2px',
                            }}
                          >
                            {getHopTitle(hop.hop)}
                          </div>
                          {hop.sub_questions && (
                            <div
                              style={{
                                ...RESEARCH_STYLES.key,
                                fontSize: '14px',
                                opacity: 0.7,
                              }}
                            >
                              {hop.sub_questions.length} sub-question
                              {hop.sub_questions.length !== 1 ? 's' : ''}
                            </div>
                          )}
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {hop.reasoner_output && !hop.reasoner_output.sufficient && (
                          <AlertCircle
                            style={{ width: '16px', height: '16px', color: '#F59E0B' }}
                          />
                        )}
                        {isExpanded ? (
                          <ChevronDown
                            style={{ width: '20px', height: '20px', color: '#6B7280' }}
                          />
                        ) : (
                          <ChevronRight
                            style={{ width: '20px', height: '20px', color: '#6B7280' }}
                          />
                        )}
                      </div>
                    </button>

                    {/* Hop Content */}
                    {isExpanded && (
                      <div
                        style={{
                          padding: '16px',
                          backgroundColor: '#FFFFFF',
                          borderTop: '1px solid #E5E7EB',
                        }}
                      >
                        {/* Sub-Questions with Expanded Details */}
                        {hop.sub_questions && hop.sub_questions.length > 0 && (
                          <div style={{ marginBottom: '16px' }}>
                            <div
                              style={{
                                ...RESEARCH_STYLES.key,
                                marginBottom: '8px',
                                fontWeight: 500,
                              }}
                            >
                              {FIELD_LABELS.SUB_QUESTIONS} ({hop.sub_questions.length})
                            </div>
                            {renderSubQuestionsList(hop.sub_questions)}

                            {/* Show summaries if available in sub-questions */}
                            {hop.sub_questions.some(
                              (sq) => sq.global_summary || sq.local_summary
                            ) && (
                              <div style={{ marginTop: '12px' }}>
                                {hop.sub_questions.map((sq, sqIndex) => (
                                  <div key={sqIndex}>
                                    {sq.global_summary && (
                                      <div style={{ marginBottom: '12px' }}>
                                        <div
                                          style={{
                                            ...RESEARCH_STYLES.key,
                                            marginBottom: '8px',
                                            fontWeight: 500,
                                          }}
                                        >
                                          Global Summary - Question {sqIndex + 1}
                                        </div>
                                        <div
                                          style={{
                                            ...RESEARCH_STYLES.value,
                                            backgroundColor: '#F0F9FF',
                                            padding: '12px',
                                            borderRadius: '6px',
                                            border: '1px solid #BAE6FD',
                                            lineHeight: '1.5',
                                          }}
                                        >
                                          {renderMarkdownContent(
                                            sq.global_summary,
                                            `global-summary-${index}-${sqIndex}`
                                          )}
                                        </div>
                                      </div>
                                    )}

                                    {sq.local_summary && (
                                      <div style={{ marginBottom: '12px' }}>
                                        <div
                                          style={{
                                            ...RESEARCH_STYLES.key,
                                            marginBottom: '8px',
                                            fontWeight: 500,
                                          }}
                                        >
                                          Local Summary - Question {sqIndex + 1}
                                        </div>
                                        <div
                                          style={{
                                            ...RESEARCH_STYLES.value,
                                            backgroundColor: '#F0FDF4',
                                            padding: '12px',
                                            borderRadius: '6px',
                                            border: '1px solid #BBF7D0',
                                            lineHeight: '1.5',
                                          }}
                                        >
                                          {renderMarkdownContent(
                                            sq.local_summary,
                                            `local-summary-${index}-${sqIndex}`
                                          )}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Generated Response (for final hop) */}
                        {hop.generator && (
                          <div style={{ marginBottom: '16px' }}>
                            <div
                              style={{
                                ...RESEARCH_STYLES.key,
                                marginBottom: '8px',
                                fontWeight: 500,
                              }}
                            >
                              Final Generated Response
                            </div>
                            <div
                              style={{
                                ...RESEARCH_STYLES.value,
                                backgroundColor: '#F8FAFC',
                                padding: '12px',
                                borderRadius: '6px',
                                border: '1px solid #E2E8F0',
                                lineHeight: '1.5',
                              }}
                            >
                              {renderTruncatedContent(hop.generator, `generator-${index}`)}
                            </div>
                          </div>
                        )}

                        {/* Reasoner Output */}
                        {hop.reasoner_output && (
                          <div style={{ marginBottom: '16px' }}>
                            <div
                              style={{
                                ...RESEARCH_STYLES.key,
                                marginBottom: '8px',
                                fontWeight: 500,
                              }}
                            >
                              Reasoning Analysis
                            </div>
                            <div
                              style={{
                                backgroundColor: '#FFFBEB',
                                padding: '12px',
                                borderRadius: '6px',
                                border: '1px solid #FED7AA',
                              }}
                            >
                              <KeyValueRow
                                keyText={FIELD_LABELS.REASONING_SUFFICIENT}
                                value={hop.reasoner_output.sufficient ? 'Yes' : 'No'}
                              />
                              {hop.reasoner_output.reasoning && (
                                <div style={{ marginTop: '8px' }}>
                                  <div style={{ ...RESEARCH_STYLES.key, marginBottom: '4px' }}>
                                    Reasoning:
                                  </div>
                                  <div style={RESEARCH_STYLES.value}>
                                    {renderTruncatedContent(
                                      hop.reasoner_output.reasoning,
                                      `reasoning-${index}`
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Memory Information */}
                        {hop.global_memory && hop.global_memory.length > 0 && (
                          <div style={{ marginBottom: '12px' }}>
                            <KeyValueRow
                              keyText="Global Memory Items"
                              value={`${hop.global_memory.length} items stored`}
                            />
                          </div>
                        )}

                        {hop.local_memory && hop.local_memory.length > 0 && (
                          <KeyValueRow
                            keyText="Local Memory Items"
                            value={`${hop.local_memory.length} items stored`}
                          />
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* View Details Button */}
      <ViewDetailsButton
        onClick={() => onViewDetails?.(knowledgeBaseAgent)}
        text="View Knowledge Base Research Details"
      />
    </React.Fragment>
  );
};

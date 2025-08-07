import React, { useState } from 'react';
import {
  ChevronDown,
  ChevronRight,
  Target,
  AlertTriangle,
  CheckCircle,
  Database,
} from 'lucide-react';
import { LLMUsageDisplay } from './LLMUsageDisplay';
import { KeyValueRow } from './KeyValueRow';
import { ViewDetailsButton } from './ViewDetailsButton';
import { RESEARCH_STYLES, SECTION_TITLES, FIELD_LABELS } from '@/constant/researchTab';
import { isEvaluatorKnowledgeBase } from '@/utils/knowledgeBaseUtils';
import type { EvaluatorAgentEnhanced } from '@/types/knowledgeBaseTypes';
import type { LLMUsage } from '@/lib/api-service';

interface DetailedEvaluatorAgentSectionProps {
  evaluators: EvaluatorAgentEnhanced[];
  onViewDetails?: (agent: EvaluatorAgentEnhanced) => void;
}

export const DetailedEvaluatorAgentSection: React.FC<DetailedEvaluatorAgentSectionProps> = ({
  evaluators,
  onViewDetails,
}) => {
  const [expandedEvaluators, setExpandedEvaluators] = useState<Set<number>>(new Set());
  const [expandedAttempts, setExpandedAttempts] = useState<Set<string>>(new Set());

  const toggleEvaluator = (evaluatorIndex: number) => {
    setExpandedEvaluators((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(evaluatorIndex)) {
        newSet.delete(evaluatorIndex);
      } else {
        newSet.add(evaluatorIndex);
      }
      return newSet;
    });
  };

  const toggleAttempt = (evaluatorIndex: number, attemptIndex: number) => {
    const key = `${evaluatorIndex}-${attemptIndex}`;
    setExpandedAttempts((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(key)) {
        newSet.delete(key);
      } else {
        newSet.add(key);
      }
      return newSet;
    });
  };

  const getScoreColor = (score: number | string) => {
    const numScore = typeof score === 'string' ? parseFloat(score) : score;
    if (numScore >= 8) return '#10B981'; // green
    if (numScore >= 6) return '#F59E0B'; // amber
    return '#EF4444'; // red
  };

  const getAttemptIcon = (attempt: any, hasError: boolean) => {
    if (hasError) return <AlertTriangle style={{ width: '16px', height: '16px' }} />;
    if (attempt.score && parseFloat(attempt.score) >= 8) {
      return <CheckCircle style={{ width: '16px', height: '16px' }} />;
    }
    return <Target style={{ width: '16px', height: '16px' }} />;
  };

  return (
    <React.Fragment>
      <div style={RESEARCH_STYLES.sectionTitle}>{SECTION_TITLES.EVALUATOR_AGENT}</div>

      {evaluators.map((evaluator, evaluatorIndex) => {
        const hasKnowledgeBase = isEvaluatorKnowledgeBase(evaluator);
        const isEvaluatorExpanded = expandedEvaluators.has(evaluatorIndex);
        const evaluationHistory = evaluator.evaluation_history || [];

        return (
          <div
            key={evaluatorIndex}
            style={{
              marginBottom: evaluatorIndex < evaluators.length - 1 ? '24px' : '0',
            }}
          >
            {/* LLM Usage Display */}
            {(() => {
              const historyObj = evaluator.evaluation_history as unknown as Record<string, unknown>;
              const llmUsage = historyObj?.llm_usage as LLMUsage;
              return (
                llmUsage && (
                  <div style={{ marginBottom: '8px' }}>
                    <LLMUsageDisplay
                      llmUsage={llmUsage}
                      executionTimeMs={evaluator.execution_time_ms || 0}
                    />
                  </div>
                )
              );
            })()}

            <div
              style={{
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                overflow: 'hidden',
              }}
            >
              {/* Evaluator Header */}
              <button
                onClick={() => toggleEvaluator(evaluatorIndex)}
                style={{
                  width: '100%',
                  padding: '16px',
                  backgroundColor: isEvaluatorExpanded ? '#F9FAFB' : '#FFFFFF',
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
                  if (!isEvaluatorExpanded) {
                    e.currentTarget.style.backgroundColor = '#F9FAFB';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isEvaluatorExpanded) {
                    e.currentTarget.style.backgroundColor = '#FFFFFF';
                  }
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div
                    style={{
                      ...RESEARCH_STYLES.key,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                  >
                    <span>Evaluator Agent #{evaluatorIndex + 1}</span>
                    {hasKnowledgeBase && (
                      <span
                        style={{
                          fontSize: '12px',
                          backgroundColor: '#E0F2FE',
                          color: '#0369A1',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontWeight: 500,
                        }}
                      >
                        Knowledge Base
                      </span>
                    )}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {evaluationHistory.length > 0 && (
                    <span
                      style={{
                        fontSize: '12px',
                        backgroundColor: '#F3F4F6',
                        color: '#374151',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontWeight: 500,
                      }}
                    >
                      {evaluationHistory.length} attempt{evaluationHistory.length !== 1 ? 's' : ''}
                    </span>
                  )}
                  {Boolean(evaluator.error) && (
                    <AlertTriangle style={{ width: '16px', height: '16px', color: '#EF4444' }} />
                  )}
                  {isEvaluatorExpanded ? (
                    <ChevronDown style={{ width: '20px', height: '20px', color: '#6B7280' }} />
                  ) : (
                    <ChevronRight style={{ width: '20px', height: '20px', color: '#6B7280' }} />
                  )}
                </div>
              </button>

              {/* Evaluator Content */}
              {isEvaluatorExpanded && (
                <div
                  style={{
                    padding: '16px',
                    backgroundColor: '#FFFFFF',
                    borderTop: '1px solid #E5E7EB',
                  }}
                >
                  {/* Knowledge Base Summary */}
                  {hasKnowledgeBase && (
                    <div style={{ marginBottom: '16px' }}>
                      {evaluator.num_hops && (
                        <KeyValueRow
                          keyText={FIELD_LABELS.RESEARCH_HOPS}
                          value={`${evaluator.num_hops} hops completed`}
                        />
                      )}
                      <div
                        style={{
                          padding: '12px',
                          backgroundColor: '#F0F9FF',
                          borderRadius: '6px',
                          border: '1px solid #E0F2FE',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          marginBottom: '12px',
                        }}
                      >
                        <Database style={{ width: '16px', height: '16px', color: '#0369A1' }} />
                        <span
                          style={{
                            ...RESEARCH_STYLES.key,
                            fontSize: '14px',
                            color: '#0369A1',
                          }}
                        >
                          Knowledge base research trace available
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Current Results Summary */}
                  <div style={{ marginBottom: '16px' }}>
                    {evaluator.evaluation_result && (
                      <KeyValueRow
                        keyText="Current Evaluation Result"
                        value={evaluator.evaluation_result}
                      />
                    )}

                    {evaluator.evaluation_score && (
                      <KeyValueRow
                        keyText="Current Evaluation Score"
                        value={evaluator.evaluation_score}
                      />
                    )}

                    {Boolean(evaluator.error) && (
                      <KeyValueRow keyText={FIELD_LABELS.ERROR} value="Error occurred" />
                    )}
                  </div>

                  {/* Evaluation Attempts Detail */}
                  {evaluationHistory.length > 0 && (
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
                        <Target style={{ width: '16px', height: '16px' }} />
                        Evaluation Attempts ({evaluationHistory.length})
                      </div>

                      <div
                        style={{
                          border: '1px solid #E5E7EB',
                          borderRadius: '6px',
                          backgroundColor: '#F9FAFB',
                          overflow: 'hidden',
                        }}
                      >
                        {evaluationHistory.map((attempt: any, attemptIndex: number) => {
                          const attemptKey = `${evaluatorIndex}-${attemptIndex}`;
                          const isAttemptExpanded = expandedAttempts.has(attemptKey);
                          const hasAttemptError = attempt.error;
                          const scoreColor = attempt.score
                            ? getScoreColor(attempt.score)
                            : '#6B7280';

                          return (
                            <div
                              key={attemptIndex}
                              style={{
                                borderBottom:
                                  attemptIndex < evaluationHistory.length - 1
                                    ? '1px solid #E5E7EB'
                                    : 'none',
                              }}
                            >
                              {/* Attempt Header */}
                              <button
                                onClick={() => toggleAttempt(evaluatorIndex, attemptIndex)}
                                style={{
                                  width: '100%',
                                  padding: '12px 16px',
                                  backgroundColor: isAttemptExpanded ? '#FFFFFF' : 'transparent',
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
                                  if (!isAttemptExpanded) {
                                    e.currentTarget.style.backgroundColor = '#F3F4F6';
                                  }
                                }}
                                onMouseLeave={(e) => {
                                  if (!isAttemptExpanded) {
                                    e.currentTarget.style.backgroundColor = 'transparent';
                                  }
                                }}
                              >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                  <div
                                    style={{
                                      width: '20px',
                                      height: '20px',
                                      borderRadius: '50%',
                                      backgroundColor: hasAttemptError ? '#EF4444' : scoreColor,
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      color: '#FFFFFF',
                                    }}
                                  >
                                    {getAttemptIcon(attempt, hasAttemptError)}
                                  </div>
                                  <div>
                                    <div
                                      style={{
                                        ...RESEARCH_STYLES.value,
                                        fontWeight: 500,
                                        fontSize: '14px',
                                      }}
                                    >
                                      Attempt #{attemptIndex + 1}
                                    </div>
                                    {attempt.score && (
                                      <div
                                        style={{
                                          fontSize: '12px',
                                          color: scoreColor,
                                          fontWeight: 500,
                                        }}
                                      >
                                        Score: {attempt.score}
                                      </div>
                                    )}
                                  </div>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                  {hasAttemptError && (
                                    <AlertTriangle
                                      style={{ width: '14px', height: '14px', color: '#EF4444' }}
                                    />
                                  )}
                                  {isAttemptExpanded ? (
                                    <ChevronDown
                                      style={{ width: '16px', height: '16px', color: '#6B7280' }}
                                    />
                                  ) : (
                                    <ChevronRight
                                      style={{ width: '16px', height: '16px', color: '#6B7280' }}
                                    />
                                  )}
                                </div>
                              </button>

                              {/* Attempt Details */}
                              {isAttemptExpanded && (
                                <div
                                  style={{
                                    padding: '12px 16px',
                                    backgroundColor: '#FFFFFF',
                                    borderTop: '1px solid #E5E7EB',
                                    fontSize: '14px',
                                  }}
                                >
                                  {attempt.score && (
                                    <div style={{ marginBottom: '8px' }}>
                                      <strong>Score:</strong>{' '}
                                      <span style={{ color: scoreColor }}>{attempt.score}</span>
                                    </div>
                                  )}
                                  {attempt.reasoning && (
                                    <div style={{ marginBottom: '8px' }}>
                                      <strong>Reasoning:</strong> {attempt.reasoning}
                                    </div>
                                  )}
                                  {attempt.feedback && (
                                    <div style={{ marginBottom: '8px' }}>
                                      <strong>Feedback:</strong> {attempt.feedback}
                                    </div>
                                  )}
                                  {hasAttemptError && (
                                    <div
                                      style={{
                                        padding: '8px',
                                        backgroundColor: '#FEF2F2',
                                        borderRadius: '4px',
                                        border: '1px solid #FECACA',
                                        color: '#DC2626',
                                      }}
                                    >
                                      <strong>Error:</strong>{' '}
                                      {typeof attempt.error === 'string'
                                        ? attempt.error
                                        : 'An error occurred during this attempt'}
                                    </div>
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
                    onClick={() => onViewDetails?.(evaluator)}
                    text={
                      hasKnowledgeBase
                        ? `View Evaluator #${evaluatorIndex + 1} Knowledge Base Details`
                        : `View Evaluator #${evaluatorIndex + 1} Details`
                    }
                  />
                </div>
              )}
            </div>
          </div>
        );
      })}
    </React.Fragment>
  );
};

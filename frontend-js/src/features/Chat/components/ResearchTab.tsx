import React, { useState } from 'react';
import type {
  TraceInfo,
  PlannerAgent,
  PlannerRefinerAgent,
  EvaluationAgent,
  ExecutorAgent,
  LLMUsage,
} from '../../../lib/api-service';
import ContextModal from './ContextModal';

// Enhanced markdown to HTML conversion utility
const convertMarkdownToHtml = (markdown: string): string => {
  if (!markdown) return '';

  // Clean the input (handle escaped characters)
  let html = markdown.replace(/\\n/g, '\n').replace(/\\"/g, '"').replace(/\\'/g, "'");

  // Apply stylish container for better readability
  const applyContainer = (content: string) => {
    return `<div style="font-family: Inter; line-height: 1.6; color: #002835; background: #f8f9fa; border-radius: 8px; padding: 16px; margin-bottom: 16px;">${content}</div>`;
  };

  html = html
    // Convert headers with proper styling
    .replace(
      /^### (.*$)/gim,
      '<h3 style="font-size: 1.25rem; margin: 1rem 0 0.75rem; color: #002835; font-weight: 600;">$1</h3>'
    )
    .replace(
      /^## (.*$)/gim,
      '<h2 style="font-size: 1.5rem; margin: 1.25rem 0 1rem; color: #002835; font-weight: 600;">$1</h2>'
    )
    .replace(
      /^# (.*$)/gim,
      '<h1 style="font-size: 1.75rem; margin: 1.5rem 0 1.25rem; color: #002835; font-weight: 600;">$1</h1>'
    )

    // Convert bold and italic with consistent styling
    .replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight: 600;">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em style="font-style: italic;">$1</em>')
    .replace(/__(.*?)__/g, '<strong style="font-weight: 600;">$1</strong>')
    .replace(/_(.*?)_/g, '<em style="font-style: italic;">$1</em>')

    // Convert links with better styling
    .replace(
      /\[(.*?)\]\((.*?)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer" style="color: #00A599; text-decoration: underline;">$1</a>'
    )

    // Handle bullet points more effectively
    .replace(
      /^\* (.*)/gm,
      '<div style="display: flex; margin: 0.25rem 0;"><span style="margin-right: 0.5rem;">•</span><span>$1</span></div>'
    )
    .replace(
      /^- (.*)/gm,
      '<div style="display: flex; margin: 0.25rem 0;"><span style="margin-right: 0.5rem;">•</span><span>$1</span></div>'
    )

    // Handle numbered lists
    .replace(/^\d+\. (.*)/gm, (match, p1) => {
      const number = match.split('.')[0];
      return `<div style="display: flex; margin: 0.25rem 0;"><span style="margin-right: 0.5rem; min-width: 1rem;">${number}.</span><span>${p1}</span></div>`;
    })

    // Convert code blocks with syntax highlighting styling
    .replace(
      /```([^`]*?)```/g,
      '<pre style="background: #f1f3f5; border-radius: 4px; padding: 12px; overflow-x: auto; margin: 1rem 0;"><code style="font-family: monospace; color: #002835;">$1</code></pre>'
    )

    // Convert inline code with improved styling
    .replace(
      /`([^`]+?)`/g,
      '<code style="background: #f1f3f5; border-radius: 3px; padding: 2px 4px; font-family: monospace; font-size: 0.9em;">$1</code>'
    )

    // Handle paragraphs properly
    .replace(/\n\n([^\n]+)/g, '</p><p style="margin: 0.75rem 0;">$1')

    // Convert single line breaks but respect lists
    .replace(/\n(?!<\/?(ul|ol|li|p|div|h1|h2|h3|pre|code))/g, '<br />');

  // Ensure paragraphs are properly wrapped
  if (
    !html.startsWith('<h1') &&
    !html.startsWith('<h2') &&
    !html.startsWith('<h3') &&
    !html.startsWith('<p') &&
    !html.startsWith('<div') &&
    !html.startsWith('<pre')
  ) {
    html = `<p style="margin: 0.75rem 0;">${html}</p>`;
  }

  // Apply container styling
  return applyContainer(html);
};

interface ResearchTabProps {
  traceInfo: TraceInfo;
}

const ResearchTab: React.FC<ResearchTabProps> = ({ traceInfo }) => {
  // Add modal state
  const [plannerModalVisible, setPlannerModalVisible] = useState(false);
  const [plannerModalContent, setPlannerModalContent] = useState<string>(''); // Format planner detailed response as structured text with appropriate styling
  const [executorModalVisible, setExecutorModalVisible] = useState(false);
  const [executorModalContent, setExecutorModalContent] = useState<string>('');
  const [evaluatorModalVisible, setEvaluatorModalVisible] = useState(false);
  const [evaluatorModalContent, setEvaluatorModalContent] = useState<string>('');

  // LLM Usage display component
  const renderLLMUsage = (llmUsage?: LLMUsage, executionTimeMs?: number) => {
    if (!llmUsage) return null;

    // Styles as specified
    const valueStyle: React.CSSProperties = {
      color: '#002835',
      fontFamily: 'Inter',
      fontSize: '16px', // Reduced from 20px
      fontStyle: 'normal',
      fontWeight: '500',
      lineHeight: 'normal',
    };

    const executionTimeValueStyle: React.CSSProperties = {
      ...valueStyle,
      color: '#23913F',
    };

    const labelStyle: React.CSSProperties = {
      color: '#002835',
      opacity: 0.6,
      fontFamily: 'Inter',
      fontSize: '12px', // Reduced from 14px
      fontStyle: 'normal',
      fontWeight: '500',
      lineHeight: 'normal',
      marginTop: '4px', // Reduced from 6px
    };

    const columnStyle: React.CSSProperties = {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start',
      paddingRight: '20px', // Reduced from 24px
      marginRight: '20px', // Reduced from 24px
      borderRight: '1px solid #E0E0E0',
      minWidth: '70px', // Reduced from 80px
    };

    const lastColumnStyle: React.CSSProperties = {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start',
      minWidth: '70px', // Reduced from 80px
    };

    return (
      <div style={{ marginTop: '18px', marginBottom: '18px', display: 'flex' }}>
        <div style={columnStyle}>
          <div style={executionTimeValueStyle}>
            <span>{executionTimeMs || 0}</span>
            <span style={{ fontSize: '14px', textTransform: 'lowercase' }}>ms</span>
          </div>
          <div style={labelStyle}>Execution Time</div>
        </div>

        <div style={{ ...columnStyle, minWidth: '200px' }}>
          <div
            style={{
              ...valueStyle,
              maxWidth: '240px',
              overflow: 'visible',
              whiteSpace: 'normal',
              cursor: 'default',
              wordBreak: 'break-word',
            }}
            title={llmUsage.model}
          >
            {llmUsage.model}
          </div>
          <div style={labelStyle}>LLM Used</div>
        </div>

        <div style={columnStyle}>
          <div style={valueStyle}>{String(llmUsage.input_tokens).padStart(2, '0')}</div>
          <div style={labelStyle}>Input Tokens</div>
        </div>

        <div style={lastColumnStyle}>
          <div style={valueStyle}>{String(llmUsage.output_tokens).padStart(2, '0')}</div>
          <div style={labelStyle}>Output Tokens</div>
        </div>
      </div>
    );
  };

  const formatExecutorDetailedResponse = (executor: ExecutorAgent): string => {
    const keyStyle =
      'color: #002835; font-family: Inter; font-size: 18px; font-style: normal; font-weight: 600; line-height: 24px;';
    const valueStyle =
      'color: #002835; font-family: Inter; font-size: 16px; font-style: normal; font-weight: 400; line-height: 24px;';

    let content = '';

    // Combined Answer of Sources with enhanced styling but without card effect
    if (executor.executor_answer) {
      content += `<div style="${keyStyle}">Combined Answer</div>`;
      content += `<div>${convertMarkdownToHtml(executor.executor_answer)}</div>`;
      content += `<div style="margin-bottom: 20px;"></div>`;
    }

    // Error if present
    if (executor.error) {
      content += `<div style="${keyStyle}">Error</div>`;
      content += `<div style="${valueStyle}">${executor.error}</div>`;
    }

    return content;
  };

  // Functions to handle opening and closing the executor modal
  const openExecutorModal = (executor: ExecutorAgent) => {
    const content = formatExecutorDetailedResponse(executor);
    setExecutorModalContent(content);
    setExecutorModalVisible(true);
  };

  const closeExecutorModal = () => {
    setExecutorModalVisible(false);
  };

  const formatPlannerDetailedResponse = (planner: PlannerAgent): string => {
    const keyStyle =
      'color: #002835; font-family: Inter; font-size: 18px; font-style: normal; font-weight: 600; line-height: 24px;';
    const valueStyle =
      'color: #002835; font-family: Inter; font-size: 16px; font-style: normal; font-weight: 400; line-height: 24px;';
    const componentKeyStyle =
      'color: #002835; font-family: Inter; font-size: 16px; font-style: normal; font-weight: 500; line-height: 24px;';
    const thinkingHeadingStyle =
      'color: #002835; font-family: Inter; font-size: 16px; font-style: normal; font-weight: 600; line-height: 24px;';

    let content = '';

    // Execution time
    content += `<div style="${keyStyle}">Execution time</div>`;
    content += `<div style="${valueStyle}">${planner.execution_time_ms}ms</div>`;
    content += `<div style="margin-bottom: 20px;"></div>`;

    // Query intent
    content += `<div style="${keyStyle}">Query intent</div>`;
    content += `<div style="${valueStyle}">${planner.plan.query_intent}</div>`;
    content += `<div style="margin-bottom: 20px;"></div>`;

    // Query components
    planner.plan.query_components.forEach((component, index) => {
      content += `<div style="margin-bottom: 10px;"><span style="${keyStyle}">Query Component ${index + 1}</span></div>`;
      content += `<div><span style="${componentKeyStyle}">ID: </span><span style="${valueStyle}">${component.id}</span></div>`;
      content += `<div><span style="${componentKeyStyle}">Sub-Query: </span><span style="${valueStyle}">${component.sub_query}</span></div>`;
      content += `<div><span style="${componentKeyStyle}">Source: </span><span style="${valueStyle}">${component.source}</span></div>`;
      if (index < planner.plan.query_components.length - 1) {
        content += `<div style="margin-bottom: 20px;"></div>`;
      }
    });
    content += `<div style="margin-bottom: 20px;"></div>`;

    // Data Sources
    content += `<div style="${keyStyle}">Data Sources</div>`;
    content += `<div style="${valueStyle}">${planner.plan.data_sources.join(', ')}</div>`;
    content += `<div style="margin-bottom: 20px;"></div>`;

    // Thinking process
    content += `<div style="${keyStyle}">Thinking process</div>`;
    content += `<div style="margin-bottom: 8px;"></div>`;

    // Query Analysis
    content += `<div style="${thinkingHeadingStyle}">Query Analysis:</div>`;
    content += `<div style="${valueStyle}">${planner.plan.think.query_analysis}</div>`;
    content += `<div style="margin-bottom: 20px;"></div>`;

    // Sub-Query Reasoning
    content += `<div style="${thinkingHeadingStyle}">Sub-Query Reasoning:</div>`;
    content += `<div style="${valueStyle}">${planner.plan.think.sub_query_reasoning}</div>`;
    content += `<div style="margin-bottom: 20px;"></div>`;

    // Source Selection
    content += `<div style="${thinkingHeadingStyle}">Source Selection:</div>`;
    content += `<div style="${valueStyle}">${planner.plan.think.source_selection}</div>`;
    content += `<div style="margin-bottom: 20px;"></div>`;

    // Execution strategy
    content += `<div style="${thinkingHeadingStyle}">Execution strategy:</div>`;
    content += `<div style="${valueStyle}">${planner.plan.think.execution_strategy}</div>`;

    return content;
  };

  // Functions to handle opening and closing the modal
  const openPlannerModal = (planner: PlannerAgent) => {
    const content = formatPlannerDetailedResponse(planner);
    setPlannerModalContent(content);
    setPlannerModalVisible(true);
  };

  const closePlannerModal = () => {
    setPlannerModalVisible(false);
  };

  const formatEvaluatorDetailedResponse = (evaluator: EvaluationAgent): string => {
    const keyStyle =
      'color: #002835; font-family: Inter; font-size: 18px; font-style: normal; font-weight: 600; line-height: 24px;';
    const valueStyle =
      'color: #002835; font-family: Inter; font-size: 16px; font-style: normal; font-weight: 400; line-height: 24px;';
    const sectionStyle =
      'color: #002835; font-family: Inter; font-size: 16px; font-style: normal; font-weight: 600; line-height: 24px;';
    const factCardStyle =
      'background-color: #F5F5F5; border-radius: 8px; padding: 16px; margin-bottom: 16px; border-left: 4px solid #00A599;';
    const factStyle =
      'color: #002835; font-family: Inter; font-size: 16px; font-style: normal; font-weight: 600; line-height: 24px;';
    const labelTrueStyle =
      'display: inline-block; padding: 2px 10px; border-radius: 12px; background-color: #34C759; color: white; font-size: 14px; margin-top: 8px; margin-bottom: 8px;';
    const labelFalseStyle =
      'display: inline-block; padding: 2px 10px; border-radius: 12px; background-color: #FF3B30; color: white; font-size: 14px; margin-top: 8px; margin-bottom: 8px;';
    const reasoningStyle =
      'color: #002835; font-family: Inter; font-size: 15px; font-style: normal; font-weight: 400; line-height: 22px;';

    let content = '';

    // Execution time if available
    if (evaluator.execution_time_ms) {
      content += `<div style="${keyStyle}">Execution time</div>`;
      content += `<div style="${valueStyle}">${evaluator.execution_time_ms}ms</div>`;
      content += `<div style="margin-bottom: 20px;"></div>`;
    }

    // LLM Usage section removed as per requirements

    // Evaluation Attempt
    content += `<div style="${keyStyle}">Evaluation Attempt</div>`;
    content += `<div style="${valueStyle}">${evaluator.attempt}</div>`;
    content += `<div style="margin-bottom: 20px;"></div>`;

    // Score
    content += `<div style="${keyStyle}">Score</div>`;
    content += `<div style="${valueStyle}">${evaluator.evaluation_history.score}</div>`;
    content += `<div style="margin-bottom: 20px;"></div>`;

    // Reasoning
    content += `<div style="${keyStyle}">Reasoning</div>`;
    content += `<div style="margin-bottom: 12px;"></div>`;

    // Check if reasoning is an array of fact checks
    if (Array.isArray(evaluator.evaluation_history.reasoning)) {
      // Safely display structured facts
      evaluator.evaluation_history.reasoning.forEach((item, index) => {
        try {
          // Use type assertion after first casting to unknown
          const factObj = item as unknown as {
            fact: string;
            label: string;
            reasoning: string;
          };

          content += `<div style="${factCardStyle}">`;
          content += `<div style="${factStyle}">${index + 1}. ${factObj.fact || 'Unknown fact'}</div>`;
          content += `<div style="${factObj.label === 'yes' ? labelTrueStyle : labelFalseStyle}">
            ${factObj.label === 'yes' ? 'Verified ✓' : 'Not Verified ✗'}
          </div>`;
          content += `<div style="${reasoningStyle}">${factObj.reasoning || ''}</div>`;
          content += `</div>`;
        } catch {
          // If there's an issue with the structure, show item as string
          content += `<div style="${valueStyle}">${JSON.stringify(item)}</div>`;
        }
      });
    } else if (typeof evaluator.evaluation_history.reasoning === 'string') {
      // Fallback for string reasoning
      content += `<div style="${valueStyle}">${convertMarkdownToHtml(evaluator.evaluation_history.reasoning)}</div>`;
    }
    content += `<div style="margin-bottom: 20px;"></div>`;

    // Evaluation History - Additional details
    try {
      // Access the evaluation history object properties while working around TypeScript constraints
      const historyObj = evaluator.evaluation_history as unknown as Record<string, unknown>;

      // Show additional evaluation details if available
      Object.entries(historyObj).forEach(([key, value]) => {
        if (!['score', 'reasoning', 'error', 'llm_usage'].includes(key) && value) {
          content += `<div style="${sectionStyle}">${key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}:</div>`;
          content += `<div style="${valueStyle}">
            ${typeof value === 'string' ? convertMarkdownToHtml(value) : JSON.stringify(value)}
          </div>`;
          content += `<div style="margin-bottom: 10px;"></div>`;
        }
      });
    } catch {
      // Silently handle if this structure doesn't exist
    }

    // Error if present
    if (evaluator.evaluation_history.error) {
      content += `<div style="${keyStyle}">Error</div>`;
      content += `<div style="${valueStyle}">${evaluator.evaluation_history.error}</div>`;
    }

    return content;
  };

  // Functions to handle opening and closing the evaluator modal
  const openEvaluatorModal = (evaluator: EvaluationAgent) => {
    const content = formatEvaluatorDetailedResponse(evaluator);
    setEvaluatorModalContent(content);
    setEvaluatorModalVisible(true);
  };

  const closeEvaluatorModal = () => {
    setEvaluatorModalVisible(false);
  };

  const sectionTitleStyle: React.CSSProperties = {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 500,
    lineHeight: 'normal',
    textTransform: 'uppercase',
    opacity: 0.4,
  };

  const keyStyle: React.CSSProperties = {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 500,
    lineHeight: '24px',
    opacity: 0.6,
  };

  const valueStyle: React.CSSProperties = {
    color: '#002835',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 400,
    lineHeight: '24px',
  };

  const batchStyle: React.CSSProperties = {
    display: 'flex',
    padding: '5px 9px',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '10px',
    borderRadius: '50px',
    background: '#34C759', // var(--Colors-Green, #34C759)
  };

  const batchTextStyle: React.CSSProperties = {
    color: '#FFF',
    fontFamily: 'Inter',
    fontSize: '14px',
    fontStyle: 'normal',
    fontWeight: 600,
    lineHeight: 'normal',
  };

  const KEY_COLUMN_WIDTH = '210px'; // Adjusted width for keys

  const truncatedTextStyle: React.CSSProperties = {
    display: '-webkit-box',
    WebkitLineClamp: 3,
    WebkitBoxOrient: 'vertical',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  };

  const viewDetailsStyle: React.CSSProperties = {
    color: '#00A599',
    fontFamily: 'Inter',
    fontSize: '16px',
    fontStyle: 'normal',
    fontWeight: 500,
    lineHeight: '24px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
  };

  const separatorStyle: React.CSSProperties = {
    background: '#9CBFBC',
    height: '1px',
    margin: '33px 0',
  };

  const renderKeyValue = (
    key: string,
    value?: string | number | null | string[],
    showBatch = false,
    index?: number
  ) => (
    <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: '11px' }}>
      {/* Number Column */}
      {index !== undefined && (
        <div style={{ ...keyStyle, width: '30px', flexShrink: 0 }}>{index + 1}.</div>
      )}
      {/* Key Column */}
      <div style={{ ...keyStyle, width: KEY_COLUMN_WIDTH, flexShrink: 0 }}>{key}</div>
      {/* Spacer Column */}
      <div style={{ width: '63px', flexShrink: 0 }} />
      {/* Value Column (takes remaining space) */}
      <div style={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
        {value !== undefined && value !== null && (
          <div
            style={
              typeof value === 'string' && !Array.isArray(value)
                ? { ...valueStyle, ...truncatedTextStyle }
                : valueStyle
            }
          >
            {Array.isArray(value) ? value.join(', ') : String(value)}
          </div>
        )}
        {showBatch && value !== undefined && value !== null && !Array.isArray(value) && (
          <div style={{ marginLeft: '4px', ...batchStyle }}>
            <span style={batchTextStyle}>Good</span>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="flex w-full flex-col gap-4 font-['Inter'] text-[#002835]">
      {/* PLANNER AGENT Section */}
      {traceInfo.planner_agent && traceInfo.planner_agent.length > 0 && (
        <>
          <div style={sectionTitleStyle}>PLANNER AGENT</div>
          {traceInfo.planner_agent.map((planner: PlannerAgent, index: number) => (
            <div key={index} style={{ marginBottom: '11px' }}>
              {renderLLMUsage(planner.llm_usage, planner.execution_time_ms)}
              {renderKeyValue('Query Intent', planner.plan.query_intent)}{' '}
              {planner.plan.query_components.length > 0 && (
                <div style={{ display: 'flex', marginBottom: '11px' }}>
                  <div style={{ ...keyStyle, width: KEY_COLUMN_WIDTH, flexShrink: 0 }}>
                    Query Component
                  </div>
                  <div style={{ width: '63px', flexShrink: 0 }} />
                  <div>
                    {' '}
                    <div>
                      <span
                        style={{
                          color: '#002835',
                          fontFamily: 'Inter',
                          fontSize: '16px',
                          fontStyle: 'normal',
                          fontWeight: 500,
                          lineHeight: '24px',
                        }}
                      >
                        ID:{' '}
                      </span>
                      <span
                        style={{
                          color: '#002835',
                          fontFamily: 'Inter',
                          fontSize: '16px',
                          fontStyle: 'normal',
                          fontWeight: 400,
                          lineHeight: '24px',
                        }}
                      >
                        {planner.plan.query_components[0].id}
                      </span>
                    </div>
                    <div>
                      <span
                        style={{
                          color: '#002835',
                          fontFamily: 'Inter',
                          fontSize: '16px',
                          fontStyle: 'normal',
                          fontWeight: 500,
                          lineHeight: '24px',
                        }}
                      >
                        Sub-Query:{' '}
                      </span>
                      <span
                        style={{
                          color: '#002835',
                          fontFamily: 'Inter',
                          fontSize: '16px',
                          fontStyle: 'normal',
                          fontWeight: 400,
                          lineHeight: '24px',
                        }}
                      >
                        {planner.plan.query_components[0].sub_query}
                      </span>
                    </div>
                    <div>
                      <span
                        style={{
                          color: '#002835',
                          fontFamily: 'Inter',
                          fontSize: '16px',
                          fontStyle: 'normal',
                          fontWeight: 500,
                          lineHeight: '24px',
                        }}
                      >
                        Source:{' '}
                      </span>
                      <span
                        style={{
                          color: '#002835',
                          fontFamily: 'Inter',
                          fontSize: '16px',
                          fontStyle: 'normal',
                          fontWeight: 400,
                          lineHeight: '24px',
                        }}
                      >
                        {planner.plan.query_components[0].source}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
          <div
            style={viewDetailsStyle}
            onClick={() => openPlannerModal(traceInfo.planner_agent[0])}
          >
            View Planner Detailed Response
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="21"
              height="22"
              viewBox="0 0 21 22"
              fill="none"
              style={{ marginLeft: '8px' }}
            >
              <path
                d="M7.875 16.25L13.125 11L7.875 5.75"
                stroke="#00A599"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div style={separatorStyle} />
        </>
      )}
      {/* Query Refinement Agent Section */}
      {traceInfo.planner_refiner_agent && traceInfo.planner_refiner_agent.length > 0 && (
        <>
          <div style={sectionTitleStyle}>Query refinement agent</div>
          {traceInfo.planner_refiner_agent.map(
            (refinementAgent: PlannerRefinerAgent, index: number) => (
              <div key={index} style={{ marginBottom: '11px' }}>
                {renderLLMUsage(refinementAgent.llm_usage, refinementAgent.execution_time_ms)}
                {renderKeyValue(
                  'Refinement Required',
                  refinementAgent.refinement_required?.toString()?.charAt(0).toUpperCase() +
                    refinementAgent.refinement_required?.toString()?.slice(1)
                )}
                {renderKeyValue('Feedback Summary', refinementAgent.feedback_summary)}
                {renderKeyValue('Feedback Reasoning', refinementAgent.feedback_reasoning)}
                {refinementAgent.error && renderKeyValue('Error', 'Yes')}
              </div>
            )
          )}
          <div style={separatorStyle} />
        </>
      )}{' '}
      {/* Knowledge Base Agent and Other Executor Agents Section */}
      {traceInfo.executor_agent && (
        <React.Fragment>
          <div style={sectionTitleStyle}>EXECUTOR AGENT</div>
          {renderLLMUsage(
            traceInfo.executor_agent.llm_usage,
            traceInfo.executor_agent.execution_time_ms || 0
          )}
          <div style={{ marginBottom: '11px' }}>
            {/* Displaying general info about executor agent with plain text in preview */}
            {traceInfo.executor_agent.executor_answer &&
              renderKeyValue('Combined Answer', traceInfo.executor_agent.executor_answer)}
            {traceInfo.executor_agent.error && renderKeyValue('Error', 'Yes')}
          </div>
          <div style={viewDetailsStyle} onClick={() => openExecutorModal(traceInfo.executor_agent)}>
            View Executor Agent Detailed Response
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="21"
              height="22"
              viewBox="0 0 21 22"
              fill="none"
              style={{ marginLeft: '8px' }}
            >
              <path
                d="M7.875 16.25L13.125 11L7.875 5.75"
                stroke="#00A599"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </React.Fragment>
      )}
      {/* Separator before Evaluator Agent if executor agents existed */}
      {traceInfo.executor_agent &&
        traceInfo.evaluation_agent &&
        traceInfo.evaluation_agent.length > 0 && <div style={separatorStyle} />}{' '}
      {/* Evaluator Agent Section */}
      {traceInfo.evaluation_agent && traceInfo.evaluation_agent.length > 0 && (
        <>
          <div style={sectionTitleStyle}>Evaluator agent</div>
          {traceInfo.evaluation_agent.map((evaluator: EvaluationAgent, index: number) => (
            <div key={index} style={{ marginBottom: '11px' }}>
              {/* Show LLM usage in preview similar to other agents */}
              {(() => {
                try {
                  // First check if there's a direct llm_usage property
                  if (evaluator.llm_usage) {
                    return renderLLMUsage(evaluator.llm_usage, evaluator.execution_time_ms || 0);
                  }

                  // Otherwise, check if it's in the evaluation_history
                  const historyObj = evaluator.evaluation_history as unknown as Record<
                    string,
                    unknown
                  >;
                  if (historyObj['llm_usage'] && typeof historyObj['llm_usage'] === 'object') {
                    return renderLLMUsage(
                      historyObj['llm_usage'] as LLMUsage,
                      evaluator.execution_time_ms || 0
                    );
                  }
                } catch {
                  // Silently handle errors
                }
                // Fallback - no LLM usage to show
                return null;
              })()}
              {renderKeyValue('Evaluation Attempt', evaluator.attempt)}
              {renderKeyValue('Score', evaluator.evaluation_history.score)}
              {/* Removed reasoning from main view as requested */}
              {evaluator.evaluation_history.error && renderKeyValue('Error', 'Yes')}
            </div>
          ))}
          <div
            style={viewDetailsStyle}
            onClick={() => openEvaluatorModal(traceInfo.evaluation_agent[0])}
          >
            View Reasoning Details
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="21"
              height="22"
              viewBox="0 0 21 22"
              fill="none"
              style={{ marginLeft: '8px' }}
            >
              <path
                d="M7.875 16.25L13.125 11L7.875 5.75"
                stroke="#00A599"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </>
      )}{' '}
      {/* Planner Modal */}
      <ContextModal
        isVisible={plannerModalVisible}
        title="Planner Detailed Response"
        content={plannerModalContent}
        onClose={closePlannerModal}
        isHtml={true}
      />
      {/* Executor Modal - New addition */}
      <ContextModal
        isVisible={executorModalVisible}
        title="Executor Detailed Response"
        content={executorModalContent}
        onClose={closeExecutorModal}
        isHtml={true}
      />
      {/* Evaluator Modal - New addition */}{' '}
      <ContextModal
        isVisible={evaluatorModalVisible}
        title="Evaluator Detailed Response"
        content={evaluatorModalContent}
        onClose={closeEvaluatorModal}
        isHtml={true}
      />
    </div>
  );
};

export default ResearchTab;

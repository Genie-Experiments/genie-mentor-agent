import React from 'react';
import type { TraceInfo, PlannerAgent, EvaluationAgent, PlannerRefinerAgent } from '../../../lib/api-service'; // Removed ExecutorAgent as it's unused after previous changes

interface ResearchTabProps {
  traceInfo: TraceInfo;
}

const ResearchTab: React.FC<ResearchTabProps> = ({ traceInfo }) => {
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

  const renderKeyValue = (key: string, value?: string | number | null | string[], showBatch = false, index?: number) => (
    <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: '11px' }}>
      {/* Number Column */}
      {index !== undefined && (
        <div style={{ ...keyStyle, width: '30px', flexShrink: 0 }}>
          {index + 1}.
        </div>
      )}
      {/* Key Column */}
      <div style={{ ...keyStyle, width: KEY_COLUMN_WIDTH, flexShrink: 0 }}>
        {key}
      </div>
      {/* Spacer Column */}
      <div style={{ width: '63px', flexShrink: 0 }} />
      {/* Value Column (takes remaining space) */}
      <div style={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
        {value !== undefined && value !== null && (
          <div style={
            typeof value === 'string' && !Array.isArray(value)
              ? { ...valueStyle, ...truncatedTextStyle }
              : valueStyle
          }>
            {Array.isArray(value) ? value.join(', ') : String(value)}
          </div>
        )}
        {showBatch && value !== undefined && value !== null && !Array.isArray(value) && (
          <div style={{ marginLeft: '4px', ...batchStyle }}>
            <span style={batchTextStyle}>{String(value)}</span>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="flex flex-col gap-4 w-full text-[#002835] font-['Inter'] p-4">
      {/* PLANNER AGENT Section */}
      {traceInfo.planner_agent && traceInfo.planner_agent.length > 0 && (
        <>
          <div style={sectionTitleStyle}>PLANNER AGENT</div>
          {traceInfo.planner_agent.map((planner: PlannerAgent, index: number) => (
            <div key={index} style={{ marginBottom: '11px' }}>
              {renderKeyValue('Query Intent', planner.plan.query_intent)}
              {renderKeyValue('Execution Time', planner.execution_time_ms, true)}
            </div>
          ))}
          <div style={viewDetailsStyle}>
            View Planner Detailed Response
            <svg xmlns="http://www.w3.org/2000/svg" width="21" height="22" viewBox="0 0 21 22" fill="none" style={{ marginLeft: '8px' }}>
              <path d="M7.875 16.25L13.125 11L7.875 5.75" stroke="#00A599" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div style={separatorStyle} />
        </>
      )}

      {/* Query Refinement Agent Section */}
      {traceInfo.planner_refiner_agent && traceInfo.planner_refiner_agent.length > 0 && (
        <>
          <div style={sectionTitleStyle}>Query refinement agent</div>
          {traceInfo.planner_refiner_agent.map((refinementAgent: PlannerRefinerAgent, index: number) => (
            <div key={index} style={{ marginBottom: '11px' }}>
              {renderKeyValue('Refinement Required', refinementAgent.refinement_required?.toString())}
              {renderKeyValue('Execution Time', refinementAgent.execution_time_ms, true)}
              {renderKeyValue('Feedback Summary', refinementAgent.feedback_summary)}
              {renderKeyValue('Feedback Reasoning', refinementAgent.feedback_reasoning)}
              {renderKeyValue('Error', refinementAgent.error ? 'Yes' : 'No')}
            </div>
          ))}
          <div style={separatorStyle} />
        </>
      )}

      {/* Knowledge Base Agent and Other Executor Agents Section */}
      {traceInfo.executor_agent && (
          <React.Fragment>
            <div style={sectionTitleStyle}>EXECUTOR AGENT</div>
            <div style={{ marginBottom: '11px' }}>
              {/* Assuming executor_agent is an object, not an array. 
                  Displaying general info. Specific fields like agent_name, execution_time, answer 
                  are not directly in ExecutorAgent type but might be in documents_by_source or metadata_by_source.
                  For now, showing a generic message or error if present. */}
              {renderKeyValue('Error', traceInfo.executor_agent.error ? 'Yes' : 'No')}
              {/* Add more specific rendering based on available data in traceInfo.executor_agent */}
              {traceInfo.executor_agent.combined_answer_of_sources && renderKeyValue('Combined Answer', traceInfo.executor_agent.combined_answer_of_sources)}
            </div>
            <div style={viewDetailsStyle}>
              View Executor Agent Detailed Response
              <svg xmlns="http://www.w3.org/2000/svg" width="21" height="22" viewBox="0 0 21 22" fill="none" style={{ marginLeft: '8px' }}>
                <path d="M7.875 16.25L13.125 11L7.875 5.75" stroke="#00A599" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </React.Fragment>
        )}
      
      {/* Separator before Evaluator Agent if executor agents existed */}
      {traceInfo.executor_agent && traceInfo.evaluation_agent && traceInfo.evaluation_agent.length > 0 && (
         <div style={separatorStyle} />
      )}


      {/* Evaluator Agent Section */}
      {traceInfo.evaluation_agent && traceInfo.evaluation_agent.length > 0 && (
        <>
          <div style={sectionTitleStyle}>Evaluator agent</div>
          {traceInfo.evaluation_agent.map((evaluator: EvaluationAgent, index: number) => (
            <div key={index} style={{ marginBottom: '11px' }}>
              {renderKeyValue('Evaluation Attempt', evaluator.attempt)}
              {renderKeyValue('Score', evaluator.evaluation_history.score)}
              {renderKeyValue('Reasoning', evaluator.evaluation_history.reasoning)}
              {renderKeyValue('Error', evaluator.evaluation_history.error ? 'Yes' : 'No')}
            </div>
          ))}
          <div style={viewDetailsStyle}>
            View Complete Reasoning
            <svg xmlns="http://www.w3.org/2000/svg" width="21" height="22" viewBox="0 0 21 22" fill="none" style={{ marginLeft: '8px' }}>
              <path d="M7.875 16.25L13.125 11L7.875 5.75" stroke="#00A599" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </>
      )}
    </div>
  );
};

export default ResearchTab;

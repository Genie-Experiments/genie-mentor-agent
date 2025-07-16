import type {
  PlannerAgent,
  ExecutorAgent,
  EvaluationAgent,
  LLMUsage,
} from '@/lib/api-service';

/**
 * Enhanced markdown to HTML conversion utility
 */
export const convertMarkdownToHtml = (markdown: string): string => {
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

/**
 * Format planner detailed response as structured HTML
 */
export const formatPlannerDetailedResponse = (planner: PlannerAgent): string => {
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

/**
 * Format executor detailed response as structured HTML
 */
export const formatExecutorDetailedResponse = (executor: ExecutorAgent): string => {
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

/**
 * Format evaluator detailed response as structured HTML
 */
export const formatEvaluatorDetailedResponse = (evaluator: EvaluationAgent): string => {
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

/**
 * Extract LLM usage from evaluator agent
 */
export const extractEvaluatorLLMUsage = (evaluator: EvaluationAgent): LLMUsage | null => {
  try {
    // First check if there's a direct llm_usage property
    if (evaluator.llm_usage) {
      return evaluator.llm_usage;
    }

    // Otherwise, check if it's in the evaluation_history
    const historyObj = evaluator.evaluation_history as unknown as Record<string, unknown>;
    if (historyObj['llm_usage'] && typeof historyObj['llm_usage'] === 'object') {
      return historyObj['llm_usage'] as LLMUsage;
    }
  } catch {
    // Silently handle errors
  }
  return null;
};

/**
 * Capitalize first letter of a string
 */
export const capitalizeFirst = (str?: string): string => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};

/**
 * Format string for display with proper capitalization
 */
export const formatDisplayValue = (value?: string | boolean | null): string => {
  if (value === undefined || value === null) return '';
  if (typeof value === 'boolean') {
    return capitalizeFirst(value.toString());
  }
  return String(value);
};

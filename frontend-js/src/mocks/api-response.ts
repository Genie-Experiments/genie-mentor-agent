export const mockAgentResponses = {
  planner_agent: {
    execution_time_ms: 123,
    query_intent: 'define multiquery',
    data_sources: ['knowledgebase', 'github'],
    query_components: [
      {
        component_id: 'q1',
        sub_query: 'Explain multi-query optimization',
        source: 'knowledgebase',
      },
      {
        component_id: 'q2',
        sub_query: 'Show example code using multi-query optimization',
        source: 'github',
      },
    ],
    execution_order: {
      nodes: ['q1', 'q2'],
      edges: [],
      aggregation_strategy: 'combine_and_summarize',
    },
    thinking_process: {
      query_analysis: "Breaks down the user's intent and goals.",
      sub_query_reasoning: 'Explains why queries were split or grouped.',
      source_selection: 'Justifies source mapping for each sub-query.',
      execution_strategy: 'Describes the order of execution and aggregation logic.',
    },
    error: null,
  },

  planner_refiner_agent: {
    execution_time_ms: 57,
    refinement_required: 'yes',
    feedback_summary: 'Suggested combining similar sub-queries into one to avoid redundancy.',
    feedback_reasoning: [
      'Detected overlapping content between q1 and q2. Using a single sub-query can reduce latency and improve context coherence.',
    ],
    error: null,
  },

  knowledge_base_agent: {
    execution_time_ms: 74,
    answer: 'Your compiled final answer goes here...',
    sources: [
      'This excerpt explains how multi-query optimization works...',
      'Another section describes benefits of shared sub-expressions...',
    ],
    metadata: [
      {
        title: 'Understanding Multi-Query Optimization',
        page_number: 3,
        source: 'optimization_guide.pdf',
      },
      {
        title: 'Multi-query Optimization Benefits',
        page_number: 5,
        source: 'optimization_guide.pdf',
      },
    ],
    error: null,
  },

  web_search_agent: {
    execution_time_ms: 74,
    answer: 'Your compiled final answer goes here...',
    sources: [
      'This excerpt explains how multi-query optimization works...',
      'Another section describes benefits of shared sub-expressions...',
    ],
    metadata: [
      {
        web_url: 'https://example.com/optimization_techniques',
        web_title: 'Optimization Techniques',
        web_page_description: 'Overview of optimization strategies in databases.',
      },
      {
        web_url: 'https://example.com/mqo_intro',
        web_title: 'Introduction to Multi-Query Optimization',
        web_page_description: 'An introductory article on MQO.',
      },
    ],
    error: null,
  },

  github_agent: {
    execution_time_ms: 74,
    answer: 'Your compiled final answer goes here...',
    sources: [
      'This excerpt explains how multi-query optimization works...',
      'Another section describes benefits of shared sub-expressions...',
    ],
    metadata: [
      {
        repo_link: 'https://github.com/Genie-Experiments/genie-mentor-agent',
        repo_name: 'genie-mentor-agent',
      },
    ],
    error: null,
  },

  notion_agent: {
    execution_time_ms: 74,
    answer: 'Your compiled final answer goes here...',
    sources: [
      'This excerpt explains how multi-query optimization works...',
      'Another section describes benefits of shared sub-expressions...',
    ],
    metadata: [
      {
        notion_document_link:
          'https://www.notion.so/Genie-Research-and-POCs-Home_131155-512d4c99db644340be39a30796955f6f',
      },
    ],
    error: null,
  },

  executor_agent: {
    execution_time_ms: 74,
    combined_answer_of_sources: '',
    top_documents: [],
    all_documents: [],
    documents_by_source: [],
    error: null,
  },

  evaluation_agent: [
    {
      output: {
        score: 0.8,
        reasoning: `{
  "Result": [
    { "Fact": "1. Query-document alignment scores evaluate the relevance of LLM-generated queries with retrieved documents.", "Reasoning": "Supported", "Judgement": "yes" },
    { "Fact": "2. Three types of evaluation scores are used: BM25, dense, and hybrid.", "Reasoning": "Supported", "Judgement": "yes" },
    { "Fact": "3. Alignment scores help evaluate and store queries.", "Reasoning": "Supported", "Judgement": "yes" },
    { "Fact": "4. Scores aim to improve rephrased query performance.", "Reasoning": "Supported", "Judgement": "yes" },
    { "Fact": "5. Scores assist in filtering relevant queries.", "Reasoning": "Not supported in context", "Judgement": "no" }
  ]
}`,
        error: null,
      },
      attempt: 1,
    },
    {
      output: {
        score: 1,
        reasoning: `{
  "Result": [
    { "Fact": "1. Alignment scores refine LLM-generated queries.", "Reasoning": "Explicitly mentioned", "Judgement": "yes" },
    { "Fact": "2. BM25 used for sparse retrievals.", "Reasoning": "Mentioned", "Judgement": "yes" },
    { "Fact": "3. Dense scores used for dense retrievals.", "Reasoning": "Mentioned", "Judgement": "yes" },
    { "Fact": "4. Hybrid scores combine sparse and dense.", "Reasoning": "Mentioned", "Judgement": "yes" },
    { "Fact": "5. Goal is improved performance of rephrased queries.", "Reasoning": "Mentioned", "Judgement": "yes" }
  ]
}`,
        error: null,
      },
      attempt: 2,
    },
  ],

  editor_history: [
    {
      output: {
        answer: `{
  "edited_answer": "The query-document alignment scores play a crucial role in refining LLM-generated queries by evaluating the relevance with retrieved documents. These scores are calculated using BM25, dense, and hybrid methods and used for evaluating and storing queries and updating prompt templates to improve performance."
}`,
        error: null,
      },
      attempt: 1,
    },
  ],

  total_time: 48.13,
  final_answer: `The query-document alignment scores help refine LLM-generated queries by measuring their relevance to documents using BM25, dense, and hybrid scores. These scores are stored, used to improve queries, and ensure better performance.`,
  session_id: '1',
};

import React from 'react';
import { KnowledgeBaseDisplay } from '@/features/Chat/components/KnowledgeBase';
import type { ExecutorAgentEnhanced } from '@/types/knowledgeBaseTypes';

// Mock data based on your response_mock.json structure
const mockKnowledgeBaseData: ExecutorAgentEnhanced = {
  trace: [
    {
      hop: 1,
      sub_questions: [
        {
          sub_question:
            'Rank Auto-Hyde among query optimization techniques tested during advanced RAG experiments, including Hyde, Multi-query, and step-back prompting, in terms of answer similarity improvement over the baseline.',
          retrieved_docs: [
            {
              content:
                'Auto-Hyde ranks among the top query optimization techniques tested during advanced RAG experiments in terms of answer similarity improvement over the baseline. It is specifically noted for its effectiveness in enhancing the semantic alignment between generated answers and reference answers. Compared to other techniques like Hyde, Multi-query, and step-back prompting, Auto-Hyde demonstrates a significant improvement in answer similarity, indicating its superior capability in optimizing query responses within the RAG framework.',
              metadata: {
                section: 'Query Optimization Results',
                page: 1,
                source: 'Experiment Report: Advanced RAG – AutoHyDE',
              },
            },
            {
              content:
                'The experiments included techniques such as Hyde, Multi-query, and step-back prompting. However, the specific ranking or comparative performance of Auto-Hyde relative to these other techniques in terms of answer similarity improvement is not explicitly detailed in the provided passages.',
              metadata: {
                section: 'Comparative Analysis',
                page: 2,
                source: 'Query Optimization Survey',
              },
            },
          ],
          global_summary:
            'Auto-Hyde ranks among the top query optimization techniques tested during advanced RAG experiments in terms of answer similarity improvement over the baseline. It is specifically noted for its effectiveness in enhancing the semantic alignment between generated answers and reference answers.',
          local_summary:
            'Based on the retrieved passages, Auto-Hyde is acknowledged as part of the suite of techniques tested, but the exact ranking or quantitative improvement it offers over the baseline is not available in the given information.',
        },
      ],
      reasoner_output: {
        sufficient: false,
        required_documents: [
          'Experiment Report: Advanced RAG – Query Optimization',
          'Experiment Report: Advanced RAG – AutoHyDE',
        ],
        documents_in_context: ['Experiment Report: Advanced RAG – AutoHyDE'],
        reasoning:
          'The global and local summaries indicate that Auto-Hyde is among the top techniques for answer similarity improvement, but specific comparative results against other query optimization techniques like Hyde, Multi-query, and step-back prompting are not detailed. The Query Optimization report is needed to obtain these comparative results.',
        next_sub_questions: [
          'Retrieve answer similarity improvement results for Hyde, Multi-query, and step-back prompting from the Query Optimization experiment report.',
        ],
      },
    },
    {
      hop: 2,
      sub_questions: [
        {
          sub_question:
            'Retrieve answer similarity improvement results for Hyde, Multi-query, and step-back prompting from the Query Optimization experiment report.',
          retrieved_docs: [
            {
              content:
                'Query optimization in retrieval-augmented large language models (LLMs) has experienced rapid growth, there has been a lack of systematic synthesis to clarify its broader trajectory. This survey endeavors to fill this gap by mapping out the query optimization process in retrieval-augmented LLMs, charting its evolution, and anticipating future developments.',
              metadata: {
                section: 'Multiple Pieces of Implicit Evidence',
                page: 1,
                source: 'A Survey of Query Optimization in Large Language Models.pdf',
              },
            },
            {
              content:
                'H Y DE (Gao et al., 2023a) employs a zero-shot prompt with a language model to generate a hypothetical document that captures relevant patterns, even if it contains "hallucinations." An unsupervised contrastive encoder then encodes this document into an embedding vector to identify a neighborhood in the corpus embedding space.',
              metadata: {
                section: '2.1.1 Internal Expansion',
                page: 2,
                source: 'A Survey of Query Optimization in Large Language Models.pdf',
              },
            },
          ],
          global_summary:
            'Auto-Hyde ranks as the most effective query optimization technique in terms of answer similarity improvement over the baseline during advanced Retrieval-Augmented Generation (RAG) experiments. It outperforms other techniques such as Hyde, Multi-query, and step-back prompting.',
          local_summary:
            'The retrieved passages do not contain specific results or data regarding answer similarity improvements for Hyde, Multi-query, and step-back prompting from the Query Optimization experiment report.',
        },
      ],
      reasoner_output: {
        sufficient: false,
        required_documents: ['Experiment Report: Advanced RAG – Query Optimization'],
        documents_in_context: [],
        reasoning:
          'The global and local summaries indicate that Auto-Hyde is highly effective, but specific comparative results for Hyde, Multi-query, and step-back prompting are missing. The Query Optimization report is needed to retrieve these specific results to accurately rank Auto-Hyde among these techniques.',
        next_sub_questions: [
          'Retrieve specific answer similarity improvement results for Hyde from the Query Optimization experiment report.',
          'Retrieve specific answer similarity improvement results for Multi-query from the Query Optimization experiment report.',
          'Retrieve specific answer similarity improvement results for step-back prompting from the Query Optimization experiment report.',
        ],
      },
    },
    {
      hop: 3,
      sub_questions: [
        {
          sub_question:
            'Retrieve specific answer similarity improvement results for Hyde from the Query Optimization experiment report.',
          retrieved_docs: [
            {
              content:
                'The specific answer similarity improvement results for Hyde from the Query Optimization experiment report are not directly provided in the passages. However, Hyde is described as employing a zero-shot prompt with a language model to generate a hypothetical document that captures relevant patterns, even if it contains "hallucinations."',
              metadata: {
                section: '3 Query Optimization using Query 3.1 Query optimization with LLM',
                page: 2,
                source: 'Optimizing Query Generation for Enhanced Document Retrieval in RAG.pdf',
              },
            },
          ],
          global_summary:
            'Auto-Hyde ranks among the top query optimization techniques tested during advanced Retrieval-Augmented Generation (RAG) experiments in terms of answer similarity improvement over the baseline.',
          local_summary:
            'The specific answer similarity improvement results for Hyde from the Query Optimization experiment report are not directly provided in the passages.',
        },
      ],
      reasoner_output: {
        sufficient: false,
        required_documents: ['Experiment Report: Advanced RAG – Query Optimization'],
        documents_in_context: [],
        reasoning:
          'The current information does not include specific experimental results for answer similarity improvement for the techniques Hyde, Multi-query, and step-back prompting from the Query Optimization experiment report. These results are necessary to compare with Auto-Hyde and determine its ranking among these techniques.',
        next_sub_questions: [
          'Retrieve specific answer similarity improvement results for Hyde from the Query Optimization experiment report.',
          'Retrieve specific answer similarity improvement results for Multi-query from the Query Optimization experiment report.',
          'Retrieve specific answer similarity improvement results for step-back prompting from the Query Optimization experiment report.',
        ],
      },
    },
    {
      hop: 'final',
      generator:
        'Auto-Hyde ranks as the most effective query optimization technique in terms of answer similarity improvement over the baseline during advanced Retrieval-Augmented Generation (RAG) experiments. It outperforms other techniques such as Hyde, Multi-query, and step-back prompting. This conclusion is based on the evaluation of semantic alignment between the generated answers and the reference answers, where Auto-Hyde demonstrates superior performance in enhancing the quality of responses generated by large language models.',
      global_memory: [
        'Auto-Hyde ranks among the top query optimization techniques tested during advanced RAG experiments in terms of answer similarity improvement over the baseline.',
        'Auto-Hyde ranks as the most effective query optimization technique in terms of answer similarity improvement over the baseline during advanced RAG experiments.',
        'Auto-Hyde ranks among the top query optimization techniques tested during advanced Retrieval-Augmented Generation (RAG) experiments in terms of answer similarity improvement over the baseline.',
      ],
      local_memory: [
        {
          sub_question:
            'Rank Auto-Hyde among query optimization techniques tested during advanced RAG experiments, including Hyde, Multi-query, and step-back prompting, in terms of answer similarity improvement over the baseline.',
          response:
            'Based on the retrieved passages, Auto-Hyde ranks among the query optimization techniques tested during advanced RAG experiments in terms of answer similarity improvement over the baseline.',
        },
        {
          sub_question:
            'Retrieve answer similarity improvement results for Hyde, Multi-query, and step-back prompting from the Query Optimization experiment report.',
          response:
            'The retrieved passages do not contain specific results or data regarding answer similarity improvements for Hyde, Multi-query, and step-back prompting from the Query Optimization experiment report.',
        },
      ],
    },
  ],
  num_hops: 3,
};

const KnowledgeBaseDemo: React.FC = () => {
  const finalAnswer =
    'Auto-Hyde ranks as the most effective query optimization technique in terms of answer similarity improvement over the baseline during advanced Retrieval-Augmented Generation (RAG) experiments. It outperforms other techniques such as Hyde, Multi-query, and step-back prompting. This conclusion is based on the evaluation of semantic alignment between the generated answers and the reference answers, where Auto-Hyde demonstrates superior performance in enhancing the quality of responses generated by large language models.';

  return (
    <div className="mx-auto min-h-screen max-w-4xl bg-gray-50 p-6">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold text-gray-900">Knowledge Base Response Demo</h1>
        <p className="text-gray-600">
          This demo shows how the new knowledge base response structure will be displayed with
          multi-hop research traces.
        </p>
      </div>

      <div className="rounded-lg bg-white p-6 shadow-lg">
        <KnowledgeBaseDisplay executorAgent={mockKnowledgeBaseData} finalAnswer={finalAnswer} />
      </div>
    </div>
  );
};

export default KnowledgeBaseDemo;

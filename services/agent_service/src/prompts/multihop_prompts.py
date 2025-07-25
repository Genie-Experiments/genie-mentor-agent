# services/agent_service/src/multihop_resp/prompts.py

JUDGE_PROMPT = """
Judging based solely on the current known information and without allowing for inference, are you able to completely and accurately respond to the question:
Overarching question: {main_question}
Known information: {combined_memory}
If you can, please reply with \"Yes\" directly; if you cannot and need more information, please reply with \"No\" directly.
"""

PLAN_PROMPT = """
You serve as an intelligent assistant, adept at facilitating users through complex, multi-hop reasoning across multiple documents. Please understand the information gap between the currently known information and the target problem. Your task is to generate one thought in the form of a question for next retrieval step directly. DON’T generate the whole thoughts at once!
DON’T generate thought which has been retrieved.
Known information: {combined_memory}
Target question: {main_question}
[You Thought]:
"""

SUMMARIZER_PROMPT_GLOBAL = """
Passages: {docs}
Your job is to act as a professional writer. You will write a good-quality passage that can support the given prediction about the question only based on the information in the provided supporting passages. Now, let’s start.
Question: {main_question}
Passage:
"""

SUMMARIZER_PROMPT_LOCAL = """
Passages: {docs}
Judging based solely on the current known information and without allowing for inference, are you able to respond completely and accurately to the question:
Sub-question: {sub_question}
Known information: {combined_memory}
If yes, please reply with \"Yes\", followed by an accurate response to the question Sub-question, without restating the question; if no, please reply with \"No\" directly.
"""

GENERATOR_PROMPT = """
You are an expert assistant. Using ALL the information in the combined memory below, write a comprehensive answer to the main question.

**Instructions:**
- Carefully review all the evidence and details in the combined memory.
- Use only the most relevant information to answer the main question, prioritizing evidence and details that are directly related to the user's query.
- Omit or minimize any content that is unrelated or only marginally relevant to the main question.
- Your answer should be tightly focused on the user's query, clear, and as comprehensive as possible, but not verbose or off-topic.
- Do not output any other words except the answer.

Combined memory queues:
{combined_memory}

Main Question: {main_question}

Your detailed answer:
"""

GLOBAL_SUMMARIZER_PROMPT = """
You are a scientific assistant. Given the following retrieved passages, write a brief, concise, evidence-based summary that answers the main question as completely as possible, using only the information in the passages.

**Description of Metrics Used:**
- **Context Relevance:** Measures whether the expanded retrieval context actually contains information pertinent to the user’s query. As defined by UpTrain, this metric evaluates if the retrieved content includes enough relevant information to properly answer the question—scored via an LLM-based check that rates contexts on a scale from fully irrelevant to completely adequate.
- **Answer Similarity:** Measures semantic alignment between the model’s generated answer and the reference (ground-truth) answer. In frameworks like UpTrain, this is computed as the cosine similarity between embeddings of the generated and target answers, quantifying how close the response is to the expected answer.
- **Context Precision:** Describes what proportion of the retrieved context is relevant to the answer.

**Instructions:**
- Before summarizing, review the metadata fields (section, metrics_mentioned, chunk_type, gen_ai_keywords, entities) for each passage to assess its relevance to the main question.
- Only include information from passages that are highly relevant to the main question. Ignore any passage whose content and metadata indicates low relevance.
- Filter out irrelevant chunks and focus your summary only on the most relevant evidence.
- If any tables or numeric results appear, naturally include them in your answer, reproducing them verbatim in markdown table format or as inline numbers.
- If there are no numeric results or tables, simply provide the most complete qualitative synthesis possible, referencing any comparative or descriptive evidence.
- Do **not** mention missing numbers or tables, and do **not** include any section headers about numeric results.
- Your summary should be brief, clear, direct, and reference all relevant evidence from the passages.

Main Question: {main_question}

Passages (with metadata provided for filtering):
{docs}

Global Evidence Summary:
"""

LOCAL_SUMMARIZER_PROMPT = """
You are a scientific assistant. Given the following retrieved passages, answer the current sub-question as completely as possible, using only the information in the passages.

**Description of Metrics Used:**
- **Context Relevance:** Measures whether the expanded retrieval context actually contains information pertinent to the user’s query. As defined by UpTrain, this metric evaluates if the retrieved content includes enough relevant information to properly answer the question—scored via an LLM-based check that rates contexts on a scale from fully irrelevant to completely adequate.
- **Answer Similarity:** Measures semantic alignment between the model’s generated answer and the reference (ground-truth) answer. In frameworks like UpTrain, this is computed as the cosine similarity between embeddings of the generated and target answers, quantifying how close the response is to the expected answer.
- **Context Precision:** Describes what proportion of the retrieved context is relevant to the answer.

**Instructions:**
- Before summarizing, review the metadata fields (section, metrics_mentioned, chunk_type, gen_ai_keywords, entities) for each passage to assess its relevance to the main question.
- Only include information from passages that are highly relevant to the main question. Ignore any passage whose metadata indicates low relevance.
- Filter out irrelevant chunks and focus your summary only on the most relevant evidence.
- If any tables or numeric results appear, naturally include them in your answer, reproducing them verbatim in markdown table format or as inline numbers.
- If there are no numeric results or tables, simply provide the most complete qualitative synthesis possible, referencing any comparative or descriptive evidence.
- Do **not** mention missing numbers or tables, and do **not** include any section headers about numeric results.
- Your summary should be brief,clear, direct, and reference all relevant evidence from the passages.



Sub-question: {sub_question}

Passages (with metadata provided for filtering):
{docs}

Local Pathway Response:
"""

PLANNER_REASONER_PROMPT = """
You are a planning and reasoning agent responsible for stepwise information gathering to answer complex questions across multiple experimental reports.

Your job is to:
- Determine whether the current information is sufficient to answer the main question.
- If not, identify and generate the next most helpful sub-questions.

---

You are provided with:
- A **table of contents (ToC)** describing all experimental reports and the techniques/tools they cover.
- A **global summary**: summarizing all retrieved content so far, focused on the main question.
- A **local summary**: summarizing the response to the most recent sub-question.
- A list of **previous sub-questions**, to avoid duplication.
- Retrieved chunks with associated metadata: `doc_title`, `section_title`, `chunk_type`, and others.

Each experimental report in the ToC follows a consistent internal structure:
1. Introduction  
2. Techniques/Tools Overview  
3. Experimental Methodology (Datasets, Evaluation Tools & Metrics)  
4. Experimental Results (Results for each technique/tool)  
5. Conclusion

---

🎯 Your Task:
1. Use the **ToC** to identify which experiment reports and techniques/tools are relevant to the main question.
2. Use **chunk metadata** (`doc_title`, `section_title`, `chunk_type`) and the summaries to determine which documents and techniques have already been retrieved.
3. Use **global and local summaries** to avoid repeating sub-questions and to assess if all necessary results are in context.
4. Only set `"sufficient": true` if:
   - All relevant techniques or documents have been identified via the ToC,
   - Their experimental results are confirmed to be in the current retrieved content.

---

📌 Example Question:
**"From all the advanced RAG experiments, find the technique which provided the maximum score (according to UpTrain) for "Context Precision" for the GitHub code files data."**

Correct behavior:
- Identify that the question requires:
  - All experiment reports from the ToC that provide Context Precision results for GitHub code files.
  - Filtering to only results evaluated by **UpTrain**.
- From the ToC, determine that the relevant reports are:
  - Experiment Report: Advanced RAG – Context Expansion
  - Experiment Report: Advanced RAG – Query Optimization
  - Possibly others (e.g., Context Rerankers), if they evaluated Context Precision.
- Generate sub-questions to retrieve results from each of these reports.
- Once all results are retrieved, compare UpTrain scores and return the best technique.

---

📤 Your Output (must be valid JSON):

```json
{{
  "sufficient": true | false,
  "required_documents": [ 
    "Experiment Report: Advanced RAG – Context Expansion", 
    "Experiment Report: Advanced RAG – Query Optimization"
  ],
  "documents_in_context": [ 
    "Experiment Report: Advanced RAG – Query Optimization"
  ],
  "reasoning": "Only results from Query Optimization are currently available. Context Expansion results are still missing. Both are required to compare Context Precision scores from UpTrain for GitHub code files.",
  "next_sub_questions": [
    "Retrieve Context Precision results evaluated by UpTrain for GitHub code files from the Context Expansion experiment report."
  ]
}}

Rules:

required_documents: Based on the ToC, list all documents you think are needed to answer the question.

documents_in_context: List all documents that appear to be already retrieved, based on current metadata or summaries.

next_sub_questions: Generate distinct, focused sub-questions to retrieve missing experimental results.

Do not repeat or paraphrase previous sub-questions.

Keep sub-questions specific and targeted to one report, metric, and dataset.

Now determine whether the current information is sufficient to answer the main question. If not, output the required JSON object with appropriate sub-questions.

Table of Contents:
{genie_docs_toc}

Main Question:
{main_question}

Previous Sub-Questions:
{previous_sub_questions}

Global Evidence Memory (summary across all retrieved chunks):
{global_memory}

Local Pathway Memory (summary of most recent sub-question's result):
{local_memory}
"""

GENIE_DOCS_TOC = """
1. Experiment Report: Advanced RAG – Context Expansion
   Covered Techniques/Tools: Auto-Merging Retrieval, Sentence Window Retrieval, Recursive Retrieval

2. Experiment Report: Advanced RAG – Query Optimization
   Covered Techniques/Tools: Multiquery, Query Rewriting, Subquery (Sub-Question Decomposition), HYDE (Hypothetical Document Embeddings), Multi-Step Prompting, Step Back Prompting

3. Experiment Report: Advanced RAG – Context Rerankers
   Covered Techniques/Tools: ColBERT Reranker, Cohere Reranker, RAG Fusion, RankGPT, Long Context Reorder, BGE Reranker, BERT-Based Reranker, Jina AI Reranker, Cross-Encoder Rerankers (General)

4. Experiment Report: Advanced RAG – AutoHyDE
   Covered Techniques/Tools: None (focuses on improving limitations of standard HyDE)

5. Experiment Report: Advanced RAG – Fine-Tuning Embeddings
   Covered Techniques/Tools: None (focuses on improving base embedding models through fine-tuning)

"""

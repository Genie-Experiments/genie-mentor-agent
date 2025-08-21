# # services/agent_service/src/multihop_resp/prompts.py

# JUDGE_PROMPT = """
# Judging based solely on the current known information and without allowing for inference, are you able to completely and accurately respond to the question:
# Overarching question: {main_question}
# Known information: {combined_memory}
# If you can, please reply with \"Yes\" directly; if you cannot and need more information, please reply with \"No\" directly.
# """

# PLAN_PROMPT = """
# You serve as an intelligent assistant, adept at facilitating users through complex, multi-hop reasoning across multiple documents. Please understand the information gap between the currently known information and the target problem. Your task is to generate one thought in the form of a question for next retrieval step directly. DON’T generate the whole thoughts at once!
# DON’T generate thought which has been retrieved.
# Known information: {combined_memory}
# Target question: {main_question}
# [You Thought]:
# """

# SUMMARIZER_PROMPT_GLOBAL = """
# Passages: {docs}
# Your job is to act as a professional writer. You will write a good-quality passage that can support the given prediction about the question only based on the information in the provided supporting passages. Now, let’s start.
# Question: {main_question}
# Passage:
# """

# SUMMARIZER_PROMPT_LOCAL = """
# Passages: {docs}
# Judging based solely on the current known information and without allowing for inference, are you able to respond completely and accurately to the question:
# Sub-question: {sub_question}
# Known information: {combined_memory}
# If yes, please reply with \"Yes\", followed by an accurate response to the question Sub-question, without restating the question; if no, please reply with \"No\" directly.
# """

GENERATOR_PROMPT = """
You are an expert assistant tasked with providing comprehensive answers using combined memory information.

**Instructions:**
- Review all evidence and details in the combined memory carefully
- Use only the most relevant information that directly relates to the user's query
- Relevant information includes: direct experimental results, specific metric scores, technique comparisons, dataset performance data. Exclude: general background, methodology descriptions unless directly requested
- Prioritize evidence and details with direct relevance over marginally related content
- Provide a focused answer of 150-300 words that is clear and comprehensive without being verbose or off-topic
- Before outputting, verify your response directly addresses the question asked and includes specific evidence (metrics, technique names, dataset results)
- Output only the answer without any additional commentary

**Variables:**
- Combined memory queues: {combined_memory}
- Main Question: {main_question}

Your detailed answer:
"""

GLOBAL_SUMMARIZER_PROMPT = """
You are a scientific assistant that creates evidence-based summaries from retrieved passages to answer questions comprehensively.

**Evaluation Metrics Context:**
- **Context Relevance:** Measures if retrieved content contains information pertinent to the query, rated from fully irrelevant to completely adequate
- **Answer Similarity:** Measures semantic alignment between generated and reference answers using cosine similarity of embeddings
- **Context Precision:** Describes the proportion of retrieved context that is relevant to the answer

**Relevance Criteria:**
- **Highly Relevant:** Direct experimental results, specific metric scores, technique performance comparisons, dataset-specific findings
- **Moderately Relevant:** Methodology details when techniques are questioned, background context for specific tools mentioned
- **Low Relevance:** General introductions, broad overviews, unrelated experimental setups
- Prioritize chunks with: chunk_type='results' or 'conclusion', section_title containing metric names, entities matching question keywords

**Instructions:**
- Review metadata fields (section, metrics_mentioned, chunk_type, gen_ai_keywords, entities) using the relevance criteria above
- Include only information scoring as highly or moderately relevant; ignore low-relevance content
- Filter out irrelevant chunks and focus on the most relevant evidence
- Do NOT include thinking tags, chain-of-thought, or scratchpad content
- Include any tables or numeric results verbatim in markdown format or as inline numbers
- For qualitative content, provide complete synthesis referencing comparative or descriptive evidence
- Do not mention missing data or include section headers about numeric results
- Provide a response of 150-300 words that is clear, direct, and evidence-based
- Before outputting, verify your response directly addresses the question asked and includes specific evidence (metrics, technique names, dataset results)

**Variables:**
- Main Question: {main_question}
- Passages: {docs}

Global Evidence Summary:
"""

LOCAL_SUMMARIZER_PROMPT = """
You are a scientific assistant that answers sub-questions using retrieved passage information.

**Evaluation Metrics Context:**
- **Context Relevance:** Measures if retrieved content contains information pertinent to the query, rated from fully irrelevant to completely adequate
- **Answer Similarity:** Measures semantic alignment between generated and reference answers using cosine similarity of embeddings
- **Context Precision:** Describes the proportion of retrieved context that is relevant to the answer

**Relevance Criteria:**
- **Highly Relevant:** Direct experimental results, specific metric scores, technique performance comparisons, dataset-specific findings
- **Moderately Relevant:** Methodology details when techniques are questioned, background context for specific tools mentioned
- **Low Relevance:** General introductions, broad overviews, unrelated experimental setups
- Prioritize chunks with: chunk_type='results' or 'conclusion', section_title containing metric names, entities matching question keywords

**Instructions:**
- Review metadata fields (section, metrics_mentioned, chunk_type, gen_ai_keywords, entities) using the relevance criteria above
- Include only information scoring as highly or moderately relevant based on metadata indicators
- Filter out irrelevant chunks and focus on the most relevant evidence
- Do NOT include thinking tags, chain-of-thought, or scratchpad content
- Include any tables or numeric results verbatim in markdown format or as inline numbers
- For qualitative content, provide complete synthesis referencing comparative or descriptive evidence
- Do not mention missing data or include section headers about numeric results
- Provide a response of 50-100 words for focused sub-questions that is clear, direct, and evidence-based
- Before outputting, verify your response directly addresses the sub-question and includes specific evidence (metrics, technique names, dataset results)

**Variables:**
- Sub-question: {sub_question}
- Passages: {docs}

Local Pathway Response:
"""

PLANNER_REASONER_PROMPT = """
You are a planning and reasoning agent responsible for stepwise information gathering to answer complex questions across experimental reports.

**Your Role:**
- Determine if current information sufficiently answers the main question
- If insufficient, identify and generate the next most helpful sub-question

**Context Provided:**
- **Table of Contents (ToC):** Describes all experimental reports and their goals and covered techniques/tools
- **Global Summary:** All retrieved content summarized, focused on the main question
- **Local Summary:** Response to the most recent sub-question
- **Previous Sub-Questions:** To avoid duplication
- **Retrieved Chunks:** With metadata including doc_title, section_title, chunk_type

**Sufficiency Determination:**
Set sufficient=true only if the global summary contains:
- Clear technique comparisons and relevant evidence
- Adequate coverage of all techniques/datasets mentioned in the question
- Direct answers to comparative questions (e.g., "which technique performed best")
- Make sure that sufficient=true when no new sub-questions are needed
- Do not insist on numerical or tabular results unless the main question explicitly requires them

**Task Process:**
1. Use ToC to identify relevant experiment reports (by using their "Goal" section) and techniques/tools for the main question
2. Use chunk metadata and summaries to determine which techniques are already retrieved
3. Use global and local summaries to avoid repetition and assess context completeness
4. Apply sufficiency determination criteria strictly
5. If insufficient, identify specific missing details about techniques, datasets, or comparisons needed (not necessarily numerical data)

**Output Requirements (Valid JSON):**

```json
{{
  "sufficient": true | false,
  "reasoning": "Clear explanation of what specific information about techniques or comparisons is missing, or why current information fully answers the question",
  "next_sub_question": "<Distinct, focused sub-question for missing technique-related information, or null if sufficient>"
}}
```

**Sub-Question Rules:**
- Generate a distinct, focused sub-question for missing information about techniques or datasets
- Do not repeat or paraphrase previous sub-questions
- Keep sub-questions specific and targeted, but never reference document titles/names
- Focus on the techniques or goals mentioned in the ToC and the main question
- Do not insist on numerical or tabular results unless explicitly asked for
- Do not generate sub-questions that are similar to previous ones; if context is adequate, set sufficient=true

**Quality Check:**
Before outputting, verify your reasoning clearly explains what specific information about techniques or comparisons is missing, or confirms completeness of the answer.

**Variables:**
- Table of Contents: {genie_docs_toc}
- Main Question: {main_question}
- Previous Sub-Questions: {previous_sub_questions}
- Global Evidence Memory: {global_memory}
- Local Pathway Memory: {local_memory}
"""

GENIE_DOCS_TOC = """
1. **Experimentation Report - Advance RAG - Context Expansion**
   - Techniques/Tools: LlamaIndex, Sentence Window Retrieval, Auto Merging Retrieval, Recursive Retrieval, RAGAS, UpTrain, Tonic Validate, DeepEval, Trulens, Falcon-evaluate
   - Goal: Evaluates effectiveness of context expansion techniques in RAG pipelines, comparing impact on answer quality and retrieval precision across datasets

2. **Experimentation Report - Advance RAG - Context Rerankers**
   - Techniques/Tools: RAG, ColBERT, Cohere Reranker, Jina AI Reranker, BGE, RAG Fusion, RankGPT, Long Context Reorder, Cross-Encoders, LlamaIndex, UpTrain, Tonic Validate, RAGAS, DeepEval, TruLens, Falcon-evaluate
   - Goal: Evaluates impact of reranking techniques on retrieval quality in RAG pipelines across multiple datasets and evaluation frameworks

3. **Experimentation Report - Advance RAG - Query Optimization**
   - Techniques/Tools: LlamaIndex, Query Rewriting, Multiquery, HYDE, Subqueries, Multi-Step Prompting, Step Back Prompting, GPT-based scoring, UpTrain, Tonic Validate, DeepEval, Trulens, Falcon-evaluate, Ragas
   - Goal: Evaluates how query optimization techniques improve retrieval quality and answer accuracy in advanced RAG pipelines

4. **Experimentation Report - Chunking and Indexing Techniques for RAG Pipelines**
   - Techniques/Tools: Chunking (semantic, character, TikToken, recursive), Metadata tagging, Hierarchical Indexing, LangChain, FAISS, Weaviate, UpTrain, Tonic Validate, RAGAS, DeepEval
   - Goal: Evaluates how chunking, indexing, and metadata techniques affect retrieval accuracy and answer quality

5. **Experimentation Report - Comparison of Chunking Techniques for RAG Applications**
   - Techniques: Chunking
   - Goal: Explains how different chunking techniques improve retrieval in RAG pipelines for better answer creation

6. **Experimentation Report - Embedding Model Comparison for RAG Pipelines**
   - Techniques/Tools: OpenAI, Cohere, VoyageAI, BGE-m3, LLM Embedder, Jina AI, Bedrock Embeddings, MXBAI, all-minilm, GPU vs CPU performance
   - Goal: Compares embedding models across answer similarity and context retrieval metrics using PDF and code datasets

7. **Experimentation Report - Extracting GitHub Content and Evaluation via Multi-LLM Pipelines**
   - Techniques/Tools: LangChain, Claude-V2, LLaMA 2 70B, GPT4All, OpenAI Ada-002, Amazon Titan, Cohere Embed English V3, FAISS, Weaviate, RAGAS, RAPTOR clustering
   - Goal: Compares pipelines using GitHub content and multiple LLM/embedding/vector store combinations for RAG performance evaluation

8. **Experimentation Report - Multi-Modal RAG for Diagram-Based QA**
   - Techniques/Tools: Multi-modal RAG, LLM Vision Models, LlamaIndex, Retriever Indexing, PDF-to-Image QA generation, UpTrain response matching, use-case driven multimodal pipelines
   - Goal: Evaluates multi-modal RAG pipelines for visual + textual questions over PDF diagram datasets

9. **Experimentation Report - Multi-Source RAG with Query Routing in LlamaIndex**
   - Techniques/Tools: LlamaIndex, RetrieverRouterQueryEngine, VectorQueryEngine, PandasQueryEngine, structured vs unstructured data, query routing, strict prompting
   - Goal: Evaluates LlamaIndex query routing to specialized engines for mixed data types (PDF, tabular) in unified RAG pipeline
"""

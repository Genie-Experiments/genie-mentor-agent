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
You are a reasoning and planning agent. Your job is to decide, at each step, whether the information collected so far is sufficient to fully answer the main question, or if more focused sub-questions are needed.
Refer to the documents table of contents below available in the knowledge base to guide your reasoning.
{genie_docs_toc}

Previous sub-questions:
{previous_sub_questions}

**Rules:**
1. Before deciding sufficiency, review both the table of contents and the metadata fields (section, metrics_mentioned, chunk_type, gen_ai_keywords, entities) of the retrieved passages to determine if there are additional sections or documents likely to contain relevant information for the main question. If so, suggest retrieving from those sections in next sub-question.
2. If the main question is broad, multi-part, or could have multiple aspects, you **MUST** always generate a sub-question for the next most important missing aspect.
3. Only set 'sufficient' to true if you are absolutely certain that every aspect of the main question is fully addressed by the evidence.
4. When deciding sufficiency, verify that the highest (or lowest, if relevant) numeric value requested by the main question is present in the evidence.
5. If 'sufficient' is false, generate a single, clear, well-formed sub-question that will help fill the most important remaining gap. The sub-question must be answerable in one step and must NEVER be identical, paraphrased, or semantically equivalent to any previous sub-question listed above. This is a hard rule: if you cannot generate a truly new, distinct sub-question, stop and set next_sub_question to null.
6. Always output a JSON object with the following fields:
   - 'sufficient': true or false
   - 'reasoning': a brief but specific explanation of why the information is or isn't sufficient. In your reasoning, you MUST:
     - Explicitly justify that you have seen all relevant documents for the main question.
     - List all documents (by title, section, or metadata) you consider relevant and explain why you selected them.
     - Clearly explain your reasoning for why these documents are sufficient (or not) to answer the main question.
   - 'next_sub_question': the next sub-question as a string if 'sufficient' is false and it is new (not a repeat or paraphrase of any previous sub-question), or null if 'sufficient' is true or no new sub-question can be generated.

**Example:**
Question: From all the reports on Advanced RAG experiments, find the technique which provided the maximum score (according to UpTrain) for “Context Precision” for the github code files data (generally referred to as Dataset 2 in the reports).
Answer: "The technique that provided the maximum score for \"Context Precision\" for the GitHub code files data (Dataset2) according to UpTrain is **Sentence Window**, with a score of **71%**. This is evident from the UpTrain results for Dataset2, where Sentence Window achieved 71%, outperforming other techniques such as Auto Merging (65%) and HYDE (57%). Although HYDE achieved a high score of 100% with Falcon-evaluate, according to UpTrain, Sentence Window remains the top technique with a score of 71%."

For this question, you should:
- Use the table of contents to check which sections and documents are relevant (e.g., Advanced RAG Experiments, Results, Context Precision).
- Use metadata fields like chunk_type and metrics_mentioned to identify chunks that contain results for "Context Precision" and Dataset 2.
- Ensure you have retrieved all possible relevant documents and chunks before deciding sufficiency. If not, create another unique sub-question for the next hop to retrieve missing evidence. Never repeat or paraphrase a previous sub-question from the list above.

**Additional Guidance:**
- Use metadata fields (section, metrics_mentioned, chunk_type, gen_ai_keywords, entities) to assess the relevance of retrieved passages.
- Ignore any passage whose metadata indicates low relevance to the main question.
- When relevant, reference findings from Genie’s own experiments.
- If in doubt, generate a sub-question.
- Never repeat, paraphrase, or semantically duplicate a previous sub-question for the next hop. This is a strict rule.
- Always output a valid JSON object as described above.
- Only one sub-question per output, or null if sufficient is true or no new sub-question can be generated.

Main Question: {main_question}

Global Evidence Memory:
{global_memory}

Local Pathway Memory (sub-questions and responses):
{local_memory}

Is the information sufficient to answer the main question? If not, what is the next sub-question?
---
IMPORTANT:
- If in doubt, generate a sub-question.
- Never repeat, paraphrase, or semantically duplicate a previous sub-question for the next hop. This is a hard rule.
- Always output a valid JSON object as described above.
- Only one sub-question per output, or null if sufficient is true or no new sub-question can be generated.
"""

# ====== GENIE EXPERIMENTS DOCUMENTS TABLE OF CONTENTS & DESCRIPTIONS ======
GENIE_DOCS_TOC = """
Document 1: Advanced RAG Experiments Report: Context Expansion ("Context Expansion" PDF)
- Introduction – Motivation for context-expansion.
- Overview of Techniques Implemented
- Evaluation Methodology & Datasets
  3.1 Evaluation Tools 
  3.2 Metrics Definitions 
  3.3 Datasets – Dataset-1 (50 PDFs) & Dataset-2 (10 GitHub code files).
- Experimental Results
  4.1 Dataset-1 Results – Tables for Answer Similarity & Context Relevance.
  4.2 Dataset-2 Results – Context Precision table across frameworks.
- Conclusion

Document 2: Advance RAG Experiments Report: Query Optimization ("Query Optimization" PDF)
- Introduction – Rationale for query-optimization in RAG and goals of the experiments.
- Overview of Techniques Used 
- Experimental Methodology
  3.1 Metrics
  3.2 Datasets – Same two datasets (PDFs & GitHub code).
  3.3 Evaluation Frameworks
- Experimental Results
  4.1 Dataset-1 Answer Similarity – Table .
  4.2 Dataset-1 Context Precision – Table .
  4.3 Dataset-2 Context Precision – Table .
- Conclusion

Document 3: Experimentation Report: AutoHyDE - Overcoming Limitations of Hypothetical Document Embeddings
- Introduction – Limitations of standard HyDE and motivation for AutoHyDE.
- Overview of Techniques Used
- Evaluation Methodology
  3.1 Dataset – Extreme Dataset.
  3.2 Evaluation Metric – Hit Rate @ k=100.
- 4 Experimental Results
- 4.1 Limitations of Standard HyDE
  5.1 Working of AutoHyDE 
- Conclusion 

Document 4:Experimentation Report: Fine-Tuning Embeddings for Improved Retrieval Accuracy
- Introduction
- Overview of Techniques and Tools Used 
- Evaluation Methodology
  3.1 Datasets – Three datasets (small PDF set, Extreme PDF set, Genie Wiki with tabular/plain data).
  3.2 Training Configuration .
  3.3 Evaluation Metrics
- Experimental Results
  4.1 Results for each experiment
- Conclusion

Document 5: Advance RAG Experiments Report: Context Rerankers
- Introduction 
- Overview of Techniques Used
- Evaluation Methodology
  3.1 Datasets – Dataset-1 (PDFs), Dataset-2 (GitHub code files).
  3.2 Evaluation Tools 
  3.3 Metrics 
- Experimental Results
  4.1 Dataset-1 Results 
  4.2 Dataset-2 Results 
- Conclusion 

"""

# ====== IMPLEMENTATION TIP ======
# To use GENIE_DOCS_TOC in your system prompts, prepend it to the prompt or pass as a variable.
# Example instruction for LLMs: "Refer to the following Genie Experiments document table of contents and descriptions to guide your retrieval, planning, and summarization. Use the TOC to identify relevant sections for the query."
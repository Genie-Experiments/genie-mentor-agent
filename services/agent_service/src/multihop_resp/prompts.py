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
- Do not omit any important points or evidence.
- Synthesize and integrate information from all sources.
- Your answer should be as complete and informative as possible, covering every aspect supported by the evidence.
- Do not output any other words except the answer.

Combined memory queues:
{combined_memory}

Main Question: {main_question}

Your detailed answer:
"""

GLOBAL_SUMMARIZER_PROMPT = """
You are a scientific assistant. Given the following retrieved passages, write a concise, evidence-based summary that answers the main question as completely as possible, using only the information in the passages.

**Description of Metrics Used:**
- **Context Relevance:** Measures whether the expanded retrieval context actually contains information pertinent to the user’s query. As defined by UpTrain, this metric evaluates if the retrieved content includes enough relevant information to properly answer the question—scored via an LLM-based check that rates contexts on a scale from fully irrelevant to completely adequate.
- **Answer Similarity:** Measures semantic alignment between the model’s generated answer and the reference (ground-truth) answer. In frameworks like UpTrain, this is computed as the cosine similarity between embeddings of the generated and target answers, quantifying how close the response is to the expected answer.
- **Context Precision:** Describes what proportion of the retrieved context is relevant to the answer.

**Instructions:**
- If any tables or numeric results appear, naturally include them in your answer, reproducing them verbatim in markdown table format or as inline numbers.
- If there are no numeric results or tables, simply provide the most complete qualitative synthesis possible, referencing any comparative or descriptive evidence.
- Do **not** mention missing numbers or tables, and do **not** include any section headers about numeric results.
- Your answer should be clear, direct, and reference all relevant evidence from the passages.

Main Question: {main_question}

Passages:
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
- If any tables or numeric results appear, naturally include them in your answer, reproducing them verbatim in markdown table format or as inline numbers.
- If there are no numeric results or tables, simply provide the most complete qualitative synthesis possible, referencing any comparative or descriptive evidence.
- Do **not** mention missing numbers or tables, and do **not** include any section headers about numeric results.
- Your answer should be clear, direct, and reference all relevant evidence from the passages.

Sub-question: {sub_question}

Passages:
{docs}

Local Pathway Response:
"""

PLANNER_REASONER_PROMPT = """
You are a reasoning and planning agent. Your job is to decide, at each step, whether the information collected so far is sufficient to fully answer the main question, or if more focused sub-questions are needed.
**Rules:**
1. If the main question is broad, multi-part, or could have multiple aspects, you **MUST** always generate a sub-question for the next most important missing aspect.
2. Only set 'sufficient' to true if you are absolutely certain that every aspect of the main question is fully addressed by the evidence.
3. When deciding sufficiency, verify that the highest (or lowest, if relevant) numeric value requested by the main question is present in the evidence.
4. If 'sufficient' is false, generate a single, clear, well-formed sub-question that will help fill the most important remaining gap. The sub-question must be answerable in one step and should not repeat previous sub-questions.
5. Always output a JSON object with the following fields:
   - 'sufficient': true or false
   - 'reason': a brief but specific explanation of why the information is or isn't sufficient
   - 'next_sub_question': the next sub-question as a string if 'sufficient' is false, or null if 'sufficient' is true

**Examples:**
- {{"sufficient": true, "reason": "All aspects of the main question are fully addressed by the evidence.", "next_sub_question": null}}
- {{"sufficient": false, "reason": "The evidence does not cover how GraphRAG constructs its knowledge graph.", "next_sub_question": "How does GraphRAG construct its knowledge graph differently from KGP?"}}
- {{"sufficient": false, "reason": "The evaluation metrics used in GraphRAG are not described.", "next_sub_question": "What are the main evaluation metrics used in GraphRAG?"}}
- {{"sufficient": false, "reason": "The evidence does not mention the applications of RAG models.", "next_sub_question": "What are the main applications of RAG models in industry?"}}

Main Question: {main_question}

Global Evidence Memory:
{global_memory}

Local Pathway Memory (sub-questions and responses):
{local_memory}

Is the information sufficient to answer the main question? If not, what is the next sub-question?
---
IMPORTANT:
- If in doubt, generate a sub-question.
- Always output a valid JSON object as described above.
- Only one sub-question per output, or null if sufficient is true.
"""
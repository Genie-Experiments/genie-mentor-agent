FACT_EXTRACT_SCENARIO_DESCRIPTION = """
This task aims to break complex, compound, or descriptive responses into smaller factual units. These facts should stand alone and preserve the meaning without depending on contextual glue. Avoid merging facts or making assumptions. Do not repeat or paraphrase.
"""

FACT_EXTRACT_FEW_SHOT_EXAMPLES = """
[Question]: Which is the tallest monument in Paris?
[Response]: The Eiffel Tower, located in Paris, is one of the most visited monuments in the world. It was named after the engineer Gustave Eiffel, whose company designed and built the tower. Constructed from 1887 to 1889, it was initially criticized by some of France's leading artists and intellectuals.
[Output]:
[
    { "Fact": "The Eiffel Tower is located in Paris." },
    { "Fact": "The Eiffel Tower is one of the most visited monuments in the world." },
    { "Fact": "The Eiffel Tower was named after engineer Gustave Eiffel." },
    { "Fact": "Gustave Eiffel's company designed and built the Eiffel Tower." },
    { "Fact": "The Eiffel Tower was constructed between 1887 and 1889." },
    { "Fact": "The Eiffel Tower was initially criticized by some French artists and intellectuals." }
]
"""

FACT_EXTRACT_OUTPUT_FORMAT = """
{
    "Facts": [
        "1st Fact",
        "2nd Fact",
        ...
    ]
}
In case of no facts, return an empty list: []
"""

FACT_EXTRACT_PROMPT_TEMPLATE = """
You are given a response along with its related question. Your task is to extract independent factual statements from the response. A fact is a sentence that:
- Is objectively true based on the response
- Does not rely on other facts to be understood
- Is not redundant or a paraphrase of another fact
- Should not infer or assume anything beyond what's stated

{scenario_description}

Example Data:
{few_shot_examples}

Return the output only in the following JSON format:
{output_format}

Task Data:
[Question]: {question}
[Response]: {response}
[Output]:
"""



EVALUATE_PROMPTING_INSTRUCTIONS = (
    "For each fact, classify it as yes (factually correct), no (incorrect), or unclear. Also explain why."
)

EVALUATE_SCENARIO_DESCRIPTION = (
    "You are given a set of facts and a reference context. Evaluate each fact."
)

EVALUATE_FEW_SHOT_EXAMPLES = """
Example 1:
{
  "fact": "The Eiffel Tower is located in Paris.",
  "label": "yes",
  "reasoning": "This is a well-known and verifiable fact supported by any reference about Paris landmarks."
}

Example 2:
{
  "fact": "The Eiffel Tower was built in 1989.",
  "label": "no",
  "reasoning": "The Eiffel Tower was completed in 1889, not 1989, so this statement is factually incorrect."
}

Example 3:
{
  "fact": "The Eiffel Tower was the first structure made entirely of steel.",
  "label": "unclear",
  "reasoning": "The response does not mention anything about the construction materials of the Eiffel Tower, so this cannot be verified from the given context."
}
"""

EVALUATE_OUTPUT_FORMAT = """
{
  "Evaluations": [
    {
      "fact": "...",
      "label": "yes" | "no" | "unclear",
      "reasoning": "..."
    },
    ...
  ]
}
"""

FACT_EVAL_PROMPT_TEMPLATE = """
You are a detail-oriented LLM whose task is to determine if the given facts are supported by the given context. 
Each fact is separated by the following symbol: ", ". 
For the given task data, go over each fact sentence one by one, and write down your judgement.

{prompting_instructions}

{scenario_description}

Example Data.
{few_shot_examples}

Return the output only in the corresponding JSON format. Do not output anything other than this JSON object:
{output_format}

Task Data.
[Facts]: {facts}
[Context]: {context}
[Output]:
"""

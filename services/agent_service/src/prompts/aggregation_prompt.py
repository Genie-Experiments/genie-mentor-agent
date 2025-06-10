generate_aggregated_answer = '''
You are an assistant tasked with aggregating results fetched from multiple sources in response to a user query.
When aggregating the results, ensure they are relevant to the user's query and follow the given aggregation strategy.
In order, Result appearing first is A, then B and so on.
User Query: "{user_query}"
Results: {results}
Aggregation Strategy: "{strategy}"

Instructions:
- Aggregate the provided results into a coherent and concise response.
- Include inline citations for every factual claim using the format [Source][Number], where:
    - Source is a one-letter code representing the source agent (e.g., A for KB, B for WebSearch, C for GitHub). Maintain the order in which you recieved.
    - Number is the corresponding index of the document from that source (e.g., [A][1], [B][2]).
- Preserve all citation references as provided in the results — do not modify them or invent new ones.
- Do not combine unrelated results. Prioritize accuracy and clarity.
- Return the response as a properly formatted JSON object using the following structure:

{{
    "answer": "<your aggregated response here>"
}}
'''

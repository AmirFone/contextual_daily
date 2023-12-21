from Open_AI_functions import OpenAIClient

def construct_prompt(query: str, context: list):
    """
    Constructs a GPT prompt including a query and its context.
    :param query: The query string.
    :param context: A list of context items, each expected to be a dictionary with 'title' and 'content'.
    :return: Constructed prompt as a string.
    """
    prompt = f"I have a query: '{query}'. Based on the following context, how would you respond?\n\n"
    for index, doc in enumerate(context):
        prompt += f"Document {index}:\nContent: {doc}\n\n"
    prompt += "Response:"
    return prompt

def create_gpt_query(query: str, context: list):
    """
    Creates a GPT query with the provided query and context.
    :param query: The query string.
    :param context: A list of context items for the query.
    :return: The GPT model's response.
    """
    if not context:
        return f"No context provided for this query: {query}"

    openai_client = OpenAIClient()
    prompt = construct_prompt(query, context)
    
    try:
        llm_response_with_context = openai_client.query_gpt3_5_turbo(prompt)
        return llm_response_with_context
    except Exception as e:
        print(f"Error querying GPT model: {e}")
        return None

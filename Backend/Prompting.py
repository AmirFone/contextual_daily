from Open_AI_functions import OpenAIClient


def construct_prompt(query: str, context: list):
    """
    Constructs a GPT prompt including a query and its context.
    :param query: The query string.
    :param context: A list of context items, each expected to be a dictionary with 'title' and 'content'.
    :return: Constructed prompt as a string.
    """
    prompt = prompt = (f"I have a query related to a document: '{query}'. The document is divided into different sections, "
          f"each providing unique information. Please analyze the section(s) most relevant to the query for your response. "
          f"Here is the pertinent context from the document: \n\n{context}\n\n"
          f"Based on this context, please provide an answer that is as accurate and helpful as possible, "
          f"without revealing the analytical process used to contextualize the response.")

    prompt += "Response:"
    print(f"contextete: {context}")
    print("promptrer:",prompt)
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
    # print(f"prompt: {prompt}")

    try:
        llm_response_with_context = openai_client.query_gpt3_5_turbo(prompt)
        print(f"llm_response_with_context: {llm_response_with_context}")
        return llm_response_with_context
    except Exception as e:
        print(f"Error querying GPT model: {e}")
        return None

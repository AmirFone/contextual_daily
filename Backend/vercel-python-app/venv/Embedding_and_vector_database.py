import os
import json
from supabase import create_client
from Open_AI_functions import OpenAIClient

# Constants
MATCH_THRESHOLD = 0.6
MATCH_COUNT = 15


def get_supabase_client():
    """
    Initializes and returns a Supabase client.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)


def upload_embeddings_to_db(embeddings_dict: dict, specific_cognito_user_id: str):
    """
    Uploads embeddings to the database.
    :param embeddings_dict: Dictionary of embeddings.
    :param specific_cognito_user_id: User ID for whom embeddings are being uploaded.
    """
    supabase = get_supabase_client()
    for key in embeddings_dict:
        embedding,content= embeddings_dict[key]
        # print(f"embedding_one{embedding} embedding_one_End")
        # print(f"embedding_two{content} embedding_two_End")
        embedding_list = (
            embedding.tolist() if not isinstance(embedding, list) else embedding
        )
        # embedding_list = embedding

        try:
            response = (
                supabase.table("documents_embeddings")
                .insert(
                    {
                        "user_id": specific_cognito_user_id,
                        "content": content,
                        "embedding": embedding_list,
                    }
                )
                .execute()
            )

        except Exception as e:
            print(f"An error occurred: {e}")
        # print(f"embedding uploaded to database:{response} ")

def get_closest_documents(
    cognito_user_id: str,
    query: str,
    match_threshold=MATCH_THRESHOLD,
    match_count=MATCH_COUNT,
):
    """
    Retrieves documents closest to the query embedding.
    :param cognito_user_id: User ID for document matching.
    :param query: Query string to match.
    :param match_threshold: Threshold for matching documents.
    :param match_count: Number of documents to return.
    :return: List of matching documents.
    """
    supabase = get_supabase_client()
    openai_client = OpenAIClient()
    query_embedding = openai_client.get_embeddings(query)
    # print('quarry_embedding:',query_embedding)
    # print(f'cognito_user_id:{cognito_user_id}')
    query_embedding_list = (
        query_embedding.tolist()
        if not isinstance(query_embedding, list)
        else query_embedding
    )

    try:
        response = supabase.rpc(
            "match_documents",
            {
                "cognito_user_id": cognito_user_id,
                "query_embedding": query_embedding_list,
                "match_threshold": match_threshold,
                "match_count": match_count,
            },
        ).execute()
        return json.dumps(response.data)
    except Exception as e:
        print(f"Error in retrieving documents: {e}")
        return []

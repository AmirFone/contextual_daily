
import os
from supabase import create_client, Client
from Audio_processing import get_embeddings
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
global supabase
supabase: Client = create_client(url, key)

def upload_embeddings_to_db(embeddings_dict: dict, specific_cognito_user_id: str):
    global supabase
    # Iterate over the dictionary of embeddings
    for content, embedding in embeddings_dict.items():
        # Convert the embedding to a list if it's not already
        if not isinstance(embedding, list):
            embedding = embedding.tolist()

        # Insert the data into the 'documents' table
        response = supabase.table('documents').insert({
            'user_id': specific_cognito_user_id,
            'content': content,
            'embedding': embedding,
        }).execute()

        # Check if the insertion was successful
        if response.error:
            print(f"Failed to insert data for user {specific_cognito_user_id}: {response.error}")
        else:
            print(f"Data inserted successfully for user {specific_cognito_user_id}")


def get_closest_documents(cognito_user_id: str, query: str, match_threshold=0.78,  match_count=10):
    global supabase
    # Convert the query into an embedding
    query_embedding = get_embeddings(query)
    if not isinstance(query_embedding, list):
        query_embedding = query_embedding.tolist()

    try:
        # Construct and execute the raw SQL query
        # sql_query = """
        # SELECT * FROM match_documents(%s, %s, %s, %s);
        # """
        response = supabase.rpc("match_documents", {
            "cognito_user_id": cognito_user_id, 
            "query_embedding": query_embedding, 
            "match_threshold": match_threshold, 
            "match_count": match_count
        }).execute()

        if response.error:
            print(f"Error fetching documents: {response.error}")
            return []

        # Extracting the content from the response
        documents = response.data
        return documents

    except Exception as e:
        print(f"Error in retrieving documents: {e}")
        return []
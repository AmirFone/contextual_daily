
import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
global supabase
supabase: Client = create_client(url, key)

def upload_embeddings_to_db(embeddings_dict: dict, specific_cognito_user_id: str):
	global supabase
	# Iterate over the dictionary of embeddings
	for user_id, embedding in embeddings_dict.items():
		# Only upload the embeddings for the specific Cognito user ID
		if user_id == specific_cognito_user_id:
			# Convert the embedding to a list if it's not already
			if not isinstance(embedding, list):
				embedding = embedding.tolist()

			# Insert the data into the 'documents' table
			response = supabase.table('documents_embedding').insert({
				'user_id': user_id,
				'embedding': embedding,
			}).execute()

			# Check if the insertion was successful
			if response.error:
				print(f"Failed to insert data for user {user_id}: {response.error}")
			else:
				print(f"Data inserted successfully for user {user_id}")
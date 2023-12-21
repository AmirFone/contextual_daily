from openai import OpenAI
import requests

class OpenAIClient:
    def __init__(self, model_name="gpt-3.5-turbo-16k", embedding_model="text-embedding-ada-002"):
        self.client = OpenAI()
        self.model_name = model_name
        self.embedding_model = embedding_model

    def query_gpt3_5_turbo(self, prompt, temperature=1, max_tokens=1000, top_p=1, frequency_penalty=0, presence_penalty=0):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network or API error occurred: {e}")

    def get_embeddings(self, text):
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            if response.status_code == 200:
                return response.data[0].embedding
            else:
                raise Exception(f"Error in OpenAI API call: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network or API error occurred: {e}")

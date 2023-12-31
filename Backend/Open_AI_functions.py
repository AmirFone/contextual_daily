from openai import OpenAI
import requests
import re

class OpenAIClient:
    def __init__(
        self, model_name="gpt-3.5-turbo-16k", embedding_model="text-embedding-ada-002"
    ):
        self.client = OpenAI()
        self.model_name = model_name
        self.embedding_model = embedding_model

    def query_gpt3_5_turbo(
        self,
        prompt,
        temperature=1,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    ):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
            )
            response_text = str(response.choices[0].message.content).strip('"')
            print(f"responsxfvdgdsfe:{response_text}")
            return str(response_text)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network or API error occurred: {e}")

    def get_embeddings(self, text):
        # Sanitize and preprocess the text
        sanitized_text = self.sanitize_text(text)

        try:
            response = self.client.embeddings.create(
                input=[sanitized_text],  # Ensure the text is in a list
                model=self.embedding_model
            )
            # Correctly access the embedding from the response
            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            raise Exception(f"Error in OpenAI API call: {e}")

    @staticmethod
    def sanitize_text(text):
        """ Sanitize and preprocess the text """
        # Convert to lowercase
        text = text.lower()
        # Remove new lines and extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove special characters (optional, based on your needs)
        text = re.sub(r'[^\w\s]', '', text)
        return text
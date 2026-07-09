import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("OPENROUTER_MODEL", "google/gemma-3-4b-it:free")
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )

    def generate_answer(self, prompt: str) -> str:
        if not self.api_key:
            raise Exception("API Key is missing")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Catch network errors, timeouts, API failures
            raise Exception(f"LLM API Error: {str(e)}")

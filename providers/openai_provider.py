import os
from openai import OpenAI
from dotenv import load_dotenv
from .base_provider import BaseProvider

load_dotenv()

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key=None, base_url="https://api.openai.com/v1"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ Clave API de OpenAI no encontrada")
        self.client = OpenAI(api_key=self.api_key)
        self.default_model = "gpt-3.5-turbo"

    def generate_text(self, prompt, model=None, max_tokens=100, temperature=0.7, **kwargs):
        model = model or self.default_model
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()

# En providers/llm/claude_provider.py
import os
import requests
from dotenv import load_dotenv
from providers.base_provider import BaseProvider

load_dotenv()

class ClaudeProvider(BaseProvider):
    def __init__(self, api_key=None, base_url="https://api.anthropic.com/v1", default_model=None):
        # Usar ANTHROPIC_API_KEY en lugar de CLAUDE_API_KEY
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("❌ ANTHROPIC_API_KEY no está definido")
        
        self.base_url = base_url
        self.default_model = default_model or "claude-3-haiku-20240307"
        
    def generate_text(self, prompt, model=None, max_tokens=300, temperature=0.7, **kwargs):
        model = model or self.default_model

        # Método de autenticación confirmado que funciona
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        body = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        # Añadir parámetros adicionales si se proporcionan
        if "system" in kwargs:
            body["system"] = kwargs["system"]
        
        if "top_p" in kwargs:
            body["top_p"] = kwargs["top_p"]
            
        if "top_k" in kwargs:
            body["top_k"] = kwargs["top_k"]

        try:
            response = requests.post(f"{self.base_url}/messages", headers=headers, json=body)
            
            # Imprimir información de depuración para errores
            if response.status_code != 200:
                print(f"❌ Error API: {response.status_code}")
                print(f"Detalles: {response.text}")
                
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
        except Exception as e:
            # Añadir más información sobre el error
            error_message = f"❌ Error al generar texto con Claude: {e}"
            try:
                # Intentar obtener más detalles del error si está disponible
                if hasattr(e, 'response') and e.response is not None:
                    error_message += f"\nDetalles: {e.response.text}"
            except:
                pass
            raise RuntimeError(error_message)
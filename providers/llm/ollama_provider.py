import requests

class OllamaProvider:
    def __init__(self, base_url="http://localhost:11434", default_model="gemma3:1b", **kwargs):
        self.url = f"{base_url}/api/generate"
        self.model = default_model

    def generate_text(self, prompt):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "⚠️ Sin respuesta del modelo.")
        except Exception as e:
            return f"❌ Error en OllamaProvider: {e}"

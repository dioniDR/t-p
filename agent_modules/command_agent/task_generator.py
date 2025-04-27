import requests

class TaskGenerator:
    def __init__(self, model="gemma3:1b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, input_text):
        payload = {
            "model": self.model,
            "prompt": input_text,
            "stream": False  # devuelve todo el texto de una
        }

        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "⚠️ No se recibió respuesta del modelo.")
        except Exception as e:
            return f"❌ Error al generar respuesta: {e}"

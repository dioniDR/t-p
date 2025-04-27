 README.md – Proyecto t-p
markdown
Copy
Edit
# 🧠 t-p — Proveedor Inteligente de Lenguaje

Este proyecto es un sistema modular que permite conectar y alternar entre diferentes **proveedores de modelos de lenguaje (LLMs)** como OpenAI, Claude (Anthropic) y un proveedor falso (`FakeProvider`) para pruebas offline. Diseñado para ser extensible, seguro y fácil de probar desde Jupyter o interfaces futuras.

---

## 🚀 Objetivos del proyecto

- ✅ Desacoplar la lógica del proveedor de IA mediante una **interfaz común (`BaseProvider`)**
- ✅ Permitir configuración desde un archivo `.yaml` y `.env`
- ✅ Alternar proveedores en caliente desde código o notebook
- ✅ Usar una estructura clara, extensible y fácil de mantener
- ✅ Incluir proveedor de prueba (`FakeProvider`) sin conexión

---

## 📦 Estructura del proyecto

t-p/ ├── config/ │ └── settings.yaml # Configuración principal de proveedores ├── providers/ │ ├── base_provider.py # Interfaz abstracta │ ├── openai_provider.py # OpenAI LLM vía API │ ├── claude_provider.py # Claude (Anthropic) │ ├── fake_provider.py # Proveedor falso para pruebas │ └── provider_manager.py # Orquestador de proveedores ├── notebooks/ │ └── providers_test.ipynb # Notebook interactivo de pruebas ├── utils/ │ └── logger.py # (opcional) Logging futuro ├── .env # Claves API ├── requirements.txt └── README.md

yaml
Copy
Edit

---

## 🔧 Instalación

1. Clona este repositorio:

```bash
git clone https://github.com/tu-usuario/t-p.git
cd t-p
Crea un entorno virtual:

bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
Instala las dependencias:

bash
Copy
Edit
pip install -r requirements.txt
Crea el archivo .env con tus claves API:

env
Copy
Edit
OPENAI_API_KEY=sk-xxxxx
CLAUDE_API_KEY=sk-ant-xxxxx
⚙️ Configuración (settings.yaml)
yaml
Copy
Edit
default_provider: openai

providers:
  openai:
    api_key: ${OPENAI_API_KEY}
  claude:
    api_key: ${CLAUDE_API_KEY}
    base_url: https://api.anthropic.com/v1
  fake: {}
📗 Uso desde Jupyter
python
Copy
Edit
from providers.provider_manager import ProviderManager

manager = ProviderManager(config_path="../config/settings.yaml")

# Usar proveedor activo por defecto
provider = manager.get_provider()
print(provider.generate_text("¿Qué es una API REST?"))

# Cambiar proveedor en caliente
manager.set_provider("claude")
print(manager.get_provider().generate_text("Hola Claude"))

# Consultar a uno específico sin cambiar el actual
respuesta = manager.ask_provider("fake", "¿Quién eres?")
print(respuesta)
✨ Proveedores disponibles

Nombre	Descripción
openai	GPT (vía OpenAI API)
claude	Claude 3 (Anthropic API)
fake	Proveedor simulado sin red
🧩 Extensiones futuras
get_capabilities() por proveedor

integración con CLI y APIs web

historial de consultas en modo log

UI básica con streamlit o webapp

🧠 Créditos
Desarrollado por Dioni — usando Python, Jupyter, y una arquitectura modular pensada para IA moderna y escalabilidad.

yaml
Copy
Edit

---

¿Quieres que este README incluya capturas o gifs del notebook más adelante? También se puede usar `badges` de estado o agregar un diagrama de arquitectura si lo deseas.








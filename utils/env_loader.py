# 📚 utils/env_loader.py

import os

def load_env_variables(env_path=".env"):
    """Carga las variables de un archivo .env manualmente."""
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

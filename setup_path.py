# 📚 setup_path.py: Detectar automáticamente la raíz del proyecto

import os
import sys

def find_project_root(reference_files=[".env", "pyproject.toml", "requirements.txt", ".project-root"]):
    """Sube carpetas hasta encontrar un archivo que indique la raíz del proyecto."""
    current_dir = os.getcwd()
    
    while True:
        if any(os.path.exists(os.path.join(current_dir, ref)) for ref in reference_files):
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            print(f"✅ Raíz del proyecto detectada dinámicamente: {current_dir}")
            return current_dir
        
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            raise RuntimeError(f"🚫 No se encontró ninguna referencia de proyecto en las carpetas superiores.")
        
        current_dir = parent_dir

# 🔥 Ejecutarlo automáticamente
PROJECT_ROOT = find_project_root()

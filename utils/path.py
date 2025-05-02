# utils/path_resolver_minimal.py
import os
import sys
from pathlib import Path

def setup_project_path():
    """
    Configura correctamente los paths del proyecto para las importaciones.
    Debe llamarse al principio de los scripts principales o notebooks.
    """
    # Buscar la raíz del proyecto (donde está setup.py o pyproject.toml)
    current = Path().resolve()
    
    # Subir en la jerarquía hasta encontrar marcadores
    while current != current.parent:
        if (current / "setup.py").exists() or (current / "pyproject.toml").exists():
            break
        current = current.parent
    
    # Si llegamos a la raíz del sistema, usar directorio actual
    project_root = current
    
    # Añadir al path si no está ya
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        
    return project_root

# Ejecutar automáticamente
PROJECT_ROOT = setup_project_path()
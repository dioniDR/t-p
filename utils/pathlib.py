# utils/path_resolver.py
import os
import sys
import inspect
from pathlib import Path
from typing import Optional, Union, List, Dict, Set

class PathResolver:
    """
    Clase para la resolución de rutas del proyecto.
    Permite encontrar automáticamente la raíz del proyecto y configurar sys.path.
    Maneja repositorios anidados y dependencias externas.
    """
    
    _instance = None  # Patrón Singleton
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PathResolver, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._project_root = None
        self._subprojects = {}  # Almacena rutas a subproyectos encontrados
        self._paths_added = set()  # Tracking de paths añadidos para evitar duplicados
        
        # Marcadores de raíz de proyecto
        self._markers = [
            ".git",           # Repositorio Git
            ".project-root",  # Marcador personalizado
            "setup.py",       # Paquetes Python
            "pyproject.toml", # Proyectos modernos
            ".env",           # Entornos
            "requirements.txt" # Dependencias
        ]
        
        self._initialized = True
    
    def find_project_root(self, start_dir: Optional[Union[str, Path]] = None) -> Path:
        """
        Encuentra la raíz del proyecto buscando archivos de marcador.
        
        Args:
            start_dir: Directorio desde donde comenzar la búsqueda
                      (por defecto, el directorio del que llama)
        
        Returns:
            Path a la raíz del proyecto
        """
        if self._project_root:
            return self._project_root
            
        # Determinar el directorio de inicio
        if start_dir is None:
            # Obtener el directorio del archivo que llama a esta función
            caller_frame = inspect.stack()[1]
            caller_file = caller_frame.filename
            start_dir = Path(caller_file).parent
        
        start_dir = Path(start_dir).resolve()
        
        # Subir en la jerarquía de directorios hasta encontrar un marcador
        current_dir = start_dir
        while True:
            # Verificar si algún marcador existe en el directorio actual
            if any((current_dir / marker).exists() for marker in self._markers):
                self._project_root = current_dir
                return current_dir
                
            # Moverse al directorio padre
            parent_dir = current_dir.parent
            
            # Si llegamos a la raíz del sistema y no encontramos nada,
            # probablemente estamos en un proyecto sin estructura estándar
            if parent_dir == current_dir:
                # Como último recurso, usar el directorio actual
                self._project_root = start_dir
                return start_dir
                
            current_dir = parent_dir
    
    def discover_subprojects(self) -> Dict[str, Path]:
        """
        Busca subproyectos (repositorios anidados) dentro del proyecto principal.
        
        Returns:
            Diccionario con nombres de subproyectos y sus rutas
        """
        if not self._project_root:
            self.find_project_root()
            
        # Limpiar descubrimientos anteriores
        self._subprojects = {}
        
        # Buscar recursivamente en directorios
        for root, dirs, files in os.walk(self._project_root):
            root_path = Path(root)
            
            # Ignorar directorios ocultos y directorios típicos de venv
            if (root_path.name.startswith('.') or 
                root_path.name in ['venv', 'env', '__pycache__', 'node_modules']):
                dirs[:] = []  # No buscar en subdirectorios
                continue
                
            # Si el directorio actual es un subproyecto, registrarlo
            if any((root_path / marker).exists() for marker in self._markers):
                # Evitar registrar el proyecto principal
                if root_path != self._project_root:
                    name = root_path.name
                    self._subprojects[name] = root_path
        
        return self._subprojects
    
    def setup_python_path(self, include_subprojects: bool = True, 
                          prioritize_main_project: bool = True) -> Set[str]:
        """
        Configura sys.path para incluir la raíz del proyecto y opcionalmente subproyectos.
        
        Args:
            include_subprojects: Si se deben incluir las raíces de subproyectos
            prioritize_main_project: Si el proyecto principal debe tener prioridad
                                    sobre subproyectos en sys.path
        
        Returns:
            Conjunto de rutas añadidas a sys.path
        """
        # Asegurar que tenemos la raíz del proyecto
        project_root = self.find_project_root()
        
        # Descubrir subproyectos si se solicita
        if include_subprojects:
            self.discover_subprojects()
        
        # Añadir la raíz del proyecto principal al principio de sys.path
        project_root_str = str(project_root)
        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
            self._paths_added.add(project_root_str)
        
        # Añadir subproyectos si se solicita
        if include_subprojects and self._subprojects:
            for name, path in self._subprojects.items():
                path_str = str(path)
                
                # Evitar duplicados
                if path_str in sys.path or path_str in self._paths_added:
                    continue
                
                if prioritize_main_project:
                    # Añadir después del proyecto principal
                    index = sys.path.index(project_root_str)
                    sys.path.insert(index + 1, path_str)
                else:
                    # Añadir al principio (tendrá prioridad sobre el proyecto principal)
                    sys.path.insert(0, path_str)
                    
                self._paths_added.add(path_str)
                
                # Buscar requirements.txt en el subproyecto y manejar dependencias
                self._handle_subproject_dependencies(path)
        
        return self._paths_added
    
    def _handle_subproject_dependencies(self, subproject_path: Path) -> None:
        """
        Maneja dependencias de un subproyecto.
        
        Args:
            subproject_path: Ruta al subproyecto
        """
        # Verificar si hay un requirements.txt
        req_file = subproject_path / 'requirements.txt'
        if req_file.exists():
            # Aquí podrías implementar lógica para instalar las dependencias
            # o al menos advertir sobre ellas
            print(f"⚠️ Subproyecto {subproject_path.name} tiene dependencias en: {req_file}")
        
        # Verificar si hay un setup.py
        setup_file = subproject_path / 'setup.py'
        if setup_file.exists():
            # Si hay un setup.py, el subproyecto debería instalarse como paquete
            print(f"⚠️ Subproyecto {subproject_path.name} tiene setup.py: {setup_file}")
            # Opcionalmente, podrías instalar el paquete en modo desarrollo:
            # subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(subproject_path)])
    
    def get_import_path(self, module_path: Union[str, Path]) -> str:
        """
        Convierte una ruta de archivo a su ruta de importación correspondiente.
        
        Args:
            module_path: Ruta al archivo o directorio a importar
            
        Returns:
            Ruta de importación (por ejemplo, 'mypackage.submodule')
        """
        if not self._project_root:
            self.find_project_root()
            
        path = Path(module_path).resolve()
        
        # Comprobar si está en el proyecto principal
        try:
            rel_path = path.relative_to(self._project_root)
            parts = list(rel_path.parts)
            
            # Eliminar extensión .py si existe
            if parts[-1].endswith('.py'):
                parts[-1] = parts[-1][:-3]
                
            # Convertir path a formato de importación
            return '.'.join(parts)
        except ValueError:
            # No está en el proyecto principal, revisar subproyectos
            for name, subpath in self._subprojects.items():
                try:
                    rel_path = path.relative_to(subpath)
                    parts = list(rel_path.parts)
                    
                    # Eliminar extensión .py si existe
                    if parts[-1].endswith('.py'):
                        parts[-1] = parts[-1][:-3]
                        
                    # Determinar el nombre del módulo base del subproyecto
                    # Podría ser el nombre del directorio o diferente
                    # Aquí asumimos el nombre del directorio como módulo base
                    return '.'.join([name] + parts)
                except ValueError:
                    continue
                    
            # Si llegamos aquí, la ruta no está dentro del proyecto o subproyectos
            raise ValueError(f"La ruta {path} no está dentro del proyecto o subproyectos conocidos")
    
    @property
    def project_root(self) -> Path:
        """Obtiene la raíz del proyecto, calculándola si es necesario."""
        if not self._project_root:
            self.find_project_root()
        return self._project_root
    
    @property
    def subprojects(self) -> Dict[str, Path]:
        """Obtiene los subproyectos, descubriéndolos si es necesario."""
        if not self._subprojects:
            self.discover_subprojects()
        return self._subprojects

# Crear una instancia global para facilitar la importación
resolver = PathResolver()
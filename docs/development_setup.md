# Configuración de Desarrollo

## Entorno de Desarrollo
- Python 3.8+ recomendado
- Virtualenv o venv para gestión de entornos
- IDE: VSCode, PyCharm, etc.

## Configuración del Entorno
1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/t-p.git
cd t-p
```

2. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Herramientas de Desarrollo
- Linting: flake8
- Formateador: black
- Tipado: mypy
- Testing: pytest

## Workflow de Desarrollo
1. Crear rama de feature
```bash
git checkout -b feature/nombre-feature
```

2. Implementar cambios
3. Escribir pruebas
4. Ejecutar validaciones

# Guía de Usuario

## Instalación
```bash
git clone https://github.com/tu-usuario/t-p.git
cd t-p
pip install -r requirements.txt
```

## Configuración
1. Configurar .env con claves API
2. Modificar settings.yaml

## Uso Básico
```python
from providers.provider_manager import ProviderManager

# Inicializar
manager = ProviderManager('config/settings.yaml')

# Generar texto
respuesta = manager.get_provider().generate_text('Tu prompt aquí')
print(respuesta)
```

## Cambiar Proveedor
```python
# Cambiar a Claude
manager.set_provider('claude')
```

## Parámetros Avanzados
- Controlar tokens
- Ajustar temperatura
- Personalizar generación

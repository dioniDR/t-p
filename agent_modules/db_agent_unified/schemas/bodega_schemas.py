# Auto-generated schema validation for database: bodega
from schema import Schema, And, Or, Use, Optional


# Schema for table: categorias
categorias_schema = Schema({
    'categoria_id': int,
    'nombre': And(str, len),
    Optional('descripcion'): Or(None, str),
    Optional('activo'): Or(None, int),
    Optional('fecha_creacion'): Or(None, str),
})

# Schema for table: clientes
clientes_schema = Schema({
    'cliente_id': int,
    'nombre': And(str, len),
    'apellido': And(str, len),
    Optional('email'): Or(None, str),
    Optional('telefono'): Or(None, str),
    Optional('direccion'): Or(None, str),
    Optional('ciudad'): Or(None, str),
    Optional('pais'): Or(None, str),
    Optional('fecha_registro'): Or(None, str),
    Optional('credito_maximo'): Or(None, float),
    Optional('activo'): Or(None, int),
})

# Schema for table: compras
compras_schema = Schema({
    'compra_id': int,
    'proveedor_id': int,
    'empleado_id': int,
    Optional('fecha_compra'): Or(None, str),
    'total': float,
    Optional('estado'): Or(None, str),
    Optional('notas'): Or(None, str),
})

# Schema for table: detalles_compras
detalles_compras_schema = Schema({
    'detalle_compra_id': int,
    'compra_id': int,
    'producto_id': int,
    'cantidad': int,
    'precio_unitario': float,
    'subtotal': float,
})

# Schema for table: detalles_ventas
detalles_ventas_schema = Schema({
    'detalle_venta_id': int,
    'venta_id': int,
    'producto_id': int,
    'cantidad': int,
    'precio_unitario': float,
    Optional('descuento'): Or(None, float),
    'subtotal': float,
})

# Schema for table: empleados
empleados_schema = Schema({
    'empleado_id': int,
    'nombre': And(str, len),
    'apellido': And(str, len),
    Optional('email'): Or(None, str),
    Optional('telefono'): Or(None, str),
    'fecha_contratacion': And(str, len),
    Optional('cargo'): Or(None, str),
    Optional('salario'): Or(None, float),
    Optional('activo'): Or(None, int),
})

# Schema for table: productos
productos_schema = Schema({
    'producto_id': int,
    'codigo': And(str, len),
    'nombre': And(str, len),
    Optional('descripcion'): Or(None, str),
    'categoria_id': int,
    Optional('proveedor_id'): Or(None, int),
    'precio_compra': float,
    'precio_venta': float,
    'stock_actual': int,
    Optional('stock_minimo'): Or(None, int),
    Optional('ubicacion_id'): Or(None, int),
    Optional('fecha_creacion'): Or(None, str),
    Optional('ultimo_ingreso'): Or(None, str),
    Optional('ultima_venta'): Or(None, str),
    Optional('activo'): Or(None, int),
})

# Schema for table: proveedores
proveedores_schema = Schema({
    'proveedor_id': int,
    'nombre': And(str, len),
    Optional('contacto_nombre'): Or(None, str),
    Optional('telefono'): Or(None, str),
    Optional('email'): Or(None, str),
    Optional('direccion'): Or(None, str),
    Optional('ciudad'): Or(None, str),
    Optional('pais'): Or(None, str),
    Optional('fecha_registro'): Or(None, str),
    Optional('activo'): Or(None, int),
})

# Schema for table: ubicaciones
ubicaciones_schema = Schema({
    'ubicacion_id': int,
    'nombre': And(str, len),
    Optional('descripcion'): Or(None, str),
    Optional('capacidad'): Or(None, int),
    Optional('disponible'): Or(None, int),
})

# Schema for table: ventas
ventas_schema = Schema({
    'venta_id': int,
    'cliente_id': int,
    'empleado_id': int,
    Optional('fecha_venta'): Or(None, str),
    'total': float,
    'metodo_pago': And(str, len),
    Optional('estado'): Or(None, str),
    Optional('notas'): Or(None, str),
})

# Export all schemas
schemas = {
    'categorias': categorias_schema,
    'clientes': clientes_schema,
    'compras': compras_schema,
    'detalles_compras': detalles_compras_schema,
    'detalles_ventas': detalles_ventas_schema,
    'empleados': empleados_schema,
    'productos': productos_schema,
    'proveedores': proveedores_schema,
    'ubicaciones': ubicaciones_schema,
    'ventas': ventas_schema,
}
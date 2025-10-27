# ventas/admin.py

from django.contrib import admin
from .models import Categoria, Producto

# 1. Clase de personalización para el modelo Producto
class ProductoAdmin(admin.ModelAdmin):
    # ¿Qué campos quieres ver en la lista de Productos?
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'esta_agotado')
    
    # Crea un campo por el que puedes buscar arriba
    search_fields = ('nombre',)
    
    # Crea filtros en el lado derecho (por Categoría y por Stock)
    list_filter = ('categoria', 'stock')
    
    # Haz que algunos campos sean editables directamente desde la lista
    list_editable = ('precio', 'stock')

    # Función para mostrar un estado simple
    def esta_agotado(self, obj):
        # Muestra 'Sí' o 'No' basado en el stock
        return obj.stock <= 0
    
    # Le da un nombre a la nueva columna en el Admin
    esta_agotado.short_description = 'Agotado'

# 2. Registrar los modelos con sus clases de personalización
admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin) # Usamos la clase personalizada aquí

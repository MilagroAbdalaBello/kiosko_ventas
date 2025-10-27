# ventas/models.py

from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE) # Relación con la tabla Categoria

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    """Representa el recibo o la transacción completa."""
    fecha_venta = models.DateTimeField(auto_now_add=True)
    # Se recomienda usar DecimalField para dinero
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        # Muestra la fecha y el total en el Admin
        return f"Venta #{self.id} - Total: ${self.total_venta}"
    
    class Meta:
        verbose_name_plural = "Ventas"


class DetalleVenta(models.Model):
    """Representa un ítem dentro de un recibo de venta."""
    # Relación: Cada detalle pertenece a una Venta (recibo)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    
    # Relación: Cada detalle apunta al Producto que se vendió
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Precio al momento de la venta
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
        
    class Meta:
        verbose_name_plural = "Detalles de Venta"

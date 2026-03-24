from django.db import models
from django.utils import timezone
from decimal import Decimal
from Dash.models import Tienda
from Productos.models import Producto
from Receta.models import DetalleReceta, Receta
from user.models import User

class Venta(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.IntegerField(default=1) #creo que 1 es activo, 0 es inactivo, no se si existen mas estados
    #vamos a usar el 3 para "cotizacion" cotizacion sera para la app VentaTienda, la cual sera para la "generaci��n"
    #de ventas en las tiendas del pollo frito, y solo se van a registrar sin descontar del stock
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)

    def actualizar_total(self):
        self.total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.save()

    def __str__(self):
        return f"Venta #{self.id} - {self.fecha.strftime('%d/%m/%Y')}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario

        if self.producto:
            # Si es un producto, actualizar su stock
            self.producto.stock -= self.cantidad
            self.producto.save()
        elif self.receta:
            # Si es una receta, actualizar el stock de sus productos
            detalles_receta = DetalleReceta.objects.filter(id_receta=self.receta)
            for detalle in detalles_receta:
                cantidad_necesaria = detalle.cantidad * self.cantidad
                detalle.producto.stock -= cantidad_necesaria
                detalle.producto.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.producto:
            # Devolver stock al producto
            self.producto.stock += self.cantidad
            self.producto.save()
        elif self.receta:
            # Devolver stock a los productos de la receta
            detalles_receta = DetalleReceta.objects.filter(id_receta=self.receta)
            for detalle in detalles_receta:
                cantidad_devolver = detalle.cantidad * self.cantidad
                detalle.producto.stock += cantidad_devolver
                detalle.producto.save()

        super().delete(*args, **kwargs)
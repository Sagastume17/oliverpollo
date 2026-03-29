from django.db import models
from Categoria.models import Categoria
from user.models import User
from Dash.models import Tienda
from datetime import date, timedelta

class Producto(models.Model):
    nombre = models.CharField(max_length=550)
    medida = models.CharField(max_length=550)
    stock = models.IntegerField(default=0)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.BooleanField(default=True)
    id_cate = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    insumo = models.ForeignKey('Insumos', on_delete=models.SET_NULL, null=True, blank=True)  # ← NUEVO CAMPO
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen = models.ImageField(
        upload_to='productos/',
        null=True,
        blank=True,
        help_text="Formatos soportados: JPG, PNG, SVG"
    )

    class Meta:
        ordering = ["id"]
        unique_together = ['nombre', 'medida', 'tienda']

    def __str__(self):
        return f"{self.nombre} - {self.tienda.nombre}"
    

class IngresoProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2)

    # Fecha editable (por defecto ayer)
    fecha_ingreso = models.DateField(default=date.today() - timedelta(days=1))

    # Fecha automática del registro
    fecha = models.DateTimeField(auto_now_add=True)

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    observacion = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Actualizar stock del producto
        self.producto.stock += self.cantidad
        self.producto.precio_compra = self.precio_compra
        self.producto.save()
        super().save(*args, **kwargs)


class Insumos(models.Model):
    nombre = models.CharField(max_length=250, blank=False, null=False)
    fecha = models.CharField(max_length=10, blank=False, null=False)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, blank=False, null=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)


 # Control Interno de Productos

class Producto2(models.Model):
    nombre = models.CharField(max_length=550)
    medida = models.CharField(max_length=550)
    stock = models.IntegerField(default=0)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.BooleanField(default=True)
    id_cate = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    insumo = models.ForeignKey('Insumos2', on_delete=models.SET_NULL, null=True, blank=True)  # ← NUEVO CAMPO
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen = models.ImageField(
        upload_to='productos2/',
        null=True,
        blank=True,
        help_text="Formatos soportados: JPG, PNG, SVG"
    )

    class Meta:
        ordering = ["id"]
        unique_together = ['nombre', 'medida', 'tienda']

    def __str__(self):
        return f"{self.nombre} - {self.tienda.nombre}"
    
from datetime import date, timedelta

class IngresoProducto2(models.Model):
    producto2 = models.ForeignKey(Producto2, on_delete=models.CASCADE)

    cantidad = models.IntegerField(default=0)  # ➕ ingreso
    salida = models.IntegerField(default=0)    # ➖ salida

    precio_compra = models.DecimalField(max_digits=12, decimal_places=2)

    fecha_ingreso = models.DateField(default=date.today() - timedelta(days=1))
    fecha = models.DateTimeField(auto_now_add=True)

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    observacion = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):

        # 🔥 VALIDACIÓN
        if self.cantidad > 0 and self.salida > 0:
            raise ValueError("No puedes ingresar y sacar al mismo tiempo")

        if self.cantidad == 0 and self.salida == 0:
            raise ValueError("Debes ingresar una cantidad o una salida")

        # ➕ INGRESO
        if self.cantidad > 0:
            self.producto2.stock += self.cantidad
            self.producto2.precio_compra = self.precio_compra

        # ➖ SALIDA
        if self.salida > 0:
            if self.producto2.stock < self.salida:
                raise ValueError("No hay suficiente stock")
            self.producto2.stock -= self.salida

        self.producto2.save()
        super().save(*args, **kwargs)

class Insumos2(models.Model):
    nombre = models.CharField(max_length=250, blank=False, null=False)
    fecha = models.CharField(max_length=10, blank=False, null=False)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, blank=False, null=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)


    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


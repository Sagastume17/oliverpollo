from django.db import models
from user.models import User
from Dash.models import Tienda
from decimal import Decimal

class CuadreReporte(models.Model):
    # Información básica
    fecha = models.DateField()
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Fechas de control
    fecha_empanizado = models.DateField(null=True, blank=True)
    fecha_gas = models.DateField(null=True, blank=True)
    fecha_cambio_aceite = models.DateField(null=True, blank=True)
    
    # Totales
    venta_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    gasto_diario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    efectivo_caja = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_depositar = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    numero_boleta = models.CharField(max_length=100, blank=True, null=True)
    faltante = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Información de Pollo Rey
    total_pollo_rey = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    numero_factura_pollo = models.CharField(max_length=100, blank=True, null=True)
    libras_pollo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Campos adicionales
    otros = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha', 'tienda']
        unique_together = ['fecha', 'tienda']  # Solo un reporte por día por tienda

    def __str__(self):
        return f"Cuadre {self.tienda.nombre} - {self.fecha}"

    def save(self, *args, **kwargs):
        # Calcula el efectivo en caja (ventas - gastos + faltante) ← ¡CORREGIDO!
        if not self.efectivo_caja:
            self.efectivo_caja = self.venta_total - self.gasto_diario + self.faltante
        super().save(*args, **kwargs)


class DetalleCuadreInventario(models.Model):
    TIPO_CHOICES = (
        ('P', 'Producto'),
        ('R', 'Receta'),
    )
    
    cuadre = models.ForeignKey(CuadreReporte, on_delete=models.CASCADE, related_name='detalles_inventario')
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    producto = models.ForeignKey('Productos.Producto', on_delete=models.PROTECT, null=True, blank=True)
    receta = models.ForeignKey('Receta.Receta', on_delete=models.PROTECT, null=True, blank=True)
    stock_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    ingreso = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    venta = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    stock_final = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        unique_together = [['cuadre', 'producto'], ['cuadre', 'receta']]

    def __str__(self):
        return f"{self.get_nombre()} - {self.cuadre.fecha}"
        
    def get_nombre(self):
        return self.producto.nombre if self.producto else self.receta.nombre

class Cierre(models.Model):
    ventas = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    gastos = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    caja = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    deposito = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    boleta = models.CharField(max_length=50,blank=False,null=False,default='0')
    pollo = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    boleta_pollo = models.CharField(max_length=50,blank=False,null=False,default='0')
    libras = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    liquido = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    tienda = models.ForeignKey(Tienda,blank=False,null=False,on_delete=models.CASCADE)
    fecha = models.DateField(blank=False,null=False,auto_now_add=True)
    fecha_mod = models.DateTimeField(blank=False,null=False,auto_now_add=True)
    usuario = models.ForeignKey(User,blank=False,null=False,on_delete=models.CASCADE)
    estado = models.IntegerField(blank=False,null=False,default=1)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return str(self.id)





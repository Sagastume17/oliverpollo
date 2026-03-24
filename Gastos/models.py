from django.db import models
from user.models import User
from Dash.models import Tienda

class Gastos(models.Model):
    nombre = models.CharField(max_length=550,blank=False,null=False)
    descripcion = models.TextField(blank=True,null=True,default='Opcional')
    factura = models.TextField(blank=True,null=True,default='S/F')
    cantidad = models.IntegerField(blank=False,null=False,default=0)
    precio = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    total = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    tienda = models.ForeignKey(Tienda,blank=False,null=False,on_delete=models.CASCADE)
    fecha = models.DateField()
    fecha_mod = models.DateTimeField(auto_now=True)
    usuario = models.ForeignKey(User,blank=False,null=False,on_delete=models.CASCADE)
    estado = models.IntegerField(blank=False,null=False,default=1)

    class Meta:
        ordering = ["fecha"]

    def __str__(self):
        return self.nombre

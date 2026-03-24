from django.db import models
from user.models import User

class Facturar(models.Model):
    facturar = models.DecimalField(max_digits=12,decimal_places=2,blank=False,name=False,default=0.00)
    fecha = models.DateField(blank=False,null=False)
    fecha_sistema = models.DateField(blank=False,null=False,auto_now_add=True)
    fecha_mod = models.DateTimeField(blank=False,null=False,auto_now_add=True)
    usuario = models.ForeignKey(User,blank=False,null=False,on_delete=models.CASCADE)
    estado = models.IntegerField(blank=False,null=False,default=1)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return str(self.id)

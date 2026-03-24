from django.db import models
from user.models import User

class Tienda(models.Model):
    nombre = models.CharField(max_length=850,blank=False,null=False)
    fecha = models.DateTimeField(blank=False,null=False,auto_now_add=True)
    fecha_mod = models.DateTimeField(blank=False,null=False,auto_now_add=True)
    estado = models.IntegerField(blank=False,null=False,default=1)
    usuario = models.ForeignKey(User,blank=False,null=False,on_delete=models.CASCADE)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.nombre

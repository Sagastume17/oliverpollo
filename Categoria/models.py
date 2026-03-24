from django.db import models
from user.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=250,blank=False,null=False)
    fecha = models.CharField(max_length=10,blank=False,null=False)
    usuario = models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False)
    imagen = models.ImageField(upload_to='categorias/', null=True, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

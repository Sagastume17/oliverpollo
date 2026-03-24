from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class User(AbstractUser):
    rol = models.CharField(max_length=250, null=True, blank=True)
    estado = models.IntegerField(blank=False,null=False,default=0)
    fecha = models.DateTimeField(blank=False,null=False,auto_now_add=True)
    fecha_mod = models.DateTimeField(blank=False,null=False,auto_now_add=True)
    usuario = models.CharField(max_length=250,blank=True,null=True,default='Admin')
    #tienda = models.CharField(max_length=250,blank=True,null=True)
    

    def __str__(self):
        return self.first_name
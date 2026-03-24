from django.db import models
from Productos.models import Producto
from user.models import User
import uuid
from Dash.models import Tienda


class Receta(models.Model):
    nombre = models.CharField(max_length=250,blank=False,null=False)
    descripcion = models.CharField(max_length=850,blank=False,null=False)
    unidad = models.CharField(max_length=850,blank=False,null=False,default='S/U')
    cantidad = models.IntegerField(blank=False,null=False,default=0)
    tiempo = models.CharField(max_length=850,blank=True,null=True,default='0')
    precio_receta = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    estado = models.IntegerField(blank=False,null=False,default=1)
    fecha = models.DateField(blank=False,null=False)
    usuario = models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False)
    token = models.UUIDField(default=uuid.uuid4,editable=False)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)  # Nuevo campo
    imagen = models.ImageField(upload_to='recetas/', null=True, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return str(self.nombre)
    

class DetalleReceta(models.Model):
    id_receta = models.ForeignKey(Receta,on_delete=models.CASCADE,blank=False,null=False)
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE,blank=False,null=False)
    cantidad = models.IntegerField(blank=False,null=False)
    precio_materia = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    total = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    estado = models.IntegerField(blank=False,null=False,default=1)
    fecha = models.DateField(blank=False,null=False)
    usuario = models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False)
    token = models.UUIDField(default=uuid.uuid4,editable=False)

    class Meta:
        ordering = ["id_receta"]

    def __str__(self):
        return str(self.id_receta)





class SolicitarReceta(models.Model):
    id_receta = models.ForeignKey(Receta,on_delete=models.CASCADE,blank=False,null=False)
    cantidad = models.IntegerField(blank=False,null=False)
    tiempo = models.IntegerField(blank=False,null=False,default=0)
    precio_receta = models.DecimalField(max_digits=12,decimal_places=2,blank=False,null=False,default=0.00)
    estado = models.IntegerField(blank=False,null=False,default=0)
    fecha = models.DateField(blank=False,null=False)
    fecha_entrega = models.DateField(blank=False,null=False)
    usuario = models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False)
    token = models.UUIDField(default=uuid.uuid4,editable=False)

    class Meta:
        ordering = ["id_receta"]

    def __str__(self):
        return str(self.id_receta)
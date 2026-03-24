from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from Dash.models import Tienda
from Productos.models import Producto
from Receta.models import Receta


class UsuarioTienda(models.Model):
    """Modelo para usuarios empleados de tienda"""
    username = models.CharField(max_length=150, unique=True, blank=False, null=False)
    nombre = models.CharField(max_length=100, blank=False, null=False)
    apellido = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    dpi = models.CharField(max_length=20, unique=True, blank=False, null=False)
    password = models.CharField(max_length=128, blank=False, null=False)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, blank=False, null=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre', 'apellido']
        verbose_name = 'Usuario de Tienda'
        verbose_name_plural = 'Usuarios de Tienda'

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.tienda.nombre}"

    def set_password(self, raw_password):
        """Encripta y guarda la contraseña"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifica la contraseña"""
        return check_password(raw_password, self.password)

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class BitacoraVenta(models.Model):
    """Modelo para registrar ventas sin afectar stock"""
    TIPO_CHOICES = [
        ('FEL', 'Venta con Factura'),
        ('inventario', 'Registro de Inventario'),
    ]

    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    usuario_tienda = models.ForeignKey(UsuarioTienda, on_delete=models.CASCADE)
    cliente_nit = models.CharField(max_length=20, default='CF', blank=True)
    cliente_nombre = models.CharField(max_length=200, default='Consumidor Final', blank=True)
    cliente_direccion = models.CharField(max_length=300, default='Ciudad', blank=True)
    tipo = models.CharField(max_length=250,blank=True,null=True)# tipo de venta
    link = models.CharField(max_length=250,blank=True,null=True)# link pdf factura fel
    numero = models.BigIntegerField(blank=True,null=True)
    serie = models.CharField(max_length=550,blank=True,null=True)
    anula = models.CharField(max_length=850,blank=True,null=True)
    fecha_fel = models.CharField(max_length=550,blank=True,null=True)
    fecha = models.DateField(blank=True,null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True, null=True)
    numero_recibo = models.CharField(max_length=50, unique=True)
    estado = models.IntegerField(default=1)  # 1=Activo, 0=Anulado
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='FEL')

    # Información del cliente (solo para tipo FEL)
    

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Bitácora de Venta'
        verbose_name_plural = 'Bitácoras de Ventas'

    def __str__(self):
        return f"Recibo {self.numero_recibo} - {self.tienda.nombre}"

    def save(self, *args, **kwargs):
        if not self.numero_recibo:
            # Generar número de recibo único
            import datetime
            fecha_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            self.numero_recibo = f"REC-{self.tienda.id}-{fecha_str}"
        super().save(*args, **kwargs)

    def actualizar_total(self):
        """Actualiza el total basado en los detalles"""
        self.total = sum(detalle.subtotal for detalle in self.detalles.all())
        self.save()


class DetalleBitacora(models.Model):
    """Detalles de cada venta en la bitácora"""
    bitacora = models.ForeignKey(BitacoraVenta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle de Bitácora'
        verbose_name_plural = 'Detalles de Bitácoras'

    def __str__(self):
        item = self.producto.nombre if self.producto else self.receta.nombre
        return f"{item} x{self.cantidad}"

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    @property
    def nombre_item(self):
        return self.producto.nombre if self.producto else self.receta.nombre


class CajaTienda(models.Model):
    """Registro de dinero inicial diario por tienda"""
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    usuario_tienda = models.ForeignKey(UsuarioTienda, on_delete=models.CASCADE)
    fecha = models.DateField()
    dinero_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['tienda', 'fecha']
        ordering = ['-fecha']
        verbose_name = 'Caja de Tienda'
        verbose_name_plural = 'Cajas de Tiendas'

    def __str__(self):
        return f"Caja {self.tienda.nombre} - {self.fecha}"
        
        

from django.db import models
from django.utils import timezone
from Dash.models import Tienda  # ← importar el modelo correcto

class CierreDiario(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.localdate)
    total_ventas = models.DecimalField(max_digits=12, decimal_places=2)
    dinero_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    cierre_diario = models.DecimalField(max_digits=12, decimal_places=2)
    ticket_texto = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Cierre Diario"
        verbose_name_plural = "Cierres Diarios"
        ordering = ['-fecha']

    def __str__(self):
        return f"Cierre {self.fecha} - {self.tienda.nombre}"


########################  CONTROL DIARIO  #############################

class ControlDiario(models.Model):
    """Formulario de control diario por tienda - Un registro por día"""
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    usuario_tienda = models.ForeignKey(UsuarioTienda, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # Tabla 1: Productos y Saldos (JSONField)
    productos_saldos = models.JSONField(default=dict, blank=True)
    # Estructura: {"Pollo": {"inicio": 10, "ingreso": 5, "final": 15}, ...}
    
    # Tabla 2: Venta por Producto (JSONField)
    venta_productos = models.JSONField(default=dict, blank=True)
    # Estructura: {"Pollo": {"cantidad": "10", "total": 150.50}, ...}
    
    # Tabla 3: Resumen Financiero
    total_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gasto_diario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    efectivo_caja = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_depositar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    no_boleta = models.CharField(max_length=100, blank=True, null=True)
    total_pollo_rey = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    no_factura_pollo_rey = models.CharField(max_length=100, blank=True, null=True)
    libras_pollo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_facturacion = models.CharField(max_length=100, blank=True, null=True)
    
    # Tabla 4: Gastos (JSONField - lista de gastos)
    gastos = models.JSONField(default=list, blank=True)
    # Estructura: [{"descripcion": "Luz", "no_factura": "123", "cantidad": 50.00}, ...]
    
    # Tabla 5: Fechas de Control (JSONField)
    fechas_control = models.JSONField(default=dict, blank=True)
    # Estructura: {"empanizado": "2025-11-19", "gas_freidora_1": "2025-11-18", ...}
    
    # Tabla 6: Resumen productos específicos (se calcula automáticamente de tabla 2)
    # No necesita campo, se toma de venta_productos
    
    # Tabla 7: Otros/Observaciones
    otros = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['tienda', 'fecha']
        ordering = ['-fecha']
        verbose_name = 'Control Diario'
        verbose_name_plural = 'Controles Diarios'
    
    def __str__(self):
        return f"Control {self.fecha} - {self.tienda.nombre}"





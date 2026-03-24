from django import forms
from django.forms import ModelForm
from Cierre.models import Cierre, CuadreReporte, DetalleCuadreInventario
from django.contrib.admin.widgets import AdminDateWidget
from django.db.models import Sum
from decimal import Decimal

from Productos.models import Producto, IngresoProducto
from Venta.models import Venta, DetalleVenta
from Gastos.models import Gastos
from Receta.models import Receta

ESTADO = (
(0,'Baja'),
(1,'Activo'),
)

class CuadreReporteForm(ModelForm):
    class Meta:
        model = CuadreReporte
        fields = ['fecha', 'tienda', 'fecha_empanizado', 'fecha_gas', 'fecha_cambio_aceite',
                'venta_total', 'gasto_diario', 'efectivo_caja', 'total_depositar', 'numero_boleta',
                'total_pollo_rey', 'numero_factura_pollo', 'libras_pollo', 'otros']
        
        labels = {
            'fecha': 'Fecha del Reporte',
            'tienda': 'Tienda',
            'fecha_empanizado': 'Fecha de Inicio Empanizado',
            'fecha_gas': 'Fecha Gas',
            'fecha_cambio_aceite': 'Fecha Cambio de Aceite',
            'venta_total': 'Total de Venta',
            'gasto_diario': 'Gasto Diario',
            'efectivo_caja': 'Efectivo en Caja',
            'total_depositar': 'Total a Depositar',
            'numero_boleta': 'No. de Boleta',
            'total_pollo_rey': 'Total de Pollo Rey',
            'numero_factura_pollo': 'No. Factura de Pollo Rey',
            'libras_pollo': 'Libras de Pollo',
            'otros': 'Otros'
        }

        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tienda': forms.Select(attrs={'class': 'form-select'}),
            'fecha_empanizado': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_gas': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_cambio_aceite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'venta_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'gasto_diario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'efectivo_caja': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'total_depositar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'numero_boleta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de Boleta'}),
            'total_pollo_rey': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'numero_factura_pollo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de Factura'}),
            'libras_pollo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'otros': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones adicionales'})
        }


def crear_detalle_inventario(cuadre):
    """Crear los registros de inventario para un cuadre específico"""
    # Eliminar registros existentes para evitar duplicados
    DetalleCuadreInventario.objects.filter(cuadre=cuadre).delete()
    
    # Productos
    for producto in Producto.objects.filter(tienda=cuadre.tienda, estado=True):
        # Total de ingresos para el día del cuadre
        ingresos_del_dia = IngresoProducto.objects.filter(
            producto=producto,
            fecha__date=cuadre.fecha
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        # Total de ventas para el día del cuadre
        ventas_del_dia = DetalleVenta.objects.filter(
            producto=producto,
            venta__fecha__date=cuadre.fecha,
            venta__tienda=cuadre.tienda,
            venta__estado=1
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        # El stock final es el stock actual del producto
        stock_final = producto.stock
        
        # El stock inicial se calcula restando los ingresos y sumando las ventas del día al stock final
        stock_inicial = stock_final - ingresos_del_dia + ventas_del_dia

        DetalleCuadreInventario.objects.create(
            cuadre=cuadre,
            tipo='P',
            producto=producto,
            stock_inicial=stock_inicial,
            ingreso=ingresos_del_dia,
            venta=ventas_del_dia,
            stock_final=stock_final
        )


class CierreForm(ModelForm):
    class Meta:
        model = Cierre
        fields = ['ventas', 'gastos', 'caja', 'deposito', 'boleta', 'pollo', 
                'boleta_pollo', 'libras', 'liquido', 'tienda', 'usuario', 'estado']
        
        labels = {
            'ventas': 'Ventas',
            'gastos': 'Gastos',
            'caja': 'Caja',
            'deposito': 'Depósito',
            'boleta': 'Boleta',
            'pollo': 'Pollo',
            'boleta_pollo': 'Boleta Pollo',
            'libras': 'Libras',
            'liquido': 'Líquido',
            'tienda': 'Tienda',
            'usuario': 'Usuario',
            'estado': 'Estado'
        }

        widgets = {
            'ventas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese ventas...'}),
            'gastos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese gastos...'}),
            'caja': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese caja...'}),
            'deposito': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese depósito...'}),
            'boleta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese boleta...'}),
            'pollo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese pollo...'}),
            'boleta_pollo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese boleta pollo...'}),
            'libras': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese libras...'}),
            'liquido': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese líquido...'}),
            'tienda': forms.Select(attrs={'class': 'form-select'}),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(choices=ESTADO, attrs={'class': 'form-select'})
        }


class UpdateCierreForm(ModelForm):
    class Meta:
        model = Cierre
        fields = ['ventas', 'gastos', 'caja', 'deposito', 'boleta', 'pollo', 
                'boleta_pollo', 'libras', 'liquido', 'tienda', 'usuario', 'estado']
        
        labels = {
            'ventas': 'Ventas',
            'gastos': 'Gastos',
            'caja': 'Caja',
            'deposito': 'Depósito',
            'boleta': 'Boleta',
            'pollo': 'Pollo',
            'boleta_pollo': 'Boleta Pollo',
            'libras': 'Libras',
            'liquido': 'Líquido',
            'tienda': 'Tienda',
            'usuario': 'Usuario',
            'estado': 'Estado'
        }

        widgets = {
            'ventas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese ventas...'}),
            'gastos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese gastos...'}),
            'caja': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese caja...'}),
            'deposito': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese depósito...'}),
            'boleta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese boleta...'}),
            'pollo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese pollo...'}),
            'boleta_pollo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese boleta pollo...'}),
            'libras': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese libras...'}),
            'liquido': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese líquido...'}),
            'tienda': forms.Select(attrs={'class': 'form-select'}),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(choices=ESTADO, attrs={'class': 'form-select'})
        }
from django import forms
from .models import Producto, IngresoProducto
from datetime import date, timedelta
UNIDAD = (
    ('Saco','Saco'),
    ('Libra','Libra'),
    ('Sobre','Sobre'),
    ('Bolsa','Bolsa'),
    ('Fardo','Fardo'),
    ('Tira','Tira'),
    ('Galon','Galon'),
    ('Unidades','Unidades'),
    ('Paquete','Paquete'),
)

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'medida', 'precio_compra', 'precio_venta', 'id_cate', 'tienda', 'insumo', 'imagen']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Producto',
                'autofocus': True
            }),
            'medida': forms.Select(
                attrs={'class': 'form-select'},
                choices=UNIDAD
            ),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'id_cate': forms.Select(attrs={'class': 'form-select'}),
            'tienda': forms.Select(attrs={'class': 'form-select'}),
            'insumo': forms.Select(attrs={
                'class': 'form-select',
                'required': False  # <-- hace que no sea obligatorio
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


class UpdateProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'medida', 'precio_compra', 'precio_venta', 'id_cate', 'tienda', 'estado', 'imagen']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Producto'
            }),
            'medida': forms.Select(
                attrs={'class': 'form-select'},
                choices=UNIDAD
            ),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'id_cate': forms.Select(attrs={'class': 'form-select'}),
            'tienda': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

class IngresoProductoForm(forms.ModelForm):
    class Meta:
        model = IngresoProducto
        fields = ['cantidad', 'precio_compra', 'observacion', 'fecha_ingreso']

        widgets = {
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'observacion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'fecha_ingreso': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Valor por defecto: el día anterior a hoy
        if not self.initial.get('fecha_ingreso'):
            self.initial['fecha_ingreso'] = date.today() - timedelta(days=1)
            
            

from django import forms
from .models import Insumos

class InsumosForm(forms.ModelForm):
    class Meta:
        model = Insumos
        fields = ['nombre', 'fecha', 'precio_compra', 'tienda']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del insumo'
            }),
            'fecha': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'precio_compra': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'tienda': forms.Select(attrs={'class': 'form-select'}),
        }

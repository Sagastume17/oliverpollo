from django import forms
from .models import Venta, DetalleVenta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['tienda', 'observaciones', 'fecha']
        widgets = {
            'tienda': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'tienda_select'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones (opcional)'
            }),
            'fecha': forms.DateTimeInput(attrs={
                'type': 'date',
                'class': 'form-control'
            })
        }

class DetalleVentaForm(forms.ModelForm):
    tipo = forms.ChoiceField(
        choices=[('producto', 'Producto'), ('receta', 'Receta')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'tipo_item'
        })
    )

    class Meta:
        model = DetalleVenta
        fields = ['cantidad', 'precio_unitario']
        widgets = {
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'id': 'cantidad_item'
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'readonly': True,
                'id': 'precio_unitario'
            })
        }
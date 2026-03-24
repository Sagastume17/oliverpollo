from django import forms
from django.forms import ModelForm
from Gastos.models import Gastos

ESTADO = (
(0,'Baja'),
(1,'Activo'),
)

#forms.Select(attrs={'class': 'selectpicker form-control','data-style':'btn-outline-info','placeholder':'Tipo','require':True},choices=TIPO),

class GastosForm(forms.ModelForm):
    class Meta:
        model = Gastos
        fields = ['fecha', 'nombre', 'descripcion', 'factura', 'cantidad', 'precio', 'tienda']
        
        labels = {
            'fecha': 'Fecha del Gasto',
            'nombre': 'Nombre de Gasto',
            'descripcion': 'Descripcion',
            'factura': 'Factura',
            'cantidad': 'Cantidad',
            'precio': 'Precio',
            'tienda': 'Tienda'
        }

        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Nombre de Gasto','autofocus': True,'required': True}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Descripcion','required': True}),
            'factura': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Factura','required': False}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder':'Cantidad', 'min': 0, 'required': True}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder':'Precio', 'min': 0, 'step': '0.01', 'required': True}),
            'tienda': forms.Select(attrs={'class': 'selectpicker form-control', 'data-style':'btn-outline-info', 'required': True}),
        }


class UpdateGastosForm(ModelForm):
    class Meta:
        model = Gastos
        fields = ['fecha','nombre','descripcion','factura','cantidad','precio','tienda','estado']
        
        labels = {
            'fecha': 'Fecha del Gasto',
            'nombre':'Nombre de Gasto',
            'descripcion':'Descripcion',
            'factura':'Factura',
            'cantidad':'Cantidad',
            'precio':'Precio',
            'tienda':'Tienda',
            'estado':'Estado'
        }     

        widgets = { 
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'readonly': True}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date','required':True}),
            'nombre': forms.TextInput(attrs={'class': 'form-control','placeholder':'Nombre de Gasto','autofocus': True,'required':True}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control','placeholder':'Descripcion','required':True}),
            'factura': forms.TextInput(attrs={'class': 'form-control','placeholder':'Factura','required':True}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control','placeholder':'Cantidad'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control','placeholder':'Precio'}),
            'tienda': forms.Select(attrs={'class': 'selectpicker form-control','data-style':'btn-outline-info'}),
            'estado': forms.Select(attrs={'class': 'selectpicker form-control','data-style':'btn-outline-info'}, choices=ESTADO),
        }


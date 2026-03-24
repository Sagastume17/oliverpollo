from django import forms
from django.forms import ModelForm
from Facturar.models import Facturar

ESTADO = (
(0,'Baja'),
(1,'Activo'),
)

#forms.Select(attrs={'class': 'selectpicker form-control','data-style':'btn-outline-info','placeholder':'Tipo','require':True},choices=TIPO),
class FacturarForm(ModelForm):

    class Meta:
        model = Facturar
        fields = ['facturar','fecha']
        
        labels = {'facturar':'Cantidad a Facturar','fecha':'Fecha de Facturacion'}     

        widgets = { 

                 'facturar':forms.TextInput(attrs={'class': 'form-control','placeholder':'0.00','id':'caja','require':True}),
                 'fecha':forms.TextInput(attrs={'type':'date','class': 'form-control','placeholder':'0.00','id':'deposito','autofocus': True,'require':True}),
        }         


class UpdateFacturarForm(ModelForm):

    class Meta:
        model = Facturar
        fields = ['facturar','fecha']
        
        labels = {'facturar':'Cantidad a Facturar','fecha':'Fecha de Facturacion'}     

        widgets = { 

                 'facturar':forms.TextInput(attrs={'class': 'form-control','placeholder':'0.00','id':'caja','require':True}),
                 'fecha':forms.TextInput(attrs={'type':'date','class': 'form-control','placeholder':'0.00','id':'deposito','autofocus': True,'require':True}),
        }   
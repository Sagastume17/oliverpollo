from django import forms
from django.forms import ModelForm
from Dash.models import Tienda

ESTADO = (
(0,'No Activo'),
(1,'Activo'),
)

#forms.Select(attrs={'class': 'selectpicker form-control','data-style':'btn-outline-info','placeholder':'Tipo','require':True},choices=TIPO),
class TiendaForm(ModelForm):

    class Meta:
        model = Tienda
        fields = ['nombre']
        
        labels = {'nombre':'Nombre de Tienda'}     

        widgets = { 

                 'nombre':forms.TextInput(attrs={'class': 'form-control','placeholder':'Nombre de Tienda','autofocus': True,'require':True}),
        }         


class UpdateTiendaForm(ModelForm):

    class Meta:
        model = Tienda
        fields = ['nombre','estado']
        
        labels = {'nombre':'Nombre de Tienda','estado':'Estado'}     

        widgets = { 

                 'nombre':forms.TextInput(attrs={'class': 'form-control','placeholder':'Nombre de Tienda','autofocus': True,'require':True}),        
                 'estado':forms.Select(attrs={'class': 'selectpicker form-control','data-style':'btn-outline-info','placeholder':'Tipo','require':True},choices=ESTADO),
        }      

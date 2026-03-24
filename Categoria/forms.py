from django import forms
from .models import Categoria


class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = ['nombre', 'imagen']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','require':True,'autofocus': True,'placeholder':'Nombre de Categoria'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class UpdateCategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = ['nombre', 'imagen']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','autofocus': True,'require':True}),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }




from django import forms
from Productos.models import Producto
from .models import Receta,DetalleReceta
from Productos.models import Producto



ESTADO = [('Alta','Alta'),
          ('Baja','Baja'),]

class RecetaForm(forms.ModelForm):

    class Meta:
        model = Receta
        fields = ['nombre','descripcion','cantidad','tiempo','precio_receta', 'tienda', 'imagen']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control','require':True,'autofocus': True,'placeholder':'Nombre de Receta'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control','require':True,'placeholder':'Descripcion de Receta'}),
            'tienda': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.TextInput(attrs={'type':'number','class': 'form-control','require':True,'placeholder':'Cantidad'}),
            'tiempo': forms.TextInput(attrs={'class': 'form-control','require':True,'placeholder':'Espeficique el Tiempo'}),
            'precio_receta': forms.TextInput(attrs={'type':'number','class': 'form-control','require':True,'placeholder':'Cantidad'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }




class UpdateRecetaForm(forms.ModelForm):

    class Meta:
        model = Receta
        fields = ['nombre','descripcion','unidad','cantidad','tiempo','precio_receta','estado','imagen']
        widgets = { 
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'autofocus': True, 'placeholder':'Nombre de Receta'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder':'Descripcion de Receta'}),
            # Se configurará dinámicamente el widget del campo 'unidad'
            'unidad': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.TextInput(attrs={'type':'number', 'class': 'form-control', 'required': True, 'placeholder':'Cantidad'}),
            'tiempo': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder':'Especifique el Tiempo'}),
            'precio_receta': forms.TextInput(attrs={'type':'number', 'class': 'form-control', 'required': True, 'placeholder':'Precio de Receta'}),
            'estado': forms.Select(attrs={'class': 'form-control'}, choices=[]),  # Asumiendo que ESTADO es definido más abajo o en otra parte
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtenemos las medidas únicas de los productos existentes
        medidas = Producto.objects.values_list('medida', flat=True).distinct()
        # Creamos la lista de choices con formato (valor, etiqueta)
        choices_unidad = [(medida, medida) for medida in medidas if medida]
        # Asignamos las opciones al widget del campo 'unidad'
        self.fields['unidad'].widget.choices = choices_unidad



class DetalleRecetaForm(forms.ModelForm):
   
    class Meta:
        model = DetalleReceta
        fields = ['producto','cantidad',]

        widgets = { 
            'producto':forms.Select(attrs={'class': 'form-control',}),
            'cantidad': forms.TextInput(attrs={'type':'number','class': 'form-control','require':True,'placeholder':'Cantidad'}),
        }
        
    def __init__(self, *args, **kwargs):
        tienda = kwargs.pop('tienda', None)
        super().__init__(*args, **kwargs)
        if tienda:
            # Se filtra el queryset para que solo se muestren los productos de la tienda
            self.fields['producto'].queryset = Producto.objects.filter(tienda=tienda)

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import UsuarioTienda, BitacoraVenta, CajaTienda


class LoginTiendaForm(forms.Form):
    """Formulario de login para usuarios de tienda"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'required': True
        })
    )


class BitacoraVentaForm(forms.ModelForm):
    """Formulario para bitácora de ventas"""
    class Meta:
        model = BitacoraVenta
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            })
        }


class CajaTiendaForm(forms.ModelForm):
    """Formulario para registro de caja diaria"""
    class Meta:
        model = CajaTienda
        fields = ['dinero_inicial', 'observaciones']
        widgets = {
            'dinero_inicial': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre la caja...'
            })
        }
        labels = {
            'dinero_inicial': 'Dinero Inicial (Q)',
            'observaciones': 'Observaciones'
        }


class UsuarioTiendaForm(forms.ModelForm):
    """Formulario para crear/editar usuarios de tienda"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        label='Contraseña',
        required=False  # No requerido para edición
    )

    class Meta:
        model = UsuarioTienda
        fields = ['username', 'nombre', 'apellido', 'email', 'telefono', 'dpi', 'tienda']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario único'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'dpi': forms.TextInput(attrs={'class': 'form-control'}),
            'tienda': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'Usuario',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'dpi': 'DPI',
            'tienda': 'Tienda',
        }

    def clean_password(self):
        """Validar contraseña"""
        password = self.cleaned_data.get('password')

        # Si es un nuevo usuario (no tiene instance.pk), la contraseña es requerida
        if not self.instance.pk and not password:
            raise forms.ValidationError('La contraseña es requerida para nuevos usuarios.')

        return password

    def save(self, commit=True):
        """Guardar usuario con contraseña encriptada"""
        usuario = super().save(commit=False)

        # Solo establecer contraseña si se proporcionó
        if self.cleaned_data.get('password'):
            usuario.set_password(self.cleaned_data['password'])

        if commit:
            usuario.save()
        return usuario


#############   CONTROL DIARIO   #############

from django import forms
from .models import ControlDiario

class ControlDiarioForm(forms.ModelForm):
    """Formulario para Control Diario con productos predefinidos"""
    
    # Productos quemados para Tabla 1: Productos y Saldos
    PRODUCTOS_SALDOS = [
        'Pollo', 'Papas', 'Mollejas', 'Medallones', 'Gran Pieza', 'Tortas', 
        'Pan', 'Ensaladas', 'Pay', 'Coca Vidrio', 'ISO Max', 'Soda Lata',
        'Soda Desechable', 'Agua Botella', 'Agua Bolsa', 
        'Mayonesa para ensalada y Hambu', 'Mayonesa para botes', 
        'Salsa para botes', 'Salsa para Hamburguesa', 'Chile galon',
        'Chile sobre', 'Salsa sobre', 'Empanizado', 'PASO #2',
        'Cajas para Pay', 'Vasos p/Mollejas', 'Caja p/papas', 
        'Vasos c/tapa', 'Aceite', 'Aceite Quemado'
    ]
    
    # Productos quemados para Tabla 2: Venta por Producto
    PRODUCTOS_VENTA = [
        'Pollo', 'Papas', 'Mollejas', 'Medallones', 'Gran Pieza', 
        'Hamburguesa', 'Ensaladas', 'Pay', 'Coca Vidrio', 'ISO Max',
        'Soda Lata', 'Soda Desechable', 'Agua Botella', 'Agua Bolsa'
    ]
    
    # Conceptos de Fechas de Control
    CONCEPTOS_FECHAS = [
        'Empanizado', 'Gas Freidora 1', 'Gas Freidora 2',
        'Cambio de Aceite 1', 'Cambio de Aceite 2'
    ]
    
    class Meta:
        model = ControlDiario
        fields = [
            'total_venta', 'gasto_diario', 'efectivo_caja', 'total_depositar',
            'no_boleta', 'total_pollo_rey', 'no_factura_pollo_rey', 
            'libras_pollo', 'fecha_facturacion', 'otros'
        ]
        widgets = {
            'total_venta': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'
            }),
            'gasto_diario': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'
            }),
            'efectivo_caja': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01'
            }),
            'total_depositar': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'
            }),
            'no_boleta': forms.TextInput(attrs={'class': 'form-control'}),
            'total_pollo_rey': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01'
            }),
            'no_factura_pollo_rey': forms.TextInput(attrs={'class': 'form-control'}),
            'libras_pollo': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01'
            }),
            'fecha_facturacion': forms.TextInput(attrs={'class': 'form-control'}),
            'otros': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import UsuarioTienda


class TiendaSecurityMiddleware:
    """
    Middleware para controlar el acceso de usuarios de tienda
    Solo pueden acceder a URLs de VentaTienda
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs permitidas para usuarios de tienda
        self.allowed_urls_tienda = [
            '/venta-tienda/',
            '/logout/',
            '/',  # Para login
        ]
        
        # URLs que requieren autenticación de tienda
        self.tienda_required_urls = [
            '/venta-tienda/',
        ]

    def __call__(self, request):
        # Verificar tipo de usuario
        user_type = request.session.get('user_type')
        current_path = request.path
        
        # Si es usuario de tienda
        if user_type == 'tienda':
            usuario_tienda_id = request.session.get('usuario_tienda_id')
            
            # Verificar que el usuario tienda existe y está activo
            if usuario_tienda_id:
                try:
                    usuario_tienda = UsuarioTienda.objects.get(id=usuario_tienda_id, activo=True)
                    request.usuario_tienda = usuario_tienda
                except UsuarioTienda.DoesNotExist:
                    # Usuario no existe o está inactivo, cerrar sesión
                    request.session.flush()
                    messages.error(request, 'Su cuenta ha sido desactivada')
                    return redirect('Login')
            
            # Verificar si la URL está permitida para usuarios tienda
            if not any(current_path.startswith(url) for url in self.allowed_urls_tienda):
                messages.error(request, 'No tiene permisos para acceder a esta sección')
                return redirect('venta_tienda:menu_principal')
        
        # Si es usuario admin, no puede acceder a VentaTienda
        elif user_type == 'admin' and current_path.startswith('/venta-tienda/'):
            messages.error(request, 'Los administradores no pueden acceder al sistema de tienda')
            return redirect('Admin')
        
        # Si no hay usuario logueado y trata de acceder a VentaTienda
        elif not user_type and any(current_path.startswith(url) for url in self.tienda_required_urls):
            messages.error(request, 'Debe iniciar sesión para acceder')
            return redirect('Login')

        response = self.get_response(request)
        return response


def get_usuario_tienda(request):
    """
    Función helper para obtener el usuario tienda actual
    """
    if request.session.get('user_type') == 'tienda':
        usuario_tienda_id = request.session.get('usuario_tienda_id')
        if usuario_tienda_id:
            try:
                return UsuarioTienda.objects.get(id=usuario_tienda_id, activo=True)
            except UsuarioTienda.DoesNotExist:
                pass
    return None

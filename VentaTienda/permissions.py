from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UsuarioTienda


def tienda_login_required(view_func):
    """
    Decorador que requiere que el usuario sea un usuario de tienda autenticado
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_type') != 'tienda':
            messages.error(request, 'Debe iniciar sesión como empleado de tienda')
            return redirect('Login')
        
        usuario_tienda_id = request.session.get('usuario_tienda_id')
        if not usuario_tienda_id:
            messages.error(request, 'Sesión inválida')
            return redirect('Login')
        
        try:
            usuario_tienda = UsuarioTienda.objects.get(id=usuario_tienda_id, activo=True)
            request.usuario_tienda = usuario_tienda
        except UsuarioTienda.DoesNotExist:
            messages.error(request, 'Usuario no encontrado o inactivo')
            request.session.flush()
            return redirect('Login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_only(view_func):
    """
    Decorador que solo permite acceso a usuarios administradores
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_type') != 'admin':
            messages.error(request, 'Solo los administradores pueden acceder a esta sección')
            return redirect('Login')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_current_usuario_tienda(request):
    """
    Obtiene el usuario tienda actual de la sesión
    """
    if request.session.get('user_type') == 'tienda':
        usuario_tienda_id = request.session.get('usuario_tienda_id')
        if usuario_tienda_id:
            try:
                return UsuarioTienda.objects.get(id=usuario_tienda_id, activo=True)
            except UsuarioTienda.DoesNotExist:
                pass
    return None


def get_current_tienda(request):
    """
    Obtiene la tienda actual del usuario logueado
    """
    usuario_tienda = get_current_usuario_tienda(request)
    if usuario_tienda:
        return usuario_tienda.tienda
    return None


def check_tienda_permission(request, required_tienda_id=None):
    """
    Verifica si el usuario tiene permisos para una tienda específica
    """
    usuario_tienda = get_current_usuario_tienda(request)
    if not usuario_tienda:
        return False
    
    if required_tienda_id and usuario_tienda.tienda.id != required_tienda_id:
        return False
    
    return True

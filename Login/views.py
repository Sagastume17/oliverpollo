from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from VentaTienda.models import UsuarioTienda
from VentaTienda.forms import LoginTiendaForm


def login_in(request):
    try:
        if request.method == 'POST':
            login_type = request.POST.get('login_type', 'admin')

            if login_type == 'admin':
                # Login de administrador
                form = AuthenticationForm(request, data=request.POST)
                if form.is_valid():
                    usuario = form.cleaned_data['username']
                    clave = form.cleaned_data['password']
                    user = authenticate(username=usuario, password=clave)
                    if user is not None:
                        if user.is_active:
                            if user.rol == 'admin':
                                login(request, user)
                                request.session['member_id'] = user.id
                                request.session['user_type'] = 'admin'
                                return redirect('Admin')
                            else:
                                messages.error(request, 'No tiene permisos de administrador')
                        else:
                            messages.error(request, 'Usuario inactivo')
                    else:
                        messages.error(request, 'Credenciales invalidas')

            elif login_type == 'tienda':
                # Login de usuario tienda
                form_tienda = LoginTiendaForm(request.POST)
                if form_tienda.is_valid():
                    username = form_tienda.cleaned_data['username']
                    password = form_tienda.cleaned_data['password']

                    try:
                        usuario_tienda = UsuarioTienda.objects.get(username=username, activo=True)
                        if usuario_tienda.check_password(password):
                            # Crear sesión para usuario tienda
                            request.session['usuario_tienda_id'] = usuario_tienda.id
                            request.session['user_type'] = 'tienda'
                            request.session['tienda_id'] = usuario_tienda.tienda.id
                            messages.success(request, f'Bienvenido {usuario_tienda.nombre_completo}')
                            return redirect('venta_tienda:menu_principal')
                        else:
                            messages.error(request, 'Password incorrecta')
                    except UsuarioTienda.DoesNotExist:
                        messages.error(request, 'Usuario no encontrado o inactivo')
                else:
                    messages.error(request, 'Por favor corrige los errores en el formulario')

        # Mostrar formularios
        form = AuthenticationForm()
        form_tienda = LoginTiendaForm()
        return render(request, 'Login/login.html', {
            'form': form,
            'form_tienda': form_tienda
        })
    except Exception as e:
        messages.error(request, 'Error en el sistema de login')
        return redirect('/')





def logout_out(request):
    try:
        user_type = request.session.get('user_type', 'admin')

        if user_type == 'admin':
            if 'member_id' in request.session:
                del request.session['member_id']
            logout(request)
        elif user_type == 'tienda':
            if 'usuario_tienda_id' in request.session:
                del request.session['usuario_tienda_id']
            if 'tienda_id' in request.session:
                del request.session['tienda_id']

        # Limpiar tipo de usuario
        if 'user_type' in request.session:
            del request.session['user_type']

        messages.success(request, 'Sesion finalizada con Exito')
        return redirect('Login')
    except Exception:
        return redirect('/')

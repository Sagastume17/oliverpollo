from decimal import Decimal
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from user.models import User
from Productos.models import Producto
from Productos.forms import ProductoForm,UpdateProductoForm,IngresoProductoForm
from Dash.models import Tienda
from django.db.models import Q
from datetime import datetime
from Categoria.models import Categoria
from django.shortcuts import get_object_or_404




@login_required
def nuevo_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST,request.FILES)
        if form.is_valid():
            try:
                producto = form.save(commit=False)
                producto.imagen = form.cleaned_data['imagen']
                producto.usuario = request.user
                producto.save()

                messages.success(request, f'Producto {producto.nombre} creado correctamente!')
                return redirect('ListaProducto')  # Redirección aquí
            except IntegrityError:
                messages.error(request, 'Ya existe un producto con el mismo nombre en la misma tienda y unidad de medida')
                # Puedes dejar que caiga al final y se re-renderice el formulario con errores

    else:
        form = ProductoForm()

    return render(request, 'Productos/nuevo.html', {'form': form})


@login_required
def listado_productos(request):
    tienda_id = request.GET.get('tienda')
    estado = request.GET.get('estado', True)  # Por defecto muestra activos

    productos = Producto.objects.filter(estado=estado)
    if tienda_id:
        productos = productos.filter(tienda_id=tienda_id)

    context = {
        'productos': productos,
        'tiendas': Tienda.objects.all(),
        'tienda_seleccionada': tienda_id,
    }
    
    return render(request, 'Productos/listado.html', context)

@login_required
def ingreso_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = IngresoProductoForm(request.POST)
        if form.is_valid():
            ingreso = form.save(commit=False)
            ingreso.producto = producto
            ingreso.usuario = request.user
            ingreso.save()

            messages.success(request, 'Ingreso registrado correctamente')
            return redirect('ListaProducto')
    else:
        form = IngresoProductoForm()

    return render(request, 'Productos/ingreso.html', {
        'form': form,
        'producto': producto
    })




@login_required
def cambiar_estado_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.estado = not producto.estado
    producto.save()

    estado = "activado" if producto.estado else "dado de baja"
    messages.success(request, f'Producto {producto.nombre} {estado} correctamente')
    return redirect('ListaProducto')

@login_required
def listado_productos_baja2(request):
    productos = Producto.objects.filter(estado=False)
    return render(request, 'Productos2/productos_baja.html', {'productos': productos})

 # Productos por tienda

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from .models import Producto2,  Tienda
from .forms import Producto2Form, IngresoProducto2Form, UpdateProducto2Form


@login_required
def nuevo_producto2(request):
    if request.method == 'POST':
        form = Producto2Form(request.POST, request.FILES)
        if form.is_valid():
            try:
                Producto2 = form.save(commit=False)
                Producto2.usuario = request.user
                Producto2.imagen = form.cleaned_data.get('imagen')
                Producto2.save()

                messages.success(request, f'Producto {Producto2.nombre} creado correctamente!')
                return redirect('ListaProducto2')

            except IntegrityError:
                messages.error(
                    request,
                    'Ya existe un producto con el mismo nombre, medida y tienda'
                )
    else:
        form = Producto2Form()

    return render(request, 'Productos2/nuevo.html', {'form': form})


@login_required
def listado_productos2(request):
    tienda_id = request.GET.get('tienda')
    estado = request.GET.get('estado', 'True')

    listado_productos2 = Producto2.objects.filter(estado=(estado == 'True'))

    if tienda_id:
        listado_productos2 = listado_productos2.filter(tienda_id=tienda_id)

    context = {
        'productos': listado_productos2,
        'tiendas': Tienda.objects.all(),
        'tienda_seleccionada': tienda_id,
        'estado': estado
    }

    return render(request, 'Productos2/listado.html', context)

@login_required
def ingreso_producto2(request, producto_id):
    producto = get_object_or_404(Producto2, id=producto_id)

    if request.method == 'POST':
        form = IngresoProducto2Form(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.producto2 = producto
            movimiento.usuario = request.user

            try:
                movimiento.save()
                messages.success(request, 'Movimiento registrado correctamente')
                return redirect('ListaProducto2')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, form.errors)
    else:
        form = IngresoProducto2Form()

    return render(request, 'Productos2/ingreso.html', {
        'form': form,
        'producto': producto
    })


@login_required
def actualizar_producto2(request, id):
    producto = get_object_or_404(Producto2, id=id)  # ✅ nombre correcto

    if request.method == 'POST':
        form = UpdateProducto2Form(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente')
            return redirect('ListaProducto2')
    else:
        form = UpdateProducto2Form(instance=producto)

    return render(request, 'Productos2/actualizar.html', {
        'form': form,
        'producto': producto
    })


@login_required
def cambiar_estado_producto2(request, producto_id):
    producto = get_object_or_404(Producto2, id=producto_id)  # ✅

    producto.estado = not producto.estado
    producto.save()

    estado = "activado" if producto.estado else "dado de baja"
    messages.success(request, f'Producto {producto.nombre} {estado} correctamente')

    return redirect('ListaProducto2')   

@login_required
def listado_productos_baja2(request):
    productos = Producto2.objects.filter(estado=False)
    return render(request, 'Productos2/productos_baja.html', {'productos': productos})


 # termina control interno de productos

def productos_por_tienda(request, tienda):
    # Filtrar productos por la tienda seleccionada
    if tienda:
        productos = Producto.objects.filter(tienda__id=tienda)
        tienda_obj = Tienda.objects.get(id=tienda)
    else:
        productos = Producto.objects.all()  # Mostrar todos los productos si no se selecciona tienda
        tienda_obj = None

    # Obtener todas las tiendas para el filtro
    tiendas = Tienda.objects.all()
    
    context = {
        'productos': productos,
        'tiendas': tiendas,
        'tienda_seleccionada': tienda,
        'tienda': tienda_obj,
    }
    return render(request, 'Productos/listado-productos.html', context)


@login_required
def actualizar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == 'POST':
        form = UpdateProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            try:
                producto = form.save(commit=False)
                # Solo actualizar imagen si se subió una nueva
                if 'imagen' in request.FILES:
                    producto.imagen = request.FILES['imagen']

                producto.usuario = request.user
                producto.save()

                messages.success(request, f'Producto {producto.nombre} actualizado correctamente!')
                return redirect('ListaProducto')
            except IntegrityError:
                messages.error(request, 'Ya existe un producto con el mismo nombre en la misma tienda y unidad de medida')
    else:
        form = UpdateProductoForm(instance=producto)

    return render(request, 'Productos/actualizar.html', {
        'form': form,
        'producto': producto
    })

@login_required
def listado_productos_baja(request):
    productos = Producto.objects.filter(estado=False)
    return render(request, 'Productos/productos_baja.html', {'productos': productos})



from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Insumos
from .forms import InsumosForm

@login_required
def crear_insumo(request):
    if request.method == 'POST':
        form = InsumosForm(request.POST)
        if form.is_valid():
            insumo = form.save(commit=False)
            insumo.usuario = request.user
            insumo.save()
            messages.success(request, 'Insumo registrado correctamente.')
            return redirect('listar_insumos')
    else:
        form = InsumosForm(initial={'fecha': timezone.now().strftime("%d-%m-%Y")})

    return render(request, 'Insumos/insumos_form.html', {'form': form, 'accion': 'Crear'})


@login_required
def listar_insumos(request):
    tienda_id = request.GET.get('tienda')
    buscar = request.GET.get('buscar', '').strip()
    
    insumos = Insumos.objects.filter(usuario=request.user)
    
    if tienda_id:
        insumos = insumos.filter(tienda_id=tienda_id)
    
    if buscar:
        insumos = insumos.filter(nombre__icontains=buscar)

    context = {
        'insumos': insumos,
        'tiendas': Tienda.objects.all(),
        'tienda_seleccionada': tienda_id,
        'buscar': buscar,
    }
    return render(request, 'Insumos/insumos_list.html', context)


@login_required
def editar_insumo(request, id):
    insumo = get_object_or_404(Insumos, id=id, usuario=request.user)
    if request.method == 'POST':
        form = InsumosForm(request.POST, instance=insumo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Insumo actualizado correctamente.')
            return redirect('listar_insumos')
    else:
        form = InsumosForm(instance=insumo)
    return render(request, 'Insumos/insumos_form.html', {'form': form, 'accion': 'Editar'})


@login_required
def eliminar_insumo(request, id):
    insumo = get_object_or_404(Insumos, id=id, usuario=request.user)
    insumo.delete()
    messages.success(request, 'Insumo eliminado correctamente.')
    return redirect('listar_insumos')
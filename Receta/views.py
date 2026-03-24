from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta,date
from Productos.models import Producto
from Receta.models import Receta,DetalleReceta,SolicitarReceta
from Receta.forms import RecetaForm,UpdateRecetaForm,DetalleRecetaForm
from user.models import User
import uuid
import random
from Categoria.models import Categoria
from django.http import JsonResponse

@login_required
def nueva(request):
    form = RecetaForm()
    if request.method == "POST":
        form = RecetaForm(request.POST)
        if form.is_valid():
            # Puedes usar form.save(commit=False) para asignar campos adicionales:
            r = form.save(commit=False)
            r.estado = 1
            r.fecha = datetime.today()
            r.usuario = User.objects.get(id=request.user.id)
            r.token = uuid.uuid4()
            # IMPORTANTE: Asegúrate que el formulario incluya el campo 'tienda'
            r.save()
            messages.success(request, f'Receta {r.nombre} ingresada correctamente. Ahora ingrese los ingredientes de esta receta')
            return redirect('DetalleReceta', r.token)
    return render(request, 'Receta/nueva.html', {'form': form})



@login_required
def detallereceta(request, t):
    receta = Receta.objects.get(token=t)
    detalle = DetalleReceta.objects.filter(token=t)

    if request.method == "POST":
        if 'quitar' in request.POST:
            det = DetalleReceta.objects.get(id=request.POST['corr'])
            pr = Producto.objects.get(id=det.producto.pk)
            # Devolver al stock la cantidad quitada de la receta
            Producto.objects.filter(id=pr.pk).update(stock=pr.stock + det.cantidad)
            det.delete()
            messages.success(request, f'Se quitó {det.cantidad} de Producto {pr.nombre} a Receta {receta.nombre}!')
            return redirect('DetalleReceta', t)
        else:
            form = DetalleRecetaForm(request.POST, tienda=receta.tienda)
            if form.is_valid():
                prod = Producto.objects.get(id=form.cleaned_data['producto'].pk)
                d = DetalleReceta()
                d.id_receta = receta
                d.producto = prod
                d.cantidad = form.cleaned_data['cantidad']
                d.precio_materia = prod.precio_venta
                d.estado = 1
                d.total = d.cantidad * d.precio_materia
                d.fecha = datetime.today()
                d.usuario = request.user
                d.token = t
                d.save()
                # Descontar del stock la cantidad usada en la receta
                Producto.objects.filter(id=prod.pk).update(stock=prod.stock - d.cantidad)
                messages.success(request, f'Producto {prod.nombre} ingresado correctamente a Receta {receta.nombre}')
                return redirect('DetalleReceta', t)
    else:
        form = DetalleRecetaForm(tienda=receta.tienda)

    return render(request, 'Receta/detalle.html', {'form': form, 'r': receta, 'd': detalle})



def obtener_productos(request, tienda_id):
    productos = Producto.objects.filter(tienda_id=tienda_id)
    productos_list = [
        {
            'id': p.id,
            'nombre': p.nombre,
        }
        for p in productos
    ]
    return JsonResponse(productos_list, safe=False)

#descuento = Producto.objects.get(id_prod=d.id_prod.id_prod)
#Producto.objects.filter(id_prod=d.id_prod.id_prod).update(stock=descuento.stock-d.cantidad,salido=descuento.salido+d.cantidad)


@login_required
def aplicar(request, t):
    r = Receta.objects.get(token=t)
    p = Producto()
    p.nombre = r.nombre
    p.medida = r.unidad
    p.stock = r.cantidad  # Asignar el stock inicial
    p.precio_compra = 0
    p.precio_venta = r.precio_receta
    p.usuario = request.user
    p.id_cate = Categoria.objects.get(id=1)
    p.tienda = r.tienda  # Asegúrate de asignar la tienda si la receta la tiene
    p.save()
    messages.success(request, f'Producto {p.nombre} ingresado con éxito.')
    return redirect('ListaReceta')

'''
@login_required
def aplicar(request,t):
    hoy = datetime.today()
    lareceta = Receta.objects.get(token = t)
    mas = timedelta(int(lareceta.tiempo))

    for i in DetalleReceta.objects.filter(token = t):
        if Producto.objects.get(id_prod=i.id_prod.id_prod) == i.id_prod:
            prod = Producto.objects.get(id_prod=i.id_prod.id_prod)
            Producto.objects.filter(id_prod=i.id_prod.id_prod).update(stock=prod.stock-i.cantidad,salido=prod.salido+i.cantidad) 
            
    s = SolicitarReceta()
    s.id_receta = Receta.objects.get(id=lareceta.id)
    s.tiempo = lareceta.tiempo
    s.cantidad =  lareceta.cantidad
    s.precio_receta = lareceta.precio_receta
    s.fecha = datetime.today()
    s.fecha_entrega = (hoy+mas)
    s.token = uuid.uuid4()
    s.estado = 0
    s.usuario = User.objects.get(id=request.user.id)
    s.save()
    messages.success(request,f'Se Solicito La Elaboracion de la Receta Verifique Su Estado Lista de Pedidos')
    return redirect('ListaReceta')        
'''    


@login_required
def lista(request):
    lista = Receta.objects.filter(estado=1)
    return render(request,'Receta/lista.html',{'lista':lista})

@login_required
def lista2(request):
    lista = Receta.objects.filter(estado=0)
    return render(request,'Receta/lista2.html',{'lista':lista})

@login_required
def bajareceta(request,receta):
    try:
        dato = Receta.objects.get(id=receta)
        Receta.objects.filter(id=receta).update(estado=0)
        messages.success(request,f'{dato.id} ha sido dada  de baja!')
        return redirect('ListaReceta')
    except:
        messages.error(request,f'{dato.id} ')
        return redirect('ListaReceta')
    
@login_required
def altareceta(request,receta):
    try:
        dato = Receta.objects.get(id=receta)
        Receta.objects.filter(id=receta).update(estado=1)
        messages.success(request,f'{dato.id} ha sido dada  de alta!')
        return redirect('ListaReceta')
    except:
        messages.error(request,f'{dato.id} ')
        return redirect('ListaReceta')


@login_required
def listapedidos(request):

    hoy = datetime.today().strftime("%Y-%m-%d")
    lista = SolicitarReceta.objects.all()

    for l in SolicitarReceta.objects.all():
        if str(l.fecha_entrega) == str(hoy):
            SolicitarReceta.objects.filter(id=l.id).update(estado=1)
        else:
            pass    

    return render(request,'Receta/listapedidos.html',{'lista':lista})